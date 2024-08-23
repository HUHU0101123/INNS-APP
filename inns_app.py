import streamlit as st
import pandas as pd
import plotly.express as px

# Load modules and submodules data
modules = pd.read_csv('modules.csv')
submodules = pd.read_csv('submodules.csv')

# Process and visualize data
if not modules.empty and not submodules.empty:
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
    st.warning("No data available. Please ensure the CSV files are correctly formatted and contain data.")
