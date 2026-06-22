from flask import Flask

app = Flask(__name__)

@app.route('/')

def home():

    return "AI Driver Dashboard Running"

app.run(debug=True)