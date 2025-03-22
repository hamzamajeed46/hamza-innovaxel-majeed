from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from datetime import datetime

app = Flask(__name__)

# MongoDB configuration
app.config["MONGO_URI"] = "mongodb://localhost:27017/url_shortener"
mongo = PyMongo(app)

# Define the 'urls' collection schema
@app.route('/initialize', methods=['POST'])
def initialize_collection():
    # Example document structure
    example_document = {
        "original_url": "https://facebook.com",
        "short_code": "abc123",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "access_count": 0
    }
    # Insert the example document into the 'urls' collection
    result = mongo.db.urls.insert_one(example_document)
    if result.inserted_id:
        return jsonify({"message": "Document inserted successfully!", "id": str(result.inserted_id)}), 201
    else:
        return jsonify({"message": "Failed to insert document!"}), 500

@app.route('/')
def home():
    return "MongoDB connection is set up!"

if __name__ == "__main__":
    app.run(debug=True)