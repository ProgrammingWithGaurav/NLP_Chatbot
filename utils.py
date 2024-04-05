import re

# Extract Session I
def extract_session_id(session_str : str):
    # extracting any string between '/sessions/' and '/contexts/'
    match = re.search('/sessions/(.*?)/contexts/', session_str) 
    if match:
        return match.group(1)
    else:
        return ""

def get_str_from_food_dict(food_dict: dict):
    # convert the dictionary to a string
    # e.g. {'pizza': 1, 'burger': 2} -> 'pizza x1, burger x2'
    return ', '.join([f'{key} x{value}' for key, value in food_dict.items()])   
