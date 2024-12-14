import dash
from dash import html, dcc,dash_table
from dash.dash_table import DataTable
from dash.dependencies import Input, Output, State
import requests
import plotly.graph_objs as go
import json
import base64
import io
import pandas as pd
import os
from datetime import datetime
import time

# Initialize Dash app
app = dash.Dash(__name__)

# Layout for the Dash application
app.layout = html.Div([
    # Main Layout Container
    html.Div([
        
        # Header (Application title)
        html.Div([
            html.H1("Visual Data Analyser", className="title"),
        ], className="header-container"),

        # About the application section
        html.Div([
            html.H2("About This Application", className="about-title"),
            html.P("This is a Dataset Explorer tool that allows users to upload a CSV file, "
                "ask questions about the dataset, and visualize insights in the form of "
                "graphs. Simply upload a CSV file and type your queries in natural language. "
                "With the power of Gemini, we can process them into meaningful insights through the search bar.", 
                className="about-description"),
            html.P("To use it, upload your dataset, type your question about the data, and hit 'Submit' or press 'Enter' "
                      "to get the answer along with any relevant graphs.\n ask it anything in about the data from simple queries like 'summarize the data' to complex operations it can do it", className="about-instructions"),
            html.H4("History Functionality", className="history-title"),
            html.P("This application also keeps track of your queries and the responses generated, creating a "
                "history of your interactions with the system.", className="history-description"),
        ], className="about-container"),

        # File Upload Section
        html.Div([
            html.Div("Upload Dataset", className="upload-heading"),
            dcc.Upload(
                id='upload-data',
                children=html.Div([
                    'Drag and Drop or ',
                    html.A('Select Files')
                ]),
                style={
                    'width': '100%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px'
                },
                accept='.csv',  # Only accept CSV files
                multiple=False  # Allow single file upload only
            ),
            html.Div(id='upload-status', className="upload-status")  # Display file upload status
        ], className="upload-container"),
        html.Div( [
            html.Div("Dataset Preview",className = "dataset-preview-heading"),
            dash_table.DataTable(
                id= 'dataset-table',
                style_table = {'height':'300px','width': '50%','margin':'0 auto','overflow':'hidden'},
                style_cell = {'textAlign':'left','padding':'5px'},
            ),
            
        ],className = "dataset-preview-container"),
        # Search Bar Section (User input for questions)
        html.Div([
            html.Div("Ask questions about the dataset for insights", className="search-bar-heading"),
            dcc.Input(id='queryInput', type='text', placeholder="Ask your question here...", className="query-input"),
            html.Button('Submit', id='submitButton', n_clicks=0, className="submit-button"),
        ], className="search-bar"),

        # Answer Section (Displays the answer to the query)
        html.Div([
            html.Div("Answer:", className="answer-heading"),
            dcc.Loading(
                id="loading-answer",  # Loading spinner for answer
                type="circle",  # Style of the spinner
                children=html.Div(id='answer', className="answer", children="Submit a query to get an answer.")
            ),
        ], className="answer-container"),

        # Graph Section (Displays the generated graph)
        html.Div([
            html.Div("Graph:", className="graph-heading"),
            dcc.Loading(
                id="loading-graph",
                type="circle",  # Spinner style
                children=dcc.Graph(id='graph')  # Displays the generated graph
            ),
        ], className="graph-container"),

        # Chat History Section (Displays the query history)
        html.Div([
            html.Div("Chat history:", className="history-heading"),
            html.Div(id='chat-container', className="chat-container")  # Displays the conversation history
        ], className="history-container"),
    ], className="main-container"),
])

@app.callback(
    Output('upload-status', 'children'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename')
)
def handle_file_upload(contents, filename):
    if contents is None:
        return "No file uploaded yet."

    try:
        # Send the file to the backend via a POST request
        content_type, content_string = contents.split(',')
        response = requests.post(
            "http://127.0.0.1:5000/upload",  # Adjust the URL to match your backend route
            json={'filename': filename, 'contents': content_string}
        )
        response.raise_for_status()
        return f"File '{filename}' uploaded successfully and saved on the backend."
    except Exception as e:
        return f"Error: {str(e)}"

# Store conversation history globally
conversation_history = []

@app.callback(
    [
        Output('chat-container', 'children'),
        Output('answer', 'children'),
        Output('graph', 'figure'),
    ],
    [
        Input('submitButton', 'n_clicks'),
        Input('queryInput', 'n_submit')
    ],
    [State('queryInput', 'value')]
)
def process_query(n_clicks, n_submit, query):
    global conversation_history
    retry_count = 0
    max_retries = 2

    # Return if no query is provided
    if not query or (n_clicks == 0 and n_submit is None):
        return conversation_history, "Submit a query to get an answer.", go.Figure()

    while retry_count <= max_retries:
        try:
            # Get current timestamp for logging
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Add the user's query at the top of the history
            conversation_history.insert(0, html.Div(f"[{timestamp}] User: {query}", className="user-message"))

            # Simulate backend request and fetch response
            response = requests.post("http://127.0.0.1:5000/generate", json={'query': query})
            response.raise_for_status()  # Raise error for non-200 HTTP responses
            data = response.json()

            # Extract answer and graph data from the response
            answer_raw = data.get('1', 'No answer available.')
            graph_data = json.loads(data.get('2', '{}'))

            # Create Plotly figure from graph data
            fig = go.Figure(
                data=graph_data.get('data', []),
                layout=graph_data.get('layout', {})
            )

            # Add the system's response at the top of the history
            conversation_history.insert(0, html.Div(f"[{timestamp}] System: {answer_raw}", className="system-message"))
            conversation_history.insert(0, dcc.Graph(figure=fig))  # Add the graph at the top

            return conversation_history, answer_raw, fig

        except Exception as e:
            retry_count += 1
            error_message = f"Error: {str(e)}"

            # If maximum retries exceeded, show error
            if retry_count > max_retries:
                conversation_history.insert(0, html.Div(f"[{timestamp}] Error: {error_message}", className="system-message"))
                return conversation_history, error_message, go.Figure()

            # If it's a retry attempt, show retry message and pause
            conversation_history.insert(0, html.Div(f"[{timestamp}] Error occurred. Retrying... Attempt {retry_count}/{max_retries}", className="system-message"))
            time.sleep(1)  # Wait for 1 second before retrying (optional)

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)
