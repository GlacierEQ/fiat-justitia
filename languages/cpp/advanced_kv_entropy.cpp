/**
 * C++ — Advanced Example: Entropy-Aware KV Cache Pruner
 *
 * What: Deterministically selects the most useful key/value cache blocks under
 *       a strict capacity budget.
 * Where: Long-context inference runtimes, retrieval caches, and memory-bound
 *        transformer serving paths.
 * When: Use after profiling shows KV memory pressure is the limiting resource
 *       and eviction decisions must be inspectable and reproducible.
 * Why: C++ combines zero-cost abstractions, deterministic ownership, numerical
 *      routines, and native-speed policy execution.
 * How: Validate probability distributions, compute Shannon entropy, combine
 *      attention/recency/entropy into a bounded utility score, preserve pinned
 *      blocks, and emit a structured decision receipt.
 */

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <limits>
#include <numeric>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

struct KVBlock {
    std::uint64_t block_id{};
    std::vector<double> attention_probabilities;
    double attention_weight{};
    std::uint64_t age_tokens{};
    bool pinned{};
};

struct ScoredBlock {
    KVBlock block;
    double entropy_bits{};
    double utility{};
};

struct PruneConfig {
    std::size_t capacity{};
    double entropy_weight{0.35};
    double attention_weight{0.50};
    double recency_weight{0.15};
};

struct PruneReceipt {
    std::size_t input_blocks{};
    std::size_t kept_blocks{};
    std::size_t evicted_blocks{};
    std::size_t pinned_blocks{};
    double mean_entropy_bits{};
    std::uint64_t decision_fingerprint{};
    std::vector<std::uint64_t> kept_ids;
    std::vector<std::uint64_t> evicted_ids;
};

class KVCachePruner {
  public:
    static double shannon_entropy_bits(const std::vector<double>& probabilities) {
        if (probabilities.empty()) {
            throw std::invalid_argument("probability distribution must not be empty");
        }
        double total = 0.0;
        for (double value : probabilities) {
            if (!std::isfinite(value) || value < 0.0) {
                throw std::invalid_argument("probabilities must be finite and non-negative");
            }
            total += value;
        }
        if (!std::isfinite(total) || total <= 0.0) {
            throw std::invalid_argument("probability distribution must have positive mass");
        }

        double entropy = 0.0;
        for (double value : probabilities) {
            if (value == 0.0) {
                continue;
            }
            const double p = value / total;
            entropy -= p * std::log2(p);
        }
        return entropy;
    }

    static PruneReceipt prune(const std::vector<KVBlock>& blocks, const PruneConfig& config) {
        validate_config(config);
        validate_blocks(blocks, config.capacity);

        const std::uint64_t max_age = std::max<std::uint64_t>(
            1, std::accumulate(blocks.begin(), blocks.end(), std::uint64_t{0},
                               [](std::uint64_t current, const KVBlock& block) {
                                   return std::max(current, block.age_tokens);
                               }));

        std::vector<ScoredBlock> scored;
        scored.reserve(blocks.size());
        double entropy_sum = 0.0;
        std::size_t pinned_count = 0;

        for (const KVBlock& block : blocks) {
            const double entropy = shannon_entropy_bits(block.attention_probabilities);
            const double max_entropy = std::log2(
                static_cast<double>(block.attention_probabilities.size()));
            const double normalized_entropy = max_entropy > 0.0 ? entropy / max_entropy : 0.0;
            const double normalized_recency =
                1.0 - static_cast<double>(block.age_tokens) / static_cast<double>(max_age);
            const double utility = block.pinned
                ? std::numeric_limits<double>::infinity()
                : config.attention_weight * block.attention_weight
                    + config.entropy_weight * normalized_entropy
                    + config.recency_weight * normalized_recency;

            entropy_sum += entropy;
            pinned_count += block.pinned ? 1U : 0U;
            scored.push_back(ScoredBlock{block, entropy, utility});
        }

        std::stable_sort(scored.begin(), scored.end(), [](const ScoredBlock& left,
                                                          const ScoredBlock& right) {
            if (left.utility != right.utility) {
                return left.utility > right.utility;
            }
            return left.block.block_id < right.block.block_id;
        });

        PruneReceipt receipt;
        receipt.input_blocks = blocks.size();
        receipt.kept_blocks = std::min(config.capacity, blocks.size());
        receipt.evicted_blocks = blocks.size() - receipt.kept_blocks;
        receipt.pinned_blocks = pinned_count;
        receipt.mean_entropy_bits = entropy_sum / blocks.size();

        for (std::size_t index = 0; index < scored.size(); ++index) {
            const auto id = scored[index].block.block_id;
            if (index < receipt.kept_blocks) {
                receipt.kept_ids.push_back(id);
            } else {
                receipt.evicted_ids.push_back(id);
            }
        }
        receipt.decision_fingerprint = fingerprint(receipt.kept_ids, receipt.evicted_ids);
        verify_receipt(blocks, config, receipt);
        return receipt;
    }

    static std::string to_json(const PruneReceipt& receipt) {
        std::ostringstream out;
        out << std::fixed << std::setprecision(6);
        out << "{\"status\":\"SUCCEEDED\","
            << "\"input_blocks\":" << receipt.input_blocks << ','
            << "\"kept_blocks\":" << receipt.kept_blocks << ','
            << "\"evicted_blocks\":" << receipt.evicted_blocks << ','
            << "\"pinned_blocks\":" << receipt.pinned_blocks << ','
            << "\"mean_entropy_bits\":" << receipt.mean_entropy_bits << ','
            << "\"decision_fingerprint\":\"" << std::hex
            << receipt.decision_fingerprint << std::dec << "\","
            << "\"kept_ids\":" << ids_json(receipt.kept_ids) << ','
            << "\"evicted_ids\":" << ids_json(receipt.evicted_ids) << '}';
        return out.str();
    }

  private:
    static void validate_config(const PruneConfig& config) {
        if (config.capacity == 0) {
            throw std::invalid_argument("capacity must be positive");
        }
        const double sum = config.entropy_weight + config.attention_weight
            + config.recency_weight;
        if (!std::isfinite(sum) || std::abs(sum - 1.0) > 1e-9) {
            throw std::invalid_argument("policy weights must be finite and sum to 1.0");
        }
        if (config.entropy_weight < 0.0 || config.attention_weight < 0.0
            || config.recency_weight < 0.0) {
            throw std::invalid_argument("policy weights must be non-negative");
        }
    }

    static void validate_blocks(const std::vector<KVBlock>& blocks, std::size_t capacity) {
        if (blocks.empty()) {
            throw std::invalid_argument("at least one KV block is required");
        }
        std::set<std::uint64_t> ids;
        std::size_t pinned_count = 0;
        for (const KVBlock& block : blocks) {
            if (!ids.insert(block.block_id).second) {
                throw std::invalid_argument("block identifiers must be unique");
            }
            if (!std::isfinite(block.attention_weight)
                || block.attention_weight < 0.0 || block.attention_weight > 1.0) {
                throw std::invalid_argument("attention weight must be within [0, 1]");
            }
            pinned_count += block.pinned ? 1U : 0U;
        }
        if (pinned_count > capacity) {
            throw std::invalid_argument("capacity cannot evict pinned blocks");
        }
    }

    static void verify_receipt(const std::vector<KVBlock>& blocks,
                               const PruneConfig& config,
                               const PruneReceipt& receipt) {
        if (receipt.kept_ids.size() != receipt.kept_blocks
            || receipt.evicted_ids.size() != receipt.evicted_blocks
            || receipt.kept_blocks > config.capacity) {
            throw std::logic_error("receipt cardinality invariant failed");
        }
        std::set<std::uint64_t> observed;
        observed.insert(receipt.kept_ids.begin(), receipt.kept_ids.end());
        observed.insert(receipt.evicted_ids.begin(), receipt.evicted_ids.end());
        if (observed.size() != blocks.size()) {
            throw std::logic_error("receipt does not account for every input block");
        }
        for (const KVBlock& block : blocks) {
            if (block.pinned
                && std::find(receipt.kept_ids.begin(), receipt.kept_ids.end(), block.block_id)
                    == receipt.kept_ids.end()) {
                throw std::logic_error("pinned block was evicted");
            }
        }
    }

    static std::uint64_t fingerprint(const std::vector<std::uint64_t>& kept,
                                     const std::vector<std::uint64_t>& evicted) {
        // FNV-1a is a deterministic decision fingerprint, not a cryptographic hash.
        std::uint64_t value = 1469598103934665603ULL;
        const auto mix = [&value](std::uint64_t input) {
            for (unsigned int shift = 0; shift < 64; shift += 8) {
                value ^= (input >> shift) & 0xffU;
                value *= 1099511628211ULL;
            }
        };
        for (auto id : kept) {
            mix(id);
        }
        mix(0xffffffffffffffffULL);
        for (auto id : evicted) {
            mix(id);
        }
        return value;
    }

    static std::string ids_json(const std::vector<std::uint64_t>& ids) {
        std::ostringstream out;
        out << '[';
        for (std::size_t index = 0; index < ids.size(); ++index) {
            if (index != 0) {
                out << ',';
            }
            out << ids[index];
        }
        out << ']';
        return out.str();
    }
};

static void require(bool condition, const std::string& message) {
    if (!condition) {
        throw std::runtime_error(message);
    }
}

static void run_self_tests() {
    const std::vector<KVBlock> blocks{
        {10, {0.90, 0.10}, 0.95, 2, true},
        {20, {0.50, 0.50}, 0.70, 5, false},
        {30, {0.99, 0.01}, 0.45, 80, false},
        {40, {0.25, 0.25, 0.25, 0.25}, 0.60, 10, false},
        {50, {0.60, 0.20, 0.10, 0.10}, 0.30, 1, false},
    };
    const PruneConfig config{3, 0.35, 0.50, 0.15};

    const auto first = KVCachePruner::prune(blocks, config);
    const auto second = KVCachePruner::prune(blocks, config);
    require(first.kept_ids == second.kept_ids, "pruning must be deterministic");
    require(first.decision_fingerprint == second.decision_fingerprint,
            "decision fingerprint must be deterministic");
    require(first.kept_blocks == 3 && first.evicted_blocks == 2,
            "capacity accounting failed");
    require(std::find(first.kept_ids.begin(), first.kept_ids.end(), 10)
                != first.kept_ids.end(),
            "pinned block was not retained");

    bool invalid_distribution_rejected = false;
    try {
        (void)KVCachePruner::shannon_entropy_bits({0.5, -0.5});
    } catch (const std::invalid_argument&) {
        invalid_distribution_rejected = true;
    }
    require(invalid_distribution_rejected, "invalid probabilities were accepted");

    bool impossible_capacity_rejected = false;
    try {
        auto impossible = blocks;
        impossible[1].pinned = true;
        impossible[2].pinned = true;
        (void)KVCachePruner::prune(impossible, PruneConfig{2, 0.35, 0.50, 0.15});
    } catch (const std::invalid_argument&) {
        impossible_capacity_rejected = true;
    }
    require(impossible_capacity_rejected, "pinned-capacity violation was accepted");

    std::cout << KVCachePruner::to_json(first) << '\n';
}

int main() {
    try {
        run_self_tests();
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "KV cache pruner test failed: " << error.what() << '\n';
        return 1;
    }
}
