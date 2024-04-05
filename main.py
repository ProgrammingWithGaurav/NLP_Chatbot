from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# Import the db 
import db


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
    print(f'Intent: {intent}')
    
    if intent == 'track.order - context: ongoing-tracking':
        return JSONResponse(
            content= {
                'fulfillmentText': f'Received =={intent}== in the backend',
            }
        )

@app.get("/")
async def handle_request(request: Request):
    return JSONResponse(
        content= {
            'result': 'Hello World',
        }
    )
        