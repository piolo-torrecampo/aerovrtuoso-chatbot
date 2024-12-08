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
    keywords = [
     "spawn", 
     "insert", 
     "add", 
     "put", 
     "place", 
     "move", 
     "push", 
     "displace", 
     "offset", 
     "replace", 
     "substitute", 
     "rotate", 
     "tilt", 
     "turn", 
     "remove", 
     "delete", 
     "banish"
    ]

    if any(word in prompt.lower() for word in keywords):
        return True
    else:
        return False

# endpoint
class UserPrompt(BaseModel):
    prompt: str

@app.post("/set/prompt")
async def set_response(response_obj: UserPrompt):
    if(check_keyword(response_obj.prompt)):
        result = full_invoke(response_obj.prompt)
        
        time.sleep(5)

        response = requests.get(os.getenv("API_URL") + "response")
        return response.content
    else:
        data = {
            "response": {
                "message": "Invalid action. Please specify an action."
            }  
        }

        return data