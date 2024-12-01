import requests
import io
import google.generativeai as genai
import pandas as pd
def generate_dataset_context(df)->str:
    # Summarize dataset
    describe_data = df.describe(include='all').to_dict()  # Summary stats
    info_buf = io.StringIO()  # To capture df.info() output
    df.info(buf=info_buf)
    info_str = '\n'.join(info_buf)  # Get DataFrame info as string

    # Create dataset context
    dataset_context = f"""
    The dataset has the following columns: {list(df.columns)}.
    Sample data: {df.head(3).to_dict(orient='records')}.
    Statistical summary (describe): {describe_data}.
    Dataset info: {info_str}.
    Column data types: {df.dtypes.to_dict()}.
    Unique value counts per column: {df.nunique().to_dict()}.
    """
    return dataset_context


def generate_prompt(query,dataset_context)->str:
        # Generate a prompt for the Gemini API based on the query and dataset context
    prompt = f"""Generate a Python code that executes automatically based on the following requirements. Avoid any extra explanations or unrelated details.

    Assumptions:

    The latest versions of Plotly, NumPy, and Pandas are installed.
    The dataset is already available as a CSV file named main_dataset.csv. No new dataset creation or inclusion is required in the code.
    The dataset context is provided as {dataset_context}.
    The Python version being used is 3.12.

    Task Instructions:

    Code Execution:
        Write Python code that performs operations based on the provided dataset context and the query: {query}.
        The code should produce:
            - A visualization that is integral to answering the query and highlights key insights.
            - A detailed explanation in `query_answer['1']` that complements the visualization and may include additional computations or aggregations to provide a complete answer.

    Explanation (`query_answer['1']`):
        Provide a clear, structured explanation in `query_answer['1']` that:
            - Directly answers the query using the dataset, including computations like summing, aggregation, filtering, or statistical analysis as needed.
            - Explains what operations were performed on the data and why.
            - Provides context to the visualization by describing what it represents, how the insights were derived, and the reasoning behind any preprocessing or analysis.
            - Is formatted as a user-friendly string that non-experts can easily understand.
            - and also explains what is the process  behind the graph and what data is used
            - Is in plain text format in a pragraph form

    Visualization (`query_answer['2']`):
        Use Plotly to create a chart that complements the explanation and directly answers the query. This chart must:
            - Be stored as a `Plotly figure object` in `query_answer['2']`.
            - Be well-formatted with a relevant chart type (e.g., bar chart for comparisons, line chart for trends, scatter plot for relationships).
            - Include clear and appropriately scaled x-axis and y-axis labels, with a descriptive title.
        
            - If needed, include aggregated or processed data to enhance its relevance and clarity.

    Data Handling:
        Ensure that the dataset is processed in a way that:
            - Aligns with the query’s intent and dataset context.

    Output:
        Both the explanation and visualization should work together seamlessly:
            - The explanation in `query_answer['1']` may include summaries, aggregations, or other calculations to address the query comprehensively.
            - The visualization in `query_answer['2']` serves as a visual representation that complements and enhances the explanation.
            - Ensure the explanation and visualization are consistent and provide a cohesive response to the query.

json
    query_answer = {{
        '1': str,  # Explanatory string for the query result, including calculations, filtering, and reasoning
        '2': 'Plotly figure object'   # Plotly figure object containing the generated visualization
    }}

Ensure that the code adheres strictly to these instructions, producing outputs that are aligned with the query and dataset context.
"""
    print("Prompt generated")
    return prompt
def call_gemini(query):
    # Function to interact with Gemini API to generate content based on a query and dataset
    print("Gemini call initiated")
    df = pd.read_csv('main_dataset.csv')  # Read the dataset from CSV
    genai.configure(api_key="AIzaSyAg9e0YBPIRJdEPcGclhvoM0-Uaw37qyNo")  # Set up Gemini API
    model = genai.GenerativeModel("gemini-1.5-flash")  # Initialize the Gemini model
    print("Model connected")

    # Generate dataset context
    dataset_context = generate_dataset_context(df)
    print("Dataset context generated")

    # Generate the prompt for the query
    prompt = generate_prompt(query=query, dataset_context=dataset_context)

    # Request content generation from the model
    response = model.generate_content(prompt)
    print("Response received")

    # Extract the response text and clean it up
    text = response.text
    text = text.lstrip()  # Remove leading whitespace
    print("Type of string:", type(text))

    # Clean the Python code from response if wrapped in markdown
    if text.startswith("```python"):
        text = text[9:]  # Remove the first 9 characters
        text = text.replace("```python", "```").replace("```", "")  # Clean up any remaining backticks

    print("Generated code:", text)
    return text  # Return the generated code as a string