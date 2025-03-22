from flask import Flask, request, jsonify, redirect, render_template
from flask_pymongo import PyMongo
from datetime import datetime, timezone
import random
import string
import re

app = Flask(__name__)

# MongoDB configuration
app.config["MONGO_URI"] = "mongodb://localhost:27017/url_shortener"
mongo = PyMongo(app)

# Helper function to validate URLs
def is_valid_url(url):
    url_regex = re.compile(
        r'^(https?:\/\/)?'  # http:// or https://
        r'(([a-zA-Z0-9_-]+\.)+[a-zA-Z]{2,})'  # domain
        r'(\/[a-zA-Z0-9._~:/?#[\]@!$&\'()*+,;=-]*)?$'  # path
    )
    return re.match(url_regex, url) is not None

# Generate a unique short code
def generate_short_code():
    while True:
        short_code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        if not mongo.db.urls.find_one({"short_code": short_code}):
            return short_code

# Endpoint to create a short URL
@app.route('/shorten', methods=['POST'])
def shorten_url():
    # Check if the request is from a form submission or an API call
    if request.content_type == 'application/json':
        data = request.get_json()
        original_url = data.get('original_url')
    else:
        original_url = request.form.get('original_url')

    # Validate the original URL
    if not original_url:
        if request.content_type == 'application/json':
            return jsonify({"error": "Original URL is required"}), 400
        return render_template('index.html', error="Original URL is required")

    if not is_valid_url(original_url):
        if request.content_type == 'application/json':
            return jsonify({"error": "Invalid URL format"}), 400
        return render_template('index.html', error="Invalid URL format")

    # Check if the original URL already exists
    existing_url = mongo.db.urls.find_one({"original_url": original_url})
    if existing_url:
        if request.content_type == 'application/json':
            return jsonify({
                "message": "Original URL is already shortened!",
                "short_code": existing_url["short_code"],
                "original_url": original_url
            }), 200
        return render_template('index.html', short_code=existing_url["short_code"])

    # Generate a unique short code
    short_code = generate_short_code()

    # Create the document
    url_document = {
        "original_url": original_url,
        "short_code": short_code,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "access_count": 0
    }

    # Insert into the 'urls' collection
    mongo.db.urls.insert_one(url_document)

    if request.content_type == 'application/json':
        return jsonify({
            "message": "Short URL created successfully!",
            "short_code": short_code,
            "original_url": original_url
        }), 201
    return render_template('index.html', short_code=short_code)

# Endpoint to retrieve the original URL
@app.route('/retrieve', methods=['GET'])
def retrieve_url():
    # Get the short_code from the query parameter
    short_code = request.args.get('short_code')

    if not short_code:
        return render_template('index.html', error="Short code is required")

    # Find the document with the given short_code
    url_document = mongo.db.urls.find_one({"short_code": short_code})

    if not url_document:
        return render_template('index.html', error="Short code not found")

    # Increment the access_count
    mongo.db.urls.update_one(
        {"short_code": short_code},
        {"$inc": {"access_count": 1}}
    )

    # Render the template with the original URL
    return render_template('index.html', retrieved_url=url_document["original_url"], short_code=short_code)

# Endpoint to update the original URL
@app.route('/shorten/<short_code>', methods=['PUT'])
def update_url(short_code):
    data = request.get_json()
    new_original_url = data.get('original_url')

    if not new_original_url:
        return jsonify({"error": "Original URL is required"}), 400

    if not is_valid_url(new_original_url):
        return jsonify({"error": "Invalid URL format"}), 400

    result = mongo.db.urls.update_one(
        {"short_code": short_code},
        {"$set": {
            "original_url": new_original_url,
            "updated_at": datetime.now(timezone.utc)
        }}
    )

    if result.matched_count == 0:
        return jsonify({"error": "Short URL not found"}), 404

    return jsonify({
        "message": "Short URL updated successfully!",
        "short_code": short_code,
        "new_original_url": new_original_url
    }), 200

# Endpoint to delete a short URL
@app.route('/shorten/<short_code>', methods=['DELETE'])
def delete_url(short_code):
    result = mongo.db.urls.delete_one({"short_code": short_code})

    if result.deleted_count == 0:
        return jsonify({"error": "Short URL not found"}), 404

    return jsonify({
        "message": "Short URL deleted successfully!",
        "short_code": short_code
    }), 200

# Endpoint to get URL statistics
@app.route('/shorten/<short_code>/stats', methods=['GET'])
def get_url_stats(short_code):
    url_document = mongo.db.urls.find_one({"short_code": short_code})

    if not url_document:
        return jsonify({"error": "Short URL not found"}), 404

    return jsonify({
        "short_code": short_code,
        "original_url": url_document["original_url"],
        "created_at": url_document["created_at"],
        "updated_at": url_document["updated_at"],
        "access_count": url_document["access_count"]
    }), 200

@app.route('/shorten/<short_code>', methods=['GET'])
def redirect_to_original(short_code):
    # Find the document with the given short_code
    url_document = mongo.db.urls.find_one({"short_code": short_code})

    if not url_document:
        # Return a 404 error if the short_code is not found
        return jsonify({"error": "Short code not found"}), 404

    # Increment the access_count
    mongo.db.urls.update_one(
        {"short_code": short_code},
        {"$inc": {"access_count": 1}}
    )

    # Redirect to the original URL
    return redirect(url_document["original_url"])

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)