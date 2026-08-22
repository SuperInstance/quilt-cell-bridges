"""
quilt-jetson (SuperInstance) ↔ Quilt Cell Bridge

The SuperInstance quilt-jetson is a Quilt reactive runtime for NVIDIA Jetson
devices — edge ML, ROS2, vision, federation. The MISSING MID-TIER in the
Quilt federation story.

Features:
- 8 cell kinds + vision primitives
- Async engine with tokio
- ROS2 bridge
- Web UI on port 8080 (axum + WebSocket)
- Federation
- SQLite storage
- Vision (camera, IMU, sensors)

THE CRUCIAL INSIGHT: quilt-jetson IS Quilt for edge devices. Same 8 primitives,
running on ARM64, talking to ROS2 and cameras. The federation story connects
the cloud Quilt to the edge.

Map:
- Cell kind → Quilt cell kind
- Vision cell → Quilt cell with Vibe (camera state)
- ROS2 message → Murmur
- Federation → Graph (federated cells)
- Edge runtime → JEPA (predict on edge, train on cloud)
- SQLite → tape (persistent)
"""

from typing import Dict, List, Any, Optional, Tuple


class VisionCell:
    """A Quilt cell for vision (camera state)."""
    def __init__(self, name: str, source: str = 'camera'):
        self.name = name
        self.source = source  # camera, imu, lidar
        self.gamma = 0.5
        self.eta = 0.5
        self.last_frame = None
        self.fps = 30.0  # Vibe (rate of change)

    def to_quilt(self) -> Dict[str, Any]:
        """Convert to a Quilt cell."""
        return {
            'name': self.name,
            'kind': 'vision',
            'source': self.source,
            'fps': self.fps,
            'gamma': self.gamma,
            'eta': self.eta,
        }


class Ros2Bridge:
    """A ROS2 bridge as a Murmur channel."""
    def __init__(self):
        self.topics: Dict[str, List[Dict[str, Any]]] = {}

    def publish(self, topic: str, msg: Any) -> None:
        """Publish a ROS2 message. Murmur."""
        if topic not in self.topics:
            self.topics[topic] = []
        self.topics[topic].append(msg)


class Federation:
    """A federation of Quilt instances."""
    def __init__(self):
        self.instances: Dict[str, Dict[str, Any]] = {}
        self.edges: List[Tuple[str, str]] = []

    def add_instance(self, name: str, kind: str, location: str) -> None:
        """Add a federated instance."""
        self.instances[name] = {
            'name': name,
            'kind': kind,  # edge, cloud, server
            'location': location,
            'gamma': 0.5,
            'eta': 0.5,
        }

    def connect(self, a: str, b: str) -> None:
        """Connect two instances. Graph edge."""
        self.edges.append((a, b))


class QuiltJetsonBridge:
    """A Quilt-Jetson runtime as a Quilt instance."""

    def __init__(self, device: str = 'jetson_orin'):
        self.device = device
        # 8 cell kinds
        self.cell_kinds = ['number', 'string', 'boolean', 'array', 'object', 'formula', 'cell', 'sheet']
        # Plus vision
        self.vision_cells: Dict[str, VisionCell] = {}
        # ROS2 bridge
        self.ros2 = Ros2Bridge()
        # Federation
        self.federation = Federation()
        # All cells
        self.cells: Dict[str, Dict[str, Any]] = {}
        # SQLite tape
        self.tape: List[Dict[str, Any]] = []

    def add_vision_cell(self, name: str, source: str = 'camera') -> VisionCell:
        """Add a vision cell. Vibe for camera state."""
        cell = VisionCell(name, source)
        self.vision_cells[name] = cell
        self.cells[name] = cell.to_quilt()
        return cell

    def ros2_publish(self, topic: str, msg: Any) -> None:
        """Publish to ROS2. Murmur."""
        self.ros2.publish(topic, msg)
        # Also write to tape
        self.tape.append({'topic': topic, 'msg': msg, 'kind': 'murmur'})

    def federate(self, name: str, kind: str, location: str) -> None:
        """Add a federated instance."""
        self.federation.add_instance(name, kind, location)

    def tick(self) -> None:
        """Run a tick. JEPA prediction on edge."""
        # Update vision cells
        for cell in self.vision_cells.values():
            # In a real implementation, this would read from a camera
            pass
        # Invalidate tape periodically
        if len(self.tape) > 1000:
            self.tape = self.tape[-500:]


if __name__ == "__main__":
    print("=" * 60)
    print("QUILT-JETSON ↔ QUILT CELL BRIDGE")
    print("=" * 60)
    print()
    print("Quilt for NVIDIA Jetson (edge ML, ROS2, vision).")
    print("The missing mid-tier in the Quilt federation story.")
    print()

    qj = QuiltJetsonBridge(device='jetson_orin')

    # Add vision cells
    cam = qj.add_vision_cell('front_camera', source='camera')
    imu = qj.add_vision_cell('imu', source='imu')
    print(f"Vision cells: {list(qj.vision_cells.keys())}")
    print()

    # ROS2 publish
    qj.ros2_publish('/cmd_vel', {'linear': 1.0, 'angular': 0.5})
    qj.ros2_publish('/odom', {'x': 1.0, 'y': 0.0})
    print(f"ROS2 topics: {list(qj.ros2.topics.keys())}")
    print(f"ROS2 messages: {sum(len(v) for v in qj.ros2.topics.values())}")
    print()

    # Federation
    qj.federate('edge_orin', 'edge', 'workshop')
    qj.federate('cloud_quilt', 'cloud', 'us-west-2')
    qj.federation.connect('edge_orin', 'cloud_quilt')
    print(f"Federation: {list(qj.federation.instances.keys())}")
    print(f"Federation edges: {qj.federation.edges}")
    print()

    # Tick
    qj.tick()
    print(f"Tape length: {len(qj.tape)}")
    print()

    # Conservation
    n = len(qj.cells) + len(qj.federation.instances)
    total = sum(c.get('gamma', 0) + c.get('eta', 0) for c in qj.cells.values()) + \
            sum(i['gamma'] + i['eta'] for i in qj.federation.instances.values())
    print(f"Conservation: {n} entities, γ+η={total:.2f} (should be {n})")
    print()

    print("=" * 60)
    print("Iron sharpens iron.")
    print("quilt-jetson IS Quilt for edge devices.")
    print("Same 8 primitives, running on ARM64.")
    print("The cloud Quilt ↔ the edge Quilt.")


if __name__ == "__main__":
    demo()
