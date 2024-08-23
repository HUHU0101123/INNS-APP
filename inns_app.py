import streamlit as st
import pandas as pd
import plotly.express as px

# Initialize session state to store the last uploaded files
if 'uploaded_file_modules' not in st.session_state:
    st.session_state.uploaded_file_modules = None
if 'uploaded_file_compulsory' not in st.session_state:
    st.session_state.uploaded_file_compulsory = None
if 'uploaded_file_elective_submodules' not in st.session_state:
    st.session_state.uploaded_file_elective_submodules = None
if 'uploaded_file_elective_courses' not in st.session_state:
    st.session_state.uploaded_file_elective_courses = None

st.title('PhD Progress Tracker')

# Provide options to upload new files or use the last uploaded files
file_option = st.radio(
    "Choose file option:",
    ("Upload new files", "Use the last uploaded files")
)

if file_option == "Upload new files":
    uploaded_file_modules = st.file_uploader("Choose the modules CSV file", type="csv", key='modules')
    uploaded_file_compulsory = st.file_uploader("Choose the compulsory courses CSV file", type="csv", key='compulsory')
    uploaded_file_elective_submodules = st.file_uploader("Choose the elective submodules CSV file", type="csv", key='elective_submodules')
    uploaded_file_elective_courses = st.file_uploader("Choose the elective courses CSV file", type="csv", key='elective_courses')

    # If new files are uploaded, update session state
    if all([uploaded_file_modules, uploaded_file_compulsory, uploaded_file_elective_submodules, uploaded_file_elective_courses]):
        st.session_state.uploaded_file_modules = uploaded_file_modules
        st.session_state.uploaded_file_compulsory = uploaded_file_compulsory
        st.session_state.uploaded_file_elective_submodules = uploaded_file_elective_submodules
        st.session_state.uploaded_file_elective_courses = uploaded_file_elective_courses
        st.write("Files uploaded successfully. Processing data...")
    else:
        st.warning("Please upload all CSV files.")
else:
    # Use the last uploaded files from session state
    uploaded_file_modules = st.session_state.uploaded_file_modules
    uploaded_file_compulsory = st.session_state.uploaded_file_compulsory
    uploaded_file_elective_submodules = st.session_state.uploaded_file_elective_submodules
    uploaded_file_elective_courses = st.session_state.uploaded_file_elective_courses

    if all([uploaded_file_modules, uploaded_file_compulsory, uploaded_file_elective_submodules, uploaded_file_elective_courses]):
        st.write("Using the last uploaded files.")
    else:
        st.warning("No previously uploaded files found. Please upload new files.")
        uploaded_file_modules = uploaded_file_compulsory = uploaded_file_elective_submodules = uploaded_file_elective_courses = None

# Load and display data if files are available
if all([uploaded_file_modules, uploaded_file_compulsory, uploaded_file_elective_submodules, uploaded_file_elective_courses]):
    @st.cache_data
    def load_data(file_modules, file_compulsory, file_elective_submodules, file_elective_courses):
        try:
            modules = pd.read_csv(file_modules)
            compulsory_courses = pd.read_csv(file_compulsory)
            elective_submodules = pd.read_csv(file_elective_submodules)
            elective_courses = pd.read_csv(file_elective_courses)
            return modules, compulsory_courses, elective_submodules, elective_courses
        except pd.errors.EmptyDataError:
            st.error("One or more uploaded files are empty or invalid. Please upload valid CSV files.")
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
        except Exception as e:
            st.error(f"Error loading files: {e}")
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    modules, compulsory_courses, elective_submodules, elective_courses = load_data(
        uploaded_file_modules, uploaded_file_compulsory, uploaded_file_elective_submodules, uploaded_file_elective_courses
    )

    if not any(df.empty for df in [modules, compulsory_courses, elective_submodules, elective_courses]):
        st.write("Data loaded successfully. Processing and visualizing...")

        # Calculate total ECTS (excluding dissertation)
        total_ects = modules[modules['module_name'] != 'Dissertation']['required_ects'].sum()

        # Calculate ECTS for compulsory modules
        compulsory_done = compulsory_courses[compulsory_courses['status'] == 'Done']['ects'].sum()
        compulsory_in_progress = compulsory_courses[compulsory_courses['status'] == 'Current Semester']['ects'].sum()
        compulsory_pending = compulsory_courses[compulsory_courses['status'] == 'Not Started']['ects'].sum()

        # Calculate ECTS for elective modules
        elective_done = elective_courses[elective_courses['status'] == 'Done']['ects'].sum()
        elective_in_progress = elective_courses[elective_courses['status'] == 'Current Semester']['ects'].sum()
        
        # Ensure elective ECTS don't exceed 5 per submodule and 10 in total
        elective_done = min(elective_done, 10)
        elective_in_progress = min(elective_in_progress, 10 - elective_done)
        elective_pending = max(0, 10 - elective_done - elective_in_progress)

        # Prepare data for pie chart
        pie_data = pd.DataFrame({
            'Status': ['Done', 'In Progress', 'Pending'],
            'ECTS': [compulsory_done + elective_done, 
                     compulsory_in_progress + elective_in_progress, 
                     compulsory_pending + elective_pending]
        })
        pie_data['Percentage'] = pie_data['ECTS'] / total_ects * 100

        # Create pie chart
        fig_pie = px.pie(
            pie_data,
            names='Status',
            values='Percentage',
            title=f'PhD Progress (Total: {total_ects} ECTS)',
            labels={'Percentage': 'Percentage'},
            height=400
        )
        st.plotly_chart(fig_pie)

        # Display detailed progress
        st.subheader("Detailed Progress")
        st.write(f"Compulsory Modules: {compulsory_done + compulsory_in_progress}/{modules[modules['module_name'] == 'Compulsory Modules']['required_ects'].values[0]} ECTS")
        st.write(f"Elective Modules: {elective_done + elective_in_progress}/{modules[modules['module_name'] == 'Elective Modules']['required_ects'].values[0]} ECTS")

        # Display elective courses progress
        st.subheader("Elective Courses Progress")
        for submodule in elective_submodules['submodule_name']:
            courses = elective_courses[elective_courses['submodule'] == submodule]
            ects_earned = min(courses[courses['status'].isin(['Done', 'Current Semester'])]['ects'].sum(), 5)
            st.write(f"{submodule}: {ects_earned}/5 ECTS")

    else:
        st.warning("Please upload valid CSV files to continue.")
