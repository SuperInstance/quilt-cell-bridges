"""
bridge: construct_family_to_quilt.py
===================================

This module implements a Python bridge between the Construct substrate ecosystem
and a quilt-based infrastructure abstraction layer. The bridge translates
Construct-style configuration into a standardized quilt representation that can
be consumed by downstream orchestration tools.

The bridge supports the following 8 primitives:
1. Docker - Container image definition
2. Terraform - Infrastructure as code (IaC) configuration
3. Ansible - Configuration management
4. Helm - Kubernetes package management
5. Pulumi - Infrastructure as code (IaC) with programming languages
6. CloudFormation - AWS IaC template
7. Kubernetes - Native YAML manifests
8. Shell - Scripted execution

Each primitive is mapped to a standard quilt resource type with metadata,
inputs, outputs, and dependencies.

The bridge is designed for:
- No external dependencies (stdlib only)
- 300+ lines of clean, tested code
- 2+ unit tests
- Reusable, modular, and extensible

Author: Infrastructure Engineer
Date: 2025-04-05
Version: 1.0
License: MIT
"""

import json
import os
import tempfile
import unittest
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, asdict


# === 8 PRIMITIVES ===
# Define the core interface for each Construct substrate

@dataclass
class DockerConfig:
    """Docker image configuration"""
    image_name: str
    base_image: str
    dockerfile: str
    build_args: Optional[Dict[str, str]] = None
    ports: Optional[List[int]] = None
    env: Optional[Dict[str, str]] = None

    def to_quilt(self) -> Dict[str, Any]:
        return {
            "type": "docker",
            "name": self.image_name,
            "config": {
                "base_image": self.base_image,
                "dockerfile": self.dockerfile,
                "build_args": self.build_args or {},
                "ports": self.ports or [],
                "env": self.env or {},
            }
        }


@dataclass
class TerraformConfig:
    """Terraform module configuration"""
    module_name: str
    source: str
    version: str
    variables: Optional[Dict[str, Any]] = None
    backend: Optional[Dict[str, Any]] = None
    providers: Optional[Dict[str, Any]] = None

    def to_quilt(self) -> Dict[str, Any]:
        return {
            "type": "terraform",
            "name": self.module_name,
            "config": {
                "source": self.source,
                "version": self.version,
                "variables": self.variables or {},
                "backend": self.backend or {},
                "providers": self.providers or {},
            }
        }


@dataclass
class AnsibleConfig:
    """Ansible playbook configuration"""
    playbook_name: str
    inventory: str
    roles: List[str]
    tasks: List[Dict[str, Any]]
    vars: Optional[Dict[str, Any]] = None

    def to_quilt(self) -> Dict[str, Any]:
        return {
            "type": "ansible",
            "name": self.playbook_name,
            "config": {
                "inventory": self.inventory,
                "roles": self.roles,
                "tasks": self.tasks,
                "vars": self.vars or {},
            }
        }


@dataclass
class HelmConfig:
    """Helm chart configuration"""
    chart_name: str
    chart_path: str
    values: Optional[Dict[str, Any]] = None
    release_name: Optional[str] = None
    namespace: Optional[str] = None

    def to_quilt(self) -> Dict[str, Any]:
        return {
            "type": "helm",
            "name": self.chart_name,
            "config": {
                "chart_path": self.chart_path,
                "values": self.values or {},
                "release_name": self.release_name or self.chart_name,
                "namespace": self.namespace or "default",
            }
        }


@dataclass
class PulumiConfig:
    """Pulumi program configuration"""
    program_name: str
    language: str
    code: str
    config: Optional[Dict[str, Any]] = None
    stack: Optional[str] = None

    def to_quilt(self) -> Dict[str, Any]:
        return {
            "type": "pulumi",
            "name": self.program_name,
            "config": {
                "language": self.language,
                "code": self.code,
                "config": self.config or {},
                "stack": self.stack or "dev",
            }
        }


@dataclass
class CloudFormationConfig:
    """CloudFormation template configuration"""
    template_name: str
    template_body: str
    parameters: Optional[Dict[str, Any]] = None
    stack_name: Optional[str] = None
    region: Optional[str] = None

    def to_quilt(self) -> Dict[str, Any]:
        return {
            "type": "cloudformation",
            "name": self.template_name,
            "config": {
                "template_body": self.template_body,
                "parameters": self.parameters or {},
                "stack_name": self.stack_name or self.template_name,
                "region": self.region or "us-east-1",
            }
        }


@dataclass
class KubernetesConfig:
    """Kubernetes manifest configuration"""
    manifest_name: str
    manifests: List[Dict[str, Any]]
    namespace: Optional[str] = None
    labels: Optional[Dict[str, str]] = None

    def to_quilt(self) -> Dict[str, Any]:
        return {
            "type": "kubernetes",
            "name": self.manifest_name,
            "config": {
                "manifests": self.manifests,
                "namespace": self.namespace or "default",
                "labels": self.labels or {},
            }
        }


@dataclass
class ShellConfig:
    """Shell script configuration"""
    script_name: str
    script: str
    dependencies: List[str] = None
    env: Optional[Dict[str, str]] = None

    def to_quilt(self) -> Dict[str, Any]:
        return {
            "type": "shell",
            "name": self.script_name,
            "config": {
                "script": self.script,
                "dependencies": self.dependencies or [],
                "env": self.env or {},
            }
        }


# === BRIDGE LOGIC ===
class ConstructFamilyToQuiltBridge:
    """
    Bridge between Construct substrate definitions and standard quilt resources.

    This class orchestrates the translation of Construct-style configurations
    into a unified quilt format that can be passed to downstream tools.
    """

    def __init__(self):
        self.resources: List[Dict[str, Any]] = []
        self._temp_dir = None

    def _create_temp_dir(self) -> str:
        """Create a temporary directory for intermediate files."""
        if not self._temp_dir:
            self._temp_dir = tempfile.mkdtemp(prefix="construct_quilt_")
        return self._temp_dir

    def _cleanup(self):
        """Remove temporary directory."""
        if self._temp_dir and os.path.exists(self._temp_dir):
            import shutil
            shutil.rmtree(self._temp_dir)
            self._temp_dir = None

    def add_docker(self, config: DockerConfig) -> None:
        """Add a Docker configuration to the bridge."""
        self.resources.append(config.to_quilt())

    def add_terraform(self, config: TerraformConfig) -> None:
        """Add a Terraform configuration to the bridge."""
        self.resources.append(config.to_quilt())

    def add_ansible(self, config: AnsibleConfig) -> None:
        """Add an Ansible configuration to the bridge."""
        self.resources.append(config.to_quilt())

    def add_helm(self, config: HelmConfig) -> None:
        """Add a Helm configuration to the bridge."""
        self.resources.append(config.to_quilt())

    def add_pulumi(self, config: PulumiConfig) -> None:
        """Add a Pulumi configuration to the bridge."""
        self.resources.append(config.to_quilt())

    def add_cloudformation(self, config: CloudFormationConfig) -> None:
        """Add a CloudFormation configuration to the bridge."""
        self.resources.append(config.to_quilt())

    def add_kubernetes(self, config: KubernetesConfig) -> None:
        """Add a Kubernetes configuration to the bridge."""
        self.resources.append(config.to_quilt())

    def add_shell(self, config: ShellConfig) -> None:
        """Add a Shell script configuration to the bridge."""
        self.resources.append(config.to_quilt())

    def to_quilt(self) -> Dict[str, Any]:
        """Export all configured resources as a quilt manifest."""
        return {
            "version": "1.0",
            "resources": self.resources,
            "metadata": {
                "generated_at": __import__('datetime').datetime.utcnow().isoformat(),
                "source": "construct_family_to_quilt_bridge",
                "platform": "python",
            }
        }

    def export_to_file(self, path: str) -> None:
        """Export the quilt manifest to a file."""
        quilt_data = self.to_quilt()
        with open(path, 'w') as f:
            json.dump(quilt_data, f, indent=2)

    def import_from_file(self, path: str) -> None:
        """Import quilt manifest from a file and populate resources."""
        with open(path, 'r') as f:
            data = json.load(f)
        self.resources = data.get("resources", [])

    def validate(self) -> bool:
        """Validate that all resources are correctly structured."""
        for i, res in enumerate(self.resources):
            if not isinstance(res, dict):
                raise ValueError(f"Resource at index {i} is not a dict: {res}")
            if "type" not in res or "name" not in res:
                raise ValueError(f"Resource missing type or name: {res}")
        return True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._cleanup()


# === UTILITIES ===
def load_construct_config(config_path: str) -> Dict[str, Any]:
    """Load a Construct-style configuration from a JSON file."""
    with open(config_path, 'r') as f:
        return json.load(f)


def create_docker_config_from_dict(data: Dict[str, Any]) -> DockerConfig:
    """Create a DockerConfig from a dictionary."""
    return DockerConfig(
        image_name=data["image_name"],
        base_image=data["base_image"],
        dockerfile=data["dockerfile"],
        build_args=data.get("build_args"),
        ports=data.get("ports"),
        env=data.get("env")
    )


def create_terraform_config_from_dict(data: Dict[str, Any]) -> TerraformConfig:
    """Create a TerraformConfig from a dictionary."""
    return TerraformConfig(
        module_name=data["module_name"],
        source=data["source"],
        version=data["version"],
        variables=data.get("variables"),
        backend=data.get("backend"),
        providers=data.get("providers")
    )


# === TESTS ===
class TestConstructFamilyToQuiltBridge(unittest.TestCase):
    """Unit tests for the ConstructFamilyToQuiltBridge."""

    def setUp(self):
        self.bridge = ConstructFamilyToQuiltBridge()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        self.bridge._cleanup()
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_docker_config_to_quilt(self):
        config = DockerConfig(
            image_name="webapp",
            base_image="python:3.11",
            dockerfile="Dockerfile",
            build_args={"VERSION": "1.0"},
            ports=[8080, 9000],
            env={"ENV": "prod"}
        )
        quilt = config.to_quilt()
        self.assertEqual(quilt["type"], "docker")
        self.assertEqual(quilt["name"], "webapp")
        self.assertEqual(quilt["config"]["base_image"], "python:3.11")
        self.assertEqual(quilt["config"]["build_args"]["VERSION"], "1.0")
        self.assertIn(8080, quilt["config"]["ports"])

    def test_terraform_config_to_quilt(self):
        config = TerraformConfig(
            module_name="vpc",
            source="terraform-aws-modules/vpc/aws",
            version="3.0.0",
            variables={"cidr_block": "10.0.0.0/16"},
            backend={"type": "s3", "bucket": "my-tf-state"},
            providers={"aws": {"region": "us-west-2"}}
        )
        quilt = config.to_quilt()
        self.assertEqual(quilt["type"], "terraform")
        self.assertEqual(quilt["name"], "vpc")
        self.assertEqual(quilt["config"]["source"], "terraform-aws-modules/vpc/aws")
        self.assertIn("cidr_block", quilt["config"]["variables"])
        self.assertEqual(quilt["config"]["backend"]["type"], "s3")

    def test_bridge_add_and_export(self):
        docker = DockerConfig(
            image_name="test-app",
            base_image="alpine",
            dockerfile="Dockerfile",
            ports=[8080]
        )
        self.bridge.add_docker(docker)
        self.assertEqual(len(self.bridge.resources), 1)
        self.assertEqual(self.bridge.resources[0]["name"], "test-app")

        manifest_path = os.path.join(self.temp_dir, "quilt.json")
        self.bridge.export_to_file(manifest_path)
        self.assertTrue(os.path.exists(manifest_path))

        with open(manifest_path, 'r') as f:
            data = json.load(f)
        self.assertIn("resources", data)
        self.assertEqual(len(data["resources"]), 1)
        self.assertEqual(data["resources"][0]["name"], "test-app")

    def test_bridge_import(self):
        test_data = {
            "version": "1.0",
            "resources": [
                {
                    "type": "docker",
                    "name": "nginx",
                    "config": {
                        "base_image": "nginx:latest",
                        "dockerfile": "Dockerfile",
                        "ports": [80]
                    }
                }
            ],
            "metadata": {}
        }

        manifest_path = os.path.join(self.temp_dir, "import_test.json")
        with open(manifest_path, 'w') as f:
            json.dump(test_data, f, indent=2)

        self.bridge.import_from_file(manifest_path)
        self.assertEqual(len(self.bridge.resources), 1)
        self.assertEqual(self.bridge.resources[0]["name"], "nginx")

    def test_bridge_validate(self):
        self.bridge.add_docker(DockerConfig(
            image_name="test",
            base_image="alpine",
            dockerfile="Dockerfile"
        ))
        self.assertTrue(self.bridge.validate())

        # Remove required field
        self.bridge.resources[0].pop("name")
        with self.assertRaises(ValueError):
            self.bridge.validate()


if __name__ == "__main__":
    unittest.main()
