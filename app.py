import streamlit as st
from firebase_manager import FirebaseManager
from child_assistant import get_child_assistant
import json
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Copilot para padres", page_icon="👶")

# Inicializar Firebase Manager con los secrets
@st.cache_resource
def get_firebase_manager():
    firebase_credentials = st.secrets["firebase"]["credencials"]
    return FirebaseManager(firebase_credentials)

# Inicializar y guardar el firebase_mgr en el estado de la sesión
firebase_mgr = get_firebase_manager()
st.session_state['firebase_mgr'] = firebase_mgr

# Obtener la instancia única del asistente
assistant = get_child_assistant()

st.title('¡Bienvenido a tu Copilot para padres! 👶')

tab1, tab2 = st.tabs(["📋 Mis pequeños", "➕ Registrar nuevo bebé"])

with tab1:
    children = firebase_mgr.get_all_children()
    if not children:
        st.info("¡Aún no hay pequeños registrados! 🎈 Registra a tu bebé en la siguiente pestaña.")
    else:
        st.write("### Aquí están todos tus pequeños 🌟")
        for child in children:
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    birth_date = datetime.fromisoformat(child['birth_date'])
                    age = assistant.calculate_age(birth_date)
                    emoji_sex = '👦' if child['gender'] == 'Masculino' else '👧'
                    st.write(f"#### {child['name']} • {age} • {emoji_sex}")
                with col2:
                    st.write("")  # Espacio para alineación
                st.divider()

with tab2:
    st.write("### ¡Registra a tu pequeño! 🎈")
    with st.form(key='child_registration_form'):
        name = st.text_input('¿Cómo se llama tu bebé?')
        birth_date = st.date_input('¿Cuándo nació?')
        gender = st.selectbox('¿Es niño o niña?', ['Masculino', 'Femenino'])
        submit_button = st.form_submit_button(label='🌟 ¡Registrar!')

        if submit_button:
            if name and birth_date:
                try:
                    child_id = firebase_mgr.save_child(name, birth_date, gender)
                    st.toast(f"¡{name} ha sido registrado con éxito! 🎉")
                except Exception as e:
                    st.toast(f"¡Ups! Algo salió mal: {str(e)} 😅")
            else:
                st.toast("¡Hey! Necesito saber el nombre y la fecha de nacimiento 😊")
