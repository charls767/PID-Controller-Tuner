"""
Página 4: Documentación - Teoría y Referencia

Proporciona documentación educativa sobre PID, métodos
y conceptos de control.
"""

import streamlit as st

# Setup
st.set_page_config(page_title="Documentation", page_icon="📖")

st.title("Technical Documentation")
st.markdown("#### Theory, Methods, and Reference Material")

# Tabs de contenido
tab1, tab2, tab3, tab4 = st.tabs(["PID Theory", "Tuning Methods", "FOPDT Model", "Examples"])

# TAB 1: Teoría PID
with tab1:
    st.header("PID Controller Fundamentals")
    
    st.markdown("""
    A **PID (Proportional-Integral-Derivative) controller** is a feedback control mechanism that:
    
    1. **Measures** the error between reference setpoint and actual output
    2. **Calculates** proportional, integral, and derivative components
    3. **Applies** a combined control action
    
    ### General Mathematical Equation
    
    $$u(t) = K_p e(t) + K_i \\int_0^t e(\\tau)d\\tau + K_d \\frac{de(t)}{dt}$$
    
    Where:
    - **e(t)** = error = r(t) - y(t)
    - **Kp** = proportional gain
    - **Ki** = integral gain  
    - **Kd** = derivative gain
    
    ### Transfer Function Form
    
    $$C(s) = K_p \\left(1 + \\frac{1}{T_i s} + T_d s\\right)$$
    
    Where:
    - **Ti** = Kp/Ki (integral time constant)
    - **Td** = Kd/Kp (derivative time constant)
    """)
    
    # 3 columnas: P, I, D
    st.markdown("---")
    st.subheader("Componentes del PID")
    
    col_p, col_i, col_d = st.columns(3)
    
    with col_p:
        st.markdown("""
        ### P - Proporcional
        
        **Función:**
        - Respuesta instantánea al error
        - Proporcional al error actual
        
        **Efecto:**
        - Reduce el error rápidamente
        - **No elimina error final** (offset)
        - Más rápido, menos preciso
        
        **Fórmula:**
        $$u_P = K_p \\cdot e(t)$$
        
        **Problema:** Offset en estado permanente
        """)
    
    with col_i:
        st.markdown("""
        ### I - Integral
        
        **Función:**
        - Acumula el error histórico
        - Proporcional a la integral del error
        
        **Efecto:**
        - **Elimina error en estado permanente**
        - Respuesta más lenta
        - Puede causar oscilación
        
        **Fórmula:**
        $$u_I = K_i \\int_0^t e(\\tau)d\\tau$$
        
        **Beneficio:** ess → 0
        """)
    
    with col_d:
        st.markdown("""
        ### D - Derivativa
        
        **Función:**
        - Anticipa cambios futuros
        - Proporcional a la velocidad del error
        
        **Efecto:**
        - Reduce overshoot
        - Mejora estabilidad
        - Sensible al ruido
        
        **Fórmula:**
        $$u_D = K_d \\frac{de(t)}{dt}$$
        
        **Beneficio:** Menor Mp, más suave
        """)
    
    # Tabla comparativa
    st.markdown("---")
    st.subheader("Comparación de Tipos")
    
    st.dataframe({
        "Tipo": ["P", "PI", "PID"],
        "Error Final": ["✗ Offset", "✓ Cero", "✓ Cero"],
        "Velocidad": ["Rápido", "Medio", "Medio"],
        "Overshoot": ["Bajo", "Medio", "Bajo"],
        "Complejidad": ["Baja", "Media", "Alta"]
    }, use_container_width=True)

# TAB 2: Métodos
with tab2:
    st.subheader("Métodos de Sintonización")
    
    metodo_sel = st.radio(
        "Elige un método:",
        ["Ziegler-Nichols", "Cohen-Coon", "Comparación"],
        horizontal=True
    )
    
    if metodo_sel == "Ziegler-Nichols":
        st.markdown("""
        ## Método de Ziegler-Nichols (ZN)
        
        ### Historia
        Propuesto por John Ziegler y Nathaniel Nichols en 1942.
        Uno de los primeros métodos prácticos de sintonización.
        
        ### Características
        - ✓ Simple y directo
        - ✓ Basado en respuesta al escalón
        - ✓ Rápido de implementar
        - ✗ Overshoot ~20-25%
        - ✗ Oscilaciones iniciales
        
        ### Procedimiento
        1. Aplicar entrada escalón unitario
        2. Registrar respuesta en lazo abierto
        3. Identificar modelo FOPDT: G(s) = K/(Ts+1) × e^(-Ls)
        4. Aplicar fórmulas
        
        ### Fórmulas ZN para FOPDT
        
        **Control P:**
        $$K_p = \\frac{T}{LK}$$
        
        **Control PI:**
        $$K_p = 0.9 \\frac{T}{LK}, \\quad T_i = 3.33L$$
        
        **Control PID:**
        $$K_p = 1.2 \\frac{T}{LK}, \\quad T_i = 2L, \\quad T_d = 0.5L$$
        
        ### Ejemplo Numérico
        Para K=2, L=2, T=10:
        
        | Tipo | Kp | Ti | Td |
        |------|----|----|-----|
        | P | 5.0 | ∞ | 0 |
        | PI | 4.5 | 6.67 | 0 |
        | **PID** | **3.0** | **4.0** | **1.0** |
        
        ### Cuándo Usar
        - ✓ Procesos rápidos
        - ✓ Cuando prioritario es velocidad
        - ✓ Primera aproximación
        """)
    
    elif metodo_sel == "Cohen-Coon":
        st.markdown("""
        ## Método de Cohen-Coon (CC)
        
        ### Historia
        Propuesto por Cohen y Coon en 1953 como mejora a ZN.
        Basado optimización de criterios de error.
        
        ### Características
        - ✓ Mayor precisión que ZN
        - ✓ Menos overshoot (~10-15%)
        - ✓ Mejor rechazo de perturbaciones
        - ✓ 3 criterios (IAE, ISE, ITAE)
        - ✗ Fórmulas más complejas
        - ✗ Requiere identificación precisa
        
        ### Criterios Disponibles
        
        **IAE (Integral Absolute Error):**
        $$IAE = \\int_0^{\\infty} |e(t)| dt$$
        - Mejor para perturbaciones ruidosas
        - Balance general (recomendado)
        
        **ISE (Integral Squared Error):**
        $$ISE = \\int_0^{\\infty} e^2(t) dt$$
        - Penaliza errores grandes
        - Respuesta más agresiva
        
        **ITAE (Integral Time-weighted Absolute Error):**
        $$ITAE = \\int_0^{\\infty} t|e(t)| dt$$
        - Penaliza errores tardíos
        - Reduce transitorios finales
        
        ### Fórmulas CC
        
        Si r = L/T < 0.3 (fórmulas simplificadas):
        
        $$K_p = 1.35 \\frac{T}{LK}, \\quad T_i = 2.5L, \\quad T_d = 0.37L$$
        
        Si r ≥ 0.3 (fórmulas generales):
        
        $$K_p = \\frac{T}{LK}\\left(\\frac{4}{3} + \\frac{r}{4}\\right)$$
        
        $$T_i = L\\frac{32 + 6r}{13 + 8r}, \\quad T_d = \\frac{4L}{11 + 2r}$$
        
        ### Ejemplo
        Para K=2, L=2, T=10 (r=0.2):
        
        | Criterio | Kp | Ti | Td |
        |----------|----|----|-----|
        | IAE | 3.375 | 5.0 | 0.74 |
        | ISE | 3.738 | 3.14 | 1.47 |
        | ITAE | 2.148 | 1.35 | 0.27 |
        
        ### Cuándo Usar
        - ✓ Sistemas críticos
        - ✓ Cuando se requiere precisión
        - ✓ Procesos lento-variantes
        - ✓ Perturbaciones frecuentes
        """)
    
    else:  # Comparación
        st.markdown("""
        ## Comparación: Ziegler-Nichols vs Cohen-Coon
        
        | Aspecto | ZN | CC |
        |---------|----|----|
        | **Complejidad** | Simple | Compleja |
        | **Overshoot** | 20-25% | 10-15% |
        | **Oscilación** | Sí | Menos |
        | **Velocidad** | Rápida | Media |
        | **Precisión** | Media | Alta |
        | **Uso** | Inicial | Producción |
        | **Tiempo cálculo** | < 1 min | < 1 min |
        | **Robustez** | Buena | Excelente |
        
        ### Decir Cuál Usar
        
        **Usa Ziegler-Nichols si:**
        - Necesitas resultado rápido
        - La aplicación no es crítica
        - Puedes ajustar después
        - Requieres respuesta rápida
        
        **Usa Cohen-Coon si:**
        - Sistema crítico (temperatura, presión)
        - Necesitas bajo overshoot
        - Hay perturbaciones frecuentes
        - Presupuesto permite sintonización precisa
        """)

# TAB 3: FOPDT
with tab3:
    st.subheader("Modelo FOPDT")
    
    st.markdown("""
    ## First Order Plus Dead Time (FOPDT)
    
    El modelo FOPDT es la aproximación más común para procesos industriales.
    
    ### Ecuación
    
    $$G(s) = \\frac{K}{Ts+1} e^{-Ls}$$
    
    Donde:
    - **K** = Ganancia DC estática (unidades output/input)
    - **T** = Constante de tiempo [seg]
    - **L** = Retardo de transporte / tiempo muerto [seg]
    
    ### Interpretación Física
    
    - **K**: ¿Cuánto cambia la salida ante un cambio en entrada?
    - **T**: ¿Cuán rápido responde el sistema?
    - **L**: ¿Cuánto tiempo tarda en reaccionar?
    
    ### Ejemplos
    
    | Proceso | K | T [seg] | L [seg] | Descripción |
    |---------|---|--------|--------|-------------|
    | Calentador | 2.0 | 10.0 | 2.0 | Respuesta lenta, con retardo |
    | Motor DC | 1.0 | 5.0 | 0.5 | Respuesta rápida |
    | Tanque | 3.0 | 8.0 | 1.0 | Medio |
    | Horno | 1.5 | 15.0 | 5.0 | Muy lento |
    
    ### Cómo Identificar FOPDT
    
    1. **Aplicar** entrada escalón
    2. **Registrar** respuesta (5-10 veces la constante T)
    3. **Calcular:**
       - K = Δy/Δu (cambio en salida / cambio en entrada)
       - L = tiempo hasta que empieza a cambiar
       - T = identificar τ (aprox 63% del cambio final)
    
    ### Efectos de Parámetros
    
    | Parámetro | Efecto | Controlabilidad |
    |-----------|--------|-----------------|
    | K grande | Mayor sensibilidad | Fácil de controlar |
    | T grande | Respuesta lenta | Difícil de controlar |
    | L grande | Retardo significativo | Difícil de controlar |
    | L/T > 0.5 | Retardo domina | Muy difícil |
    """)

# TAB 4: Ejemplos
with tab4:
    st.subheader("Ejemplos Prácticos")
    
    ejemplo_sel = st.selectbox(
        "Elige un ejemplo:",
        [
            "Sistema de Calentamiento",
            "Motor DC",
            "Tanque de Mezcla"
        ]
    )
    
    if ejemplo_sel == "Sistema de Calentamiento":
        st.markdown("""
        ## Sistema de Calentamiento
        
        ### Descripción
        Horno eléctrico que calienta agua. Se controla la temperatura mediante
        potencia del elemento calefactor.
        
        ### Parámetros FOPDT
        - **K** = 2.0 °C por % de potencia
        - **L** = 2.0 seg (retardo del sensor)
        - **T** = 10.0 seg (constante térmica)
        
        ### Sintonización
        
        **Ziegler-Nichols:**
        - Kp = 3.000, Ti = 4.000, Td = 1.000
        - Overshoot: ~20%, ts: ~18 seg
        
        **Cohen-Coon (IAE):**
        - Kp = 3.375, Ti = 5.000, Td = 0.740
        - Overshoot: ~15%, ts: ~20 seg
        - Mejor balance, menos oscilación
        
        ### Aplicación
        ```
        Referencia: 70°C
        Controlador PI sintonizado con ZN
        Respuesta esperada: Alcanza ~87°C en 15 seg, baja a 70°C en otros 5 seg
        ```
        """)
    
    elif ejemplo_sel == "Motor DC":
        st.markdown("""
        ## Motor DC de Primer Orden
        
        ### Descripción
        Motor de corriente continua pequeño (ex: robot, ventilador).
        Controlado por voltaje, mide RPM.
        
        ### Parámetros FOPDT
        - **K** = 1.0 RPM por Voltio
        - **L** = 0.5 seg
        - **T** = 5.0 seg
        
        ### Sintonización
        
        **Recomendado: Cohen-Coon**
        - Mejor para precisión de velocidad
        - Respuesta sin sobre-picos
        
        ### Aplicación
        ```
        Referencia: 3000 RPM
        Controlador PID
        Respuesta: Suave, sin oscilación
        ```
        """)
    
    else:  # Tanque
        st.markdown("""
        ## Tanque de Mezcla
        
        ### Descripción
        Proceso común en industria química/alimentaria.
        Mezcla de dos líquidos, controla concentración por pH.
        
        ### Parámetros FOPDT
        - **K** = 3.0 (unidades de pH)
        - **L** = 1.0 seg
        - **T** = 8.0 seg
        
        ### Característica
        - Sistema muy no-lineal
        - Perturbaciones externas
        - Requiere sintonización robusta
        
        ### Recomendación
        **Usar Cohen-Coon con criterio ISE**
        - Penaliza sobre-picos grandes
        - Evita daño a producto
        """)

st.markdown("---")

st.markdown("""
<div style='text-align: center; color: #999; font-size: 0.9rem;'>
    <p><b>Referencias:</b></p>
    <p>Ziegler, J. G., & Nichols, N. B. (1942). IEEE Transactions on Automatic Control.</p>
    <p>Cohen, G. H., & Coon, G. A. (1953). Trans. ASME, 75(6), 827-834.</p>
</div>
""", unsafe_allow_html=True)
