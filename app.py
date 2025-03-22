from flask import Flask, request, jsonify, redirect
from flask_pymongo import PyMongo
from datetime import datetime
import random
import string

app = Flask(__name__)

# MongoDB configuration
app.config["MONGO_URI"] = "mongodb://localhost:27017/url_shortener"
mongo = PyMongo(app)

# Generate a unique short code
def generate_short_code():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))

# Endpoint to create a short URL
@app.route('/shorten', methods=['POST'])
def shorten_url():
    data = request.get_json()
    original_url = data.get('original_url')

    if not original_url:
        return jsonify({"error": "Original URL is required"}), 400

    # Generate a unique short code
    short_code = generate_short_code()
    while mongo.db.urls.find_one({"short_code": short_code}):
        short_code = generate_short_code()

    # Create the document
    url_document = {
        "original_url": original_url,
        "short_code": short_code,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "access_count": 0
    }

    # Insert into the 'urls' collection
    result = mongo.db.urls.insert_one(url_document)
    if result.inserted_id:
        return jsonify({
            "message": "Short URL created successfully!",
            "short_code": short_code,
            "original_url": original_url
        }), 201
    else:
        return jsonify({"error": "Failed to create short URL"}), 500
from flask import Flask, request, jsonify, redirect

@app.route('/shorten/<short_code>', methods=['GET'])
def retrieve_url(short_code):
    # Find the document with the given short_code
    url_document = mongo.db.urls.find_one({"short_code": short_code})

    if not url_document:
        return jsonify({"error": "Short URL not found"}), 404

    # Increment the access_count
    mongo.db.urls.update_one(
        {"short_code": short_code},
        {"$inc": {"access_count": 1}}
    )

    # Redirect to the original URL
    return redirect(url_document["original_url"])

@app.route('/shorten/<short_code>', methods=['PUT'])
def update_url(short_code):
    # Get the new data from the request
    data = request.get_json()
    new_original_url = data.get('original_url')

    if not new_original_url:
        return jsonify({"error": "Original URL is required"}), 400

    # Find and update the document with the given short_code
    result = mongo.db.urls.update_one(
        {"short_code": short_code},
        {"$set": {
            "original_url": new_original_url,
            "updated_at": datetime.utcnow()
        }}
    )

    if result.matched_count == 0:
        return jsonify({"error": "Short URL not found"}), 404

    return jsonify({
        "message": "Short URL updated successfully!",
        "short_code": short_code,
        "new_original_url": new_original_url
    }), 200

@app.route('/shorten/<short_code>', methods=['DELETE'])
def delete_url(short_code):
    # Find and delete the document with the given short_code
    result = mongo.db.urls.delete_one({"short_code": short_code})

    if result.deleted_count == 0:
        return jsonify({"error": "Short URL not found"}), 404

    return jsonify({
        "message": "Short URL deleted successfully!",
        "short_code": short_code
    }), 200

@app.route('/')
def home():
    return "MongoDB connection is set up!"

if __name__ == "__main__":
    app.run(debug=True)