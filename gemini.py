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
    prompt = f"""Generate a Python code that executes automatically based on the following requirements. Avoid any extra explanations or unrelated details. 

    Assumptions:

    The latest versions of Plotly, NumPy, and Pandas are installed.
    The dataset is already available as a CSV file named main_dataset.csv. No new dataset creation or inclusion is required in the code.
    The dataset context is provided as {dataset_context}.
    The Python version being used is 3.12.

    Task Instructions:

    Code Execution:
        Write Python code that performs operations based on the provided dataset context and the query: {query}.
        The code should produce a visualization and explanation that is both clear and easy to understand, especially for non-experts.
        The visualization must include clearly labeled x-axis and y-axis with appropriate scaling based on the dataset’s context.

    Handling Large Datasets:
        If the query asks for a broader view (e.g., "show 100 instances" or "give me the top 100 items"), or if a broader view benefits the query (e.g., showing trends across many data points), process and display the necessary number of instances.
        For general queries (where no specific requirement for large datasets is mentioned), limit the data displayed to the most relevant 20 instances by default.
        Always ensure that the axes are properly labeled and that the scales of the axes are appropriate for the dataset and query context.
        If the data has been filtered to a specific subset (e.g., top 20, or only certain categories), clearly specify this in the output.

    Explanation Format:
        Provide an explanation of the query results in a well-formatted, user-friendly string. The explanation should make it clear for non-data-science individuals what the data means and how it answers the query.
        This explanation should be stored in the query_answer['1'] field.

    Visualization:
        Use Plotly to generate a suitable chart based on the query.
        The chart should be easy to interpret, with clear labels, a title, and appropriately scaled axes. The visualization should effectively convey the insights derived from the data.
        The code to generate the visualization should be stored in the query_answer['2'] field.

Guidelines for Visualization:

    If necessary, aggregate the data (e.g., summing, averaging) to provide more meaningful insights in the visualization.
    Select a chart type that is relevant to the query. For example, use bar charts, scatter plots, line charts, etc., depending on the nature of the query.
    Ensure that the axes are meaningful and not overly detailed, especially when using identifiers like IDs. Instead, use more context-relevant columns (like categories or numerical values).
    The chart should serve to draw clear conclusions from the data, helping the user easily understand the patterns or insights.

json
    query_answer = {{
        '1': str,  # Explanatory string for the query result
        '2': str   # Plotly visualization code
    }}
    
Ensure that:

    The code adheres to the instructions and generates only what is necessary to execute the query and provide the visualization.
    The final explanation is clear and understandable, with the relevant insights and charts provided as part of the output.
    """
    print("prompt generated")
    return prompt
def call_gemini(query):
    print("gemin_call")
    df = pd.read_csv('main_dataset.csv')
    genai.configure(api_key="AIzaSyAg9e0YBPIRJdEPcGclhvoM0-Uaw37qyNo")
    model = genai.GenerativeModel("gemini-1.5-flash")
    print("model connect)")
    dataset_context = generate_dataset_context(df)
    print("HELO")
    prompt = generate_prompt(query=query,dataset_context=dataset_context)
    response = model.generate_content(prompt)
    print("EHEEEr")
    print(response)
    
    text = response.text
    text  = text.lstrip()
    print("Type of string:",type(text))
    if text.startswith("```python"):
        text = text[9:]  # Remove the first 9 characters
        # Alternatively, use replace for multiple occurrences
        text = text.replace("```python", "```").replace("```", "")  # Clean up any remaining backticks
    print(text)
    return text