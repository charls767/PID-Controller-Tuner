# Arquitectura de Módulos - Backend Python

## Estructura de Directorios

```
pid-tuner/
├── README.md
├── requirements.txt
├── setup.py
│
├── src/
│   ├── __init__.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── transfer_function.py      # Manejo de funciones de transferencia
│   │   └── validation.py              # Validaciones de entrada
│   │
│   ├── tuning/
│   │   ├── __init__.py
│   │   ├── base_tuner.py             # Clase abstracta para sintonizadores
│   │   ├── ziegler_nichols.py        # Método Ziegler–Nichols
│   │   ├── cohen_coon.py             # Método Cohen–Coon
│   │   └── tuning_utils.py           # Funciones auxiliares
│   │
│   ├── simulation/
│   │   ├── __init__.py
│   │   ├── controller.py             # Controlador PID
│   │   ├── simulator.py              # Motor de simulación
│   │   └── metrics.py                # Cálculo de métricas (ts, Mp, ess, tr)
│   │
│   ├── visualization/
│   │   ├── __init__.py
│   │   ├── plotter.py                # Generación de gráficos
│   │   └── styles.py                 # Temas y estilos
│   │
│   └── utils/
│       ├── __init__.py
│       ├── export.py                 # Exportación CSV/PNG
│       ├── logger.py                 # Logging
│       └── constants.py              # Constantes globales
│
├── app/
│   ├── main.py                       # Punto de entrada Streamlit
│   ├── pages/
│   │   ├── __init__.py
│   │   ├── 1_Inicio.py               # Home/Bienvenida
│   │   ├── 2_Diseñador.py            # Interfaz de diseño
│   │   ├── 3_Resultados.py           # Visualización de resultados
│   │   └── 4_Documentacion.py        # Ayuda y teoría
│   │
│   ├── components/
│   │   ├── __init__.py
│   │   ├── input_form.py             # Componente de entrada de G(s)
│   │   ├── results_display.py        # Componente de visualización
│   │   └── sidebar.py                # Barra lateral
│   │
│   └── config.py                     # Configuración de Streamlit
│
├── tests/
│   ├── __init__.py
│   ├── test_transfer_function.py
│   ├── test_ziegler_nichols.py
│   ├── test_cohen_coon.py
│   ├── test_simulator.py
│   ├── test_metrics.py
│   └── fixtures/                     # Datos de prueba
│       └── test_systems.json
│
└── docs/
    ├── MANUAL_USUARIO.md
    ├── TEORÍA.md
    ├── API_BACKEND.md
    └── ARQUITECTURA.md
```

---

## 2. Descripción de Módulos

### **2.1 core/transfer_function.py**
Gestiona la representación y manipulación de funciones de transferencia.

```python
class TransferFunction:
    """Representa una función de transferencia G(s) = N(s)/D(s)"""
    
    def __init__(self, numerador: List[float], denominador: List[float]):
        """Crea una función de transferencia"""
        # Almacena coeficientes, los normaliza, valida
    
    def get_poles(self) -> np.ndarray:
        """Retorna los polos de G(s)"""
    
    def get_zeros(self) -> np.ndarray:
        """Retorna los ceros de G(s)"""
    
    def stability_status(self) -> bool:
        """Verifica si el sistema es estable"""
    
    def evaluate(self, s: complex) -> complex:
        """Evalúa G(s) en un punto del plano complejo"""
```

### **2.2 core/validation.py**
Valida entradas del usuario.

```python
def validate_polynomial(coefficients: List[float]) -> bool:
    """Valida que los coeficientes sean válidos"""

def validate_transfer_function(num, den) -> ValidationResult:
    """Valida una función de transferencia completa"""
```

### **2.3 tuning/base_tuner.py**
Clase abstracta para todos los sintonizadores.

```python
from abc import ABC, abstractmethod

class BaseTuner(ABC):
    """Clase base para métodos de sintonización"""
    
    def __init__(self, tf: TransferFunction):
        self.tf = tf
    
    @abstractmethod
    def tune(self) -> Tuple[float, float, float]:
        """Retorna (Kp, Ti, Td)"""
    
    def validate_applicability(self) -> bool:
        """Verifica si el método es aplicable al sistema"""
```

### **2.4 tuning/ziegler_nichols.py**
Implementa el método Ziegler–Nichols.

```python
class ZieglerNichols(BaseTuner):
    """Sintonización Ziegler–Nichols"""
    
    def __init__(self, tf: TransferFunction, method: str = "step_response"):
        """
        method: "step_response" o "sustained_oscillation"
        """
        super().__init__(tf)
        self.method = method
    
    def tune(self) -> Tuple[float, float, float]:
        """Calcula parámetros PID"""
        if self.method == "step_response":
            return self._tune_step_response()
        else:
            return self._tune_sustained_oscillation()
    
    def _tune_step_response(self) -> Tuple[float, float, float]:
        """Método de la curva de reacción"""
        # Implementar: extrae L (retardo), T (constante de tiempo)
        # Kp = 1.2*T/(L*K), Ti = 2*L, Td = 0.5*L
    
    def _tune_sustained_oscillation(self) -> Tuple[float, float, float]:
        """Método del lazo cerrado con oscilaciones sostenidas"""
        # Implementar: encuentra Kcr (ganancia crítica), Pcr (período crítico)
```

### **2.5 tuning/cohen_coon.py**
Implementa el método Cohen–Coon.

```python
class CohenCoon(BaseTuner):
    """Sintonización Cohen–Coon"""
    
    def tune(self) -> Tuple[float, float, float]:
        """Calcula parámetros PID con mejoramientos Cohen–Coon"""
        # Kp más agresivo que Ziegler–Nichols
        # Incluye términos de corrección para sistemas con retardo
```

### **2.6 simulation/controller.py**
Representa el controlador PID.

```python
class PIDController:
    """Controlador PID digital o analógico"""
    
    def __init__(self, Kp: float, Ti: float, Td: float, dt: float = 0.01):
        """
        Kp: ganancia proporcional
        Ti: tiempo integral (segundos)
        Td: tiempo derivativo (segundos)
        dt: paso de tiempo de muestreo
        """
    
    def update(self, error: float) -> float:
        """Calcula acción de control dado el error"""
    
    def reset(self):
        """Reinicia el estado del controlador"""
```

### **2.7 simulation/simulator.py**
Motor de simulación del sistema en lazo cerrado.

```python
class SimulationEngine:
    """Simula la respuesta del sistema con y sin controlador"""
    
    def __init__(self, tf: TransferFunction, dt: float = 0.01, t_max: float = 20):
        self.tf = tf
        self.dt = dt
        self.t_max = t_max
    
    def open_loop(self, reference: float = 1.0) -> Tuple[np.ndarray, np.ndarray]:
        """Simula respuesta sin control. Retorna (tiempo, salida)"""
    
    def closed_loop(self, controller: PIDController, 
                    reference: float = 1.0) -> Tuple[np.ndarray, np.ndarray]:
        """Simula respuesta con PID. Retorna (tiempo, salida)"""
```

### **2.8 simulation/metrics.py**
Calcula métricas de desempeño.

```python
class PerformanceMetrics:
    """Calcula métricas de la respuesta del sistema"""
    
    @staticmethod
    def settling_time(time: np.ndarray, response: np.ndarray, 
                      tolerance: float = 0.05) -> float:
        """Tiempo de establecimiento (ts) - tiempo para ±5%"""
    
    @staticmethod
    def overshoot(response: np.ndarray, final_value: float) -> float:
        """Sobreimpulso (Mp) en porcentaje"""
    
    @staticmethod
    def steady_state_error(response: np.ndarray, reference: float) -> float:
        """Error en estado estacionario (ess)"""
    
    @staticmethod
    def rise_time(time: np.ndarray, response: np.ndarray) -> float:
        """Tiempo de levantamiento (tr) - 10% a 90%"""
    
    @staticmethod
    def calculate_all(time: np.ndarray, response: np.ndarray, 
                      reference: float = 1.0) -> Dict[str, float]:
        """Retorna diccionario con todas las métricas"""
```

### **2.9 visualization/plotter.py**
Genera visualizaciones.

```python
class Plotter:
    """Genera gráficos para Streamlit"""
    
    @staticmethod
    def compare_responses(time: np.ndarray, 
                         y_open_loop: np.ndarray,
                         y_closed_loop: np.ndarray,
                         title: str = "Comparación de Respuestas") -> go.Figure:
        """Gráfico interactivo de comparación"""
    
    @staticmethod
    def pole_zero_map(tf: TransferFunction) -> go.Figure:
        """Diagrama de polos y ceros"""
    
    @staticmethod
    def step_response_detail(time: np.ndarray, 
                            response: np.ndarray,
                            metrics: Dict) -> go.Figure:
        """Gráfico detallado con tabla de métricas"""
```

### **2.10 utils/export.py**
Exporta resultados.

```python
class Exporter:
    """Exporta resultados a CSV y PNG"""
    
    @staticmethod
    def export_csv(df: pd.DataFrame, filename: str) -> bytes:
        """Exporta resultados a CSV"""
    
    @staticmethod
    def export_figure_png(fig: go.Figure, filename: str) -> bytes:
        """Exporta gráfico a PNG"""
```

---

## 3. Flujo de Datos

```
Usuario → Streamlit UI
    ↓
[Input: num[], den[]]
    ↓
Validación → Transfer Function
    ↓
Selector de Método (ZN / CC)
    ↓
Tuner.tune() → (Kp, Ti, Td)
    ↓
SimulationEngine
    ├─→ open_loop() → y_open
    └─→ closed_loop() → y_closed
    ↓
PerformanceMetrics.calculate_all()
    ↓
Plotter.create_figures()
    ↓
Streamlit Display + Export Options
    ↓
Usuario
```

---

## 4. Dependencias Entre Módulos

```
core/ (independiente)
├─ validation.py
├─ transfer_function.py
│
tuning/ (depende de core)
├─ base_tuner.py
├─ ziegler_nichols.py (extends base_tuner)
├─ cohen_coon.py (extends base_tuner)
│
simulation/ (depende de core, usa tuning para parámetros)
├─ controller.py
├─ simulator.py (usa controller, transfer_function)
├─ metrics.py
│
visualization/ (depende de simulation)
├─ plotter.py (visualiza resultados)
│
utils/ (independiente, usado por todos)

app/ (Streamlit - integra todos los módulos)
```

---

## 5. Tecnologías por Módulo

| Módulo | Librerías |
|--------|-----------|
| `core/` | `numpy`, `scipy.signal` |
| `tuning/` | `scipy`, `numpy` |
| `simulation/` | `scipy`, `numpy`, `control` |
| `metrics/` | `numpy`, `pandas` |
| `visualization/` | `matplotlib`, `plotly` |
| `app/` | `streamlit`, todos los anteriores |
| `utils/` | `pandas`, `matplotlib` |

---

## 6. Estándares de Codificación

- **Nomenclatura**: snake_case para funciones/variables, PascalCase para clases
- **Docstrings**: formato Google o NumPy
- **Type hints**: todas las funciones públicas
- **Logging**: usar módulo `logging` estándar
- **Errores personalizados**: en `src/core/exceptions.py`

```python
class InvalidTransferFunctionError(Exception):
    """Se levanta cuando la función de transferencia es inválida"""

class TuningError(Exception):
    """Se levanta cuando el método de sintonización falla"""
```

