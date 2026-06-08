from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func


class SoftDeleteMixin:
    """Reusable, non-destructive delete fields for auditable records."""

    deleted_at = Column(DateTime, nullable=True, index=True)
    deleted_by = Column(Integer, nullable=True)
    delete_reason = Column(String(255), nullable=True)

    def soft_delete(self, deleted_by: int | None = None, reason: str | None = None) -> None:
        self.deleted_at = func.now()
        self.deleted_by = deleted_by
        self.delete_reason = reason

    def restore(self) -> None:
        self.deleted_at = None
        self.deleted_by = None
        self.delete_reason = None
