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
            modules = pd.read_csv(file, delimiter=',', encoding='utf-8')
            modules.columns = modules.columns.str.strip()
            return modules
        except pd.errors.EmptyDataError:
            st.error("The uploaded file is empty or invalid. Please upload a valid CSV file.")
            return pd.DataFrame()  # Return an empty DataFrame
        except UnicodeDecodeError:
            st.warning("UnicodeDecodeError: Trying with a different encoding (ISO-8859-1).")
            try:
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
            # Data processing and visualization
            st.write("Data loaded successfully. Ready for processing and visualization.")
            
            # Define main modules and their sub-modules
            main_modules = {
                "Compulsory Modules": ["Methodologische Grundlagen", "Quantitative Foschungsmethoden", "Qualitative Forschungsmethoden", "Professionelle Development", "Verteidigung der Dissertation"],
                "Elective Modules": ["Generic Competences", "Specific Research Methods", "PhD Research Seminar", "Scientific Discourse"],
                "Dissertation": []
            }
            
            # Initialize dictionary to store total ECTS for each category
            total_ects = {
                "Compulsory Modules": 0,
                "Elective Modules": 0,
                "Dissertation": 0
            }
            
            # Initialize dictionary to store ECTS for elective sub-modules
            elective_ects = {
                "Generic Competences": 0,
                "Specific Research Methods": 0,
                "PhD Research Seminar": 0,
                "Scientific Discourse": 0
            }
            
            # Create a DataFrame for progress summary
            progress_summary = pd.DataFrame(columns=['Category', 'Progress', 'ECTS'])
            
            # Calculate total ECTS for compulsory modules
            compulsory_data = modules[modules['module_name'].isin(main_modules["Compulsory Modules"])]
            total_ects["Compulsory Modules"] = compulsory_data['current_ects'].sum()
            
            # Calculate total ECTS for dissertation
            dissertation_data = modules[modules['module_name'] == "Dissertation"]
            total_ects["Dissertation"] = dissertation_data['current_ects'].sum()
            
            # Process elective modules
            elective_data = modules[modules['module_name'].isin(main_modules["Elective Modules"])]
            
            # Calculate ECTS for each sub-module within Elective Modules
            for module in main_modules["Elective Modules"]:
                module_data = elective_data[elective_data['module_name'] == module]
                sub_module_ects = module_data['current_ects'].sum()
                elective_ects[module] = min(sub_module_ects, 5)  # Each sub-module can have a max of 5 ECTS
            
            # Calculate total ECTS for all elective modules, respecting the max total of 10 ECTS
            total_elective_ects = sum(elective_ects.values())
            total_elective_ects = min(total_elective_ects, 10)
            
            # Update total ECTS for Elective Modules category
            total_ects["Elective Modules"] = total_elective_ects
            
            # Append progress for each category
            for category, ects in total_ects.items():
                progress_summary = progress_summary.append({
                    'Category': category,
                    'Progress': 'Total',
                    'ECTS': ects
                }, ignore_index=True)
            
            # Calculate progress percentages
            progress_summary['Percentage'] = progress_summary['ECTS'] / progress_summary['ECTS'].max() * 100
            progress_summary['Label'] = progress_summary.apply(
                lambda x: f"{x['Category']} ({x['ECTS']} ECTS)",
                axis=1
            )
            
            # Pie chart
            fig_pie = px.pie(
                progress_summary,
                names='Label',
                values='Percentage',
                title='Progress Distribution (Excluding Dissertation)',
                labels={'Percentage': 'Percentage'},
                height=400
            )
            st.plotly_chart(fig_pie)

            # Total ECTS Earned vs. Required
            fig1 = px.bar(modules, x='module_name', y=['current_ects', 'required_ects'],
                          title='ECTS Earned vs. Required',
                          labels={'value': 'ECTS', 'variable': 'Type'},
                          height=400)
            st.plotly_chart(fig1)

            # Status Distribution
            status_counts = modules['status'].value_counts().reset_index()
            status_counts.columns = ['Status', 'Count']
            fig2 = px.bar(status_counts, x='Status', y='Count',
                          title='Status Distribution',
                          height=400)
            st.plotly_chart(fig2)
        else:
            st.error("The uploaded CSV file is missing one or more required columns. Please ensure it contains 'current_ects', 'module_name', 'required_ects', 'status', and 'notes'.")
            st.write("Available columns:", modules.columns.tolist())
    else:
        st.warning("Please upload a CSV file to continue.")
