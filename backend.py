from flask import Flask, request, jsonify
import pandas as pd
import plotly.io as pio
import plotly.express as px
import json
import numpy as np
from gemini import call_gemini
import time  # Import time for sleep

app = Flask(__name__)

# Define the maximum number of retries
MAX_RETRIES = 3

@app.route('/generate', methods=['POST'])
def generate():
    print("EEERIRIR\n\n")
    # Get the user query from the frontend
    query = request.json.get('query')
    print("here")
    
    # Call Gemini API to get the Python code for the query
    response = call_gemini(query)
    generated_code = response
    print("EEEEEEEEEEEEEEEEEEEEEE")
    print(response)

    # Initialize a counter for retries
    retry_count = 0

    while retry_count < MAX_RETRIES:
        try:
            # Assume the generated code returns a Plotly figure `fig`
            exec_locals = {
                'pd': pd,
                'np': np,
                'px': px,
                'pio': pio
            }
            exec(generated_code, {}, exec_locals)
            print("HERE")

            # If the figure is created successfully, return the graph's JSON data
            if 'fig' in exec_locals:
                print("fig is present")

            if 'query_answer' in exec_locals:
                query_answer = exec_locals['query_answer']
                print("here?")
                print(query_answer['1'])
                query_answer['2'] = pio.to_json(exec_locals['query_answer']['2'])
                return jsonify(query_answer)
            else:
                return jsonify({
                    'result': 'Code executed but no query_answer returned',
                    'graph': None,
                    'code': generated_code
                })

        except Exception as e:
            print(f"Error on attempt {retry_count + 1}: {str(e)}")

            # Increment retry count
            retry_count += 1
            
            # If we have retries left, wait a bit and retry
            if retry_count < MAX_RETRIES:
                print("Retrying...")
                time.sleep(2)  # Wait for 2 seconds before retrying
            else:
                # After MAX_RETRIES, return the error
                return jsonify({'error': str(e)})


DATASET_PATH = os.path.join(UPLOAD_DIR, "main_dataset.csv")

@app.route('/summarize', methods=['GET'])
def summarize():
    if not os.path.exists(DATASET_PATH):
        return jsonify({"error": "Dataset not found. Please upload a dataset."}), 404

    try:
        df = pd.read_csv(DATASET_PATH)
        summary = {
            "describe": df.describe(include='all').to_dict(),
            "info": df.info(buf=None)  # Use `buf=None` to return as a string
        }
        return jsonify(summary)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
