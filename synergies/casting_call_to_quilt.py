"""
casting-call (SuperInstance) ↔ Quilt Cell Bridge

The SuperInstance casting-call (Python) is a living library of AI voices.
Each model is an instrument. Maps pipeline roles to AI models via a
capability atlas. Enforces the counterpoint constraint (no parallel octaves).

THE CRUCIAL INSIGHT: Each model IS a cell with a kind. The atlas IS the
cell graph. The counterpoint constraint IS a JEPA error (parallel octaves
predict same output). The cast() function IS the watch selecting cells.

Map:
- Model → cell (with capability scores)
- Role → subgraph
- Atlas → Graph
- Capability score → Vibe (state of expertise)
- Counterpoint → JEPA (no two models in parallel produce same output)
- cast() → watch (selection)
"""

from typing import Dict, List, Any, Optional


class ModelCell:
    """A Quilt cell representing an AI model."""
    def __init__(self, name: str, capabilities: Dict[str, float]):
        self.name = name
        # Capability scores for each role
        self.capabilities = capabilities
        # Voice character
        self.voice: str = ''
        # Total capability
        self.total = sum(capabilities.values())
        self.gamma = 0.5
        self.eta = 0.5


class CastingCallBridge:
    """A model atlas as a Quilt cell graph."""

    def __init__(self):
        self.models: Dict[str, ModelCell] = {}
        # Roles
        self.roles: List[str] = ['planner', 'coder', 'writer', 'reviewer', 'designer']
        # Atlas: role -> list of models
        self.atlas: Dict[str, List[str]] = {role: [] for role in self.roles}
        # Casted: pipeline stages
        self.casts: List[Dict[str, str]] = []

    def add_model(self, name: str, capabilities: Dict[str, float], voice: str = '') -> ModelCell:
        """Add a model. A cell with capabilities."""
        model = ModelCell(name, capabilities)
        model.voice = voice
        self.models[name] = model
        # Add to atlas for each capable role
        for role, score in capabilities.items():
            if role in self.roles and score > 0.5:
                self.atlas[role].append(name)
        return model

    def cast(self, role: str) -> Optional[ModelCell]:
        """Cast a model for a role. Watch selection."""
        candidates = self.atlas.get(role, [])
        if not candidates:
            return None
        # Pick the best (highest total capability)
        best = max(candidates, key=lambda m: self.models[m].total)
        return self.models[best]

    def cast_pipeline(self, pipeline: List[str]) -> List[Dict[str, str]]:
        """Cast a pipeline of roles. The watch orchestrates."""
        casted = []
        for role in pipeline:
            model = self.cast(role)
            if model:
                casted.append({'role': role, 'model': model.name, 'voice': model.voice})
                self.casts.append(casted[-1])
        return casted

    def check_counterpoint(self, models_in_parallel: List[ModelCell]) -> bool:
        """Check counterpoint constraint: no two models in parallel produce same output."""
        if len(models_in_parallel) < 2:
            return True
        # Check that capabilities differ
        for i in range(len(models_in_parallel)):
            for j in range(i + 1, len(models_in_parallel)):
                m1 = models_in_parallel[i]
                m2 = models_in_parallel[j]
                # If all capabilities match, fail
                if all(abs(m1.capabilities.get(k, 0) - m2.capabilities.get(k, 0)) < 1e-9
                       for k in set(m1.capabilities.keys()) | set(m2.capabilities.keys())):
                    return False
        return True


if __name__ == "__main__":
    print("=" * 60)
    print("CASTING-CALL ↔ QUILT CELL BRIDGE")
    print("=" * 60)
    print()
    print("Living library of AI voices on Quilt cells.")
    print("Each model IS a cell. The atlas IS the cell graph.")
    print()

    cc = CastingCallBridge()

    # Add models
    cc.add_model("planner_pro",
                 {'planner': 0.95, 'writer': 0.7, 'reviewer': 0.6},
                 voice='The Architect')
    cc.add_model("coder_pro",
                 {'coder': 0.95, 'reviewer': 0.8},
                 voice='The Smith')
    cc.add_model("writer_pro",
                 {'writer': 0.95, 'designer': 0.7, 'reviewer': 0.5},
                 voice='The Bard')
    cc.add_model("reviewer_pro",
                 {'reviewer': 0.95, 'planner': 0.6, 'writer': 0.6},
                 voice='The Critic')

    print(f"Models: {list(cc.models.keys())}")
    print()

    # Atlas
    print("Atlas:")
    for role, models in cc.atlas.items():
        print(f"  {role}: {models}")
    print()

    # Cast a pipeline
    pipeline = cc.cast_pipeline(['planner', 'coder', 'writer', 'reviewer'])
    print("Cast pipeline:")
    for c in pipeline:
        print(f"  {c['role']:10s} → {c['model']:15s} ({c['voice']})")
    print()

    # Counterpoint
    p = [cc.models['planner_pro'], cc.models['reviewer_pro']]
    print(f"Counterpoint (planner + reviewer): {cc.check_counterpoint(p)}")
    p = [cc.models['planner_pro'], cc.models['planner_pro']]
    print(f"Counterpoint (same model twice): {cc.check_counterpoint(p)}")
    print()

    # Conservation
    n = len(cc.models)
    total = sum(m.gamma + m.eta for m in cc.models.values())
    print(f"Conservation: {n} models, γ+η={total:.2f} (should be {n})")
    print()

    print("=" * 60)
    print("Iron sharpens iron.")
    print("Each model IS a cell. The atlas IS the cell graph.")
    print("The cast() function IS the watch.")


if __name__ == "__main__":
    demo()
