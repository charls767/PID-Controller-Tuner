"""
Módulo de Sintonización Ziegler-Nichols (ZN)

Implementa el método clásico de Ziegler-Nichols para sintonización de PID.
"""

from typing import Tuple, Literal
import numpy as np


class TuningError(Exception):
    """Se levanta cuando hay error en el cálculo de sintonización."""
    pass


def sintonia_pid_ziegler_nichols(K: float,
                                L: float,
                                T: float,
                                control_type: Literal["P", "PI", "PID"] = "PID") -> Tuple[float, float, float]:
    """
    Calcula parámetros PID usando el método de Ziegler-Nichols.
    
    ============================================================================
    TEORÍA
    ============================================================================
    
    Ziegler-Nichols es el método más clásico para sintonización de controladores
    PID. Usa los parámetros de un modelo FOPDT (Primer Orden + Retardo):
    
        G(s) = K / (T*s + 1) * e^(-L*s)
    
    Donde:
        K = Ganancia DC del proceso
        L = Retardo de transporte (tiempo muerto)
        T = Constante de tiempo
    
    ============================================================================
    FÓRMULAS ZIEGLER-NICHOLS (Método de la Curva de Reacción)
    ============================================================================
    
    Para control PID:
        Kp = 1.2 * T / (L * K)
        Ti = 2 * L                   [segundos]
        Td = 0.5 * L                 [segundos]
    
    Para control PI (sin derivada):
        Kp = 0.9 * T / (L * K)
        Ti = 3.33 * L
        Td = 0                       [sin componente derivativa]
    
    Para control P (solo proporcional):
        Kp = T / (L * K)
        Ti = ∞
        Td = 0
    
    ============================================================================
    CARACTERÍSTICAS
    ============================================================================
    
    - Simple y rápido de aplicar
    - Funciona bien en la mayoría de procesos industriales
    - Produce overshoot de 20-25% (aceptable en muchas aplicaciones)
    - No requiere identificación completa del sistema
    
    ============================================================================
    
    Parameters:
        K (float):
            Ganancia DC del proceso (adimensional o unidades de control).
            - Típico: 0.5 a 5
            - Debe ser positivo: K > 0
            - Ejemplo: 2.0 para un calentador (2°C por % de potencia)
        
        L (float):
            Retardo de transporte en segundos (tiempo muerto).
            - Típico: 0.1 a 10 seg
            - Debe ser no-negativo: L >= 0
            - Ejemplo: 2.0 para un sensor remoto
        
        T (float):
            Constante de tiempo del proceso en segundos.
            - Típico: 1 a 100 seg
            - Debe ser positivo: T > 0
            - Ejemplo: 10.0 para una constante térmica
        
        control_type (str):
            Tipo de controlador a sintonizar:
            - "P":   Solo proporcional
            - "PI":  Proporcional + Integral
            - "PID": Proporcional + Integral + Derivativo (default)
    
    Returns:
        Tuple[float, float, float]:
            (Kp, Ti, Td) parámetros sintonizados del PID
            - Kp (float): Ganancia proporcional
            - Ti (float): Tiempo integral en segundos
            - Td (float): Tiempo derivativo en segundos (0 si no se usa)
    
    Raises:
        TuningError:
            - Si K <= 0 (ganancia debe ser positiva)
            - Si L < 0 (retardo no puede ser negativo)
            - Si T <= 0 (constante de tiempo debe ser positiva)
            - Si L/T > 0.5 (relación muy alta, método menos preciso)
            - Si control_type no es válido
    
    Examples:
        ===== Ejemplo 1: Proceso FOPDT de Calentamiento =====
        
        Parámetros del proceso:
            K = 2.0      [°C por % de potencia]
            L = 2.0 seg  [tiempo del sensor]
            T = 10.0 seg [constante térmica]
        
        >>> Kp, Ti, Td = sintonia_pid_ziegler_nichols(K=2.0, L=2.0, T=10.0)
        >>> print(f"Kp = {Kp:.3f}")
        >>> print(f"Ti = {Ti:.3f} seg")
        >>> print(f"Td = {Td:.3f} seg")
        Kp = 3.000
        Ti = 4.000 seg
        Td = 1.000 seg
        
        ===== Ejemplo 2: Comparar tipos de control =====
        
        >>> K, L, T = 1.0, 1.0, 5.0
        >>> 
        >>> # Solo proporcional
        >>> Kp_p, Ti_p, Td_p = sintonia_pid_ziegler_nichols(K, L, T, "P")
        >>> print(f"P:   Kp={Kp_p:.2f}")
        P:   Kp=5.00
        >>> 
        >>> # Proporcional + Integral
        >>> Kp_pi, Ti_pi, Td_pi = sintonia_pid_ziegler_nichols(K, L, T, "PI")
        >>> print(f"PI:  Kp={Kp_pi:.2f}, Ti={Ti_pi:.2f}")
        PI:  Kp=4.50, Ti=3.33
        >>> 
        >>> # Proporcional + Integral + Derivativo
        >>> Kp_pid, Ti_pid, Td_pid = sintonia_pid_ziegler_nichols(K, L, T, "PID")
        >>> print(f"PID: Kp={Kp_pid:.2f}, Ti={Ti_pid:.2f}, Td={Td_pid:.2f}")
        PID: Kp=6.00, Ti=2.00, Td=0.50
        
        ===== Ejemplo 3: Validación de parámetros =====
        
        >>> # Esto lanzará TuningError
        >>> try:
        ...     Kp, Ti, Td = sintonia_pid_ziegler_nichols(K=-1.0, L=1.0, T=5.0)
        ... except TuningError as e:
        ...     print(f"Error: {e}")
        Error: K debe ser positivo (K > 0), recibido: -1.0
    
    Notes:
        - Si L = 0 (sin retardo), usar método alternativo (recomendado Cohen-Coon)
        - Si L/T > 0.5, mostrar advertencia (método pierde precisión)
        - Ti siempre es = 2*L (relación fija en ZN)
        - Td siempre es = 0.5*L (relación fija en ZN)
    """
    
    # ====================================================================
    # VALIDACIÓN DE PARÁMETROS
    # ====================================================================
    
    # Validar K
    if K <= 0:
        raise TuningError(
            f"K debe ser positivo (K > 0), recibido: {K}"
        )
    
    # Validar L
    if L < 0:
        raise TuningError(
            f"L debe ser no-negativo (L >= 0), recibido: {L}"
        )
    
    # Validar T
    if T <= 0:
        raise TuningError(
            f"T debe ser positivo (T > 0), recibido: {T}"
        )
    
    # Validar control_type
    if control_type not in ["P", "PI", "PID"]:
        raise TuningError(
            f"control_type debe ser 'P', 'PI' o 'PID', recibido: {control_type}"
        )
    
    # Advertencia si L/T es muy grande
    if L / T > 0.5:
        print(f"⚠️  Advertencia: Relación L/T = {L/T:.2f} es muy alta (> 0.5)")
        print("   El método ZN es menos preciso en estos casos.")
        print("   Considera usar Cohen-Coon o aumentar T.")
    
    # ====================================================================
    # CÁLCULO DE PARÁMETROS
    # ====================================================================
    
    if control_type == "P":
        # Solo proporcional
        Kp = T / (L * K)
        Ti = float('inf')  # Sin integral
        Td = 0.0           # Sin derivada
    
    elif control_type == "PI":
        # Proporcional + Integral
        Kp = 0.9 * T / (L * K)
        Ti = 3.33 * L
        Td = 0.0  # Sin derivada
    
    else:  # control_type == "PID"
        # Proporcional + Integral + Derivativo (fórmulas clásicas ZN)
        Kp = 1.2 * T / (L * K)
        Ti = 2.0 * L
        Td = 0.5 * L
    
    return float(Kp), float(Ti), float(Td)


# ============================================================================
# FUNCIÓN ALTERNATIVA: Desde un modelo FOPDT (compatibilidad con API)
# ============================================================================

def tune_ziegler_nichols_from_fopdt(fopdt_dict, control_type: str = "PID"):
    """
    Wrapper para sintonia_pid_ziegler_nichols que acepta un diccionario FOPDT.
    
    Parameters:
        fopdt_dict (dict): Diccionario con claves "K", "L", "T"
        control_type (str): "P", "PI" o "PID"
    
    Returns:
        dict: Diccionario con claves "Kp", "Ti", "Td", "method"
    
    Example:
        >>> fopdt = {"K": 2.0, "L": 2.0, "T": 10.0}
        >>> pid = tune_ziegler_nichols_from_fopdt(fopdt)
        >>> print(pid)
        {'Kp': 3.0, 'Ti': 4.0, 'Td': 1.0, 'method': 'Ziegler-Nichols'}
    """
    try:
        K = fopdt_dict["K"]
        L = fopdt_dict["L"]
        T = fopdt_dict["T"]
    except KeyError as e:
        raise TuningError(f"Diccionario FOPDT incompleto. Falta clave: {e}")
    
    Kp, Ti, Td = sintonia_pid_ziegler_nichols(K, L, T, control_type)
    
    return {
        "Kp": Kp,
        "Ti": Ti,
        "Td": Td,
        "method": "Ziegler-Nichols"
    }


if __name__ == "__main__":
    print("=" * 70)
    print("MÓDULO: Sintonización Ziegler-Nichols")
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
    print(f"  L = {L:.1f}   [seg] - retardo del sensor")
    print(f"  T = {T:.1f}   [seg] - constante térmica")
    print(f"  Relación L/T = {L/T:.2f}")
    
    print(f"\nSintonización Ziegler-Nichols:")
    Kp, Ti, Td = sintonia_pid_ziegler_nichols(K, L, T, "PID")
    print(f"  PID:")
    print(f"    Kp = {Kp:.3f}")
    print(f"    Ti = {Ti:.3f} seg")
    print(f"    Td = {Td:.3f} seg")
    
    # ========== EJEMPLO 2: Comparación de tipos de control ==========
    print("\n" + "=" * 70)
    print("EJEMPLO 2: Comparación de Tipos de Control")
    print("=" * 70)
    
    print(f"\nUsando mismos parámetros FOPDT (K={K}, L={L}, T={T}):\n")
    
    for control_type in ["P", "PI", "PID"]:
        Kp, Ti, Td = sintonia_pid_ziegler_nichols(K, L, T, control_type)
        print(f"  {control_type}:")
        print(f"    Kp = {Kp:.4f}")
        print(f"    Ti = {Ti:.4f} seg" if Ti != float('inf') else f"    Ti = ∞ (sin integral)")
        print(f"    Td = {Td:.4f} seg")
        print()
    
    # ========== EJEMPLO 3: Variando L/T ==========
    print("=" * 70)
    print("EJEMPLO 3: Efecto de La Relación L/T")
    print("=" * 70)
    
    T = 10.0
    print(f"\nConservando T = {T}, variando L:\n")
    
    for L in [1.0, 2.0, 5.0, 10.0]:
        Kp, Ti, Td = sintonia_pid_ziegler_nichols(K=1.0, L=L, T=T, control_type="PID")
        ratio = L / T
        print(f"  L = {L:>4.1f} (L/T = {ratio:.2f}): Kp = {Kp:>6.3f}, Ti = {Ti:>6.3f}, Td = {Td:>6.3f}")
    
    # ========== EJEMPLO 4: Manejo de errores ==========
    print("\n" + "=" * 70)
    print("EJEMPLO 4: Validación y Manejo de Errores")
    print("=" * 70)
    
    test_cases = [
        {"K": -1.0, "L": 1.0, "T": 5.0, "desc": "K negativa"},
        {"K": 1.0, "L": -1.0, "T": 5.0, "desc": "L negativa"},
        {"K": 1.0, "L": 1.0, "T": 0.0, "desc": "T cero"},
    ]
    
    for test in test_cases:
        try:
            print(f"\nIntentando: {test['desc']}")
            print(f"  Parámetros: K={test['K']}, L={test['L']}, T={test['T']}")
            Kp, Ti, Td = sintonia_pid_ziegler_nichols(test['K'], test['L'], test['T'])
        except TuningError as e:
            print(f"  ❌ Error capturado: {e}")
    
    # ========== EJEMPLO 5: Usando función wrapper ==========
    print("\n" + "=" * 70)
    print("EJEMPLO 5: Usando Función Wrapper con Diccionario FOPDT")
    print("=" * 70)
    
    fopdt = {"K": 2.0, "L": 2.0, "T": 10.0}
    result = tune_ziegler_nichols_from_fopdt(fopdt, control_type="PID")
    print(f"\nEntrada: {fopdt}")
    print(f"Resultado: {result}")
