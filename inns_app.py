import streamlit as st
import pandas as pd
import plotly.express as px

# File uploader for the CSV file
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

# Check if the file is uploaded
if uploaded_file is not None:
    # Load data from the uploaded file
    @st.cache_data
    def load_data(file):
        try:
            # Try loading with default comma separator
            modules = pd.read_csv(file)
        except pd.errors.ParserError:
            # If there's a parsing error, try with semicolon
            modules = pd.read_csv(file, delimiter=';')
        
        # Remove any leading/trailing whitespace from column names
        modules.columns = modules.columns.str.strip()
        
        return modules

    modules = load_data(uploaded_file)

    st.title('PhD Progress Tracker')

    # Ensure necessary columns are present
    if 'current_ects' in modules.columns and 'module_name' in modules.columns and 'required_ects' in modules.columns and 'status' in modules.columns and 'notes' in modules.columns:
        # Overall progress
        total_ects_required = 180  # Total ECTS for the entire PhD program
        total_ects_earned = modules['current_ects'].sum()
        overall_progress = (total_ects_earned / total_ects_required) * 100

        st.metric("Overall PhD Progress", f"{overall_progress:.1f}% ({total_ects_earned}/{total_ects_required} ECTS)")

        # Main modules progress
        main_modules = modules[modules['module_name'].isin(['Dissertation', 'Compulsory Modules', 'Elective Modules'])]
        st.subheader('Main Modules Progress')
        fig = px.bar(main_modules, x='module_name', y=['current_ects', 'required_ects'],
                     labels={'value': 'ECTS', 'variable': 'Type'},
                     title='ECTS Progress by Main Module')
        st.plotly_chart(fig)

        # Detailed module progress
        st.subheader('Detailed Module Progress')

        # Dissertation
        dissertation = modules[modules['module_name'] == 'Dissertation'].iloc[0]
        st.write(f"Dissertation: {dissertation['current_ects']}/{dissertation['required_ects']} ECTS - {dissertation['status']}")

        # Compulsory Modules
        st.write("Compulsory Modules:")
        compulsory_modules = modules[modules['notes'] == 'Compulsory module']
        for _, module in compulsory_modules.iterrows():
            st.write(f"- {module['module_name']}: {module['current_ects']}/{module['required_ects']} ECTS - {module['status']}")

        # Elective Modules
        st.write("Elective Modules:")
        elective_groups = modules[modules['notes'].str.contains('Elective group', na=False)]
        total_elective_ects = elective_groups['current_ects'].sum()
        st.write(f"Total Elective ECTS: {total_elective_ects}/10 ECTS")

        for _, group in elective_groups.iterrows():
            st.write(f"- {group['module_name']}: {group['current_ects']}/{group['required_ects']} ECTS (max 5 ECTS)")
            submodules = modules[modules['notes'].str.contains(f'Part of {group['module_name']}', na=False)]
            for _, submodule in submodules.iterrows():
                st.write(f"  • {submodule['module_name']}: {submodule['current_ects']}/{submodule['required_ects']} ECTS - {submodule['status']}")
    else:
        st.error("The uploaded CSV file is missing one or more required columns. Please ensure it contains 'current_ects', 'module_name', 'required_ects', 'status', and 'notes'.")

else:
    st.warning("Please upload a CSV file to continue.")
