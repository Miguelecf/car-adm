from datetime import date, timedelta
from typing import Optional, Literal
from sqlalchemy.orm import Session
from sqlalchemy import and_, extract
from app.models import Payment, PaymentStatus, PaymentMethod, Contract
from app.core.config import settings


class PaymentService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[Payment]:
        return (
            self.db.query(Payment)
            .join(Contract)
            .order_by(Payment.due_date.desc())
            .all()
        )

    def get_pending(self) -> list[Payment]:
        return (
            self.db.query(Payment)
            .join(Contract)
            .filter(Payment.status == PaymentStatus.PENDIENTE)
            .order_by(Payment.due_date.asc())
            .all()
        )

    def get_overdue(self) -> list[Payment]:
        return (
            self.db.query(Payment)
            .join(Contract)
            .filter(
                Payment.status.in_([PaymentStatus.PENDIENTE, PaymentStatus.ATRASADO]),
                Payment.due_date < date.today()
            )
            .order_by(Payment.due_date.asc())
            .all()
        )

    def get_by_id(self, payment_id: int) -> Optional[Payment]:
        return self.db.query(Payment).filter(Payment.id == payment_id).first()

    def create(self, data: dict) -> Payment:
        payment = Payment(**data)
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)
        return payment

    def mark_paid(self, payment_id: int, payment_date: date, method: PaymentMethod, notes: str = "") -> Optional[Payment]:
        payment = self.get_by_id(payment_id)
        if not payment:
            return None
        payment.status = PaymentStatus.PAGADO
        payment.payment_date = payment_date
        payment.method = method
        if notes:
            payment.notes = notes
        self.db.commit()
        self.db.refresh(payment)
        return payment

    def update(self, payment_id: int, data: dict) -> Optional[Payment]:
        payment = self.get_by_id(payment_id)
        if not payment:
            return None
        for key, value in data.items():
            setattr(payment, key, value)
        self.db.commit()
        self.db.refresh(payment)
        return payment

    def delete(self, payment_id: int) -> bool:
        payment = self.get_by_id(payment_id)
        if not payment:
            return False
        self.db.delete(payment)
        self.db.commit()
        return True

    def get_weekly_revenue(self) -> int:
        today = date.today()
        start_of_week = today - timedelta(days=today.weekday())
        result = (
            self.db.query(Payment)
            .filter(
                Payment.status == PaymentStatus.PAGADO,
                Payment.payment_date >= start_of_week,
                Payment.payment_date <= today
            )
            .all()
        )
        return sum(p.amount for p in result)

    def get_pending_amount(self) -> int:
        result = self.get_overdue()
        return sum(p.amount for p in result)

    def generate_weekly_payments(self) -> list[Payment]:
        from app.services.contract_service import ContractService
        contract_service = ContractService(self.db)
        contracts = contract_service.get_active()
        created = []

        for contract in contracts:
            existing = (
                self.db.query(Payment)
                .filter(
                    Payment.contract_id == contract.id,
                    Payment.due_date >= date.today()
                )
                .first()
            )
            if existing:
                continue

            payment = Payment(
                contract_id=contract.id,
                amount=contract.weekly_amount,
                due_date=date.today() + timedelta(days=(settings.PAYMENT_DAY - date.today().weekday()) % 7),
                status=PaymentStatus.PENDIENTE
            )
            self.db.add(payment)
            created.append(payment)

        self.db.commit()
        for p in created:
            self.db.refresh(p)
        return created