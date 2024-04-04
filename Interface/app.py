from flask import Flask, render_template, request
# import model
# import dbms connector

"""
Flask app to serve the user interface
Consists of basic options for user to 
interact with the LLM SQL model.
"""

app = Flask(__name__)

# consists of dictionaries of form {user, bot, result}
chat_history = []

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        
        chat_entry = {'user': "", 'bot': "", 'result': ""}

        # get data from form
        nl_query = request.form['nl_query']
        chat_entry['user'] = nl_query
        
        # get response from model
        prompt = f"translate SQL to English: {nl_query}"
        sql = f"convert_to_sql('{prompt}')"
        chat_entry['bot'] = sql

        # get result from dbms, if needed
        result = "\n"
        chat_entry['result'] = result

        # add entry to chat history
        chat_history.append(chat_entry)

        if len(chat_history) > 5:
            chat_history.pop(0)

        # pass results to template
        return render_template('home.html', chat_history=chat_history)
    
    else:
        return render_template('home.html', chat_history=chat_history)

if __name__ == '__main__':
    app.run(debug=True)