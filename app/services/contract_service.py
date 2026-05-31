from datetime import date, timedelta
from typing import Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import extract
from app.models import Contract, ContractStatus, Vehicle, Driver
from app.core.config import settings


class ContractService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[Contract]:
        return (
            self.db.query(Contract)
            .options(joinedload(Contract.vehicle), joinedload(Contract.driver))
            .order_by(Contract.id.desc())
            .all()
        )

    def get_active(self) -> list[Contract]:
        return (
            self.db.query(Contract)
            .options(joinedload(Contract.vehicle), joinedload(Contract.driver))
            .filter(Contract.status == ContractStatus.ACTIVO)
            .order_by(Contract.id.desc())
            .all()
        )

    def get_by_id(self, contract_id: int) -> Optional[Contract]:
        return (
            self.db.query(Contract)
            .options(joinedload(Contract.vehicle), joinedload(Contract.driver))
            .filter(Contract.id == contract_id)
            .first()
        )

    def create(self, data: dict) -> Contract:
        contract = Contract(**data)
        self.db.add(contract)
        self.db.commit()
        self.db.refresh(contract)
        return contract

    def update(self, contract_id: int, data: dict) -> Optional[Contract]:
        contract = self.get_by_id(contract_id)
        if not contract:
            return None
        for key, value in data.items():
            setattr(contract, key, value)
        self.db.commit()
        self.db.refresh(contract)
        return contract

    def end_contract(self, contract_id: int, end_km: int, end_date: date) -> Optional[Contract]:
        contract = self.get_by_id(contract_id)
        if not contract:
            return None
        contract.end_km = end_km
        contract.end_date = end_date
        contract.status = ContractStatus.FINALIZADO
        self.db.commit()
        self.db.refresh(contract)
        return contract

    def delete(self, contract_id: int) -> bool:
        contract = self.get_by_id(contract_id)
        if not contract:
            return False
        self.db.delete(contract)
        self.db.commit()
        return True

    def get_contracts_due_this_week(self) -> list[Contract]:
        today = date.today()
        _, last_day = divmod(today.weekday(), 7)
        days_until_end = 6 - last_day
        end_of_week = today + timedelta(days=days_until_end)

        return (
            self.db.query(Contract)
            .options(joinedload(Contract.vehicle), joinedload(Contract.driver))
            .filter(
                Contract.status == ContractStatus.ACTIVO,
                Contract.start_date <= end_of_week,
            )
            .all()
        )