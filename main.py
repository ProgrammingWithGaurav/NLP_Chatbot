from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# Import the db 
import db 

# utility functions
import utils


inprogress_orders = {}

#initialize the database
db.init_db()

app = FastAPI()

@app.post("/")
async def handle_request(request: Request):
    # get json data from the request
    data = await request.json()
    
    # extract the necessary data
    intent = data['queryResult']['intent']['displayName']
    parameters = data['queryResult']['parameters']
    output_contexts = data['queryResult']['outputContexts']

    session_id = utils.extract_session_id(output_contexts[0]['name'])

    intent_handler_dict = {
        'order.add - context: ongoing-order': add_to_order,
        'order.complete - context: ongoing-order': complete_order,
        'track.order - context: ongoing-tracking': track_order,
        'order.menu': show_menu,
        'order.remove - context: ongoing-order': remove_from_order,
        'order.cancel - context: ongoing-order': cancel_order,
    }
    return intent_handler_dict[intent](parameters, session_id)

# TRACK ORDER
def track_order(parameter: dict, session_id: str):  
    order_id = parameter['order_id']
    status = db.get_order_status(int(order_id))
    if(status):
        fullfillment_text = f'The status of order {order_id} is {status}'
    else:
        fullfillment_text = f'Order {order_id} not found'
    
    return JSONResponse(content= {
            'fulfillmentText': fullfillment_text,
        })
        

# ADD ORDER
def add_to_order(parameters: dict, session_id: str):
    food_items = parameters['food-item']
    quantity = parameters['number']

    # check if the food item has quantity
    if len(food_items) != len(quantity):    
        fullfillment_text = 'Please provide the quantity for each food item'

    else : 
        # food_items = ['pizza', 'burger']
        # quantity = [1, 2]
        # result: {'pizza': 1, 'burger': 2}
        new_food_dict = dict(zip(food_items, quantity))

        if session_id in inprogress_orders:
            inprogress_orders[session_id].update(new_food_dict) 
        else:
            inprogress_orders[session_id] = new_food_dict

        order_str = utils.get_str_from_food_dict(inprogress_orders[session_id])
        fullfillment_text = f'Added {order_str} to your order. Anything else?'

    return JSONResponse(content= {
            'fulfillmentText': fullfillment_text,
        })

# COMPLETE ORDER
def complete_order(parameters: dict, session_id: str):
    address = parameters['address']
    if session_id in inprogress_orders:
        order = inprogress_orders[session_id]
        if len(order) == 0:
            fullfillment_text = 'Your order is empty. What would you like to order?'
        else:
            if address == '':
                fullfillment_text = 'Please provide an address for delivery'
            else:
                order_id = save_to_db(order, address)
                if order_id != -1:
                    order_total = db.get_order_total(order_id)
                    fullfillment_text = f'Your order will be delivered to {address}. Your total is {order_total}, order id is {order_id}'
                    inprogress_orders.pop(session_id)
                else:
                    fullfillment_text = 'An error occurred. Please try again'
    else:
        fullfillment_text = 'Trouble finding your order. Please try again'

    return JSONResponse(content= {
            'fulfillmentText': fullfillment_text,
        })

def save_to_db(order: dict, address: str):
    # get next order id
    next_order_id = db.get_next_order_id()

    # {'pizza': 1, 'burger': 2}
    for food_item, quantity in order.items():
        item_id = db.get_food_item_id(food_item)
        rcode = db.insert_order_item(food_item, quantity, next_order_id)
        if rcode == -1:
            return -1
            
    # set in-progress order to completed
    db.insert_order_tracking(next_order_id, 'in progress', address)
    return next_order_id
    
def show_menu(parameters: dict, session_id: str):
    # show items with price
    menu = db.get_menu()
    menu_str = utils.get_str_from_menu(menu)
    fullfillment_text = f'Here is the menu: {menu_str}. What would you like to order?'
    return JSONResponse(
        content= {
            'fulfillmentText': fullfillment_text,
        }
        
    )

def remove_from_order(parameters: dict, session_id: str):
    food_item = parameters['food-item']
    current_order = inprogress_orders[session_id]

    removed_items = []
    no_such_items = []

    for item in food_item:
        if item not in current_order:
            no_such_items.append(item)
        else:
            removed_items.append(item)
            del current_order[item]

    if len(removed_items) > 0:
        fulfillmentText =f'Removed {", ".join(removed_items)} from your order'
    if len(no_such_items) > 0:
        fulfillmentText =f'Could not find {", ".join(no_such_items)} in your order'

    if len(current_order.keys()) == 0:
        fulfillmentText += 'Your order is empty. What would you like to order?'

    else :
        order_str = utils.get_str_from_food_dict(current_order)
        fulfillmentText += f'Your order now contains {order_str}. Anything else?'

    return JSONResponse(
        content= {
            'fulfillmentText': fulfillmentText,
        }
    )


# CACNCEL ORDER
def cancel_order(parameters: dict, session_id: str):
    if session_id in inprogress_orders:
        inprogress_orders.pop(session_id)
        fullfillment_text = 'Your order has been cancelled'
    else:
        fullfillment_text = 'Trouble finding your order. Please try again'

    return JSONResponse(
        content= {
            'fulfillmentText': fullfillment_text,
        }
    )

@app.get("/")
async def hello_world(request: Request):
    return JSONResponse(
        content= {
            'result': 'Hello World',
        }
    )
