import streamlit as st
import pandas as pd
import plotly.express as px

# Load data
@st.cache_data
def load_data():
    modules = pd.read_csv('modules.csv')
    return modules

modules = load_data()

st.title('PhD Progress Tracker')

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
    submodules = modules[modules['notes'].str.contains(f'Part of {group["module_name"]}', na=False)]
    for _, submodule in submodules.iterrows():
        st.write(f"  • {submodule['module_name']}: {submodule['current_ects']}/{submodule['required_ects']} ECTS - {submodule['status']}")
