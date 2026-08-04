# Elixir — Advanced Example: Supervised Idempotent Mission Worker
#
# What: Executes bounded missions, rejects duplicates, and demonstrates automatic
# worker replacement after a deliberate crash.
# Where: Realtime control planes, event processors, and long-lived agent services.
# When: Failure isolation and restart semantics are part of the product contract.
# Why: BEAM supervision turns process failure into an explicit lifecycle event.
# How: A one_for_one supervisor owns a registered GenServer whose state enforces
# input validation, idempotency, bounded history, and structured receipts.

defmodule MissionWorker do
  use GenServer

  def start_link(opts), do: GenServer.start_link(__MODULE__, opts, name: __MODULE__)
  def execute(mission), do: GenServer.call(__MODULE__, {:execute, mission})
  def crash, do: GenServer.cast(__MODULE__, :crash)

  @impl true
  def init(opts) do
    {:ok, %{seen: MapSet.new(), max_seen: Keyword.get(opts, :max_seen, 64), completed: 0}}
  end

  @impl true
  def handle_call({:execute, mission}, _from, state) do
    with {:ok, id, payload} <- validate(mission),
         false <- MapSet.member?(state.seen, id),
         true <- MapSet.size(state.seen) < state.max_seen do
      digest = :crypto.hash(:sha256, :erlang.term_to_binary(payload)) |> Base.encode16(case: :lower)
      receipt = %{status: :accepted, mission_id: id, output_sha256: digest}
      {:reply, receipt, %{state | seen: MapSet.put(state.seen, id), completed: state.completed + 1}}
    else
      true -> {:reply, %{status: :rejected, reason: :duplicate}, state}
      false -> {:reply, %{status: :rejected, reason: :capacity}, state}
      {:error, reason} -> {:reply, %{status: :rejected, reason: reason}, state}
    end
  end

  @impl true
  def handle_cast(:crash, _state), do: raise("intentional supervision probe")

  defp validate(%{id: id, payload: payload}) when is_binary(id) and byte_size(id) in 1..128,
    do: {:ok, id, payload}
  defp validate(_), do: {:error, :invalid_mission}
end

defmodule MissionSupervisor do
  use Supervisor
  def start_link(opts), do: Supervisor.start_link(__MODULE__, opts, name: __MODULE__)
  @impl true
  def init(opts), do: Supervisor.init([{MissionWorker, opts}], strategy: :one_for_one)
end

defmodule Demo do
  def wait_for_replacement(old_pid, attempts \\ 100)
  def wait_for_replacement(_old_pid, 0), do: raise("worker was not restarted")
  def wait_for_replacement(old_pid, attempts) do
    case Process.whereis(MissionWorker) do
      pid when is_pid(pid) and pid != old_pid -> pid
      _ -> Process.sleep(10); wait_for_replacement(old_pid, attempts - 1)
    end
  end

  def run do
    {:ok, _supervisor} = MissionSupervisor.start_link(max_seen: 4)
    first = MissionWorker.execute(%{id: "mission-1", payload: %{operation: :index}})
    duplicate = MissionWorker.execute(%{id: "mission-1", payload: %{operation: :index}})
    old_pid = Process.whereis(MissionWorker)
    MissionWorker.crash()
    new_pid = wait_for_replacement(old_pid)
    second = MissionWorker.execute(%{id: "mission-2", payload: %{operation: :verify}})

    unless first.status == :accepted and duplicate.reason == :duplicate and
             second.status == :accepted and old_pid != new_pid do
      raise("supervision or idempotency invariant failed")
    end
    IO.puts(~s({"status":"VERIFIED","duplicate_rejected":true,"worker_restarted":true,"missions_after_restart":1}))
  end
end

Demo.run()
