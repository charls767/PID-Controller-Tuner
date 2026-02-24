"""
Módulo de Funciones de Transferencia

Maneja la creación y manipulación de funciones de transferencia usando python-control.
"""

from typing import List, Tuple, Union
import numpy as np
import control as ct


class InvalidTransferFunctionError(Exception):
    """Se levanta cuando la función de transferencia es inválida."""
    pass


def create_transfer_function(numerator: Union[List[float], np.ndarray],
                            denominator: Union[List[float], np.ndarray]) -> ct.TransferFunction:
    """
    Crea una función de transferencia G(s) = N(s) / D(s) a partir de coeficientes.
    
    Los coeficientes se especifican en orden descendente de potencia:
    - Numerador [1, 2] representa (s + 2)
    - Denominador [1, 3, 2] representa (s² + 3s + 2)
    
    Parameters:
        numerator (List[float] or np.ndarray):
            Coeficientes del numerador en orden descendente de potencia.
            Ej: [1, 2] para (s + 2)
            
        denominator (List[float] or np.ndarray):
            Coeficientes del denominador en orden descendente de potencia.
            Ej: [1, 3, 2] para (s² + 3s + 2)
    
    Returns:
        ct.TransferFunction:
            Objeto de python-control que representa la función de transferencia.
    
    Raises:
        InvalidTransferFunctionError:
            - Si numerator o denominator están vacíos
            - Si denominador es todo ceros
            - Si los coeficientes no son numéricos
            - Si hay elementos complejos en los coeficientes
    
    Examples:
        >>> # Crear G(s) = 1 / (s + 1)
        >>> tf1 = create_transfer_function([1], [1, 1])
        >>> print(tf1)
             1
        -------
        s + 1
        
        >>> # Crear G(s) = (s + 2) / (s² + 3s + 2)
        >>> tf2 = create_transfer_function([1, 2], [1, 3, 2])
        >>> print(tf2)
          s + 2
        -----------
        s^2 + 3 s + 2
    """
    try:
        # Convertir a numpy arrays de floats
        num_array = np.asarray(numerator, dtype=float)
        den_array = np.asarray(denominator, dtype=float)
    except (TypeError, ValueError):
        raise InvalidTransferFunctionError(
            "Los coeficientes deben ser numéricos (int o float)"
        )
    
    # Validar que no estén vacíos
    if num_array.size == 0:
        raise InvalidTransferFunctionError("Numerador no puede estar vacío")
    
    if den_array.size == 0:
        raise InvalidTransferFunctionError("Denominador no puede estar vacío")
    
    # Validar que el denominador no sea todo ceros
    if np.allclose(den_array, 0):
        raise InvalidTransferFunctionError("Denominador no puede ser todo ceros")
    
    # Validar que no haya NaN o Inf
    if np.any(np.isnan(num_array)) or np.any(np.isnan(den_array)):
        raise InvalidTransferFunctionError("Los coeficientes contienen NaN")
    
    if np.any(np.isinf(num_array)) or np.any(np.isinf(den_array)):
        raise InvalidTransferFunctionError("Los coeficientes contienen Inf")
    
    # Crear la función de transferencia usando python-control
    try:
        tf = ct.TransferFunction(num_array, den_array)
    except Exception as e:
        raise InvalidTransferFunctionError(f"Error al crear TransferFunction: {str(e)}")
    
    return tf


def get_poles(tf: ct.TransferFunction) -> np.ndarray:
    """
    Calcula los polos de una función de transferencia.
    
    Los polos son las raíces del polinomio denominador.
    Para estabilidad BIBO, todos los polos deben tener parte real negativa.
    
    Parameters:
        tf (ct.TransferFunction): Función de transferencia
    
    Returns:
        np.ndarray: Array de polos (números complejos). Forma (n_polos,)
    
    Examples:
        >>> tf = create_transfer_function([1], [1, 1])  # 1/(s+1)
        >>> poles = get_poles(tf)
        >>> print(poles)
        [-1.+0.j]
    """
    return np.asarray(tf.poles())


def get_zeros(tf: ct.TransferFunction) -> np.ndarray:
    """
    Calcula los ceros de una función de transferencia.
    
    Los ceros son las raíces del polinomio numerador.
    
    Parameters:
        tf (ct.TransferFunction): Función de transferencia
    
    Returns:
        np.ndarray: Array de ceros (números complejos). Forma (n_ceros,)
    
    Examples:
        >>> tf = create_transfer_function([1, 2], [1, 1])  # (s+2)/(s+1)
        >>> zeros = get_zeros(tf)
        >>> print(zeros)
        [-2.+0.j]
    """
    return np.asarray(tf.zeros())


def is_stable(tf: ct.TransferFunction, tolerance: float = 1e-10) -> bool:
    """
    Verifica si una función de transferencia es BIBO-estable.
    
    Un sistema es BIBO-estable (Bounded Input Bounded Output) si todos
    los polos tienen parte real estrictamente negativa.
    
    Parameters:
        tf (ct.TransferFunction): Función de transferencia
        tolerance (float): Tolerancia para considerar parte real como negativa.
                          Default: 1e-10 (sensible a polos muy cercanos al eje imaginario)
    
    Returns:
        bool: True si es estable, False en caso contrario
    
    Examples:
        >>> tf_stable = create_transfer_function([1], [1, 1])  # 1/(s+1)
        >>> is_stable(tf_stable)
        True
        
        >>> tf_unstable = create_transfer_function([1], [1, -1])  # 1/(s-1)
        >>> is_stable(tf_unstable)
        False
        
        >>> tf_marginal = create_transfer_function([1], [1, 0])  # 1/s (polo en origen)
        >>> is_stable(tf_marginal)
        False
    """
    poles = get_poles(tf)
    # Todos los polos deben tener parte real < 0 (con tolerancia)
    return np.all(np.real(poles) < -tolerance)


def get_dc_gain(tf: ct.TransferFunction) -> float:
    """
    Calcula la ganancia DC de una función de transferencia.
    
    La ganancia DC es el valor de G(s) cuando s → 0:
    G(0) = N(0) / D(0) = constante del numerador / constante del denominador
    
    Solo es válida si el sistema es estable en lazo abierto.
    
    Parameters:
        tf (ct.TransferFunction): Función de transferencia
    
    Returns:
        float: Ganancia DC (valor escalar)
    
    Raises:
        ValueError: Si el denominador evaluado en s=0 es cero
    
    Examples:
        >>> tf = create_transfer_function([2], [2, 1])  # 2/(2s+1) = 1/(s+0.5)
        >>> k = get_dc_gain(tf)
        >>> print(f"Ganancia DC: {k:.2f}")
        Ganancia DC: 1.00
    """
    # Evaluar en s = 0
    num_array = np.asarray(tf.num[0][0]).flatten()  # Aplanar coeficientes del numerador
    den_array = np.asarray(tf.den[0][0]).flatten()  # Aplanar coeficientes del denominador
    
    # Evaluar polinomios en s=0 y asegurar que son escalares
    num_at_0 = float(np.polyval(num_array, 0))
    den_at_0 = float(np.polyval(den_array, 0))
    
    if abs(den_at_0) < 1e-15:
        raise ValueError("Denominador es cero en s=0. No hay ganancia DC definida.")
    
    return float(num_at_0 / den_at_0)


if __name__ == "__main__":
    # Ejemplo de uso
    print("=" * 60)
    print("MÓDULO: Transfer Function")
    print("=" * 60)
    
    # Crear G(s) = 1/(s+1)
    print("\nCreando G(s) = 1/(s+1)...")
    tf1 = create_transfer_function([1], [1, 1])
    print(f"G(s) = {tf1}")
    print(f"Polos: {get_poles(tf1)}")
    print(f"Ceros: {get_zeros(tf1)}")
    print(f"¿Estable?: {is_stable(tf1)}")
    print(f"Ganancia DC: {get_dc_gain(tf1):.4f}")
    
    # Crear G(s) = 2/(10s+1) [proceso FOPDT sin retardo]
    print("\n" + "-" * 60)
    print("Creando G(s) = 2/(10s+1) [Proceso FOPDT]...")
    tf2 = create_transfer_function([2], [10, 1])
    print(f"G(s) = {tf2}")
    print(f"Polos: {get_poles(tf2)}")
    print(f"Ganancia DC: {get_dc_gain(tf2):.4f}")
    print(f"¿Estable?: {is_stable(tf2)}")
    
    # Crear sistema inestable
    print("\n" + "-" * 60)
    print("Creando G(s) = 1/(s-1) [Inestable]...")
    tf3 = create_transfer_function([1], [1, -1])
    print(f"G(s) = {tf3}")
    print(f"Polos: {get_poles(tf3)}")
    print(f"¿Estable?: {is_stable(tf3)}")
