from flask import Flask, request, jsonify
import google.generativeai as genai
import pandas as pd
import plotly.express as px
import json
from gemini import call_gemini
import pandas as pd
app = Flask(__name__)



@app.route('/generate', methods=['POST'])
def generate():
    # Get the user query from the frontend
    query = request.json.get('query')

    # Call Gemini API to get the Python code for the query
    model = genai.GenerativeModel("gemini-1.5-pro-latest")

    response = call_gemini(query)
    generated_code = response
    print("EEEEEEEEEEEEEEEEEEEEEE")
    print(response)

    try:
        # Assume the generated code returns a Plotly figure `fig`
        exec_locals ={}
        exec(generated_code,{},exec_locals)
        print("HERE")
        # If the figure is created successfully, return the graph's JSON data
        if 'fig' in locals():
            print("generation is sucessfull")
            exec_locals['fig'].show()
            plot_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            return jsonify({'result': 'Graph generated', 'graph': plot_json, 'code': generated_code})
        else:

            return jsonify({'result': 'Code executed but no graph returned', 'graph': None, 'code': generated_code})

    except Exception as e:
        print(" then here right?")
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
