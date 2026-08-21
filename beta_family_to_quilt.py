"""
beta_family_to_quilt.py
======================

Bridge layer between Beta Family feature flags and Quilt-based feature management.

This module implements a mapping between the Beta Family lifecycle states
and a structured Quilt-based feature flag system. The Beta Family includes:
- beta-tester
- alpha-tester
- canary
- shadow
- staged-rollout

Each of these represents a progressive tier in feature release, and this bridge
converts them to a consistent Quilt representation for unified management.

The Quilt system is a hierarchical, key-based feature flag system that supports:
- Feature flags (boolean)
- Feature variants (string-based)
- Feature weights (float-based)
- Feature contexts (user, org, device, etc.)
- Feature rules (conditional logic)
- Feature metadata (description, owner, etc.)
- Feature visibility (public, internal, private)
- Feature history (audit trail)

This bridge provides:
- State conversion from Beta Family to Quilt
- State reconstruction from Quilt to Beta Family
- Validation of Beta Family state transitions
- Helper functions for feature flag management
- Testing utilities

All code uses only standard library modules.

Author: Engineering Team
Date: 2024-04-05
Version: 1.0
License: MIT
"""

import json
import re
from typing import Dict, List, Optional, Tuple, Any, Union
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timezone


# ========================
# 8 Primitives (Core Types)
# ========================

class BetaTier(Enum):
    """The five tiers in the Beta Family lifecycle."""
    BETA_TESTER = "beta-tester"
    ALPHA_TESTER = "alpha-tester"
    CANARY = "canary"
    SHADOW = "shadow"
    STAGED_ROLLOUT = "staged-rollout"

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"BetaTier.{self.name}"


class QuiltFeatureKey(str):
    """A unique key for a feature in the Quilt system."""
    pass


class QuiltVariant(str):
    """A variant value assigned to a feature."""
    pass


class QuiltWeight(float):
    """A float weight between 0.0 and 1.0 for feature rollout."""
    def __new__(cls, value: float) -> 'QuiltWeight':
        if not (0.0 <= value <= 1.0):
            raise ValueError("Weight must be between 0.0 and 1.0")
        return super().__new__(cls, value)


class QuiltContextKey(str):
    """A key used to identify a user context (e.g., 'user_id', 'org_id')."""
    pass


class QuiltContextValue(str):
    """A value associated with a context key."""
    pass


class QuiltRuleOperator(str, Enum):
    """Supported operators for rule evaluation."""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    IN = "in"
    NOT_IN = "not_in"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    GREATER_THAN_OR_EQUAL = "greater_than_or_equal"
    LESS_THAN_OR_EQUAL = "less_than_or_equal"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"


class QuiltRuleCondition:
    """A single condition in a rule."""
    def __init__(
        self,
        context_key: QuiltContextKey,
        operator: QuiltRuleOperator,
        value: Union[QuiltContextValue, List[QuiltContextValue]]
    ):
        self.context_key = context_key
        self.operator = operator
        self.value = value

    def __repr__(self) -> str:
        return f"QuiltRuleCondition({self.context_key}, {self.operator}, {self.value})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, QuiltRuleCondition):
            return False
        return (
            self.context_key == other.context_key
            and self.operator == other.operator
            and self.value == other.value
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "context_key": str(self.context_key),
            "operator": str(self.operator),
            "value": self.value if isinstance(self.value, list) else [self.value]
        }


# ========================
# Core Feature Representation
# ========================

@dataclass
class QuiltFeature:
    """A full feature definition in the Quilt system."""
    key: QuiltFeatureKey
    enabled: bool
    variants: Dict[QuiltVariant, QuiltWeight]
    rules: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    def __post_init__(self):
        if not isinstance(self.created_at, datetime):
            raise TypeError("created_at must be a datetime object")
        if not isinstance(self.updated_at, datetime):
            raise TypeError("updated_at must be a datetime object")
        if self.created_at.tzinfo is None:
            self.created_at = self.created_at.replace(tzinfo=timezone.utc)
        if self.updated_at.tzinfo is None:
            self.updated_at = self.updated_at.replace(tzinfo=timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "key": str(self.key),
            "enabled": self.enabled,
            "variants": dict(self.variants),
            "rules": [rule.to_dict() for rule in self.rules],
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QuiltFeature':
        return cls(
            key=QuiltFeatureKey(data["key"]),
            enabled=data["enabled"],
            variants={QuiltVariant(k): QuiltWeight(v) for k, v in data["variants"].items()},
            rules=[QuiltRuleCondition(**r) for r in data["rules"]],
            metadata=data["metadata"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )


# ========================
# Beta to Quilt Mapping
# ========================

def beta_tier_to_quilt(
    tier: BetaTier,
    feature_key: str,
    context: Optional[Dict[str, Any]] = None,
    weight: Optional[QuiltWeight] = None,
    variant: Optional[QuiltVariant] = None
) -> QuiltFeature:
    """
    Convert a Beta Family tier into a structured Quilt feature.

    Args:
        tier: The Beta Family tier (e.g., BetaTester)
        feature_key: The unique Quilt feature key
        context: Optional context (e.g., {"user_id": "123"})
        weight: Optional rollout weight (0.0 to 1.0)
        variant: Optional variant assignment

    Returns:
        A QuiltFeature object representing the tier.

    Raises:
        ValueError: If invalid weight or context provided.
    """
    if weight is not None and not isinstance(weight, QuiltWeight):
        raise TypeError("weight must be a QuiltWeight")

    # Default weight based on tier
    default_weight = {
        BetaTier.BETA_TESTER: QuiltWeight(0.25),
        BetaTier.ALPHA_TESTER: QuiltWeight(0.10),
        BetaTier.CANARY: QuiltWeight(0.05),
        BetaTier.SHADOW: QuiltWeight(0.01),
        BetaTier.STAGED_ROLLOUT: QuiltWeight(0.005),
    }.get(tier, QuiltWeight(0.0))

    # Default variant
    default_variant = {
        BetaTier.BETA_TESTER: QuiltVariant("beta"),
        BetaTier.ALPHA_TESTER: QuiltVariant("alpha"),
        BetaTier.CANARY: QuiltVariant("canary"),
        BetaTier.SHADOW: QuiltVariant("shadow"),
        BetaTier.STAGED_ROLLOUT: QuiltVariant("staged"),
    }.get(tier, QuiltVariant("default"))

    # Use provided or default values
    use_weight = weight if weight is not None else default_weight
    use_variant = variant if variant is not None else default_variant

    # Build rules based on tier
    rules = []
    if context:
        for key, value in context.items():
            rules.append(
                QuiltRuleCondition(
                    context_key=QuiltContextKey(key),
                    operator=QuiltRuleOperator.EQUALS,
                    value=QuiltContextValue(str(value))
                )
            )
    else:
        # Default: all users
        rules.append(
            QuiltRuleCondition(
                context_key=QuiltContextKey("user_id"),
                operator=QuiltRuleOperator.EQUALS,
                value=QuiltContextValue("all")
            )
        )

    # Meta
    metadata = {
        "tier": str(tier),
        "description": f"Feature flag for {tier.value} users",
        "owner": "engineering@company.com",
        "visibility": "internal",
        "source": "beta_family_bridge",
    }

    # Create feature
    now = datetime.now(timezone.utc)
    return QuiltFeature(
        key=QuiltFeatureKey(feature_key),
        enabled=True,
        variants={use_variant: use_weight},
        rules=rules,
        metadata=metadata,
        created_at=now,
        updated_at=now,
    )


def quilt_to_beta_tier(
    quilt_feature: QuiltFeature,
    context: Optional[Dict[str, Any]] = None
) -> Optional[BetaTier]:
    """
    Reconstruct the Beta Family tier from a Quilt feature and context.

    Args:
        quilt_feature: The Quilt feature to analyze
        context: The runtime context (e.g., {"user_id": "123"})

    Returns:
        The corresponding BetaTier, or None if not recognized.
    """
    if not quilt_feature.enabled:
        return None

    # Check metadata
    meta_tier = quilt_feature.metadata.get("tier")
    if meta_tier:
        try:
            return BetaTier(meta_tier)
        except ValueError:
            pass

    # Fallback: analyze variants and rules
    if not quilt_feature.variants:
        return None

    # Get the variant with the highest weight
    sorted_variants = sorted(quilt_feature.variants.items(), key=lambda x: x[1], reverse=True)
    top_variant, top_weight = sorted_variants[0]

    # Map variant to tier
    variant_to_tier = {
        "beta": BetaTier.BETA_TESTER,
        "alpha": BetaTier.ALPHA_TESTER,
        "canary": BetaTier.CANARY,
        "shadow": BetaTier.SHADOW,
        "staged": BetaTier.STAGED_ROLLOUT,
    }

    tier = variant_to_tier.get(str(top_variant))
    if not tier:
        return None

    # Validate weight range
    weight_map = {
        BetaTier.BETA_TESTER: (0.2, 0.3),
        BetaTier.ALPHA_TESTER: (0.08, 0.12),
        BetaTier.CANARY: (0.04, 0.06),
        BetaTier.SHADOW: (0.005, 0.015),
        BetaTier.STAGED_ROLLOUT: (0.004, 0.006),
    }

    min_w, max_w = weight_map.get(tier, (0, 0))
    if not (min_w <= float(top_weight) <= max_w):
        return None

    # Validate context rules (if provided)
    if context is None:
        return tier

    for rule in quilt_feature.rules:
        if rule.context_key == QuiltContextKey("user_id") and rule.operator == QuiltRuleOperator.EQUALS:
            if rule.value == QuiltContextValue("all"):
                continue
            if str(rule.value) not in context.get("user_id", ""):
                return None
        # Add more context validation as needed

    return tier


# ========================
# Utilities
# ========================

def is_valid_beta_tier(tier: str) -> bool:
    """Check if a string represents a valid BetaTier."""
    try:
        BetaTier(tier)
        return True
    except ValueError:
        return False


def validate_quilt_feature(quilt_feature: QuiltFeature) -> bool:
    """Validate that a QuiltFeature is well-formed."""
    if not isinstance(quilt_feature, QuiltFeature):
        return False
    if not isinstance(quilt_feature.key, QuiltFeatureKey):
        return False
    if not isinstance(quilt_feature.enabled, bool):
        return False
    if not isinstance(quilt_feature.variants, dict):
        return False
    if not all(isinstance(k, QuiltVariant) for k in quilt_feature.variants.keys()):
        return False
    if not all(isinstance(v, QuiltWeight) for v in quilt_feature.variants.values()):
        return False
    if not isinstance(quilt_feature.rules, list):
        return False
    if not all(isinstance(r, QuiltRuleCondition) for r in quilt_feature.rules):
        return False
    if not isinstance(quilt_feature.metadata, dict):
        return False
    if not isinstance(quilt_feature.created_at, datetime):
        return False
    if not isinstance(quilt_feature.updated_at, datetime):
        return False
    return True


def serialize_feature(quilt_feature: QuiltFeature) -> str:
    """Serialize a QuiltFeature to JSON."""
    return json.dumps(quilt_feature.to_dict(), indent=2)


def deserialize_feature(json_str: str) -> QuiltFeature:
    """Deserialize a QuiltFeature from JSON."""
    data = json.loads(json_str)
    return QuiltFeature.from_dict(data)


# ========================
# Unit Tests
# ========================

def test_beta_tier_to_quilt():
    """Test conversion from BetaTier to QuiltFeature."""
    feature_key = "user_profile_v2"
    context = {"user_id": "12345", "org_id": "67890"}

    for tier in BetaTier:
        feature = beta_tier_to_quilt(tier, feature_key, context, weight=QuiltWeight(0.15))
        assert isinstance(feature, QuiltFeature)
        assert feature.key == QuiltFeatureKey(feature_key)
        assert feature.enabled is True
        assert len(feature.variants) == 1
        assert feature.metadata["tier"] == str(tier)
        assert feature.metadata["description"].startswith(f"Feature flag for {tier.value}")

        # Check variant
        variant = list(feature.variants.keys())[0]
        assert variant in ["beta", "alpha", "canary", "shadow", "staged"]

        # Check weight
        weight = list(feature.variants.values())[0]
        assert 0.0 <= float(weight) <= 1.0

        # Check rules
        assert len(feature.rules) >= 1
        rule = feature.rules[0]
        assert rule.context_key in [QuiltContextKey("user_id"), QuiltContextKey("org_id")]
        assert rule.operator == QuiltRuleOperator.EQUALS
        assert isinstance(rule.value, QuiltContextValue)

    # Test invalid weight
    try:
        beta_tier_to_quilt(BetaTier.BETA_TESTER, "test", weight=QuiltWeight(1.5))
        assert False, "Should raise ValueError"
    except ValueError:
        pass


def test_quilt_to_beta_tier():
    """Test reconstruction of BetaTier from QuiltFeature."""
    # Test with metadata
    feature = QuiltFeature(
        key=QuiltFeatureKey("feature_x"),
        enabled=True,
        variants={QuiltVariant("alpha"): QuiltWeight(0.10)},
        rules=[QuiltRuleCondition(QuiltContextKey("user_id"), QuiltRuleOperator.EQUALS, "test_user")],
        metadata={"tier": "alpha-tester"},
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    assert quilt_to_beta_tier(feature, {"user_id": "test_user"}) == BetaTier.ALPHA_TESTER
    assert quilt_to_beta_tier(feature, {"user_id": "other_user"}) is None

    # Test with variant and weight
    feature2 = QuiltFeature(
        key=QuiltFeatureKey("feature_y"),
        enabled=True,
        variants={QuiltVariant("canary"): QuiltWeight(0.05)},
        rules=[QuiltRuleCondition(QuiltContextKey("user_id"), QuiltRuleOperator.EQUALS, "canary_user")],
        metadata={},
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    assert quilt_to_beta_tier(feature2, {"user_id": "canary_user"}) == BetaTier.CANARY

    # Test invalid variant
    feature3 = QuiltFeature(
        key=QuiltFeatureKey("feature_z"),
        enabled=True,
        variants={QuiltVariant("unknown"): QuiltWeight(0.10)},
        rules=[],
        metadata={},
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    assert quilt_to_beta_tier(feature3, {}) is None

    # Test invalid weight
    feature4 = QuiltFeature(
        key=QuiltFeatureKey("feature_w"),
        enabled=True,
        variants={QuiltVariant("beta"): QuiltWeight(0.5)},
        rules=[],
        metadata={},
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    assert quilt_to_beta_tier(feature4, {}) is None


def test_serialization():
    """Test serialization and deserialization."""
    feature = beta_tier_to_quilt(
        BetaTier.BETA_TESTER,
        "test_feature",
        {"user_id": "12345"},
        weight=QuiltWeight(0.25)
    )
    json_str = serialize_feature(feature)
    loaded_feature = deserialize_feature(json_str)
    assert isinstance(loaded_feature, QuiltFeature)
    assert feature.key == loaded_feature.key
    assert feature.enabled == loaded_feature.enabled
    assert feature.variants == loaded_feature.variants
    assert feature.rules == loaded_feature.rules
    assert feature.metadata == loaded_feature.metadata


def test_validations():
    """Test validation utilities."""
    # Valid feature
    valid_feature = QuiltFeature(
        key=QuiltFeatureKey("valid"),
        enabled=True,
        variants={QuiltVariant("beta"): QuiltWeight(0.25)},
        rules=[QuiltRuleCondition(QuiltContextKey("user_id"), QuiltRuleOperator.EQUALS, "test")],
        metadata={"tier": "beta-tester"},
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    assert validate_quilt_feature(valid_feature) is True

    # Invalid feature
    invalid_feature = {"not": "a", "feature": "dict"}
    assert validate_quilt_feature(invalid_feature) is False

    # Valid tier
    assert is_valid_beta_tier("beta-tester") is True
    assert is_valid_beta_tier("invalid-tier") is False


if __name__ == "__main__":
    # Run tests
    print("Running tests...")
    test_beta_tier_to_quilt()
    test_quilt_to_beta_tier()
    test_serialization()
    test_validations()
    print("All tests passed.")
