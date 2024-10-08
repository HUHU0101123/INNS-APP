import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.title('PhD Progress Tracker')

# Function to load data from CSV files in the repository
@st.cache_data
def load_data():
    try:
        modules = pd.read_csv("modules.csv")
        compulsory_courses = pd.read_csv("compulsory_courses.csv")
        elective_submodules = pd.read_csv("elective_submodules.csv")
        elective_courses = pd.read_csv("elective_courses.csv")
        return modules, compulsory_courses, elective_submodules, elective_courses
    except FileNotFoundError as e:
        st.error(f"File not found: {e.filename}")
        return None, None, None, None
    except pd.errors.EmptyDataError:
        st.error("One or more files are empty or invalid.")
        return None, None, None, None
    except Exception as e:
        st.error(f"Error loading files: {e}")
        return None, None, None, None

# Load data
modules, compulsory_courses, elective_submodules, elective_courses = load_data()

if all([df is not None for df in [modules, compulsory_courses, elective_submodules, elective_courses]]):
    

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
    st.write(f"**{completion_percentage:.1f}% Complete**")  # Display percentage
    st.progress(completion_percentage / 100)

    # Prepare data for the stacked bar chart
    categories = ['Compulsory', 'Elective']
    done_percentages = [compulsory_done_percent, elective_done_percent]
    in_progress_percentages = [compulsory_in_progress_percent, elective_in_progress_percent]
    pending_percentages = [compulsory_pending_percent, elective_pending_percent]

    # Calculate the number of courses for each category and status
    compulsory_done_count = compulsory_courses[compulsory_courses['status'] == 'Done'].shape[0]
    compulsory_in_progress_count = compulsory_courses[compulsory_courses['status'] == 'Current Semester'].shape[0]
    compulsory_pending_count = compulsory_courses[compulsory_courses['status'] == 'Not Started'].shape[0]
    elective_done_count = elective_courses[elective_courses['status'] == 'Done'].shape[0]
    elective_in_progress_count = elective_courses[elective_courses['status'] == 'Current Semester'].shape[0]
    elective_pending_count = elective_courses[elective_courses['status'] == 'Not Started'].shape[0]
    
    # Create the stacked bar chart
    fig_stacked_bar = go.Figure()
    
    fig_stacked_bar.add_trace(go.Bar(
        name='Done', x=categories, y=done_percentages,
        text=[f'{compulsory_done_percent:.1f}%<br>({compulsory_done_count} courses)', 
              f'{elective_done_percent:.1f}%<br>({elective_done_count} courses)'],
        textposition='inside',
        marker_color='#2ecc71'
    ))
    fig_stacked_bar.add_trace(go.Bar(
        name='In Progress', x=categories, y=in_progress_percentages,
        text=[f'{compulsory_in_progress_percent:.1f}%<br>({compulsory_in_progress_count} courses)', 
              f'{elective_in_progress_percent:.1f}%<br>({elective_in_progress_count} courses)'],
        textposition='inside',
        marker_color='#f39c12'
    ))
    fig_stacked_bar.add_trace(go.Bar(
        name='Pending', x=categories, y=pending_percentages,
        text=[f'{compulsory_pending_percent:.1f}%<br>({compulsory_pending_count} courses)', 
              f'{elective_pending_percent:.1f}%<br>({elective_pending_count} courses)'],
        textposition='inside',
        marker_color='#e74c3c'
    ))
    
    fig_stacked_bar.update_layout(
        barmode='stack',
        title="Compulsory and Elective Modules",
        yaxis_title="Percentage",
        yaxis=dict(tickformat='.0%', range=[0, 100], visible=False),  # Hide Y axis
        legend_title="Status",
        width=700,
        height=500,
    )
    
    st.plotly_chart(fig_stacked_bar)

    # Define summary_data for the summary table
    summary_data = {
        "Category": ["Compulsory", "Elective", "Total"],
        "Total ECTS": [total_compulsory, max(10, elective_done + elective_in_progress + elective_pending), total_compulsory + total_elective],
        "Completed ECTS": [compulsory_done, elective_done, completed_ects],
        "Completion Percentage": [compulsory_done_percent, elective_done_percent, completion_percentage]
    }

    # Create the summary DataFrame
    summary_df = pd.DataFrame(summary_data)

    # Custom CSS to style the table
    st.markdown("""
    <style>
        .dataframe thead th {
            background-color: #4CAF50; /* Green background */
            color: white; /* White text */
            text-align: center; /* Center align text */
            font-weight: bold; /* Bold text */
            border: 1px solid #ddd; /* Light grey border */
        }
        .dataframe tbody tr:nth-child(even) {
            background-color: #f2f2f2; /* Light grey for even rows */
        }
        .dataframe tbody tr:nth-child(odd) {
            background-color: #ffffff; /* White for odd rows */
        }
        .dataframe tbody tr:hover {
            background-color: #ddd; /* Light grey on hover */
        }
        .dataframe td {
            text-align: center; /* Center align text in cells */
            padding: 10px; /* Padding around text */
            border: 1px solid #ddd; /* Light grey border for cells */
        }
        .dataframe {
            border-collapse: collapse; /* Collapse borders */
            width: 100%; /* Full width */
        }
    </style>
    """, unsafe_allow_html=True)

    # Apply styling to the DataFrame without conditional formatting
    styled_df = summary_df.style \
        .format({
            'Total ECTS': '{:.1f}',
            'Completed ECTS': '{:.1f}',
            'Completion Percentage': '{:.1f}%'
        }) \
        .set_table_styles([{
            'selector': 'thead th',
            'props': [('background-color', '#4CAF50'), ('color', 'white'), ('font-weight', 'bold'), ('text-align', 'center')]
        }, {
            'selector': 'tbody tr:nth-child(even)',
            'props': [('background-color', '#f2f2f2')]
        }, {
            'selector': 'tbody tr:nth-child(odd)',
            'props': [('background-color', '#ffffff')]
        }, {
            'selector': 'tbody tr:hover',
            'props': [('background-color', '#ddd')]
        }, {
            'selector': 'td',
            'props': [('text-align', 'center'), ('padding', '10px'), ('border', '1px solid #ddd')]
        }]) \
        .hide(axis='index')

    # Display the styled DataFrame
    st.dataframe(styled_df, use_container_width=True)

else:
    st.error("Failed to load data from the repository. Please check if all required CSV files are present and valid in your GitHub repository.")

