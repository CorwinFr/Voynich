"""
Exception registry: manual overrides and forced decodings.
Backed by exceptions.json, grows through iterative quality review.
"""
import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class ExceptionEntry:
    eva_word: str
    forced_latin: str
    reason: str
    added_by: str = 'manual'
    date_added: str = ''
    folio_context: str = ''


class ExceptionRegistry:
    """Manages manual override decodings."""

    def __init__(self, path: str):
        self.path = path
        self.entries: dict[str, ExceptionEntry] = {}
        self._load()

    def _load(self):
        if os.path.exists(self.path):
            with open(self.path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for eva, info in data.get('_entries', {}).items():
                if isinstance(info, str):
                    self.entries[eva] = ExceptionEntry(eva_word=eva, forced_latin=info, reason='legacy')
                elif isinstance(info, dict):
                    self.entries[eva] = ExceptionEntry(eva_word=eva, **info)

    def lookup(self, eva_word: str) -> str | None:
        """Get forced Latin for an EVA word, or None."""
        entry = self.entries.get(eva_word.lower())
        return entry.forced_latin if entry else None

    def add(self, eva_word: str, latin: str, reason: str,
            folio: str = '', added_by: str = 'manual'):
        """Add or update an exception."""
        self.entries[eva_word.lower()] = ExceptionEntry(
            eva_word=eva_word.lower(),
            forced_latin=latin,
            reason=reason,
            added_by=added_by,
            date_added=datetime.now().isoformat()[:10],
            folio_context=folio,
        )
        self._save()

    def remove(self, eva_word: str):
        """Remove an exception."""
        self.entries.pop(eva_word.lower(), None)
        self._save()

    def _save(self):
        data = {'_comment': 'Manual override registry.', '_entries': {}}
        for eva, entry in sorted(self.entries.items()):
            data['_entries'][eva] = {
                'forced_latin': entry.forced_latin,
                'reason': entry.reason,
                'added_by': entry.added_by,
                'date_added': entry.date_added,
                'folio_context': entry.folio_context,
            }
        with open(self.path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def __len__(self):
        return len(self.entries)
