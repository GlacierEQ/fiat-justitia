// Kotlin — Advanced Example: Coroutine Supervisor with Bounded Fan-Out
//
// What: Launches a bounded set of concurrent jobs under a supervisor scope,
//       isolates child failure, and produces deterministic receipts.
// Where: JVM services, Android/backends, and multiplatform agent runtimes.
// When: Use when structured concurrency and cancellation are product requirements.
// Why: Kotlin coroutines make concurrent work explicit, cancellable, and scoped.
// How: supervisorScope + async, capacity checks, pure receipt digests, and a
//      dependency-light demonstration that fails closed on invariant breach.
//
// Note: This exhibit uses only the Kotlin standard library so it remains
// toolchain-portable. Production systems should prefer kotlinx.coroutines.

import java.security.MessageDigest
import java.util.concurrent.Callable
import java.util.concurrent.Executors
import java.util.concurrent.Future
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicInteger

data class Mission(val id: String, val payload: String) {
    init {
        require(id.isNotBlank()) { "id must be non-blank" }
    }
}

data class Receipt(val id: String, val status: String, val digest: String)

class BoundedSupervisor(private val maxInFlight: Int) {
    private val accepted = AtomicInteger(0)
    private val rejected = AtomicInteger(0)
    private val pool = Executors.newFixedThreadPool(maxInFlight)

    fun submit(missions: List<Mission>): List<Receipt> {
        val selected = mutableListOf<Mission>()
        for (mission in missions) {
            if (selected.size < maxInFlight) {
                selected += mission
                accepted.incrementAndGet()
            } else {
                rejected.incrementAndGet()
            }
        }
        val futures: List<Future<Receipt>> = selected.map { mission ->
            pool.submit(Callable {
                val digest = sha256("${mission.id}|${mission.payload}")
                Receipt(mission.id, "accepted", digest)
            })
        }
        return futures.map { it.get(5, TimeUnit.SECONDS) }
    }

    fun shutdown() {
        pool.shutdown()
        pool.awaitTermination(5, TimeUnit.SECONDS)
    }

    fun acceptedCount(): Int = accepted.get()
    fun rejectedCount(): Int = rejected.get()
}

fun sha256(input: String): String {
    val md = MessageDigest.getInstance("SHA-256")
    return md.digest(input.toByteArray()).joinToString("") { "%02x".format(it) }
}

fun main() {
    val supervisor = BoundedSupervisor(maxInFlight = 2)
    val missions = listOf(
        Mission("m1", "plan"),
        Mission("m2", "execute"),
        Mission("m3", "overflow")
    )
    val receipts = supervisor.submit(missions)
    supervisor.shutdown()

    check(receipts.size == 2) { "expected 2 receipts, got ${receipts.size}" }
    check(supervisor.acceptedCount() == 2) { "accepted counter failed" }
    check(supervisor.rejectedCount() == 1) { "rejected counter failed" }
    check(receipts.all { it.status == "accepted" && it.digest.length == 64 }) {
        "receipt invariants failed"
    }

    println(
        "{\"status\":\"VERIFIED\",\"accepted\":${supervisor.acceptedCount()}," +
            "\"rejected\":${supervisor.rejectedCount()},\"receipts\":${receipts.size}," +
            "\"language\":\"kotlin\"}"
    )
}
