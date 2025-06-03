import csv
import logging
from db.connection import db_connection
from validators.validation import *
from currency import convert_currency

from homework4_task4.validators.validation import validate_datetime, validate_account_number, validate_field, \
    ALLOWED_TYPES, validate_user_name, ALLOWED_STATUS


@db_connection
def add_user(cursor, *users):
    for user in users:
        if isinstance(user, dict):
            name, surname = validate_user_name(user["user_full_name"])
            cursor.execute("""
                INSERT INTO User (Name, Surname, Birth_day, Accounts)
                VALUES (?, ?, ?, ?)
            """, (name, surname, user.get("Birth_day"), user.get("Accounts")))
    return f"{len(users)} user(s) added."

@db_connection
def add_bank(cursor, *banks):
    for bank in banks:
        cursor.execute("INSERT INTO Bank (name) VALUES (?)", (bank["name"],))
    return f"{len(banks)} bank(s) added."

@db_connection
def add_account(cursor, *accounts):
    for acc in accounts:
        acc_num = validate_account_number(acc["Account Number"])
        validate_field(acc["Type"], ALLOWED_TYPES, "Type")
        validate_field(acc["Status"], ALLOWED_STATUS, "Status")
        cursor.execute("""
            INSERT INTO Account (User_id, Type, Account Number, Bank_id, Currency, Amount, Status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            acc["User_id"], acc["Type"], acc_num,
            acc["Bank_id"], acc["Currency"],
            acc["Amount"], acc["Status"]
        ))
    return f"{len(accounts)} account(s) added."

@db_connection
def transfer_money(cursor, sender_acc, receiver_acc, amount, currency, dt=None):
    dt = validate_datetime(dt)
    cursor.execute("SELECT Amount, Currency FROM Account WHERE Id=?", (sender_acc,))
    s_data = cursor.fetchone()
    if not s_data or s_data[0] < amount:
        return "Insufficient funds"
    converted_amount = convert_currency(currency, s_data[1], amount)
    cursor.execute("UPDATE Account SET Amount = Amount - ? WHERE Id=?", (amount, sender_acc))
    cursor.execute("UPDATE Account SET Amount = Amount + ? WHERE Id=?", (converted_amount, receiver_acc))
    cursor.execute("""
        INSERT INTO Transaction (
            Bank_sender_name, Account_sender_id, Bank_receiver_name, 
            Account_receiver_id, Sent Currency, Sent Amount, Datetime)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        "SenderBank", sender_acc, "ReceiverBank",
        receiver_acc, currency, amount, dt
    ))
    return "Transfer completed"
