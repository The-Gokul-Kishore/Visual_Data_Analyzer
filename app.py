from dash import Dash, html, dcc, Input, Output
import pandas as pd
import plotly.express as px
from gemini import call_gemini

# Load dataset
DATASET_PATH = "sample_data.csv"
df = pd.read_csv(DATASET_PATH)

# Dash app
app = Dash(__name__)

app.layout = html.Div([
    html.H1("Dynamic Visualization Bot"),
    dcc.Input(id="query_input", type="text", placeholder="Ask a question...", style={"width": "50%"}),
    html.Button("Submit", id="submit_button"),
    html.Div(id="response_text", style={"margin": "20px 0"}),
    dcc.Graph(id="response_graph")
])

@app.callback(
    [Output("response_text", "children"), Output("response_graph", "figure")],
    [Input("submit_button", "n_clicks")],
    [Input("query_input", "value")]
)
def handle_query(n_clicks, user_query):
    if n_clicks:
        # Prepare prompt with dataset context
        dataset_context = f"The dataset has columns {list(df.columns)} and sample data {df.head(3).to_dict(orient='records')}."
        prompt = f"""{dataset_context} Based on this dataset compile a python pandas code to work on this query: {user_query} and give the code and also a plotly code to show the output as dashboard\
            use this JSON schema : 
            pandas code ={'the pandas code'}
            """
        
        # Call Gemini API
        response = call_gemini(prompt)
        
        if "error" in response:
            return "Error: Unable to process query.", {}
        
        # Extract response content
        text_response = response.get("text", "No textual response provided.")
        chart_data = response.get("chart_data", None)
        chart_type = response.get("chart_type", "bar")  # Assume bar chart as default
        
        # Generate graph if chart data is provided
        if chart_data:
            chart_df = pd.DataFrame(chart_data)
            if chart_type == "bar":
                fig = px.bar(chart_df, x=chart_df.columns[0], y=chart_df.columns[1])
            elif chart_type == "line":
                fig = px.line(chart_df, x=chart_df.columns[0], y=chart_df.columns[1])
            else:
                fig = {}
            return text_response, fig
        
        return text_response, {}
    return "", {}

if __name__ == "__main__":
    app.run_server(debug=True)
