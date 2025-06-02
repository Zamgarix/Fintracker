"""
Finance Tracker Web Application

To run this application:

1.  **Set up a virtual environment (recommended):**
    python -m venv venv
    # On Windows:
    # venv\Scripts\activate
    # On macOS/Linux:
    # source venv/bin/activate

2.  **Install dependencies:**
    pip install -r requirements.txt

3.  **Run the Flask application:**
    python app.py

4.  **Open your web browser and navigate to:**
    http://127.0.0.1:5000/

This application allows you to upload a CSV file or paste CSV-formatted text
containing financial data (expected columns: 'date', 'category', 'amount', 'type').
It then performs various analyses and displays them on a results page,
including summary statistics, scenario analysis, data visualizations,
and an interactive dashboard.
"""
import io
import pandas as pd
from flask import Flask, render_template, request
import matplotlib
matplotlib.use('Agg') # Use Agg backend for non-GUI environments
import matplotlib.pyplot as plt
import seaborn as sns
import os
import plotly.express as px

app = Flask(__name__)

# Create static directory if it doesn't exist (though typically done outside request flow or at startup)
# For the worker environment, this step is fine here or can be done via a separate tool call if preferred.
if not os.path.exists('static'):
    os.makedirs('static')

def load_data(data_input, is_file):
    # Reads CSV data from an uploaded file object or a string into a pandas DataFrame.
    # Validates the data for UTF-8 encoding and missing values.
    if is_file:
        if not data_input or not data_input.filename:
            raise ValueError("No file provided or file is empty. Please upload a CSV file.")
        source = data_input
    else: # data_input is a string
        if not data_input or not data_input.strip():
            raise ValueError("No text data provided. Please paste CSV data.")
        source = io.StringIO(data_input)

    try:
        df = pd.read_csv(source, encoding='utf-8')
    except UnicodeDecodeError:
        raise ValueError("Encoding Error: The data is not UTF-8 encoded. Please ensure the CSV data is UTF-8.")
    except Exception as e: # Catch other potential pandas parsing errors
        raise ValueError(f"CSV Parsing Error: Could not parse CSV data. Details: {str(e)}")

    if df.isnull().values.any():
        raise ValueError("Data Quality Error: The dataset contains missing values. Please clean the data and try again.")
    return df

def summary_analysis(df):
    # """Provide summary statistics of the data."""
    summary = df.describe()
    return summary

def scenario_analysis(df):
    # """Perform what-if analysis."""
    scenarios = {}
    if 'amount' not in df.columns or 'type' not in df.columns:
        raise ValueError("Dataframe must contain 'amount' and 'type' columns for scenario analysis.")
    
    income_sum = df['amount'][df['type'] == 'income'].sum() if not df[df['type'] == 'income'].empty else 0
    expense_sum = df['amount'][df['type'] == 'expense'].sum() if not df[df['type'] == 'expense'].empty else 0

    scenarios['increase_income'] = income_sum * 1.10
    scenarios['decrease_expense'] = expense_sum * 0.90
    return scenarios

def exploratory_data_analysis(df):
    # """Create various plots and save them as images."""
    plot_filenames = {}
    required_cols = ['category', 'amount', 'type', 'date']
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Dataframe must contain '{col}' column for exploratory data analysis.")

    # Bar plot
    plt.figure()
    sns.barplot(x='category', y='amount', hue='type', data=df)
    plt.title("Income and Expenses by Category")
    plt.xticks(rotation=45)
    plt.tight_layout()
    bar_plot_path = os.path.join('static', 'income_expense_by_category.png')
    plt.savefig(bar_plot_path)
    plt.close()
    plot_filenames['bar_plot'] = 'income_expense_by_category.png'

    # Line plot
    df_copy = df.copy()
    df_copy['date'] = pd.to_datetime(df_copy['date'])
    df_expense = df_copy[df_copy['type'] == 'expense']
    if not df_expense.empty:
        plt.figure()
        df_expense.set_index('date')['amount'].plot()
        plt.title("Expenses Over Time")
        plt.tight_layout()
        line_plot_path = os.path.join('static', 'expenses_over_time.png')
        plt.savefig(line_plot_path)
        plt.close()
        plot_filenames['line_plot'] = 'expenses_over_time.png'
    else:
        plot_filenames['line_plot'] = None
    return plot_filenames

def create_interactive_dashboard(df):
    # """Create an interactive dashboard using Plotly and return its HTML representation."""
    required_cols = ['category', 'amount', 'type']
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Dataframe must contain '{col}' column for the interactive dashboard.")

    fig = px.bar(df, x='category', y='amount', color='type', title="Interactive Income and Expenses by Category")
    dashboard_html = fig.to_html(full_html=False, include_plotlyjs='cdn')
    return dashboard_html

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_data():
    uploaded_file = request.files.get('csv_file')
    pasted_data = request.form.get('csv_text')
    df = None
    summary_df = None
    scenarios_dict = None
    plot_paths_dict = None
    dashboard_html_output = None

    try:
        if uploaded_file and uploaded_file.filename:
            df = load_data(uploaded_file, is_file=True)
        elif pasted_data and pasted_data.strip():
            df = load_data(pasted_data, is_file=False)
        else:
            return render_template('results.html', error="No data provided. Please upload a CSV file or paste CSV data."), 400

        summary_df = summary_analysis(df)
        scenarios_dict = scenario_analysis(df)
        plot_paths_dict = exploratory_data_analysis(df) # This saves plots to static/
        dashboard_html_output = create_interactive_dashboard(df)

        return render_template('results.html',
                               summary_html=summary_df.to_html(classes='table table-striped'),
                               scenarios=scenarios_dict,
                               plots=plot_paths_dict,
                               interactive_dashboard_html=dashboard_html_output,
                               error=None)

    except ValueError as e: # Catches errors from load_data and analysis functions
        return render_template('results.html', error=str(e)), 400
    except Exception as e: # Catch any other unexpected errors
        app.logger.error(f"Unexpected error during analysis: {e}", exc_info=True)
        return render_template('results.html', error="An unexpected server error occurred. Please check logs or contact support."), 500

if __name__ == '__main__':
    app.run(debug=True)
