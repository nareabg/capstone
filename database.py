import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_file):
        self.db_file = db_file
        self.conn = None
        self.cursor = None

    def connect(self):
        """
        Connects to the SQLite database and creates the 'customers' table if it doesn't exist.
        """
        self.conn = sqlite3.connect(self.db_file)
        self.cursor = self.conn.cursor()

        # Create the 'customers' table if it doesn't exist
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY,
                purchase_date DATE NOT NULL,
                customer_id INTEGER NOT NULL,
                product_price INTEGER NOT NULL,
                product_quantity INTEGER NOT NULL,
                gender TEXT,
                location TEXT
            )
        """)

        self.conn.commit()

    def insert_data(self, data):
        """
        Inserts the given data into the 'customers' table.

        Args:
            data: A list of tuples containing the data to be inserted. Each tuple should contain the following fields
                in order: purchase_date (str or datetime object), customer_id (int), product_price (int), product_quantity (int),
                gender (str), location (str).
        """
        # Convert the purchase_date field to a datetime object if it's not already
        data = [(datetime.strptime(row[0], '%Y-%m-%d') if isinstance(row[0], str) else row[0], *row[1:]) for row in data]

        # Insert the data into the 'customers' table
        self.cursor.executemany("""
            INSERT INTO customers (purchase_date, customer_id, product_price, product_quantity, gender, location)
            VALUES (?, ?, ?, ?, ?, ?)
        """, data)

        self.conn.commit()

    def get_data(self):
        """
        Retrieves all the data from the 'customers' table.

        Returns:
            A list of tuples containing the data. Each tuple contains the following fields in order:
            purchase_date (datetime object), customer_id (int), product_price (int), product_quantity (int),
            gender (str), location (str).
        """
        self.cursor.execute("""
            SELECT purchase_date, customer_id, product_price, product_quantity, gender, location
            FROM customers
        """)

        data = self.cursor.fetchall()

        # Convert the purchase_date field from a string to a datetime object
        data = [(datetime.strptime(row[0], '%Y-%m-%d'), *row[1:]) for row in data]

        return data

    def calculate_clv(self):
        """
        Calculates the customer lifetime value.
        """
        # Placeholder for future implementation
        pass

    def predict_future(self):
        """
        Predicts future customer behavior.
        """
        # Placeholder for future implementation
        pass
