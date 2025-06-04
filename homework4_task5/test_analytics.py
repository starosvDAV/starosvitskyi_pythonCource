import unittest
from analytics import (
    assign_random_discounts,
    get_users_with_debts,
    get_richest_bank,
    get_bank_with_oldest_client,
    get_bank_with_most_unique_senders,
    delete_incomplete_users_and_accounts,
    get_user_transactions_last_3_months
)

class TestAnalyticsFunctions(unittest.TestCase):

    def test_assign_random_discounts(self):
        discounts = assign_random_discounts()
        self.assertIsInstance(discounts, dict)
        self.assertLessEqual(len(discounts), 10)
        for uid, discount in discounts.items():
            self.assertIn(discount, [25, 30, 50])

    def test_get_users_with_debts(self):
        result = get_users_with_debts()
        self.assertIsInstance(result, list)
        for name in result:
            self.assertIsInstance(name, str)

    def test_get_richest_bank(self):
        richest = get_richest_bank()
        self.assertIsInstance(richest, str)

    def test_get_bank_with_oldest_client(self):
        bank = get_bank_with_oldest_client()
        self.assertIsInstance(bank, str)

    def test_get_bank_with_most_unique_senders(self):
        bank = get_bank_with_most_unique_senders()
        self.assertIsInstance(bank, str)

    def test_delete_incomplete_users_and_accounts(self):
        # just make sure no errors raised
        result = delete_incomplete_users_and_accounts()
        self.assertIsNone(result)

    def test_get_user_transactions_last_3_months(self):
        result = get_user_transactions_last_3_months(1)  # test user ID = 1
        self.assertIsInstance(result, list)
        for tx in result:
            self.assertIsInstance(tx, tuple)

if __name__ == '__main__':
    unittest.main()
