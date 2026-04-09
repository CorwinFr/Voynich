"""
Audit trail: logs every decoding decision for traceability.
"""
from dataclasses import dataclass, field
from v12.stages.logogram import DecodedWord


@dataclass
class AuditEntry:
    eva_word: str
    folio: str
    line: int
    position: int
    final_latin: str
    confidence: str
    layer: str
    rule: str
    alternatives: list[tuple[str, str]] = field(default_factory=list)


class AuditTrail:
    """Collects decoding decisions for a folio."""

    def __init__(self):
        self.entries: list[AuditEntry] = []

    def log(self, dw: DecodedWord, folio: str, line: int, position: int):
        self.entries.append(AuditEntry(
            eva_word=dw.eva,
            folio=folio,
            line=line,
            position=position,
            final_latin=dw.latin,
            confidence=dw.confidence,
            layer=dw.layer,
            rule=dw.rule,
            alternatives=dw.alternatives or [],
        ))

    def summary(self) -> str:
        """Generate a summary of the audit trail."""
        lines = []
        for e in self.entries:
            alts = ', '.join(f'{a[0]}({a[1]})' for a in e.alternatives[:2])
            lines.append(
                f"  {e.folio}.{e.line:02d}.{e.position:02d} "
                f"{e.eva_word:15s} -> {e.final_latin:20s} "
                f"[{e.confidence:9s}] {e.layer} | {e.rule}"
                f"{f' | alts: {alts}' if alts else ''}"
            )
        return '\n'.join(lines)

    def opaque_words(self) -> list[AuditEntry]:
        """Return all OPAQUE entries for review."""
        return [e for e in self.entries if e.confidence == 'OPAQUE']

    def low_words(self) -> list[AuditEntry]:
        """Return all LOW confidence entries for review."""
        return [e for e in self.entries if e.confidence == 'LOW']
