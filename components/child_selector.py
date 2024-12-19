import streamlit as st
from datetime import datetime

def select_child():
    """
    Componente común para seleccionar un niño de la lista
    Retorna el niño seleccionado con la fecha de nacimiento convertida a datetime
    """
    # Obtener el Firebase Manager del estado de la sesión
    firebase_mgr = st.session_state.get('firebase_mgr')
    if not firebase_mgr:
        st.toast("¡Ups! No pude conectar con la base de datos 😅")
        st.stop()

    # Obtener la lista de niños
    children = firebase_mgr.get_all_children()

    if not children:
        st.info("¡Aún no hay pequeños registrados! 🎈 Regístralos en la página principal.")
        st.stop()

    # Crear el selector de niños
    selected_child = st.selectbox(
        "¿Para quién creamos hoy? 🌟",
        options=children,
        format_func=lambda x: x['name']
    )

    if selected_child:
        # Convertir la fecha de nacimiento de string a datetime
        selected_child['birth_date'] = datetime.fromisoformat(selected_child['birth_date'])
        return selected_child
    
    return None
