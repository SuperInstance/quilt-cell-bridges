"""
plainsong (SuperInstance) ↔ Quilt Cell Bridge

The SuperInstance plainsong is music notation you can write in any text editor,
read like a lead sheet, keep in version control, and compile to MIDI and audio.

A plainsong file:
```
[V1] (Verse - 4 Bars)
Chords: | Am . . . | F . . . | C . . . | G . . . |
Melody: | A4 . C5 E5 | F4 . A4 C5 | E4 . G4 C5 | D4 . F4 B4 |
Lyrics: | the tide  came | in  before  dawn | and  left  a | line  of  salt |
@bass   | a1 . e2 . | f1 . c2 . | c1 . g1 . | g1 . d2 . | vel: 70
```

THE CRUCIAL INSIGHT: A plain song IS a Quilt sheet. Each line is a row of cells.
Each bar is a column. Each note is a cell with pitch and time.

Map:
- Note → cell (with pitch and time)
- Bar → cell graph (4 beats)
- Chord → DoubleEntry (multiple notes at once)
- Lyric → Murmur (timed text)
- Tempo → Vibe (rate of state change)
- Voice (@bass, @melody) → Graph (subgraph)
"""

from typing import Dict, List, Any, Optional, Tuple


class Cell:
    """A Quilt cell representing a note."""
    def __init__(self, pitch: str, beat: float, voice: str = 'melody'):
        self.pitch = pitch
        self.beat = beat
        self.voice = voice
        self.gamma = 0.5
        self.eta = 0.5

    def __repr__(self):
        return f"Cell({self.pitch}, beat={self.beat}, voice={self.voice})"


class Plainsong:
    """A plainsong piece as a Quilt sheet."""
    def __init__(self, title: str = 'untitled'):
        self.title = title
        self.cells: List[Cell] = []
        self.bars: List[List[Cell]] = []
        self.bpm: int = 120  # default tempo (Vibe)

    def add_note(self, pitch: str, beat: float, voice: str = 'melody') -> Cell:
        """Add a note. A cell."""
        cell = Cell(pitch, beat, voice)
        self.cells.append(cell)
        return cell

    def add_bar(self, notes: List[Cell]) -> None:
        """Add a bar of notes."""
        self.bars.append(notes)

    def set_tempo(self, bpm: int) -> None:
        """Set the tempo. Vibe acceleration."""
        self.bpm = bpm

    def parse(self, text: str) -> None:
        """Parse a plainsong file."""
        current_voice = 'melody'
        for line in text.split('\n'):
            line = line.strip()
            if not line or line.startswith('#') or line.startswith('['):
                continue
            if line.startswith('Chords:'):
                current_voice = 'chord'
                continue
            if line.startswith('Melody:'):
                current_voice = 'melody'
                continue
            if line.startswith('Lyrics:'):
                current_voice = 'lyric'
                continue
            if line.startswith('@'):
                # Voice marker
                parts = line.split(maxsplit=1)
                if len(parts) == 2:
                    current_voice = parts[0][1:]
                continue
            # Parse notes
            if '|' in line:
                bars = line.split('|')
                for bar in bars:
                    bar = bar.strip()
                    if not bar:
                        continue
                    notes = bar.split()
                    bar_cells = []
                    for i, note in enumerate(notes):
                        if note == '.':
                            continue
                        # Strip vel:N if present
                        if note.startswith('vel:'):
                            continue
                        cell = self.add_note(pitch=note, beat=i * 0.5, voice=current_voice)
                        bar_cells.append(cell)
                    if bar_cells:
                        self.add_bar(bar_cells)

    def to_quilt_sheet(self) -> Dict[str, Any]:
        """Convert to a Quilt sheet representation."""
        return {
            'name': self.title,
            'cells': [
                {'pitch': c.pitch, 'beat': c.beat, 'voice': c.voice, 'gamma': c.gamma, 'eta': c.eta}
                for c in self.cells
            ],
            'bars': len(self.bars),
            'bpm': self.bpm,
        }


if __name__ == "__main__":
    print("=" * 60)
    print("PLAINSONG ↔ QUILT CELL BRIDGE")
    print("=" * 60)
    print()
    print("Music notation as plain text on Quilt cells.")
    print("A song IS a Quilt sheet. Each note IS a cell.")
    print()

    song_text = """[V1] (Verse - 4 Bars)
Chords: | Am . . . | F . . . | C . . . | G . . . |
Melody: | A4 . C5 E5 | F4 . A4 C5 | E4 . G4 C5 | D4 . F4 B4 |
Lyrics: | the tide  came | in  before  dawn | and  left  a | line  of  salt |
@bass   | a1 . e2 . | f1 . c2 . | c1 . g1 . | g1 . d2 . | vel: 70"""

    plainsong = Plainsong(title="The Tide")
    plainsong.parse(song_text)
    plainsong.set_tempo(120)

    print(f"Title: {plainsong.title}")
    print(f"Bars: {len(plainsong.bars)}")
    print(f"Total notes: {len(plainsong.cells)}")
    print(f"Tempo: {plainsong.bpm} BPM")
    print()

    # Show first bar
    if plainsong.bars:
        print(f"First bar: {plainsong.bars[0]}")
    print()

    # Convert to Quilt sheet
    sheet = plainsong.to_quilt_sheet()
    print(f"Quilt sheet: {sheet['name']} ({sheet['bars']} bars, {len(sheet['cells'])} cells)")
    print()

    # Conservation
    n = len(plainsong.cells)
    total = sum(c.gamma + c.eta for c in plainsong.cells)
    print(f"Conservation: {n} cells, γ+η={total:.2f} (should be {n})")
    print()

    print("=" * 60)
    print("Iron sharpens iron.")
    print("A song IS a Quilt sheet.")
    print("Each note IS a cell. Each bar IS a sub-graph.")


if __name__ == "__main__":
    demo()
