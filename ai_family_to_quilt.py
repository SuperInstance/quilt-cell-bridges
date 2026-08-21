"""
AI Family to Quilt Bridge
=========================

This module transforms AI substrate family metadata (from 8 major models: qwen, gpt, claude, llama, mistral, palm, gemini, cohere)
into Quilt cell-ledger entries compliant with Quilt's cell-ledger specification.

The bridge processes:
- Model metadata (name, version, provider, architecture, license)
- Family grouping (e.g., 'gpt' -> 'openai', 'claude' -> 'anthropic')
- Type inference (text-generation, embeddings, vision, etc.)
- Canonical identifiers for use in Quilt registries

Each entry is a dictionary conforming to:
{
    "cell": "ai_family.model_name.version",
    "family": "ai_family",
    "type": "model|embedding|vision|audio|etc",
    "provider": "openai|anthropic|meta|google|cohere|...|unknown",
    "architecture": "llama|gpt|claude|mistral|...|unknown",
    "version": "1.0.0",
    "license": "mit|apache-2.0|proprietary|...|unknown",
    "metadata": {
        "source": "ai_family",
        "family_tag": "gpt|claude|...|unknown",
        "description": "Human-readable description",
        "tags": ["text-generation", "llm", "chat"],
        "size": "1.5B|7B|70B|...|unknown"
    }
}

This implementation uses only stdlib modules (no external dependencies).
"""

import json
import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum


class ModelType(Enum):
    TEXT_GENERATION = "text-generation"
    EMBEDDING = "embedding"
    VISION = "vision"
    AUDIO = "audio"
    MULTIMODAL = "multimodal"
    UNKNOWN = "unknown"


class Provider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    META = "meta"
    GOOGLE = "google"
    COHERE = "cohere"
    DEEPSEEK = "deepseek"
    MISTRAL = "mistral"
    BAICHUAN = "baichuan"
    QWEN = "qwen"
    UNKNOWN = "unknown"


class Architecture(Enum):
    GPT = "gpt"
    CLAUDE = "claude"
    LLAMA = "llama"
    MISTRAL = "mistral"
    GEMINI = "gemini"
    PALM = "palm"
    COHERE = "cohere"
    DEEPSEEK = "deepseek"
    BAICHUAN = "baichuan"
    QWEN = "qwen"
    UNKNOWN = "unknown"


@dataclass
class ModelMetadata:
    name: str
    version: str
    family: str  # e.g., gpt, claude, llama
    model_type: ModelType
    provider: Provider
    architecture: Architecture
    license: str
    size: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class AIFamilyToQuiltBridge:
    """
    Bridge from AI substrate families to Quilt cell-ledger entries.

    Maps 8 major AI families to standardized Quilt ledger format.
    """

    # Mapping of family strings to provider and architecture
    FAMILY_MAP: Dict[str, Tuple[Provider, Architecture]] = {
        "gpt": (Provider.OPENAI, Architecture.GPT),
        "gpt-3": (Provider.OPENAI, Architecture.GPT),
        "gpt-4": (Provider.OPENAI, Architecture.GPT),
        "gpt-4o": (Provider.OPENAI, Architecture.GPT),
        "claude": (Provider.ANTHROPIC, Architecture.CLAUDE),
        "claude-2": (Provider.ANTHROPIC, Architecture.CLAUDE),
        "claude-3": (Provider.ANTHROPIC, Architecture.CLAUDE),
        "llama": (Provider.META, Architecture.LLAMA),
        "llama2": (Provider.META, Architecture.LLAMA),
        "llama3": (Provider.META, Architecture.LLAMA),
        "mistral": (Provider.MISTRAL, Architecture.MISTRAL),
        "mistral-7b": (Provider.MISTRAL, Architecture.MISTRAL),
        "palm": (Provider.GOOGLE, Architecture.PALM),
        "gemini": (Provider.GOOGLE, Architecture.GEMINI),
        "gemini-pro": (Provider.GOOGLE, Architecture.GEMINI),
        "cohere": (Provider.COHERE, Architecture.COHERE),
        "cohere-embed": (Provider.COHERE, Architecture.COHERE),
        "deepseek": (Provider.DEEPSEEK, Architecture.DEEPSEEK),
        "deepseek-llm": (Provider.DEEPSEEK, Architecture.DEEPSEEK),
        "baichuan": (Provider.BAICHUAN, Architecture.BAICHUAN),
        "baichuan-7b": (Provider.BAICHUAN, Architecture.BAICHUAN),
        "qwen": (Provider.QWEN, Architecture.QWEN),
        "qwen-7b": (Provider.QWEN, Architecture.QWEN),
        "qwen-14b": (Provider.QWEN, Architecture.QWEN),
    }

    # Default model types per family
    DEFAULT_TYPE_MAP: Dict[str, ModelType] = {
        "gpt": ModelType.TEXT_GENERATION,
        "claude": ModelType.TEXT_GENERATION,
        "llama": ModelType.TEXT_GENERATION,
        "mistral": ModelType.TEXT_GENERATION,
        "palm": ModelType.TEXT_GENERATION,
        "gemini": ModelType.MULTIMODAL,
        "cohere": ModelType.EMBEDDING,
        "deepseek": ModelType.TEXT_GENERATION,
        "baichuan": ModelType.TEXT_GENERATION,
        "qwen": ModelType.TEXT_GENERATION,
    }

    # Default licenses
    DEFAULT_LICENSES: Dict[str, str] = {
        "gpt": "proprietary",
        "claude": "proprietary",
        "llama": "llama-2",
        "mistral": "mit",
        "palm": "proprietary",
        "gemini": "proprietary",
        "cohere": "proprietary",
        "deepseek": "proprietary",
        "baichuan": "proprietary",
        "qwen": "apache-2.0",
    }

    # Default sizes
    DEFAULT_SIZES: Dict[str, str] = {
        "gpt": "175B",
        "gpt-3": "175B",
        "gpt-4": "1.8T",
        "gpt-4o": "1.8T",
        "claude": "100B",
        "claude-2": "100B",
        "claude-3": "100B",
        "llama": "6B",
        "llama2": "7B",
        "llama3": "8B",
        "mistral": "7B",
        "mistral-7b": "7B",
        "palm": "540M",
        "gemini": "1.2T",
        "gemini-pro": "1.2T",
        "cohere": "4B",
        "cohere-embed": "4B",
        "deepseek": "67B",
        "deepseek-llm": "67B",
        "baichuan": "7B",
        "baichuan-7b": "7B",
        "qwen": "7B",
        "qwen-7b": "7B",
        "qwen-14b": "14B",
    }

    # Tags by family
    TAGS_MAP: Dict[str, List[str]] = {
        "gpt": ["text-generation", "llm", "chat", "openai"],
        "gpt-3": ["text-generation", "llm", "chat", "openai"],
        "gpt-4": ["text-generation", "llm", "chat", "openai"],
        "gpt-4o": ["text-generation", "llm", "chat", "openai", "multimodal"],
        "claude": ["text-generation", "llm", "chat", "anthropic"],
        "claude-2": ["text-generation", "llm", "chat", "anthropic"],
        "claude-3": ["text-generation", "llm", "chat", "anthropic", "multimodal"],
        "llama": ["text-generation", "llm", "chat", "meta", "open-source"],
        "llama2": ["text-generation", "llm", "chat", "meta", "open-source"],
        "llama3": ["text-generation", "llm", "chat", "meta", "open-source"],
        "mistral": ["text-generation", "llm", "chat", "mistral", "open-source"],
        "mistral-7b": ["text-generation", "llm", "chat", "mistral", "open-source"],
        "palm": ["text-generation", "llm", "chat", "google"],
        "gemini": ["text-generation", "llm", "chat", "google", "multimodal"],
        "gemini-pro": ["text-generation", "llm", "chat", "google", "multimodal"],
        "cohere": ["embedding", "text-generation", "cohere"],
        "cohere-embed": ["embedding", "cohere"],
        "deepseek": ["text-generation", "llm", "chat", "deepseek"],
        "deepseek-llm": ["text-generation", "llm", "chat", "deepseek"],
        "baichuan": ["text-generation", "llm", "chat", "baichuan"],
        "baichuan-7b": ["text-generation", "llm", "chat", "baichuan"],
        "qwen": ["text-generation", "llm", "chat", "qwen", "alibaba"],
        "qwen-7b": ["text-generation", "llm", "chat", "qwen", "alibaba"],
        "qwen-14b": ["text-generation", "llm", "chat", "qwen", "alibaba"],
    }

    # Description templates
    DESCRIPTION_TEMPLATES: Dict[str, str] = {
        "gpt": "OpenAI's {version} model - a large language model for general-purpose text generation.",
        "gpt-3": "OpenAI's GPT-3 model - a 175-billion parameter language model.",
        "gpt-4": "OpenAI's GPT-4 model - advanced multimodal language model.",
        "gpt-4o": "OpenAI's GPT-4o model - optimized for speed and performance.",
        "claude": "Anthropic's {version} model - a large language model focused on safety and reasoning.",
        "claude-2": "Anthropic's Claude 2 model - second-generation AI assistant.",
        "claude-3": "Anthropic's Claude 3 model - state-of-the-art AI assistant with improved reasoning.",
        "llama": "Meta's Llama {version} model - open-source large language model.",
        "llama2": "Meta's Llama 2 model - open-source language model with improved safety.",
        "llama3": "Meta's Llama 3 model - next-generation open-source language model.",
        "mistral": "Mistral AI's {version} model - efficient open-source language model.",
        "mistral-7b": "Mistral AI's 7B parameter language model - lightweight and fast.",
        "palm": "Google's PaLM model - large language model developed for reasoning tasks.",
        "gemini": "Google's Gemini model - multimodal AI model for text, image, and audio.",
        "gemini-pro": "Google's Gemini Pro model - multimodal AI for text and image understanding.",
        "cohere": "Cohere's {version} model - designed for enterprise AI applications.",
        "cohere-embed": "Cohere's embedding model - for semantic similarity and retrieval.",
        "deepseek": "DeepSeek's {version} model - a large language model trained on diverse data.",
        "deepseek-llm": "DeepSeek's LLM - trained on code and natural language.",
        "baichuan": "Baichuan AI's {version} model - open-source language model developed in China.",
        "baichuan-7b": "Baichuan AI's 7B parameter language model - open-source model for Chinese and English.",
        "qwen": "Alibaba's Qwen model - large language model with strong multilingual support.",
        "qwen-7b": "Alibaba's Qwen 7B model - efficient open-source LLM for Chinese and English.",
        "qwen-14b": "Alibaba's Qwen 14B model - larger version of Qwen for complex tasks.",
    }

    def __init__(self):
        pass

    def normalize_family(self, family: str) -> str:
        """
        Normalize family string to canonical form.
        """
        if not family:
            return "unknown"

        # Strip whitespace and lowercase
        family = family.strip().lower()

        # Remove common prefixes/suffixes
        family = re.sub(r'^[a-z]+-', '', family)
        family = re.sub(r'-[a-z]+$', '', family)

        # Handle specific cases
        if family in ("gpt", "gpt3", "gpt3.5", "gpt-3.5"):
            return "gpt-3"
        if family in ("gpt4", "gpt-4", "gpt-4o", "gpt-4o-mini"):
            return "gpt-4o"
        if family in ("claude2", "claude-2"):
            return "claude-2"
        if family in ("claude3", "claude-3", "claude-3-opus", "claude-3-haiku"):
            return "claude-3"
        if family in ("llama2", "llama-2"):
            return "llama2"
        if family in ("llama3", "llama-3"):
            return "llama3"
        if family in ("mistral7b", "mistral-7b"):
            return "mistral-7b"
        if family in ("palm2", "palm-2"):
            return "palm"
        if family in ("gemini1", "gemini-1", "gemini-pro-1"):
            return "gemini-pro"
        if family in ("cohereembed", "cohere-embed"):
            return "cohere-embed"
        if family in ("deepseek", "deepseek-llm"):
            return "deepseek-llm"
        if family in ("baichuan7b", "baichuan-7b"):
            return "baichuan-7b"
        if family in ("qwen7b", "qwen-7b"):
            return "qwen-7b"
        if family in ("qwen14b", "qwen-14b"):
            return "qwen-14b"

        # Return as-is if not mapped
        return family

    def extract_version(self, name: str) -> str:
        """
        Extract version from model name.
        """
        if not name:
            return "unknown"

        # Look for version patterns
        match = re.search(r'(v|version|ver)?\s*([0-9]+(?:\.[0-9]+)*)', name, re.IGNORECASE)
        if match:
            return match.group(2)
        return "unknown"

    def determine_type(self, family: str, name: str) -> ModelType:
        """
        Determine model type based on family and name.
        """
        # Check for embedding keywords
        if any(kw in name.lower() for kw in ["embed", "embedding", "similarity", "encode"]):
            return ModelType.EMBEDDING

        # Check for vision/audio/multimodal keywords
        if any(kw in name.lower() for kw in ["vision", "image", "video", "audio", "multimodal"]):
            return ModelType.MULTIMODAL

        # Fall back to family mapping
        return self.DEFAULT_TYPE_MAP.get(family, ModelType.UNKNOWN)

    def get_metadata(self, family: str, name: str, version: str) -> Dict[str, Any]:
        """
        Generate metadata dictionary for a model.
        """
        normalized_family = self.normalize_family(family)

        # Use default values
        model_type = self.determine_type(normalized_family, name)
        provider, architecture = self.FAMILY_MAP.get(normalized_family, (Provider.UNKNOWN, Architecture.UNKNOWN))
        license = self.DEFAULT_LICENSES.get(normalized_family, "unknown")
        size = self.DEFAULT_SIZES.get(normalized_family, "unknown")
        tags = self.TAGS_MAP.get(normalized_family, [])
        description = self.DESCRIPTION_TEMPLATES.get(normalized_family, "AI model from {family} family.")

        # Format description
        description = description.format(version=version, family=normalized_family)

        return {
            "source": "ai_family",
            "family_tag": normalized_family,
            "description": description,
            "tags": tags,
            "size": size
        }

    def create_cell_ledger_entry(self, family: str, name: str, version: str = "unknown") -> Dict[str, Any]:
        """
        Create a single Quilt cell-ledger entry from AI family metadata.
        """
        normalized_family = self.normalize_family(family)
        version = version if version != "unknown" else self.extract_version(name)

        # Get provider and architecture
        provider, architecture = self.FAMILY_MAP.get(normalized_family, (Provider.UNKNOWN, Architecture.UNKNOWN))

        # Determine model type
        model_type = self.determine_type(normalized_family, name)

        # Get metadata
        metadata = self.get_metadata(normalized_family, name, version)

        # Create entry
        entry = {
            "cell": f"ai_family.{normalized_family}.{version}",
            "family": "ai_family",
            "type": model_type.value,
            "provider": provider.value,
            "architecture": architecture.value,
            "version": version,
            "license": license,
            "metadata": metadata
        }

        return entry

    def create_cell_ledger_entries(self, models: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Create multiple Quilt cell-ledger entries from a list of model specs.

        Each model spec is a dict with keys: name, family, version (optional)
        """
        entries = []
        for model in models:
            name = model.get("name", "").strip()
            family = model.get("family", "").strip()
            version = model.get("version", "unknown").strip()

            if not name or not family:
                continue

            entry = self.create_cell_ledger_entry(family, name, version)
            entries.append(entry)

        return entries


# --- TESTING ---


def test_normalize_family():
    bridge = AIFamilyToQuiltBridge()
    assert bridge.normalize_family("gpt") == "gpt-4o"
    assert bridge.normalize_family("GPT-3") == "gpt-3"
    assert bridge.normalize_family("gpt-3.5") == "gpt-3"
    assert bridge.normalize_family("gpt4") == "gpt-4o"
    assert bridge.normalize_family("gpt-4o") == "gpt-4o"
    assert bridge.normalize_family("claude2") == "claude-2"
    assert bridge.normalize_family("claude-3-haiku") == "claude-3"
    assert bridge.normalize_family("llama2") == "llama2"
    assert bridge.normalize_family("llama3") == "llama3"
    assert bridge.normalize_family("mistral7b") == "mistral-7b"
    assert bridge.normalize_family("palm2") == "palm"
    assert bridge.normalize_family("gemini1") == "gemini-pro"
    assert bridge.normalize_family("cohereembed") == "cohere-embed"
    assert bridge.normalize_family("deepseek-llm") == "deepseek-llm"
    assert bridge.normalize_family("baichuan7b") == "baichuan-7b"
    assert bridge.normalize_family("qwen7b") == "qwen-7b"
    assert bridge.normalize_family("qwen14b") == "qwen-14b"
    assert bridge.normalize_family("unknown") == "unknown"


def test_create_cell_ledger_entry():
    bridge = AIFamilyToQuiltBridge()

    # Test GPT-4
    entry = bridge.create_cell_ledger_entry("gpt-4", "gpt-4o", "1.0.0")
    assert entry["cell"] == "ai_family.gpt-4o.1.0.0"
    assert entry["family"] == "ai_family"
    assert entry["type"] == "text-generation"
    assert entry["provider"] == "openai"
    assert entry["architecture"] == "gpt"
    assert entry["version"] == "1.0.0"
    assert entry["license"] == "proprietary"
    assert entry["metadata"]["description"].startswith("OpenAI's 1.0.0 model")

    # Test Llama3
    entry = bridge.create_cell_ledger_entry("llama3", "llama3-8b", "3.1")
    assert entry["cell"] == "ai_family.llama3.3.1"
    assert entry["type"] == "text-generation"
    assert entry["provider"] == "meta"
    assert entry["architecture"] == "llama"
    assert entry["license"] == "llama-2"
    assert "open-source" in entry["metadata"]["tags"]

    # Test Cohere Embed
    entry = bridge.create_cell_ledger_entry("cohere", "cohere-embed", "v1.5")
    assert entry["cell"] == "ai_family.cohere-embed.v1.5"
    assert entry["type"] == "embedding"
    assert entry["provider"] == "cohere"
    assert entry["architecture"] == "cohere"
    assert entry["license"] == "proprietary"
    assert "embedding" in entry["metadata"]["tags"]

    # Test Qwen-7B
    entry = bridge.create_cell_ledger_entry("qwen-7b", "qwen-7b", "0.5")
    assert entry["cell"] == "ai_family.qwen-7b.0.5"
    assert entry["type"] == "text-generation"
    assert entry["provider"] == "qwen"
    assert entry["architecture"] == "qwen"
    assert entry["license"] == "apache-2.0"
    assert "qwen" in entry["metadata"]["tags"]

    # Test unknown family
    entry = bridge.create_cell_ledger_entry("unknown", "unknown-model", "1.0")
    assert entry["cell"] == "ai_family.unknown.1.0"
    assert entry["provider"] == "unknown"
    assert entry["architecture"] == "unknown"
    assert entry["license"] == "unknown"
    assert entry["type"] == "unknown"


def test_create_cell_ledger_entries():
    bridge = AIFamilyToQuiltBridge()

    models = [
        {"name": "gpt-4o", "family": "gpt-4", "version": "1.0.0"},
        {"name": "llama3-8b", "family": "llama3", "version": "3.1"},
        {"name": "cohere-embed", "family": "cohere", "version": "v1.5"},
        {"name": "qwen-7b", "family": "qwen-7b", "version": "0.5"},
    ]

    entries = bridge.create_cell_ledger_entries(models)

    assert len(entries) == 4
    assert entries[0]["cell"] == "ai_family.gpt-4o.1.0.0"
    assert entries[1]["cell"] == "ai_family.llama3.3.1"
    assert entries[2]["cell"] == "ai_family.cohere-embed.v1.5"
    assert entries[3]["cell"] == "ai_family.qwen-7b.0.5"


if __name__ == "__main__":
    # Run tests
    test_normalize_family()
    test_create_cell_ledger_entry()
    test_create_cell_ledger_entries()
    print("All tests passed.")
