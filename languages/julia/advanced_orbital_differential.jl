using LinearAlgebra
using Printf

# Julia — Advanced Example: Energy-Audited Velocity-Verlet Orbit Integrator
#
# What: Propagates a two-body orbit while measuring conservation of specific
# mechanical energy and angular momentum.
# Where: Flight dynamics, scientific digital twins, and numerical-method validation.
# When: Expressive mathematics and native-speed array operations must coexist.
# Why: Julia makes numerical kernels readable while specializing them through JIT compilation.
# How: Velocity-Verlet integration, finite-state validation, conservation diagnostics,
# and a deterministic circular-orbit test expose accuracy rather than merely drawing a path.

struct State
    r::Vector{Float64}
    v::Vector{Float64}
    function State(r, v)
        length(r) == 3 && length(v) == 3 || throw(ArgumentError("state must be three-dimensional"))
        all(isfinite, r) && all(isfinite, v) || throw(ArgumentError("state must be finite"))
        new(Vector{Float64}(r), Vector{Float64}(v))
    end
end

acceleration(r::Vector{Float64}, μ::Float64) = begin
    radius = norm(r)
    radius > 0 || throw(ArgumentError("radius must be positive"))
    -μ .* r ./ radius^3
end

function velocity_verlet(state::State, dt::Float64, μ::Float64)::State
    dt > 0 && isfinite(dt) || throw(ArgumentError("dt must be positive and finite"))
    μ > 0 && isfinite(μ) || throw(ArgumentError("μ must be positive and finite"))
    a0 = acceleration(state.r, μ)
    r1 = state.r .+ state.v .* dt .+ 0.5 .* a0 .* dt^2
    a1 = acceleration(r1, μ)
    v1 = state.v .+ 0.5 .* (a0 .+ a1) .* dt
    State(r1, v1)
end

specific_energy(state::State, μ::Float64) = dot(state.v, state.v) / 2 - μ / norm(state.r)
angular_momentum(state::State) = norm(cross(state.r, state.v))

function propagate(initial::State, dt::Float64, steps::Int, μ::Float64)
    steps > 0 || throw(ArgumentError("steps must be positive"))
    state = initial
    energy0 = specific_energy(initial, μ)
    momentum0 = angular_momentum(initial)
    max_energy_drift = 0.0
    max_momentum_drift = 0.0
    for _ in 1:steps
        state = velocity_verlet(state, dt, μ)
        max_energy_drift = max(max_energy_drift, abs((specific_energy(state, μ) - energy0) / energy0))
        max_momentum_drift = max(max_momentum_drift, abs((angular_momentum(state) - momentum0) / momentum0))
    end
    (; state, max_energy_drift, max_momentum_drift)
end

function main()
    μ = 3.986004418e14
    radius = 7_000_000.0
    initial = State([radius, 0.0, 0.0], [0.0, sqrt(μ / radius), 0.0])
    period = 2π * sqrt(radius^3 / μ)
    dt = 5.0
    steps = round(Int, period / dt)
    result = propagate(initial, dt, steps, μ)
    result.max_energy_drift < 1e-6 || error("energy drift exceeded reference bound")
    result.max_momentum_drift < 1e-12 || error("angular momentum drift exceeded reference bound")
    @printf("{\"status\":\"VERIFIED\",\"integrator\":\"velocity-verlet\",\"steps\":%d,\"max_relative_energy_drift\":%.12e,\"max_relative_angular_momentum_drift\":%.12e}\n",
            steps, result.max_energy_drift, result.max_momentum_drift)
end

main()
