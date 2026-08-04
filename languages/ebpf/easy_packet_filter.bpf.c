/*
 * Easy Exhibit: eBPF Packet Filter
 * Category: Kernel Tracing & Network Security
 */

typedef unsigned int u32;
typedef unsigned long long u64;

struct bpf_map_def {
    u32 type;
    u32 key_size;
    u32 value_size;
    u32 max_entries;
    u32 map_flags;
};

#define SEC(NAME) __attribute__((section(NAME), used))

SEC("socket")
int filter_packets(void *ctx) {
    (void)ctx;
    // Return 0 to drop, >0 to pass
    return 1;
}
