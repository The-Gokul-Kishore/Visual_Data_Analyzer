import plotly
import plotly.express as px
import plotly.io as pio
import json


string = """\nimport pandas as pd\nimport plotly.graph_objs as go\nfrom plotly.subplots import make_subplots\n\n# Load the dataset\ndf = pd.read_csv(\"sample_data.csv\")\n\n#1. Top Flight Carriers (Bar Chart)\n\n#Calculate the counts of each airline\nairline_counts = df['Airline'].value_counts()\n\nfig1 = go.Figure(data=[go.Bar(x=airline_counts.index, y=airline_counts.values)])\nfig1.update_layout(title='Top Flight Carriers',\n                   xaxis_title='Airline',\n                   yaxis_title='Number of Flights')\n\n\n# Create the dashboard\nfig = make_subplots(rows=1, cols=1,\n                    subplot_titles=('Top Flight Carriers'))\n\nfig.add_trace(fig1.data[0], row=1, col=1)\n\n\nfig.update_layout(height=600, width=800, title_text=\"Flight Dashboard\")\nfig.show()\n\n\n"""

try:
        # Assume the generated code returns a Plotly figure `fig`
        exec(string)

        # If the figure is created successfully, return the graph's JSON data
        if 'fig' in locals():
            graph_html = pio.to_html(fig, full_html=False)  # Generates HTML representation of the plot
            print(graph_html)
            
            plot_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
except Exception as e:
         print(e)