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

                # Dataset Summary Section
        html.Div([
            html.H3("Dataset Summary", className="dataset-summary-heading"),
            html.Div(id="dataset-summary", className="dataset-summary"),
        ], className="summary-container"),

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


@app.callback(
    Output('upload-status', 'children'),
    [Input('upload-data', 'contents')],
    [State('upload-data', 'filename')]
)
def handle_file_upload(contents, filename):
    if contents is None:
        return "No file uploaded yet."

    try:
        # Parse the uploaded file
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        # Save the uploaded file
        upload_path = os.path.join(UPLOAD_DIR, "main_dataset.csv")
        df.to_csv(upload_path, index=False)
        return f"File '{filename}' uploaded and saved successfully!"
    except Exception as e:
        return f"Error processing the file: {str(e)}"

@app.callback(
    [
        Output('chat-container', 'children'),
        Output('answer', 'children'),
        Output('graph', 'figure'),
        Output('submitButton', 'disabled'),
        Output('queryInput', 'disabled'),
        Output('dataset-summary', 'children')
    ],
    [Input('submitButton', 'n_clicks')],
    [State('queryInput', 'value')]
)
def update_output(n_clicks, query):
    global conversation_history

    if not query or n_clicks == 0:
        return conversation_history, "", go.Figure(), False, False, ""

    disable_inputs = True

    try:
        conversation_history.append(html.Div(f"User: {query}", className="user-message"))

        response = requests.post("http://127.0.0.1:5000/generate", json={'query': query})
        data = response.json()

        answer_raw = data.get('1', '')
        graph_data_raw = data.get('2', '{}')

        describe_raw = data.get('describe', '{}')
        info_raw = data.get('info', '')

        try:
            graph_data = json.loads(graph_data_raw)
        except json.JSONDecodeError as e:
            return conversation_history, f"Error: Could not decode graph JSON - {str(e)}", go.Figure(), False, False, ""

        fig = go.Figure(
            data=graph_data.get('data', []),
            layout=graph_data.get('layout', {})
        )

        formatted_answer = answer_raw
        conversation_history.append(html.Div(formatted_answer, className="system-message"))

        conversation_history.append(dcc.Graph(
            id=f'graph-{n_clicks}', figure=fig, className="graph", style={'marginTop': '20px', 'marginBottom': '20px'}
        ))

        # Format describe and info for display
        describe_df = pd.read_json(describe_raw).to_html(classes="table table-striped")
        summary_html = f"<h4>Describe:</h4>{describe_df}<h4>Info:</h4><pre>{info_raw}</pre>"

        return conversation_history, html.Div(formatted_answer), fig, False, False, html.Div([
            html.Div(dcc.Markdown(summary_html), className="dataset-summary-content")
        ])

    except Exception as e:
        error_message = f"Error: {str(e)}"
        conversation_history.append(html.Div(f"System: {error_message}", className="system-message"))
        return conversation_history, error_message, go.Figure(), False, False, ""
    
if __name__ == '__main__':
    app.run_server(debug=True)
