import streamlit as st
from datetime import datetime, timedelta
import plotly.graph_objects as go
import numpy as np

# Configuración de la página
st.set_page_config(page_title="Seguimiento Diario", page_icon="📊")

# Recuperar el firebase manager de la sesión
firebase_mgr = st.session_state.get('firebase_mgr')
if not firebase_mgr:
    st.error("Error: No se pudo conectar con la base de datos")
    st.stop()

# Obtener los niños registrados
children = firebase_mgr.get_all_children()

if not children:
    st.info("¡Aún no hay pequeños registrados! 🎈")
    st.button("⚙️ Ir a Administración para registrar a tu bebé", 
             on_click=lambda: st.switch_page("pages/1_⚙️_Administracion.py"))
else:
    # Selector de niño
    if len(children) > 1:
        selected_child_name = st.selectbox(
            "Selecciona un pequeño",
            [child['name'] for child in children],
            index=0
        )
        selected_child = next(child for child in children if child['name'] == selected_child_name)
    else:
        selected_child = children[0]

    st.title(f"Seguimiento Diario de {selected_child['name']} 📊")

    # Crear tres columnas para los contadores
    col1, col2, col3 = st.columns(3)

    # Función para crear un contador
    def create_counter(column, title, record_type, emoji):
        with column:
            st.subheader(f"{title} {emoji}")
            col_minus, col_count, col_plus = st.columns([1,1,1])
            
            # Obtener registros del día actual
            today_records = firebase_mgr.get_daily_records(selected_child['id'], days=1)[0]
            current_count = today_records.get(record_type, 0)
            
            # Botones y contador
            with col_minus:
                if st.button(f"➖", key=f"minus_{record_type}"):
                    firebase_mgr.save_daily_record(selected_child['id'], record_type, -1)
                    st.rerun()
            
            with col_count:
                st.markdown(f"<h1 style='text-align: center; padding: 0px;line-height: 40px;'>{current_count}</h1>", unsafe_allow_html=True)
            
            with col_plus:
                if st.button(f"➕", key=f"plus_{record_type}"):
                    firebase_mgr.save_daily_record(selected_child['id'], record_type, 1)
                    st.rerun()

    # Crear los tres contadores
    create_counter(col1, "Pañal Pipi", "pee_diaper", "💧")
    create_counter(col2, "Pañal", "full_diaper", "💩")
    create_counter(col3, "Tomas", "feeding", "🍼")

    st.divider()

    # Fecha actual
    now = datetime.now()

    # Obtener registros de los últimos 7 días
    records = firebase_mgr.get_daily_records(selected_child['id'], days=7)

    # Calcular promedios
    avg_feeding = np.mean([record.get('feeding', 0) for record in records])
    avg_diapers = np.mean([record.get('pee_diaper', 0) + record.get('full_diaper', 0) for record in records])

    # Mostrar métricas
    st.markdown("### Promedios últimos 7 días")
    col_metrics1, col_metrics2 = st.columns(2)
    
    with col_metrics1:
        st.metric(
            label="Tomas por día 🍼",
            value=f"{avg_feeding:.1f}"
        )
    
    with col_metrics2:
        st.metric(
            label="Cambios de pañal por día 👶",
            value=f"{avg_diapers:.1f}"
        )

    # Gráfico de tendencias
    st.markdown("### Últimos 7 días")
    
    # Preparar datos para el gráfico
    dates = [record['date'] for record in records]
    feedings = [record.get('feeding', 0) for record in records]
    total_diapers = [record.get('pee_diaper', 0) + record.get('full_diaper', 0) for record in records]

    # Crear gráfico de barras
    fig = go.Figure()
    
    # Añadir barras para pañales
    fig.add_trace(go.Bar(
        x=dates,
        y=total_diapers,
        name="Pañales",
        marker_color="#99CCFF"
    ))
    
    # Añadir barras para tomas
    fig.add_trace(go.Bar(
        x=dates,
        y=feedings,
        name="Tomas",
        marker_color="#FF9999"
    ))

    # Configurar layout
    fig.update_layout(
        xaxis_title="Fecha",
        yaxis_title="Cantidad",
        barmode='group',
        bargap=0.15,
        bargroupgap=0.1,
        showlegend=True
    )

    st.plotly_chart(fig, use_container_width=True)
