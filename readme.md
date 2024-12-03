# Visual Data Analyzer

The **Visual Data Analyzer** is a web-based tool that allows users to upload CSV files, ask natural language questions about the dataset, and receive insights along with interactive visualizations. Powered by machine learning and a dynamic charting system, this application provides an intuitive way to explore and visualize datasets. 
This uses the power of Gemini to achive insights and visualizations.

## Features

- **Dataset Upload:** Users can upload CSV files and analyze them.
- **Natural Language Querying:** Ask questions about the data in plain English.
- **Insights Generation:** The app processes the queries and provides relevant answers.
- **Interactive Visualizations:** Automatically generates graphs and charts based on the dataset and query.
- **Chat History:** Track and review previous queries and answers.

## Tech Stack

- **Frontend:** Dash, HTML, CSS, JavaScript
- **Backend:** Flask (for handling queries and processing data)
- **Charting:** Plotly (for creating dynamic graphs and charts)
- **File Handling:** Pandas for managing and processing CSV files
- **APIs:** Gemini API for dynamic querying (customized for natural language processing)

## Setup Instructions

### Prerequisites

Make sure you have Python 3.x installed. You will also need to install the following dependencies.

### Step 1: Clone the Repository

Clone this repository to your local machine:

```bash
git clone https://github.com/The-Gokul-Kishore/Visual_Data_Analyzer.git
cd visual-data-analyzer
```

### Step 2: Create a Virtual Environment (Optional)

It's recommended to use a virtual environment to manage dependencies:

```bash
python -m venv venv
source Dash_llm/bin/activate  # On Windows use `venv\Scripts\activate`
```

### Step 3: Install Dependencies

Install the required Python libraries:

```bash
pip install -r requirements.txt
```

Ensure you have the following libraries:

- `dash`
- `pandas`
- `plotly`
- `requests`
- `flask`
- `google-generativeai`

### Step 4: Running the Backend

Before running the Dash frontend, ensure that the backend Flask server is running. In a separate terminal window, navigate to the project folder and run:

```bash
python backend.py  
```

This will start the Flask server that handles queries and data processing.

### Step 5: Running the Frontend

After the backend is running, start the Dash frontend with the following command:

```bash
python app.py
```

This will launch the web application locally on `http://127.0.0.1:8050`.

### Step 6: Interacting with the Application

1. **Upload CSV Files:** Use the file upload feature to upload your CSV dataset.
2. **Ask Questions:** Type your query in the search bar to get insights from the data.
3. **Visualize Data:** The app will generate charts based on your query and display them dynamically.
4. **View History:** All interactions are logged in the chat history for easy reference.

## File Structure

```
visual-data-analyzer/
│
├── app.py                # Main Dash app script (frontend)
├── backend.py            # Flask backend for data processing and query handling
├── requirements.txt      # List of dependencies
├── main_dataset.csv      # (Optional) Default CSV dataset to load
├── assets/               # Contains static files like images and stylesheets
│   └── styles.css        # Custom CSS for app styling
├── README.md             # Project README
└── data/                 # Folder to store uploaded datasets (optional)
```

