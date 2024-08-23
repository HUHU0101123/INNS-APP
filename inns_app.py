import streamlit as st
import pandas as pd
import plotly.express as px

# [Código de inicialización y carga de archivos se mantiene igual]

if uploaded_file is not None:
    modules = load_data(uploaded_file)
    
    if not modules.empty:
        required_columns = {'current_ects', 'module_name', 'required_ects', 'status', 'notes'}
        if required_columns.issubset(modules.columns):
            # Excluir la disertación
            modules_without_dissertation = modules[modules['module_name'] != 'Dissertation']
            
            # Calcular ECTS totales excluyendo la disertación
            total_ects_required = modules_without_dissertation['required_ects'].sum()
            total_ects_earned = modules_without_dissertation['current_ects'].sum()
            
            # Identificar cursos en progreso
            current_courses = modules_without_dissertation[modules_without_dissertation['status'] == 'Current Semester']
            ects_in_progress = current_courses['required_ects'].sum()
            
            # Calcular ECTS restantes
            ects_remaining = total_ects_required - total_ects_earned - ects_in_progress
            
            st.markdown("## PhD Progress Tracker: Course Advancement")
            
            # Gráfico circular actualizado
            fig = px.pie(
                values=[total_ects_earned, ects_in_progress, ects_remaining],
                names=['Completed', 'In Progress', 'Remaining'],
                title='Overall Course Progress (Excluding Dissertation)',
                color_discrete_sequence=['#4CAF50', '#FFC107', '#E0E0E0']
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig)
            
            st.write(f"Completed: {total_ects_earned:.1f} ECTS")
            st.write(f"In Progress: {ects_in_progress:.1f} ECTS")
            st.write(f"Remaining: {ects_remaining:.1f} ECTS")
            
            # Progreso de módulos obligatorios
            st.markdown("### Compulsory Modules Progress")
            compulsory_modules = modules_without_dissertation[modules_without_dissertation['notes'] == 'Compulsory module']
            fig = px.bar(compulsory_modules, x='module_name', y=['current_ects', 'required_ects'],
                         title='Compulsory Modules Progress',
                         labels={'value': 'ECTS', 'variable': 'Type'},
                         color_discrete_map={'current_ects': '#9C27B0', 'required_ects': '#8BC34A'},
                         barmode='group')
            fig.update_layout(yaxis_title='ECTS Credits')
            st.plotly_chart(fig)
            
            # Progreso de módulos electivos
            st.markdown("### Elective Modules Progress")
            elective_modules = modules_without_dissertation[modules_without_dissertation['notes'].str.contains('Elective', na=False)]
            fig = px.bar(elective_modules, x='module_name', y=['current_ects', 'required_ects'],
                         title='Elective Modules Progress',
                         labels={'value': 'ECTS', 'variable': 'Type'},
                         color_discrete_map={'current_ects': '#00BCD4', 'required_ects': '#FF9800'},
                         barmode='group')
            fig.update_layout(yaxis_title='ECTS Credits')
            st.plotly_chart(fig)
            
            # Cursos actuales
            st.markdown("### Currently Enrolled Courses")
            st.table(current_courses[['module_name', 'required_ects']])
            
            # Resumen
            st.markdown("## Course Progress Summary")
            st.write(f"1. Overall course completion: {(total_ects_earned/total_ects_required)*100:.1f}%")
            st.write(f"2. Courses in progress: {ects_in_progress:.1f} ECTS")
            st.write(f"3. Compulsory modules completed: {compulsory_modules['current_ects'].sum():.1f} out of {compulsory_modules['required_ects'].sum():.1f} ECTS")
            st.write(f"4. Elective modules completed: {elective_modules['current_ects'].sum():.1f} out of {elective_modules['required_ects'].sum():.1f} ECTS")
            
            st.write("Keep up the great work and continue making progress in your coursework!")

        else:
            st.error("The uploaded CSV file is missing one or more required columns.")
    else:
        st.warning("Please upload a valid CSV file to continue.")
