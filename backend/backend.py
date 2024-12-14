from flask import Flask, request, jsonify
import pandas as pd
import plotly.io as pio
import plotly.express as px
import json
import numpy as np
import os
import io
from gemini import call_gemini
import base64
import time  # Import time for sleep between retries

app = Flask(__name__)


UPLOAD_FOLDER = './'  # Directory where datasets will be saved
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        # Parse JSON data
        data = request.get_json()
        filename = data.get('filename')
        content_string = data.get('contents')

        # Validate inputs
        if not filename or not content_string:
            raise ValueError("Filename or content is missing")

        # Decode and read the file
        decoded = base64.b64decode(content_string)
        df = None

        try:
            # Attempt to read with UTF-8
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        except UnicodeDecodeError:
            # Fallback to Latin-1
            df = pd.read_csv(io.StringIO(decoded.decode('latin-1')))

        # Save the dataset
        file_path = os.path.join(UPLOAD_FOLDER, 'main_dataset.csv')
        df.to_csv(file_path, index=False)

        return jsonify({'message': f"File '{filename}' saved successfully.", 'path': file_path}), 200

    except Exception as e:
        # Log and return the error
        print("Error:", str(e))
        return jsonify({'error': str(e)}), 400

# Define the maximum number of retries in case of errors
MAX_RETRIES = 3

@app.route('/generate', methods=['POST'])
def generate():
    retry_count =0
    while retry_count < MAX_RETRIES:
    # Get the user query from the frontend
            query = request.json.get('query')
            print(f"Received query: {query}")
            
            # Call Gemini API to get Python code for the query
            response = call_gemini(query)
            generated_code = response
            print(f"Generated code from Gemini: {generated_code}")            
            try:
                    # Prepare the execution environment for the generated code
                    exec_locals = {
                        'pd': pd,
                        'np': np,
                        'px': px,
                        'pio': pio
                    }

                    # Execute the generated code to process the query and generate the graph
                    exec(generated_code, {}, exec_locals)
                    print("Executed generated code.")

                    # Check if the 'fig' (graph) was created successfully
                    if 'query_answer' in exec_locals:
                        # Return the answer and graph data as JSON
                        query_answer = exec_locals.get('query_answer', {'1': 'No answer', '2': {}})
                        query_answer['2'] = pio.to_json(exec_locals['query_answer']['2'])
                        return jsonify(query_answer)
                    else:
                        # Return an error message if no figure is created
                        return jsonify({
                            'result': 'Code executed but no figure created.',
                            'graph': None,
                            'code': generated_code
                        })

            except Exception as e:
                    print(f"Error on attempt {retry_count + 1}: {str(e)}")

                    # Increment retry count
                    retry_count += 1

                    # If retries are left, wait for a while and retry
                    if retry_count < MAX_RETRIES:
                        print("Retrying...")
                        time.sleep(2)  # Wait for 2 seconds before retrying
                    else:
                        # After maximum retries, return the error message
                        return jsonify({'error': str(e)})


if __name__ == '__main__':
    app.run(debug=True)
