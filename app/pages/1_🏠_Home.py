"""
Página 1: Inicio y Bienvenida

Proporciona información sobre la herramienta y acceso rápido a ejemplos.
"""

import streamlit as st
import numpy as np
import sys
from pathlib import Path

# Setup
st.set_page_config(page_title="Home", page_icon="🏠")
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

st.title("PID Controller Tuner")
st.markdown("#### Computer-Aided Design Tool for PID Control Systems")

# Sección principal
st.markdown("""
## Fundamentals of PID Control

A **Proportional-Integral-Derivative (PID) controller** is a feedback mechanism that minimizes the error 
between a desired setpoint and the process measurement.

### Mathematical Definition

The error signal is defined as:
$$e(t) = r(t) - y(t)$$

where $r(t)$ is the reference signal and $y(t)$ is the process output.

The control action is given by:
$$u(t) = K_p \\cdot e(t) + K_i \\int_0^t e(\\tau)d\\tau + K_d \\frac{de(t)}{dt}$$

Alternatively, in terms of time constants:
$$u(t) = K_p \\left[ e(t) + \\frac{1}{T_i} \\int_0^t e(\\tau)d\\tau + T_d \\frac{de(t)}{dt} \\right]$$

### Parameter Interpretation

| Parameter | Meaning | Effect |
|-----------|---------|--------|
| **Kp** | Proportional gain | Immediate response to error |
| **Ti** | Integral time constant | Eliminates steady-state error |
| **Td** | Derivative time constant | Anticipates future error trends |

""")

st.markdown("---")

# Pestañas con diferente información
tab1, tab2, tab3, tab4 = st.tabs(["Tuning Methods", "Process Examples", "Performance Metrics", "Reference"])

# Tab 1: Métodos disponibles
with tab1:
    st.header("Tuning Methods")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Method: Ziegler-Nichols")
        
        st.markdown("""
        **Characteristics:**
        - Simple and rapid procedure
        - Based on step response analysis
        - Optimized for system response speed
        
        **Limitations:**
        - Produces 20-25% overshoot
        - Initial oscillations
        - Limited applicability for multiple objective criteria
        
        **Recommended for:**
        - Fast-responding processes
        - When precise regulation is not critical
        - Initial controller tuning estimates
        
        **Tuning Formulas (P control):**
        - $K_p = \\frac{1.2T}{L \\cdot K}$
        - $T_i = 2L$
        - $T_d = 0.5L$
        """)
    
    with col2:
        st.subheader("Method: Cohen-Coon")
        
        st.markdown("""
        **Characteristics:**
        - More sophisticated than Ziegler-Nichols
        - Produces 10-15% overshoot
        - Better disturbance rejection capability
        - Three optimization criteria available
        
        **Advantages:**
        - Superior setpoint tracking
        - Reduced oscillations
        - Flexible criterion selection
        
        **Recommended for:**
        - Critical control applications
        - When precision is required
        - Slow time-varying systems
        
        **Optimization Criteria:**
        - **IAE**: Integral Absolute Error (balanced)
        - **ISE**: Integral Squared Error (penalizes peaks)
        - **ITAE**: Time-weighted Error (faster transients)
        """)


# Tab 2: Ejemplos precargados
with tab2:
    st.header("Benchmark Process Models")
    
    # Selector de ejemplos
    ejemplo = st.selectbox(
        "Select a process model:",
        [
            "Heating System (Heating/Cooling)",
            "DC Motor (First-Order Response)",
            "Mixing Tank (Chemical Process)",
            "Industrial Furnace (High-Order Response)"
        ]
    )
    
    ejemplos_data = {
        "Heating System (Heating/Cooling)": {
            "description": "Typical first-order system with transport delay",
            "K": 2.0,
            "L": 2.0,
            "T": 10.0,
            "unidades": "°C per % power input",
            "model": "FOPDT: $G(s) = \\frac{2e^{-2s}}{10s+1}$"
        },
        "DC Motor (First-Order Response)": {
            "description": "Low-order motor model with negligible delay",
            "K": 1.0,
            "L": 0.1,
            "T": 5.0,
            "unidades": "RPM per Volt",
            "model": "FOPDT: $G(s) = \\frac{1e^{-0.1s}}{5s+1}$"
        },
        "Mixing Tank (Chemical Process)": {
            "description": "Typical chemical industry process",
            "K": 3.0,
            "L": 1.0,
            "T": 8.0,
            "unidades": "L/min per % valve opening",
            "model": "FOPDT: $G(s) = \\frac{3e^{-s}}{8s+1}$"
        },
        "Industrial Furnace (High-Order Response)": {
            "description": "Slow process with significant transport delay",
            "K": 1.5,
            "L": 5.0,
            "T": 15.0,
            "unidades": "°C per % burner input",
            "model": "FOPDT: $G(s) = \\frac{1.5e^{-5s}}{15s+1}$"
        }
    }
    
    if ejemplo in ejemplos_data:
        data = ejemplos_data[ejemplo]
        
        st.markdown(f"**Process Description:** {data['description']}")
        
        # Mathematical model
        st.markdown(f"**Mathematical Model:** {data['model']}")
        
        col1, col2, col3  = st.columns(3)
        with col1:
            st.metric("Steady-State Gain (K)", data['K'], "units/input%")
        with col2:
            st.metric("Transport Delay (L)", data['L'], "seconds")
        with col3:
            st.metric("Time Constant (T)", data['T'], "seconds")
        
        st.markdown(f"**Output Units:** {data['unidades']}")
        
        if st.button("Load this model in Designer"):
            st.session_state.ejemplo_seleccionado = data
            st.success("Model loaded. Go to Designer tab to proceed.")


# Tab 3: Conceptos
with tab3:
    st.header("Performance Specifications")
    
    concept_exp = st.expander("Settling Time (ts)")
    with concept_exp:
        st.markdown("""
        **Definition:** The time required for the response to remain within a tolerance band 
        (typically ±2%) around the steady-state value.
        
        **Interpretation:**
        - Small $t_s$ → Fast system response
        - Large $t_s$ → Slow system response
        
        **Approximate Formula (2nd-order system):**
        $$t_s \\approx \\frac{-5}{\\zeta \\omega_n}$$
        
        where $\\zeta$ is the damping ratio and $\\omega_n$ is the natural frequency.
        
        **Context:**
        $$\\zeta = \\frac{T_d}{\\sqrt{T_d T_i}}, \\quad \\omega_n = \\frac{1}{\\sqrt{T_d T_i}}$$
        """)
    
    concept_exp2 = st.expander("Overshoot (Mp %)")
    with concept_exp2:
        st.markdown("""
        **Definition:** The maximum percent by which the response exceeds the reference value.
        
        $$M_p = \\frac{\\max(y(t)) - y_{\\infty}}{|y_{\\infty}|} \\times 100 \\%$$
        
        **Interpretation:**
        - $M_p = 0\\%$ → No overshoot (critically damped)
        - $M_p \\in [5\\%, 10\\%]$ → Good for most applications
        - $M_p \\approx 20\\%$ → Typical Ziegler-Nichols result
        - $M_p > 50\\%$ → Poorly tuned controller
        
        **Damping Relationship:**
        $$M_p \\approx e^{-\\frac{\\pi \\zeta}{\\sqrt{1-\\zeta^2}}} \\times 100 \\%$$
        """)
    
    concept_exp3 = st.expander("Steady-State Error (ess)")
    with concept_exp3:
        st.markdown("""
        **Definition:** The residual error that persists in steady-state operation.
        
        $$e_{ss} = \\lim_{t \\to \\infty} [r(t) - y(t)]$$
        
        **Interpretation:**
        - $e_{ss} \\approx 0$ → Perfect steady-state tracking
        - $e_{ss} > 0$ → P control has permanent error
        - **Requirement:** PI or PID: $e_{ss} \\to 0$ (integral action)
        
        **Error type vs. system type:**
        
        | Input Type | Type 0 | Type 1 | Type 2 |
        |------------|--------|--------|---------|
        | Step | Nonzero | 0 | 0 |
        | Ramp | ∞ | Nonzero | 0 |
        | Parabolic | ∞ | ∞ | Nonzero |
        """)


# Tab 4: Algoritmos
with tab4:
    st.header("Implementation Reference")
    
    ref_col1, ref_col2 = st.columns(2)
    
    with ref_col1:
        st.markdown("""
        ### Algorithm: Ziegler-Nichols
        
        **Procedure:**
        1. Apply step input to process
        2. Record Process Step Response
        3. Identify FOPDT parameters (K, L, T)
        4. Apply ZN tuning formulas
        
        **Process Identification:**
        - Use tangent method or numerical fitting
        - FOPDT model: $G_p(s) = \\frac{Ke^{-Ls}}{Ts + 1}$
        
        **PID Formulas:**
        - $K_p = \\frac{1.2T}{LK}$
        - $T_i = 2L$
        - $T_d = 0.5L$
        
        **Validation Checks:**
        ✓ $K > 0$ (positive gain)
        ✓ $L \\geq 0$ (non-negative delay)
        ✓ $T > 0$ (positive time constant)
        ✓ $L/T < 0.5$ (ratio constraint)
        """)
    
    with ref_col2:
        st.markdown("""
        ### Algorithm: Cohen-Coon
        
        **Procedure:**
        1. Identify FOPDT model (same as ZN)
        2. Calculate ratio: $r = L/T$
        3. If $r < 0.3$: use simple formulas
        4. If $r \\geq 0.3$: use general formulas
        5. Select optimization criterion (IAE/ISE/ITAE)
        
        **Optimization Criteria Effects:**
        - IAE: Balanced control (preferred)
        - ISE: Penalizes large errors
        - ITAE: Reduces late-time oscillations
        
        **Advantages over ZN:**
        ✓ Lower overshoot (10-15%)
        ✓ Better disturbance rejection
        ✓ Flexible performance objectives
        ✓ Suitable for critical applications
        """)

st.markdown("---")

# Footer
st.markdown("""
<div style='text-align: center; margin-top: 3rem; border-top: 1px solid #ccc; padding-top: 2rem;'>
    <h5>Getting Started</h5>
    <p>Refer to <strong>Tuning Methods</strong> tab for detailed algorithm descriptions.</p>
    <p>Or start directly in the <strong>Designer</strong> module to compute your PID parameters.</p>
</div>
""", unsafe_allow_html=True)
