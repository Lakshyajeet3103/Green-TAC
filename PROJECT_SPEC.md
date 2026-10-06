# Green TAC — Project Specification

## Research objective

Build a small compiler that generates Three-Address Code (TAC), supports multiple optimization strategies, and adaptively selects a strategy using an empirical cost model and carbon intensity.

## Strategies

1. Baseline TAC — straightforward TAC generation.
2. Lightweight — constant folding, algebraic simplification, copy propagation.
3. DAG — lightweight optimization plus local common-subexpression elimination.

## Carbon objective

For strategy i:

E_total(i) = E_compile(i) + N * E_runtime(i)

CO2e(i) = E_compile(i) * CI_compile / 3.6e6
         + N * E_runtime(i) * CI_runtime / 3.6e6

Units: E in joules, CI in gCO2e/kWh, N = expected executions.

The selector minimizes CO2e subject to a configurable runtime-overhead constraint.

## Data methodology

### Code/energy data
Collect empirical measurements of each benchmark under every strategy on the chosen machine. Record compilation time/energy and runtime/energy. Split train/test by program, not by repeated runs of the same program.

### Carbon-intensity data
Use an external grid-carbon dataset or API. Store it separately from compiler-energy measurements. Ember's India dataset is suitable for monthly India-level context; Electricity Maps can provide historical hourly zone data to eligible academic users; the official Great Britain Carbon Intensity API provides hourly historical/forecast data for GB.

### Important limitation
A carbon-intensity multiplier alone cannot change the strategy ranking when the same intensity applies to all strategies. To make carbon-aware selection meaningful, the model should distinguish compilation-period and expected runtime-period carbon intensity (or explicitly model when compilation/execution occurs).
