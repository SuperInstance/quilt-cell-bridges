"""
Tests for the Quilt Bridge Compiler

Run: python3 -m unittest test_bridge_compiler
"""
import unittest
import sys
import os
from pathlib import Path

# Add bridges to path
sys.path.insert(0, str(Path(__file__).parent))

from bridge_compiler import BridgeCompiler


class TestBridgeCompiler(unittest.TestCase):
    """Test the bridge compiler."""
    
    def setUp(self):
        self.compiler = BridgeCompiler()
    
    def test_compiler_instantiates(self):
        """Compiler can be instantiated."""
        self.assertIsNotNone(self.compiler)
    
    def test_bridges_generated(self):
        """Bridges were generated to the output dir."""
        self.compiler.generate_all_bridges()
        output = Path(self.compiler.output_dir)
        self.assertTrue(output.exists())
        files = list(output.glob("*.py"))
        self.assertGreater(len(files), 0)
    
    def test_postgresql_bridge_works(self):
        """The PostgreSQL bridge has working to_ledger/from_ledger."""
        sys.path.insert(0, str(Path(self.compiler.output_dir).parent))
        from _generated.postgresql import Bridge_PostgreSQL
        
        b = Bridge_PostgreSQL()
        original = {"id": 1, "name": "test", "value": 3.14}
        ledger = b.to_ledger(original)
        self.assertIn("header", ledger)
        self.assertIn("payload", ledger)
        back = b.from_ledger(ledger)
        self.assertEqual(back["id"], 1)
        self.assertEqual(back["name"], "test")
    
    def test_csv_bridge_works(self):
        """The CSV bridge has working to_ledger/from_ledger."""
        from _generated.csv import Bridge_CSV
        
        b = Bridge_CSV()
        original = {"id": "1", "name": "test", "value": "3.14"}
        ledger = b.to_ledger(original)
        back = b.from_ledger(ledger)
        self.assertIsInstance(back, dict)
    
    def test_mongodb_bridge_works(self):
        """The MongoDB bridge has working to_ledger/from_ledger."""
        from _generated.mongodb import Bridge_MongoDB
        
        b = Bridge_MongoDB()
        original = {"_id": "abc", "name": "test", "value": 42}
        ledger = b.to_ledger(original)
        back = b.from_ledger(ledger)
        self.assertIsInstance(back, dict)


if __name__ == "__main__":
    unittest.main()
