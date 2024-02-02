import unittest

from faker import Faker

from connector import connect
from helper import table_exists
from models.bill import Bills
from models.customer import Customers, Customer

# Connect to test database (test/nea.db)
db = connect()

# Create cursor
cur = db.cursor()

# Create Faker object
fake = Faker()


class TestCustomer(unittest.TestCase):
    def setUp(self):
        self.db = db
        self.cur = cur
        self.customers = Customers(self.cur, self.db)
        self.customer = self.customers.add(fake.name(), fake.boolean())
        self.bills = Bills(self.cur, self.db)

        self.__reset()

    def test_set_up_created_table(self):
        """
        Test that the customer table exists
        """
        self.assertTrue(table_exists('customer'))

    def test_adding_valid_customer_adds_to_database(self):
        """
        Tests that a customer being added is added to the database
        """
        # Add a customer
        fake_name = fake.name()  # Generates a fake name
        fake_bool = fake.boolean()  # Generates a fake boolean value (True or False)
        new_customer = self.customers.add(fake_name, fake_bool)

        # Assert that the new customer is in self.customers
        self.assertIn(new_customer, self.customers.customers)

        # Assert that the new customer is in the database
        self.cur.execute('SELECT * FROM customer WHERE id=?', (new_customer.cid,))
        self.assertIsNotNone(self.cur.fetchone())

    def test_setting_same_name_does_nothing(self):
        """
        Test that setting the same name for a customer does nothing
        """
        original_name = self.customer.name
        self.customer.name = original_name
        self.assertEqual(self.customer.name, original_name)

    def test_setting_name_to_non_string_raises_type_error(self):
        """
        Test that setting the name of a customer to a non-string raises a TypeError
        """
        with self.assertRaises(TypeError):
            self.customer.name = 123  # Non-string value

    def test_setting_name_to_empty_string_raises_value_error(self):
        """
        Test that setting the name of a customer to an empty string raises a ValueError
        """
        with self.assertRaises(ValueError):
            self.customer.name = ""  # Empty string

    def test_setting_name_to_long_string_raises_value_error(self):
        """
        Test that setting the name of a customer to a string longer than 50 characters raises a ValueError
        """
        with self.assertRaises(ValueError):
            self.customer.name = "a" * 51

    def test_setting_same_vip_does_nothing(self):
        original_vip = self.customer.vip
        self.customer.vip = original_vip
        self.assertEqual(self.customer.vip, original_vip)

    def test_setting_vip_to_non_boolean_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.customer.vip = "not a boolean"

    def test_deleting_existent_customer_removes_from_db(self):
        """
        Tests that a customer being deleted is deleted from the database
        """
        # Add a customer
        fake_name = fake.name()
        fake_bool = fake.boolean()
        new_customer = self.customers.add(fake_name, fake_bool)

        # Delete customer
        self.customers.delete(new_customer.cid)

        # Assert that the new customer is not in self.customers
        self.assertNotIn(new_customer, self.customers.customers)

        # Assert that the new customer is not in the database
        self.cur.execute('SELECT * FROM customer WHERE id=?', (new_customer.cid,))
        self.assertIsNone(self.cur.fetchone())

    def test_deleting_nonexistent_customer_raises_value_error(self):
        """
        Test that deleting a customer that does not exist raises an error
        """
        nonexistent_id = 9999  # Assuming this id does not exist
        with self.assertRaises(ValueError):
            self.customers.delete(nonexistent_id)

    def test_updating_customers_name_updates_database(self):
        """
        Tests that a customer's name being updated is reflected in the database
        """
        # Add a customer
        fake_name = fake.name()
        fake_bool = fake.boolean()
        new_customer = self.customers.add(fake_name, fake_bool)

        # Update name
        new_name = fake.name()
        new_customer.name = new_name

        # Assert that the customers name is updated in self.customers
        self.assertEqual(new_customer.name, new_name)

    def test_updating_non_existent_customer_raises_attribute_error(self):
        """
        Test that updating a customer that does not exist raises an error
        """
        nonexistent_id = 9999  # Assuming this id does not exist
        with self.assertRaises((ValueError, AttributeError)):
            customer = self.customers.get(cid=nonexistent_id)
            customer.name = "New Name"

    def test_updating_existing_customers_vip_status_updates_database(self):
        """
        Tests that a customer's vip status being updated is reflected in the database
        """
        # Add a customer
        fake_name = fake.name()
        fake_bool = fake.boolean()
        new_customer = self.customers.add(fake_name, fake_bool)

        # Update vip status
        new_bool = not fake_bool
        new_customer.vip = new_bool

        # Assert that the customers vip status is updated in self.customers
        self.assertEqual(new_customer.vip, new_bool)

    def test_getting_customer_by_id_returns_correct_customer(self):
        """
        Tests that getting a customer by id returns the correct customer
        """
        # Add a customer
        fake_name = fake.name()
        fake_bool = fake.boolean()
        new_customer = self.customers.add(fake_name, fake_bool)

        # Get customer by id
        retrieved_customer = self.customers.get(cid=new_customer.cid)

        # Assert that the retrieved customer is the new customer
        self.assertEqual(retrieved_customer, [new_customer])

    def test_getting_customer_by_name_returns_correctly(self):
        """
        Tests that getting a customer by name returns the correct customer
        """
        # Add a customer
        fake_name = fake.name()
        fake_bool = fake.boolean()
        new_customer = self.customers.add(fake_name, fake_bool)

        # Get customers by name
        retrieved_customers = self.customers.get(name=new_customer.name)

        # Assert that the retrieved customers list contains the new customer
        self.assertIn(new_customer, retrieved_customers)

    def test_getting_customer_by_vip_status_returns_correctly(self):
        """
        Tests that getting a customer by vip status returns the correct customer
        """
        # Add a customer
        fake_name = fake.name()
        fake_bool = fake.boolean()
        new_customer = self.customers.add(fake_name, fake_bool)

        print(new_customer)

        # Get customers by vip status
        retrieved_customers = self.customers.get(vip=new_customer.vip)

        # Assert that the retrieved customers list contains the new customer
        self.assertIn(new_customer, retrieved_customers)

    def test_getting_all_customers_returns_all(self):
        """
        Tests that all customers being retrieved is retrieved from the database
        """
        # Add a customer
        fake_name = fake.name()
        fake_bool = fake.boolean()
        new_customer = self.customers.add(fake_name, fake_bool)

        # Get all customers
        all_customers = self.customers.customers

        # Assert that the all_customers list contains the new customer
        self.assertIn(new_customer, all_customers)

    def test_getting_customer_by_non_existent_id_returns_none(self):
        """
        Test that getting a customer by an id that does not exist returns None
        """
        nonexistent_id = 9999  # Assuming this id does not exist
        self.assertEqual(self.customers.get(cid=nonexistent_id), [])

    def test_getting_id_of_existing_customer_returns_correct_id(self):
        """
        Tests that getting a customer's id returns the correct id
        """
        self.assertEqual(self.customer.cid, self.customer._id)

    def test_getting_id_of_nonexistent_customer_raises_value_error(self):
        """
        Test that getting a customer's id that does not exist raises a ValueError
        """
        with self.assertRaises(ValueError):
            nonexistent_customer = Customer(9999, self.cur, self.db)  # Assuming this id does not exist
            nonexistent_customer.cid

    # TODO Fix when bills are implemented
    # def test_getting_bills_of_existing_customer_returns_correct_bills(self):
    #     """
    #     Tests that getting a customer's bills returns the correct bills
    #     """
    #     # Create bill
    #     random_total = fake.random_int(0, 1000) / 10
    #     random_covers = fake.random_int(1, 10)
    #     new_bill = self.bills.add(self.customer.cid, total=random_total, covers=random_covers)
    #
    #     self.assertIn(new_bill, self.customer.bills)
    #
    # def test_adding_bill_to_existing_customer_updates_bills(self):
    #     """
    #     Tests that adding a bill to a customer updates the bills
    #     """
    #     # Create bill
    #     random_total = fake.random_int(0, 1000) / 10
    #     random_covers = fake.random_int(1, 10)
    #     new_bill = self.bills.add(total=random_total, covers=random_covers)
    #
    #     # Add bill to customer
    #     self.customer.add_bill(new_bill.bid)
    #
    #     # Assert that the bill was added to the customer
    #     original_bills = self.customer.bills
    #     self.assertNotEqual(self.customer.bills, original_bills)
    #
    # def test_adding_nonexistent_bill_to_customer_raises_value_error(self):
    #     """
    #     Test that adding a bill that does not exist to a customer raises a ValueError
    #     """
    #     with self.assertRaises(ValueError):
    #         self.customer.add_bill(9999)  # Assuming this bill id does not exist

    def test_clear_customers_removes_all_values(self):
        """
        Tests that the clear method removes all customers from the database
        """
        # Add a few customers
        for _ in range(3):
            fake_name = fake.name()
            fake_bool = fake.boolean()
            self.customers.add(fake_name, fake_bool)

        # Assert that customers were added
        self.assertTrue(len(self.customers.customers) > 0)

        # Clear customers
        self.customers.clear()

        # Assert that all customers were removed
        self.assertEqual(len(self.customers.customers), 0)

    def __reset(self):
        # Clear customers
        self.customers.customers.clear()


if __name__ == '__main__':
    unittest.main()
