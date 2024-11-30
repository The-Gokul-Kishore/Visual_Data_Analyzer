import dash
from dash import html, dcc  # Dash HTML and core components
from dash.dependencies import Input, Output, State  # Callback-related dependencies
import requests
import plotly.graph_objs as go
import json
import base64
import io
import pandas as pd
import os
# Ensure the upload directory is in the same place as the Python script
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)))

# Create the upload directory if it doesn't exist
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

def parse_summary(raw_text):
    sections = raw_text.split("\n\n")
    formatted_sections = []
    for section in sections: 
        lines = section.strip().split("\n")
        if not lines:
            continue
        title = lines[0]
        rows = lines[1:]

        table_rows = [
            html.Tr([html.Td(cell) for cell in row.split(" ") if cell])  # Split by spaces for columns
            for row in rows
        ]
        formatted_sections.append(html.Div([
            html.H3(title, className="summary-title"),
            html.Table(table_rows, className="summary-table")
        ]))

    return html.Div(formatted_sections, className="summary-container")

# Initialize Dash app
app = dash.Dash(__name__)

app.layout = html.Div([
    # Main Layout Container
    html.Div([
        # Header (Inside its own container)
        html.Div([
            html.H1("Dataset Explorer", className="title"),
        ], className="header-container"),

        # File Upload Section (Inside its own container)
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
            html.Div(id='upload-status', className="upload-status")  # To display status messages
        ], className="upload-container"),


        # Search Bar Section (Inside its own container)
        html.Div([
            html.Div("Ask questions about the dataset for insights", className="search-bar-heading"),
            dcc.Input(id='queryInput', type='text', placeholder="Ask your question here...", className="query-input"),
            html.Button('Submit', id='submitButton', n_clicks=0, className="submit-button"),
        ], className="search-bar"),

        # Answer Section (Inside its own container)
        html.Div([
                html.Div("Answer:", className="answer-heading"),
            html.Div(id='answer', className="answer")
        ], className="answer-container"),

        # Graph Section (Inside its own container)
        html.Div([
            html.Div("Graph:", className="graph-heading"),
            dcc.Loading(
                id="loading-graph",
                type="circle",  # You can change the type (circle, dot, etc.)
                children=dcc.Graph(id='graph')
            ),
        ], className="graph-container"),


        # Chat History Section (Inside its own container)
        html.Div([
            html.Div("Chat history:", className="history-heading"),
            html.Div(id='chat-container', className="chat-container")
        ], className="history-container"),
    ], className="main-container"),
])

# Store conversation history in a global variable
conversation_history = []
loading = False

@app.callback(
    [
        Output('chat-container', 'children'),
        Output('answer', 'children'),
        Output('graph', 'figure'),
        Output('submitButton', 'disabled'),
        Output('queryInput', 'disabled')
    ],
    [Input('submitButton', 'n_clicks'),
     Input('queryInput', 'n_submit')],  # Listen for Enter key press
    [State('queryInput', 'value')]
)
def update_output(n_clicks, n_submit, query):
    global conversation_history
    global loading
    # Maximum retries
    max_retries = 3

    # If no query is entered and neither submit nor enter is pressed, return default state
    if not query or (n_clicks == 0 and n_submit == 0 and not loading):
        return conversation_history, "", go.Figure(), False, False

    # If a query is entered and it's not loading, show the loading state
    if query and not loading:
        loading = True
        return conversation_history, "loading...", go.Figure(), True, True

    disable_inputs = True

    # Process the query when loading is True
    for attempt in range(max_retries):
        try:
            # Log the current attempt
            print(f"Attempt {attempt + 1} of {max_retries}")

            # Add user query to conversation history only once
            if attempt == 0:  # Only add the query during the first attempt
                conversation_history.append(html.Div(f"User: {query}", className="user-message"))

            # Send query to the backend
            response = requests.post("http://127.0.0.1:5000/generate", json={'query': query})
            response.raise_for_status()  # Raise an error for bad HTTP status codes
            data = response.json()

            # Extract data from the response
            answer_raw = data.get('1', '')
            graph_data_raw = data.get('2', '{}')

            # Parse graph data
            try:
                graph_data = json.loads(graph_data_raw)
            except json.JSONDecodeError as e:
                raise ValueError(f"Could not decode graph JSON - {str(e)}")

            # Create the graph figure
            fig = go.Figure(
                data=graph_data.get('data', []),
                layout=graph_data.get('layout', {})
            )

            # Format the answer
            formatted_answer = answer_raw
            conversation_history.append(html.Div(formatted_answer, className="system-message"))

            # Append the graph to the conversation
            conversation_history.append(dcc.Graph(
                id=f'graph-{n_clicks}', figure=fig, className="graph", style={'marginTop': '20px', 'marginBottom': '20px'}
            ))

            # Reset loading state after processing is complete
            loading = False

            # Return success response
            return conversation_history, html.Div(formatted_answer), fig, False, False

        except Exception as e:
            # Log the error and retry
            loading = False
            print(f"Error encountered during attempt {attempt + 1}: {str(e)}")
            if attempt < max_retries - 1:
                continue  # Retry on failure
            else:
                # Maximum retries exceeded
                error_message = f"Error: Unable to process your query after {max_retries} attempts. Please try again later."
                conversation_history.append(html.Div(error_message, className="system-message"))
                return conversation_history, error_message, go.Figure(), False, False
 
if __name__ == '__main__':
    app.run_server(debug=True)
