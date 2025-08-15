from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True, kw_only=True)
class BaseDomainObject:
    id: UUID = field(default_factory=uuid4, compare=True)

    @property
    def str_id(self) -> str:
        return str(self.id)

    def _replace(self, **changes) -> "BaseDomainObject":
        from dataclasses import replace

        return replace(self, **changes)
