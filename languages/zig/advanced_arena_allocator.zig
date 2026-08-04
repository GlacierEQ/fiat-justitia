const std = @import("std");

/// Zig — Advanced Example: Bounded Arena-Backed Telemetry Batch
///
/// What: Collects a mission-scoped telemetry batch with deterministic cleanup,
/// duplicate-sequence rejection, and a hard sample ceiling.
/// Where: Portable native CLIs, embedded ingest adapters, and FFI boundaries.
/// When: Many short-lived allocations share one lifetime and must be reclaimed together.
/// Why: Zig makes allocator ownership, failure, and deinitialization explicit.
/// How: ArenaAllocator owns batch memory; ArrayListUnmanaged and AutoHashMapUnmanaged
/// share that arena while append enforces uniqueness and bounded growth.

const Sample = struct {
    sequence: u32,
    temperature_c: f32,
    pressure_pa: f32,
};

const BatchError = error{ DuplicateSequence, CapacityExceeded };

const TelemetryBatch = struct {
    arena: std.heap.ArenaAllocator,
    samples: std.ArrayListUnmanaged(Sample) = .{},
    seen: std.AutoHashMapUnmanaged(u32, void) = .{},
    max_samples: usize,

    fn init(backing: std.mem.Allocator, max_samples: usize) TelemetryBatch {
        return .{
            .arena = std.heap.ArenaAllocator.init(backing),
            .max_samples = max_samples,
        };
    }

    fn deinit(self: *TelemetryBatch) void {
        self.samples.deinit(self.arena.allocator());
        self.seen.deinit(self.arena.allocator());
        self.arena.deinit();
    }

    fn append(self: *TelemetryBatch, sample: Sample) !void {
        if (self.samples.items.len >= self.max_samples) {
            return BatchError.CapacityExceeded;
        }
        const entry = try self.seen.getOrPut(self.arena.allocator(), sample.sequence);
        if (entry.found_existing) {
            return BatchError.DuplicateSequence;
        }
        try self.samples.append(self.arena.allocator(), sample);
    }

    fn meanTemperature(self: *const TelemetryBatch) f32 {
        var total: f32 = 0;
        for (self.samples.items) |sample| total += sample.temperature_c;
        return if (self.samples.items.len == 0)
            0
        else
            total / @as(f32, @floatFromInt(self.samples.items.len));
    }

    fn receiptFingerprint(self: *const TelemetryBatch) u64 {
        var hash: u64 = 1469598103934665603;
        for (self.samples.items) |sample| {
            hash ^= sample.sequence;
            hash *%= 1099511628211;
        }
        return hash;
    }
};

test "bounded arena batch preserves order and rejects duplicates" {
    var batch = TelemetryBatch.init(std.testing.allocator, 3);
    defer batch.deinit();

    try batch.append(.{ .sequence = 10, .temperature_c = 20.0, .pressure_pa = 101_325 });
    try batch.append(.{ .sequence = 11, .temperature_c = 22.0, .pressure_pa = 101_300 });
    try std.testing.expectApproxEqAbs(@as(f32, 21.0), batch.meanTemperature(), 0.001);
    try std.testing.expect(batch.receiptFingerprint() != 0);
    try std.testing.expectError(
        BatchError.DuplicateSequence,
        batch.append(.{ .sequence = 11, .temperature_c = 99.0, .pressure_pa = 1 }),
    );
    try batch.append(.{ .sequence = 12, .temperature_c = 24.0, .pressure_pa = 101_280 });
    try std.testing.expectError(
        BatchError.CapacityExceeded,
        batch.append(.{ .sequence = 13, .temperature_c = 25.0, .pressure_pa = 101_260 }),
    );
    try std.testing.expectEqual(@as(usize, 3), batch.samples.items.len);
}
