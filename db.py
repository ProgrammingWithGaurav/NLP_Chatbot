# import sqlite
import sqlite3

# create a connection to the database
conn = sqlite3.connect('./db/data.db')

# function to initialize the database
def init_db():
    # create a cursor object
    cursor = conn.cursor()

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
    cursor.close()

# function to get the order status
def get_order_status(order_id):
    cursor = conn.cursor()
    try:
        # Execute the SQL command
        cursor.execute(f'SELECT status FROM order_tracking WHERE order_id = {int(order_id)}')
        status = cursor.fetchone()

        # Always close the connection before returning
        conn.close()

        if status is not None:
            return status[0]
        else:
            return None
    except sqlite3.ProgrammingError as e:
        print(f"An error occurred: {e}")
        conn.close()

# function to get next order i
def get_next_order_id():
    cursor = conn.cursor()
    try:
        # Execute the SQL command
        cursor.execute('SELECT MAX(order_id) FROM orders')
        order_id = cursor.fetchone()

        cursor.close()

        if order_id[0] is not None:
            return order_id[0] + 1
        else:
            return 1
    except sqlite3.ProgrammingError as e:
        print(f"An error occurred: {e}")
        conn.close()

# function to get the id of the food items
def get_food_item_id(food_item: str):
    try: 
        cursor = conn.cursor()
        cursor.execute(f'SELECT item_id FROM food_items WHERE item_name = "{food_item}"')
        item_id = cursor.fetchone()

        cursor.close()

        if item_id is not None:
            return item_id[0]
        else:
            return None

    except sqlite3.ProgrammingError as e:
        print(f"An error occurred: {e}")
        conn.close()

def insert_food_item(food_item, quantity, order_id):
    cursor = conn.cursor()
    try:
        # Get the item_id from the food_items table
        item_id = get_food_item_id(food_item)
        if item_id is None:
            return "Item not found"

        # Get the price of the item
        cursor.execute(f'SELECT price FROM food_items WHERE item_id = {int(item_id)}')
        price = cursor.fetchone()

        # Calculate the total price
        total_price = price[0] * quantity 

        # Insert the order into the orders table
        cursor.execute(f'INSERT INTO orders (order_id, item_id, quantity, total_price) VALUES ({order_id}, {item_id}, {quantity}, {total_price})')

        # Commit changes
        conn.commit()
        cursor.close()

        return "Order inserted successfully"

    except sqlite3.ProgrammingError as e:
        print(f"An error occurred: {e}")
        conn.close()


# add food items manually 

# Price in USD
food_items = [
    ("Pizza", 10.00),
    ("Burger", 5.00),
    ("Fries", 3.00),
    ("Cola", 2.00),
    ("Sandwich", 4.00),
    ("Chicken", 12.00),
    ("Cake", 6.00)
]
        
def insert_food_items():
    cursor = conn.cursor()
    try:
        # Insert food items into the food_items table
        cursor.executemany('INSERT INTO food_items (item_name, price) VALUES (?, ?)', food_items)

        # Commit changes
        conn.commit()
        cursor.close()

        return "Food items inserted successfully"

    except sqlite3.ProgrammingError as e:
        print(f"An error occurred: {e}")
        cursor.close()

if __name__ == '__main__':
    insert_food_items()
    
    