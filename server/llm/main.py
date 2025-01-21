from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_huggingface.llms import HuggingFacePipeline
from peft import PeftModel
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline, GenerationConfig
import json
import requests
import os
from dotenv import load_dotenv
import time

# load .env 
load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Load the base model
base_model_name = "TinyLlama/TinyLlama-1.1B-intermediate-step-240k-503b"  # Replace with your base model name
tokenizer = AutoTokenizer.from_pretrained(base_model_name)  

print("Loading base model...")
base_model = AutoModelForCausalLM.from_pretrained(base_model_name)
print("Base model loaded.")

# Create a Hugging Face pipeline
hf_pipeline = pipeline(
    "text-generation",
    model=base_model,
    tokenizer=tokenizer,
    generation_config = GenerationConfig(
        penalty_alpha=0.6,
        do_sample=True,
        top_k=3,
        temperature=0.5,
        repetition_penalty=1.2,
        max_new_tokens=64,
        pad_token_id=tokenizer.eos_token_id
    )
)

# Load the PEFT fine-tuned model
peft_model_name = "/llm/app/model/tinyllama-instruct-tuned/checkpoint-60080/"

print("Loading PEFT model...")
pipeline.model = PeftModel.from_pretrained(base_model, peft_model_name)
print("PEFT model loaded.")

# Wrap the pipeline in LangChain's HuggingFacePipeline
print("Wrapping in HuggingFacePipeline...")
formatter = HuggingFacePipeline(pipeline=hf_pipeline)

print("LLM Initiated")
status_response = requests.post(os.getenv("API_URL") + '/set/llm_status', json={"status": True})
print(status_response.json())

## router
router =  PromptTemplate.from_template(
    """Instruction:
Classify the given sentence into either spawn, move, replace, rotate, or delete. 
Here are the keywords for each classification
spawn - spawn, insert, add, put, place, or any synonyms to these words.
move - move, push, displace, offset, or any synonyms to these words.
replace - replace, substitute, or any other synonyms to these words.
rotate - rotate, tilt, turn, or any synonyms to these words
delete - remove, delete, banish or any other synonyms
Return only one word, the classification.

Input:
{instruction}

Response:
"""
) | formatter | StrOutputParser()


## spawn chain
spawn_chain = PromptTemplate.from_template(
    """Instruction:
Format the given sentence and assign them to the proper parameter:
here are the parameters and their description: 
    prefab - the object to be inserted/placed/spawned
    reference_object - the object of reference, if there is no reference_object set the value to "default"
    direction - the direction of the placement of inserted object and it should be be only be either top, left, right, bottom, front, back, if there is no direction set the value to "default"
    value - the displacement from the reference object, if there is no value set the value to 1No need to explain just get the output which should be in a valid json format like this example, use underscore and numbers on the names if there is any given.
example sentence
Spawn a turbine_blade next to the engine_stand.
example output
{{
    "prefab": "turbine_blade",
    "reference_object": "engine_stand",
    "direction": "right",
    "value": "1"
}}

Input:
{instruction}

Response:
"""
) | formatter

## move chain
move_chain = PromptTemplate.from_template(
    """Instruction:
Format the given sentence and assign them to the proper parameter:
here are the parameters and their description:
    prefab - the object to be moved
    direction - in which direction the object should move either top, left, right, bottom, front, back
    value - how many units to be moved
No need to explain just get the output which should be in a valid json format like this example, use underscore and numbers on the names if there is any given.
example sentence
Move the workbench to the right.
example output
{{
    "prefab": "workbench",
    "direction": "right", 
    "value": "1"
}}

Input:
{instruction}

Response:
"""
) | formatter

## replace chain
replace_chain = PromptTemplate.from_template(
    """Instruction:
Format the given sentence and assign them to the proper parameter:
here are the parameters and their description:
    prefab - the object to be placed
    object_to_replace - the object in the scene to be replaced
No need to explain just get the output which should be in a valid json format like this example, use underscore and numbers on the names if there is any given.
example sentence
Replace the workbench with wrench
example output
{{
    "prefab": "wrench",
    "object_to_replace": "workbench"
}}

Input:
{instruction}

Response:
"""
) | formatter

## rotate chain
rotate_chain = PromptTemplate.from_template(
    """Instruction:
Format them and sign them to the proper parameter:
here are the parameters and their description:
    prefab - the object to be rotated
    axis - in which axis the object should rotate either x, y, z or reset (to reset all axis)
    value - how much degrees to rotate
No need to explain just get the output which should be in a valid json format like this example, use underscore and numbers on the names if there is any given.
example sentence
Rotate the screwdriver 45 degrees in x axis.
example output
{{
    "prefab": "screwdriver",
    "axis": "x",
    "value": "45"
}}

Input:
{instruction}

Response:
"""
) | formatter

## remove chain
remove_chain = PromptTemplate.from_template(
    """Instruction:
Format them and sign them to the proper parameter:
here are the parameters and their description: 
    prefab - the object to be deleted
No need to explain just get the output which should be in a valid json format like this example, use underscore and numbers on the names if there is any given.
Remove screwdriver in the scene.
example output
{{
    "prefab": "screwdriver"
}}

Input:
{instruction}

Response:
"""
) | formatter 

## routing function
def route(prompt):
    # url setup
    url = os.getenv("API_URL")
    
    print('Classifying route...')
    classification_result = router.invoke(prompt)
    print('Route detected')

    if "Response:" in classification_result:
        result = classification_result.split("Response:")[1].strip()
        action = result.split(' ')[0].lower()

        print('Action: ' + action)

        print('Generating JSON...')

        if action == "spawn":
            output = spawn_chain.invoke(prompt)
        elif action == "move":
            output = move_chain.invoke(prompt)
        elif action == "replace":
            output = replace_chain.invoke(prompt)
        elif action == "rotate":
            output = rotate_chain.invoke(prompt)
        elif action == "remove":
            output = remove_chain.invoke(prompt)
        else:
            output = "Error: Could not classify the instruction."

        print('JSON Generated')
        
        if "Response:" in output:
            if_parsed, payload = get_json(output)
            if if_parsed:
                route = f"set/{payload['action']}"
                print(f"Route: {url}{route}")
                response = requests.post(url+route, json=payload.get("parameters"))
                return f"Type: Spawn\nResponse Code: {response.status_code}\nPayload:{payload}"

def get_json(output):
    try: 
        # extract data
        result = output.split("Response:")[1].strip()
        converted = json.loads(result.splitlines()[0])

        # print json
        pretty_json = json.dumps(converted, indent=4)
        print("JSON Output: ")
        print(pretty_json)

        return True, converted
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return False
        
def full_invoke(prompt):
    print('LLM Started')
    start_time = time.time()
    response = route(prompt)
    print(f"LLM Duration: {time.time() - start_time}")
    
def check_keyword(prompt):
    splitted_prompt = prompt.lower().split(' ')
    
    keyword_categories = {
        "spawn": ["spawn", "insert", "add", "put", "place"],
        "move": ["move", "push", "displace", "offset"],
        "replace": ["replace", "substitute"],
        "rotate": ["rotate", "tilt", "turn"],
        "remove": ["remove", "delete", "banish"]
    }
    
    for word in splitted_prompt:
        word_lower = word.lower()
        for category, keywords in keyword_categories.items():
            if word_lower in keywords:
                return True, category
    
    return False, None 

def check_available(object): 
    try:
        # Make a GET request to fetch the current prefabs
        response = requests.get(os.getenv("API_URL") + "response")
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        
        # Parse the response JSON and get the current objects
        response_json = response.json()  # Ensure the response is in JSON format
        objects = response_json["response"]["available_prefabs"].split(", ")

        print(objects)

        return object in objects
    except Exception as e:
        print(f"Error in check_prefab: {e}")
        return False

def check_prefab(object): 
    try:
        # Make a GET request to fetch the current prefabs
        response = requests.get(os.getenv("API_URL") + "response")
        print(response)

        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        
        # Parse the response JSON and get the current objects
        response_json = response.json()  # Ensure the response is in JSON format
        objects = response_json["response"]["current_objects"].split(", ")

        print(objects)

        return object in objects
    except Exception as e:
        print(f"Error in check_prefab: {e}")
        return False
    
def check_direction(splitted_prompt):
    directions = ["left", "right", "front", "back", "top", "bottom"]
    return any(word in directions for word in splitted_prompt)

def check_axis(splitted_prompt):
    axes = ['x', 'y', 'z']
    return any(word in axes for word in splitted_prompt)

def check_value(splitted_prompt):
    pass

# endpoint
class UserPrompt(BaseModel):
    prompt: str

def generate_response(status, result, prompt): 
    if(status): 
        result = full_invoke(prompt)
            
        time.sleep(5)

        response = requests.get(os.getenv("API_URL") + "response")
        return response.content
    else:
        return result

def format_missing_items(items):
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    return ', '.join(items[:-1]) + f", and {items[-1]}"

@app.post("/set/prompt")
async def set_response(response_obj: UserPrompt):
    prompt = response_obj.prompt
    category_status, category = check_keyword(prompt)

    data = {"response": {"message": ""}}
    missing_items = []

    def format_response(action, missing_items):
        items_str = format_missing_items(missing_items)
        data["response"]["message"] += f"{action} Action: Please specify {items_str} or add one."

    if category_status:
        splitted_prompt = prompt.lower().split(' ')

        # Define checks for each category
        if category == "spawn":
            prefab_status = check_available(splitted_prompt[1])
            reference_prefab_status = check_prefab(splitted_prompt[-1])
            direction_status = check_direction(splitted_prompt)

            if not prefab_status:
                missing_items.append("new prefab")
            if not reference_prefab_status:
                missing_items.append("new reference prefab")
            if not direction_status:
                missing_items.append("direction")

            if missing_items:
                format_response("Spawn", missing_items)
                return generate_response(False, data, prompt)
            else:
                return generate_response(True, {"message": "Spawn action successful."}, prompt)

        elif category == "move":
            prefab = check_prefab(splitted_prompt[1])
            direction_status = check_direction(splitted_prompt)

            if not prefab:
                missing_items.append("new prefab")
            if not direction_status:
                missing_items.append("direction")

            if missing_items:
                format_response("Move", missing_items)
                return generate_response(False, data, prompt)
            else:
                return generate_response(True, {"message": "Move action successful."}, prompt)

        elif category == "replace":
            replace_prefab = check_prefab(splitted_prompt[1])
            prefab = check_available(splitted_prompt[-1])

            if not prefab:
                missing_items.append("new prefab")
            if not replace_prefab:
                missing_items.append("new replacement prefab")

            if missing_items:
                format_response("Replace", missing_items)
                return generate_response(False, data, prompt)
            else:
                return generate_response(True, {"message": "Replace action successful."}, prompt)

        elif category == "rotate":
            prefab = check_prefab(splitted_prompt[1])
            check_axis_status = check_axis(splitted_prompt)

            if not prefab:
                missing_items.append("new prefab")
            if not check_axis_status:
                missing_items.append("valid axis")

            if missing_items:
                format_response("Rotate", missing_items)
                return generate_response(False, data, prompt)
            else:
                return generate_response(True, {"message": "Rotate action successful."}, prompt)

        elif category == "remove":
            prefab = check_prefab(splitted_prompt[1])

            if not prefab:
                missing_items.append("new prefab")

            if missing_items:
                format_response("Remove", missing_items)
                return generate_response(False, data, prompt)
            else:
                return generate_response(True, {"message": "Remove action successful."}, prompt)

    else:
        data["response"]["message"] = "Invalid action. Please specify a valid action."
        return generate_response(False, data, prompt)
