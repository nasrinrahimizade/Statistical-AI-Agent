import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def prepare_example_plot():
    """
    Create and return a matplotlib figure for the example plot.
    Returns a matplotlib.figure.Figure object that can be passed to plot_view.
    """
    try:
        # Load the all_statistics.csv data
        df = pd.read_csv("data/all_statistics.csv")
        
        # Create a comprehensive plot showing sensor data statistics
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle('Sensor Data Statistics Analysis', fontsize=16)
        
        # Plot 1: Temperature statistics by sample
        temp_data = df[df['channel'] == 'TEMP']
        if not temp_data.empty:
            samples = temp_data['sample'].unique()[:5]  # Limit to first 5 samples
            for sample in samples:
                sample_data = temp_data[temp_data['sample'] == sample]
                ax1.errorbar(range(len(sample_data)), sample_data['mean'], 
                           yerr=sample_data['std'], marker='o', label=sample)
            ax1.set_title('Temperature Statistics by Sample')
            ax1.set_xlabel('Sensor Index')
            ax1.set_ylabel('Temperature (°C)')
            ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            ax1.grid(True, alpha=0.3)
        
        # Plot 2: Humidity statistics by sample
        hum_data = df[df['channel'] == 'HUM']
        if not hum_data.empty:
            samples = hum_data['sample'].unique()[:5]  # Limit to first 5 samples
            for sample in samples:
                sample_data = hum_data[hum_data['sample'] == sample]
                ax2.errorbar(range(len(sample_data)), sample_data['mean'], 
                           yerr=sample_data['std'], marker='s', label=sample)
            ax2.set_title('Humidity Statistics by Sample')
            ax2.set_xlabel('Sensor Index')
            ax2.set_ylabel('Humidity (%)')
            ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            ax2.grid(True, alpha=0.3)
        
        # Plot 3: Acceleration statistics (Z-axis)
        acc_z_data = df[df['channel'] == 'A_z [g]']
        if not acc_z_data.empty:
            samples = acc_z_data['sample'].unique()[:5]  # Limit to first 5 samples
            for sample in samples:
                sample_data = acc_z_data[acc_z_data['sample'] == sample]
                ax3.errorbar(range(len(sample_data)), sample_data['mean'], 
                           yerr=sample_data['std'], marker='^', label=sample)
            ax3.set_title('Z-Axis Acceleration Statistics')
            ax3.set_xlabel('Sensor Index')
            ax3.set_ylabel('Acceleration (g)')
            ax3.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            ax3.grid(True, alpha=0.3)
        
        # Plot 4: Pressure statistics
        press_data = df[df['channel'] == 'PRESS']
        if not press_data.empty:
            samples = press_data['sample'].unique()[:5]  # Limit to first 5 samples
            for sample in samples:
                sample_data = press_data[press_data['sample'] == sample]
                ax4.errorbar(range(len(sample_data)), sample_data['mean'], 
                           yerr=sample_data['std'], marker='d', label=sample)
            ax4.set_title('Pressure Statistics by Sample')
            ax4.set_xlabel('Sensor Index')
            ax4.set_ylabel('Pressure (hPa)')
            ax4.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            ax4.grid(True, alpha=0.3)
        
        # Ensure the figure is properly configured
        fig.tight_layout()
        
        return fig
        
    except FileNotFoundError:
        # Create a placeholder plot if data file is not found
        fig, ax = plt.subplots()
        ax.text(0.5, 0.5, 'Data file not found.\nPlease ensure data/all_statistics.csv exists.', 
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

def prepare_sensor_comparison_plot():
    """
    Create a comparison plot showing different sensors and their statistics
    """
    try:
        df = pd.read_csv("data/all_statistics.csv")
        
        # Get unique sensors
        sensors = df['sensor'].unique()[:6]  # Limit to first 6 sensors
        
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        fig.suptitle('Sensor Data Comparison', fontsize=16)
        
        for i, sensor in enumerate(sensors):
            row = i // 3
            col = i % 3
            ax = axes[row, col]
            
            sensor_data = df[df['sensor'] == sensor]
            
            # Create box plot for mean values
            channels = sensor_data['channel'].unique()
            means = []
            labels = []
            
            for channel in channels:
                channel_data = sensor_data[sensor_data['channel'] == channel]
                if not channel_data.empty:
                    means.append(channel_data['mean'].values)
                    labels.append(channel)
            
            if means:
                ax.boxplot(means, labels=labels)
                ax.set_title(f'{sensor}')
                ax.set_ylabel('Mean Value')
                ax.tick_params(axis='x', rotation=45)
        
        fig.tight_layout()
        return fig
        
    except Exception as e:
        fig, ax = plt.subplots()
        ax.text(0.5, 0.5, f'Error creating sensor comparison:\n{str(e)}', 
                ha='center', va='center', transform=ax.transAxes)
        ax.set_title("Error")
        return fig

def prepare_statistics_summary_plot():
    """
    Create a summary plot showing overall statistics
    """
    try:
        df = pd.read_csv("data/all_statistics.csv")
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle('Data Statistics Summary', fontsize=16)
        
        # Plot 1: Distribution of means
        ax1.hist(df['mean'], bins=30, alpha=0.7, edgecolor='black')
        ax1.set_title('Distribution of Mean Values')
        ax1.set_xlabel('Mean Value')
        ax1.set_ylabel('Frequency')
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Distribution of standard deviations
        ax2.hist(df['std'], bins=30, alpha=0.7, edgecolor='black', color='orange')
        ax2.set_title('Distribution of Standard Deviations')
        ax2.set_xlabel('Standard Deviation')
        ax2.set_ylabel('Frequency')
        ax2.grid(True, alpha=0.3)
        
        # Plot 3: Mean vs Standard Deviation
        ax3.scatter(df['mean'], df['std'], alpha=0.6)
        ax3.set_title('Mean vs Standard Deviation')
        ax3.set_xlabel('Mean Value')
        ax3.set_ylabel('Standard Deviation')
        ax3.grid(True, alpha=0.3)
        
        # Plot 4: Channel types distribution
        channel_counts = df['channel'].value_counts()
        ax4.bar(range(len(channel_counts)), channel_counts.values)
        ax4.set_title('Channel Types Distribution')
        ax4.set_xlabel('Channel Type')
        ax4.set_ylabel('Count')
        ax4.set_xticks(range(len(channel_counts)))
        ax4.set_xticklabels(channel_counts.index, rotation=45)
        ax4.grid(True, alpha=0.3)
        
        fig.tight_layout()
        return fig
        
    except Exception as e:
        fig, ax = plt.subplots()
        ax.text(0.5, 0.5, f'Error creating summary plot:\n{str(e)}', 
                ha='center', va='center', transform=ax.transAxes)
        ax.set_title("Error")
        return fig
