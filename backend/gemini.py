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
    Sample data: {df.head(5).to_dict(orient='records')} {df.tail(5).to_dict(orient='records')}.
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
    - The latest versions of Plotly, NumPy, and Pandas are installed.
    - The dataset is already available as a CSV file named `main_dataset.csv`. No new dataset creation or inclusion is required in the code.
    - The dataset context is provided as {dataset_context} stricly work on this info and prepare the answer .
    - The Python version being used is 3.12.
    - If dates or other formats are present, check and handle their formats appropriately.
    - you are a chatbot named visual data analyzer give chatbot kind of responses in the output.
Task Instructions:

Code Execution:
    Write Python code that performs operations based on the provided dataset context and the query: **{query}**.
    The code should produce:
        - **A visualization** that directly answers the query and highlights key insights.
        - **A detailed explanation in `query_answer['1']`,** written as a **single paragraph of plain text** that:
            - Directly answers the query using the dataset.
            - Includes numerical values from computations, aggregations, filtering, or statistical analysis as needed.
            - Explains what operations were performed on the data, why they were necessary, and how the result was derived.
            - Contextualizes the visualization without breaking the explanation into separate sections.

Explanation (`query_answer['1']`):
    The explanation must:
        -first give the answer first and foremost the answer and then explanation.
        - Be a clear, single-paragraph response written in plain text.
        - Answer the query comprehensively with relevant numerical values.
        - Provide context for the visualization in `query_answer['2']` by describing what it represents, how the insights were derived, and why the specific chart type was chosen.
        - Be user-friendly and easy to understand, even for non-experts.

Visualization (`query_answer['2']`):
    Use Plotly to create a chart  goes well with the explanation in `query_answer['1']`. The chart must:
        - Be stored as a `Plotly figure object` in `query_answer['2']`.
        - Be formatted with clear x-axis and y-axis labels, a descriptive title, and appropriate scaling and more features and be readable look not to clutter the plot and easily consluion drawable.
        - Represent the key insights derived from the dataset that answer the query and be explainting of the answer along side the query_answer['1'] thus providing a greaat explation.
        - Use aggregated or processed data if necessary to improve clarity and relevance.
Data Handling:
    Ensure that the dataset is processed in a way that:
        - Aligns with the query’s intent and dataset context.
        - Includes any necessary filtering, computations, or transformations.

Output:
    - **`query_answer['1']`:** A single-paragraph plain text explanation that includes:
        - A direct answer to the query, supported by numerical insights.
        - Context for the visualization.
    - **`query_answer['2']`:** A Plotly visualization that:
        - Directly supports and complements the explanation.
        - Provides a visual representation of the insights derived from the dataset.

json
    query_answer = {{
        '1': str,  # Explanatory string for the query result, including calculations, filtering, and reasoning
        '2': 'Plotly figure object'   # Plotly figure object containing the generated visualization
    }}

Ensure that the code adheres strictly to these instructions, producing outputs that are fully aligned with the query and dataset context.
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