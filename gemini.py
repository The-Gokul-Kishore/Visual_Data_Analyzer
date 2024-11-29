import requests
import google.generativeai as genai
import pandas as pd
def call_gemini(prompt):
    df = pd.read_csv('main_dataset.csv')
    genai.configure(api_key="AIzaSyAg9e0YBPIRJdEPcGclhvoM0-Uaw37qyNo")
    model = genai.GenerativeModel("gemini-1.5-flash")
    dataset_context = f"The dataset has columns {list(df.columns)} and sample data {df.head(3).to_dict(orient='records')}."
    prompt = f"we have a dataset of this context: {dataset_context} Assume the data is already there in a csv named main_dataset.csv and dont give any new dataset in the code but give the code excuting only this dataset . and that all the requirements are satified and just give the code to do the visualization and answer and no more only just the code :Based on this dataset compile a python 3.11 ploty code to work on this query : '{prompt}' just give the asnwer and a graph to visualize dont give anything but code not even the the title python you give dont give that pls ," 
    response = model.generate_content(prompt)
    print(response.text)
    
    text = str(response.text)
    text  = text.lstrip()
    print("Type of string:",type(text))
    if text.startswith("```python"):
        text = text[9:]  # Remove the first 9 characters
        # Alternatively, use replace for multiple occurrences
        text = text.replace("```python", "```").replace("```", "")  # Clean up any remaining backticks
    print(text)
    return text