# Core Dash and Plotly libraries
import dash
from dash import html, dcc  # Dash HTML and core components
from dash.dependencies import Input, Output, State  # Callback-related dependencies

# Requests for interacting with the Flask backend
import requests

# Plotly graph objects for creating and handling figures
import plotly.graph_objs as go

# JSON for decoding graph data
import json


def parse_summary(raw_text):
    sections = raw_text.split("\n\n")
    formatted_sections = []
    for section in sections : 
        lines = section.strip().split("\n")
        if not lines:
            continue

        # Use the first line as the title
        title = lines[0]
        rows = lines[1:]

        # Create a table for the data
        table_rows = [
            html.Tr([html.Td(cell) for cell in row.split(" ") if cell])  # Split by spaces for columns
            for row in rows
        ]

        # Append formatted section
        formatted_sections.append(html.Div([
            html.H3(title, className="summary-title"),
            html.Table(table_rows, className="summary-table")
        ]))

    return html.Div(formatted_sections, className="summary-container")

# Initialize Dash app
# Initialize Dash app
app = dash.Dash(__name__)

# Layout of the Dash app
app.layout = html.Div([
    # Header
    html.H1("Dataset Insight Driver", className="title"),

    # Search bar section (query input and submit button)
    html.Div([
        dcc.Input(id='queryInput', type='text', placeholder="Ask your question here...", className="query-input"),
        html.Button('Submit', id='submitButton', n_clicks=0, className="submit-button"),
    ], className="search-bar"),

    # Space for the textual answer (system's response)
    html.Div(id='answer', className="answer"),


    # Graph placeholder with a loading indicator
    dcc.Loading(
        id="loading-graph",
        type="circle",  # You can change the type (circle, dot, etc.)
        children=dcc.Graph(id='graph')
    ),
    # Container for the conversation history (chat container)
    html.Div(id='chat-container', className="chat-container"),

])

# Store conversation history in a global variable
conversation_history = []
@app.callback(
    [Output('chat-container', 'children'),
     Output('answer', 'children'),
     Output('graph', 'figure')],
    [Input('submitButton', 'n_clicks')],
    [State('queryInput', 'value')]
)
def update_output(n_clicks, query):
    global conversation_history

    if not query or n_clicks == 0:
        return conversation_history, "", go.Figure()

    try:
        # Add user message to conversation history
        conversation_history.append(html.Div(f"User: {query}", className="user-message"))
        
        # Send query to the backend (Flask)
        response = requests.post("http://127.0.0.1:5000/generate", json={'query': query})
        data = response.json()

        # Debugging
        print("Frontend Data Received:", data)

        # Extract textual answer
        answer_raw = data.get('1', '')
        print("Answer Raw:", answer_raw)
        
        # Extract graph JSON and handle errors
        graph_data_raw = data.get('2', '{}')
        try:
            graph_data = json.loads(graph_data_raw)
        except json.JSONDecodeError as e:
            print("Failed to decode graph JSON:", e)
            return conversation_history, f"Error: Could not decode graph JSON - {str(e)}", go.Figure()

        # Debugging
        print("Graph Data (Raw JSON):", graph_data_raw)
        print("Graph Data (Parsed):", graph_data)

        # Create Plotly figure
        fig = go.Figure(
            data=graph_data.get('data', []),
            layout=graph_data.get('layout', {})
        )

        # Format the textual answer
        try:
            formatted_answer = parse_summary(answer_raw)
        except Exception as e:
            print("Error in parsing summary:", e)
            return conversation_history, f"Error in formatting answer: {str(e)}", go.Figure()

        # Add system response to conversation history
        conversation_history.append(html.Div(formatted_answer, className="system-message"))

        # Add graph to conversation
        conversation_history.append(dcc.Graph(
            id=f'graph-{n_clicks}', figure=fig, className="graph", style={'marginTop': '20px', 'marginBottom': '20px'}
        ))

        return conversation_history, html.Div(formatted_answer), fig

    except Exception as e:
        print("General Error:", e)
        error_message = f"Error: {str(e)}"
        conversation_history.append(html.Div(f"System: {error_message}", className="system-message"))
        return conversation_history, error_message, go.Figure()

if __name__ == '__main__':
    app.run_server(debug=True)
