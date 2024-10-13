from sqlalchemy import create_engine, text

# Replace these with your actual database connection details
db_uri = "postgresql://telegram_bot_user:your_password@localhost:5432/telegram_bot_db"
engine = create_engine(db_uri)

# SQL command to delete all entries from the user_context table
delete_query = text("DELETE FROM user_context")

# Execute the query
with engine.connect() as connection:
    result = connection.execute(delete_query)
    connection.commit()

print(f"Deleted {result.rowcount} rows from user_context table")

with engine.connect() as connection:
    result = connection.execute(text("SELECT * FROM user_context"))
    print(result.fetchall())

