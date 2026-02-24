"""
PID CONTROLLER TUNER - Aplicación Streamlit Principal

Punto de entrada que configura la app multi-página.
"""

import streamlit as st
import sys
from pathlib import Path

# Agregar src al path para importar módulos
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configurar página
st.set_page_config(
    page_title="PID Controller Tuner",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/usuario/pid-tuner",
        "Report a bug": "https://github.com/usuario/pid-tuner/issues",
        "About": "### PID Controller Tuner - Control Systems Design Tool v1.0"
    }
)

# Estilos CSS personalizados
st.markdown("""
<style>
    /* Custom styling for better UI */
    .main {
        padding-top: 2rem;
    }
    
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.1rem;
        font-weight: 600;
    }
    
    .metric-card {
        background-color: #f0f5ff;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #0066CC;
    }
    
    .success-card {
        background-color: #e6ffe6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #00CC66;
    }
    
    .warning-card {
        background-color: #fff3e6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #FF9900;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar session state
if "transfer_function" not in st.session_state:
    st.session_state.transfer_function = None

if "pid_params" not in st.session_state:
    st.session_state.pid_params = None

if "metricas" not in st.session_state:
    st.session_state.metricas = None

if "respuesta_simulada" not in st.session_state:
    st.session_state.respuesta_simulada = None

# Título y descripción principal
st.title("🎛️ PID Controller Tuner")
st.markdown("### Sistema Inteligente de Sintonización de Controladores PID")

# Información en la página principal
with st.container():
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="🚀 Métodos",
            value="3",
            delta="ZN • CC • Crítico"
        )
    
    with col2:
        st.metric(
            label="📊 Métricas",
            value="3",
            delta="ts • Mp • ess"
        )
    
    with col3:
        st.metric(
            label="💾 Exportar",
            value="3 Formatos",
            delta="PNG • PDF • CSV"
        )

st.markdown("---")

# Instrucciones generales
with st.expander("📖 ¿Cómo usar esta herramienta?", expanded=False):
    st.markdown("""
    ## Flujo de Trabajo
    
    1. **🔧 Diseñador**: Ingresa la función de transferencia y selecciona el método
    2. **📊 Resultados**: Visualiza parámetros PID y métricas de desempeño
    3. **📚 Documentación**: Consulta teoría y ejemplos
    
    ## Métodos Disponibles
    
    - **Ziegler-Nichols**: Sintonización rápida (~20% overshoot)
    - **Cohen-Coon**: Mejor balance (~15% overshoot, menos oscilaciiones)
    - **Amortiguado Crítico**: Mínimo overshoot (~0-5%)
    
    ## Modelo Soportado
    
    Funciones de transferencia FOPDT (First Order Plus Dead Time):
    
    $$G(s) = \\frac{K}{Ts+1} \\times e^{-Ls}$$
    
    Donde:
    - **K**: Ganancia DC del proceso
    - **T**: Constante de tiempo
    - **L**: Retardo de transporte
    """)

st.markdown("---")

# Información de estado
if st.session_state.pid_params:
    st.success("""
    ✅ **Cálculo completado**
    
    Accede a la página "📊 Resultados" para ver gráficos y métricas detalladas.
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #999; font-size: 0.9rem;'>
    <p>PID Controller Tuner v1.0 | © 2026 Control Engineering</p>
    <p>Basado en métodos clásicos de sintonización (Ziegler-Nichols, Cohen-Coon)</p>
</div>
""", unsafe_allow_html=True)
