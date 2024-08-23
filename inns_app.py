import streamlit as st
import pandas as pd
import plotly.graph_objects as go

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
        st.write("Data loaded successfully. Let's explore your PhD progress!")

        # Debug information
        st.write("## Debug Information")
        st.write(f"Modules shape: {modules.shape}")
        st.write(f"Compulsory courses shape: {compulsory_courses.shape}")
        st.write(f"Elective submodules shape: {elective_submodules.shape}")
        st.write(f"Elective courses shape: {elective_courses.shape}")

        # Calculate ECTS for compulsory and elective modules
        compulsory_done = compulsory_courses[compulsory_courses['status'] == 'Done']['ects'].sum()
        compulsory_in_progress = compulsory_courses[compulsory_courses['status'] == 'Current Semester']['ects'].sum()
        compulsory_pending = compulsory_courses[compulsory_courses['status'] == 'Not Started']['ects'].sum()

        elective_done = elective_courses[elective_courses['status'] == 'Done']['ects'].sum()
        elective_in_progress = elective_courses[elective_courses['status'] == 'Current Semester']['ects'].sum()
        elective_pending = elective_courses[elective_courses['status'] == 'Not Started']['ects'].sum()

        # More debug information
        st.write("## ECTS Calculations")
        st.write(f"Compulsory done: {compulsory_done}")
        st.write(f"Compulsory in progress: {compulsory_in_progress}")
        st.write(f"Compulsory pending: {compulsory_pending}")
        st.write(f"Elective done: {elective_done}")
        st.write(f"Elective in progress: {elective_in_progress}")
        st.write(f"Elective pending: {elective_pending}")

        # Prepare data for the sunburst chart
        labels = [
            "PhD Progress", "Compulsory Modules", "Elective Modules",
            "Compulsory Done", "Compulsory In Progress", "Compulsory Pending",
            "Elective Done", "Elective In Progress", "Elective Pending"
        ]
        parents = [
            "", "PhD Progress", "PhD Progress",
            "Compulsory Modules", "Compulsory Modules", "Compulsory Modules",
            "Elective Modules", "Elective Modules", "Elective Modules"
        ]
        values = [
            1,  # PhD Progress (root)
            compulsory_done + compulsory_in_progress + compulsory_pending,  # Compulsory Modules
            elective_done + elective_in_progress + elective_pending,  # Elective Modules
            compulsory_done, compulsory_in_progress, compulsory_pending,
            elective_done, elective_in_progress, elective_pending
        ]

        # Prepare data for the Treemap chart
        labels = [
            "PhD Progress", 
            "Compulsory Modules", "Elective Modules",
            "Compulsory Done", "Compulsory In Progress", "Compulsory Pending",
            "Elective Done", "Elective In Progress", "Elective Pending"
        ]
        parents = [
            "", 
            "PhD Progress", "PhD Progress",
            "Compulsory Modules", "Compulsory Modules", "Compulsory Modules",
            "Elective Modules", "Elective Modules", "Elective Modules"
        ]
        values = [
            compulsory_done + compulsory_in_progress + compulsory_pending + elective_done + elective_in_progress + elective_pending,
            compulsory_done + compulsory_in_progress + compulsory_pending,
            elective_done + elective_in_progress + elective_pending,
            compulsory_done, compulsory_in_progress, compulsory_pending,
            elective_done, elective_in_progress, elective_pending
        ]

        # Create the Treemap chart
        try:
            st.write("Attempting to create Treemap chart...")
            fig_treemap = go.Figure(go.Treemap(
                labels=labels,
                parents=parents,
                values=values,
                textinfo="label+value",
                hoverinfo="label+value+percent parent+percent root",
                marker=dict(
                    colorscale='Viridis'
                ),
            ))

            fig_treemap.update_layout(
                title="PhD Progress: Compulsory and Elective Modules",
                width=700,
                height=700,
            )

            st.write("Treemap chart created successfully. Attempting to display...")
            st.plotly_chart(fig_treemap)
            st.write("Treemap chart should be displayed above.")
        except Exception as e:
            st.error(f"Error creating or displaying Treemap chart: {e}")
            st.write("Chart data:")
            st.write(pd.DataFrame({"labels": labels, "parents": parents, "values": values}))

        # Add a simple bar chart as a fallback
        st.write("Displaying a simple bar chart as a fallback:")
        bar_data = pd.DataFrame({
            'Category': ['Compulsory Done', 'Compulsory In Progress', 'Compulsory Pending', 
                         'Elective Done', 'Elective In Progress', 'Elective Pending'],
            'ECTS': [compulsory_done, compulsory_in_progress, compulsory_pending, 
                     elective_done, elective_in_progress, elective_pending]
        })
        st.bar_chart(bar_data.set_index('Category'))

    else:
        st.warning("One or more DataFrames are empty. Please check your CSV files.")
else:
    st.warning("Please upload all required CSV files to proceed.")

# Add Plotly version information
import plotly
st.write(f"Plotly version: {plotly.__version__}")
