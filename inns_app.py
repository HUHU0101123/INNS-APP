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

        # Calculate ECTS for compulsory and elective modules
        compulsory_done = compulsory_courses[compulsory_courses['status'] == 'Done']['ects'].sum()
        compulsory_in_progress = compulsory_courses[compulsory_courses['status'] == 'Current Semester']['ects'].sum()
        compulsory_pending = compulsory_courses[compulsory_courses['status'] == 'Not Started']['ects'].sum()

        elective_done = min(elective_courses[elective_courses['status'] == 'Done']['ects'].sum(), 10)
        elective_in_progress = min(elective_courses[elective_courses['status'] == 'Current Semester']['ects'].sum(), 10 - elective_done)
        elective_pending = max(0, 10 - elective_done - elective_in_progress)

        # Create data for the sunburst chart
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
            0,  # PhD Progress (root)
            compulsory_done + compulsory_in_progress + compulsory_pending,  # Compulsory Modules
            elective_done + elective_in_progress + elective_pending,  # Elective Modules
            compulsory_done, compulsory_in_progress, compulsory_pending,
            elective_done, elective_in_progress, elective_pending
        ]

        # Create the sunburst chart
        fig_sunburst = go.Figure(go.Sunburst(
            labels=labels,
            parents=parents,
            values=values,
            branchvalues="total",
            textinfo="label+value",
            insidetextorientation='radial'
        ))

        fig_sunburst.update_layout(
            title="PhD Progress: Compulsory and Elective Modules",
            width=700,
            height=700,
        )

        st.plotly_chart(fig_sunburst)

        # Storytelling
        st.subheader("Your PhD Journey So Far")
        total_done = compulsory_done + elective_done
        total_in_progress = compulsory_in_progress + elective_in_progress
        total_pending = compulsory_pending + elective_pending
        
        if total_ects > 0:
            st.write(f"You've completed {total_done:.1f} ECTS out of the required {total_ects} ECTS, which is {(total_done/total_ects)*100:.1f}% of your coursework.")
        else:
            st.write("Total ECTS required is not defined. Please check your data.")
        
        st.write(f"Currently, you're working on {total_in_progress:.1f} ECTS, and have {total_pending:.1f} ECTS pending.")
        
        if total_done > (total_ects / 2):
            st.write("Great job! You're more than halfway through your coursework.")
        elif total_done + total_in_progress > (total_ects / 2):
            st.write("You're making good progress. Keep up the good work!")
        else:
            st.write("You're in the early stages of your PhD journey. Stay focused and keep moving forward!")

        # Display detailed progress table
        st.subheader("Detailed Progress")
        progress_table = pd.DataFrame({
            'Module': ['Compulsory Modules', 'Elective Modules'],
            'Done': [compulsory_done, elective_done],
            'In Progress': [compulsory_in_progress, elective_in_progress],
            'Pending': [compulsory_pending, elective_pending],
            'Total Required': [22.5, 10]
        })
        progress_table['Completion %'] = (progress_table['Done'] / progress_table['Total Required']) * 100
        st.table(progress_table.style.format({'Done': '{:.1f}', 'In Progress': '{:.1f}', 'Pending': '{:.1f}', 'Completion %': '{:.1f}%'}))

        # Display elective courses progress
        st.subheader("Elective Courses Progress")
        fig_electives = go.Figure()
        for submodule in elective_submodules['submodule_name']:
            courses = elective_courses[elective_courses['submodule'] == submodule]
            ects_earned = min(courses[courses['status'].isin(['Done', 'Current Semester'])]['ects'].sum(), 5)
            fig_electives.add_trace(go.Bar(
                x=[submodule],
                y=[ects_earned],
                name=submodule,
                text=[f"{ects_earned}/5 ECTS"],
                textposition='auto'
            ))
        fig_electives.update_layout(
            title="Elective Submodules Progress",
            xaxis_title="Submodule",
            yaxis_title="ECTS Earned",
            yaxis_range=[0, 5],
            height=400
        )
        st.plotly_chart(fig_electives)

        # Advice based on progress
        st.subheader("Next Steps")
        if elective_done + elective_in_progress < 10:
            st.write("Consider enrolling in more elective courses to reach the required 10 ECTS.")
        if compulsory_done + compulsory_in_progress < 22.5:
            st.write("Focus on completing your remaining compulsory modules.")
        if total_done + total_in_progress >= total_ects:
            st.write("Great job on your coursework! It's time to focus on your dissertation.")

    else:
        st.warning("Please upload valid CSV files to continue.")
else:
    st.warning("Please upload all required CSV files to proceed.")
