package main

import "core:fmt"
import "core:math"

// Odin — Advanced Example: Data-Oriented Re-entry Thermal Tile Integrator
//
// What: Advances a bank of thermal-protection tiles through bounded convective
// heating, radiative cooling, and ablative mass loss.
// Where: Real-time simulation, vehicle digital twins, and deterministic physics loops.
// When: Data layout and explicit state mutation matter more than object abstraction.
// Why: Odin keeps arrays, procedures, and memory ownership visible and predictable.
// How: A tile bank is stepped with explicit units, clamped physical bounds,
// invariant checks, and a deterministic mission receipt.

SIGMA :: 5.670374419e-8

Tile :: struct {
    temperature_k: f64,
    mass_kg:        f64,
    area_m2:        f64,
    emissivity:     f64,
}

Environment :: struct {
    density_kg_m3: f64,
    velocity_m_s:  f64,
    nose_radius_m: f64,
    ambient_k:     f64,
}

clamp :: proc(value, low, high: f64) -> f64 {
    if value < low do return low
    if value > high do return high
    return value
}

heat_flux :: proc(env: Environment, tile: Tile) -> f64 {
    convective := 1.83e-4 * math.sqrt(env.density_kg_m3 / env.nose_radius_m) *
        env.velocity_m_s * env.velocity_m_s * env.velocity_m_s
    t2 := tile.temperature_k * tile.temperature_k
    a2 := env.ambient_k * env.ambient_k
    radiative := tile.emissivity * SIGMA * (t2 * t2 - a2 * a2)
    return convective - radiative
}

step_tile :: proc(tile: ^Tile, env: Environment, dt_s: f64) -> (q_net_w_m2: f64) {
    q_net_w_m2 = heat_flux(env, tile)
    heat_capacity_j_k := 900.0 * tile.mass_kg
    tile.temperature_k = clamp(
        tile.temperature_k + q_net_w_m2 * tile.area_m2 * dt_s / heat_capacity_j_k,
        env.ambient_k,
        4_000.0,
    )
    if tile.temperature_k > 1_800.0 {
        ablation_rate_kg_s := (tile.temperature_k - 1_800.0) * 1.0e-6 * tile.area_m2
        tile.mass_kg = clamp(tile.mass_kg - ablation_rate_kg_s * dt_s, 0.05, 10_000.0)
    }
    return
}

main :: proc() {
    tiles := [4]Tile{
        {temperature_k = 300, mass_kg = 2.0, area_m2 = 0.15, emissivity = 0.88},
        {temperature_k = 300, mass_kg = 2.1, area_m2 = 0.15, emissivity = 0.90},
        {temperature_k = 300, mass_kg = 1.9, area_m2 = 0.14, emissivity = 0.86},
        {temperature_k = 300, mass_kg = 2.2, area_m2 = 0.16, emissivity = 0.91},
    }
    env := Environment{density_kg_m3 = 0.018, velocity_m_s = 7_500, nose_radius_m = 1.2, ambient_k = 220}
    peak_flux: f64 = 0
    for tick in 0..<600 {
        _ = tick
        for i in 0..<len(tiles) {
            flux := step_tile(&tiles[i], env, 0.02)
            if flux > peak_flux do peak_flux = flux
        }
    }

    max_temperature := tiles[0].temperature_k
    total_mass: f64 = 0
    for tile in tiles {
        if tile.temperature_k > max_temperature do max_temperature = tile.temperature_k
        total_mass += tile.mass_kg
        if tile.temperature_k < env.ambient_k || tile.mass_kg <= 0 {
            panic("thermal invariant failed")
        }
    }
    fmt.printf(
        "{\"status\":\"VERIFIED\",\"tiles\":%d,\"peak_flux_w_m2\":%.3f,\"max_temperature_k\":%.3f,\"remaining_mass_kg\":%.6f}\n",
        len(tiles), peak_flux, max_temperature, total_mass,
    )
}
