import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import requests
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
app = dash.Dash(__name__)

# Layout of the Dash app
app.layout = html.Div([
    html.H1("Dataset Insight Driver", className="title"),

    # Container for the conversation (including graphs and text)
    html.Div(id='chat-container', className="chat-container"),

    # Input field for the query
    dcc.Input(id='queryInput', type='text', placeholder="Ask your question here...", className="query-input"),

    # Submit button
    html.Button('Submit', id='submitButton', n_clicks=0, className="submit-button"),

    # Space for the textual answer (system's response)
    html.Div(id='answer', className="answer"),

    # Graph placeholder with a loading indicator
    dcc.Loading(
        id="loading-graph",
        type="circle",  # You can change the type (circle, dot, etc.)
        children=dcc.Graph(id='graph')
    )
])

# Store conversation history in a global variable
conversation_history = []

# Callback to handle query submission and update output
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
        print("EER",data)
        # Extract textual answer and graph data
        answer_raw = data['1']
        print("anwer raw is loaded")
        graph_data = json.loads(data['2'])
        print("answer 1 ",answer_raw)
        
        # Create a Plotly figure from the response data
        fig = go.Figure(data=graph_data['data'], layout=graph_data['layout'])
        print("GRAP CREATED")
        # Add system response to conversation history
        formatted_answer = parse_summary(answer_raw)        
        print("BEfore converstaion added")
        conversation_history.append(html.Div(formatted_answer, className="system-message"))
        print("after coverstaion added ")
        # Add the graph to the conversation
        conversation_history.append(dcc.Graph(
            id=f'graph-{n_clicks}', figure=fig, className="graph", style={'marginTop': '20px', 'marginBottom': '20px'}
        ))

        # Return updated conversation, answer, and graph
        return conversation_history, html.Div(formatted_answer), fig

    except Exception as e:
        print("thee error message",e)
        error_message = f"Error: {str(e)}"
        conversation_history.append(html.Div(f"System: {error_message}", className="system-message"))
        return conversation_history, error_message, go.Figure()

if __name__ == '__main__':
    app.run_server(debug=True)
