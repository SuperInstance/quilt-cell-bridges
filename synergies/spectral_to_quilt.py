from collections import defaultdict
import numpy as np

def _eig(matrix):
    return np.linalg.eig(matrix)
# from scipy.sparse import csgraph
from typing import Dict, List, Tuple, Any

class SpectralFleetBridge:
    """Bridge between spectral-fleet's agent interaction graph and Quilt's cell graph.
    Maps eigenvalues and eigenvectors from interaction graph to cell properties:
    - spectral centrality → cell.gamma
    - spectral gap → cell.vibe
    """

    def __init__(self):
        pass

    def compute_spectral_metrics(self, cells: List[Dict], edges: List[Tuple[str, str]]) -> Dict[str, Any]:
        """Compute spectral centrality and gap from cell interaction graph."""
        laplacian = cell_graph_to_laplacian(cells, edges)
        centrality = spectral_centrality(laplacian)
        apply_centrality_to_cells(cells, centrality)

        # Compute spectral gap (difference between first and second eigenvalues)
        eigenvals = np.linalg.eigvalsh(laplacian.toarray())
        eigenvals = np.sort(eigenvals)
        spectral_gap = eigenvals[1] - eigenvals[0]  # gap between smallest two

        # Set vibe on all cells (shared property across the fleet)
        for cell in cells:
            cell['vibe'] = float(spectral_gap)

        return {
            'centrality': centrality,
            'spectral_gap': float(spectral_gap),
            'eigenvalues': eigenvals.tolist()
        }


def cell_graph_to_laplacian(cells: List[Dict], edges: List[Tuple[str, str]]) -> np.ndarray:
    """Convert cell graph (nodes + edges) to symmetric graph Laplacian matrix."""
    # Map cell_id to index
    cell_to_idx = {cell['id']: i for i, cell in enumerate(cells)}
    n = len(cells)

    # Initialize adjacency matrix
    adj = np.zeros((n, n))

    # Fill adjacency matrix from edges
    for u, v in edges:
        i, j = cell_to_idx[u], cell_to_idx[v]
        adj[i, j] = 1.0
        adj[j, i] = 1.0

    # Compute degree matrix
    degrees = np.sum(adj, axis=1)
    D = np.diag(degrees)

    # Laplacian: L = D - A
    laplacian = D - adj

    return laplacian


def spectral_centrality(laplacian: np.ndarray) -> Dict[str, float]:
    """Compute eigenvector centrality from graph Laplacian.
    Returns dict of cell_id → centrality score (based on smallest eigenvector)."""
    # Compute eigenvalues and eigenvectors
    eigenvals, eigenvects = np.linalg.eigh(laplacian)

    # Sort by eigenvalue ascending
    sorted_indices = np.argsort(eigenvals)
    eigenvals = eigenvals[sorted_indices]
    eigenvects = eigenvects[:, sorted_indices]

    # Use the smallest non-zero eigenvalue's eigenvector (Fiedler vector)
    # But for centrality, we use the first non-trivial eigenvector (index 1, if 0 is trivial)
    # The first eigenvector (index 0) is constant → trivial
    # So use index 1 (second smallest) as primary centrality vector
    # This is the Fiedler vector, used for spectral clustering
    fiedler_vec = eigenvects[:, 1]  # second smallest eigenvalue's eigenvector

    # Normalize by absolute value (positive and negative components used for partitioning)
    # But for centrality, we use magnitude
    centrality_scores = np.abs(fiedler_vec)

    # Map back to cell IDs
    cell_ids = [cell['id'] for cell in cells]
    centrality_dict = {cell_id: float(score) for cell_id, score in zip(cell_ids, centrality_scores)}

    return centrality_dict


def apply_centrality_to_cells(cells: List[Dict], centrality: Dict[str, float]) -> None:
    """Update each cell's gamma with its spectral centrality value."""
    for cell in cells:
        cell_id = cell['id']
        if cell_id in centrality:
            cell['gamma'] = float(centrality[cell_id])
        else:
            cell['gamma'] = 0.0
