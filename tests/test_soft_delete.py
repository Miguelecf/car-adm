import unittest
from datetime import date

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models import Driver, Vehicle, VehicleStatus
from app.services.driver_service import DriverService
from app.services.vehicle_service import VehicleService


class SoftDeleteServiceTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=self.engine)
        self.Session = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.db = self.Session()

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(bind=self.engine)

    def test_vehicle_delete_marks_deleted_and_hides_from_default_queries(self):
        service = VehicleService(self.db)
        vehicle = service.create({
            "brand": "Toyota",
            "model": "Etios",
            "year": 2020,
            "plate": "AB 123 CD",
            "color": "Blanco",
            "current_km": 84200,
            "status": VehicleStatus.ACTIVO,
        })

        self.assertTrue(service.delete(vehicle.id))
        self.assertEqual(service.get_all(), [])
        self.assertIsNone(service.get_by_id(vehicle.id))

        persisted = service.get_by_id(vehicle.id, include_deleted=True)
        self.assertIsNotNone(persisted)
        self.assertIsNotNone(persisted.deleted_at)
        self.assertEqual(persisted.delete_reason, "Deleted from vehicles UI")

    def test_driver_delete_marks_deleted_and_dni_lookup_excludes_deleted(self):
        service = DriverService(self.db)
        driver = service.create({
            "name": "Leandro Acosta",
            "dni": "30111222",
            "phone": "+54 11 6300-2001",
            "address": "Av. Corrientes 1400, CABA",
            "license_number": "CABA-A-30111222",
            "license_expiry": date(2028, 4, 15),
        })

        self.assertTrue(service.delete(driver.id))
        self.assertEqual(service.get_all(), [])
        self.assertIsNone(service.get_by_dni("30111222"))

        persisted = service.get_by_id(driver.id, include_deleted=True)
        self.assertIsNotNone(persisted)
        self.assertIsNotNone(persisted.deleted_at)
        self.assertEqual(persisted.delete_reason, "Deleted from drivers UI")


if __name__ == "__main__":
    unittest.main()
