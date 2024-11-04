# this file now refer to the folder template 2 that has the home.html that
#  include java script to work withh websocket, and layout file located in templates2 folder
#  that now has all the css to make the webpage look beautifull

import openai
from fastapi import FastAPI, Form,Request,WebSocket
from typing import Annotated
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import os
from dotenv import load_dotenv



# Load .env file from specific path that contain the OpenAIKey
env_path = r"C:\Users\anton\OneDrive\Desktop\Corsi\Chat Bot\fastapi\fastapienv\.env"
load_dotenv(env_path)

# Set API key contained in the .env file
openai.api_key = os.getenv("OPENAI_API_SECRET_KEY")

# Optional: Add validation if you want to catch configuration errors early
if not openai.api_key:
    raise ValueError("No API key found in environment variables!")

app=FastAPI()
# templates=Jinja2Templates(directory=r"C:\Users\anton\OneDrive\Desktop\Corsi\Chat Bot\fastapi\fastapienv\templates")#use this option when running locally
templates = Jinja2Templates(directory="templates")
chat_responses=[] 



# @app.get("/", response_class=HTMLResponse)
# async def chat_page(request:Request):
#     return templates.TemplateResponse("home.html", {"request":request,"chat_responses":chat_responses})# this keep the hystory even if you open another browser

@app.get("/", response_class=HTMLResponse)
async def chat_page(request: Request):
    global chat_responses
    chat_responses = []  # Use this if you want to Clear chat history                   
    return templates.TemplateResponse("home.html", {"request": request, "chat_responses": chat_responses})



chat_log=[{'role': 'system', 'content': 'You tell a joke, do not be repetitive'}]


@app.websocket("/ws")
async def chat(websocket: WebSocket):

    await websocket.accept()
    while True:
        try:
            user_input = await websocket.receive_text()
            chat_log.append({'role':'user','content':user_input})
            chat_responses.append(user_input)

            response= openai.chat.completions.create(
                model='gpt-3.5-turbo',
                messages=chat_log,
                temperature=0.6,
                stream=True
                )

            ai_response= ''

            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    ai_response= ai_response+ chunk.choices[0].delta.content
                    await websocket.send_text(chunk.choices[0].delta.content)
            chat_responses.append(ai_response)

        except Exception as e:
            await websocket.send_text(f'Error: {str(e)}')
            break


# ------------------- HTTP POST Endpoint Explanation Below -------------------
# @app.post("/") is an alternative route that handles form submissions via HTTP requests.
# This method is useful as a fallback option for clients that don't support WebSockets 
# (for example, older browsers or specific network conditions where WebSockets are blocked).
# 
# We are keeping this route to ensure backward compatibility or if real-time streaming
# is not strictly required, allowing for a basic request-response model. If WebSockets
# fail, the client can still communicate with the server using this traditional method.
#
# Even though WebSockets offer real-time communication, this POST method remains useful for:
# 1. Handling non-real-time communication.
# 2. Ensuring compatibility with clients that have limited WebSocket support.
# 3. Providing a fallback mechanism to maintain application robustness.
# -----------------------------------------------------------------------------

@app.post("/",response_class=HTMLResponse)
async def chat(request:Request, user_input: Annotated[str, Form()]):

    chat_log.append({'role':'user' , 'content':user_input})
    chat_responses.append(user_input)

    response= openai.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=chat_log,
        temperature=1)


    bot_response= response.choices[0].message.content
    chat_log.append({'role':'assistant', 'content':'bot_response'})
    chat_responses.append(bot_response)

    return templates.TemplateResponse("home.html", {"request": request, "chat_responses": chat_responses})


################################################### image generator ##############################################

@app.get("/image",response_class=HTMLResponse)
async def image_page(request: Request):
    return templates.TemplateResponse("image.html", {"request":request})


@app.post("/image", response_class=HTMLResponse)
async def create_image(request: Request, user_input: Annotated[str, Form()]):

    response= openai.images.generate(
        prompt=user_input,
        n=1,
        size="256x256"
    )

    image_url=response.data[0].url
    return templates.TemplateResponse("image.html",{"request": request, "image_url":image_url})





# After running the code you can run in the terminal the usual (if running locally) :
# uvicorn chatbot+image_gen_websocket_secr_key7:app --reload


#---------------------------------------------------------------------------------------------------------------------#
# I have created a txt file (Requirements) to contain all of the dependencied with the version of them (pip show openai for example to get the version that we are using),
# Those are needed for the server to download the dependencies to make the app run on line
# the .txt file will need the following dependencies updated with their version:
#aiofiles
#fastapi
#Jinja2
#openai
#python-dotenv
#python_multipart
#uvicorn
#websocket




#---------------------------------------------------------------------------------------------------------------------#
