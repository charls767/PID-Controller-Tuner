"""
Módulo de Simulación en Lazo Abierto (Open Loop)

Simula la respuesta de un sistema sin controlador ante entrada escalón.
"""

from typing import Tuple, Optional
import numpy as np
import control as ct
from src.core.transfer_function import is_stable, InvalidTransferFunctionError


class SimulationError(Exception):
    """Se levanta cuando hay error en la simulación."""
    pass


def simulate_step_response(tf: ct.TransferFunction,
                          t_final: Optional[float] = None,
                          num_points: int = 1000,
                          input_magnitude: float = 1.0) -> Tuple[np.ndarray, np.ndarray]:
    """
    Simula la respuesta al escalón de un sistema sin control (lazo abierto).
    
    Resuelve numéricamente la ecuación diferencial que describe el sistema
    usando el método de integración de python-control.
    
    La entrada es un escalón unitario de magnitud `input_magnitude`.
    
    Parameters:
        tf (ct.TransferFunction):
            Función de transferencia del sistema G(s)
        
        t_final (float, optional):
            Tiempo final de simulación en segundos.
            Si es None, se estima automáticamente basado en los polos.
            Default: None (automático)
        
        num_points (int):
            Número de puntos a simular (determina resolución).
            Default: 1000 puntos
        
        input_magnitude (float):
            Magnitud del escalón de entrada.
            Default: 1.0 (escalón unitario)
    
    Returns:
        Tuple[np.ndarray, np.ndarray]:
            - time (np.ndarray): Vector de tiempo [segundos]. Forma (n_points,)
            - output (np.ndarray): Salida del sistema y(t). Forma (n_points,)
    
    Raises:
        SimulationError:
            - Si el sistema es inestable
            - Si la simulación falla por razones numéricas
            - Si los parámetros son inválidos
        InvalidTransferFunctionError:
            - Si la función de transferencia es inválida
    
    Notes:
        - Para sistemas estables, autom detiene la simulación cuando
          se alcanza el 99% del valor final (ahorr cálculos innecesarios)
        - Para sistemas marginalmente estables (ej: integradores),
          simula hasta t_final completo
    
    Examples:
        >>> import control as ct
        >>> from src.core.transfer_function import create_transfer_function
        >>> 
        >>> # System: G(s) = 1/(s+1)
        >>> tf = create_transfer_function([1], [1, 1])
        >>> time, output = simulate_step_response(tf, t_final=10.0)
        >>> 
        >>> # Output shape
        >>> print(f"Tiempo: forma {time.shape}, rango [{time[0]:.2f}, {time[-1]:.2f}]")
        Tiempo: forma (1000,), rango [0.00, 10.00]
        
        >>> # Valor final (aprox al valor estacionario)
        >>> print(f"Salida inicial: {output[0]:.4f}")
        >>> print(f"Salida final: {output[-1]:.4f}")
        Salida inicial: 0.0000
        Salida final: 1.0000
        
        >>> # With custom input magnitude
        >>> time, output = simulate_step_response(tf, t_final=5.0, input_magnitude=2.0)
        >>> print(f"Salida final (entrada=2): {output[-1]:.4f}")
        Salida final (entrada=2): 2.0000
    """
    
    # Validar función de transferencia
    if tf is None:
        raise SimulationError("Función de transferencia no puede ser None")
    
    # Validar que sea estable
    if not is_stable(tf):
        raise SimulationError(
            "No se puede simular un sistema inestable. "
            "Todos los polos deben tener parte real negativa."
        )
    
    # Validar parámetros
    if num_points < 10:
        raise SimulationError("num_points debe ser >= 10")
    
    if input_magnitude <= 0:
        raise SimulationError("input_magnitude debe ser positivo")
    
    # Estimar tiempo final si no se proporciona
    if t_final is None:
        t_final = _estimate_settling_time(tf)
    elif t_final <= 0:
        raise SimulationError("t_final debe ser positivo")
    
    # Crear vector de tiempo
    time = np.linspace(0, t_final, num_points)
    
    try:
        # Usar python-control para calcular respuesta al escalón
        # step_info retorna (t, y)
        t_response, y_response = ct.step_response(tf, T=time)
        
        # Escalar por magnitud de entrada
        y_response = y_response * input_magnitude
        
    except Exception as e:
        raise SimulationError(
            f"Error durante la simulación de respuesta al escalón: {str(e)}"
        )
    
    return t_response, y_response


def _estimate_settling_time(tf: ct.TransferFunction, 
                            tolerance: float = 0.05,
                            max_time: float = 1000.0) -> float:
    """
    Estima el tiempo de establecimiento basado en los polos del sistema.
    
    Usa la regla: ts_approx = -5 / Re(polo más lento)
    donde el polo más lento es el que tiene la menor magnitud de parte real.
    
    Parameters:
        tf (ct.TransferFunction): Función de transferencia
        tolerance (float): Tolerancia (5% por defecto)
        max_time (float): Límite superior del tiempo estimado
    
    Returns:
        float: Tiempo estimado en segundos
    """
    poles = np.asarray(tf.pole())
    
    if len(poles) == 0:
        return 10.0  # Valor por defecto
    
    # Obtener polo con parte real más pequeña en magnitud (más lento)
    real_parts = np.real(poles)
    slowest_pole = np.max(real_parts)  # Menos negativo = más lento
    
    if slowest_pole >= 0:
        # Sistema marginal o inestable (ya validado antes)
        return max_time
    
    # Regla de oro: ts ~ -5 / Re(polo)
    # Para 5% de tolerancia
    ts_estimate = -5.0 / slowest_pole
    
    # Limitar a un máximo razonable
    return min(ts_estimate, max_time)


def simulate_multiple_scenarios(tf_list: list,
                               labels: list,
                               t_final: Optional[float] = None,
                               num_points: int = 1000) -> list:
    """
    Simula la respuesta al escalón para múltiples sistemas.
    
    Útil para comparar comportamientos de diferentes funciones de transferencia.
    
    Parameters:
        tf_list (list): Lista de funciones de transferencia (ct.TransferFunction)
        labels (list): Etiquetas descriptivas para cada sistema
        t_final (float, optional): Tiempo final de simulación
        num_points (int): Número de puntos de simulación
    
    Returns:
        list: Lista de tuplas (time, output, label) para cada sistema
    
    Examples:
        >>> tf1 = create_transfer_function([1], [1, 1])
        >>> tf2 = create_transfer_function([1], [2, 1])
        >>> results = simulate_multiple_scenarios([tf1, tf2], ["Sistema 1", "Sistema 2"])
        >>> for time, output, label in results:
        ...     print(f"{label}: y_final = {output[-1]:.4f}")
        Sistema 1: y_final = 1.0000
        Sistema 2: y_final = 1.0000
    """
    if len(tf_list) != len(labels):
        raise SimulationError("tf_list y labels deben tener la misma longitud")
    
    results = []
    for tf, label in zip(tf_list, labels):
        time, output = simulate_step_response(tf, t_final=t_final, num_points=num_points)
        results.append((time, output, label))
    
    return results


if __name__ == "__main__":
    from src.core.transfer_function import create_transfer_function
    
    print("=" * 60)
    print("MÓDULO: Simulación Open Loop")
    print("=" * 60)
    
    # Crear sistema de prueba
    print("\nSistema: G(s) = 1/(s+1)")
    tf = create_transfer_function([1], [1, 1])
    
    # Simular respuesta
    print("Simulando respuesta al escalón...")
    time, output = simulate_step_response(tf, t_final=5.0, num_points=500)
    
    print(f"Tiempo: {len(time)} puntos, rango [{time[0]:.2f}, {time[-1]:.2f}] seg")
    print(f"Salida: y[0] = {output[0]:.6f}, y[-1] = {output[-1]:.6f}")
    
    # Análisis rápido
    steady_state = output[-1]
    rise_idx = np.argmin(np.abs(output - 0.9 * steady_state))
    rise_time = time[rise_idx]
    print(f"Tiempo de levantamiento (10%-90%): ~{rise_time:.3f} seg")
    
    # Simular proceso FOPDT
    print("\n" + "-" * 60)
    print("Sistema FOPDT: G(s) = 2/(10s+1)")
    tf_fopdt = create_transfer_function([2], [10, 1])
    
    time_fopdt, output_fopdt = simulate_step_response(tf_fopdt, t_final=50.0)
    print(f"Valor estacionario: {output_fopdt[-1]:.4f} (esperado: 2.0)")
    
    # Comparar múltiples sistemas
    print("\n" + "-" * 60)
    print("Comparando 3 sistemas con diferentes velocidades...")
    tf1 = create_transfer_function([1], [1, 1])       # Tiempo 1s
    tf2 = create_transfer_function([1], [5, 1])       # Tiempo 5s
    tf3 = create_transfer_function([1], [0.1, 1])     # Tiempo 0.1s
    
    results = simulate_multiple_scenarios(
        [tf1, tf2, tf3],
        ["T=1s", "T=5s", "T=0.1s"],
        t_final=15.0
    )
    
    for time, output, label in results:
        steady_state = output[-1]
        idx_63 = np.argmin(np.abs(output - 0.632 * steady_state))
        time_63 = time[idx_63]
        print(f"  {label}: Tiempo al 63.2% = {time_63:.3f} seg, y_final = {steady_state:.4f}")
