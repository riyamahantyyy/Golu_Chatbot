from fastapi import FastAPI
from fastapi import  Request
from fastapi.responses import JSONResponse
import db
import session_file
app = FastAPI()
inprogress_orders={}

@app.post("/")
async def handle_request(request: Request):
    #retrieve json data from request
    payload = await request.json()
    #extract necessary info from payload
    intent = payload['queryResult']['intent']['displayName']
    parameters = payload['queryResult']['parameters']
    output_contexts = payload['queryResult']['outputContexts']
    session_id = session_file.extract_session_id(output_contexts[0]['name'])

    # if intent == "Track.Order-Context:Ongoing-Tracking":
    #     return track_order(parameters)
    # elif intent == "Complete.Order : Context: ongoing-order":
    #     pass
    # elif intent == "Complete.Order : Context: ongoing-order":
    #     pass
    # elif intent == "Complete.Order : Context: ongoing-order":

    intent_handler_dict={
        'Add.Order -Context: Ongoing-order' : add_to_order,
        'Remove.order-context: ongoing-order':remove_from_order,
        'Complete.Order : Context: ongoing-order':complete_order,
        'Track.Order-Context:Ongoing-Tracking': track_order
    }

    return intent_handler_dict[intent](parameters, session_id)


def add_to_order(parameters: dict, session_id: str):
    food_items = parameters["Food-Item"]
    quantity = parameters["number"]
    if len(food_items) != len(quantity):
        fulfillment_text = "Sorry I didn't understand. Can you please specify food items and quantity correctly"
    else:
        food_dict=dict(zip(food_items, quantity))
        if session_id in inprogress_orders:
            current_food_dict=inprogress_orders[session_id]
            current_food_dict.update(food_dict)
        else:
            inprogress_orders[session_id]=food_dict;

        order_str=session_file.get_string_from_food_dict(current_food_dict)
        fulfillment_text = f"So far you have : {order_str}. Do you need anything else ?"

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })
def complete_order(parameters: dict, session_id: str):
    if session_id not in inprogress_orders:
        fulfillment_text="I am having trouble finding your order. Sorry! Can you place a new order?"
    else:
        order = inprogress_orders[session_id]
        order_id = save_to_db(order)

        if (order_id == -1):
            fulfillment_text="Sorry, I couldn't place your order due to a backend error."\
                             "please place a new order again"
        else:
            order_total= db.get_total_order_price(order_id)
            fulfillment_text=f"Awesome. We placed your order."\
            f"Here is your order is #{order_id}."\
            f"Your order total is {order_total} which you can pay at the time of delivery!"
        del inprogress_orders[session_id]

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })


def save_to_db(order: dict):
    next_order_id= db.get_next_order_id()
    for food_item, quantity in order.items():
        rcode= db.insert_order_item(
            food_item,
            quantity,
            next_order_id
        )
        if rcode == -1:
            return -1
    db.insert_order_tracking(next_order_id, "in progress")
    return  next_order_id

def remove_from_order(parameters: dict, session_id: str):
    if session_id not in inprogress_orders:
        return JSONResponse(content={
            "fulfillmentText": "I am having trouble finding your order. Sorry! Can you place a new order?"
        })
    current_order  = inprogress_orders[session_id]
    food_items=parameters["food-item"]
    removed_item=[]
    no_such_items=[]
    for item in food_items:
        if item not in current_order:
            no_such_items.append(item)
        else:
            removed_item.append(item)
            del current_order[item]
    if len(removed_item)>0:
        fulfillment_text= f'Removed {",".join(removed_item)} from your order.'
    if len(no_such_items)>0:
        fulfillment_text = f' Your current order does not have {", ".join(removed_item)}.'
    if len(current_order.keys()) == 0:
        fulfillment_text += "Your order is empty."
    else:
        order_str= session_file.get_string_from_food_dict(current_order)
        fulfillment_text += f"Your order : {order_str}."
    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })


def track_order(parameters: dict, session_id : str):
    order_id = int(parameters['number'])
    order_status= db.get_order_status(order_id)

    if order_status:
        fulfillment_text = f"The order status for order id {order_id} is : {order_status}"
    else:
        fulfillment_text = f"No order found with order id {order_id} "

    return JSONResponse(content={
                "fulfillmentText": fulfillment_text
    })

