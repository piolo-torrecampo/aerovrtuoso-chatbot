from fastapi import FastAPI, HTTPException, Body, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from chains import full_invoke
from dotenv import load_dotenv
import os
import requests
import time

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserPrompt(BaseModel):
    prompt: str

@app.post("/set/prompt")
async def set_response(response_obj: UserPrompt):
    result = full_invoke(response_obj.prompt)
    
    time.sleep(5)

    response = requests.get(os.getenv("API_URL") + "response")
    return response.content

