Directory structure
===================
backend: Contains Python FastAPI backend code
db: contains the dump of the database. you need to import this into your MySQL db by using MySQL workbench tool
dialogflow_assets: this has training phrases etc. for our intents
frontend: website code

Install these modules
======================
pip install mysql
pip install mysql-connector
pip install "fastapi[all]"

OR just run pip install -r backend/requirements.txt to install both in one shot

To start fastapi backend server
================================
pip install uvicorn
1. Go to backend directory in your command prompt
2. Run this command: uvicorn main:app --reload

while connecting db provide your own password and sq workbench user name.

ngrok for https tunneling
================================
1. To install ngrok, go to https://ngrok.com/download and install ngrok version that is suitable for your OS
2. Extract the zip file and place ngrok.exe in your project folder.
3. Open windows command prompt, go to that folder and run this command: ngrok http 80000

NOTE: ngrok can timeout. you need to restart the session if you see session expired message.you will have to copy and paste the new generated ngrok link in fulfillments url of bot in dialogflow.
