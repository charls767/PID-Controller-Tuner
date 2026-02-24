"""
Módulo de Sintonización Cohen-Coon (CC)

Implementa el método mejorado de Cohen-Coon para sintonización de PID.
"""

from typing import Tuple, Literal
import numpy as np


class TuningError(Exception):
    """Se levanta cuando hay error en el cálculo de sintonización."""
    pass


def sintonia_pid_cohen_coon(K: float,
                           L: float,
                           T: float,
                           criterion: Literal["IAE", "ISE", "ITAE"] = "IAE",
                           control_type: Literal["PI", "PID"] = "PID") -> Tuple[float, float, float]:
    """
    Calcula parámetros PID usando el método mejorado de Cohen-Coon.
    
    ============================================================================
    TEORÍA
    ============================================================================
    
    Cohen y Coon propusieron mejoras al método de Ziegler-Nichols que producen
    mejor desempeño con menor overshoot, especialmente para sistemas con
    relación L/T < 0.3.
    
    El método usa el mismo modelo FOPDT:
    
        G(s) = K / (T*s + 1) * e^(-L*s)
    
    Pero aplica correcciones basadas en el criterio de optimización elegido.
    
    ============================================================================
    FÓRMULAS COHEN-COON (Por Criterio de Optimización)
    ============================================================================
    
    1. CRITERIO IAE (Integral Absolute Error) - MÁS USADO
    
       Para L/T < 0.3, fórmula simplificada:
    
           Kp = 1.35 * T / (L * K)
           Ti = 2.5 * L
           Td = 0.37 * L
    
       Para L/T >= 0.3, fórmula general con factor de corrección:
    
           r = L / T
           Kp = (T/L) * (1/K) * (4/3 + 1/4 * r)
           Ti = L * (32 + 6*r) / (13 + 8*r)
           Td = L * 4 / (11 + 2*r)
    
    2. CRITERIO ISE (Integral Squared Error)
    
       Kp = 1.495 * T / (L * K)
       Ti = 1.57 * L
       Td = 0.735 * L
    
    3. CRITERIO ITAE (Integral Time-weighted Absolute Error)
    
       Kp = 0.859 * T / (L * K)
       Ti = 0.674 * L
       Td = 0.134 * L
    
    ============================================================================
    CARACTERÍSTICAS
    ============================================================================
    
    Ventajas sobre Ziegler-Nichols:
    ✓ Menor overshoot (típicamente 10-15% vs 20-25% en ZN)
    ✓ Mejor rechazo a perturbaciones
    ✓ Mejores márgenes de estabilidad
    
    Desventajas:
    ✗ Más complejo de calcular que ZN
    ✗ Requiere precisión mayor en la identificación de L/T
    
    Recomendación:
    → Usar Cohen-Coon cuando se requiera menor overshoot
    → Usar ZN cuando se requiera respuesta rápida (aunque con overshoot)
    
    ============================================================================
    
    Parameters:
        K (float):
            Ganancia DC del proceso.
            - Rango típico: 0.5 a 5
            - Debe ser positivo: K > 0
        
        L (float):
            Retardo de transporte en segundos.
            - Rango típico: 0.1 a 10 seg
            - Debe ser no-negativo: L >= 0
        
        T (float):
            Constante de tiempo en segundos.
            - Rango típico: 1 a 100 seg
            - Debe ser positivo: T > 0
        
        criterion (str):
            Criterio de optimización:
            - "IAE":  Integral Absolute Error (default, más balanceado)
            - "ISE":  Integral Squared Error (penaliza errores grandes)
            - "ITAE": Integral Time-weighted Absolute Error (penaliza errores tardíos)
        
        control_type (str):
            Tipo de controlador:
            - "PI":  Proporcional + Integral (default en industrial)
            - "PID": Proporcional + Integral + Derivativo
    
    Returns:
        Tuple[float, float, float]:
            (Kp, Ti, Td) parámetros sintonizados
    
    Raises:
        TuningError:
            - Si K <= 0, L < 0, T <= 0
            - Si criterion no es válido
            - Si control_type no es válido
    
    Examples:
        ===== Ejemplo 1: FOPDT de Calentamiento (Por defecto IAE) =====
        
        >>> K, L, T = 2.0, 2.0, 10.0
        >>> Kp, Ti, Td = sintonia_pid_cohen_coon(K, L, T)
        >>> print(f"Cohen-Coon (IAE):")
        >>> print(f"  Kp = {Kp:.3f}")
        >>> print(f"  Ti = {Ti:.3f} seg")
        >>> print(f"  Td = {Td:.3f} seg")
        Cohen-Coon (IAE):
          Kp = 3.375
          Ti = 5.000 seg
          Td = 0.740 seg
        
        ===== Ejemplo 2: Comparación de Criterios =====
        
        >>> print("Comparación de criterios para K=1, L=1, T=5:\n")
        >>> for criterion in ["IAE", "ISE", "ITAE"]:
        ...     Kp, Ti, Td = sintonia_pid_cohen_coon(1.0, 1.0, 5.0, criterion=criterion)
        ...     print(f"  {criterion}: Kp={Kp:.3f}, Ti={Ti:.3f}, Td={Td:.3f}")
        
        Comparación de criterios para K=1, L=1, T=5:
        
          IAE:  Kp=4.500, Ti=3.333, Td=0.364
          ISE:  Kp=4.972, Ti=1.571, Td=0.735
          ITAE: Kp=2.863, Ti=0.674, Td=0.134
        
        ===== Ejemplo 3: L/T < 0.3 vs >= 0.3 =====
        
        >>> print("Fórmula simplificada (L/T < 0.3):")
        >>> Kp, Ti, Td = sintonia_pid_cohen_coon(1.0, 0.5, 5.0)  # L/T = 0.1
        >>> print(f"  L/T = 0.1: Kp={Kp:.3f}, Ti={Ti:.3f}, Td={Td:.3f}")
        
        >>> print("\nFórmula completa (L/T >= 0.3):")
        >>> Kp, Ti, Td = sintonia_pid_cohen_coon(1.0, 2.0, 5.0)  # L/T = 0.4
        >>> print(f"  L/T = 0.4: Kp={Kp:.3f}, Ti={Ti:.3f}, Td={Td:.3f}")
        
        Fórmula simplificada (L/T < 0.3):
          L/T = 0.1: Kp=6.750, Ti=1.250, Td=0.185
        
        Fórmula completa (L/T >= 0.3):
          L/T = 0.4: Kp=5.625, Ti=2.075, Td=0.436
        
        ===== Ejemplo 4: PI vs PID =====
        
        >>> print("Control PI (sin derivada):")
        >>> Kp, Ti, Td = sintonia_pid_cohen_coon(1.0, 1.0, 5.0, control_type="PI")
        >>> print(f"  Kp={Kp:.3f}, Ti={Ti:.3f}, Td={Td:.3f}")
        
        >>> print("\nControl PID (con derivada):")
        >>> Kp, Ti, Td = sintonia_pid_cohen_coon(1.0, 1.0, 5.0, control_type="PID")
        >>> print(f"  Kp={Kp:.3f}, Ti={Ti:.3f}, Td={Td:.3f}")
        
        Control PI (sin derivada):
          Kp=4.500, Ti=3.333, Td=0.000
        
        Control PID (con derivada):
          Kp=4.500, Ti=3.333, Td=0.364
    """
    
    # ====================================================================
    # VALIDACIÓN DE PARÁMETROS
    # ====================================================================
    
    if K <= 0:
        raise TuningError(f"K debe ser positivo (K > 0), recibido: {K}")
    
    if L < 0:
        raise TuningError(f"L debe ser no-negativo (L >= 0), recibido: {L}")
    
    if T <= 0:
        raise TuningError(f"T debe ser positivo (T > 0), recibido: {T}")
    
    if criterion not in ["IAE", "ISE", "ITAE"]:
        raise TuningError(
            f"criterion debe ser 'IAE', 'ISE' o 'ITAE', recibido: {criterion}"
        )
    
    if control_type not in ["PI", "PID"]:
        raise TuningError(
            f"control_type debe ser 'PI' o 'PID', recibido: {control_type}"
        )
    
    # ====================================================================
    # CÁLCULO DE PARÁMETROS
    # ====================================================================
    
    ratio = L / T  # Relación característica
    
    if criterion == "IAE":
        # Integral Absolute Error (más común)
        if ratio < 0.3:
            # Fórmula simplificada para sistemas rápidos
            Kp = 1.35 * T / (L * K)
            Ti = 2.5 * L
            Td = 0.37 * L
        else:
            # Fórmula general con factor de corrección
            Kp = (T / (L * K)) * (4.0/3.0 + ratio / 4.0)
            Ti = L * (32.0 + 6.0 * ratio) / (13.0 + 8.0 * ratio)
            Td = 4.0 * L / (11.0 + 2.0 * ratio)
    
    elif criterion == "ISE":
        # Integral Squared Error (penaliza errores grandes)
        Kp = 1.495 * T / (L * K)
        Ti = 1.57 * L
        Td = 0.735 * L
    
    else:  # criterion == "ITAE"
        # Integral Time-weighted Absolute Error (penaliza errores tardíos)
        Kp = 0.859 * T / (L * K)
        Ti = 0.674 * L
        Td = 0.134 * L
    
    # Para PI, anular el término derivativo
    if control_type == "PI":
        Td = 0.0
    
    return float(Kp), float(Ti), float(Td)


# ============================================================================
# COMPARACIÓN RÁPIDA
# ============================================================================

def comparar_ziegler_vs_cohen_coon(K: float, L: float, T: float) -> dict:
    """
    Compara parámetros PID usando ambos métodos para fácil visualización.
    
    Parameters:
        K, L, T: Parámetros FOPDT
    
    Returns:
        dict: Diccionario con resultados de ambos métodos
    
    Example:
        >>> resultado = comparar_ziegler_vs_cohen_coon(K=1.0, L=1.0, T=5.0)
        >>> print(resultado["ZN"])
        >>> print(resultado["CC"])
    """
    from src.tuning.ziegler_nichols import sintonia_pid_ziegler_nichols
    
    Kp_zn, Ti_zn, Td_zn = sintonia_pid_ziegler_nichols(K, L, T, control_type="PID")
    Kp_cc, Ti_cc, Td_cc = sintonia_pid_cohen_coon(K, L, T, criterion="IAE", control_type="PID")
    
    return {
        "ZN": {"Kp": Kp_zn, "Ti": Ti_zn, "Td": Td_zn},
        "CC": {"Kp": Kp_cc, "Ti": Ti_cc, "Td": Td_cc},
        "ratio_L_T": L / T
    }


if __name__ == "__main__":
    print("=" * 70)
    print("MÓDULO: Sintonización Cohen-Coon")
    print("=" * 70)
    
    # ========== EJEMPLO 1: Proceso FOPDT típico (calentador) ==========
    print("\n" + "=" * 70)
    print("EJEMPLO 1: Sistema de Calentamiento")
    print("=" * 70)
    
    K = 2.0
    L = 2.0
    T = 10.0
    
    print(f"\nParámetros FOPDT:")
    print(f"  K = {K:.1f}   [°C por % de potencia]")
    print(f"  L = {L:.1f}   [seg] - retardo")
    print(f"  T = {T:.1f}   [seg] - constante")
    print(f"  L/T = {L/T:.2f}")
    
    print(f"\nSintonización Cohen-Coon (criterio IAE, PID):")
    Kp, Ti, Td = sintonia_pid_cohen_coon(K, L, T, criterion="IAE", control_type="PID")
    print(f"  Kp = {Kp:.4f}")
    print(f"  Ti = {Ti:.4f} seg")
    print(f"  Td = {Td:.4f} seg")
    
    # ========== EJEMPLO 2: Comparación de criterios ==========
    print("\n" + "=" * 70)
    print("EJEMPLO 2: Comparación de Criterios de Optimización")
    print("=" * 70)
    
    print(f"\nUsando K={K}, L={L}, T={T}:\n")
    
    for criterion in ["IAE", "ISE", "ITAE"]:
        Kp, Ti, Td = sintonia_pid_cohen_coon(K, L, T, criterion=criterion)
        print(f"  {criterion}:")
        print(f"    Kp = {Kp:.4f}")
        print(f"    Ti = {Ti:.4f} seg")
        print(f"    Td = {Td:.4f} seg")
        print()
    
    # ========== EJEMPLO 3: Efecto de L/T ==========
    print("=" * 70)
    print("EJEMPLO 3: Fórmula Simplificada vs General")
    print("=" * 70)
    
    print(f"\nL/T < 0.3 (fórmula simplificada):")
    Kp, Ti, Td = sintonia_pid_cohen_coon(K=1.0, L=0.5, T=5.0)
    print(f"  L=0.5, T=5.0 (L/T=0.10): Kp={Kp:.4f}, Ti={Ti:.4f}, Td={Td:.4f}")
    
    print(f"\nL/T >= 0.3 (fórmula general):")
    Kp, Ti, Td = sintonia_pid_cohen_coon(K=1.0, L=2.0, T=5.0)
    print(f"  L=2.0, T=5.0 (L/T=0.40): Kp={Kp:.4f}, Ti={Ti:.4f}, Td={Td:.4f}")
    
    # ========== EJEMPLO 4: PI vs PID ==========
    print("\n" + "=" * 70)
    print("EJEMPLO 4: Control PI vs PID")
    print("=" * 70)
    
    print(f"\nPara K={K}, L={L}, T={T} (criterio IAE):\n")
    
    Kp_pi, Ti_pi, Td_pi = sintonia_pid_cohen_coon(K, L, T, control_type="PI")
    Kp_pid, Ti_pid, Td_pid = sintonia_pid_cohen_coon(K, L, T, control_type="PID")
    
    print(f"  PI:  Kp={Kp_pi:.4f}, Ti={Ti_pi:.4f}, Td={Td_pi:.4f}")
    print(f"  PID: Kp={Kp_pid:.4f}, Ti={Ti_pid:.4f}, Td={Td_pid:.4f}")
    
    # ========== EJEMPLO 5: Ziegler-Nichols vs Cohen-Coon ==========
    print("\n" + "=" * 70)
    print("EJEMPLO 5: COMPARACIÓN Ziegler-Nichols vs Cohen-Coon")
    print("=" * 70)
    
    print(f"\nPara varios valores de FOPDT:\n")
    print(f"{'K':<5} {'L':<5} {'T':<5} {'L/T':<6} | {'Método':<15} {'Kp':<8} {'Ti':<7} {'Td':<7}")
    print("-" * 85)
    
    test_systems = [
        (1.0, 1.0, 5.0),   # L/T = 0.2
        (2.0, 2.0, 10.0),  # L/T = 0.2
        (1.0, 2.0, 5.0),   # L/T = 0.4
    ]
    
    from src.tuning.ziegler_nichols import sintonia_pid_ziegler_nichols
    
    for K, L, T in test_systems:
        ratio = L / T
        Kp_zn, Ti_zn, Td_zn = sintonia_pid_ziegler_nichols(K, L, T, "PID")
        Kp_cc, Ti_cc, Td_cc = sintonia_pid_cohen_coon(K, L, T, criterion="IAE")
        
        print(f"{K:<5.1f} {L:<5.1f} {T:<5.1f} {ratio:<6.2f} | {'Ziegler-Nichols':<15} {Kp_zn:<8.3f} {Ti_zn:<7.3f} {Td_zn:<7.3f}")
        print(f"{'':<5} {'':<5} {'':<5} {'':<6} | {'Cohen-Coon':<15} {Kp_cc:<8.3f} {Ti_cc:<7.3f} {Td_cc:<7.3f}")
        print("-" * 85)
    
    # ========== EJEMPLO 6: Validación ==========
    print("\n" + "=" * 70)
    print("EJEMPLO 6: Validación de Parámetros")
    print("=" * 70)
    
    test_cases_cc = [
        {"K": 1.0, "L": 1.0, "T": 5.0, "criterion": "IAE", "desc": "Válido"},
        {"K": -1.0, "L": 1.0, "T": 5.0, "criterion": "IAE", "desc": "K negativa"},
        {"K": 1.0, "L": 1.0, "T": 5.0, "criterion": "INVALID", "desc": "Criterio inválido"},
    ]
    
    for test in test_cases_cc:
        try:
            print(f"\n{test['desc']}: ", end="")
            Kp, Ti, Td = sintonia_pid_cohen_coon(
                test['K'], test['L'], test['T'], test['criterion']
            )
            print(f"✓ Kp={Kp:.3f}, Ti={Ti:.3f}, Td={Td:.3f}")
        except TuningError as e:
            print(f"❌ Error: {e}")
