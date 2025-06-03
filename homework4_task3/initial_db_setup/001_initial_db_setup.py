import sqlite3
import argparse
import sys

# Обробка параметрів командного рядка
parser = argparse.ArgumentParser(description="Initial DB setup with optional uniqueness constraint on User Name+Surname")
parser.add_argument("--enforce-user-uniqueness", action="store_true", help="Enforce uniqueness on User(Name, Surname)")
args = parser.parse_args()

# Підключення до бази
conn = sqlite3.connect("bank_system.db")
cursor = conn.cursor()

# Видаляємо таблиці, якщо існують (для перезапуску)
cursor.execute("DROP TABLE IF EXISTS Transaction")
cursor.execute("DROP TABLE IF EXISTS Account")
cursor.execute("DROP TABLE IF EXISTS User")
cursor.execute("DROP TABLE IF EXISTS Bank")

# Створення таблиці Bank
cursor.execute("""
CREATE TABLE Bank (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
)
""")

# Створення таблиці User (з опційною унікальністю)
if args.enforce_user_uniqueness:
    cursor.execute("""
    CREATE TABLE User (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        surname TEXT NOT NULL,
        birth_day TEXT,
        accounts TEXT NOT NULL,
        UNIQUE(name, surname)
    )
    """)
    print("Uniqueness constraint on User(Name, Surname) is ON")
else:
    cursor.execute("""
    CREATE TABLE User (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        surname TEXT NOT NULL,
        birth_day TEXT,
        accounts TEXT NOT NULL
    )
    """)
    print("Uniqueness constraint on User(Name, Surname) is OFF")

# Створення таблиці Account
cursor.execute("""
CREATE TABLE Account (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('credit', 'debit')),
    account_number TEXT NOT NULL UNIQUE,
    bank_id INTEGER NOT NULL,
    currency TEXT NOT NULL,
    amount REAL NOT NULL,
    status TEXT CHECK(status IN ('gold', 'silver', 'platinum')),
    FOREIGN KEY(user_id) REFERENCES User(id),
    FOREIGN KEY(bank_id) REFERENCES Bank(id)
)
""")

# Створення таблиці Transaction
cursor.execute("""
CREATE TABLE Transaction (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bank_sender_name TEXT NOT NULL,
    account_sender_id INTEGER NOT NULL,
    bank_receiver_name TEXT NOT NULL,
    account_receiver_id INTEGER NOT NULL,
    sent_currency TEXT NOT NULL,
    sent_amount REAL NOT NULL,
    datetime TEXT,
    FOREIGN KEY(account_sender_id) REFERENCES Account(id),
    FOREIGN KEY(account_receiver_id) REFERENCES Account(id)
)
""")

# Завершення
conn.commit()
conn.close()
print("✅ Database structure created successfully.")
