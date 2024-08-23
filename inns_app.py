import streamlit as st
import pandas as pd
import plotly.express as px

# Initialize session state to store the last uploaded file
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None

st.title('PhD Progress Tracker')

# Provide an option to upload a new file or use the last uploaded file
file_option = st.radio(
    "Choose file option:",
    ("Upload a new file", "Use the last uploaded file")
)

if file_option == "Upload a new file":
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    # If a new file is uploaded, update session state
    if uploaded_file is not None:
        st.session_state.uploaded_file = uploaded_file
else:
    # Use the last uploaded file from session state
    uploaded_file = st.session_state.uploaded_file
    if uploaded_file:
        st.write("Using the last uploaded file.")
    else:
        st.warning("No previously uploaded file found. Please upload a new file.")
        uploaded_file = None

# Load and display data if a file is available
if uploaded_file is not None:
    # Load data from the uploaded file
    @st.cache_data
    def load_data(file):
        try:
            # Attempt to load the data using the correct delimiter and encoding
            modules = pd.read_csv(file, delimiter=',', encoding='utf-8')
            # Remove any leading/trailing whitespace from column names
            modules.columns = modules.columns.str.strip()
            return modules
        except Exception as e:
            st.error(f"Error loading file: {e}")
            return pd.DataFrame()

    modules = load_data(uploaded_file)
    
    if not modules.empty:
        # Rest of your code for data processing and visualization goes here
        # ...

    else:
        st.warning("Please upload a valid CSV file to continue.")
