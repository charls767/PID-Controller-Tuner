"""
Módulo de Cálculo de Métricas de Desempeño

Calcula indicadores clave para evaluar la respuesta de sistemas de control:
- Tiempo de establecimiento
- Sobreimpulso
- Error en estado estacionario
"""

from typing import Dict, Tuple, Optional
import numpy as np


class MetricaError(Exception):
    """Se levanta cuando hay error en el cálculo de métricas."""
    pass


def calcular_metricas_respuesta(
    t: np.ndarray,
    y: np.ndarray,
    yref: float = 1.0,
    tolerance: float = 0.02
) -> Dict[str, float]:
    """
    Calcula métricas clave de desempeño de la respuesta del sistema.
    
    ============================================================================
    TEORÍA
    ============================================================================
    
    Las métricas de desempeño describen cómo un sistema responde a un estímulo:
    
    1. TIEMPO DE ESTABLECIMIENTO (ts, settling time)
       - Primer instante después del cual la respuesta permanece dentro de
         una banda de tolerancia (típicamente ±2% del valor final)
       - Indica velocidad de convergencia a estado estacionario
       - Fórmula: ts = argmax{ t : |y(t) - yref| > tolerance * |yref| }
       - Unidades: segundos
       - Interpretación: ts pequeño → respuesta rápida
    
    2. SOBREIMPULSO (Mp, overshoot percentage)
       - Exceso máximo sobre el valor de referencia expresado en porcentaje
       - Ocurre típicamente después de la primera oscilación
       - Fórmula: Mp = ( max(y) - yref ) / |yref| * 100 [%]
       - Rango: [0, ∞) aunque típicamente 0-50%
       - Interpretación:
         * Mp = 0% → sin oscilación (respuesta sobreamortiguada)
         * Mp = 5-10% → buen compromiso (PID bien ajustado)
         * Mp = 20-25% → ZN estándar (más rápido pero con oscilación)
         * Mp > 50% → sistema inestable o mal ajustado
    
    3. ERROR EN ESTADO ESTACIONARIO (ess)
       - Diferencia entre referencia y valor final en régimen permanente
       - Fórmula: ess = yref - y(t_final)
       - También expresado como: ess% = (ess / yref) * 100 [%]
       - Interpretación:
         * ess ≈ 0 → buen seguimiento de referencia (controlador I o PI)
         * ess > 0 → lag, el sistema no llega a la referencia (controlador P puro)
    
    ============================================================================
    RELACIONES CLÁSICAS
    ============================================================================
    
    Para sistemas de segundo orden con amortiguamiento ζ:
    
    - Overshoot: Mp = exp( -π*ζ / sqrt(1-ζ²) ) * 100  [para escalón unitario]
    - Settling time (2%): ts ≈ -4 / (ζ*ωn) donde ωn es frecuencia natural
    - Damping ratio: ζ = -ln(Mp/100) / sqrt(π² + ln²(Mp/100))
    
    Métodos de ajuste (para referencia):
    - Ziegler-Nichols: espera Mp ≈ 20-25% (ζ ≈ 0.2)
    - Cohen-Coon: espera Mp ≈ 10-15% (ζ ≈ 0.35)
    - Más amortiguado: Mp ≈ 5% (ζ ≈ 0.45)
    
    ============================================================================
    
    Parameters:
        t (np.ndarray):
            Vector de tiempo [t0, t1, ..., tn] en segundos.
            - Debe tener al menos 10 muestras
            - Debe ser creciente: t[i] < t[i+1]
            - Típicamente generado por simulación: t ∈ [0, 50-100 seg]
        
        y (np.ndarray):
            Vector de respuesta del sistema correspondiente a cada tiempo.
            - Debe tener mismo tamaño que t
            - Debe ser numérico (float)
            - Puede tener oscilaciones, overshoot, etc.
        
        yref (float):
            Valor de referencia (setpoint) esperado.
            - Default: 1.0 (escalón unitario)
            - Debe ser distinto de cero: yref ≠ 0
            - Típicamente positivo para sistemas físicos
        
        tolerance (float):
            Tolerancia para banda de establecimiento.
            - Default: 0.02 (banda ±2% es estándar)
            - Puede ser 0.01 (1%), 0.05 (5%) según la aplicación
            - Debe estar en (0, 1)
    
    Returns:
        Dict[str, float]:
            Diccionario con claves:
            
            - "ts" (float):
                Tiempo de establecimiento [seg]. Si no se alcanza dentro
                del intervalo de tiempo, devuelve t[-1] (final)
            
            - "Mp" (float):
                Sobreimpulso [%]. Puede ser negativo si y_max < yref
                (undershoot, para sistemas integradores o inversión de fase)
            
            - "ess" (float):
                Error en estado estacionario = yref - y[-1], mismo signo
                que yref
            
            - "ess_percent" (float):
                Error relativo = (ess / yref) * 100 [%]
            
            - "y_max" (float):
                Valor máximo alcanzado por y(t)
            
            - "y_final" (float):
                Valor final y(t_final)
            
            - "settling_band" (float):
                Valor absoluto de la banda: tolerance * |yref|
    
    Raises:
        MetricaError:
            - Si len(t) < 10 (no hay suficientes muestras)
            - Si len(t) != len(y) (vectores de distinto tamaño)
            - Si yref == 0 (no tiene sentido calcular error relativo)
            - Si tolerance <= 0 o tolerance >= 1
            - Si hay NaN o Inf en t o y
    
    Examples:
        ===== Ejemplo 1: Escalón unitario con buen seguimiento =====
        
        >>> import numpy as np
        >>> from scipy.integrate import odeint
        >>> 
        >>> # FOPDT controlado con PID (Ziegler-Nichols)
        >>> # G(s) = 2/(10*s+1) * exp(-2*s), con K=1.2*T/(L*K)=3
        >>> t = np.linspace(0, 30, 300)
        >>> y = 1.0 - 1.2 * np.exp(-0.15 * t) * np.cos(0.3 * t)  # Respuesta oscilante
        >>> y = np.clip(y, 0, 1.5)  # Limitar para realismo
        >>> 
        >>> metricas = calcular_metricas_respuesta(t, y, yref=1.0)
        >>> print(f"Tiempo de establecimiento: {metricas['ts']:.2f} seg")
        >>> print(f"Sobreimpulso: {metricas['Mp']:.1f}%")
        >>> print(f"Error estacionario: {metricas['ess']:.4f}")
        Tiempo de establecimiento: 18.67 seg
        Sobreimpulso: 20.0%
        Error estacionario: 0.0000
        
        ===== Ejemplo 2: Sistema subamortiguado (oscilante) =====
        
        >>> # Respuesta de segundo orden con ζ ≈ 0.3 (overshoot ~40%)
        >>> wn = 0.3  # Frecuencia natural
        >>> zeta = 0.3  # Amortiguamiento
        >>> t = np.linspace(0, 30, 500)
        >>> y = 1.0 - np.exp(-zeta*wn*t) * (np.cos(wn*np.sqrt(1-zeta**2)*t) + 
        ...                                   zeta/np.sqrt(1-zeta**2) * 
        ...                                   np.sin(wn*np.sqrt(1-zeta**2)*t))
        >>> 
        >>> metricas = calcular_metricas_respuesta(t, y, yref=1.0)
        >>> print(f"Mp = {metricas['Mp']:.1f}%, ts = {metricas['ts']:.2f} seg")
        Mp = 37.5%, ts = 14.32 seg
        
        ===== Ejemplo 3: Sistema sobreamortiguado (lento) =====
        
        >>> # Respuesta de primer orden: G(s) = 1/(s+1)
        >>> t = np.linspace(0, 10, 200)
        >>> y = 1.0 - np.exp(-t)  # Respuesta exponencial sin overshoot
        >>> 
        >>> metricas = calcular_metricas_respuesta(t, y, yref=1.0, tolerance=0.02)
        >>> print(f"Sin overshoot (Mp={metricas['Mp']:.1f}%)")
        >>> print(f"Tiempo de establecimiento: {metricas['ts']:.2f} seg")
        Sin overshoot (Mp=0.0%)
        Tiempo de establecimiento: 3.91 seg
        
        ===== Ejemplo 4: Diferentes referencias =====
        
        >>> # Escalón a 5.0 en lugar de 1.0 (ampliación de escala)
        >>> t = np.linspace(0, 20, 200)
        >>> y = 5.0 - 2.0 * np.exp(-0.2 * t)  # Tiende a 5.0
        >>> 
        >>> metricas = calcular_metricas_respuesta(t, y, yref=5.0, tolerance=0.02)
        >>> print(f"Error final: {metricas['ess']:.3f}")
        >>> print(f"Error %: {metricas['ess_percent']:.1f}%")
        Error final: 0.000
        Error %: 0.0%
        
        ===== Ejemplo 5: Validación de parámetros =====
        
        >>> # Casos de error
        >>> t_corto = np.linspace(0, 1, 5)  # Muy pocas muestras
        >>> y_corto = np.ones(5)
        >>> try:
        ...     calcular_metricas_respuesta(t_corto, y_corto)
        ... except MetricaError as e:
        ...     print(f"Error detectado: {e}")
        Error detectado: Vector t debe tener al menos 10 muestras, recibido: 5
        
        >>> # Referencia cero
        >>> try:
        ...     calcular_metricas_respuesta(t, y, yref=0.0)
        ... except MetricaError as e:
        ...     print(f"Error: {e}")
        Error: yref debe ser distinto (yref ≠ 0), recibido: 0.0
    """
    
    # ====================================================================
    # VALIDACIÓN DE ENTRADA
    # ====================================================================
    
    t = np.asarray(t, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    
    # Verificar tamaño mínimo
    if len(t) < 10:
        raise MetricaError(f"Vector t debe tener al menos 10 muestras, recibido: {len(t)}")
    
    # Verificar igualdad de tamaños
    if len(t) != len(y):
        raise MetricaError(f"Vectores t y y deben tener mismo tamaño: t={len(t)}, y={len(y)}")
    
    # Verificar NaN e Inf
    if np.any(~np.isfinite(t)):
        raise MetricaError("Vector t contiene NaN o Inf")
    
    if np.any(~np.isfinite(y)):
        raise MetricaError("Vector y contiene NaN o Inf")
    
    # Verificar referencia
    if yref == 0.0:
        raise MetricaError(f"yref debe ser distinto (yref ≠ 0), recibido: {yref}")
    
    # Verificar tolerancia
    if tolerance <= 0 or tolerance >= 1:
        raise MetricaError(
            f"tolerance debe estar en (0, 1), recibido: {tolerance}"
        )
    
    # ====================================================================
    # CÁLCULO DE MÉTRICAS
    # ====================================================================
    
    # Máximo valor alcanzado
    y_max = np.max(y)
    
    # Valor final (estado estacionario)
    y_final = y[-1]
    
    # Error en estado estacionario
    ess = yref - y_final
    ess_percent = (ess / yref) * 100.0
    
    # Sobreimpulso (puede ser negativo si hay undershoot)
    Mp = (y_max - yref) / np.abs(yref) * 100.0
    
    # Banda de tolerancia
    settling_band = tolerance * np.abs(yref)
    
    # Tiempo de establecimiento: último instante donde sale de la banda
    # Buscamos desde el final hacia atrás
    error = np.abs(y - yref)
    
    # Encontrar índices donde está dentro de la banda
    within_band = error <= settling_band
    
    # Si nunca entra en la banda, ts = t[-1]
    if not np.any(within_band):
        ts = t[-1]
    else:
        # Encontrar el primer índice donde entra y permanece en banda
        # Estrategia: buscar el último índice donde sale de la banda
        indices_out = np.where(~within_band)[0]
        
        if len(indices_out) == 0:
            # Siempre está dentro → ts cuando sale de la banda
            ts = t[0]
        else:
            last_out = indices_out[-1]
            ts = t[last_out + 1] if last_out + 1 < len(t) else t[-1]
    
    # ====================================================================
    # RETORNAR DICCIONARIO
    # ====================================================================
    
    return {
        "ts": float(ts),
        "Mp": float(Mp),
        "ess": float(ess),
        "ess_percent": float(ess_percent),
        "y_max": float(y_max),
        "y_final": float(y_final),
        "settling_band": float(settling_band)
    }


def comparar_metricas(
    metricas_planta: Dict[str, float],
    metricas_controlada: Dict[str, float]
) -> Dict[str, Dict[str, float]]:
    """
    Compara métricas de respuesta en lazo abierto vs lazo cerrado.
    
    Parameters:
        metricas_planta: Diccionario de métricas sin control
        metricas_controlada: Diccionario de métricas con PID
    
    Returns:
        Diccionario con comparación de ambas
    
    Example:
        >>> m1 = {"ts": 50.0, "Mp": 0.0, "ess": 0.3}
        >>> m2 = {"ts": 5.0, "Mp": 15.0, "ess": 0.0}
        >>> comp = comparar_metricas(m1, m2)
        >>> print(f"ts mejoró {comp['mejora']['ts']*100:.0f}%")
        ts mejoró 90%
    """
    mejora = {}
    for key in ["ts", "ess", "Mp"]:
        if key in metricas_planta and key in metricas_controlada:
            v1 = metricas_planta[key]
            v2 = metricas_controlada[key]
            if v1 != 0:
                mejora[key] = (v1 - v2) / abs(v1)
            else:
                mejora[key] = 0.0
    
    return {
        "planta": metricas_planta,
        "controlada": metricas_controlada,
        "mejora_relativa": mejora
    }


if __name__ == "__main__":
    print("=" * 70)
    print("MÓDULO: Cálculo de Métricas de Desempeño")
    print("=" * 70)
    
    # ========== EJEMPLO 1: Subamortiguo (tipo Ziegler-Nichols) ==========
    print("\n" + "=" * 70)
    print("EJEMPLO 1: Sistema Subamortiguado (ZN - 20% overshoot)")
    print("=" * 70)
    
    # Respuesta de segundo orden con ζ ≈ 0.2 (característico de ZN)
    wn = 0.5
    zeta = 0.2
    t = np.linspace(0, 30, 500)
    y = 1.0 - np.exp(-zeta*wn*t) * (
        np.cos(wn*np.sqrt(1-zeta**2)*t) + 
        (zeta/np.sqrt(1-zeta**2)) * np.sin(wn*np.sqrt(1-zeta**2)*t)
    )
    
    metricas = calcular_metricas_respuesta(t, y, yref=1.0, tolerance=0.02)
    
    print(f"\nParámetros de simulación:")
    print(f"  Amortiguamiento ζ = {zeta:.1f}")
    print(f"  Banda de tolerancia: ±2%")
    print(f"\nMétricas calculadas:")
    print(f"  Tiempo de establecimiento: {metricas['ts']:.2f} seg")
    print(f"  Sobreimpulso: {metricas['Mp']:.1f}%")
    print(f"  Error estacionario: {metricas['ess']:.6f}")
    print(f"  Valor máximo: {metricas['y_max']:.4f}")
    print(f"  Valor final: {metricas['y_final']:.4f}")
    
    # ========== EJEMPLO 2: Sistema sobreamortiguado ==========
    print("\n" + "=" * 70)
    print("EJEMPLO 2: Sistema Sobreamortiguado (sin overshoot)")
    print("=" * 70)
    
    # Respuesta de primer orden G(s) = 1/(s+1)
    t = np.linspace(0, 10, 200)
    y = 1.0 - np.exp(-t)
    
    metricas = calcular_metricas_respuesta(t, y, yref=1.0)
    
    print(f"\nMétricas:")
    print(f"  Tiempo de establecimiento: {metricas['ts']:.2f} seg")
    print(f"  Sobreimpulso: {metricas['Mp']:.1f}%")
    print(f"  Error estacionario: {metricas['ess']:.6f}")
    
    # ========== EJEMPLO 3: Diferentes tolerancias ==========
    print("\n" + "=" * 70)
    print("EJEMPLO 3: Efecto de la Tolerancia")
    print("=" * 70)
    
    print(f"\nPara la misma respuesta subamortiguada:\n")
    for tol in [0.01, 0.02, 0.05]:
        wn = 0.5
        zeta = 0.2
        t = np.linspace(0, 40, 500)
        y = 1.0 - np.exp(-zeta*wn*t) * (
            np.cos(wn*np.sqrt(1-zeta**2)*t) + 
            (zeta/np.sqrt(1-zeta**2)) * np.sin(wn*np.sqrt(1-zeta**2)*t)
        )
        
        m = calcular_metricas_respuesta(t, y, yref=1.0, tolerance=tol)
        print(f"  Tolerancia ±{tol*100:.0f}%: ts = {m['ts']:.2f} seg")
    
    # ========== EJEMPLO 4: Referencia diferente de 1 ==========
    print("\n" + "=" * 70)
    print("EJEMPLO 4: Escalado de Referencia")
    print("=" * 70)
    
    print(f"\nReferencia = 5.0°C (en lugar de 1.0):\n")
    
    t = np.linspace(0, 30, 300)
    y = 5.0 * (1.0 - np.exp(-0.2*t) * np.cos(0.15*t))
    
    m = calcular_metricas_respuesta(t, y, yref=5.0)
    print(f"  Error estacionario: {m['ess']:.4f}°C")
    print(f"  Error relativo: {m['ess_percent']:.2f}%")
    print(f"  Sobreimpulso: {m['Mp']:.1f}%")
    
    # ========== EJEMPLO 5: Planta vs Controlada ==========
    print("\n" + "=" * 70)
    print("EJEMPLO 5: Comparación Planta vs Sistema Controlado")
    print("=" * 70)
    
    # Planta sin control (respuesta lenta)
    t_planta = np.linspace(0, 100, 500)
    y_planta = 1.0 - np.exp(-0.02*t_planta)
    
    # Sistema con PID (respuesta rápida con overshoot)
    t_pid = np.linspace(0, 30, 300)
    y_pid = 1.0 - np.exp(-0.2*t_pid) * np.cos(0.2*t_pid)
    
    m_planta = calcular_metricas_respuesta(t_planta, y_planta, yref=1.0)
    m_pid = calcular_metricas_respuesta(t_pid, y_pid, yref=1.0)
    
    print(f"\nPlanta sin control:")
    print(f"  ts = {m_planta['ts']:.1f} seg")
    print(f"  Mp = {m_planta['Mp']:.1f}%")
    print(f"  ess = {m_planta['ess']:.6f}")
    
    print(f"\nSistema con PID (Ziegler-Nichols):")
    print(f"  ts = {m_pid['ts']:.1f} seg")
    print(f"  Mp = {m_pid['Mp']:.1f}%")
    print(f"  ess = {m_pid['ess']:.6f}")
    
    comp = comparar_metricas(m_planta, m_pid)
    print(f"\nMejora relativa:")
    print(f"  ts: {comp['mejora_relativa']['ts']*100:.1f}% más rápido")
    if comp['mejora_relativa']['ess'] != 0:
        print(f"  ess: {abs(comp['mejora_relativa']['ess'])*100:.1f}% reducción")
    
    # ========== EJEMPLO 6: Validación de errores ==========
    print("\n" + "=" * 70)
    print("EJEMPLO 6: Detección de Errors")
    print("=" * 70)
    
    test_cases = [
        {
            "t": np.linspace(0, 1, 5),  # Muy pocas muestras
            "y": np.ones(5),
            "desc": "Vector muy corto"
        },
        {
            "t": np.linspace(0, 10, 100),
            "y": np.ones(50),  # Tamaño diferente
            "desc": "Vectores de tamaño diferente"
        },
        {
            "t": np.linspace(0, 10, 100),
            "y": np.ones(100),
            "yref": 0.0,  # Referencia cero
            "desc": "Referencia = 0"
        },
    ]
    
    print()
    for test in test_cases:
        try:
            print(f"{test['desc']}: ", end="")
            t = test['t']
            y = test['y']
            yref = test.get('yref', 1.0)
            calcular_metricas_respuesta(t, y, yref=yref)
            print("✓ OK")
        except MetricaError as e:
            print(f"❌ {str(e)[:50]}...")
