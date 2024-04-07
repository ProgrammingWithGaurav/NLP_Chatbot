import sqlite3
conn = sqlite3.connect('./db/data.db')

food_item = "Burger"

cursor = conn.cursor()
cursor.execute(f'SELECT item_id FROM food_items WHERE item_name = "{food_item}"')
item_id = cursor.fetchone()


print(item_id[0])
cursor.close()