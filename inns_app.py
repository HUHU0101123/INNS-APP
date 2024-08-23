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
        st.write("Data loaded successfully.")

        # Calculate ECTS for compulsory and elective modules
        compulsory_done = compulsory_courses[compulsory_courses['status'] == 'Done']['ects'].sum()
        compulsory_in_progress = compulsory_courses[compulsory_courses['status'] == 'Current Semester']['ects'].sum()
        compulsory_pending = compulsory_courses[compulsory_courses['status'] == 'Not Started']['ects'].sum()
        elective_done = elective_courses[elective_courses['status'] == 'Done']['ects'].sum()
        elective_in_progress = elective_courses[elective_courses['status'] == 'Current Semester']['ects'].sum()
        elective_total = elective_done + elective_in_progress
        elective_pending = max(0, 10 - elective_total)  # Ensure at least 10 ECTS for electives

        # Calculate total ECTS for each category
        total_compulsory = compulsory_done + compulsory_in_progress + compulsory_pending
        total_elective = max(10, elective_done + elective_in_progress + elective_pending)

        # Calculate percentages
        def calculate_percentage(value, total):
            return (value / total * 100) if total > 0 else 0

        compulsory_done_percent = calculate_percentage(compulsory_done, total_compulsory)
        compulsory_in_progress_percent = calculate_percentage(compulsory_in_progress, total_compulsory)
        compulsory_pending_percent = calculate_percentage(compulsory_pending, total_compulsory)
        elective_done_percent = calculate_percentage(elective_done, total_elective)
        elective_in_progress_percent = calculate_percentage(elective_in_progress, total_elective)
        elective_pending_percent = calculate_percentage(elective_pending, total_elective)

        # Display overall completion percentage with a progress bar
        completed_ects = compulsory_done + elective_done
        total_ects = total_compulsory + total_elective
        completion_percentage = (completed_ects / total_ects) * 100 if total_ects > 0 else 0

        st.write("## Overall Completion Percentage")
        st.progress(completion_percentage / 100)

        # Prepare data for the stacked bar chart
        categories = ['Compulsory', 'Elective']
        done_percentages = [compulsory_done_percent, elective_done_percent]
        in_progress_percentages = [compulsory_in_progress_percent, elective_in_progress_percent]
        pending_percentages = [compulsory_pending_percent, elective_pending_percent]

        # Create the stacked bar chart
        try:
            fig_stacked_bar = go.Figure()

            # Add bars for each status
            fig_stacked_bar.add_trace(go.Bar(
                name='Done', x=categories, y=done_percentages,
                text=[f'{p:.1f}%' for p in done_percentages], textposition='inside',
                marker_color='#2ecc71'
            ))
            fig_stacked_bar.add_trace(go.Bar(
                name='In Progress', x=categories, y=in_progress_percentages,
                text=[f'{p:.1f}%' for p in in_progress_percentages], textposition='inside',
                marker_color='#f39c12'
            ))
            fig_stacked_bar.add_trace(go.Bar(
                name='Pending', x=categories, y=pending_percentages,
                text=[f'{p:.1f}%' for p in pending_percentages], textposition='inside',
                marker_color='#e74c3c'
            ))

            # Update layout
            fig_stacked_bar.update_layout(
                barmode='stack',
                title="PhD Progress: Compulsory and Elective Modules",
                yaxis_title="Percentage",
                yaxis=dict(tickformat='.0%', range=[0, 100], visible=False),  # Hide Y axis
                legend_title="Status",
                width=700,
                height=500,
            )

            st.plotly_chart(fig_stacked_bar)

            # Create the dictionary with the data
            summary_data = {
                "Category": ["Compulsory", "Elective", "Total"],
                "Total ECTS": [f"{total_compulsory:.1f}", f"{total_elective:.1f}", f"{total_ects:.1f}"],
                "Completed ECTS": [f"{compulsory_done:.1f}", f"{elective_done:.1f}", f"{completed_ects:.1f}"],
                "Completion Percentage": [f"{compulsory_done_percent:.1f}%", f"{elective_done_percent:.1f}%", f"{completion_percentage:.1f}%"]
            }

            # Create a pandas DataFrame
            summary_df = pd.DataFrame(summary_data)

            # Display the table in Streamlit with improved formatting
            st.write("### Summary Table")
            st.table(summary_df)

        except Exception as e:
            st.error(f"Error creating or displaying percentage stacked bar chart: {e}")
            st.write("Chart data:")
            st.write(pd.DataFrame({
                "Category": categories * 3,
                "Status": ["Done"] * 2 + ["In Progress"] * 2 + ["Pending"] * 2,
                "Percentage": done_percentages + in_progress_percentages + pending_percentages
            }))
    else:
        st.warning("One or more DataFrames are empty. Please check your CSV files.")
else:
    st.warning("Please upload all required CSV files to proceed.")
