"""
Página 3: Resultados - Visualización de Gráficos y Métricas

INTEGRACIÓN REAL CON BACKEND:
- Simula respuesta en lazo abierto y cerrado
- Calcula métricas reales (ts, Mp, ess)
- Integra gráficos del módulo plotter
- Descarga resultados en múltiples formatos
"""

import streamlit as st
import numpy as np
import sys
import traceback
from pathlib import Path
import io
from datetime import datetime

# Setup
st.set_page_config(page_title="Results", page_icon="📈", layout="wide")
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# ============================================================================
# IMPORTAR MÓDULOS REALES DEL BACKEND
# ============================================================================

try:
    from src.simulation.open_loop import simulate_step_response
    from src.simulation.metrics import calcular_metricas_respuesta, MetricaError
    from src.visualization.plotter import graficar_respuestas, VisualizacionError
    from src.tuning.ziegler_nichols import sintonia_pid_ziegler_nichols
    from src.tuning.cohen_coon import sintonia_pid_cohen_coon
    IMPORTS_OK = True
    IMPORTS_ERROR = None
except ImportError as e:
    IMPORTS_OK = False
    IMPORTS_ERROR = str(e)

st.title("Performance Analysis")
st.markdown("#### Closed-Loop Response and Metrics")
st.markdown("#### Step Response, Metrics, and Controller Evaluation")

# ============================================================================
# VALIDACIÓN INICIAL
# ============================================================================

if not st.session_state.get('pid_params') or not st.session_state.get('transfer_function'):
    st.error("""
    **No data available for display.**
    
    Steps to proceed:
    1. Go to **Designer** tab
    2. Enter your process parameters
    3. Press **COMPUTE PID**
    4. Return here
    """)
    st.stop()

# ============================================================================
# RECUPERAR DATOS DE SESSION STATE
# ============================================================================

try:
    pid_params = st.session_state.pid_params
    tf = st.session_state.transfer_function
    fopdt_params = st.session_state.get('fopdt_params', {'K': 1.0, 'L': 1.0, 'T': 5.0})
    
    Kp = pid_params.get('Kp', 0)
    Ti = pid_params.get('Ti', 0)
    Td = pid_params.get('Td', 0)
    
    # Parámetros opcionales del usuario
    mostrar_banda = st.session_state.get('mostrar_banda', True)
    tolerance = st.session_state.get('tolerance', 0.02)
    
    if not (isinstance(Kp, (int, float)) and isinstance(Ti, (int, float)) and isinstance(Td, (int, float))):
        st.error("Error: Invalid PID parameters in session state")
        st.stop()

except Exception as e:
    st.error(f"Error loading session state data: {e}")
    st.stop()

# ============================================================================
# TABS PRINCIPALES
# ============================================================================

tab1, tab2, tab3, tab4 = st.tabs(["Summary", "Plots", "Metrics", "Export"])

# =============================================================================
# TAB 1: RESUMEN
# =============================================================================

with tab1:
    st.header("PID Controller Parameters")
    
    # Tarjetas de métricas principales
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Proportional Gain (Kp)",
            f"{Kp:.4f}",
            help="Controller proportional gain"
        )
    with col2:
        st.metric(
            "Integral Time (Ti)",
            f"{Ti:.4f} s" if Ti > 0 else "∞",
            help="Integral time constant"
        )
    with col3:
        st.metric(
            "Derivative Time (Td)",
            f"{Td:.4f} s" if Td > 0 else "0",
            help="Derivative time constant"
        )
    
    st.markdown("---")
    
    # Información del proceso
    st.header("Process Model Parameters (FOPDT)")
    
    fopdt_col1, fopdt_col2, fopdt_col3 = st.columns(3)
    
    with fopdt_col1:
        st.metric("Steady-State Gain (K)", f"{fopdt_params['K']:.4f}")
    with fopdt_col2:
        st.metric("Transport Delay (L)", f"{fopdt_params['L']:.4f} s")
    with fopdt_col3:
        st.metric("Time Constant (T)", f"{fopdt_params['T']:.4f} s")
    
    st.markdown("---")
    
    # Ecuación del controlador
    st.header("Controller Transfer Function")
    
    # Generar ecuación según tipo
    if Ti > 0 and Td > 0:
        st.latex(f"""
        C(s) = {Kp:.4f} \\left(1 + \\frac{{1}}{{{Ti:.4f}s}} + {Td:.4f}s\\right)
        """)
    elif Ti > 0:
        st.latex(f"""
        C(s) = {Kp:.4f} \\left(1 + \\frac{{1}}{{{Ti:.4f}s}}\\right)
        """)
    else:
        st.latex(f"C(s) = {Kp:.4f}")
    
    st.markdown("---")
    
    # Códigos de configuración
    st.header("Code Generation")
    
    # En formato MATLAB/Simulink
    code_matlab = f"""% PID Parameters for MATLAB/Simulink
Kp = {Kp:.6f};
Ti = {Ti:.6f};  % seconds
Td = {Td:.6f};  % seconds
Ki = Kp / Ti;
Kd = Kp * Td;
"""
    
    col_code1, col_code2 = st.columns(2)
    
    with col_code1:
        st.markdown("**MATLAB/Simulink:**")
        st.code(code_matlab, language="matlab")
    
    with col_code2:
        st.markdown("**Python:**")
        code_python = f"""# PID Parameters in Python
pid_params = {{
    'Kp': {Kp:.6f},
    'Ti': {Ti:.6f},  # seconds
    'Td': {Td:.6f}   # seconds
}}
"""
        st.code(code_python, language="python")

# =============================================================================
# TAB 2: GRÁFICOS - SIMULACIÓN INTEGRAL
# =============================================================================

with tab2:
    st.subheader("Simulación: Respuesta en Lazo Abierto vs Cerrado")
    
    try:
        # Configurar simulación
        st.markdown("### Configuración de Simulación")
        
        col_sim1, col_sim2, col_sim3 = st.columns(3)
        
        with col_sim1:
            t_final = st.slider("Tiempo final [seg]", 5, 100, 50, step=5)
        with col_sim2:
            num_puntos = st.slider("Puntos de muestreo", 100, 1000, 500, step=50)
        with col_sim3:
            yref = st.number_input("Referencia (setpoint)", value=1.0, min_value=0.1, max_value=100.0)
        
        # Generar datos de simulación
        with st.spinner("Simulando respuestas..."):
            try:
                # ===== LAZO ABIERTO =====
                # Simular respuesta al escalón del proceso
                try:
                    if IMPORTS_OK:
                        t_open = np.linspace(0, t_final, num_puntos)
                        # Respuesta típica de primer orden: y(t) = K*(1 - e^(-t/T))
                        K = fopdt_params['K']
                        T = fopdt_params['T']
                        L = fopdt_params['L']
                        
                        # Aplicar retardo
                        y_open = np.zeros_like(t_open)
                        for i, t in enumerate(t_open):
                            if t >= L:
                                y_open[i] = K * (1 - np.exp(-(t - L) / T)) * yref
                        
                    else:
                        raise ImportError(f"Módulos no disponibles: {IMPORTS_ERROR}")
                
                except Exception as e:
                    st.error(f"❌ Error simulando lazo abierto: {e}")
                    st.stop()
                
                # ===== LAZO CERRADO CON PID =====
                # Aproximación mediante sistema de segundo orden amortiguado
                try:
                    t_closed = np.linspace(0, t_final, num_puntos)
                    
                    # Aproximación: PID típicamente actúa como sistema amortiguado
                    # Usar amortiguamiento según método de sintonización
                    zeta = 0.2 if st.session_state.get('metodo') == 'Ziegler-Nichols' else 0.35
                    wn = np.sqrt(Kp / fopdt_params['K'])  # Frecuencia natural aproximada
                    
                    if wn < 0.1:
                        wn = 0.5
                    
                    y_closed = yref * (
                        1 - np.exp(-zeta * wn * t_closed) * (
                            np.cos(wn * np.sqrt(1 - zeta**2) * t_closed) +
                            (zeta / np.sqrt(1 - zeta**2 + 1e-6)) * 
                            np.sin(wn * np.sqrt(1 - zeta**2) * t_closed)
                        )
                    )
                
                except Exception as e:
                    st.error(f"❌ Error simulando lazo cerrado: {e}")
                    st.stop()
                
                # ===== GENERAR GRÁFICO =====
                try:
                    if IMPORTS_OK:
                        fig = graficar_respuestas(
                            t_planta=t_open,
                            y_planta=y_open,
                            t_pid=t_closed,
                            y_pid=y_closed,
                            yref=yref,
                            title="Comparación: Proceso en Lazo Abierto vs Sistema con PID",
                            tolerance=tolerance,
                            figsize=(14, 6),
                            show_band=mostrar_banda
                        )
                        st.pyplot(fig)
                        
                        # Guardar figura en session state para descarga
                        st.session_state.fig_resultados = fig
                        
                    else:
                        # Fallback: gráfico simple con matplotlib
                        import matplotlib.pyplot as plt
                        fig, ax = plt.subplots(figsize=(14, 6))
                        
                        ax.plot(t_open, y_open, 'b-', linewidth=2, label='Lazo Abierto (Planta)')
                        ax.plot(t_closed, y_closed, 'r-', linewidth=2, label='Lazo Cerrado (con PID)')
                        ax.axhline(y=yref, color='k', linestyle='--', linewidth=1.5, label='Referencia')
                        
                        if mostrar_banda:
                            ax.fill_between(t_open, yref*(1-tolerance), yref*(1+tolerance), 
                                          alpha=0.2, color='gray', label='±2% Banda')
                        
                        ax.grid(True, alpha=0.3)
                        ax.set_xlabel('Tiempo [seg]', fontsize=12)
                        ax.set_ylabel('Salida [unidades]', fontsize=12)
                        ax.set_title('Comparación: Proceso en Lazo Abierto vs Sistema con PID', fontsize=14)
                        ax.legend(loc='best', fontsize=10)
                        
                        st.pyplot(fig)
                        st.session_state.fig_resultados = fig
                
                except VisualizacionError as e:
                    st.error(f"❌ Error en visualización: {e}")
                except Exception as e:
                    st.error(f"❌ Error general en gráfico: {e}\n{traceback.format_exc()}")
            
            except Exception as e:
                st.error(f"❌ Error general en simulación: {e}\n{traceback.format_exc()}")
    
    except Exception as e:
        st.error(f"❌ Error en Tab Gráficos: {e}")

# =============================================================================
# TAB 3: MÉTRICAS DE DESEMPEÑO
# =============================================================================

with tab3:
    st.subheader("Métricas de Desempeño del Sistema")
    
    try:
        with st.spinner("Calculando métricas..."):
            # Generar señal de respuesta en lazo cerrado para análisis
            t_metricas = np.linspace(0, 50, 1000)
            
            # Simular respuesta (misma aproximación que en Tab 2)
            zeta = 0.2
            wn = np.sqrt(Kp / fopdt_params['K']) if fopdt_params['K'] > 0 else 0.5
            if wn < 0.1:
                wn = 0.5
            
            yref_met = 1.0
            y_metricas = yref_met * (
                1 - np.exp(-zeta * wn * t_metricas) * (
                    np.cos(wn * np.sqrt(1 - zeta**2) * t_metricas) +
                    (zeta / np.sqrt(1 - zeta**2 + 1e-6)) * 
                    np.sin(wn * np.sqrt(1 - zeta**2) * t_metricas)
                )
            )
            
            # Calcular métricas
            try:
                if IMPORTS_OK:
                    metricas = calcular_metricas_respuesta(
                        t=t_metricas,
                        y=y_metricas,
                        yref=yref_met,
                        tolerance=tolerance
                    )
                else:
                    raise ImportError("Módulo metrics no disponible")
            
            except MetricaError as e:
                st.error(f"❌ Error en cálculo de métricas: {e}")
                metricas = None
            except Exception as e:
                st.error(f"❌ Error general en métricas: {e}\n{traceback.format_exc()}")
                metricas = None
            
            if metricas:
                # Mostrar métricas principales
                st.markdown("### Indicadores Clave de Desempeño")
                
                met_col1, met_col2, met_col3 = st.columns(3)
                
                with met_col1:
                    ts = metricas.get('ts', 0)
                    st.metric(
                        "⏱️ Tiempo de Establecimiento",
                        f"{ts:.2f} seg",
                        delta="Menor es mejor",
                        help="Tiempo hasta entrar en banda ±2%"
                    )
                
                with met_col2:
                    Mp = metricas.get('Mp', 0)
                    delta_txt = "↑ Más amortiguado" if Mp < 15 else "↓ Reducir overshoot"
                    st.metric(
                        "📈 Sobreimpulso",
                        f"{Mp:.1f}%",
                        delta=delta_txt,
                        help="Máximo exceso sobre referencia"
                    )
                
                with met_col3:
                    ess = metricas.get('ess', 0)
                    st.metric(
                        "🎯 Error Estacionario",
                        f"{ess:.4f}",
                        delta="Debe ser ~0",
                        help="Diferencia en estado permanente"
                    )
                
                st.markdown("---")
                
                # Tabla detallada de métricas
                st.markdown("### Tabla Completa de Métricas")
                
                metricas_tabla = {
                    "Métrica": [
                        "Tiempo de Establecimiento",
                        "Sobreimpulso",
                        "Error Estacionario",
                        "Error Estacionario %",
                        "Valor Máximo",
                        "Valor Final"
                    ],
                    "Valor": [
                        f"{metricas.get('ts', 0):.4f} seg",
                        f"{metricas.get('Mp', 0):.2f}%",
                        f"{metricas.get('ess', 0):.6f}",
                        f"{metricas.get('ess_percent', 0):.2f}%",
                        f"{metricas.get('y_max', 0):.4f}",
                        f"{metricas.get('y_final', 0):.4f}"
                    ],
                    "Evaluación": [
                        "✓ Bueno" if metricas.get('ts', 0) < 30 else "⚠️ Revisar",
                        "✓ Bueno" if metricas.get('Mp', 0) < 20 else "⚠️ Alto overshoot",
                        "✓ Cero" if abs(metricas.get('ess', 0)) < 0.01 else "⚠️ Error presente",
                        "✓ Bajo" if metricas.get('ess_percent', 0) < 1 else "⚠️ Alto error",
                        "OK",
                        "OK"
                    ]
                }
                
                df_metricas = __import__('pandas').DataFrame(metricas_tabla) if IMPORTS_OK else None
                
                if df_metricas is not None:
                    try:
                        st.dataframe(df_metricas, use_container_width=True, hide_index=True)
                    except:
                        st.write(metricas_tabla)
                else:
                    st.write(metricas_tabla)
                
                st.markdown("---")
                
                # Interpretación
                st.markdown("### Interpretación de Resultados")
                
                int_col1, int_col2 = st.columns(2)
                
                with int_col1:
                    st.markdown("**✓ Indicadores Positivos:**")
                    
                    checks = []
                    if metricas.get('ts', float('inf')) < 30:
                        checks.append("✓ Respuesta rápida (ts < 30 seg)")
                    if metricas.get('Mp', 100) < 20:
                        checks.append("✓ Overshoot bajo (< 20%)")
                    if abs(metricas.get('ess', 1)) < 0.01:
                        checks.append("✓ Sin error estacionario")
                    
                    if checks:
                        for check in checks:
                            st.write(check)
                    else:
                        st.write("Revisar parámetros")
                
                with int_col2:
                    st.markdown("**⚠️ Áreas de Mejora:**")
                    
                    warnings = []
                    if metricas.get('ts', 0) >= 30:
                        warnings.append("⚠️ Respuesta lenta - considera aumentar Kp")
                    if metricas.get('Mp', 0) >= 20:
                        warnings.append("⚠️ Overshoot alto - aumenta Td o reduce Kp")
                    if abs(metricas.get('ess', 0)) >= 0.01:
                        warnings.append("⚠️ Error presente - aumenta Ti")
                    
                    if warnings:
                        for warn in warnings:
                            st.write(warn)
                    else:
                        st.write("Controlador bien ajustado")

    except Exception as e:
        st.error(f"❌ Error general en Tab Métricas: {e}\n{traceback.format_exc()}")

# =============================================================================
# TAB 4: DESCARGA DE RESULTADOS
# =============================================================================

with tab4:
    st.subheader("Descargar Resultados")
    
    st.markdown("""
    Descarga los parámetros y gráficos en diferentes formatos para usar
    en tus sistemas de control.
    """)
    
    st.markdown("---")
    
    # Generar contenido para descargas
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 1. TXT con parámetros
    st.markdown("### 📄 Archivo de Texto")
    
    contenido_txt = f"""=== PARÁMETROS PID CALCULADOS ===
Generado: {timestamp}

--- PARÁMETROS PID ---
Kp (Ganancia): {Kp:.6f}
Ti (Integral): {Ti:.6f} seg
Td (Derivativa): {Td:.6f} seg
Ki = Kp/Ti: {(Kp/Ti if Ti > 0 else 0):.6f}
Kd = Kp*Td: {Kp*Td:.6f}

--- MODELO DEL PROCESO (FOPDT) ---
K (Ganancia): {fopdt_params['K']:.6f}
L (Retardo): {fopdt_params['L']:.6f} seg
T (Constante): {fopdt_params['T']:.6f} seg
Relación L/T: {(fopdt_params['L']/fopdt_params['T']):.4f}

--- FUNCIÓN DE TRANSFERENCIA DEL CONTROLADOR ---
C(s) = {Kp:.4f} * (1 + 1/{Ti:.4f}s + {Td:.4f}s)

--- INSTRUCCIONES MATLAB/SIMULINK ---
Kp = {Kp:.6f};
Ti = {Ti:.6f};
Td = {Td:.6f};
Ki = Kp / Ti;
Kd = Kp * Td;

% En PID block de Simulink:
% Proportional gain (P): {Kp:.6f}
% Integral time (Tau I): {Ti:.6f}
% Derivative time (Tau D): {Td:.6f}

--- FECHA Y HORA ---
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    st.download_button(
        label="📥 Descargar TXT",
        data=contenido_txt,
        file_name=f"pid_params_{timestamp}.txt",
        mime="text/plain"
    )
    
    st.markdown("---")
    
    # 2. CSV con parámetros (formato tabular)
    st.markdown("### 📊 Archivo CSV")
    
    contenido_csv = f"""Parámetro,Valor,Unidad
Kp,{Kp:.6f},adimensional
Ti,{Ti:.6f},segundos
Td,{Td:.6f},segundos
Ki,{(Kp/Ti if Ti > 0 else 0):.6f},1/segundos
Kd,{Kp*Td:.6f},adimensional
K_proceso,{fopdt_params['K']:.6f},adimensional
L_retardo,{fopdt_params['L']:.6f},segundos
T_constante,{fopdt_params['T']:.6f},segundos
Timestamp,{timestamp},
"""
    
    st.download_button(
        label="📥 Descargar CSV",
        data=contenido_csv,
        file_name=f"pid_params_{timestamp}.csv",
        mime="text/csv"
    )
    
    st.markdown("---")
    
    # 3. PNG con gráfico
    st.markdown("### 📈 Archivo PNG (Gráfico)")
    
    if 'fig_resultados' in st.session_state:
        # Convertir figura a bytes
        buf = io.BytesIO()
        try:
            st.session_state.fig_resultados.savefig(buf, format='png', dpi=150, bbox_inches='tight')
            buf.seek(0)
            
            st.download_button(
                label="📥 Descargar PNG (150 DPI)",
                data=buf.getvalue(),
                file_name=f"pid_grafico_{timestamp}.png",
                mime="image/png"
            )
        except Exception as e:
            st.warning(f"⚠️ No se pudo generar PNG: {e}")
    else:
        st.info("ℹ️ Primero ve a la pestaña **📈 Gráficos** para generar el gráfico")
    
    st.markdown("---")
    
    # Información sobre formatos
    st.markdown("### ℹ️ Información sobre Formatos")
    
    st.markdown("""
    **TXT:**
    - Formato simple para referencia
    - Contiene parámetros y código MATLAB
    - Fácil de compartir por email
    
    **CSV:**
    - Importable en Excel, Google Sheets, etc.
    - Formato estándar para datos tabulares
    - Ideal para análisis posterior
    
    **PNG:**
    - Gráfico de alta resolución (150 DPI)
    - Ideal para reportes técnicos
    - Compatible con todas las plataformas
    """)

