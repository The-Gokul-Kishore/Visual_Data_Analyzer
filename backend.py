from flask import Flask, request, jsonify
import pandas as pd
import plotly.io as pio
import plotly.express as px
import json
import numpy as np
from gemini import call_gemini
app = Flask(__name__)




@app.route('/generate', methods=['POST'])
def generate():
    print("EEERIR\n\n")
    # Get the user query from the frontend
    query = request.json.get('query')
    print("here")
    # Call Gemini API to get the Python code for the query
    response = call_gemini(query)
    generated_code = response
    print("EEEEEEEEEEEEEEEEEEEEEE")
    print(response)

    try:
        # Assume the generated code returns a Plotly figure `fig`
        exec_locals ={ 
    'pd': pd,
    'np': np,
    'px': px,
    'pio': pio
    }
        exec(generated_code,{},exec_locals)
        print("HERE")
        # If the figure is created successfully, return the graph's JSON data
        if 'fig' in exec_locals:
           print("fig is present")
        if 'query_answer' in exec_locals:
            
            query_answer = exec_locals['query_answer']
            print( "here?")
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
        print(" then here right? lesssssssssssssssssssssssssssssss goooo",str(e))
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
