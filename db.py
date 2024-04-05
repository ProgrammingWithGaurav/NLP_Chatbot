# import sqlite
import sqlite3

# create a connection to the database
conn = sqlite3.connect('./db/data.db')
cursor = conn.cursor()

# function to initialize the database
def init_db():

    # Execute SQL command to create the food_orders table
    # orders table
    cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
                        order_id INTEGER PRIMARY KEY,
                        item_id INTEGER,
                        quantity INTEGER,
                        total_price REAL
                        )''')

    # food items table
    cursor.execute('''CREATE TABLE IF NOT EXISTS food_items (
                        item_id INTEGER PRIMARY KEY,
                        item_name TEXT,
                        price REAL
                        )''')


    # order tracking table
    cursor.execute('''CREATE TABLE IF NOT EXISTS order_tracking (
                        order_id INTEGER PRIMARY KEY,
                        status TEXT
                    )''')

    # Commit changes and close connection
    conn.commit()
    conn.close()