import streamlit as st
from firebase_manager import FirebaseManager
from child_assistant import get_child_assistant
from datetime import datetime
from langchain.prompts import PromptTemplate

# Configuración de la página
st.set_page_config(page_title="Chat Montessori", page_icon="💭")

# Obtener las instancias necesarias
firebase_mgr = st.session_state['firebase_mgr']
assistant = get_child_assistant()

st.title('Chat Montessori 💭')

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
    
    st.write(f"### Conversando sobre {selected_child['name']} • {age} • {emoji_sex}")
    
    # Inicializar el historial de chat en el estado de la sesión si no existe
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    
    # Mostrar mensajes del chat
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("¿Qué te gustaría saber sobre la crianza de tu pequeño?"):
        # Agregar mensaje del usuario al chat
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generar respuesta del asistente
        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                # Crear el mensaje del sistema personalizado usando el prompt de prompts.yaml
                prompt_template = PromptTemplate.from_template(assistant.prompts['chat_prompt'])
                system_prompt = prompt_template.format(nombre=selected_child['name'], edad=age)
                
                # Configurar el chat con el mensaje del sistema
                messages = [
                    {"role": "system", "content": system_prompt},
                    *st.session_state.chat_messages  # Incluir historial del chat
                ]
                
                # Obtener respuesta
                response = assistant.llm.invoke(messages).content
                st.markdown(response)
                
                # Agregar respuesta al historial
                st.session_state.chat_messages.append({"role": "assistant", "content": response})
