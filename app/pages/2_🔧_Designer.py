"""
Página 2: Diseñador - Ingreso de Parámetros y Cálculo

Permite al usuario ingresar función de transferencia, seleccionar método
y calcular parámetros PID con integración real del backend.
"""

import streamlit as st
import numpy as np
import sys
import traceback
from pathlib import Path

# Setup
st.set_page_config(page_title="Designer", page_icon="🔧", layout="wide")
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Intentar importar módulos REALES del backend
try:
    from src.core.transfer_function import (
        create_transfer_function, 
        is_stable, 
        get_dc_gain, 
        get_poles,
        InvalidTransferFunctionError
    )
    from src.tuning.ziegler_nichols import sintonia_pid_ziegler_nichols, TuningError as ZNError
    from src.tuning.cohen_coon import sintonia_pid_cohen_coon, TuningError as CCError
    IMPORTS_OK = True
except ImportError as e:
    st.error(f"Critical import error: {e}")
    st.error("Ensure modules are located in src/")
    IMPORTS_OK = False

st.title("PID Controller Designer")
st.markdown("#### Transfer Function Analysis and Automatic Tuning")

# Inicializar variables
numerador = []
denominador = []
K, L, T = None, None, None
metodo = None
control_type = None
criterio = None

# Layout: Sidebar para entrada
with st.sidebar:
    st.header("Input Parameters")
    
    # Sección 1: Función de Transferencia
    st.subheader("1. Process Transfer Function")
    st.markdown("Enter: G(s) = Numerator / Denominator")
    
    # Opción: cargar ejemplo o ingresar manual
    entrada_tipo = st.radio(
        "Input method:",
        ["Manual Entry", "Preset Example", "FOPDT (K, L, T)"],
        horizontal=True
    )
    
    if entrada_tipo == "Manual Entry":
        st.markdown("**Format:** Coefficients in descending power order, space-separated")
        
        try:
            numerador_str = st.text_input(
                "Numerator (e.g.: '1 2.5' for s+2.5)",
                value="1",
                help="Coefficients in descending power order"
            )
            denominador_str = st.text_input(
                "Denominator (e.g.: '10 1' for 10s+1)",
                value="10 1",
                help="Coefficients in descending power order"
            )
            
            if numerador_str.strip():
                numerador = [float(x.strip()) for x in numerador_str.split() if x.strip()]
            if denominador_str.strip():
                denominador = [float(x.strip()) for x in denominador_str.split() if x.strip()]
                
        except ValueError as e:
            st.error(f"Format error: {e}. Use only numbers and spaces.")
    
    elif entrada_tipo == "Preset Example":
        ejemplo_sel = st.selectbox(
            "Choose a preset:",
            ["Heating (K=2, L=2, T=10)", "DC Motor (K=1, L=0.5, T=5)", "Tank (K=3, L=1, T=8)"]
        )
        
        ejemplos = {
            "Heating (K=2, L=2, T=10)": ([2], [10, 1], {"K": 2.0, "L": 2.0, "T": 10.0}),
            "DC Motor (K=1, L=0.5, T=5)": ([1], [5, 1], {"K": 1.0, "L": 0.5, "T": 5.0}),
            "Tank (K=3, L=1, T=8)": ([3], [8, 1], {"K": 3.0, "L": 1.0, "T": 8.0})
        }
        
        if ejemplo_sel in ejemplos:
            numerador, denominador, fopdt_ejemplo = ejemplos[ejemplo_sel]
            st.session_state.fopdt_params = fopdt_ejemplo
            st.success(f"Preset loaded: {ejemplo_sel}")
    
    else:  # FOPDT
        st.markdown("**Modelo FOPDT:** G(s) = K/(Ts+1) × e^(-Ls)")
        
        K = st.number_input("K (Ganancia DC)", value=2.0, min_value=0.01, max_value=100.0, 
                           help="Ganancia del proceso")
        L = st.number_input("L (Retardo) [seg]", value=2.0, min_value=0.0, max_value=1000.0,
                           help="Tiempo muerto / retardo de transporte")
        T = st.number_input("T (Constante tiempo) [seg]", value=10.0, min_value=0.01, max_value=1000.0,
                           help="Constante de tiempo del proceso")
        
        # Guardar parámetros FOPDT (ignorar retardo en TF, usar solo para sintonización)
        numerador = [K]
        denominador = [T, 1.0]
        st.session_state.fopdt_params = {"K": K, "L": L, "T": T}
    
    # Sección 2: Método de Sintonización
    st.subheader("2️⃣ Método de Sintonización")
    
    metodo = st.radio(
        "Select method:",
        ["Ziegler-Nichols", "Cohen-Coon"],
        help="ZN: Fast, ~20% overshoot | CC: Precise, ~10% overshoot"
    )
    
    control_type = st.radio(
        "Controller type:",
        ["PI", "PID"],
        horizontal=True,
        help="PI: No derivative | PID: With derivative (smoother)"
    )
    
    # Opciones específicas por método
    criterio = None
    if metodo == "Cohen-Coon":
        criterio = st.select_slider(
            "Optimization criterion:",
            options=["IAE", "ISE", "ITAE"],
            value="IAE",
            help="IAE: Balanced (recommended) | ISE: Penalizes large errors | ITAE: Penalizes transients"
        )
    
    # Opciones avanzadas
    with st.expander("Advanced Options", expanded=False):
        st.markdown("**Settings:**")
        st.session_state.mostrar_banda = st.checkbox("Show ±2% band in plots", value=True)
        st.session_state.tolerance = st.slider("Settling time tolerance:", 0.01, 0.10, 0.02, step=0.01)
        st.session_state.show_verification = st.checkbox("Show stability verification", value=True)
    
    # Botón de cálculo
    st.markdown("---")
    if not IMPORTS_OK:
        st.error("Error: Modules not available. Cannot compute.")
        calcular = False
    else:
        calcular = st.button(
            "COMPUTE PID",
            use_container_width=True,
            type="primary"
        )

# ============================================================================
# PANEL PRINCIPAL (DERECHA) - CÁLCULO Y RESULTADOS
# ============================================================================

if calcular and numerador and denominador:
    # Crear dos columnas: resultados principal e info compacta
    col_main, col_info = st.columns([3, 1])
    
    # Validación de entrada
    try:
        if len(denominador) == 0 or all(c == 0 for c in denominador):
            st.error("❌ El denominador no puede estar vacío o ser todo ceros")
        elif len(numerador) == 0:
            st.error("❌ El numerador no puede estar vacío")
        else:
            # ========== PASO 1: Crear función de transferencia ==========
            with col_main:
                with st.spinner("Creando función de transferencia..."):
                    try:
                        tf = create_transfer_function(numerador, denominador)
                        st.session_state.transfer_function = tf
                        
                    except InvalidTransferFunctionError as e:
                        st.error(f"""
                        ❌ **Error en función de transferencia:**
                        
                        {str(e)}
                        
                        **Comprueba:**
                        - Numerador y denominador no pueden estar vacíos
                        - Denominador no puede ser todo ceros
                        - Solo usa números reales
                        """)
                        st.stop()
                    except Exception as e:
                        st.error(f"""
                        ❌ **Error inesperado** al crear función de transferencia:
                        
                        {str(e)}
                        
                        Stacktrace: {traceback.format_exc()}
                        """)
                        st.stop()
            
            # ========== PASO 2: Verificar estabilidad ==========
            with col_info:
                st.markdown("### Verification")
                try:
                    stable = is_stable(tf)
                    # Asegurar que stable es bool
                    stable = bool(stable) if hasattr(stable, '__len__') is False else stable
                    if stable:
                        st.success("Stable")
                    else:
                        st.error("Unstable")
                except Exception as e:
                    st.warning(f"Stability check failed: {e}")
                
                # DC Gain
                try:
                    dc_gain_value = get_dc_gain(tf)
                    # Convertir a float si es array
                    dc_gain = float(np.asarray(dc_gain_value).flat[0])
                    st.metric("DC Gain", f"{dc_gain:.3f}")
                except Exception as e:
                    st.warning(f"DC Gain: {e}")
            
            # ========== PASO 3: Obtener parámetros FOPDT ==========
            try:
                if st.session_state.get('fopdt_params'):
                    fopdt = st.session_state.fopdt_params
                    K, L, T = fopdt["K"], fopdt["L"], fopdt["T"]
                else:
                    # Aproximación a partir de la TF (método simple)
                    try:
                        dc_gain_value = get_dc_gain(tf)
                        K = float(np.asarray(dc_gain_value).flat[0])  # Convertir array a float
                        
                        poles = get_poles(tf)
                        L = 0.1  # Retardo default
                        
                        # Obtener el primer polo (más lento)
                        if len(poles) > 0:
                            first_pole = complex(poles[0])  # Convertir a escalar complejo
                            real_part = float(first_pole.real)
                            
                            # Verificar que real_part es diferente de cero (sin comparación ambigua)
                            if abs(real_part) > 1e-10:
                                T = abs(-1.0 / real_part)
                            else:
                                T = 10.0
                        else:
                            T = 10.0
                        
                        st.session_state.fopdt_params = {"K": K, "L": L, "T": T}
                    except Exception as e:
                        st.warning(f"⚠️ No se pudieron estimar parámetros FOPDT: {e}")
                        st.stop()
            
            except Exception as e:
                st.error(f"❌ Error al procesar parámetros FOPDT: {e}")
                st.stop()
            
            # ========== PASO 4: Calcular PID ==========
            with col_main:
                with st.spinner(f"Computing PID using {metodo}..."):
                    try:
                        if metodo == "Ziegler-Nichols":
                            Kp, Ti, Td = sintonia_pid_ziegler_nichols(
                                K=K, L=L, T=T, 
                                control_type=control_type
                            )
                        else:  # Cohen-Coon
                            Kp, Ti, Td = sintonia_pid_cohen_coon(
                                K=K, L=L, T=T,
                                criterion=criterio,
                                control_type=control_type
                            )
                        
                        # Validar resultados
                        if not (isinstance(Kp, (int, float)) and isinstance(Ti, (int, float)) and isinstance(Td, (int, float))):
                            raise ValueError("PID parameters must be numbers")
                        
                        if Kp <= 0 or Ti < 0 or Td < 0:
                            raise ValueError("PID parameters must be non-negative (Kp > 0)")
                        
                        # Guardar en session state
                        st.session_state.pid_params = {"Kp": Kp, "Ti": Ti, "Td": Td}
                        
                    except (ZNError, CCError) as e:
                        st.error(f"""
                        **Tuning Error ({metodo}):**
                        
                        {str(e)}
                        
                        **Solutions:**
                        - Verify K, L, T are positive
                        - K must be > 0
                        - Try typical values: K ∈ [0.5, 5], T ∈ [1, 100]
                        """)
                        st.stop()
                    except Exception as e:
                        st.error(f"""
                        **Unexpected Error in PID Computation:**
                        
                        {str(e)}
                        
                        Stack: {traceback.format_exc()}
                        """)
                        st.stop()
                
                # ========== PASO 5: Mostrar resultados ==========
                st.success("Successfully computed.")
                
                st.markdown("### Computed PID Parameters")
                
                res_col1, res_col2, res_col3 = st.columns(3)
                
                with res_col1:
                    st.metric(
                        "Proportional Gain (Kp)",
                        f"{Kp:.4f}",
                        "P gain"
                    )
                
                with res_col2:
                    st.metric(
                        "Integral Time (Ti)",
                        f"{Ti:.4f} s" if Ti > 0 else "∞ (P/D only)",
                        "Integral time"
                    )
                
                with res_col3:
                    st.metric(
                        "Derivative Time (Td)",
                        f"{Td:.4f} s" if Td > 0 else "0 (P/I only)",
                        "Derivative time"
                    )
                
                # Ecuación del controlador
                st.markdown("### Controller Transfer Function")
                
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
                
                # Información del método
                st.markdown("---")
                st.markdown("### Computation Information")
                
                info_text = f"""
                - **Method:** {metodo}
                - **Controller Type:** {control_type}
                - **FOPDT Model:** K={K:.3f}, L={L:.3f}s, T={T:.3f}s
                - **Delay Ratio (L/T):** {(L/T):.3f}
                """
                
                if metodo == "Cohen-Coon":
                    criterio_desc = {
                        "IAE": "Integral Absolute Error (balanced)",
                        "ISE": "Integral Squared Error (penalizes peaks)",
                        "ITAE": "Time-weighted Error (penalizes transients)"
                    }
                    info_text += f"- **Criterion:** {criterio} ({criterio_desc.get(criterio, 'unknown')})\n"
                
                st.markdown(info_text)
                
                # Botón para ver resultados
                st.markdown("---")
                st.info("Next step: Go to Results tab to view plots, simulation, and metrics")
    
    except Exception as e:
        st.error(f"""
        ❌ **Error general no manejado:**
        
        {str(e)}
        
        Stacktrace completo:
        ```
        {traceback.format_exc()}
        ```
        """)

elif calcular and not (numerador and denominador):
    st.warning("⚠️ Por favor ingresa numerador y denominador válidos")

# Información y ayuda
st.markdown("---")

with st.expander("ℹ️ Ayuda - ¿Cómo ingresar la función?"):
    st.markdown("""
    ### Formato de Entrada
    
    Los coeficientes se ingresan en **orden descendente de potencia**:
    
    | Función Deseada | Numerador | Denominador |
    |-----------------|-----------|-------------|
    | 1/(s+1) | `1` | `1 1` |
    | 2/(s+1) | `2` | `1 1` |
    | (s+2)/(s²+3s+2) | `1 2` | `1 3 2` |
    | 1/(10s+1) | `1` | `10 1` |
    | Kp/(Ts+1) | `Kp` | `T 1` |
    
    ### Notas Importantes
    - **Separador:** Espacios entre coeficientes
    - **Orden:** De mayor a menor potencia de s
    - **Ejemplo:** Para G(s) = 2/(5s+1), ingresa Num=`2`, Den=`5 1`
    
    ### Validaciones Automáticas
    - ✓ Comprobación de estabilidad (polos en semiplano izquierdo)
    - ✓ Cálculo de ganancia DC
    - ✓ Verificación de parámetros PID válidos
    """)

with st.expander("📖 Métodos de Sintonización"):
    st.markdown("""
    ### Ziegler-Nichols
    - **Ventaja:** Rápido y simple
    - **Desventaja:** Overshoot ~20-25%
    - **Uso:** Primera aproximación, sistemas no críticos
    
    ### Cohen-Coon  
    - **Ventaja:** Menor overshoot (~10-15%), mejor rechazo perturbaciones
    - **Desventaja:** Más complejo
    - **Uso:** Sistemas críticos (temperatura, presión)
    
    ### Criterios Cohen-Coon
    - **IAE:** Equilibrado, buen compromiso
    - **ISE:** Penaliza errores grandes, menos picos
    - **ITAE:** Penaliza transitorios tardíos, respuesta más rápida
    """)

