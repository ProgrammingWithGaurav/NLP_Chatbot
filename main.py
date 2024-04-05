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
        # 'order.remove - context: ongoing-order': remove_from_order,
    }
    return intent_handler_dict[intent](parameters, session_id)

# TRACK ORDER
def track_order(parameter: dict, session_id: str):  
    order_id = parameter['order_id']
    status = db.get_order_status(order_id)
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
    if session_id in inprogress_orders:
        order = inprogress_orders[session_id]
        save_to_db(order)
    else:
        fullfillment_text = 'Trouble finding your order. Please try again'

    return JSONResponse(content= {
            'fulfillmentText': fullfillment_text,
        })

def save_to_db(order: dict):
    # get next order id
    next_order_id = db.get_next_order_id()

    # {'pizza': 1, 'burger': 2}
    for food_item, quantity in order.items():
        item_id = db.get_item_id(food_item)
        db.insert_order_item(item_id, quantity, next_order_id)


@app.get("/")
async def hello_world(request: Request):
    return JSONResponse(
        content= {
            'result': 'Hello World',
        }
    )
