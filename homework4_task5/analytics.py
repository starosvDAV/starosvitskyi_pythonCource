import sqlite3
import random
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

DB_PATH = "bank_system.db"

def with_connection(func):
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            result = func(cursor, *args, **kwargs)
            conn.commit()
            return result
        except Exception as e:
            logging.error(f"Error in {func.__name__}: {e}")
            return None
        finally:
            conn.close()
    return wrapper

@with_connection
def assign_random_discounts(cursor):
    """Randomly assign discounts (25%, 30%, 50%) to up to 10 users."""
    cursor.execute("SELECT id FROM User")
    user_ids = [row[0] for row in cursor.fetchall()]
    selected = random.sample(user_ids, min(len(user_ids), 10))
    discounts = {uid: random.choice([25, 30, 50]) for uid in selected}
    logging.info(f"Assigned discounts: {discounts}")
    return discounts

@with_connection
def get_users_with_debts(cursor):
    """Return full names of users with negative account balances."""
    cursor.execute("""
        SELECT u.Name, u.Surname FROM User u
        JOIN Account a ON u.id = a.User_id
        WHERE a.Amount < 0
    """)
    return [f"{row[0]} {row[1]}" for row in cursor.fetchall()]

@with_connection
def get_richest_bank(cursor):
    """Return bank name with biggest capital (sum of balances)."""
    cursor.execute("""
        SELECT b.name, SUM(a.Amount) as total FROM Bank b
        JOIN Account a ON b.id = a.Bank_id
        GROUP BY b.id
        ORDER BY total DESC
        LIMIT 1
    """)
    result = cursor.fetchone()
    return result[0] if result else None

@with_connection
def get_bank_with_oldest_client(cursor):
    """Return the bank name that serves the oldest client."""
    cursor.execute("""
        SELECT b.name, MIN(u.Birth_day) FROM Bank b
        JOIN Account a ON b.id = a.Bank_id
        JOIN User u ON a.User_id = u.id
        WHERE u.Birth_day IS NOT NULL
    """)
    result = cursor.fetchone()
    return result[0] if result else None

@with_connection
def get_bank_with_most_unique_senders(cursor):
    """Bank with most unique users who performed outbound transactions."""
    cursor.execute("""
        SELECT t.Bank_sender_name, COUNT(DISTINCT a.User_id) FROM Transaction t
        JOIN Account a ON t.Account_sender_id = a.id
        GROUP BY t.Bank_sender_name
        ORDER BY COUNT(DISTINCT a.User_id) DESC
        LIMIT 1
    """)
    result = cursor.fetchone()
    return result[0] if result else None

@with_connection
def delete_incomplete_users_and_accounts(cursor):
    """Delete users/accounts where required fields are missing."""
    cursor.execute("DELETE FROM Account WHERE User_id IS NULL OR Type IS NULL OR Bank_id IS NULL OR Amount IS NULL")
    cursor.execute("DELETE FROM User WHERE Name IS NULL OR Surname IS NULL OR Accounts IS NULL")
    logging.info("Deleted incomplete users and accounts.")

@with_connection
def get_user_transactions_last_3_months(cursor, user_id):
    """Return transactions of a user within the last 3 months."""
    date_limit = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
    cursor.execute("""
        SELECT * FROM Transaction
        WHERE Account_sender_id IN (
            SELECT id FROM Account WHERE User_id = ?
        )
        AND Datetime >= ?
    """, (user_id, date_limit))
    return cursor.fetchall()
