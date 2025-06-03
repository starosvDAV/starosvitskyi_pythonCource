import logging
from analytics import *

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def main():
    try:
        print("🎲 Discount assignment:")
        print(assign_random_discounts())

        print("\n💳 Users with debts:")
        for name in get_users_with_debts():
            print(f"- {name}")

        print("\n🏦 Richest bank:", get_richest_bank())
        print("👴 Bank with oldest client:", get_bank_with_oldest_client())
        print("📤 Bank with most outbound transfers:", get_bank_with_most_unique_senders())

        print("\n🧹 Cleaning incomplete entries...")
        delete_incomplete_users_and_accounts()

        print("\n📋 Last 3 months transactions for user_id = 1:")
        transactions = get_user_transactions_last_3_months(1)
        for tx in transactions:
            print(tx)

    except Exception as e:
        logging.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
