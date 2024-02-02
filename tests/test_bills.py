import unittest
from datetime import datetime, timedelta

from faker import Faker

# Connect to db
from connector import connect
from models.bill import Bills
from models.customer import Customers

fake = Faker()

db = connect()

# Create cursor
cur = db.cursor()


class TestBills(unittest.TestCase):
    def setUp(self):
        self.db = db
        self.cur = cur
        self.customers = Customers(self.cur, self.db)

        random_customer = fake.random_element(self.customers.get())

        self.bills = Bills(self.cur, self.db)
        self.bill = self.bills.add(customer_id=random_customer.cid, seating_id=1, created_by_staff_id=1, total=100.0, covers=5)

    def test_bill_creation_returns_correct_bill(self):
        retrieved_bill = self.bills.get(bid=self.bill.bid)
        self.assertEqual(retrieved_bill[0], self.bill)

    def test_bill_creation_with_non_existent_customer_id_raises_error(self):
        with self.assertRaises(ValueError):
            self.bills.add(customer_id=9999, seating_id=1, created_by_staff_id=1, total=100.0, covers=5)

    def test_bill_creation_with_negative_total_raises_error(self):
        with self.assertRaises(ValueError):
            self.bills.add(customer_id=1, seating_id=1, created_by_staff_id=1, total=-100.0, covers=5)

    def test_bill_deletion_removes_bill(self):
        self.bills.delete(self.bill.bid)
        self.assertEqual(self.bills.get(bid=self.bill.bid), [])

    def test_bill_deletion_with_non_existent_id_raises_error(self):
        with self.assertRaises(ValueError):
            self.bills.delete(9999)

    def test_update_valid_total_updates_value(self):
        new_total = 200.0
        self.bill.total = new_total
        self.assertEqual(self.bill.total, new_total)

    def test_update_invalid_total_raises_error(self):
        new_total = -200.0
        with self.assertRaises(ValueError):
            self.bill.total = new_total

    def test_update_valid_covers_updates_value(self):
        new_covers = 10
        self.bill.covers = new_covers
        self.assertEqual(self.bill.covers, new_covers)

    def test_update_invalid_covers_raises_error(self):
        new_covers = -1
        with self.assertRaises(ValueError):
            self.bill.covers = new_covers

    def test_update_valid_customer_id_updates_value(self):
        new_customer_id = 2
        self.bill.customer_id = new_customer_id
        self.assertEqual(self.bill.customer_id, new_customer_id)

    def test_update_invalid_customer_id_raises_error(self):
        new_customer_id = 9999
        with self.assertRaises(ValueError):
            self.bill.customer_id = new_customer_id

    def test_update_valid_seating_id_updates_value(self):
        new_seating_id = 2
        self.bill.seating_id = new_seating_id
        self.assertEqual(self.bill.seating_id, new_seating_id)

    # TODO update when seating implemented
    # def test_update_invalid_seating_id_raises_error(self):
    #     new_seating_id = 9999
    #     with self.assertRaises(ValueError):
    #         self.bill.seating_id = new_seating_id

    def test_update_valid_created_by_staff_id_updates_value(self):
        new_created_by_staff_id = 2
        self.bill.created_by_staff_id = new_created_by_staff_id
        self.assertEqual(self.bill.created_by_staff_id, new_created_by_staff_id)

    # TODO Update when staff implemented
    # def test_update_invalid_created_by_staff_id_raises_error(self):
    #     new_created_by_staff_id = 9999
    #     with self.assertRaises(ValueError):
    #         self.bill.created_by_staff_id = new_created_by_staff_id

    def test_update_created_at_returns_error(self):
        with self.assertRaises(AttributeError):
            self.bill.created_at = datetime.now()

    def test_update_valid_updated_at_updates_value(self):
        new_updated_at = datetime.now()
        self.bill.updated_at = new_updated_at

        # Assert that the difference between the two is less than 1 second
        self.assertTrue(new_updated_at - self.bill.updated_at < timedelta(seconds=1))

    def test_update_invalid_updated_at_raises_error(self):
        with self.assertRaises(TypeError):
            self.bill.updated_at = "2022-01-01"

    def test_get_all_bills_returns_correct_bills(self):
        retrieved_bills = self.bills.get()
        self.assertIn(self.bill, retrieved_bills)

    def test_get_bill_with_non_existent_id_returns_none(self):
        self.assertEqual(self.bills.get(bid=9999), [])

    def test_get_bill_with_valid_id_returns_array(self):
        retrieved_bill = self.bills.get(bid=self.bill.bid)
        self.assertIsInstance(retrieved_bill, list)

    def test_get_bill_with_valid_id_returns_correct_bill(self):
        retrieved_bill = self.bills.get(bid=self.bill.bid)
        self.assertEqual(retrieved_bill[0], self.bill)

    def test_get_bill_with_valid_id_returns_correct_length_array(self):
        retrieved_bill = self.bills.get(bid=self.bill.bid)
        self.assertEqual(len(retrieved_bill), 1)

    def test_get_bill_with_valid_customer_id_includes_correct_bill(self):
        retrieved_bills = self.bills.get(customer_id=self.bill.customer_id)
        self.assertIn(self.bill, retrieved_bills)

    def test_get_bill_with_valid_total_returns_value(self):
        retrieved_bills = self.bills.get(total=self.bill.total)
        self.assertIn(self.bill, retrieved_bills)

    def test_get_bills_created_between_returns_correct_bills(self):
        start = datetime.now() - timedelta(days=1)
        end = datetime.now() + timedelta(days=1)
        retrieved_bills = self.bills.get(created_between=(start, end))
        self.assertIn(self.bill, retrieved_bills)

    def test_get_bills_created_between_with_invalid_dates_raises_error(self):
        start = "2022-01-01"
        end = datetime.now() + timedelta(days=1)
        with self.assertRaises(TypeError):
            self.bills.get(created_between=(start, end))


if __name__ == '__main__':
    unittest.main()
