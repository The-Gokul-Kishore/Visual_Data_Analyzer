from flask import Flask, request, jsonify
import pandas as pd
import plotly.io as pio
import plotly.express as px
import json
import numpy as np
from gemini import call_gemini
import time  # Import time for sleep between retries

app = Flask(__name__)

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
                        query_answer['2'] = pio.to_json(exec_locals['fig'])
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
