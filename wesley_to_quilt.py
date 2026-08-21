#!/usr/bin/env python3
"""
Wesley to Quilt Converter
Converts the wesley repo structure to a Quilt sheet (.qzt format)
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any

class WesleyToQuilt:
    """Converts wesley repo cells to Quilt sheet format"""
    
    def __init__(self):
        self.cells = {}
        self.relationships = []
        
    def define_cells(self):
        """Define all 5 wesley cells with their state, methods, and transitions"""
        
        # 1. WesleyCore - The ensign's main loop
        self.cells['WesleyCore'] = {
            'id': 'wesley_core',
            'name': 'WesleyCore',
            'type': 'core',
            'description': 'The ensign\'s main loop - orchestrates all operations',
            'state': {
                'status': ['idle', 'running', 'paused', 'error'],
                'current_operation': None,
                'last_heartbeat': None,
                'active_cells': []
            },
            'methods': [
                'initialize()',
                'run_main_loop()',
                'pause_operations()',
                'resume_operations()',
                'shutdown()',
                'monitor_cells()'
            ],
            'transitions': {
                'idle_to_running': 'initialize() called',
                'running_to_paused': 'pause_operations() called',
                'paused_to_running': 'resume_operations() called',
                'any_to_error': 'critical failure detected',
                'error_to_idle': 'recovery procedure completed'
            }
        }
        
        # 2. ReceiptSorter - Categorizes incoming items
        self.cells['ReceiptSorter'] = {
            'id': 'receipt_sorter',
            'name': 'ReceiptSorter',
            'type': 'processor',
            'description': 'Categorizes incoming items and receipts',
            'state': {
                'status': ['ready', 'processing', 'waiting', 'error'],
                'current_batch': None,
                'categorization_rules': ['beverage', 'inventory', 'supplies', 'misc'],
                'processed_count': 0
            },
            'methods': [
                'sort_receipt(receipt)',
                'categorize_item(item)',
                'batch_process(items)',
                'update_rules(rules)',
                'get_statistics()'
            ],
            'transitions': {
                'ready_to_processing': 'new batch received',
                'processing_to_ready': 'batch completed',
                'processing_to_waiting': 'awaiting more data',
                'waiting_to_processing': 'data received',
                'any_to_error': 'categorization failure'
            }
        }
        
        # 3. VectorDB - The growing embedding database
        self.cells['VectorDB'] = {
            'id': 'vector_db',
            'name': 'VectorDB',
            'type': 'storage',
            'description': 'Growing embedding database for semantic search',
            'state': {
                'status': ['initializing', 'active', 'indexing', 'backup', 'error'],
                'vector_count': 0,
                'dimensions': 768,
                'index_type': 'HNSW',
                'last_index_update': None
            },
            'methods': [
                'add_embedding(vector)',
                'search(query_vector, k)',
                'build_index()',
                'optimize_index()',
                'backup_database()',
                'restore_database()'
            ],
            'transitions': {
                'initializing_to_active': 'initialization complete',
                'active_to_indexing': 'index rebuild triggered',
                'indexing_to_active': 'index build complete',
                'active_to_backup': 'backup initiated',
                'backup_to_active': 'backup complete',
                'any_to_error': 'database corruption detected'
            }
        }
        
        # 4. CountingEngine - Counts bottles and inventory
        self.cells['CountingEngine'] = {
            'id': 'counting_engine',
            'name': 'CountingEngine',
            'type': 'processor',
            'description': 'Counts bottles and other inventory items',
            'state': {
                'status': ['idle', 'counting', 'verifying', 'error'],
                'inventory_type': ['bottles', 'cans', 'kegs', 'glasses', 'other'],
                'current_count': 0,
                'last_verification': None,
                'accuracy_rate': 0.98
            },
            'methods': [
                'count_inventory(type)',
                'verify_count(expected, actual)',
                'update_inventory(item, quantity)',
                'generate_report()',
                'reconcile_differences()'
            ],
            'transitions': {
                'idle_to_counting': 'inventory count requested',
                'counting_to_verifying': 'count complete',
                'verifying_to_idle': 'verification complete',
                'any_to_error': 'counting discrepancy detected'
            }
        }
        
        # 5. HighlightReel - Records noteworthy events
        self.cells['HighlightReel'] = {
            'id': 'highlight_reel',
            'name': 'HighlightReel',
            'type': 'recorder',
            'description': 'Records noteworthy events from The Tap',
            'state': {
                'status': ['recording', 'paused', 'archiving', 'error'],
                'event_types': ['milestone', 'achievement', 'anomaly', 'celebration'],
                'current_recording': None,
                'archive_size': 0,
                'highlight_count': 0
            },
            'methods': [
                'record_event(event)',
                'categorize_highlight(event)',
                'archive_highlights()',
                'generate_reel()',
                'search_highlights(query)'
            ],
            'transitions': {
                'recording_to_paused': 'pause requested',
                'paused_to_recording': 'resume requested',
                'recording_to_archiving': 'archive threshold reached',
                'archiving_to_recording': 'archive complete',
                'any_to_error': 'recording failure'
            }
        }
    
    def define_relationships(self):
        """Define relationships between cells"""
        
        # WesleyCore orchestrates all other cells
        self.relationships = [
            {
                'source': 'WesleyCore',
                'target': 'ReceiptSorter',
                'type': 'orchestrates',
                'description': 'WesleyCore dispatches receipt processing tasks'
            },
            {
                'source': 'WesleyCore',
                'target': 'VectorDB',
                'type': 'orchestrates',
                'description': 'WesleyCore manages database operations'
            },
            {
                'source': 'WesleyCore',
                'target': 'CountingEngine',
                'type': 'orchestrates',
                'description': 'WesleyCore triggers inventory counts'
            },
            {
                'source': 'WesleyCore',
                'target': 'HighlightReel',
                'type': 'orchestrates',
                'description': 'WesleyCore monitors and records events'
            },
            {
                'source': 'ReceiptSorter',
                'target': 'VectorDB',
                'type': 'feeds',
                'description': 'ReceiptSorter provides categorized data for embeddings'
            },
            {
                'source': 'CountingEngine',
                'target': 'VectorDB',
                'type': 'feeds',
                'description': 'CountingEngine provides inventory data for embeddings'
            },
            {
                'source': 'HighlightReel',
                'target': 'VectorDB',
                'type': 'feeds',
                'description': 'HighlightReel provides event data for embeddings'
            },
            {
                'source': 'VectorDB',
                'target': 'WesleyCore',
                'type': 'returns',
                'description': 'VectorDB returns search results to WesleyCore'
            },
            {
                'source': 'ReceiptSorter',
                'target': 'CountingEngine',
                'type': 'informs',
                'description': 'ReceiptSorter informs CountingEngine of new inventory'
            },
            {
                'source': 'HighlightReel',
                'target': 'WesleyCore',
                'type': 'reports',
                'description': 'HighlightReel reports notable events to WesleyCore'
            }
        ]
    
    def build_quilt_sheet(self) -> Dict[str, Any]:
        """Build the complete Quilt sheet structure"""
        
        self.define_cells()
        self.define_relationships()
        
        quilt_sheet = {
            'format': 'quilt_sheet',
            'version': '1.0',
            'metadata': {
                'name': 'Wesley System Architecture',
                'description': 'Complete architecture of the wesley repo - The Ensign system',
                'created': datetime.now().isoformat(),
                'source_repo': 'wesley',
                'cell_count': len(self.cells),
                'relationship_count': len(self.relationships)
            },
            'cells': list(self.cells.values()),
            'relationships': self.relationships,
            'system_flow': {
                'main_loop': [
                    'WesleyCore.initialize()',
                    'WesleyCore.run_main_loop()',
                    'ReceiptSorter.sort_receipt()',
                    'CountingEngine.count_inventory()',
                    'VectorDB.add_embedding()',
                    'HighlightReel.record_event()',
                    'WesleyCore.monitor_cells()'
                ],
                'data_flow': [
                    'ReceiptSorter -> VectorDB (embeddings)',
                    'CountingEngine -> VectorDB (inventory data)',
                    'HighlightReel -> VectorDB (event data)',
                    'VectorDB -> WesleyCore (search results)'
                ]
            }
        }
        
        return quilt_sheet
    
    def save_quilt(self, output_path: str):
        """Save the Quilt sheet to a .qzt file"""
        
        quilt_data = self.build_quilt_sheet()
        
        # Ensure the output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save as JSON with .qzt extension
        with open(output_path, 'w') as f:
            json.dump(quilt_data, f, indent=2)
        
        print(f"✅ Quilt sheet saved to: {output_path}")
        print(f"   Cells: {quilt_data['metadata']['cell_count']}")
        print(f"   Relationships: {quilt_data['metadata']['relationship_count']}")
        
        # Also save a human-readable version for inspection
        readable_path = output_path.replace('.qzt', '_readable.json')
        with open(readable_path, 'w') as f:
            json.dump(quilt_data, f, indent=2)
        print(f"📄 Readable version saved to: {readable_path}")
    
    def validate_quilt(self, quilt_data: Dict[str, Any]) -> bool:
        """Validate the Quilt sheet structure"""
        
        required_keys = ['format', 'version', 'metadata', 'cells', 'relationships']
        
        # Check required top-level keys
        for key in required_keys:
            if key not in quilt_data:
                print(f"❌ Missing required key: {key}")
                return False
        
        # Validate cells
        if len(quilt_data['cells']) != 5:
            print(f"❌ Expected 5 cells, found {len(quilt_data['cells'])}")
            return False
        
        # Validate each cell has required structure
        for cell in quilt_data['cells']:
            for key in ['id', 'name', 'type', 'description', 'state', 'methods', 'transitions']:
                if key not in cell:
                    print(f"❌ Cell {cell.get('name', 'unknown')} missing key: {key}")
                    return False
        
        # Validate relationships
        for rel in quilt_data['relationships']:
            for key in ['source', 'target', 'type', 'description']:
                if key not in rel:
                    print(f"❌ Relationship missing key: {key}")
                    return False
        
        print("✅ Quilt sheet validation passed")
        return True

def main():
    """Main execution function"""
    
    # Define output path
    output_path = '/workspace/superinstance-website/bridges/wesley-quilt.qzt'
    
    # Create converter instance
    converter = WesleyToQuilt()
    
    # Build and save the Quilt sheet
    quilt_data = converter.build_quilt_sheet()
    
    # Validate before saving
    if converter.validate_quilt(quilt_data):
        converter.save_quilt(output_path)
        print("\n🎉 Wesley repo successfully converted to Quilt sheet!")
    else:
        print("\n❌ Quilt sheet validation failed - not saving")

if __name__ == "__main__":
    main()
