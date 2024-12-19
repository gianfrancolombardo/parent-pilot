import streamlit as st
from child_assistant import get_child_assistant
from components.child_selector import select_child

# Configuración de la página
st.set_page_config(page_title="Actividades Montessori", page_icon="🎯")

# Título
st.title("¡Actividades Montessori! 🎯")
st.write("Descubre actividades divertidas y educativas para tu pequeño 🌈")

# Seleccionar niño
selected_child = select_child()

if selected_child:
    # Obtener la instancia única del asistente
    assistant = get_child_assistant()
    
    if st.button("¡Generar actividades! 🎨"):
        with st.spinner("Creando actividades especiales... 🎪"):
            try:
                activities = assistant.create_activities(selected_child)
                st.toast("¡Tus actividades están listas! 🎉")
                st.markdown("### ¡Aquí están tus actividades! 🌟")
                st.markdown(activities)
            except Exception as e:
                st.toast("¡Ups! Algo salió mal al crear las actividades 🎭")
