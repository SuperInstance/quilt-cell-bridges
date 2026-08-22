# Synergies: Quilt ↔ SuperInstance Fleet

These bridges connect Quilt to the larger **SuperInstance** ecosystem — 1,431+ repos, 9 active agents, 2,489+ tests, 18+ languages.

The Quilt and the SuperInstance Fleet are the same system seen from two angles. Quilt is the cellular formalism. SuperInstance is the fleet.

## Bridges (14)

### Foundational (the 6 frontier frameworks)

| Bridge | Maps | Source |
|---|---|---|
| **i2i_to_quilt.py** | I2I bottles ↔ Quilt cells | [a2a-adapter](https://github.com/SuperInstance/a2a-adapter) |
| **conservation_to_quilt.py** | γ+H=C ↔ γ+η=C (proves H = η) | [01-conservation-law-of-intelligence.md](https://github.com/SuperInstance/SuperInstance-papers/blob/main/01-conservation-law-of-intelligence.md) |
| **plato_to_quilt.py** | PLATO rooms ↔ Quilt rooms | [plato-portal](https://github.com/SuperInstance/plato-portal) |
| **sunset_to_quilt.py** | sunset-ecosystem ↔ Vibe+GC | [sunset-ecosystem](https://github.com/SuperInstance/sunset-ecosystem) |
| **hermit_crab_to_quilt.py** | Hermit Crab Protocol ↔ cell evolution | [03-hermit-crab-protocol.md](https://github.com/SuperInstance/SuperInstance-papers/blob/main/03-hermit-crab-protocol.md) |
| **spectral_to_quilt.py** | spectral-fleet ↔ Graph | [spectral-fleet](https://github.com/SuperInstance/SuperInstance-papers) |

### Production implementations

| Bridge | Maps | Source |
|---|---|---|
| **murmur_agent_to_quilt.py** | murmur-agent (5 thinking strategies) ↔ Quilt cells | [murmur-agent](https://github.com/SuperInstance/murmur-agent) |
| **spreadsheet_engine_to_quilt.py** | spreadsheet-engine (7 cell types) ↔ Quilt | [spreadsheet-engine](https://github.com/SuperInstance/spreadsheet-engine) |
| **superinstance_spreadsheet_to_quilt.py** | superinstance-spreadsheet (browser formulas) ↔ Quilt | [superinstance-spreadsheet](https://github.com/SuperInstance/superinstance-spreadsheet) |
| **noether_guard_to_quilt.py** | noether-guard (Noether's theorem) ↔ Quilt conservation | [noether-guard](https://github.com/SuperInstance/noether-guard) |

### Compilers and solvers

| Bridge | Maps | Source |
|---|---|---|
| **sat_solver_to_quilt.py** | DPLL SAT solver ↔ Quilt cells (variables, clauses, conflicts) | [sat-solver](https://github.com/SuperInstance/sat-solver) |
| **smt_core_to_quilt.py** | SMT solver (Nelson-Oppen, congruence closure) ↔ Quilt cells | [smt-core](https://github.com/SuperInstance/smt-core) |
| **vibe_compiler_to_quilt.py** | lau-vibe-compiler (natural language → code) ↔ Quilt (Vibe primitive!) | [lau-vibe-compiler](https://github.com/SuperInstance/lau-vibe-compiler) |
| **forgemaster_to_quilt.py** | Forgemaster (constraint-aware compiler) ↔ Quilt (build = cell graph) | [forgemaster](https://github.com/SuperInstance/forgemaster) |

## The Key Discoveries

### "vibe" IS a Quilt primitive
The `lau-vibe-compiler` compiles natural language to PLATO ops. "Vibe" is **literally** a Quilt primitive (state: position, velocity, acceleration). The vibe-to-code compiler is a direct mapping. Bridge 13.

### A "build" IS a cell graph
`forgemaster` produces a build (a set of assembled components). In Quilt, a build is **literally** a cell graph. The forgemaster's output is a Quilt sheet. Bridge 14.

### DPLL IS Quilt runtime
The `sat-solver` DPLL algorithm is unit propagation (JEPA), pure literal elimination (Vibe), clause learning (Graph), backtracking (GC). The DPLL solver IS a Quilt runtime. Bridge 11.

### Theory combination IS Murmur
The `smt-core` theory combination (Nelson-Oppen) propagates equalities between theories. This is **literally** Murmur — inter-cell message passing. Bridge 12.

### "H" = "η" by construction
The SuperInstance's `γ+H=C` and Quilt's `γ+η=C` are the same law. H (entropy) = η (liquid intelligence). `noether_guard_to_quilt.py` proves this with Noether's theorem.

## See also

- [Quilt README: Synergies section](https://github.com/SuperInstance/quilt#synergies-with-the-superinstance-fleet)
- [Paper 77: The Quilt and the SuperInstance Fleet](https://github.com/SuperInstance/quilt/blob/main/papers/paper-77-quilt-superinstance.md)
- [superinstance-spreadsheet live](https://spreadsheet-moment.pages.dev)
- [Ai-Writings 42: The Two Maps of the Same Ocean](https://github.com/SuperInstance/AI-Writings)
