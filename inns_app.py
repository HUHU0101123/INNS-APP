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

    @st.cache_data
    def load_data(file):
        try:
            # Attempt to load the data using the correct delimiter and encoding
            modules = pd.read_csv(file, delimiter=',', encoding='utf-8')
            # Remove any leading/trailing whitespace from column names
            modules.columns = modules.columns.str.strip()
            return modules
        except pd.errors.EmptyDataError:
            st.error("The uploaded file is empty or invalid. Please upload a valid CSV file.")
            return pd.DataFrame()  # Return an empty DataFrame
        except UnicodeDecodeError:
            st.warning("UnicodeDecodeError: Trying with a different encoding (ISO-8859-1).")
            try:
                # Try reading with a different encoding
                modules = pd.read_csv(file, delimiter=';', encoding='ISO-8859-1')
                modules.columns = modules.columns.str.strip()
                return modules
            except pd.errors.EmptyDataError:
                st.error("The uploaded file is empty or invalid after trying with ISO-8859-1. Please check the file content.")
                return pd.DataFrame()  # Return an empty DataFrame
            except pd.errors.ParserError:
                st.error("ParserError: The uploaded file could not be parsed. Please check the file content and format.")
                return pd.DataFrame()  # Return an empty DataFrame
            except Exception as e:
                st.error(f"Failed to load file with different encoding. Error: {e}")
                return pd.DataFrame()  # Return an empty DataFrame

    modules = load_data(uploaded_file)

    if not modules.empty:
        # Ensure necessary columns are present
        required_columns = {'current_ects', 'module_name', 'required_ects', 'status', 'notes'}
        if required_columns.issubset(modules.columns):
            # Your existing code for data processing and visualization goes here
            st.write("Data loaded successfully. Ready for processing and visualization.")
            # For example, you might add:
            # st.dataframe(modules)
            # total_ects_earned = modules['current_ects'].sum()
            # st.write(f"Total ECTS earned: {total_ects_earned}")
        else:
            st.error("The uploaded CSV file is missing one or more required columns. Please ensure it contains 'current_ects', 'module_name', 'required_ects', 'status', and 'notes'.")
            st.write("Available columns:", modules.columns.tolist())
    else:
        st.warning("Please upload a CSV file to continue.")
