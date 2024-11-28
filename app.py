import google.generativeai as genai
genai.configure(api_key="AIzaSyAg9e0YBPIRJdEPcGclhvoM0-Uaw37qyNo")
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# Sample data.csv - replace with your actual dataset
sample_data = {
    'Flight Carrier': ['Airline A', 'Airline B', 'Airline A', 'Airline C', 'Airline B'],
    'Flights Taken': [500, 300, 700, 200, 400],
    'Region': ['North', 'South', 'North', 'East', 'West']
}
df = pd.DataFrame(sample_data)

# Initialize Dash App
app = dash.Dash(__name__)

# Layout of the Web Application
app.layout = html.Div([
    html.H1("AI-powered Data Insights"),
    dcc.Input(id='query-input', type='text', placeholder='Ask a query like "Most used flight carrier"'),
    html.Button("Submit", id="submit-button"),
    html.Div(id="output"),
    dcc.Graph(id="output-graph")
])

# Callback to interact with the Gemini API and process the query
@app.callback(
    [Output('output', 'children'),
     Output('output-graph', 'figure')],
    [Input('submit-button', 'n_clicks')],
    [dash.dependencies.State('query-input', 'value')]
)
def generate_response(n_clicks, query):
    if not query:
        return "", {}

    # Generate content using Gemini API (Query Handling)
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(query)
    
    # Example query: "What is the most used flight carrier?"
    if "most used flight carrier" in query.lower():
        # Extract insights from Gemini response
        response_text = response.text
        
        # Generate a bar graph for "Most used flight carrier"
        fig = px.bar(df, x="Flight Carrier", y="Flights Taken", title="Most Used Flight Carrier")
        return response_text, fig
    else:
        return "No insights available for this query.", {}

# Run the server
if __name__ == '__main__':
    app.run_server(debug=True)
