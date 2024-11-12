import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import timedelta

# Load data from file upload or default CSV
def load_data(file=None):
    if file is not None:
        # Load the user-uploaded file
        data = pd.read_csv(file)
    else:
        # Load the default CSV file
        data = pd.read_csv("activity_subset_data_v2.csv")

    data['startTime'] = pd.to_datetime(data['startTime'])
    data['endTime'] = pd.to_datetime(data['endTime'])
    
    # Create 'person_id' column if it doesn't exist
    if 'person_id' not in data.columns:
        data['person_id'] = data['id'].astype(str) + '-' + data['member'].astype(str)
    
    return data

# Streamlit UI for file upload
st.title("Activity Timeline Viewer")
st.write("Upload a CSV file with `id`, `member`, `startTime`, `endTime`, and `activityName` columns, or use the default data.")

# File uploader widget
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

# Load data based on the uploaded file or default file
data = load_data(uploaded_file)

# Helper function to plot timeline for a selected person_id
def plot_timeline(person_data):
    # Define the start and end boundaries for the timeline
    start_day = person_data['startTime'].min().normalize() + timedelta(hours=4)
    end_day = start_day + timedelta(days=1) - timedelta(minutes=1)
    
    fig, ax = plt.subplots(figsize=(12, 2))
    previous_end_time = None
    
    for row in person_data.itertuples():
        start_time = row.startTime
        end_time = row.endTime
        activity_name = row.activityName.split('(')[0].strip()
        
        # Plot gap if there's a time difference
        if previous_end_time and start_time > previous_end_time:
            ax.plot([previous_end_time, start_time], [1, 1], color='red', linewidth=6)
        
        # Plot activity duration
        ax.plot([start_time, end_time], [1, 1], color='blue', linewidth=6)
        ax.text(start_time, 1.03, activity_name, ha='right', va='bottom', fontsize=8, rotation=90)
        
        previous_end_time = end_time
    
    # Set axis limits to the defined time range
    ax.set_xlim(start_day, end_day)
    ax.set_ylim(0.95, 1.05)
    ax.set_yticks([])
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
    plt.xticks(rotation=90)
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    
    st.pyplot(fig)

# Dropdown to select person_id
if 'person_id' in data.columns:
    unique_person_ids = data['person_id'].unique()
    selected_person_id = st.selectbox("Choose person_id:", unique_person_ids)

    # Filter data for the selected person_id and plot timeline
    if selected_person_id:
        person_data = data[data['person_id'] == selected_person_id]
        plot_timeline(person_data)
else:
    st.error("Uploaded file must contain `id`, `member`, `startTime`, `endTime`, and `activityName` columns.")
