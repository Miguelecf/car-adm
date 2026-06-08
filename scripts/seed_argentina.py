"""Seed synthetic Buenos Aires demo data without deleting existing records.

Run from the project root:
    python scripts/seed_argentina.py

The script is idempotent by DNI/plate and restores matching soft-deleted
records instead of inserting duplicates. All data is synthetic.
"""

from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.database import Base, SessionLocal, engine, ensure_soft_delete_columns
from app.models import (
    Contract,
    ContractStatus,
    Document,
    DocumentType,
    Driver,
    Incident,
    IncidentStatus,
    IncidentType,
    Maintenance,
    MaintenanceType,
    Payment,
    PaymentMethod,
    PaymentStatus,
    Vehicle,
    VehicleStatus,
)


DRIVERS = [
    {"name": "Leandro Acosta", "dni": "30111222", "phone": "+54 11 6300-2001", "address": "Av. Corrientes 1400, CABA", "license_number": "CABA-A-30111222", "license_expiry": date(2028, 4, 15)},
    {"name": "Mariana Ibarra", "dni": "31222333", "phone": "+54 11 6300-2002", "address": "Av. Santa Fe 1800, Recoleta", "license_number": "CABA-A-31222333", "license_expiry": date(2027, 11, 20)},
    {"name": "Pablo Duarte", "dni": "32333444", "phone": "+54 11 6300-2003", "address": "Av. Cabildo 2200, Belgrano", "license_number": "CABA-A-32333444", "license_expiry": date(2029, 2, 5)},
    {"name": "Carla Romano", "dni": "33444555", "phone": "+54 11 6300-2004", "address": "Av. Rivadavia 5000, Caballito", "license_number": "CABA-A-33444555", "license_expiry": date(2028, 8, 30)},
    {"name": "Sebastián Varela", "dni": "34555666", "phone": "+54 11 6300-2005", "address": "Av. San Juan 1200, San Telmo", "license_number": "CABA-A-34555666", "license_expiry": date(2027, 6, 18)},
    {"name": "Paula Sanz", "dni": "35666777", "phone": "+54 11 6300-2006", "address": "Alicia Moreau de Justo 1800, Puerto Madero", "license_number": "CABA-A-35666777", "license_expiry": date(2028, 12, 1)},
    {"name": "Ignacio Cárdenas", "dni": "36777888", "phone": "+54 11 6300-2007", "address": "Av. Leandro N. Alem 600, Retiro", "license_number": "CABA-A-36777888", "license_expiry": date(2029, 1, 25)},
    {"name": "Micaela Torres", "dni": "37888999", "phone": "+54 11 6300-2008", "address": "Av. Scalabrini Ortiz 1600, Palermo", "license_number": "CABA-A-37888999", "license_expiry": date(2028, 9, 10)},
    {"name": "Rodrigo Páez", "dni": "38999000", "phone": "+54 11 6300-2009", "address": "Av. Triunvirato 4200, Villa Urquiza", "license_number": "CABA-A-38999000", "license_expiry": date(2027, 10, 2)},
    {"name": "Belén Cejas", "dni": "39100111", "phone": "+54 11 6300-2010", "address": "Av. Maipú 1000, Vicente López", "license_number": "CABA-A-39100111", "license_expiry": date(2028, 3, 14)},
]

VEHICLES = [
    {"brand": "Toyota", "model": "Etios", "year": 2020, "plate": "AB 123 CD", "color": "Blanco", "current_km": 84200, "status": VehicleStatus.ACTIVO},
    {"brand": "Fiat", "model": "Cronos", "year": 2021, "plate": "AC 456 EF", "color": "Gris", "current_km": 61750, "status": VehicleStatus.ACTIVO},
    {"brand": "Peugeot", "model": "208", "year": 2019, "plate": "AD 789 GH", "color": "Azul", "current_km": 93600, "status": VehicleStatus.ACTIVO},
    {"brand": "Chevrolet", "model": "Onix", "year": 2022, "plate": "AE 147 JK", "color": "Negro", "current_km": 40200, "status": VehicleStatus.ACTIVO},
    {"brand": "Renault", "model": "Logan", "year": 2018, "plate": "AF 258 LM", "color": "Rojo", "current_km": 121400, "status": VehicleStatus.EN_TALLER},
    {"brand": "Volkswagen", "model": "Gol Trend", "year": 2017, "plate": "AG 369 NP", "color": "Plata", "current_km": 138900, "status": VehicleStatus.ACTIVO},
    {"brand": "Nissan", "model": "Versa", "year": 2020, "plate": "AH 741 QR", "color": "Gris oscuro", "current_km": 77500, "status": VehicleStatus.ACTIVO},
    {"brand": "Ford", "model": "Ka", "year": 2019, "plate": "AJ 852 ST", "color": "Blanco", "current_km": 88900, "status": VehicleStatus.ACTIVO},
    {"brand": "Toyota", "model": "Corolla", "year": 2016, "plate": "AK 963 UV", "color": "Negro", "current_km": 156300, "status": VehicleStatus.FUERA_SERVICIO},
    {"brand": "Hyundai", "model": "HB20", "year": 2021, "plate": "AL 159 WX", "color": "Azul", "current_km": 54500, "status": VehicleStatus.ACTIVO},
]


def upsert_by_unique(db, model, unique_field: str, payload: dict):
    value = payload[unique_field]
    record = db.query(model).filter(getattr(model, unique_field) == value).first()
    if record:
        for key, item in payload.items():
            setattr(record, key, item)
        if getattr(record, "deleted_at", None) is not None:
            record.restore()
        return record, False
    record = model(**payload)
    db.add(record)
    return record, True


def seed():
    Base.metadata.create_all(bind=engine)
    ensure_soft_delete_columns()
    db = SessionLocal()
    try:
        created = {"drivers": 0, "vehicles": 0, "contracts": 0, "payments": 0, "documents": 0, "maintenance": 0, "incidents": 0}

        drivers = []
        vehicles = []
        for payload in DRIVERS:
            driver, was_created = upsert_by_unique(db, Driver, "dni", payload)
            created["drivers"] += int(was_created)
            drivers.append(driver)
        for payload in VEHICLES:
            vehicle, was_created = upsert_by_unique(db, Vehicle, "plate", payload)
            created["vehicles"] += int(was_created)
            vehicles.append(vehicle)
        db.commit()
        for item in [*drivers, *vehicles]:
            db.refresh(item)

        start = date.today() - timedelta(days=28)
        for index, (driver, vehicle) in enumerate(zip(drivers[:8], vehicles[:8]), start=1):
            contract = (
                db.query(Contract)
                .filter(Contract.driver_id == driver.id, Contract.vehicle_id == vehicle.id, Contract.deleted_at.is_(None))
                .first()
            )
            if not contract:
                contract = Contract(
                    driver_id=driver.id,
                    vehicle_id=vehicle.id,
                    start_date=start + timedelta(days=index),
                    weekly_amount=145000 + index * 8000,
                    deposit_amount=250000,
                    start_km=max(vehicle.current_km - 4500, 0),
                    status=ContractStatus.ACTIVO,
                )
                db.add(contract)
                db.flush()
                created["contracts"] += 1

            for week in range(4):
                due_date = contract.start_date + timedelta(days=7 * (week + 1))
                exists = (
                    db.query(Payment)
                    .filter(Payment.contract_id == contract.id, Payment.due_date == due_date, Payment.deleted_at.is_(None))
                    .first()
                )
                if not exists:
                    is_paid = week < 2 or (index % 3 == 0 and week == 2)
                    db.add(Payment(
                        contract_id=contract.id,
                        amount=contract.weekly_amount,
                        due_date=due_date,
                        payment_date=due_date if is_paid else None,
                        method=PaymentMethod.TRANSFERENCIA if is_paid else None,
                        status=PaymentStatus.PAGADO if is_paid else PaymentStatus.PENDIENTE,
                        notes="Demo Buenos Aires - canon semanal sintético",
                    ))
                    created["payments"] += 1

        db.commit()

        for vehicle in vehicles:
            for doc_type, months in [(DocumentType.SEGURO, 9), (DocumentType.ITV, 5), (DocumentType.MATRICULA, 24)]:
                expiry = date.today() + timedelta(days=30 * months)
                existing_docs = (
                    db.query(Document)
                    .filter(Document.vehicle_id == vehicle.id, Document.type == doc_type, Document.deleted_at.is_(None))
                    .order_by(Document.id.asc())
                    .all()
                )
                primary_doc = existing_docs[0] if existing_docs else None
                for duplicate_doc in existing_docs[1:]:
                    duplicate_doc.soft_delete(reason="Seed cleanup: duplicate active demo document")

                exists = (
                    db.query(Document)
                    .filter(Document.vehicle_id == vehicle.id, Document.type == doc_type, Document.expiry_date == expiry, Document.deleted_at.is_(None))
                    .first()
                )
                if primary_doc and not exists:
                    primary_doc.issue_date = date.today() - timedelta(days=365)
                    primary_doc.expiry_date = expiry
                    primary_doc.file_notes = f"Documento demo Argentina ({doc_type.value}). Usar VTV/seguro real sólo en staging privada."
                elif not primary_doc:
                    db.add(Document(
                        vehicle_id=vehicle.id,
                        type=doc_type,
                        issue_date=date.today() - timedelta(days=365),
                        expiry_date=expiry,
                        file_notes=f"Documento demo Argentina ({doc_type.value}). Usar VTV/seguro real sólo en staging privada.",
                    ))
                    created["documents"] += 1

            maintenance_exists = db.query(Maintenance).filter(Maintenance.vehicle_id == vehicle.id, Maintenance.deleted_at.is_(None)).first()
            if not maintenance_exists:
                db.add(Maintenance(
                    vehicle_id=vehicle.id,
                    type=MaintenanceType.ACEITE,
                    description="Service preventivo demo: aceite, filtros y revisión general para flota CABA/GBA.",
                    km_at_service=max(vehicle.current_km - 2500, 0),
                    service_date=date.today() - timedelta(days=21),
                    cost=85000,
                    next_service_km=vehicle.current_km + 7500,
                    next_service_date=date.today() + timedelta(days=70),
                ))
                created["maintenance"] += 1

        incident_specs = [
            (vehicles[0], drivers[0], IncidentType.RECLAMO, "Pasajero reportó demora en retiro en Palermo; seguimiento soporte demo.", 0, IncidentStatus.RESUELTO),
            (vehicles[4], drivers[4], IncidentType.ACCIDENTE, "Toque menor de paragolpes en Caballito; unidad derivada a taller.", 120000, IncidentStatus.PENDIENTE),
            (vehicles[6], drivers[6], IncidentType.MULTA, "Acta de estacionamiento zona Retiro; pendiente validación administrativa.", 35000, IncidentStatus.PENDIENTE),
        ]
        for vehicle, driver, incident_type, description, cost, status in incident_specs:
            exists = db.query(Incident).filter(Incident.description == description, Incident.deleted_at.is_(None)).first()
            if not exists:
                db.add(Incident(
                    vehicle_id=vehicle.id,
                    driver_id=driver.id,
                    type=incident_type,
                    description=description,
                    date=date.today() - timedelta(days=5),
                    cost=cost,
                    status=status,
                ))
                created["incidents"] += 1

        db.commit()
        return created
    finally:
        db.close()


if __name__ == "__main__":
    result = seed()
    print("Seed Argentina/Buenos Aires completado (sin hard deletes):")
    for key, value in result.items():
        print(f"- {key}: {value} nuevos")
