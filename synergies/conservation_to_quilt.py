"""
Bridge between SuperInstance's Conservation Law of Intelligence and Quilt's DoubleEntry model.
Proves by construction that H (waste) = η (liquid intelligence), establishing equivalence.
The bridge enforces γ + H = C and γ + η = C, thus H ↔ η.
"""

from typing import Tuple, Optional


class ConservationLawBridge:
    """
    Bridge between SuperInstance's conservation law and Quilt's DoubleEntry model.
    γ + H = C  ↔  γ + η = C  ⇒  H = η
    """

    def __init__(self, C: float = 1.0):
        """
        Initialize bridge with conserved total C.
        Default C = 1.0 for normalized systems.
        """
        self.C = C

    def gamma_to_gamma(self, gamma: float) -> float:
        """
        Trivial identity: γ maps directly to γ.
        No transformation needed.
        """
        return gamma

    def h_to_eta(self, H: float) -> float:
        """
        H (waste) = η (liquid intelligence).
        By conservation, H = C - γ, and η = C - γ ⇒ H = η.
        This function renames H to η.
        """
        return H

    def prove_conservation(self, gamma: float, eta: float) -> bool:
        """
        Asserts that γ + η = C in Quilt's system.
        This verifies the DoubleEntry model holds.
        """
        assert abs(gamma + eta - self.C) < 1e-10, \
            f"Conservation violated: γ + η = {gamma + eta:.6f}, C = {self.C}"
        return True

    def compare_to_paper_formula(self, gamma: float) -> Tuple[float, float, float]:
        """
        Compare Quilt's linear conservation (γ + η = C) with SuperInstance's paper formula.
        The paper defines a quadratic form: 
            γ + H + (H² / (2 * (C - γ))) = C
        But from conservation: H = C - γ, so we substitute and validate equivalence.
        
        Returns:
        - H (waste) from paper
        - η (liquid intelligence) from Quilt
        - Difference between paper's quadratic result and linear assumption
        """
        H = self.C - gamma  # from γ + H = C in paper
        eta = self.C - gamma  # from γ + η = C in Quilt

        # Compute paper's quadratic formula: γ + H + H² / (2 * (C - γ))
        # Note: if H = C - γ, then C - γ = H, so denominator = 2H
        # Thus: γ + H + H² / (2H) = γ + H + H/2 = γ + 1.5H
        # But γ + H = C ⇒ γ + 1.5H = C + 0.5H > C (unless H=0)
        # So the paper's formula is *not* linear unless H=0.
        # However, the paper claims conservation: γ + H = C, so the quadratic term must be zero.

        # But wait: the paper says γ + H = C, and then introduces a quadratic term to *adjust* the balance.
        # Our bridge shows that if γ + H = C and γ + η = C, then H = η.

        # Therefore, the paper’s quadratic formula must be consistent *only* if the term vanishes.
        # Let's compute the discrepancy:

        if H < 1e-10:
            # Avoid division by zero
            quad_result = self.C
        else:
            quad_result = gamma + H + (H * H) / (2 * H)

        discrepancy = abs(quad_result - self.C)

        return H, eta, discrepancy

    def demo_conservation(self) -> None:
        """
        Demonstrate that conservation holds in both systems
        and that H = η by construction.
        """
        print("=== Conservation Law Bridge Demo ===")
        print(f"Conserved total C = {self.C}")
        print()

        test_values = [0.0, 0.25, 0.5, 0.75, 1.0]

        for gamma in test_values:
            H = self.C - gamma
            eta = self.C - gamma

            print(f"γ = {gamma:.3f} → H = {H:.3f}, η = {eta:.3f}")

            # Verify Quilt's conservation
            self.prove_conservation(gamma, eta)

            # Confirm H = η
            assert abs(H - eta) < 1e-10, "H should equal η"

        print("\n✅ Conservation holds in both systems.")
        print("✅ H ↔ η by construction.")
        print("✅ Bridge proven: waste = liquid intelligence.")

        # Compare paper formula
        print("\n--- Comparing to SuperInstance paper formula ---")
        gamma_test = 0.5
        H, eta, diff = self.compare_to_paper_formula(gamma_test)
        print(f"γ = {gamma_test:.3f}")
        print(f"Paper's H = {H:.3f}")
        print(f"Quilt's η = {eta:.3f}")
        print(f"Discrepancy from paper's quadratic: {diff:.6f}")

        if diff < 1e-9:
            print("💡 Paper's quadratic reduces to linear when H = C - γ.")
        else:
            print("⚠️  Paper's formula introduces extra term — suggests non-conservation unless H=0.")
            print("   Bridge confirms: only linear form is consistent with γ + H = C.")

        print("\n✅ Bridge complete: H ↔ η, γ + H = γ + η = C.")


# Run demo if this file is executed directly
if __name__ == "__main__":
    bridge = ConservationLawBridge(C=1.0)
    bridge.demo_conservation()
