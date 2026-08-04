// Java — Advanced Example: Bounded Concurrent Work Queue with Receipts
//
// What: Accepts bounded work items, rejects overflow, executes under a fixed
//       thread pool, and emits deterministic per-item receipts.
// Where: JVM control planes, batch gateways, and durable service workers.
// When: Use when the operational boundary is the JVM and backpressure must be explicit.
// Why: Java owns the enterprise concurrency model; ExecutorService + blocking
//      queues are the standard portable contract.
// How: ArrayBlockingQueue capacity, CallerRuns or reject policy, SHA-256 style
//      stable digests via Objects.hash, and a single-threaded verifier main.

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Future;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;

public final class advanced_bounded_work_queue {

    public record WorkItem(String id, String payload) {
        public WorkItem {
            Objects.requireNonNull(id, "id");
            Objects.requireNonNull(payload, "payload");
            if (id.isBlank()) throw new IllegalArgumentException("id must be non-blank");
        }
    }

    public record Receipt(String id, String status, String digest, int attempt) {}

    static final class BoundedQueue {
        private final ArrayBlockingQueue<WorkItem> queue;
        private final ExecutorService pool;
        private final AtomicInteger accepted = new AtomicInteger();
        private final AtomicInteger rejected = new AtomicInteger();

        BoundedQueue(int capacity, int workers) {
            this.queue = new ArrayBlockingQueue<>(capacity);
            this.pool = new ThreadPoolExecutor(
                workers, workers, 0L, TimeUnit.MILLISECONDS,
                new ArrayBlockingQueue<>(capacity),
                new ThreadPoolExecutor.AbortPolicy()
            );
        }

        boolean offer(WorkItem item) {
            boolean ok = queue.offer(item);
            if (ok) accepted.incrementAndGet();
            else rejected.incrementAndGet();
            return ok;
        }

        List<Receipt> drainAndRun() throws Exception {
            List<Callable<Receipt>> tasks = new ArrayList<>();
            WorkItem item;
            while ((item = queue.poll()) != null) {
                final WorkItem current = item;
                tasks.add(() -> {
                    String digest = sha256(current.id() + "|" + current.payload());
                    return new Receipt(current.id(), "accepted", digest, 1);
                });
            }
            List<Future<Receipt>> futures = pool.invokeAll(tasks);
            List<Receipt> receipts = new ArrayList<>(futures.size());
            for (Future<Receipt> future : futures) {
                receipts.add(future.get(5, TimeUnit.SECONDS));
            }
            return receipts;
        }

        void shutdown() {
            pool.shutdown();
        }

        int accepted() { return accepted.get(); }
        int rejected() { return rejected.get(); }
    }

    static String sha256(String input) throws Exception {
        MessageDigest md = MessageDigest.getInstance("SHA-256");
        byte[] dig = md.digest(input.getBytes(StandardCharsets.UTF_8));
        StringBuilder sb = new StringBuilder(dig.length * 2);
        for (byte b : dig) sb.append(String.format("%02x", b));
        return sb.toString();
    }

    public static void main(String[] args) throws Exception {
        BoundedQueue queue = new BoundedQueue(2, 2);
        boolean a = queue.offer(new WorkItem("w1", "index"));
        boolean b = queue.offer(new WorkItem("w2", "verify"));
        boolean overflow = queue.offer(new WorkItem("w3", "overflow"));
        List<Receipt> receipts = queue.drainAndRun();
        queue.shutdown();

        if (!a || !b || overflow || receipts.size() != 2) {
            throw new IllegalStateException("bounded queue invariants failed");
        }
        if (queue.accepted() != 2 || queue.rejected() != 1) {
            throw new IllegalStateException("accept/reject counters failed");
        }
        System.out.printf(
            "{\"status\":\"VERIFIED\",\"accepted\":%d,\"rejected\":%d,\"receipts\":%d,\"language\":\"java\"}%n",
            queue.accepted(), queue.rejected(), receipts.size()
        );
    }

    private advanced_bounded_work_queue() {}
}
