# Guía Rápida de Inicio

**Proyecto:** Sintonizador de Controladores PID  
**Fecha:** 2026-02-24  
**Versión:** 1.0 (Especificación)

---

## 📋 Documentos de Referencia

He creado **4 documentos principales** para tu proyecto:

### 1. **ESPECIFICACION.md**
   - Requisitos funcionales (RF1-RF7)
   - Requisitos no funcionales (RNF1-RNF6)
   - Criterios de aceptación
   - Priorización MoSCoW

### 2. **ARQUITECTURA_MODULOS.md**
   - Estructura de directorios completa
   - Diseño de 10 módulos principales
   - Clases y métodos por módulo
   - Flujo de datos y dependencias

### 3. **FLUJO_USUARIO.md**
   - Experiencia de usuario paso a paso
   - 4 páginas Streamlit diseñadas
   - Mockups de interfaz
   - Manejo de errores

### 4. **PLAN_IMPLEMENTACION.md**
   - 8 fases de desarrollo (7 semanas)
   - Tasks desglosadas por fase
   - Dependencias entre fases
   - Casos de prueba críticos

---

## 🎯 Resumen Ejecutivo

**¿Qué hace este sistema?**
- El usuario ingresa una función de transferencia G(s)
- Elige método de sintonización: Ziegler–Nichols o Cohen–Coon
- El sistema calcula parámetros PID: Kp, Ti, Td
- Visualiza respuesta al escalón (con y sin controlador)
- Muestra métricas: ts, Mp, ess, tr
- Exporta resultados en CSV/PNG

**¿Por qué esta arquitectura?**
- **Modular:** Fácil de extender con nuevos métodos
- **Testeable:** Separación clear entre lógica y UI
- **Escalable:** Backend independiente de Streamlit
- **Mantenible:** Documentación y estándares claros

---

## 🏗️ Arquitectura en 60 Segundos

```
┌─────────────────────────────────────────┐
│         FRONTEND (Streamlit)            │
│  • Ingreso de parámetros                │
│  • Visualización de resultados          │
│  • Exportación                          │
└────────────────┬────────────────────────┘
                 │
┌─────────────────▼────────────────────────┐
│        BACKEND (Módulos Python)         │
│                                         │
│  core/                                  │
│  ├─ TransferFunction                    │
│  └─ Validation                          │
│                                         │
│  tuning/                                │
│  ├─ BaseTuner                           │
│  ├─ ZieglerNichols                      │
│  └─ CohenCoon                           │
│                                         │
│  simulation/                            │
│  ├─ PIDController                       │
│  ├─ SimulationEngine                    │
│  └─ PerformanceMetrics                  │
│                                         │
│  visualization/                         │
│  ├─ Plotter                             │
│  └─ Styles                              │
│                                         │
│  utils/                                 │
│  ├─ Export                              │
│  ├─ Logger                              │
│  └─ Constants                           │
└─────────────────────────────────────────┘
```

---

## 📊 Estructura de Directorios (Lista Completa)

```
pid-tuner/
├── README.md
├── requirements.txt
├── setup.py
├── .gitignore
├── .pylintrc
│
├── src/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── exceptions.py           [AGREGAR]
│   │   ├── transfer_function.py
│   │   └── validation.py
│   ├── tuning/
│   │   ├── __init__.py
│   │   ├── base_tuner.py
│   │   ├── ziegler_nichols.py
│   │   ├── cohen_coon.py
│   │   └── tuning_utils.py
│   ├── simulation/
│   │   ├── __init__.py
│   │   ├── controller.py
│   │   ├── simulator.py
│   │   └── metrics.py
│   ├── visualization/
│   │   ├── __init__.py
│   │   ├── plotter.py
│   │   └── styles.py
│   └── utils/
│       ├── __init__.py
│       ├── export.py
│       ├── logger.py
│       └── constants.py
│
├── app/
│   ├── main.py
│   ├── config.py
│   ├── pages/
│   │   ├── 1_Inicio.py
│   │   ├── 2_Diseñador.py
│   │   ├── 3_Resultados.py
│   │   └── 4_Documentacion.py
│   └── components/
│       ├── input_form.py
│       ├── results_display.py
│       └── sidebar.py
│
├── tests/
│   ├── __init__.py
│   ├── test_transfer_function.py
│   ├── test_ziegler_nichols.py
│   ├── test_cohen_coon.py
│   ├── test_simulator.py
│   ├── test_metrics.py
│   ├── test_export.py
│   └── fixtures/
│       └── test_systems.json
│
└── docs/
    ├── ESPECIFICACION.md
    ├── ARQUITECTURA_MODULOS.md
    ├── FLUJO_USUARIO.md
    ├── PLAN_IMPLEMENTACION.md
    ├── MANUAL_USUARIO.md
    ├── TEORÍA.md
    ├── API_BACKEND.md
    └── EJEMPLOS.md
```

**Nota:** Los archivos con `[AGREGAR]` deben crearse pero no están detallados en este documento.

---

## 🚀 Cómo Empezar (Día 1)

### Paso 1: Setup Inicial
```bash
# Crea carpeta del proyecto
mkdir pid-tuner && cd pid-tuner

# Crea virtual environment
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Crea estructura básica de carpetas
mkdir -p src/{core,tuning,simulation,visualization,utils}
mkdir -p app/{pages,components}
mkdir -p tests/fixtures
mkdir -p docs
```

### Paso 2: Crea Archivos Iniciales
```bash
# Archivos raíz
touch README.md requirements.txt setup.py .gitignore

# Archivos __init__.py
touch src/__init__.py
touch src/core/__init__.py
touch src/tuning/__init__.py
touch src/simulation/__init__.py
touch src/visualization/__init__.py
touch src/utils/__init__.py
touch app/__init__.py
touch tests/__init__.py
```

### Paso 3: Agrega requirements.txt
```text
# requirements.txt
python-control>=0.9.0
numpy>=1.21.0
scipy>=1.7.0
plotly>=5.0.0
matplotlib>=3.5.0
streamlit>=1.2.0
pandas>=1.3.0
pillow>=8.0.0
pytest>=7.0.0
pytest-cov>=3.0.0
```

### Paso 4: Instala Dependencias
```bash
pip install -r requirements.txt
```

### Paso 5: Primera Clase (TransferFunction)
Crea `src/core/transfer_function.py`:

```python
"""
Módulo para manipulación de funciones de transferencia.
"""
import numpy as np
from typing import List, Tuple

class TransferFunction:
    """
    Representa una función de transferencia lineal.
    
    G(s) = N(s) / D(s) donde N(s) y D(s) son polinomios.
    """
    
    def __init__(self, numerador: List[float], denominador: List[float]):
        """
        Inicializa una función de transferencia.
        
        Args:
            numerador: Coeficientes del numerador [an, an-1, ..., a0]
            denominador: Coeficientes del denominador [bm, bm-1, ..., b0]
        
        Raises:
            ValueError: Si los coeficientes son inválidos
        """
        self.num = np.array(numerador, dtype=float)
        self.den = np.array(denominador, dtype=float)
        
        if len(self.num) == 0 or len(self.den) == 0:
            raise ValueError("Numerador y denominador no pueden estar vacíos")
        
        if np.all(self.den == 0):
            raise ValueError("Denominador no puede ser todo ceros")
    
    @property
    def order(self) -> Tuple[int, int]:
        """Retorna (orden_numerador, orden_denominador)"""
        return len(self.num) - 1, len(self.den) - 1
    
    def evaluate(self, s: complex) -> complex:
        """
        Evalúa G(s) en un punto del plano complejo.
        
        Args:
            s: Valor complejo donde evaluar
        
        Returns:
            G(s) = P(s) / Q(s)
        """
        return np.polyval(self.num, s) / np.polyval(self.den, s)
    
    def get_poles(self) -> np.ndarray:
        """Retorna los polos de G(s)"""
        return np.roots(self.den)
    
    def get_zeros(self) -> np.ndarray:
        """Retorna los ceros de G(s)"""
        return np.roots(self.num)
    
    def is_stable(self) -> bool:
        """
        Verifica si el sistema es estable.
        
        Un sistema es BIBO estable si todos los polos están
        en el semiplano izquierdo (Re < 0).
        
        Returns:
            True si estable, False en caso contrario
        """
        poles = self.get_poles()
        return np.all(np.real(poles) < 0)
    
    def __str__(self) -> str:
        """Representación en string de la función de transferencia"""
        num_str = f"({'+'.join(f'{c:.3f}' for c in self.num)})"
        den_str = f"({'+'.join(f'{c:.3f}' for c in self.den)})"
        return f"G(s) = {num_str} / {den_str}"
```

### Paso 6: Prueba Básica
Crea `tests/test_transfer_function.py`:

```python
"""Tests para TransferFunction"""
import pytest
from src.core.transfer_function import TransferFunction

def test_transfer_function_creation():
    """Test creación básica"""
    tf = TransferFunction([1], [1, 1])
    assert tf.order == (0, 1)

def test_first_order_stable():
    """Test sistema de 1er orden estable"""
    tf = TransferFunction([1], [1, 1])  # 1/(s+1)
    assert tf.is_stable()

def test_first_order_unstable():
    """Test sistema de 1er orden inestable"""
    tf = TransferFunction([1], [1, -1])  # 1/(s-1)
    assert not tf.is_stable()

def test_evaluate():
    """Test evaluación de G(s)"""
    tf = TransferFunction([1], [1, 1])
    g_at_0 = tf.evaluate(0)
    assert abs(g_at_0 - 1.0) < 1e-6

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

### Paso 7: Ejecuta Tests
```bash
pytest tests/test_transfer_function.py -v
```

---

## 📝 Checklist Semana 1

- [ ] Estructura de directorios creada
- [ ] `requirements.txt` instalado
- [ ] `src/core/transfer_function.py` implementado
- [ ] `src/core/validation.py` implementado
- [ ] Tests para Core (cobertura >90%)
- [ ] README básico con instrucciones
- [ ] Primer commit a GitHub

---

## 🔍 Puntos Clave de Diseño

### 1. **Validación en Capas**
```
Usuario Input
    ↓
Frontend Streamlit (validación básica)
    ↓
Backend validation.py (validación rigurosa)
    ↓
Cada módulo (validación específica)
```

### 2. **Manejo de Errores**
- Crear `src/core/exceptions.py` con excepciones personalizadas
- Cada módulo maneja sus errores y levanta excepciones claras
- Streamlit las captura y muestra al usuario

### 3. **Session State en Streamlit**
```python
# Guardar persistencia entre páginas
if 'tf_num' not in st.session_state:
    st.session_state['tf_num'] = None

# Usar en componentes
st.session_state['tf_num'] = input_value
```

### 4. **Tests Antes de Fronend**
- Implementar backend 100% testeable
- Que sea independiente de Streamlit
- Luego integrar en la UI

---

## 🎓 Puntos de Aprendizaje para el Portafolio

1. **Control Automático:** Implementación de métodos clásicos
2. **Ingeniería de Software:** Arquitectura modular, tests, documentación
3. **Python Avanzado:** Type hints, excepciones, design patterns
4. **Full-Stack:** Backend + Frontend con Streamlit
5. **Git/GitHub:** Versionamiento, commits significativos, README profesional

---

## 📞 Preguntas Frecuentes

**P: ¿Qué versión de Python usar?**  
R: 3.9+ recomendado. Mínimo 3.8

**P: ¿Dónde comienza la implementación?**  
R: Con `src/core/transfer_function.py` (Fase 1)

**P: ¿Pruebo mientras desarrollo?**  
R: Sí, escribe tests mientras implementas (TDD)

**P: ¿Cómo hago los gráficos interactivos?**  
R: Usa `plotly` en `visualization/plotter.py`, Streamlit los visualiza automáticamente

**P: ¿Se puede exportar a código MATLAB?**  
R: Eso está en "Could Have" (futuro), no en v1.0

---

## 🎁 Bonus: Ejemplo Completo Ziegler–Nichols

Pseudocódigo para la implementación de sintonización:

```python
class ZieglerNichols(BaseTuner):
    """
    Parámetros finales usando método de la curva de reacción:
    
    1. Aplicar escalón unitario a sistema sin control
    2. Extraer L (retardo), T (constante de tiempo), K (ganancia DC)
    3. Calcular:
       Kp = 1.2 * T / (L * K)
       Ti = 2 * L
       Td = 0.5 * L
    """
    
    def _extract_curve_params(self) -> Tuple[float, float, float]:
        """Extrae L, T, K de respuesta escalón"""
        # Simular respuesta open-loop
        time, response = self.tf.step_response(t_max=100)
        
        # L: tiempo en que comienza a cambiar la respuesta
        # T: diferencia entre tiempo de establecimiento y L
        # K: valor final (ganancia DC)
        
        L = time[np.where(response > 0.01 * response[-1])[0][0]]
        K = response[-1]
        T = (time[np.where(response > 0.63 * K)[0][0]] - L)
        
        return L, T, K
    
    def tune(self) -> Tuple[float, float, float]:
        L, T, K = self._extract_curve_params()
        
        Kp = 1.2 * T / (L * K) if L != 0 else 0
        Ti = 2 * L
        Td = 0.5 * L
        
        return Kp, Ti, Td
```

---

## 📚 Referencias Externas

- **python-control:** https://python-control.readthedocs.io/
- **Streamlit:** https://docs.streamlit.io/
- **Control Automático:** Ogata "Modern Control Engineering"
- **GitHub Best Practices:** https://github.com/google/styleguide

---

**¡A programar!**  
Comienza con Fase 1 mañana. Suerte con tu portafolio. 🚀

