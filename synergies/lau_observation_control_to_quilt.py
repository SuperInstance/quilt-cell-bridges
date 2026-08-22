"""
lau-observation-control (SuperInstance) ↔ Quilt Cell Bridge

The SuperInstance lau-observation-control (Rust) formalizes the
observe-predict-control loop as a category-theoretic adjunction:
- Observation functor (left adjoint): sheaf pullback / measurement
- Control functor (right adjoint): pushforward / actuation
- Unit of the adjunction = Kalman filter
- Counit = LQR optimal control
- Triangle identities verified computationally

THE CRUCIAL INSIGHT: The observe-predict-control loop IS the Quilt runtime.
Observation is Z_in. Prediction is JEPA. Control is Z_out. Kalman IS the
watch integrating over time. LQR IS DoubleEntry optimization.

Map:
- World state → Quilt cell graph
- Observation → Z_in (read cells)
- Internal model → JEPA (predict)
- Actuation → Z_out (write cells)
- Kalman filter → watch integrator
- LQR → DoubleEntry (γ+η=1 optimization)
- Adjunction → Murmur (inter-cell)
"""

from typing import Dict, List, Any, Tuple
import math


class StateCell:
    """A Quilt cell representing a system state."""
    def __init__(self, name: str, value: float = 0.0):
        self.name = name
        self.value = value
        self.variance = 1.0  # Uncertainty
        self.gamma = 0.5
        self.eta = 0.5

    def __repr__(self):
        return f"State({self.name}={self.value:.2f}±{self.variance:.2f})"


class ObservationControlBridge:
    """Observe-predict-control loop on Quilt cells."""

    def __init__(self, process_noise: float = 0.1, measurement_noise: float = 0.5):
        # Cells = state
        self.states: Dict[str, StateCell] = {}
        # Process model: x' = F*x + B*u
        self.F = 1.0  # State transition
        self.B = 1.0  # Control input
        # Measurement model: z = H*x
        self.H = 1.0
        # Noise
        self.Q = process_noise  # Process noise
        self.R = measurement_noise  # Measurement noise
        # Covariance
        self.P = 1.0
        # Measurements
        self.measurements: List[float] = []

    def add_state(self, name: str, value: float = 0.0) -> StateCell:
        """Add a state cell."""
        cell = StateCell(name, value)
        self.states[name] = cell
        return cell

    def predict(self) -> StateCell:
        """Predict step. JEPA: predict the next state."""
        # x_pred = F * x
        for cell in self.states.values():
            cell.value = self.F * cell.value
            # P_pred = F * P * F + Q
            self.P = self.F * self.P * self.F + self.Q
        return list(self.states.values())[0] if self.states else None

    def observe(self, measurement: float) -> None:
        """Observe step. Z_in: read a measurement."""
        self.measurements.append(measurement)

    def update_kalman(self) -> None:
        """Update step. Kalman filter = watch integrator."""
        if not self.measurements or not self.states:
            return
        z = self.measurements[-1]
        # Innovation
        for cell in self.states.values():
            y = z - self.H * cell.value
            # Kalman gain
            S = self.H * self.P * self.H + self.R
            K = self.P * self.H / S
            # Update state
            cell.value = cell.value + K * y
            # Update covariance
            self.P = (1 - K * self.H) * self.P
            # Update variance
            cell.variance = self.P

    def lqr_control(self, target: float) -> float:
        """LQR control. DoubleEntry: γ+η=1 optimization."""
        if not self.states:
            return 0.0
        # Get current state
        x = list(self.states.values())[0].value
        # LQR: u = -K * (x - target)
        # Simplified: K = 1 for single-state
        error = x - target
        return -1.0 * error

    def control(self, u: float) -> None:
        """Apply control. Z_out."""
        for cell in self.states.values():
            cell.value += self.B * u

    def step(self, measurement: float, target: float) -> Dict[str, Any]:
        """Run one observe-predict-control step."""
        self.observe(measurement)
        self.predict()
        self.update_kalman()
        u = self.lqr_control(target)
        self.control(u)
        return {
            'state': list(self.states.values())[0].value if self.states else 0,
            'variance': list(self.states.values())[0].variance if self.states else 0,
            'control': u,
            'measurement': measurement,
        }


if __name__ == "__main__":
    print("=" * 60)
    print("LAU-OBSERVATION-CONTROL ↔ QUILT CELL BRIDGE")
    print("=" * 60)
    print()
    print("Observe-Predict-Control loop on Quilt cells.")
    print("Kalman IS the watch. LQR IS DoubleEntry.")
    print()

    oc = ObservationControlBridge(process_noise=0.1, measurement_noise=0.5)
    oc.add_state("position", value=0.0)

    print("Initial state:", oc.states["position"])
    print()

    # Run 10 steps with noisy measurements
    import random
    random.seed(42)
    print("Observe-Predict-Control loop:")
    for i in range(10):
        true_position = i * 0.5
        measurement = true_position + random.gauss(0, 0.5)
        result = oc.step(measurement=measurement, target=5.0)
        print(f"  Step {i}: measured={measurement:.2f}, state={result['state']:.2f}±{result['variance']:.2f}, control={result['control']:.2f}")
    print()

    # Conservation
    n = len(oc.states)
    total = sum(s.gamma + s.eta for s in oc.states.values())
    print(f"Conservation: {n} states, γ+η={total:.2f} (should be {n})")
    print()

    print("=" * 60)
    print("Iron sharpens iron.")
    print("The observe-predict-control loop IS the Quilt runtime.")
    print("Kalman IS the watch. LQR IS DoubleEntry.")


if __name__ == "__main__":
    demo()
