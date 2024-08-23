import streamlit as st
import pandas as pd
import plotly.express as px

# Initialize session state to store the last uploaded file
if 'uploaded_file_modules' not in st.session_state:
    st.session_state.uploaded_file_modules = None
if 'uploaded_file_submodules' not in st.session_state:
    st.session_state.uploaded_file_submodules = None

st.title('PhD Progress Tracker')

# Provide options to upload new files or use the last uploaded files
file_option = st.radio(
    "Choose file option:",
    ("Upload new files", "Use the last uploaded files")
)

if file_option == "Upload new files":
    uploaded_file_modules = st.file_uploader("Choose the modules CSV file", type="csv", key='modules')
    uploaded_file_submodules = st.file_uploader("Choose the submodules CSV file", type="csv", key='submodules')

    # If new files are uploaded, update session state
    if uploaded_file_modules is not None and uploaded_file_submodules is not None:
        st.session_state.uploaded_file_modules = uploaded_file_modules
        st.session_state.uploaded_file_submodules = uploaded_file_submodules
        st.write("Files uploaded successfully. Processing data...")
    else:
        st.warning("Please upload both CSV files.")
else:
    # Use the last uploaded files from session state
    uploaded_file_modules = st.session_state.uploaded_file_modules
    uploaded_file_submodules = st.session_state.uploaded_file_submodules

    if uploaded_file_modules and uploaded_file_submodules:
        st.write("Using the last uploaded files.")
    else:
        st.warning("No previously uploaded files found. Please upload new files.")
        uploaded_file_modules = None
        uploaded_file_submodules = None

# Load and display data if files are available
if uploaded_file_modules is not None and uploaded_file_submodules is not None:
    @st.cache_data
    def load_data(file_modules, file_submodules):
        try:
            # Load the modules and submodules data
            modules = pd.read_csv(file_modules)
            submodules = pd.read_csv(file_submodules)
            return modules, submodules
        except pd.errors.EmptyDataError:
            st.error("One or both uploaded files are empty or invalid. Please upload valid CSV files.")
            return pd.DataFrame(), pd.DataFrame()
        except Exception as e:
            st.error(f"Error loading files: {e}")
            return pd.DataFrame(), pd.DataFrame()

    modules, submodules = load_data(uploaded_file_modules, uploaded_file_submodules)

    if not modules.empty and not submodules.empty:
        # Process and visualize data
        st.write("Data loaded successfully. Ready for processing and visualization.")
        
        # Summarize the total ECTS for each main module
        main_module_summary = modules[['module_name', 'current_ects']].copy()
        main_module_summary = main_module_summary.rename(columns={'module_name': 'Category', 'current_ects': 'ECTS'})
        main_module_summary['Percentage'] = main_module_summary['ECTS'] / main_module_summary['ECTS'].sum() * 100
        main_module_summary['Label'] = main_module_summary.apply(lambda x: f"{x['Category']} ({x['ECTS']} ECTS)", axis=1)
        
        # Pie chart of main modules progress
        fig_pie = px.pie(
            main_module_summary,
            names='Label',
            values='Percentage',
            title='Progress Distribution of Main Modules (Excluding Dissertation)',
            labels={'Percentage': 'Percentage'},
            height=400
        )
        st.plotly_chart(fig_pie)
        
        # Summarize the ECTS for each sub-module
        submodule_summary = submodules[['submodule_name', 'parent_module', 'current_ects']].copy()
        submodule_summary = submodule_summary.rename(columns={'submodule_name': 'Sub-module', 'current_ects': 'ECTS'})
        
        # Filter sub-modules for elective modules
        elective_submodules = submodule_summary[submodule_summary['parent_module'] == 'Elective Modules']
        
        # Bar chart of elective sub-modules progress
        fig_bar = px.bar(
            elective_submodules,
            x='Sub-module',
            y='ECTS',
            title='ECTS Earned in Elective Sub-modules',
            labels={'ECTS': 'ECTS'},
            height=400
        )
        st.plotly_chart(fig_bar)
        
        # Additional visualizations and summaries can be added here

    else:
        st.warning("Please upload valid CSV files to continue.")
