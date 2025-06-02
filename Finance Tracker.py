import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import os


def get_csv_directory():
    """
    Prompt the user for the CSV file location and return the directory path.
    """
    file_path = input("Please provide the directory path of the CSV file: ")
    if not os.path.isfile(file_path):
        raise FileNotFoundError("The provided file path does not exist.")
    # Note: If you encounter errors with file paths containing special non-ASCII characters,
    # please ensure your operating system's locale is configured to support UTF-8.
    # Alternatively, try using file paths that only contain standard ASCII characters.
    return file_path


def load_data(file_path):
    """
    Read the CSV file into a pandas DataFrame and validate the data.
    """
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
    except FileNotFoundError:
        raise FileNotFoundError("Error: The file was not found at the specified path. Please check the path and try again.")
    except UnicodeDecodeError:
        raise ValueError("Error: The file is not encoded in UTF-8. Please ensure the CSV file is saved with UTF-8 encoding and try again.")
    # Check for missing values
    if df.isnull().values.any():
        raise ValueError("The dataset contains missing values. Please clean the data and try again.")
    return df


def summary_analysis(df):
    """
    Provide summary statistics of the data.
    """
    summary = df.describe()
    print("Summary Analysis:\n", summary)
    summary.to_csv("summary_analysis.csv")
    return summary


def scenario_analysis(df):
    """
    Perform what-if analysis.
    """
    scenarios = {}
    scenarios['increase_income'] = df['amount'][df['type'] == 'income'].sum() * 1.10
    scenarios['decrease_expense'] = df['amount'][df['type'] == 'expense'].sum() * 0.90
    print("Scenario Analysis:\n", scenarios)
    with open("scenario_analysis.csv", "w", encoding="utf-8") as f:
        for key, value in scenarios.items():
            f.write(f"{key},{value}\n")
    return scenarios


def exploratory_data_analysis(df):
    """
    Create various plots and save them as images.
    """
    # Bar plot of income and expenses
    sns.barplot(x='category', y='amount', hue='type', data=df)
    plt.title("Income and Expenses by Category")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("income_expense_by_category.png")
    plt.close()

    # Line plot of expenses over time
    df['date'] = pd.to_datetime(df['date'])
    df_expense = df[df['type'] == 'expense']
    df_expense.set_index('date')['amount'].plot()
    plt.title("Expenses Over Time")
    plt.tight_layout()
    plt.savefig("expenses_over_time.png")
    plt.close()


def create_interactive_dashboard(df):
    """
    Create an interactive dashboard using Plotly.
    """
    fig = px.bar(df, x='category', y='amount', color='type', title="Interactive Income and Expenses by Category")
    fig.show()

    # Save interactive dashboard as HTML
    fig.write_html("interactive_dashboard.html")


def main():
    """
    Main function to orchestrate the workflow.
    """
    try:
        file_path = get_csv_directory()
        df = load_data(file_path)

        summary = summary_analysis(df)
        scenarios = scenario_analysis(df)
        exploratory_data_analysis(df)
        create_interactive_dashboard(df)

        print("Dashboard and analysis files created successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
