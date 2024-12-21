import streamlit as st
from firebase_manager import FirebaseManager
from child_assistant import get_child_assistant
from datetime import datetime
from gtts import gTTS
import os
import base64
import re

# Configuración de la página
st.set_page_config(page_title="Copilot para padres", page_icon="👶")

# Función para limpiar el texto markdown
def clean_markdown(text):
    # Eliminar encabezados
    text = re.sub(r'#+\s+', '', text)
    # Eliminar negrita
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    # Eliminar cursiva
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    # Eliminar viñetas
    text = re.sub(r'[-*]\s+', '', text)
    # Eliminar enlaces
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
    # Eliminar líneas vacías múltiples
    text = re.sub(r'\n\s*\n', '\n', text)
    return text.strip()

# Función para convertir texto a audio y obtener el HTML para reproducirlo
def get_audio_player(text, lang='es'):
    # Limpiar el markdown del texto
    clean_text = clean_markdown(text)
    
    # Crear el audio con gTTS
    tts = gTTS(text=clean_text, lang=lang)
    
    # Guardar temporalmente el archivo
    audio_path = "temp_audio.mp3"
    tts.save(audio_path)
    
    # Leer el archivo y convertirlo a base64
    with open(audio_path, "rb") as audio_file:
        audio_bytes = audio_file.read()
    audio_b64 = base64.b64encode(audio_bytes).decode()
    
    # Eliminar el archivo temporal
    os.remove(audio_path)
    
    # Crear el reproductor de audio HTML con controles de velocidad
    audio_player = f"""
    <audio id="audio-player" controls>
        <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
    </audio>
    <script>
        // Selecciona el reproductor de audio y establece la velocidad predeterminada
        const audioPlayer = document.getElementById("audio-player");
        audioPlayer.addEventListener("loadedmetadata", () => {{
            audioPlayer.playbackRate = 1.5;
        }});
    </script>
    """
    return audio_player

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

# Obtener los niños registrados
children = firebase_mgr.get_all_children()

if not children:
    st.info("¡Aún no hay pequeños registrados! 🎈")
    st.button("⚙️ Ir a Administración para registrar a tu bebé", on_click=lambda: st.switch_page("pages/1_⚙️_Administracion.py"))
else:
    # Mostrar selector de niño si hay más de uno
    if len(children) > 1:
        selected_child_name = st.selectbox(
            "Selecciona un pequeño",
            [child['name'] for child in children]
        )
        selected_child = next(child for child in children if child['name'] == selected_child_name)
    else:
        selected_child = children[0]
    
    # Mostrar información del niño seleccionado
    age = assistant.calculate_age(selected_child['birth_date'])
    emoji_sex = '👦' if selected_child['gender'] == 'Masculino' else '👧'
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.write(f"### {selected_child['name']} • {age} • {emoji_sex}")
    with col2:
        # Botón para generar el resumen
        btn_summary = st.button(f'📝 Generar resumen de {selected_child["name"]}')

    if btn_summary:
        with st.spinner(f'Analizando el desarrollo de {selected_child["name"]}...'):
            daily_summary = assistant.create_welcome_summary(selected_child)
            
            # Mostrar el resumen en un expander
            with st.expander("📝 Resumen del desarrollo", expanded=True):
                col3, col4 = st.columns([1, 2])
                with col3:
                    st.write("🔊 Escuchar resumen:")
                with col4:
                    audio_player = get_audio_player(daily_summary)
                    st.markdown(audio_player, unsafe_allow_html=True)

                st.markdown(daily_summary)
                    
                
    # Si hay más niños, mostrar sus resúmenes en expanders colapsados
    if len(children) > 1:
        other_children = [child for child in children if child['name'] != selected_child['name']]
        for child in other_children:
            age = assistant.calculate_age(child['birth_date'])
            emoji_sex = '👦' if child['gender'] == 'Masculino' else '👧'
            with st.expander(f"📝 {child['name']} • {age} • {emoji_sex}", expanded=False):
                with st.spinner(f'Analizando el desarrollo de {child["name"]}...'):
                    summary = assistant.create_welcome_summary(child)
                    st.markdown(summary)
