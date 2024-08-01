from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
import json
import requests
import os
from dotenv import load_dotenv

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

## formatter
formatter = ChatOpenAI(
    model="gpt-3.5-turbo-1106",
    temperature=0.3,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    #response_format={ "type": "json_object" },
)

## router
router =  PromptTemplate.from_template(
    """Classify this sentence into either spawn, move, replace, rotate, or delete. 
Here are the keywords for each classification
spawn - spawn, insert, add, put, place, or any synomyns to these words.
move - move, push, displace, offset, or any synomyns to these words.
replace - replace, substitute, or any other synomyns to these words.
rotate - rotate, tilt, turn, or any synonyms to these words
delete - remove, delete, despawn, or any other synonym\
Here is the sentence
{instruction}
Return only one word, the classification.
"""
) | formatter | StrOutputParser()


## spawn chain
spawn_chain = PromptTemplate.from_template(
    """Format them and sign them to the proper parameter:
here are the parameters and their description: 
    prefab - the object to be placed/spawned
    reference_object - the object of reference, it is ok if there is no reference object
    direction - the direction of the placement of inserted object and it should be be only be either top, left, right, bottom, front, back
    value - the displacement from the reference object \
here is the sentence
{instruction} \
No need to explain just get the output which should be in a valid json format like this example, use underscore on the names, include @ sign and a uuid if there is any given.
example sentence
Spawn a turbine blade next to the engine stand.
example output
{{
    "prefab": "turbine_blade",
    "reference_object": "engine_stand",
    "direction": "right",
    "value": "1"
}}
"""
) | formatter

## move chain
move_chain = PromptTemplate.from_template(
    """Format them and sign them to the proper parameter:
here are the parameters and their description:
    prefab - the object to be deleted
    direction - in which direction the object should rotate either top, left, right, bottom, front, back
    value - how many units to be moved
here is the sentence:
{instruction} \
No need to explain just get the output which should be in a valid json format like this example, use underscore on the names, include @ sign and a uuid if there is any given.
example sentence
Move the workbench to the right.
example output
{{
    "prefab": "workbench",
    "direction": "right", 
    "value": "1"
}}
"""
) | formatter

## replace chain
replace_chain = PromptTemplate.from_template(
    """Format them and sign them to the proper parameter:
here are the parameters and their description:
    prefab - the object to be placed
    object_to_replace - the object in the scene to be replaced
here is the sentence \
{instruction} \
No need to explain just get the output which should be in a valid json format like this example, use underscore on the names, include @ sign and a uuid if there is any given.
example sentence
Replace the workbench with wrench
example output
{{
    "prefab": "workbench",
    "object_to_replace": "wrench"
}}
"""
) | formatter

## rotate chain
rotate_chain = PromptTemplate.from_template(
    """Format them and sign them to the proper parameter:
here are the parameters and their description:
    prefab - the object to be deleted
    axis - in which axis the object should rotate either x, y, z or reset (to reset all axis)
    value - how much degrees to rotate \
here is the sentence
{instruction} \
No need to explain just get the output which should be in a valid json format like this example, use underscore on the names, include @ sign and a uuid if there is any given.
example sentence
Remove screwdriver in the scene.
example output
{{
    "prefab": "screwdriver",
    "axis": "x",
    "value": "45"
}}
"""
) | formatter

## remove chain
remove_chain = PromptTemplate.from_template(
    """Format them and sign them to the proper parameter:
here are the parameters and their description: 
    prefab - the object to be deleted
    value - the number of object to be removed \
here is the sentence
{instruction} \
No need to explain just get the output which should be in a valid json format like this example, use underscore on the names, include @ sign and a uuid if there is any given.
example sentence
Remove screwdriver in the scene.
example output
{{
    "prefab": "screwdriver",
    "value": "1"
}}
"""
) | formatter 

## routing function
def route(info):
    # url setup
    url = os.getenv("API_URL")
    # routes
    if "spawn" in info["topic"].lower():
        # Invoke
        output = spawn_chain.invoke(info).content
        # Spawn API Call
        payload = json.loads(output)
        response = requests.post(url+"set/spawn", json=payload)
        # Logging
        print("spawn")
        print(response.status_code)
        print(response.json()) 
        # Return
        return f"Type: Spawn\nResponse Code: {response.status_code}\nPayload:{payload}"
    elif "move" in info["topic"].lower():
        # Invoke 
        output = move_chain.invoke(info).content
        # Move API Call
        payload = json.loads(output)
        response = requests.post(url+"set/move", json=payload)
        # Logging
        print("move")
        print(response.status_code)
        print(response.json()) 
        # Return
        return f"Type: Move\nResponse Code: {response.status_code}\nPayload:{payload}"
    elif "replace" in info["topic"].lower():
        # Invoke 
        output = replace_chain.invoke(info).content
        # Replace API Call
        payload = json.loads(output)
        response = requests.post(url+"set/replace", json=payload)
        # Logging
        print("invoke")
        print(response.status_code)
        print(response.json()) 
        # Return
        return f"Type: Replace\nResponse Code: {response.status_code}\nPayload:{payload}"
    elif "rotate" in info["topic"].lower():
        # Invoke 
        output = rotate_chain.invoke(info).content
        # Rotate API Call
        payload = json.loads(output)
        response = requests.post(url+"set/rotate", json=payload)
        # Logging
        print("rotate")
        print(response.status_code)
        print(response.json()) 
        # Return
        return f"Type: Rotate\nResponse Code: {response.status_code}\nPayload:{payload}"
    elif "delete" in info["topic"].lower():
        # Invoke 
        output = remove_chain.invoke(info).content
        # Remove API Call
        print("remove")
        payload = json.loads(output)
        response = requests.post(url+"set/remove", json=payload)
        # Logging
        print(response.status_code)
        print(response.json()) 
        # Return
        return f"Type: Delete\nResponse Code: {response.status_code}\nPayload:{payload}"
    else:
        output = "No matching command"
        print(output)
        return output
    
def full_invoke(prompt):
    full_chain = {"topic": router, "instruction": lambda x: x["instruction"]} | RunnableLambda(route)
    return full_chain.invoke({"instruction": prompt})