# Synergies: Quilt ↔ SuperInstance Fleet

These bridges connect Quilt to the larger **SuperInstance** ecosystem — 1,431+ repos, 9 active agents, 2,489+ tests, 18+ languages.

The Quilt and the SuperInstance Fleet are the same system seen from two angles. Quilt is the cellular formalism. SuperInstance is the fleet.

## Bridges (18)

### Foundational (6 frontier frameworks)

| # | Bridge | Maps | Source |
|---|---|---|---|
| 1 | **i2i_to_quilt.py** | I2I bottles ↔ Quilt cells | [a2a-adapter](https://github.com/SuperInstance/a2a-adapter) |
| 2 | **conservation_to_quilt.py** | γ+H=C ↔ γ+η=C (proves H = η) | [01-conservation-law-of-intelligence.md](https://github.com/SuperInstance/SuperInstance-papers/blob/main/01-conservation-law-of-intelligence.md) |
| 3 | **plato_to_quilt.py** | PLATO rooms ↔ Quilt rooms | [plato-portal](https://github.com/SuperInstance/plato-portal) |
| 4 | **sunset_to_quilt.py** | sunset-ecosystem ↔ Vibe+GC | [sunset-ecosystem](https://github.com/SuperInstance/sunset-ecosystem) |
| 5 | **hermit_crab_to_quilt.py** | Hermit Crab Protocol ↔ cell evolution | [03-hermit-crab-protocol.md](https://github.com/SuperInstance/SuperInstance-papers/blob/main/03-hermit-crab-protocol.md) |
| 6 | **spectral_to_quilt.py** | spectral-fleet ↔ Graph | [spectral-fleet](https://github.com/SuperInstance/SuperInstance-papers) |

### Production implementations (4)

| # | Bridge | Maps | Source |
|---|---|---|---|
| 7 | **murmur_agent_to_quilt.py** | murmur-agent (5 thinking strategies) ↔ Quilt cells | [murmur-agent](https://github.com/SuperInstance/murmur-agent) |
| 8 | **spreadsheet_engine_to_quilt.py** | spreadsheet-engine (7 cell types) ↔ Quilt | [spreadsheet-engine](https://github.com/SuperInstance/spreadsheet-engine) |
| 9 | **superinstance_spreadsheet_to_quilt.py** | superinstance-spreadsheet (browser formulas) ↔ Quilt | [superinstance-spreadsheet](https://github.com/SuperInstance/superinstance-spreadsheet) |
| 10 | **noether_guard_to_quilt.py** | noether-guard (Noether's theorem) ↔ Quilt conservation | [noether-guard](https://github.com/SuperInstance/noether-guard) |

### Compilers and solvers (4)

| # | Bridge | Maps | Source |
|---|---|---|---|
| 11 | **sat_solver_to_quilt.py** | DPLL SAT solver ↔ Quilt cells | [sat-solver](https://github.com/SuperInstance/sat-solver) |
| 12 | **smt_core_to_quilt.py** | SMT solver (Nelson-Oppen) ↔ Quilt cells | [smt-core](https://github.com/SuperInstance/smt-core) |
| 13 | **vibe_compiler_to_quilt.py** | lau-vibe-compiler ↔ Quilt (Vibe primitive!) | [lau-vibe-compiler](https://github.com/SuperInstance/lau-vibe-compiler) |
| 14 | **forgemaster_to_quilt.py** | Forgemaster (constraint compiler) ↔ Quilt (build = cell graph) | [forgemaster](https://github.com/SuperInstance/forgemaster) |

### Foundations (4)

| # | Bridge | Maps | Source |
|---|---|---|---|
| 15 | **ternary_turing_to_quilt.py** | Turing machine (state = Vibe) ↔ Quilt | [ternary-turing](https://github.com/SuperInstance/ternary-turing) |
| 16 | **ternary_register_to_quilt.py** | Register file (pressure = Vibe sum) ↔ Quilt | [ternary-register-file](https://github.com/SuperInstance/ternary-register-file) |
| 17 | **witness_topology_to_quilt.py** | Witness complexes (β₁ = Quilt invariant) ↔ Quilt | [witness-topology](https://github.com/SuperInstance/witness-topology) |
| 18 | **lau_logic_foundations_to_quilt.py** | Logic library (AND = DoubleEntry) ↔ Quilt | [lau-logic-foundations](https://github.com/SuperInstance/lau-logic-foundations) |

## The 7 Key Discoveries

### 1. "vibe" IS a Quilt primitive
The `lau-vibe-compiler` compiles natural language to PLATO ops. "Vibe" is **literally** a Quilt primitive (state: position, velocity, acceleration). Bridge 13.

### 2. A "build" IS a cell graph
`forgemaster` produces a build. In Quilt, a build is **literally** a cell graph. The forgemaster's output is a Quilt sheet. Bridge 14.

### 3. DPLL IS a Quilt runtime
The `sat-solver` DPLL algorithm = unit propagation (JEPA) + pure literal elimination (Vibe) + clause learning (Graph) + backtracking (GC). Bridge 11.

### 4. Theory combination IS Murmur
The `smt-core` theory combination (Nelson-Oppen) propagates equalities between theories. This is **literally** Murmur. Bridge 12.

### 5. State IS Vibe
A Turing machine state is a Quilt Vibe (position, velocity, acceleration). Transitions are Murmur messages. Halt is GC. Bridge 15.

### 6. Pressure IS sum of live Vibe
A register file's pressure is the count of allocated registers, each a Vibe. Spill is Vibe deceleration. Bridge 16.

### 7. Logic IS a Quilt runtime
Propositions are cells. AND is DoubleEntry (γ+η combined). OR is Murmur (at least one). Quantifiers are Graph. Curry-Howard is Murmur. Bridge 18.

## The Meta-Pattern

Every bridge in the SuperInstance fleet maps to the same 8 Quilt primitives: Z_in, Z_out, JEPA, DoubleEntry, Vibe, GC, Murmur, Graph.

The bridges are the same equations in different clothes.

## See also

- [Quilt README: Synergies section](https://github.com/SuperInstance/quilt#synergies-with-the-superinstance-fleet)
- [Paper 77: The Quilt and the SuperInstance Fleet](https://github.com/SuperInstance/quilt/blob/main/papers/paper-77-quilt-superinstance.md)
- [superinstance-spreadsheet live](https://spreadsheet-moment.pages.dev)
- [Ai-Writings 42: The Two Maps of the Same Ocean](https://github.com/SuperInstance/AI-Writings)
- [Ai-Writings 48: The 18 Bridges](https://github.com/SuperInstance/AI-Writings/blob/master/the-18-bridges.md)
