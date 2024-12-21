import streamlit as st
from child_assistant import get_child_assistant
from components.child_selector import select_child

# Configuración de la página
st.set_page_config(page_title="Cuenta Cuentos", page_icon="📚")

# Título
st.title("¡Hora del cuento! 📚")
st.write("Vamos a crear un cuento mágico y personalizado para tu pequeño ✨")

# Seleccionar niño
selected_child = select_child()

if selected_child:
    # Obtener la instancia única del asistente
    assistant = get_child_assistant()
    
    if st.button("¡Crear un cuento mágico! ✨"):
        with st.spinner("Tejiendo una historia mágica... ✍️"):
            try:
                story = assistant.create_story(selected_child)
                st.toast("¡Tu cuento está listo! 🎉")
                st.markdown("### ¡Aquí está tu cuento mágico! 🌟")
                st.markdown(story)
            except Exception as e:
                print(e)
                st.toast("¡Ups! La magia falló un poquito 🎭")
