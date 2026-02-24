"""
API del Backend - Sintonizador de Controladores PID

Este módulo define las firmas de todas las funciones principales del backend.
Cada función está documentada con sus parámetros, retornos y propósito.

Uso: Guía para implementación de los módulos src/
"""

from typing import List, Tuple, Dict, Optional, NamedTuple
from dataclasses import dataclass
import numpy as np


# ============================================================================
# TIPO DE DATOS: Modelo FOPDT
# ============================================================================

class FOPDTModel(NamedTuple):
    """
    Modelo de Primer Orden + Retardo de Transporte.
    
    Attributes:
        K (float): Ganancia DC del proceso (adimensional o unidades/%)
        L (float): Retardo de transporte (segundos) - tiempo muerto
        T (float): Constante de tiempo (segundos) - velocidad de respuesta
    """
    K: float
    L: float
    T: float


class PIDParameters(NamedTuple):
    """
    Parámetros sintonizados de un controlador PID.
    
    Attributes:
        Kp (float): Ganancia proporcional
        Ti (float): Tiempo integral (segundos)
        Td (float): Tiempo derivativo (segundos)
        method (str): Método de sintonización usado ("ZN" o "CC")
    """
    Kp: float
    Ti: float
    Td: float
    method: str


@dataclass
class PerformanceMetricsResult:
    """
    Métricas de desempeño de la respuesta del sistema.
    
    Attributes:
        settling_time (float): Tiempo de establecimiento [segundos] - 5% de tolerancia
        overshoot (float): Sobreimpulso máximo [porcentaje] - 0 a 100
        steady_state_error (float): Error en estado estacionario [valor absoluto]
        rise_time (float): Tiempo de levantamiento [segundos] - 10% a 90%
        peak_value (float): Valor máximo alcanzado
        peak_time (float): Tiempo en el que se alcanza el pico [segundos]
    """
    settling_time: float
    overshoot: float
    steady_state_error: float
    rise_time: float
    peak_value: float
    peak_time: float


@dataclass
class SimulationResult:
    """
    Resultado de una simulación de respuesta del sistema.
    
    Attributes:
        time (np.ndarray): Vector de tiempo [segundos] - forma (n_steps,)
        output (np.ndarray): Salida del sistema y(t) - forma (n_steps,)
        control_signal (Optional[np.ndarray]): Acción de control u(t) para PID - forma (n_steps,)
        reference (np.ndarray): Referencia deseada r(t) - forma (n_steps,)
    """
    time: np.ndarray
    output: np.ndarray
    control_signal: Optional[np.ndarray] = None
    reference: Optional[np.ndarray] = None


# ============================================================================
# MÓDULO 1: CORE - FUNCIONES DE TRANSFERENCIA
# ============================================================================

def create_transfer_function(numerator: List[float], 
                            denominator: List[float]) -> object:
    """
    Crea una función de transferencia G(s) = N(s) / D(s).
    
    La función de transferencia se almacena internamente como polinomios
    de coeficientes en orden descendente de potencia.
    
    Parameters:
        numerator (List[float]): Coeficientes del numerador N(s)
                               Ej: [1, 2] representa (s + 2)
                               Debe ser lista no vacía
        denominator (List[float]): Coeficientes del denominador D(s)
                                 Ej: [1, 3, 2] representa (s² + 3s + 2)
                                 Debe ser lista no vacía, no todo ceros
    
    Returns:
        TransferFunction: Objeto que representa G(s)
    
    Raises:
        ValueError: Si numerador o denominador están vacíos
        ValueError: Si denominador es todo ceros
        ValueError: Si los coeficientes no son numéricos
    
    Example:
        >>> # Crear G(s) = (s + 2) / (s² + 3s + 2)
        >>> tf = create_transfer_function([1, 2], [1, 3, 2])
        >>> print(tf)
        TransferFunction: (s + 2) / (s² + 3s + 2)
    """
    pass


def get_transfer_function_poles(tf: object) -> np.ndarray:
    """
    Calcula los polos de una función de transferencia.
    
    Los polos son las raíces del polinomio denominador.
    Un sistema es BIBO-estable si todos los polos están en el
    semiplano izquierdo (Re(p) < 0).
    
    Parameters:
        tf (TransferFunction): Función de transferencia creada con create_transfer_function()
    
    Returns:
        np.ndarray: Array de polos (complejos). Forma (n_polos,)
    
    Example:
        >>> tf = create_transfer_function([1], [1, 1])  # 1/(s+1)
        >>> poles = get_transfer_function_poles(tf)
        >>> print(poles)
        array([-1.+0.j])
    """
    pass


def get_transfer_function_zeros(tf: object) -> np.ndarray:
    """
    Calcula los ceros de una función de transferencia.
    
    Los ceros son las raíces del polinomio numerador.
    
    Parameters:
        tf (TransferFunction): Función de transferencia
    
    Returns:
        np.ndarray: Array de ceros (complejos). Forma (n_ceros,)
    
    Example:
        >>> tf = create_transfer_function([1, 2], [1, 1])  # (s+2)/(s+1)
        >>> zeros = get_transfer_function_zeros(tf)
        >>> print(zeros)
        array([-2.+0.j])
    """
    pass


def is_transfer_function_stable(tf: object) -> bool:
    """
    Verifica si una función de transferencia es BIBO-estable.
    
    Un sistema es BIBO-estable si y solo si todos los polos
    tienen parte real estrictamente negativa.
    
    Parameters:
        tf (TransferFunction): Función de transferencia
    
    Returns:
        bool: True si es estable, False en caso contrario
    
    Example:
        >>> tf_stable = create_transfer_function([1], [1, 1])  # 1/(s+1)
        >>> is_transfer_function_stable(tf_stable)
        True
        
        >>> tf_unstable = create_transfer_function([1], [1, -1])  # 1/(s-1)
        >>> is_transfer_function_stable(tf_unstable)
        False
    """
    pass


# ============================================================================
# MÓDULO 2: IDENTIFICACIÓN - APROXIMACIÓN A MODELO FOPDT
# ============================================================================

def approximate_to_fopdt_from_step_response(time: np.ndarray, 
                                            response: np.ndarray, 
                                            reference: float = 1.0) -> FOPDTModel:
    """
    Aproxima un modelo FOPDT a partir de la respuesta al escalón del sistema.
    
    Utiliza el método de la tangente (método de Miller):
    1. Identifica el retardo L (tiempo en que comienza el cambio)
    2. Calcula la constante de tiempo T usando el punto 63.2% del valor final
    3. Extrae K como el valor final de la respuesta normalizado
    
    Parameters:
        time (np.ndarray): Vector de tiempo [segundos]. Forma (n_steps,)
        response (np.ndarray): Respuesta del sistema y(t). Forma (n_steps,)
        reference (float): Valor de referencia (valor final esperado). Default: 1.0
    
    Returns:
        FOPDTModel: Modelo FOPDT con parámetros K, L, T
                   K: ganancia DC
                   L: retardo de transporte [segundos]
                   T: constante de tiempo [segundos]
    
    Raises:
        ValueError: Si el tiempo y respuesta tienen dimensiones distintas
        ValueError: Si el vector de tiempo no es monótonamente creciente
    
    Example:
        >>> time = np.linspace(0, 50, 1000)
        >>> response = 2 * (1 - np.exp(-time / 10))  # Respuesta teórica
        >>> model = approximate_to_fopdt_from_step_response(time, response, ref=2.0)
        >>> print(f"K={model.K:.2f}, L={model.L:.2f}, T={model.T:.2f}")
        K=2.00, L=0.00, T=10.00
    """
    pass


def approximate_to_fopdt_from_transfer_function(tf: object) -> FOPDTModel:
    """
    Aproxima un modelo FOPDT a partir de una función de transferencia arbitraria.
    
    Simula la respuesta al escalón de la función de transferencia y luego
    aplica approximate_to_fopdt_from_step_response() para la identificación.
    
    Parameters:
        tf (TransferFunction): Función de transferencia (puede ser orden arbitrario)
    
    Returns:
        FOPDTModel: Modelo FOPDT aproximado
    
    Raises:
        ValueError: Si la función de transferencia es inestable
    
    Example:
        >>> tf = create_transfer_function([1], [1, 1])  # 1/(s+1)
        >>> model = approximate_to_fopdt_from_transfer_function(tf)
        >>> print(model)
        FOPDTModel(K=1.0, L=0.0, T=1.0)
    """
    pass


# ============================================================================
# MÓDULO 3: SINTONIZACIÓN - ZIEGLER-NICHOLS
# ============================================================================

def tune_pid_ziegler_nichols(fopdt_model: FOPDTModel, 
                             method: str = "step_response",
                             control_type: str = "PID") -> PIDParameters:
    """
    Calcula parámetros PID usando el método de Ziegler–Nichols.
    
    Es el método más clásico y popular. Utiliza los parámetros del modelo FOPDT
    (K, L, T) para calcular Kp, Ti, Td.
    
    El método de la curva de reacción (step_response) es el más usado:
    - Kp = 1.2 * T / (L * K)
    - Ti = 2 * L
    - Td = 0.5 * L
    
    Parameters:
        fopdt_model (FOPDTModel): Modelo FOPDT con parámetros K, L, T
        method (str): "step_response" (por defecto) o "sustained_oscillation"
                     - step_response: Usa la curva de reacción
                     - sustained_oscillation: Usa método del lazo cerrado
        control_type (str): "P", "PI", o "PID" (default)
                          Determina qué parámetros calcular
    
    Returns:
        PIDParameters: Parámetros sintonizados (Kp, Ti, Td, method="ZN")
    
    Raises:
        ValueError: Si L/T > 0.5 (aviso: método menos preciso)
        ValueError: Si los parámetros FOPDT son inconsistentes
    
    Example:
        >>> model = FOPDTModel(K=1.0, L=2.0, T=10.0)
        >>> pid = tune_pid_ziegler_nichols(model, method="step_response", control_type="PID")
        >>> print(f"Kp={pid.Kp:.2f}, Ti={pid.Ti:.2f}, Td={pid.Td:.2f}")
        Kp=6.00, Ti=4.00, Td=1.00
    """
    pass


def tune_pid_ziegler_nichols_from_transfer_function(tf: object,
                                                    method: str = "step_response") -> PIDParameters:
    """
    Versión simplificada: Ziegler–Nichols directamente desde G(s).
    
    Combina: approximate_to_fopdt_from_transfer_function() + tune_pid_ziegler_nichols()
    
    Parameters:
        tf (TransferFunction): Función de transferencia arbitraria
        method (str): "step_response" o "sustained_oscillation"
    
    Returns:
        PIDParameters: Parámetros PID sintonizados
    
    Example:
        >>> tf = create_transfer_function([1], [1, 3, 2])
        >>> pid = tune_pid_ziegler_nichols_from_transfer_function(tf)
        >>> print(pid)
        PIDParameters(Kp=..., Ti=..., Td=..., method='ZN')
    """
    pass


# ============================================================================
# MÓDULO 4: SINTONIZACIÓN - COHEN-COON
# ============================================================================

def tune_pid_cohen_coon(fopdt_model: FOPDTModel,
                        criterion: str = "IAE",
                        control_type: str = "PID") -> PIDParameters:
    """
    Calcula parámetros PID usando el método de Cohen–Coon.
    
    Mejora sobre Ziegler–Nichols con fórmulas más refinadas. Produce
    menor overshoot y mejor rechazo a perturbaciones.
    
    Para L/T < 0.3 usa fórmulas simplificadas:
    - Kp = 1.35 * T / (L * K)
    - Ti = 2.5 * L
    - Td = 0.37 * L
    
    Para L/T >= 0.3 usa fórmulas generales con factor de corrección.
    
    Parameters:
        fopdt_model (FOPDTModel): Modelo FOPDT con parámetros K, L, T
        criterion (str): "IAE" (Integral Absolute Error) - default
                        Criterio de optimización
        control_type (str): "P", "PI", o "PID" (default)
    
    Returns:
        PIDParameters: Parámetros sintonizados (Kp, Ti, Td, method="CC")
    
    Raises:
        ValueError: Si los parámetros FOPDT son inválidos
    
    Example:
        >>> model = FOPDTModel(K=1.0, L=2.0, T=10.0)
        >>> pid = tune_pid_cohen_coon(model, criterion="IAE", control_type="PID")
        >>> print(f"Kp={pid.Kp:.2f}, Ti={pid.Ti:.2f}, Td={pid.Td:.2f}")
        Kp=6.75, Ti=5.00, Td=0.74
    """
    pass


def tune_pid_cohen_coon_from_transfer_function(tf: object) -> PIDParameters:
    """
    Versión simplificada: Cohen–Coon directamente desde G(s).
    
    Parameters:
        tf (TransferFunction): Función de transferencia
    
    Returns:
        PIDParameters: Parámetros PID sintonizados
    
    Example:
        >>> tf = create_transfer_function([2], [10, 1])
        >>> pid = tune_pid_cohen_coon_from_transfer_function(tf)
        >>> print(pid)
        PIDParameters(Kp=..., Ti=..., Td=..., method='CC')
    """
    pass


def compare_tuning_methods(fopdt_model: FOPDTModel) -> Dict[str, PIDParameters]:
    """
    Compara Ziegler–Nichols vs Cohen–Coon para el mismo modelo.
    
    Útil para análisis y decisión de qué método usar.
    
    Parameters:
        fopdt_model (FOPDTModel): Modelo FOPDT
    
    Returns:
        Dict con claves "ZN" y "CC", valores PIDParameters
    
    Example:
        >>> model = FOPDTModel(K=1.0, L=2.0, T=10.0)
        >>> comparison = compare_tuning_methods(model)
        >>> print(comparison["ZN"])
        >>> print(comparison["CC"])
    """
    pass


# ============================================================================
# MÓDULO 5: SIMULACIÓN - SIN CONTROLADOR (LAZO ABIERTO)
# ============================================================================

def simulate_open_loop(tf: object,
                       reference: float = 1.0,
                       t_final: float = 50.0,
                       dt: float = 0.01) -> SimulationResult:
    """
    Simula la respuesta del sistema en lazo abierto (sin controlador).
    
    Resuelve la ecuación diferencial ordinaria (ODE) que describe el sistema
    usando métodos de integración numérica (RK4 o similar).
    
    Parameters:
        tf (TransferFunction): Función de transferencia G(s)
        reference (float): Magnitud del escalón de entrada. Default: 1.0
        t_final (float): Tiempo final de simulación [segundos]. Default: 50.0
                        Se ajusta automáticamente si el sistema es muy lento
        dt (float): Paso de tiempo de simulación [segundos]. Default: 0.01
    
    Returns:
        SimulationResult: Objeto con campos:
                         - time: vector de tiempo
                         - output: salida y(t)
                         - control_signal: None (no hay controlador)
                         - reference: referencia constante
    
    Example:
        >>> tf = create_transfer_function([1], [1, 1])  # 1/(s+1)
        >>> result = simulate_open_loop(tf, reference=1.0, t_final=5.0)
        >>> print(f"Tamaño: {len(result.time)} muestras")
        >>> print(f"Valor final: {result.output[-1]:.4f}")
        Tamaño: 501 muestras
        Valor final: 0.9933
    """
    pass


# ============================================================================
# MÓDULO 6: SIMULACIÓN - CON CONTROLADOR PID (LAZO CERRADO)
# ============================================================================

def simulate_closed_loop_with_pid(tf: object,
                                  pid_params: PIDParameters,
                                  reference: float = 1.0,
                                  t_final: float = 50.0,
                                  dt: float = 0.01) -> SimulationResult:
    """
    Simula la respuesta del sistema en lazo cerrado con controlador PID.
    
    Implementa el PID en tiempo discreto:
    u[k] = Kp*(e[k] + (dt/Ti)*sum(e) + (Td/dt)*(e[k]-e[k-1]))
    
    Parameters:
        tf (TransferFunction): Función de transferencia del sistema G(s)
        pid_params (PIDParameters): Parámetros PID (Kp, Ti, Td)
        reference (float): Referencia deseada r(t). Default: 1.0
        t_final (float): Tiempo final de simulación [segundos]. Default: 50.0
        dt (float): Paso de tiempo [segundos]. Default: 0.01
    
    Returns:
        SimulationResult: Objeto con campos:
                         - time: vector de tiempo
                         - output: salida controlada y(t)
                         - control_signal: acción de control u(t)
                         - reference: referencia constante
    
    Example:
        >>> tf = create_transfer_function([1], [1, 3, 2])
        >>> pid = PIDParameters(Kp=2.0, Ti=1.0, Td=0.5, method="ZN")
        >>> result = simulate_closed_loop_with_pid(tf, pid, reference=1.0)
        >>> print(f"Salida final: {result.output[-1]:.4f}")
        >>> print(f"Control final: {result.control_signal[-1]:.4f}")
        Salida final: 0.9998
        Control final: 0.0045
    """
    pass


def simulate_comparison(tf: object,
                       pid_params: PIDParameters,
                       reference: float = 1.0,
                       t_final: float = 50.0,
                       dt: float = 0.01) -> Tuple[SimulationResult, SimulationResult]:
    """
    Simula ambos escenarios: lazo abierto vs lazo cerrado con PID.
    
    Versión conveniente que retorna ambas simulaciones juntas.
    
    Parameters:
        tf (TransferFunction): Función de transferencia
        pid_params (PIDParameters): Parámetros PID
        reference (float): Referencia deseada
        t_final (float): Tiempo final [segundos]
        dt (float): Paso de tiempo [segundos]
    
    Returns:
        Tuple[SimulationResult, SimulationResult]: (open_loop_result, closed_loop_result)
    
    Example:
        >>> tf = create_transfer_function([1], [1, 1, 1])
        >>> pid = tune_pid_ziegler_nichols_from_transfer_function(tf)
        >>> open_result, closed_result = simulate_comparison(tf, pid)
        >>> # Comparar resultados
    """
    pass


# ============================================================================
# MÓDULO 7: MÉTRICAS DE DESEMPEÑO
# ============================================================================

def calculate_performance_metrics(time: np.ndarray,
                                 response: np.ndarray,
                                 reference: float = 1.0,
                                 tolerance: float = 0.05) -> PerformanceMetricsResult:
    """
    Calcula todas las métricas de desempeño de una respuesta.
    
    Métricas calculadas:
    - settling_time: Tiempo para entrar en ±5% del valor final
    - overshoot: Máximo porcentaje de sobrepaso
    - steady_state_error: Error final respecto a la referencia
    - rise_time: Tiempo de 10% a 90% del valor final
    - peak_value: Valor máximo alcanzado
    - peak_time: Tiempo en que se alcanza el pico
    
    Parameters:
        time (np.ndarray): Vector de tiempo [segundos]. Forma (n_steps,)
        response (np.ndarray): Respuesta del sistema y(t). Forma (n_steps,)
        reference (float): Valor de referencia deseado. Default: 1.0
        tolerance (float): Tolerancia para settling time [fracción]. Default: 0.05 (5%)
    
    Returns:
        PerformanceMetricsResult: Objeto con todas las métricas
    
    Raises:
        ValueError: Si time y response tienen longitudes distintas
    
    Example:
        >>> import numpy as np
        >>> time = np.linspace(0, 10, 1000)
        >>> # Respuesta de 1er orden: y(t) = 1 - exp(-t)
        >>> response = 1 - np.exp(-time)
        >>> metrics = calculate_performance_metrics(time, response, reference=1.0)
        >>> print(f"ts={metrics.settling_time:.2f}s")
        >>> print(f"Mp={metrics.overshoot:.2f}%")
        >>> print(f"tr={metrics.rise_time:.2f}s")
        ts=3.00s
        Mp=0.00%
        tr=2.20s
    """
    pass


def calculate_metrics_for_comparison(time_ol: np.ndarray,
                                    response_ol: np.ndarray,
                                    time_cl: np.ndarray,
                                    response_cl: np.ndarray,
                                    reference: float = 1.0) -> Tuple[PerformanceMetricsResult, PerformanceMetricsResult]:
    """
    Calcula métricas para ambas respuestas (abierta y cerrada).
    
    Versión conveniente que retorna ambas métricas juntas de manera
    comparable.
    
    Parameters:
        time_ol (np.ndarray): Vector de tiempo para lazo abierto
        response_ol (np.ndarray): Respuesta en lazo abierto
        time_cl (np.ndarray): Vector de tiempo para lazo cerrado
        response_cl (np.ndarray): Respuesta en lazo cerrado
        reference (float): Referencia deseada
    
    Returns:
        Tuple: (metrics_open_loop, metrics_closed_loop)
    
    Example:
        >>> # Usar después de simulate_comparison()
        >>> open_result, closed_result = simulate_comparison(tf, pid)
        >>> metrics_ol, metrics_cl = calculate_metrics_for_comparison(
        ...     open_result.time, open_result.output,
        ...     closed_result.time, closed_result.output,
        ...     reference=1.0
        ... )
    """
    pass


# ============================================================================
# MÓDULO 8: UTILIDADES Y VALIDACIÓN
# ============================================================================

def validate_pid_parameters(pid_params: PIDParameters,
                           fopdt_model: Optional[FOPDTModel] = None) -> bool:
    """
    Valida que los parámetros PID sintonizados sean razonables.
    
    Comprobaciones:
    - Kp > 0
    - Ti > 0
    - Td >= 0
    - Ti > 4*Td (relación típica)
    - Valores dentro de rangos físicamente realizables
    
    Parameters:
        pid_params (PIDParameters): Parámetros a validar
        fopdt_model (Optional[FOPDTModel]): Modelo para contexto adicional
    
    Returns:
        bool: True si son válidos, False en caso contrario
    
    Raises:
        ValueError: Si al menos un parámetro es inválido
    
    Example:
        >>> pid = PIDParameters(Kp=2.0, Ti=1.0, Td=0.25, method="ZN")
        >>> validate_pid_parameters(pid)
        True
    """
    pass


def validate_fopdt_model(fopdt_model: FOPDTModel) -> bool:
    """
    Valida que el modelo FOPDT sea físicamente realizable.
    
    Comprobaciones:
    - K > 0
    - L >= 0 (no negativo)
    - T > 0
    - L/T < 1 (relación razonable)
    
    Parameters:
        fopdt_model (FOPDTModel): Modelo a validar
    
    Returns:
        bool: True si es válido
    
    Raises:
        ValueError: Con mensaje descriptivo si hay problemas
    """
    pass


# ============================================================================
# EJEMPLO DE FLUJO COMPLETO (PSEUDOCÓDIGO)
# ============================================================================

def complete_pid_design_workflow(numerator: List[float],
                                denominator: List[float],
                                tuning_method: str = "ZN",
                                reference: float = 1.0) -> Dict:
    """
    Ejecuta el flujo completo de diseño PID.
    
    Pasos:
    1. Crear función de transferencia
    2. Aproximar a modelo FOPDT
    3. Sintonizar PID (ZN o CC)
    4. Validar parámetros
    5. Simular ambos escenarios
    6. Calcular métricas
    
    Parameters:
        numerator (List[float]): Coeficientes del numerador
        denominator (List[float]): Coeficientes del denominador
        tuning_method (str): "ZN" o "CC"
        reference (float): Valor de referencia
    
    Returns:
        Dict con todas las salidas:
        {
            "transfer_function": ...,
            "fopdt_model": FOPDTModel(...),
            "pid_parameters": PIDParameters(...),
            "simulation_open_loop": SimulationResult(...),
            "simulation_closed_loop": SimulationResult(...),
            "metrics_open_loop": PerformanceMetricsResult(...),
            "metrics_closed_loop": PerformanceMetricsResult(...),
            "status": "SUCCESS" o "ERROR"
        }
    
    Example:
        >>> result = complete_pid_design_workflow(
        ...     numerator=[1],
        ...     denominator=[10, 1],
        ...     tuning_method="ZN"
        ... )
        >>> if result["status"] == "SUCCESS":
        ...     print(result["pid_parameters"])
        ...     print(result["metrics_closed_loop"])
    """
    pass


# ============================================================================
# FUNCIONES AUXILIARES (OPCIONAL)
# ============================================================================

def export_results_to_csv(simulation_results: Dict,
                         metrics_results: Dict,
                         filename: str) -> None:
    """
    Exporta resultados de simulación y métricas a archivo CSV.
    
    Parameters:
        simulation_results (Dict): Resultados de simulación
        metrics_results (Dict): Resultados de métricas
        filename (str): Ruta del archivo (ej: "resultados.csv")
    
    Returns:
        None
    """
    pass


def export_figure_to_png(figure_object: object,
                        filename: str) -> None:
    """
    Exporta un gráfico (Plotly/Matplotlib) a formato PNG.
    
    Parameters:
        figure_object (object): Objeto Figure de Plotly o Matplotlib
        filename (str): Ruta del archivo (ej: "comparacion.png")
    
    Returns:
        None
    """
    pass


def create_comparison_plot(time_ol: np.ndarray,
                          response_ol: np.ndarray,
                          time_cl: np.ndarray,
                          response_cl: np.ndarray,
                          reference: float = 1.0) -> object:
    """
    Crea un gráfico interactivo de comparación (Plotly).
    
    Parameters:
        time_ol (np.ndarray): Tiempo lazo abierto
        response_ol (np.ndarray): Respuesta lazo abierto
        time_cl (np.ndarray): Tiempo lazo cerrado
        response_cl (np.ndarray): Respuesta lazo cerrado
        reference (float): Línea de referencia
    
    Returns:
        object: Figure de Plotly
    """
    pass


# ============================================================================
# NOTAS DE IMPLEMENTACIÓN
# ============================================================================

"""
ORDEN RECOMENDADO DE IMPLEMENTACIÓN:

Fase 1 (Módulo 1):
  ✓ create_transfer_function()
  ✓ get_transfer_function_poles()
  ✓ get_transfer_function_zeros()
  ✓ is_transfer_function_stable()

Fase 2 (Módulo 2):
  ✓ approximate_to_fopdt_from_step_response()
  ✓ approximate_to_fopdt_from_transfer_function()

Fase 3 (Módulo 3 & 4):
  ✓ tune_pid_ziegler_nichols()
  ✓ tune_pid_ziegler_nichols_from_transfer_function()
  ✓ tune_pid_cohen_coon()
  ✓ tune_pid_cohen_coon_from_transfer_function()
  ✓ compare_tuning_methods()

Fase 4 (Módulo 5 & 6):
  ✓ simulate_open_loop()
  ✓ simulate_closed_loop_with_pid()
  ✓ simulate_comparison()

Fase 5 (Módulo 7):
  ✓ calculate_performance_metrics()
  ✓ calculate_metrics_for_comparison()

Fase 6 (Módulo 8):
  ✓ validate_pid_parameters()
  ✓ validate_fopdt_model()
  ✓ complete_pid_design_workflow()

Fase 7 (Utilidades):
  ✓ export_results_to_csv()
  ✓ export_figure_to_png()
  ✓ create_comparison_plot()


DEPENDENCIAS ENTRE FUNCIONES:

create_transfer_function
├── get_transfer_function_poles
├── get_transfer_function_zeros
├── is_transfer_function_stable
├── approximate_to_fopdt_from_transfer_function
└── simulate_open_loop / simulate_closed_loop_with_pid

approximate_to_fopdt_from_step_response
└── approximate_to_fopdt_from_transfer_function

tune_pid_ziegler_nichols
├── tune_pid_ziegler_nichols_from_transfer_function
├── compare_tuning_methods
└── complete_pid_design_workflow

simulate_open_loop / simulate_closed_loop_with_pid
├── simulate_comparison
├── calculate_performance_metrics
└── complete_pid_design_workflow

calculate_performance_metrics
└── calculate_metrics_for_comparison


LIBRERÍAS REQUERIDAS:

import numpy as np
from scipy.integrate import odeint  # Para ODE
from scipy.signal import step       # Para respuesta al escalón
from scipy.optimize import minimize # Para identificación (opcional)
import plotly.graph_objects as go   # Para gráficos
from dataclasses import dataclass
from typing import NamedTuple, List, Dict, Tuple, Optional
"""
