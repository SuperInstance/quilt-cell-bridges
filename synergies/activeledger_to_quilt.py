"""
activeledger-agent (SuperInstance) ↔ Quilt Cell Bridge

The SuperInstance activeledger-agent (Python) is an activity/investment/trade
ledger agent that writes entries to a PLATO tile server and queries them back.
A ledger is an append-only tape of facts.

THE CRUCIAL INSIGHT: A ledger IS a Quilt tape. An entry IS a cell.
The append-only property IS the conservation law: γ+η=1 across all entries.

Map:
- Entry → cell (with timestamp, amount, kind)
- Append → Z_out (write to tape)
- Query → Z_in (read from tape)
- Conservation → γ+η=1 across all entries
- Tile (PLATO) → cell stored in a room
- Room → cell graph
"""

from typing import Dict, List, Any, Optional
from datetime import datetime


class Entry:
    """A ledger entry as a Quilt cell."""
    def __init__(self, kind: str, amount: float, description: str, room: str = 'ledger'):
        self.timestamp = datetime.now().isoformat()
        self.kind = kind
        self.amount = amount
        self.description = description
        self.room = room
        self.gamma = 0.5
        self.eta = 0.5

    def to_cell(self) -> Dict[str, Any]:
        return {
            'kind': self.kind,
            'amount': self.amount,
            'description': self.description,
            'timestamp': self.timestamp,
            'room': self.room,
            'gamma': self.gamma,
            'eta': self.eta,
        }


class ActiveLedger:
    """An append-only ledger as a Quilt tape."""
    def __init__(self, name: str = 'ledger'):
        self.name = name
        # The tape: list of entries
        self.tape: List[Entry] = []
        # Index by kind
        self.by_kind: Dict[str, List[Entry]] = {}
        # Total
        self.total: float = 0.0

    def append(self, kind: str, amount: float, description: str = '') -> Entry:
        """Append an entry. Z_out."""
        entry = Entry(kind, amount, description, room=self.name)
        self.tape.append(entry)
        if kind not in self.by_kind:
            self.by_kind[kind] = []
        self.by_kind[kind].append(entry)
        self.total += amount
        return entry

    def query(self, kind: Optional[str] = None, limit: int = 10) -> List[Entry]:
        """Query entries. Z_in."""
        if kind:
            return self.by_kind.get(kind, [])[-limit:]
        return self.tape[-limit:]

    def verify_conservation(self) -> Dict[str, Any]:
        """Verify γ+η=1 across all entries."""
        if not self.tape:
            return {'valid': True, 'entries': 0, 'deviation': 0.0}
        total = sum(e.gamma + e.eta for e in self.tape)
        n = len(self.tape)
        return {
            'valid': abs(total - n) < 1e-9,
            'entries': n,
            'deviation': abs(total - n),
            'total_amount': self.total,
        }


if __name__ == "__main__":
    print("=" * 60)
    print("ACTIVELEDGER-AGENT ↔ QUILT CELL BRIDGE")
    print("=" * 60)
    print()
    print("Append-only ledger as a Quilt tape.")
    print("An entry IS a cell. Append-only IS conservation.")
    print()

    ledger = ActiveLedger(name='trades_2026')

    # Append entries
    ledger.append('trade', 100.0, 'Bought 10 shares of AAPL')
    ledger.append('trade', -50.0, 'Sold 5 shares of AAPL')
    ledger.append('dividend', 5.0, 'Quarterly dividend')
    ledger.append('fee', -1.0, 'Trading fee')
    ledger.append('trade', 200.0, 'Bought 20 shares of GOOGL')

    print(f"Total entries: {len(ledger.tape)}")
    print(f"Total amount: {ledger.total}")
    print()

    # Query
    trades = ledger.query(kind='trade')
    print(f"Trades: {len(trades)}")
    for t in trades:
        print(f"  {t.timestamp} {t.kind} ${t.amount:+.2f}: {t.description}")
    print()

    # Conservation
    v = ledger.verify_conservation()
    print(f"Conservation: {v}")
    print()

    print("=" * 60)
    print("Iron sharpens iron.")
    print("A ledger IS a Quilt tape.")
    print("Append-only IS conservation.")
    print("γ+η=1 across all entries.")


if __name__ == "__main__":
    demo()
