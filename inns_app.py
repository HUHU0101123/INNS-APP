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
            # Overall progress
            total_ects_required = 180  # Total ECTS for the entire PhD program
            total_ects_earned = modules['current_ects'].sum()
            overall_progress = (total_ects_earned / total_ects_required) * 100

            st.markdown("## PhD Progress Tracker: Your Academic Journey Visualized")

            st.markdown("Your PhD journey is a remarkable odyssey of knowledge and discovery. Let's explore your progress through an innovative lens.")

            st.markdown("### Overall Progress: The Big Picture")

            st.write(f"You've made significant strides in your doctoral pursuit. Currently, you've earned {total_ects_earned:.1f} out of 180 ECTS credits, placing you at {overall_progress:.1f}% completion of your PhD program.")

            fig = px.pie(values=[total_ects_earned, total_ects_required - total_ects_earned], 
                         names=['Completed', 'Remaining'], 
                         title='Overall PhD Progress',
                         color_discrete_sequence=['#4CAF50', '#E0E0E0'])
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig)

            st.markdown("### Module Mastery: Breaking It Down")

            st.write("Your PhD journey is composed of three main pillars: Dissertation, Compulsory Modules, and Elective Modules. Let's see how you're progressing in each area.")

            # Main modules progress
            main_modules = modules[modules['module_name'].isin(['Dissertation', 'Compulsory Modules', 'Elective Modules'])]
            fig = px.bar(main_modules, x='module_name', y=['current_ects', 'required_ects'],
                         title='ECTS Progress by Main Module',
                         labels={'value': 'ECTS', 'variable': 'Type'},
                         color_discrete_map={'current_ects': '#1E88E5', 'required_ects': '#FFC107'},
                         barmode='group')
            fig.update_layout(yaxis_title='ECTS Credits')
            st.plotly_chart(fig)

            st.markdown("### The Heart of Your PhD: Dissertation Progress")

            # Dissertation
            dissertation = modules[modules['module_name'] == 'Dissertation'].iloc[0]
            st.write(f"Your dissertation is the cornerstone of your doctoral journey. You've completed {dissertation['current_ects']} out of {dissertation['required_ects']} ECTS credits, marking a {dissertation['current_ects']/dissertation['required_ects']*100:.1f}% completion rate.")

            fig = px.pie(values=[dissertation['current_ects'], dissertation['required_ects'] - dissertation['current_ects']], 
                         names=['Completed', 'Remaining'], 
                         title='Dissertation Progress',
                         color_discrete_sequence=['#FF5722', '#E0E0E0'])
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig)

            st.markdown("### Compulsory Modules: Building Your Foundation")

            st.write("These modules form the bedrock of your PhD education. Let's see how you're faring:")

            # Compulsory Modules
            compulsory_modules = modules[modules['notes'] == 'Compulsory module']
            fig = px.bar(compulsory_modules, x='module_name', y=['current_ects', 'required_ects'],
                         title='Compulsory Modules Progress',
                         labels={'value': 'ECTS', 'variable': 'Type'},
                         color_discrete_map={'current_ects': '#9C27B0', 'required_ects': '#8BC34A'},
                         barmode='group')
            fig.update_layout(yaxis_title='ECTS Credits')
            st.plotly_chart(fig)

            st.markdown("### Elective Modules: Tailoring Your Expertise")

            # Elective Modules
            elective_groups = modules[modules['notes'].str.contains('Elective group', na=False)]
            total_elective_ects = elective_groups['current_ects'].sum()
            st.write(f"You've earned {total_elective_ects} out of 10 ECTS credits in elective modules, allowing you to customize your PhD experience. Here's how you've distributed your efforts:")

            fig = px.bar(elective_groups, x='module_name', y=['current_ects', 'required_ects'],
                         title='Elective Modules Progress',
                         labels={'value': 'ECTS', 'variable': 'Type'},
                         color_discrete_map={'current_ects': '#00BCD4', 'required_ects': '#FF9800'},
                         barmode='group')
            fig.update_layout(yaxis_title='ECTS Credits')
            st.plotly_chart(fig)

            st.markdown("## Your PhD Story: Milestones and Next Steps")

            st.write("As you progress through your PhD, remember that each credit earned is a step towards your goal. Here are some key takeaways:")

            st.write(f"1. You're {overall_progress:.1f}% through your overall PhD journey.")
            st.write(f"2. Your dissertation is {dissertation['current_ects']/dissertation['required_ects']*100:.1f}% complete.")
            st.write(f"3. You've completed {total_elective_ects/10*100:.1f}% of your elective module requirements.")

            st.write("Keep pushing forward, and don't forget to celebrate each milestone along the way!")

        else:
            st.error("The uploaded CSV file is missing one or more required columns. Please ensure it contains 'current_ects', 'module_name', 'required_ects', 'status', and 'notes'.")
            st.write("Available columns:", modules.columns.tolist())
else:
    st.warning("Please upload a CSV file to continue.")
