@property
    def bills(self) -> list:
        """
        Returns the bills associated with the Customer by ID
        """
        cur.execute(f"""
           SELECT * FROM bill WHERE customer_id = {self.cid}
        """)
        return cur.fetchall() if cur.fetchall() else []

    @bills.getter
    def bills(self) -> list:
        """
        Returns the bills associated with the Customer by ID
        """
        cur.execute(f"""
           SELECT * FROM bill WHERE customer_id = {self.cid}
        """)
        return cur.fetchall() if cur.fetchall() else []

    def add_bill(self, new_bill_id: int) -> None:
        """
        Adds a bill to the Customer by ID
        """

        # If the bill does not exist, raise a ValueError
        if not row_exists("bills", new_bill_id):
            raise ValueError(f'Bill<{new_bill_id}> does not exist')

        cur.execute(f"""
            UPDATE bill 
            SET 
                customer_id = {self.cid},
                updated_at = {datetime.now()} 
            WHERE id = {new_bill_id}
        """)
        db.commit()
        print(f'Bill<{new_bill_id}> added to Customer<{self.cid}>')