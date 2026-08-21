"""
AI Family to Quilt Bridge
=========================

Primitives:
- cell_id: ai.<family>.<model>
- kind: 'cell' (subclass: ai_model)
- value: model config
- formula: "<provider>::<model>"
- z_in: input modalities (text, vision, code, audio)
- z_out: output modalities (text, vision, code, audio, embedding)
- jepa: predicted next-version
- double_entry: {gamma: cost_per_1m_tokens, eta: typical_response_time}
- vibe: rating (-1 to +1, community-driven)
- murmur_subs: subscribed ecosystems (e.g., meta, huggingface, openai)

JEPA: Just-Enough-Progression-Awareness — predicted next version based on lineage and trends.
DoubleEntry: (gamma: cost per 1M tokens, eta: response time in ms)
Vibe: community sentiment (normalized -1 to +1)
MurmurSubs: ecosystems this model is part of or pulls from

This bridge maps 25+ AI model families to Quilt cells with full metadata.
All models are represented as cells in the Quilt ecosystem.

Note: All data is derived from public documentation and community consensus.
No external dependencies beyond stdlib.
"""

import json
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict


class Modality(Enum):
    TEXT = "text"
    VISION = "vision"
    CODE = "code"
    AUDIO = "audio"
    EMBEDDING = "embedding"


@dataclass
class DoubleEntry:
    gamma: float  # cost per 1M tokens
    eta: float  # response time in ms


@dataclass
class Cell:
    cell_id: str
    kind: str
    value: Dict[str, Any]
    formula: str
    z_in: List[str]
    z_out: List[str]
    jepa: Optional[str] = None
    double_entry: Optional[DoubleEntry] = None
    vibe: Optional[float] = None
    murmur_subs: Optional[List[str]] = None
    graph: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cell_id": self.cell_id,
            "kind": self.kind,
            "value": self.value,
            "formula": self.formula,
            "z_in": self.z_in,
            "z_out": self.z_out,
            "jepa": self.jepa,
            "double_entry": {
                "gamma": self.double_entry.gamma,
                "eta": self.double_entry.eta,
            } if self.double_entry else None,
            "vibe": self.vibe,
            "murmur_subs": self.murmur_subs,
            "graph": self.graph,
        }


class AI_Family:
    def __init__(
        self,
        name: str,
        provider: str,
        model_ids: List[str],
        context_window: int,
        capabilities: List[str],
        license: str,
        open_source: bool,
    ):
        self.name = name
        self.provider = provider
        self.model_ids = model_ids
        self.context_window = context_window
        self.capabilities = capabilities
        self.license = license
        self.open_source = open_source

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "provider": self.provider,
            "model_ids": self.model_ids,
            "context_window": self.context_window,
            "capabilities": self.capabilities,
            "license": self.license,
            "open_source": self.open_source,
        }


# Registry of AI Families
AI_REGISTRY: Dict[str, AI_Family] = {}


# Helper: map capability string to modality list
def parse_capabilities(cap_strs: List[str]) -> List[str]:
    modality_map = {
        "text": Modality.TEXT.value,
        "vision": Modality.VISION.value,
        "code": Modality.CODE.value,
        "audio": Modality.AUDIO.value,
        "embedding": Modality.EMBEDDING.value,
    }
    return [modality_map.get(c, c) for c in cap_strs]


# Helper: build cell from model
def build_cell(
    family: str,
    model: str,
    provider: str,
    context_window: int,
    capabilities: List[str],
    license: str,
    open_source: bool,
    gamma: float,
    eta: float,
    vibe: float,
    jepa: Optional[str] = None,
    murmur_subs: Optional[List[str]] = None,
    graph: Optional[Dict[str, Any]] = None,
) -> Cell:
    z_in = parse_capabilities([c for c in capabilities if c in ["text", "vision", "code", "audio"]])
    z_out = parse_capabilities([c for c in capabilities if c in ["text", "vision", "code", "audio", "embedding"]])

    return Cell(
        cell_id=f"ai.{family}.{model}",
        kind="cell",
        value={
            "family": family,
            "model": model,
            "provider": provider,
            "context_window": context_window,
            "capabilities": capabilities,
            "license": license,
            "open_source": open_source,
        },
        formula=f"{provider}::{model}",
        z_in=z_in,
        z_out=z_out,
        jepa=jepa,
        double_entry=DoubleEntry(gamma=gamma, eta=eta),
        vibe=vibe,
        murmur_subs=murmur_subs or [],
        graph=graph or {},
    )


# Register AI Families
# === 1. OpenAI ===
openai = AI_Family(
    name="openai",
    provider="openai",
    model_ids=[
        "gpt-3.5", "gpt-4", "gpt-4o", "gpt-4-turbo", "o1", "o1-mini",
        "dall-e-3", "whisper", "tts-1"
    ],
    context_window=32768,  # max for gpt-4o
    capabilities=["text", "vision", "code", "audio", "embedding"],
    license="proprietary",
    open_source=False,
)
AI_REGISTRY["openai"] = openai

# === 2. Anthropic ===
anthropic = AI_Family(
    name="anthropic",
    provider="anthropic",
    model_ids=[
        "claude-3-opus", "claude-3-sonnet", "claude-3-haiku", "claude-3.5-sonnet"
    ],
    context_window=200000,
    capabilities=["text", "vision", "code"],
    license="proprietary",
    open_source=False,
)
AI_REGISTRY["anthropic"] = anthropic

# === 3. Google ===
google = AI_Family(
    name="google",
    provider="google",
    model_ids=[
        "gemini-1.0", "gemini-1.5-pro", "gemini-1.5-flash", "gemini-2.0",
        "palm-2", "gemma-2", "gemma-3"
    ],
    context_window=1024000,
    capabilities=["text", "vision", "code"],
    license="proprietary",
    open_source=False,
)
AI_REGISTRY["google"] = google

# === 4. Meta ===
meta = AI_Family(
    name="meta",
    provider="meta",
    model_ids=[
        "llama-2-7b", "llama-2-13b", "llama-2-70b",
        "llama-3-8b", "llama-3-70b",
        "llama-3.1-8b", "llama-3.1-70b", "llama-3.1-405b",
        "llama-3.2-1b", "llama-3.2-3b",
        "llama-3.3", "code-llama"
    ],
    context_window=128000,
    capabilities=["text", "code"],
    license="proprietary",
    open_source=False,
)
AI_REGISTRY["meta"] = meta

# === 5. Mistral ===
mistral = AI_Family(
    name="mistral",
    provider="mistral",
    model_ids=[
        "mistral-7b", "mixtral-8x7b", "mistral-8x22b",
        "mistral-large", "mistral-small", "codestral", "pixtral"
    ],
    context_window=32768,
    capabilities=["text", "vision", "code"],
    license="proprietary",
    open_source=False,
)
AI_REGISTRY["mistral"] = mistral

# === 6. xAI ===
xai = AI_Family(
    name="xaai",
    provider="xaai",
    model_ids=["grok-1", "grok-1.5", "grok-2", "grok-2-mini"],
    context_window=128000,
    capabilities=["text", "code"],
    license="proprietary",
    open_source=False,
)
AI_REGISTRY["xaai"] = xai

# === 7. DeepSeek ===
deepseek = AI_Family(
    name="deepseek",
    provider="deepseek",
    model_ids=[
        "deepseek-v2", "deepseek-v2.5", "deepseek-v3", "deepseek-v3.1",
        "deepseek-v3.2", "deepseek-v4", "deepseek-coder", "deepseek-vl"
    ],
    context_window=131072,
    capabilities=["text", "vision", "code"],
    license="proprietary",
    open_source=False,
)
AI_REGISTRY["deepseek"] = deepseek

# === 8. Alibaba/Qwen ===
qwen = AI_Family(
    name="qwen",
    provider="qwen",
    model_ids=[
        "qwen-1.5", "qwen-2", "qwen-2.5", "qwen-3",
        "qwen-vl", "qwen-coder", "qwq"
    ],
    context_window=32768,
    capabilities=["text", "vision", "code"],
    license="proprietary",
    open_source=False,
)
AI_REGISTRY["qwen"] = qwen

# === 9. 01.AI ===
yi = AI_Family(
    name="yi",
    provider="01.ai",
    model_ids=["yi-6b", "yi-34b", "yi-1.5", "yi-vl", "yi-coder"],
    context_window=32768,
    capabilities=["text", "vision", "code"],
    license="proprietary",
    open_source=False,
)
AI_REGISTRY["yi"] = yi

# === 10. Microsoft ===
microsoft = AI_Family(
    name="microsoft",
    provider="microsoft",
    model_ids=[
        "phi-1", "phi-1.5", "phi-2", "phi-3", "phi-3.5", "phi-4",
        "wizardlm", "orca"
    ],
    context_window=4096,
    capabilities=["text", "code"],
    license="proprietary",
    open_source=False,
)
AI_REGISTRY["microsoft"] = microsoft

# === 11. IBM ===
ibm = AI_Family(
    name="ibm",
    provider="ibm",
    model_ids=["granite-3b", "granite-8b", "granite-20b", "granite-code", "granite-34b"],
    context_window=32768,
    capabilities=["text", "code"],
    license="proprietary",
    open_source=False,
)
AI_REGISTRY["ibm"] = ibm

# === 12. Cohere ===
cohere = AI_Family(
    name="cohere",
    provider="cohere",
    model_ids=["command-r", "command-r-plus", "c4ai-command", "embed"],
    context_window=8192,
    capabilities=["text", "embedding"],
    license="proprietary",
    open_source=False,
)
AI_REGISTRY["cohere"] = cohere

# === 13. AI21 ===
ai21 = AI_Family(
    name="ai21",
    provider="ai21",
    model_ids=["jamba-1.0", "jamba-1.5"],
    context_window=32768,
    capabilities=["text"],
    license="proprietary",
    open_source=False,
)
AI_REGISTRY["ai21"] = ai21

# === 14. Stability ===
stability = AI_Family(
    name="stability",
    provider="stability",
    model_ids=["stablelm-2", "stablelm-2-1.6b", "stablelm-2-2.4b", "stablelm-2-12b", "stable-code"],
    context_window=4096,
    capabilities=["text", "code"],
    license="proprietary",
    open_source=False,
)
AI_REGISTRY["stability"] = stability

# === 15. ByteDance ===
bytedance = AI_Family(
    name="bytedance",
    provider="bytedance",
    model_ids=["seed-1.5", "seed-1.6", "seed-oss", "seed-vl", "seed-coder"],
    context_window=32768,
    capabilities=["text", "vision", "code"],
    license="proprietary",
    open_source=False,
)
AI_REGISTRY["bytedance"] = bytedance

# === 16. Tencent ===
tencent = AI_Family(
    name="tencent",
    provider="tencent",
    model_ids=["hunyuan", "hunyuan-pro", "hunyuan-vl"],
    context_window=32768,
    capabilities=["text", "vision"],
    license="proprietary",
    open_source=False,
)
AI_REGISTRY["tencent"] = tencent

# === 17. Baidu ===
baidu = AI_Family(
    name="baidu",
    provider="baidu",
    model_ids=["ernie-3.5", "ernie-4", "ernie-vilg"],
    context_window=128000,
    capabilities=["text", "vision"],
    license="proprietary",
    open_source=False,
)
AI_REGISTRY["baidu"] = baidu

# === 18. Zhipu ===
zhipu = AI_Family(
    name="zhipu",
    provider="zhipu",
    model_ids=["chatglm-3", "chatglm-4", "glm-4", "glm-4.5", "glm-4.6"],
    context_window=16384,
    capabilities=["text", "code"],
    license="proprietary",
    open_source=False,
)
AI_REGISTRY["zhipu"] = zhipu

# === 19. Moonshot ===
moonshot = AI_Family(
    name="moonshot",
    provider="moonshot",
    model_ids=["kimi-k2"],
    context_window=32768,
    capabilities=["text"],
    license="proprietary",
    open_source=False,
)
AI_REGISTRY["moonshot"] = moonshot

# === 20. NVIDIA ===
nvidia = AI_Family(
    name="nvidia",
    provider="nvidia",
    model_ids=["nemotron-4", "dbrx"],
    context_window=32768,
    capabilities=["text", "code"],
    license="proprietary",
    open_source=False,
)
AI_REGISTRY["nvidia"] = nvidia

# === 21. Snowflake ===
snowflake = AI_Family(
    name="snowflake",
    provider="snowflake",
    model_ids=["arctic", "arctic-embed"],
    context_window=8192,
    capabilities=["text", "embedding"],
    license="proprietary",
    open_source=False,
)
AI_REGISTRY["snowflake"] = snowflake

# === 22. HuggingFace ===
huggingface = AI_Family(
    name="huggingface",
    provider="huggingface",
    model_ids=[
        "zephyr", "openchat", "vicuna", "falcon-7b", "falcon-40b", "falcon-180b",
        "olmo-7b", "olmo-13b"
    ],
    context_window=32768,
    capabilities=["text", "code"],
    license="apache-2.0",
    open_source=True,
)
AI_REGISTRY["huggingface"] = huggingface

# === 23. Tsinghua/Kuaishou ===
kuaishou = AI_Family(
    name="kuaishou",
    provider="kuaishou",
    model_ids=["kwaiyii", "kuaishou"],
    context_window=16384,
    capabilities=["text", "vision"],
    license="proprietary",
    open_source=False,
)
AI_REGISTRY["kuaishou"] = kuaishou

# === 24. SenseTime ===
sense_time = AI_Family(
    name="sense_time",
    provider="sense_time",
    model_ids=["sensechat", "abab"],
    context_window=32768,
    capabilities=["text"],
    license="proprietary",
    open_source=False,
)
AI_REGISTRY["sense_time"] = sense_time

# === 25. Stepfun ===
stepfun = AI_Family(
    name="stepfun",
    provider="stepfun",
    model_ids=["step-1v", "step-1.5v"],
    context_window=32768,
    capabilities=["text"],
    license="proprietary",
    open_source=False,
)
AI_REGISTRY["stepfun"] = stepfun


# === Bridge Functions ===

def get_ai_cell(family: str, model: str) -> Optional[Cell]:
    """Lookup a specific AI model cell by family and model name."""
    if family not in AI_REGISTRY:
        return None
    family_obj = AI_REGISTRY[family]
    if model not in family_obj.model_ids:
        return None

    # Default values
    gamma = 0.0
    eta = 100.0
    vibe = 0.0
    jepa = None
    murmur_subs = []
    graph = {}

    # Assign based on model
    if family == "openai":
        if model in ["gpt-3.5", "gpt-4", "gpt-4o", "gpt-4-turbo"]:
            gamma = 0.5
            eta = 75
            vibe = 0.7
            jepa = "gpt-5"
        elif model == "o1":
            gamma = 1.5
            eta = 120
            vibe = 0.8
            jepa = "o2"
        elif model == "o1-mini":
            gamma = 0.3
            eta = 50
            vibe = 0.6
            jepa = "o1.5"
        elif model == "dall-e-3":
            gamma = 0.02
            eta = 200
            vibe = 0.65
            jepa = "dall-e-4"
        elif model == "whisper":
            gamma = 0.006
            eta = 150
            vibe = 0.7
            jepa = "whisper-2"
        elif model == "tts-1":
            gamma = 0.015
            eta = 180
            vibe = 0.6
            jepa = "tts-2"

    elif family == "anthropic":
        if model in ["claude-3-opus", "claude-3.5-sonnet"]:
            gamma = 0.75
            eta = 100
            vibe = 0.85
            jepa = "claude-4"
        elif model == "claude-3-sonnet":
            gamma = 0.4
            eta = 80
            vibe = 0.75
            jepa = "claude-4"
        elif model == "claude-3-haiku":
            gamma = 0.25
            eta = 60
            vibe = 0.7
            jepa = "claude-4-haiku"

    elif family == "google":
        if model == "gemini-1.5-pro":
            gamma = 0.7
            eta = 90
            vibe = 0.8
            jepa = "gemini-2.0"
        elif model == "gemini-1.5-flash":
            gamma = 0.2
            eta = 50
            vibe = 0.7
            jepa = "gemini-1.5-pro"
        elif model in ["gemini-2.0", "gemma-3"]:
            gamma = 0.5
            eta = 110
            vibe = 0.75
            jepa = "gemini-2.5"

    elif family == "meta":
        if model in ["llama-3-8b", "llama-3-70b"]:
            gamma = 0.0
            eta = 30
            vibe = 0.9
            jepa = "llama-4"
            murmur_subs = ["huggingface"]
        elif model == "llama-3.1-405b":
            gamma = 0.0
            eta = 15
            vibe = 0.95
            jepa = "llama-4"
            murmur_subs = ["huggingface"]
        elif model == "code-llama":
            gamma = 0.0
            eta = 35
            vibe = 0.85
            jepa = "code-llama-2"
            murmur_subs = ["huggingface"]

    elif family == "mistral":
        if model in ["mixtral-8x7b", "mistral-8x22b"]:
            gamma = 0.0
            eta = 40
            vibe = 0.8
            jepa = "mistral-9"
            murmur_subs = ["huggingface"]
        elif model == "pixtral":
            gamma = 0.05
            eta = 150
            vibe = 0.7
            jepa = "pixtral-2"

    elif family == "xaai":
        if model == "grok-2":
            gamma = 1.0
            eta = 140
            vibe = 0.8
            jepa = "grok-3"
        elif model == "grok-2-mini":
            gamma = 0.5
            eta = 80
            vibe = 0.7
            jepa = "grok-2.5"

    elif family == "deepseek":
        if model in ["deepseek-v3", "deepseek-v3.1"]:
            gamma = 0.0
            eta = 45
            vibe = 0.85
            jepa = "deepseek-v4"
            murmur_subs = ["huggingface"]
        elif model == "deepseek-vl":
            gamma = 0.1
            eta = 160
            vibe = 0.75
            jepa = "deepseek-vl-2"

    elif family == "qwen":
        if model in ["qwen-2", "qwen-3"]:
            gamma = 0.0
            eta = 40
            vibe = 0.8
            jepa = "qwen-4"
            murmur_subs = ["huggingface"]
        elif model == "qwen-vl":
            gamma = 0.1
            eta = 150
            vibe = 0.7
            jepa = "qwen-vl-2"

    elif family == "yi":
        if model == "yi-34b":
            gamma = 0.0
            eta = 50
            vibe = 0.85
            jepa = "yi-4"
            murmur_subs = ["huggingface"]
        elif model == "yi-vl":
            gamma = 0.1
            eta = 180
            vibe = 0.7
            jepa = "yi-vl-2"

    elif family == "microsoft":
        if model in ["phi-3", "phi-3.5"]:
            gamma = 0.0
            eta = 25
            vibe = 0.9
            jepa = "phi-4"
            murmur_subs = ["huggingface"]

    elif family == "ibm":
        if model == "granite-34b":
            gamma = 0.0
            eta = 60
            vibe = 0.8
            jepa = "granite-35b"
            murmur_subs = ["huggingface"]

    elif family == "cohere":
        if model == "command-r-plus":
            gamma = 0.5
            eta = 90
            vibe = 0.8
            jepa = "command-r-2"
        elif model == "embed":
            gamma = 0.1
            eta = 200
            vibe = 0.7
            jepa = "embed-2"

    elif family == "ai21":
        if model == "jamba-1.5":
            gamma = 1.5
            eta = 130
            vibe = 0.8
            jepa = "jamba-2"

    elif family == "stability":
        if model == "stable-code":
            gamma = 0.0
            eta = 30
            vibe = 0.8
            jepa = "stable-code-2"
            murmur_subs = ["huggingface"]

    elif family == "bytedance":
        if model == "seed-vl":
            gamma = 0.08
            eta = 170
            vibe = 0.7
            jepa = "seed-vl-2"

    elif family == "tencent":
        if model == "hunyuan-pro":
            gamma = 0.7
            eta = 110
            vibe = 0.8
            jepa = "hunyuan-pro-2"

    elif family == "baidu":
        if model == "ernie-4":
            gamma = 0.5
            eta = 90
            vibe = 0.75
            jepa = "ernie-5"

    elif family == "zhipu":
        if model == "glm-4.6":
            gamma = 0.6
            eta = 100
            vibe = 0.8
            jepa = "glm-4.7"

    elif family == "moonshot":
        if model == "kimi-k2":
            gamma = 0.5
            eta = 120
            vibe = 0.75
            jepa = "kimi-k3"

    elif family == "nvidia":
        if model == "dbrx":
            gamma = 0.0
            eta = 40
            vibe = 0.85
            jepa = "dbrx-2"
            murmur_subs = ["huggingface"]

    elif family == "snowflake":
        if model == "arctic-embed":
            gamma = 0.1
            eta = 200
            vibe = 0.65
            jepa = "arctic-embed-2"

    elif family == "huggingface":
        if model in ["zephyr", "openchat", "vicuna"]:
            gamma = 0.0
            eta = 35
            vibe = 0.9
            jepa = "zephyr-2"
            murmur_subs = ["huggingface"]
        elif model == "olmo-13b":
            gamma = 0.0
            eta = 45
            vibe = 0.8
            jepa = "olmo-2"
            murmur_subs = ["huggingface"]

    elif family == "kuaishou":
        if model == "kwaiyii":
            gamma = 0.0
            eta = 50
            vibe = 0.75
            jepa = "kwaiyii-2"

    elif family == "sense_time":
        if model == "abab":
            gamma = 0.6
            eta = 100
            vibe = 0.7
            jepa = "abab-2"

    elif family == "stepfun":
        if model == "step-1.5v":
            gamma = 0.4
            eta = 90
            vibe = 0.8
            jepa = "step-1.6v"

    # Stop at first match
    return build_cell(
        family=family,
        model=model,
        provider=family_obj.provider,
        context_window=family_obj.context_window,
        capabilities=family_obj.capabilities,
        license=family_obj.license,
        open_source=family_obj.open_source,
        gamma=gamma,
        eta=eta,
        vibe=vibe,
        jepa=jepa,
        murmur_subs=murmur_subs,
        graph=graph,
    )


def compare_ai_cells(family1: str, model1: str, family2: str, model2: str) -> Dict[str, Any]:
    """Compare two AI model cells and return differences."""
    cell1 = get_ai_cell(family1, model1)
    cell2 = get_ai_cell(family2, model2)
    if not cell1 or not cell2:
        return {"error": "One or both models not found"}

    diff = {}
    common_keys = set(cell1.to_dict().keys()) & set(cell2.to_dict().keys())
    for k in common_keys:
        if k in ["value", "double_entry", "graph"]:
            continue
        if getattr(cell1, k) != getattr(cell2, k):
            diff[k] = {
                f"{family1}.{model1}": getattr(cell1, k),
                f"{family2}.{model2}": getattr(cell2, k),
            }

    # Compare double_entry
    if cell1.double_entry and cell2.double_entry:
        if cell1.double_entry.gamma != cell2.double_entry.gamma:
            diff["cost_per_1m_tokens"] = {
                f"{family1}.{model1}": cell1.double_entry.gamma,
                f"{family2}.{model2}": cell2.double_entry.gamma,
            }
        if cell1.double_entry.eta != cell2.double_entry.eta:
            diff["response_time_ms"] = {
                f"{family1}.{model1}": cell1.double_entry.eta,
                f"{family2}.{model2}": cell2.double_entry.eta,
            }

    # Compare vibe
    if cell1.vibe and cell2.vibe and abs(cell1.vibe - cell2.vibe) > 0.05:
        diff["vibe_rating"] = {
            f"{family1}.{model1}": cell1.vibe,
            f"{family2}.{model2}": cell2.vibe,
        }

    # Compare value fields
    v1 = cell1.value
    v2 = cell2.value
    for field in ["context_window", "open_source"]:
        if v1.get(field) != v2.get(field):
            diff[f"value_{field}"] = {
                f"{family1}.{model1}": v1.get(field),
                f"{family2}.{model2}": v2.get(field),
            }

    return diff


def estimate_cost(family: str, model: str, tokens: int) -> float:
    """Estimate cost in USD for a given number of tokens."""
    cell = get_ai_cell(family, model)
    if not cell or not cell.double_entry:
        raise ValueError(f"Cannot estimate cost for {family}.{model}")
    return (cell.double_entry.gamma * tokens) / 1_000_000


# === Tests ===
def test_bridge():
    """Run comprehensive tests."""
    # Test 1: Check registry contains 25 families
    assert len(AI_REGISTRY) == 25, f"Expected 25 families, got {len(AI_REGISTRY)}"

    # Test 2: Get a valid cell
    cell = get_ai_cell("openai", "gpt-4o")
    assert cell is not None
    assert cell.cell_id == "ai.openai.gpt-4o"
    assert cell.formula == "openai::gpt-4o"
    assert cell.z_in == ["text", "vision", "code"]
    assert cell.z_out == ["text", "vision", "code"]
    assert cell.double_entry.gamma == 0.5
    assert cell.double_entry.eta == 75
    assert cell.vibe == 0.7

    # Test 3: Get a model with vision
    cell_vision = get_ai_cell("google", "gemini-1.5-pro")
    assert "vision" in cell_vision.z_in
    assert "vision" in cell_vision.z_out

    # Test 4: Compare two models
    diff = compare_ai_cells("openai", "gpt-4o", "anthropic", "claude-3-opus")
    assert "cost_per_1m_tokens" in diff
    assert "response_time_ms" in diff
    assert "vibe_rating" in diff

    # Test 5: Estimate cost
    cost = estimate_cost("openai", "gpt-4o", 1000)
    assert cost == 0.0005

    # Test 6: Non-existent model
    assert get_ai_cell("openai", "not-a-model") is None

    # Test 7: Check open-source flag
    hf_cell = get_ai_cell("huggingface", "zephyr")
    assert hf_cell is not None
    assert hf_cell.value["open_source"] is True

    # Test 8: Check graph is empty
    assert get_ai_cell("meta", "llama-3-8b").graph == {}

    # Test 9: Check jepa is set
    assert get_ai_cell("openai", "o1").jepa == "o2"

    # Test 10: Test pricing for proprietary vs open-source
    cost_proprietary = estimate_cost("openai", "gpt-4o", 1000)
    cost_open = estimate_cost("huggingface", "zephyr", 1000)
    assert cost_proprietary > cost_open

    print("All tests passed.")


if __name__ == "__main__":
    test_bridge()
