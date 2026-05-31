from datetime import date, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from app.models import Document, DocumentType, DocumentStatus, Vehicle


class DocumentService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[Document]:
        return (
            self.db.query(Document)
            .join(Vehicle)
            .order_by(Document.expiry_date.asc())
            .all()
        )

    def get_by_vehicle(self, vehicle_id: int) -> list[Document]:
        return (
            self.db.query(Document)
            .filter(Document.vehicle_id == vehicle_id)
            .order_by(Document.expiry_date.asc())
            .all()
        )

    def get_by_id(self, document_id: int) -> Optional[Document]:
        return self.db.query(Document).filter(Document.id == document_id).first()

    def create(self, data: dict) -> Document:
        document = Document(**data)
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document

    def update(self, document_id: int, data: dict) -> Optional[Document]:
        document = self.get_by_id(document_id)
        if not document:
            return None
        for key, value in data.items():
            setattr(document, key, value)
        self.db.commit()
        self.db.refresh(document)
        return document

    def delete(self, document_id: int) -> bool:
        document = self.get_by_id(document_id)
        if not document:
            return False
        self.db.delete(document)
        self.db.commit()
        return True

    def get_upcoming(self, days: int = 30) -> list[Document]:
        cutoff = date.today() + timedelta(days=days)
        return (
            self.db.query(Document)
            .join(Vehicle)
            .filter(
                Document.expiry_date >= date.today(),
                Document.expiry_date <= cutoff
            )
            .order_by(Document.expiry_date.asc())
            .all()
        )

    def get_expired(self) -> list[Document]:
        return (
            self.db.query(Document)
            .join(Vehicle)
            .filter(Document.expiry_date < date.today())
            .order_by(Document.expiry_date.asc())
            .all()
        )

    def get_status(self, document: Document) -> DocumentStatus:
        if document.expiry_date < date.today():
            return DocumentStatus.VENCIDO
        if document.expiry_date <= date.today() + timedelta(days=30):
            return DocumentStatus.PROXIMO_VENCER
        return DocumentStatus.VIGENTE