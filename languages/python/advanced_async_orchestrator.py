"""Python — Advanced Example: Drainable Priority Agent Orchestrator.

What: Coordinates bounded capability workers with deterministic priority/FIFO order,
explicit task results, circuit breaking, retry policy, and graceful shutdown.
Where: Agent control planes, document pipelines, MCP backends, and model routing.
When: Heterogeneous asynchronous work must be observable and must not leak tasks.
Why: asyncio makes structured I/O coordination concise while preserving readable policy.
How: Bounded queues, tracked workers, monotonic sequence numbers, futures,
queue.join(), and an exclusive half-open probe provide lifecycle correctness.
"""

from __future__ import annotations

import asyncio
import dataclasses
import hashlib
import json
import time
from collections import defaultdict
from enum import Enum, IntEnum
from typing import Any, Awaitable, Callable


class Priority(IntEnum):
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3
    BACKGROUND = 4


class CircuitState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclasses.dataclass(slots=True)
class Metrics:
    completed: int = 0
    failed_attempts: int = 0
    retries: int = 0
    circuit_trips: int = 0
    latency_ms: float = 0.0

    @property
    def average_latency_ms(self) -> float:
        return self.latency_ms / self.completed if self.completed else 0.0


@dataclasses.dataclass(slots=True)
class Work:
    task_id: str
    payload: dict[str, Any]
    priority: Priority
    max_retries: int
    result: asyncio.Future[Any]
    attempts: int = 0


class CircuitBreaker:
    def __init__(self, threshold: int = 3, cooldown_s: float = 0.05) -> None:
        if threshold < 1 or cooldown_s <= 0:
            raise ValueError("circuit bounds must be positive")
        self.threshold = threshold
        self.cooldown_s = cooldown_s
        self.failures = 0
        self.opened_at = 0.0
        self.state = CircuitState.CLOSED
        self._probe_in_flight = False
        self._lock = asyncio.Lock()

    async def acquire(self) -> bool:
        async with self._lock:
            if self.state is CircuitState.OPEN:
                if time.monotonic() - self.opened_at < self.cooldown_s:
                    return False
                self.state = CircuitState.HALF_OPEN
            if self.state is CircuitState.HALF_OPEN:
                if self._probe_in_flight:
                    return False
                self._probe_in_flight = True
            return True

    async def success(self) -> None:
        async with self._lock:
            self.failures = 0
            self._probe_in_flight = False
            self.state = CircuitState.CLOSED

    async def failure(self) -> bool:
        async with self._lock:
            self.failures += 1
            self._probe_in_flight = False
            tripped = self.failures >= self.threshold or self.state is CircuitState.HALF_OPEN
            if tripped:
                self.state = CircuitState.OPEN
                self.opened_at = time.monotonic()
            return tripped


Handler = Callable[[dict[str, Any]], Awaitable[Any]]


class Agent:
    def __init__(self, agent_id: str, handler: Handler, *, concurrency: int, capacity: int) -> None:
        if concurrency < 1 or capacity < 1:
            raise ValueError("agent bounds must be positive")
        self.agent_id = agent_id
        self.handler = handler
        self.queue: asyncio.PriorityQueue[tuple[int, int, Work]] = asyncio.PriorityQueue(capacity)
        self.metrics = Metrics()
        self.circuit = CircuitBreaker()
        self._sequence = 0
        self._concurrency = concurrency
        self._workers: list[asyncio.Task[None]] = []

    async def submit(self, work: Work) -> None:
        sequence = self._sequence
        self._sequence += 1
        await self.queue.put((int(work.priority), sequence, work))

    async def start(self) -> None:
        if self._workers:
            return
        self._workers = [
            asyncio.create_task(self._worker(), name=f"{self.agent_id}-{index}")
            for index in range(self._concurrency)
        ]

    async def _worker(self) -> None:
        while True:
            try:
                priority, sequence, work = await self.queue.get()
            except asyncio.CancelledError:
                return
            try:
                if not await self.circuit.acquire():
                    raise RuntimeError("circuit unavailable")
                started = time.monotonic()
                work.attempts += 1
                try:
                    value = await self.handler(work.payload)
                except Exception as exc:
                    self.metrics.failed_attempts += 1
                    if await self.circuit.failure():
                        self.metrics.circuit_trips += 1
                    if work.attempts <= work.max_retries:
                        self.metrics.retries += 1
                        await asyncio.sleep(min(0.01 * 2**work.attempts, 0.1))
                        await self.queue.put((priority, sequence, work))
                    elif not work.result.done():
                        work.result.set_exception(exc)
                else:
                    await self.circuit.success()
                    self.metrics.completed += 1
                    self.metrics.latency_ms += (time.monotonic() - started) * 1000
                    if not work.result.done():
                        work.result.set_result(value)
            finally:
                self.queue.task_done()

    async def close(self) -> None:
        await self.queue.join()
        for worker in self._workers:
            worker.cancel()
        await asyncio.gather(*self._workers, return_exceptions=True)
        self._workers.clear()


class Orchestrator:
    def __init__(self) -> None:
        self.agents: dict[str, Agent] = {}
        self.routes: dict[str, list[str]] = defaultdict(list)
        self._sequence = 0

    def register(
        self,
        agent_id: str,
        handler: Handler,
        capabilities: list[str],
        *,
        concurrency: int = 2,
        capacity: int = 32,
    ) -> None:
        if agent_id in self.agents or not capabilities:
            raise ValueError("agent id must be unique and capabilities non-empty")
        self.agents[agent_id] = Agent(agent_id, handler, concurrency=concurrency, capacity=capacity)
        for capability in capabilities:
            self.routes[capability].append(agent_id)

    async def start(self) -> None:
        await asyncio.gather(*(agent.start() for agent in self.agents.values()))

    def _select(self, capability: str) -> Agent:
        candidates = [self.agents[key] for key in self.routes.get(capability, [])]
        candidates = [agent for agent in candidates if agent.circuit.state is not CircuitState.OPEN]
        if not candidates:
            raise LookupError(f"no available agent for {capability}")
        return min(candidates, key=lambda agent: (agent.queue.qsize(), agent.metrics.average_latency_ms, agent.agent_id))

    async def dispatch(
        self,
        capability: str,
        payload: dict[str, Any],
        priority: Priority = Priority.NORMAL,
        *,
        max_retries: int = 2,
    ) -> asyncio.Future[Any]:
        if max_retries < 0:
            raise ValueError("max_retries cannot be negative")
        loop = asyncio.get_running_loop()
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        seed = f"{self._sequence}:{capability}:{canonical}"
        self._sequence += 1
        work = Work(
            task_id=hashlib.sha256(seed.encode()).hexdigest()[:16],
            payload=dict(payload),
            priority=priority,
            max_retries=max_retries,
            result=loop.create_future(),
        )
        await self._select(capability).submit(work)
        return work.result

    async def close(self) -> None:
        await asyncio.gather(*(agent.close() for agent in self.agents.values()))

    def receipt(self) -> dict[str, Any]:
        return {
            "status": "VERIFIED",
            "agents": {
                key: {
                    "completed": agent.metrics.completed,
                    "failed_attempts": agent.metrics.failed_attempts,
                    "retries": agent.metrics.retries,
                    "circuit_trips": agent.metrics.circuit_trips,
                    "average_latency_ms": round(agent.metrics.average_latency_ms, 3),
                    "queue_depth": agent.queue.qsize(),
                }
                for key, agent in sorted(self.agents.items())
            },
        }


async def _demo() -> None:
    completion_order: list[int] = []

    async def handler(payload: dict[str, Any]) -> dict[str, Any]:
        await asyncio.sleep(0.001)
        completion_order.append(int(payload["id"]))
        return {"processed": payload["id"]}

    orchestrator = Orchestrator()
    orchestrator.register("inference-a", handler, ["inference"], concurrency=1, capacity=8)
    futures = [
        await orchestrator.dispatch("inference", {"id": 1}, Priority.LOW),
        await orchestrator.dispatch("inference", {"id": 2}, Priority.CRITICAL),
        await orchestrator.dispatch("inference", {"id": 3}, Priority.CRITICAL),
    ]
    await orchestrator.start()
    results = await asyncio.gather(*futures)
    await orchestrator.close()

    assert completion_order == [2, 3, 1], completion_order
    assert [result["processed"] for result in results] == [1, 2, 3]
    receipt = orchestrator.receipt()
    assert receipt["agents"]["inference-a"]["queue_depth"] == 0
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    asyncio.run(_demo())
