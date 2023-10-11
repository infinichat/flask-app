import mysql.connector
import requests

# Define your API URL
API_URL = "https://flowiseai-railway-production-a82a.up.railway.app/api/v1/prediction/cd1fec15-b4e2-48e4-ae5d-9caeddeaf314"


# Define your MySQL database connection settings
DB_CONFIG = {
    'host': 'containers-us-west-102.railway.app',
    'user': 'root',
    'password': 'Og4XTe1e7qCLfNXPa9uQ',
    'database': 'railway',
}

# Function to query the API and return the response
def query_api(payload):
    try:
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes
        print("API Response:", response.text)  # Print the API response
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API Request Error: {e}")
        return None


# Function to query the database and return the answer
def query_database(question, regex=False):
    try:
        with mysql.connector.connect(**DB_CONFIG) as connection:
            cursor = connection.cursor()
            if regex:
                # Use regular expression to search for matching questions
                cursor.execute("SELECT question, answer FROM qa WHERE question REGEXP %s", (question,))
            else:
                # Use exact match for non-regex queries
                cursor.execute("SELECT question, answer FROM qa WHERE question = %s", (question,))
            results = cursor.fetchall()
            if results:
                return results
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
    return None
    
def query_with_caching(payload, regex=False):
    # Check the database first
    question = payload.get("question")
    if question:
        if not regex:
            answer_from_db = query_database(question)
        else:
            answer_from_db = query_database(question, regex=True)
        if answer_from_db:
            # Return only the answer from the database
            return [row[1] for row in answer_from_db]  # Index 1 corresponds to the answer in the database

    # If not found in the database, make the API request
    response_json = query_api(payload)

    # Store the question and answer in the database
    if question and response_json:  # Check if response_json is not empty
        try:
            with mysql.connector.connect(**DB_CONFIG) as connection:
                cursor = connection.cursor()
                print("Inserting into database:", question, response_json)
                cursor.execute("INSERT INTO qa (question, answer) VALUES (%s, %s)", (question, response_json))
                connection.commit()
        except mysql.connector.Error as err:
            print(f"Database Error: {err}")

    # Return the API response
    return response_json  # This line was added to return the API response directly


# Replace this with your actual API query
example_query_payload = {
    "question": "яка ціна шкіряних ",
}

def makeTheOrder(orderPayload):
    try:
        # Define your API key for KeyCRM
        api_key = 'ZjBjNDFhN2M4YjJjNjM5NzU1MGVhMTcxZjhjYzNhNDU3ZTAwMTIwMA'  # Replace with your actual KeyCRM API key
        
        # Send a POST request to the KeyCRM API
        response = requests.post(
            "https://openapi.keycrm.app/v1/order",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            json=orderPayload,
        )
        
        if response.status_code == 200:
            # Order placed successfully
            return "Order placed successfully!"
        else:
            # Error placing the order
            return "Error placing order."
    except Exception as e:
        return f"Error: {str(e)}"


# Call the query_with_caching function with regex=True to enable regular expression matching
response = query_with_caching(example_query_payload, regex=True)

# Print the API response
from flask import Flask, request, jsonify, render_template
import mysql.connector
import requests

app = Flask(__name__)

# Define your API URL and DB_CONFIG as in your original code

# ... (API and database functions)

@app.route('/')
def home():
    return render_template('widget.html')
# Modify your makeOrderButton click event to call makeTheOrder function
@app.route('/api', methods=['POST'])
def api():
    try:
        payload = request.json
        if 'make_order' in payload:
            # Extract the order payload from the request
            orderPayload = payload['make_order']

            # Call makeTheOrder function to submit the order
            response = makeTheOrder(orderPayload)
        else:
            # Handle other chatbot queries here
            response = query_with_caching(payload, regex=True)

        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)})


if __name__ == '__main__':
    app.run(debug=True)
