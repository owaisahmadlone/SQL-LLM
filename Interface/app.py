from flask import Flask, render_template, redirect, request, url_for
import psycopg2
import requests
from dotenv import dotenv_values
import pandas as pd
from tabulate import tabulate

"""
Access the environment variables for the database
connection details. This is done to avoid hardcoding
the credentials in the code.
"""

# Load environment variables from .env file
env_vars = dotenv_values('../.env')

# Access sensitive information
API_TOKEN = env_vars.get("API_TOKEN")
USER = env_vars.get("DB_USER")
PASSWORD = env_vars.get("DB_PASSWORD")
HOST = env_vars.get("HOST_IP")

# Check if the environment variables are available
if None in (API_TOKEN, USER, PASSWORD, HOST):
    print("Error: One or more environment variables are not set.")
    exit(1)

"""
Use the Hugging Face API to access the LLM model
to convert natural language to SQL queries.
"""

API_URL = "https://api-inference.huggingface.co/models/barunparua/flant5-nltosql-final-model"
headers = {"Authorization": f"Bearer {API_TOKEN}"}

def query(payload):
	response = requests.post(API_URL, headers=headers, json=payload)
	return response.json()

"""
Database selection flags
"""
isDBselected = False
db_id = -1
schema = ""
conn = None

# Preset schemas for the database

preset_schemas = [
    {
        "id": 0,
        "db_name": "21CS10014",
        "name": "Fest Management System",
        "schema": "ADMIN: USERNAME (PRIMARY KEY) (text); PASS (text)//STUDENT: FEST_ID (PRIMARY KEY) (numeric); NAME (text); ROLL (text); DEPT (text); PASS (text)//EVENT: EVENT_ID (PRIMARY KEY) (numeric); EVENT_NAME (text); EVENT_DATE (date); EVENT_TIME (time); EVENT_VENUE (text); EVENT_TYPE (text); EVENT_DESCRIPTION (text); EVENT_WINNER (numeric)//ACCOMODATION: ACC_ID (numeric) (PRIMARY KEY); NAME (text); CAPACITY (numeric)//EXT_PARTICIPANT: FEST_ID (numeric) (PRIMARY KEY); NAME (text); COLLEGE (text); ACC_ID (numeric); PASS (text)//ORGANISING: FEST_ID (numeric); EVENT_ID (numeric); PRIMARY KEY (FEST_ID, EVENT_ID)//VOLUNTEERING: FEST_ID (numeric); EVENT_ID (numeric); PRIMARY KEY (FEST_ID, EVENT_ID)//PARTICIPATING_EXT: FEST_ID (numeric); EVENT_ID (numeric); PRIMARY KEY (FEST_ID, EVENT_ID)//PARTICIPATING_INT: FEST_ID (numeric); EVENT_ID (numeric); PRIMARY KEY (FEST_ID, EVENT_ID)",
        "df" : [
    {'Table': 'ADMIN', 'Attributes': ['USERNAME (PRIMARY KEY) (text)', 'PASS (text)']},
    {'Table': 'STUDENT', 'Attributes': ['FEST_ID (PRIMARY KEY) (numeric)', 'NAME (text)', 'ROLL (text)', 'DEPT (text)', 'PASS (text)']},
    {'Table': 'EVENT', 'Attributes': ['EVENT_ID (PRIMARY KEY) (numeric)', 'EVENT_NAME (text)', 'EVENT_DATE (date)', 'EVENT_TIME (time)', 'EVENT_VENUE (text)', 'EVENT_TYPE (text)', 'EVENT_DESCRIPTION (text)', 'EVENT_WINNER (numeric)']},
    {'Table': 'ACCOMODATION', 'Attributes': ['ACC_ID (numeric) (PRIMARY KEY)', 'NAME (text)', 'CAPACITY (numeric)']},
    {'Table': 'EXT_PARTICIPANT', 'Attributes': ['FEST_ID (numeric) (PRIMARY KEY)', 'NAME (text)', 'COLLEGE (text)', 'ACC_ID (numeric)', 'PASS (text)']},
    {'Table': 'ORGANISING', 'Attributes': ['FEST_ID (numeric)', 'EVENT_ID (numeric)', 'PRIMARY KEY (FEST_ID, EVENT_ID)']},
    {'Table': 'VOLUNTEERING', 'Attributes': ['FEST_ID (numeric)', 'EVENT_ID (numeric)', 'PRIMARY KEY (FEST_ID, EVENT_ID)']},
    {'Table': 'PARTICIPATING_EXT', 'Attributes': ['FEST_ID (numeric)', 'EVENT_ID (numeric)', 'PRIMARY KEY (FEST_ID, EVENT_ID)']},
    {'Table': 'PARTICIPATING_INT', 'Attributes': ['FEST_ID (numeric)', 'EVENT_ID (numeric)', 'PRIMARY KEY (FEST_ID, EVENT_ID)']}
]
    },
]

"""
psycopg2 is a PostgreSQL adapter for Python.
It is used to connect to the database and 
execute SQL queries.
"""

def connect_to_db(id):
    global isDBselected, schema, conn, preset_schemas
    try:
        conn = psycopg2.connect(
            dbname=preset_schemas[id]["db_name"],
            user=USER,
            password=PASSWORD,
            host=HOST
        )
        isDBselected = True
        schema = preset_schemas[id]["schema"]

        print("Connected to the database. Schema selected.")
        print(f"Database: {preset_schemas[id]['db_name']}")
        print(f"Name: {preset_schemas[id]['name']}")
        print(f"Schema: {schema[:50]}...")

    except Exception as e:
        print(f"Error: Unable to connect to the database. {e}")
        return None

def close_connection():
    global isDBselected, schema, conn
    try:
        conn.close()
        isDBselected = False
        schema = ""
        print("Connection to the database closed. Schema deselected.")
    except Exception as e:
        print(f"Error: Unable to close the connection. {e}")

"""
Flask app to serve the user interface
Consists of basic options for user to 
interact with the LLM SQL model.
"""

app = Flask(__name__)
app.secret_key = 'my_secret_key'  # Change this to a secure secret key

# consists of dictionaries of form {user, bot, result}
chat_history = []
schema_struct = None

@app.route('/', methods=['GET', 'POST'])
def home():
    global chat_history, schema_struct

    if request.method == 'POST':
        
        chat_entry = {'user': "", 'bot': "", 'result': ""}

        # get data from form
        nl_query = request.form['nl_query']
        chat_entry['user'] = nl_query
        
        # get response from model
        prompt = f"{schema} {nl_query}"
        output = query({"inputs": prompt, "parameters": {"max_new_tokens": 200},"options": {"wait_for_model": True}})
        try:
            sql = output[0]['generated_text']
        except Exception as e:
            sql = f"Error: Unable to generate SQL query. {e}\n\nResponse: {output}"
        chat_entry['bot'] = sql

        # get result from dbms, if db is selected
        result = "<p></p>"
        if isDBselected:
            try:
                df = pd.read_sql_query(sql, conn)
                result = tabulate(df, headers='keys', tablefmt='html')
            except Exception as e:
                result = f"<p>Error: Unable to execute the query in database. {e}</p>"
    
        chat_entry['result'] = result

        # add entry to chat history
        chat_history.append(chat_entry)

        if len(chat_history) > 1:
            chat_history.pop(0)

        # pass results to template

        return redirect(url_for('home', chat_history=chat_history, databases=[{"id":db["id"], "name":db["name"]} for db in preset_schemas], db_id=db_id, schema = schema_struct))
    
    else:
        return render_template('home.html', chat_history=chat_history, databases=[{"id":db["id"], "name":db["name"]} for db in preset_schemas], db_id=db_id, schema = schema_struct)

@app.route('/update_db_id', methods=['POST'])
def update_db_id():
    global db_id
    data = request.json
    new_db_id = int(data['id'])
    # Update the global db_id variable
    db_id = new_db_id

    # Connect to the database
    if db_id != -1:
        connect_to_db(db_id)
        x =  pd.DataFrame(preset_schemas[db_id]["df"])
        schema_struct = tabulate(x, headers='keys', tablefmt='html')
    else:
        close_connection()
        schema_struct = "<p>No schema set.</p>"

    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)