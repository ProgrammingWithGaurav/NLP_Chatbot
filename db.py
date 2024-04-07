from pymongo import MongoClient
import os
import dotenv

# Load environment variables
dotenv.load_dotenv()

# Create a client to connect to your MongoDB server
client = MongoClient(os.getenv("MONGODB_URI"))

# Access your database (it will be created if it doesn't exist)
db = client['FoodDeliveryChatbot']

# Access your collections (similar to tables in SQL databases)
food_items = db['food_items']
order_tracking = db['order_tracking']
orders = db['orders']

# Function to initialize the database
def init_db():
    # Check if the food_items collection is  empty
    if food_items.count_documents({}) == 0:
        # Insert data into food_items collection
        food_items.insert_many([
            {"item_name": "Pizza", "price": 10.00},
            {"item_name": "Burger", "price": 5.00},
            {"item_name": "Fries", "price": 3.00},
            {"item_name": "Cola", "price": 2.00},
            {"item_name": "Sandwich", "price": 4.00},
            {"item_name": "Chicken", "price": 12.00},
            {"item_name": "Cake", "price": 6.00}
        ])

if __name__ == '__main__':
    init_db()

    


# Function to get menu
def get_menu():
    try:
        # Fetch all documents in the food_items collection
        menu = food_items.find({}, {'_id': 0}) # _id is excluded from the result
        # Convert the cursor to a list
        return list(menu)
    except Exception as e:
        print(f"An error occurred: {e}")

# function to get the order status
def get_order_status(order_id):
    try:
        # Fetch the order status from the order_tracking collection
        status = order_tracking.find_one({"order_id": order_id}, {'_id': 0})
        return status['status']
    except Exception as e:
        print(f"An error occurred: {e}")
        
# Function to get next order id
def get_next_order_id():
    try:
        # Fetch the document with the highest order_id
        order = order_tracking.find_one(sort=[("order_id", -1)])
        if order is not None:
            return order["order_id"] + 1
        else:
            return 1
    except Exception as e:
        print(f"An error occurred: {e}")

# Function to get the id of the food items
def get_food_item_id(food_item: str):
    try:
        # Fetch the document with the given item_name
        item = food_items.find_one({"item_name": food_item}, {"_id": 1}) # _id is included in the result
        if item is not None:
            return item["_id"]
        else:
            return None
    except Exception as e:
        print(f"An error occurred: {e}") 

# Function to insert order item
def insert_order_item(food_item, quantity, order_id):
    try:
        # Get the item_id from the food_items collection
        item_id = get_food_item_id(food_item)
        print(food_item)

        # Get the price of the item
        item = food_items.find_one({"_id": item_id}, {"price": 1})
        price = item["price"]

        # Calculate the total price
        total_price = price * quantity 

        # Insert the order into the orders collection
        orders.insert_one({"order_id": order_id, "item_id": item_id, "quantity": quantity, "total_price": total_price})

        return "Order inserted successfully"
    except Exception as e:
        print(f"An error occurred: {e}")

# function to get total order price
def get_order_total(order_id):
    try :
        # get all the orers with the given order_id
        order = orders.find({"order_id": order_id})
        total_price = 0
        for item in order:
            total_price += item["total_price"]
        return total_price
    except Exception as e:
        print(f"An error occurred: {e}")
        

# insert order tracking
def insert_order_tracking(order_id, status):
    try:
        # Insert the order tracking status into the order_tracking collection
        order_tracking.insert_one({"order_id": order_id, "status": status})
    except Exception as e:
        print(f"An error occurred: {e}")
