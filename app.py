from flask import Flask
from flask_pymongo import PyMongo

app = Flask(__name__)

# MongoDB configuration
app.config["MONGO_URI"] = "mongodb://localhost:27017/url_shortener"
mongo = PyMongo(app)

@app.route('/')
def home():
    return "MongoDB connection is set up!"

if __name__ == "__main__":
    app.run(debug=True)