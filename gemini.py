import requests
import google.generativeai as genai
import pandas as pd
def call_gemini(query):
    df = pd.read_csv('main_dataset.csv')
    genai.configure(api_key="AIzaSyAg9e0YBPIRJdEPcGclhvoM0-Uaw37qyNo")
    model = genai.GenerativeModel("gemini-1.5-flash")
    dataset_context = f"The dataset has columns {list(df.columns)} and sample data {df.head(3).to_dict(orient='records')}."
    prompt = f"we have a dataset of this context: {dataset_context} Assume the data is already there in a csv named main_dataset.csv and dont give any new dataset in the code but give the code excuting only this dataset . and that all the requirements are satified and just give the code to do the visualization and answer and no more only just the code :Based on this dataset compile a python 3.11 ploty code to work on this query : '{query}' just give the asnwer and a graph to visualize dont give anything but code not even the the title python you give dont give that pls ," 
    print("HELO")


    prompt = f"""ok bro we need you to generate a python statement which gets into execution automatically. Please don't give extra explanation or extra stuff. 
Assume we have plotly, numpy, and pandas installed. We have a dataset of this context: {dataset_context}. 
Assume that the data is already present in a CSV named main_dataset.csv, and don't give any dataset in the code. Just give the code and explanation in this format:

We have a dataset of this context: {dataset_context}. Assume the data is already there in a CSV named main_dataset.csv, and don't give any new dataset in the code, 
but give the code executing only this dataset. All requirements are satisfied. Just give the code to do the visualization and answer, and no more—only just the code:

Based on this dataset, compile a Python 3.11 plotly code to work on this query: '{query}'. Just give the answer and a graph to visualize. Don't give anything but code, not even a title.

You may need Python manipulation (but not necessary) with pandas and numpy (assume they are already installed). Then, give a Python code to produce the desired result for the query and produce a good output for that and store it as a string in that string along with the result explain the result and query to the person in a  few lines of explaining this is for a non data science person with little knowledge of these stuff so be more explanative and store them answer and explanation in query_answer 1.
bro i cant adjust it so you give code as the prompt says and give the best results possible and store the results in the dict as follows:
Also, include a plotly code to give a good explanation of the related part of the data in this format:
The aggregation should be for the output and can be placed in the output.  
the format is as follows :
python code to do operations in the dataframe to get numerical results and give them as a well-formatted answer string and store it in a string named answer is called as the query_answer 1
and python plotly code to create an explanation in visual format with graphs of the related subject (be genreral or specific to give good visualization is the key if possible compare is given and store the answer fig in  query_answer 2
Use this JSON schema:
query_answer = {{
    '1': str,
    '2':str
}}
This is the query: {query} do for this."""


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