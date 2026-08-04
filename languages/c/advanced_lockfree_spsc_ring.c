#define _POSIX_C_SOURCE 200112L
/**
 * C — Advanced Example: Lock-Free SPSC Ring Buffer for Real-Time Telemetry
 *
 * What: A bounded single-producer/single-consumer telemetry queue with explicit
 *       acquire/release memory ordering and observable backpressure.
 * Where: Audio pipelines, embedded controllers, telemetry collectors, and
 *        native inter-thread handoff paths.
 * When: Use when one producer and one consumer need deterministic bounded
 *       memory without mutexes or hidden allocation in the hot path.
 * Why: C exposes exact layout, cache-line separation, atomics, and ABI control.
 * How: The producer publishes frames before advancing write_idx; the consumer
 *      acquires write_idx before reading and releases read_idx after consuming.
 */

#include <pthread.h>
#include <sched.h>
#include <stdbool.h>
#include <stdatomic.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define RING_CAPACITY 1024U
#define RING_MASK (RING_CAPACITY - 1U)
#define CACHE_LINE_SIZE 64U
#define CONCURRENT_FRAMES 100000U

_Static_assert((RING_CAPACITY & (RING_CAPACITY - 1U)) == 0U,
               "RING_CAPACITY must be a power of two");

typedef struct {
    uint64_t timestamp_ns;
    float accel_x;
    float accel_y;
    float accel_z;
    float pressure_pa;
    float temperature_c;
    uint32_t sensor_id;
    uint32_t sequence;
} TelemetryFrame;

typedef struct {
    TelemetryFrame buffer[RING_CAPACITY];
    _Alignas(CACHE_LINE_SIZE) _Atomic(uint64_t) write_idx;
    _Alignas(CACHE_LINE_SIZE) _Atomic(uint64_t) read_idx;
    _Alignas(CACHE_LINE_SIZE) _Atomic(uint64_t) total_produced;
    _Atomic(uint64_t) total_consumed;
    _Atomic(uint64_t) backpressure_events;
} SPSCRingBuffer;

typedef struct {
    SPSCRingBuffer *ring;
    _Atomic(bool) producer_done;
    _Atomic(uint64_t) sequence_errors;
} ConcurrentHarness;

static SPSCRingBuffer *ring_create(void) {
    void *memory = NULL;
    if (posix_memalign(&memory, CACHE_LINE_SIZE, sizeof(SPSCRingBuffer)) != 0) {
        return NULL;
    }
    SPSCRingBuffer *ring = memory;
    memset(ring, 0, sizeof(*ring));
    atomic_init(&ring->write_idx, 0);
    atomic_init(&ring->read_idx, 0);
    atomic_init(&ring->total_produced, 0);
    atomic_init(&ring->total_consumed, 0);
    atomic_init(&ring->backpressure_events, 0);
    return ring;
}

static bool ring_try_push(SPSCRingBuffer *ring, const TelemetryFrame *frame) {
    if (ring == NULL || frame == NULL) {
        return false;
    }
    const uint64_t write = atomic_load_explicit(&ring->write_idx, memory_order_relaxed);
    const uint64_t read = atomic_load_explicit(&ring->read_idx, memory_order_acquire);
    if (write - read >= RING_CAPACITY) {
        atomic_fetch_add_explicit(&ring->backpressure_events, 1, memory_order_relaxed);
        return false;
    }

    ring->buffer[write & RING_MASK] = *frame;
    atomic_store_explicit(&ring->write_idx, write + 1U, memory_order_release);
    atomic_fetch_add_explicit(&ring->total_produced, 1, memory_order_relaxed);
    return true;
}

static bool ring_try_pop(SPSCRingBuffer *ring, TelemetryFrame *out) {
    if (ring == NULL || out == NULL) {
        return false;
    }
    const uint64_t read = atomic_load_explicit(&ring->read_idx, memory_order_relaxed);
    const uint64_t write = atomic_load_explicit(&ring->write_idx, memory_order_acquire);
    if (read >= write) {
        return false;
    }

    *out = ring->buffer[read & RING_MASK];
    atomic_store_explicit(&ring->read_idx, read + 1U, memory_order_release);
    atomic_fetch_add_explicit(&ring->total_consumed, 1, memory_order_relaxed);
    return true;
}

static uint64_t ring_size(const SPSCRingBuffer *ring) {
    const uint64_t write = atomic_load_explicit(&ring->write_idx, memory_order_acquire);
    const uint64_t read = atomic_load_explicit(&ring->read_idx, memory_order_acquire);
    return write - read;
}

static TelemetryFrame frame_for(uint32_t sequence) {
    const TelemetryFrame frame = {
        .timestamp_ns = (uint64_t)sequence * 1000000ULL,
        .accel_x = 0.0F,
        .accel_y = 0.0F,
        .accel_z = -9.81F,
        .pressure_pa = 101325.0F,
        .temperature_c = 22.5F,
        .sensor_id = 7U,
        .sequence = sequence,
    };
    return frame;
}

static int require_true(bool condition, const char *message) {
    if (!condition) {
        fprintf(stderr, "SPSC invariant failed: %s\n", message);
        return 1;
    }
    return 0;
}

static int test_overflow_boundary(void) {
    SPSCRingBuffer *ring = ring_create();
    if (ring == NULL) {
        fprintf(stderr, "unable to allocate overflow-test ring\n");
        return 1;
    }

    for (uint32_t sequence = 0; sequence < RING_CAPACITY; ++sequence) {
        TelemetryFrame frame = frame_for(sequence);
        if (!ring_try_push(ring, &frame)) {
            free(ring);
            return require_true(false, "queue rejected a frame before reaching capacity");
        }
    }
    TelemetryFrame overflow = frame_for(RING_CAPACITY);
    int failed = 0;
    failed |= require_true(!ring_try_push(ring, &overflow),
                           "queue accepted a frame beyond its bounded capacity");
    failed |= require_true(ring_size(ring) == RING_CAPACITY,
                           "full queue reported the wrong size");
    failed |= require_true(atomic_load(&ring->backpressure_events) == 1U,
                           "overflow was not recorded as backpressure");

    for (uint32_t expected = 0; expected < RING_CAPACITY; ++expected) {
        TelemetryFrame frame;
        failed |= require_true(ring_try_pop(ring, &frame),
                               "full queue could not be drained");
        failed |= require_true(frame.sequence == expected,
                               "FIFO sequence changed while draining");
    }
    failed |= require_true(ring_size(ring) == 0U, "drained queue was not empty");
    free(ring);
    return failed;
}

static void *producer_main(void *opaque) {
    ConcurrentHarness *harness = opaque;
    for (uint32_t sequence = 0; sequence < CONCURRENT_FRAMES; ++sequence) {
        TelemetryFrame frame = frame_for(sequence);
        while (!ring_try_push(harness->ring, &frame)) {
            sched_yield();
        }
    }
    atomic_store_explicit(&harness->producer_done, true, memory_order_release);
    return NULL;
}

static void *consumer_main(void *opaque) {
    ConcurrentHarness *harness = opaque;
    uint32_t expected = 0;
    while (expected < CONCURRENT_FRAMES) {
        TelemetryFrame frame;
        if (ring_try_pop(harness->ring, &frame)) {
            if (frame.sequence != expected) {
                atomic_fetch_add_explicit(&harness->sequence_errors, 1,
                                          memory_order_relaxed);
            }
            ++expected;
        } else {
            if (atomic_load_explicit(&harness->producer_done, memory_order_acquire)
                && ring_size(harness->ring) == 0U) {
                break;
            }
            sched_yield();
        }
    }
    return NULL;
}

static int test_concurrent_handoff(void) {
    SPSCRingBuffer *ring = ring_create();
    if (ring == NULL) {
        fprintf(stderr, "unable to allocate concurrent-test ring\n");
        return 1;
    }
    ConcurrentHarness harness = {.ring = ring};
    atomic_init(&harness.producer_done, false);
    atomic_init(&harness.sequence_errors, 0);

    pthread_t producer;
    pthread_t consumer;
    if (pthread_create(&producer, NULL, producer_main, &harness) != 0
        || pthread_create(&consumer, NULL, consumer_main, &harness) != 0) {
        free(ring);
        fprintf(stderr, "unable to start SPSC test threads\n");
        return 1;
    }
    (void)pthread_join(producer, NULL);
    (void)pthread_join(consumer, NULL);

    const uint64_t produced = atomic_load(&ring->total_produced);
    const uint64_t consumed = atomic_load(&ring->total_consumed);
    const uint64_t backpressure = atomic_load(&ring->backpressure_events);
    const uint64_t errors = atomic_load(&harness.sequence_errors);

    int failed = 0;
    failed |= require_true(produced == CONCURRENT_FRAMES,
                           "producer count did not match the mission input");
    failed |= require_true(consumed == CONCURRENT_FRAMES,
                           "consumer count did not match the mission input");
    failed |= require_true(errors == 0U, "concurrent handoff corrupted sequence order");
    failed |= require_true(ring_size(ring) == 0U,
                           "concurrent handoff left unconsumed frames");

    if (!failed) {
        printf("{\"status\":\"SUCCEEDED\",\"frames\":%u,"
               "\"produced\":%llu,\"consumed\":%llu,"
               "\"sequence_errors\":%llu,\"backpressure_events\":%llu}\n",
               CONCURRENT_FRAMES,
               (unsigned long long)produced,
               (unsigned long long)consumed,
               (unsigned long long)errors,
               (unsigned long long)backpressure);
    }
    free(ring);
    return failed;
}

int main(void) {
    if (require_true(!ring_try_push(NULL, NULL), "null input guard failed") != 0) {
        return 1;
    }
    if (test_overflow_boundary() != 0) {
        return 1;
    }
    return test_concurrent_handoff();
}
