# Synergies: Quilt ↔ SuperInstance Fleet

These bridges connect Quilt to the larger **SuperInstance** ecosystem — 1,431+ repos, 9 active agents, 2,489+ tests, 18+ languages.

The Quilt and the SuperInstance Fleet are the same system seen from two angles. Quilt is the cellular formalism. SuperInstance is the fleet.

## Bridges (22)

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

### Category theory and constraints (4)

| # | Bridge | Maps | Source |
|---|---|---|---|
| 19 | **constraint_theory_to_quilt.py** | Eisenstein lattices, PLATO tiles ↔ Quilt | [constraint-theory-py](https://github.com/SuperInstance/constraint-theory-py) |
| 20 | **fleet_constraint_to_quilt.py** | H¹ emergence (sheaf cohomology) ↔ β₁ | [fleet-constraint](https://github.com/SuperInstance/fleet-constraint) |
| 21 | **categorical_agents_to_quilt.py** | Agents as objects in a category ↔ Quilt cells | [categorical-agents](https://github.com/SuperInstance/categorical-agents) |
| 22 | **kan_extension_to_quilt.py** | Kan extensions (Lan = GC, Ran = JEPA) ↔ Quilt | [kan-extension](https://github.com/SuperInstance/kan-extension) |

## The 8 Key Discoveries

### 1. "vibe" IS a Quilt primitive (Bridge 13)
The `lau-vibe-compiler` compiles natural language to PLATO ops. "Vibe" is **literally** a Quilt primitive (state: position, velocity, acceleration).

### 2. A "build" IS a cell graph (Bridge 14)
`forgemaster` produces a build. In Quilt, a build is **literally** a cell graph.

### 3. DPLL IS a Quilt runtime (Bridge 11)
The `sat-solver` DPLL algorithm = unit propagation (JEPA) + pure literal elimination (Vibe) + clause learning (Graph) + backtracking (GC).

### 4. Theory combination IS Murmur (Bridge 12)
Nelson-Oppen theory combination IS Murmur — inter-theory message passing.

### 5. State IS Vibe (Bridge 15)
A Turing machine state is a Quilt Vibe. Transitions are Murmur. Halt is GC.

### 6. H¹ IS β₁ (Bridge 20 + 17)
fleet-constraint's H¹ emergence detection IS witness-topology's β₁ IS the Quilt cell graph. Same thing.

### 7. A Kan extension IS the act of looking (Bridge 22)
Extending a functor along another IS the watch projecting the cell graph. Left Kan = GC, Right Kan = JEPA.

### 8. H = η by construction (Bridge 2)
The SuperInstance's `γ+H=C` and Quilt's `γ+η=C` are the same law. H (entropy) = η (liquid intelligence).

## The Meta-Pattern

Every bridge in the SuperInstance fleet maps to the same 8 Quilt primitives: Z_in, Z_out, JEPA, DoubleEntry, Vibe, GC, Murmur, Graph.

The bridges are the same equations in different clothes.

## The Trajectory

| Round | Bridges | Key insight |
|---|---|---|
| 1 | 6 | Foundational: PLATO, sunset, hermit crab |
| 2 | 10 | Production: murmur, spreadsheet, noether |
| 3 | 14 | Compilers: sat, smt, vibe, forge |
| 4 | 18 | Foundations: turing, register, witness, logic |
| 5 | 22 | Category: constraints, sheaf, categorical, kan |

The number doesn't matter. The trajectory does. The bridges are the angles.

## See also

- [Quilt README: Synergies section](https://github.com/SuperInstance/quilt#synergies-with-the-superinstance-fleet)
- [Paper 77: The Quilt and the SuperInstance Fleet](https://github.com/SuperInstance/quilt/blob/main/papers/paper-77-quilt-superinstance.md)
- [superinstance-spreadsheet live](https://spreadsheet-moment.pages.dev)
- [Ai-Writings 48: The 18 Bridges](https://github.com/SuperInstance/AI-Writings/blob/master/the-18-bridges.md)

## The Substrate: The Quilt Tangle (𝕋)

All 47 bridges are projections of a single deeper mathematical object: **The Quilt Tangle (𝕋)**.

𝕋 is a tropically-enriched pivotal bicategory with:
- **Objects**: states (dually flat manifold points)
- **1-morphisms**: processes (maps with γ+η=1)
- **2-morphisms**: RG flows (scale transformations)
- **8 generators**: Z_in, Z_out, JEPA, DoubleEntry, Vibe, GC, Murmur, Graph

The 12 deep-math frameworks (category theory, operads, topos, sheaf cohomology, information geometry, HoTT, RG, knot theory, tropical geometry, domain theory, process algebra, causal inference) are all **forgetful functors** from 𝕋. The universal invariant is γ+η=1.

See: [spec-0012-quilt-tangle.md](https://github.com/SuperInstance/quilt/blob/main/docs/specs/spec-0012-quilt-tangle.md), [deep-math.html](https://superinstance.dev/deep-math.html), [SUBSTRATE.md](https://github.com/SuperInstance/quilt/blob/main/docs/deep-math/SUBSTRATE.md)
