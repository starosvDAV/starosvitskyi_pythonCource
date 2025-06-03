import sqlite3
import logging

def db_connection(func):
    def wrapper(*args, **kwargs):
        try:
            conn = sqlite3.connect('bank_system.db')
            cursor = conn.cursor()
            result = func(cursor, *args, **kwargs)
            conn.commit()
            conn.close()
            logging.info(f"{func.__name__} executed successfully.")
            return {"status": "success", "data": result}
        except Exception as e:
            logging.error(f"Error in {func.__name__}: {str(e)}")
            return {"status": "fail", "message": str(e)}
    return wrapper
