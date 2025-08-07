import matplotlib.pyplot as plt
import pandas as pd

def prepare_example_plot():
    """
    Create and return a matplotlib figure for the example plot.
    Returns a matplotlib.figure.Figure object that can be passed to plot_view.
    """
    try:
        # Just a simple CSV and plot for test
        df = pd.read_csv("data/sales.csv")  # Replace with your test CSV
        months = df["Month"]
        sales = df["Sales"]

        fig, ax = plt.subplots()
        ax.plot(months, sales, marker="o")
        ax.set_title("Monthly Sales")
        ax.set_xlabel("Month")
        ax.set_ylabel("Sales")
        
        # Ensure the figure is properly configured
        fig.tight_layout()
        
        return fig
        
    except FileNotFoundError:
        # Create a placeholder plot if data file is not found
        fig, ax = plt.subplots()
        ax.text(0.5, 0.5, 'Data file not found.\nPlease ensure data/sales.csv exists.', 
                ha='center', va='center', transform=ax.transAxes)
        ax.set_title("No Data Available")
        return fig
        
    except Exception as e:
        # Create an error plot
        fig, ax = plt.subplots()
        ax.text(0.5, 0.5, f'Error loading plot:\n{str(e)}', 
                ha='center', va='center', transform=ax.transAxes)
        ax.set_title("Error")
        return fig
