# Guía de Implementación: De la Teoría a la API

## Introducción

Este documento conecta la **teoría de control** (TEORIA_CONTROL.md) con la **API del backend** (API_BACKEND.py).

Muestra cómo cada función de la API corresponde a un concepto teórico y cómo implementarlas siguiendo la teoría.

---

## 1. Mapeo: Teoría ↔ API ↔ Código

### Concepto 1: Función de Transferencia

**Teoría:**
- Representa el sistema: $G(s) = \frac{N(s)}{D(s)}$
- Se expresa en forma de coeficientes polinomiales
- Ejemplo: $G(s) = \frac{s+2}{s^2+3s+2}$ → numerador=[1,2], denominador=[1,3,2]

**API:**
```python
tf = create_transfer_function(
    numerator=[1, 2],
    denominator=[1, 3, 2]
)
```

**Implementación (Fase 1):**
```python
# src/core/transfer_function.py

class TransferFunction:
    def __init__(self, numerator: List[float], denominator: List[float]):
        # Validar
        if not numerator or not denominator:
            raise ValueError("Polinomios no pueden estar vacíos")
        if np.all(np.array(denominator) == 0):
            raise ValueError("Denominador no puede ser todo ceros")
        
        # Convertir a numpy arrays
        self.num = np.array(numerator, dtype=float)
        self.den = np.array(denominator, dtype=float)
        
        # Usar scipy.signal.TransferFunction para cálculos internos
        self._tf_scipy = scipy.signal.TransferFunction(self.num, self.den)
    
    def get_poles(self) -> np.ndarray:
        """Retorna raíces del denominador"""
        return np.roots(self.den)
    
    def get_zeros(self) -> np.ndarray:
        """Retorna raíces del numerador"""
        return np.roots(self.num)
    
    def is_stable(self) -> bool:
        """Todos los polos en semiplano izquierdo?"""
        poles = self.get_poles()
        return np.all(np.real(poles) < 0)
```

---

### Concepto 2: Modelo FOPDT

**Teoría:**
- $G(s) = \frac{K}{Ts+1} e^{-Ls}$
- Parametrizado por: K (ganancia), L (retardo), T (constante de tiempo)
- Se obtiene de la respuesta al escalón del sistema
- Método de identificación: extraer L, T, K de la curva (L = retardo, T = 63.2%)

**API:**
```python
# Opción 1: Desde respuesta al escalón medida
model = approximate_to_fopdt_from_step_response(
    time=time_data,
    response=y_data,
    reference=1.0
)

# Opción 2: Desde función de transferencia
model = approximate_to_fopdt_from_transfer_function(tf)
```

**Implementación (Fase 2):**
```python
# src/tuning/tuning_utils.py

def approximate_to_fopdt_from_step_response(time, response, reference=1.0):
    """
    Extrae K, L, T de la respuesta al escalón.
    
    Teoría:
    1. K = valor final / magn. entrada = response[-1]
    2. L = tiempo en que empieza a cambiar (cuando sale de ±2%)
    3. T = tiempo para llegar a 63.2% del cambio desde L
    """
    # Normalizar respuesta
    steady_state = response[-1]
    K = steady_state / reference
    
    # Encontrar retardo L (primer cambio > 1% del total)
    change_threshold = 0.01 * (steady_state - response[0])
    indices_above_threshold = np.where(
        np.abs(response - response[0]) > np.abs(change_threshold)
    )[0]
    
    if len(indices_above_threshold) == 0:
        L = 0
    else:
        L = time[indices_above_threshold[0]]
    
    # Encontrar punto 63.2% del cambio
    target_63 = response[0] + 0.632 * (steady_state - response[0])
    idx_63 = np.argmin(np.abs(response - target_63))
    
    # T = tiempo desde L hasta 63% menos el retardo
    T = time[idx_63] - L
    if T <= 0:
        T = 0.001  # Mínimo
    
    return FOPDTModel(K=K, L=L, T=T)
```

---

### Concepto 3: Sintonización Ziegler–Nichols

**Teoría:**
- Fórmulas directas del modelo FOPDT:
  - $K_p = \frac{1.2T}{LK}$
  - $T_i = 2L$
  - $T_d = 0.5L$

**API:**
```python
pid_params = tune_pid_ziegler_nichols(
    fopdt_model=model,
    method="step_response",
    control_type="PID"
)
```

**Implementación (Fase 3):**
```python
# src/tuning/ziegler_nichols.py

class ZieglerNichols(BaseTuner):
    def tune(self) -> PIDParameters:
        """Implementar fórmulas directas"""
        K, L, T = self.fopdt_model.K, self.fopdt_model.L, self.fopdt_model.T
        
        # Validar parámetros
        if L == 0:
            raise TuningError("Retardo L no puede ser cero en ZN")
        if K <= 0 or T <= 0:
            raise TuningError("K y T deben ser positivos")
        
        # Fórmulas ZN para control PID
        Kp = 1.2 * T / (L * K)
        Ti = 2.0 * L
        Td = 0.5 * L
        
        return PIDParameters(Kp=Kp, Ti=Ti, Td=Td, method="ZN")
```

---

### Concepto 4: Simulación del Sistema

**Teoría:**
- Sistema lineal: $\dot{x} = Ax + Bu$, $y = Cx + Du$
- Para FOPDT: derivar ecuación diferencial equivalente
- Resolver numéricamente usando integrador (RK4, Dopri, etc.)

**API:**
```python
# Lazo abierto (sin control)
result_ol = simulate_open_loop(tf, reference=1.0, t_final=50.0)

# Lazo cerrado (con PID)
result_cl = simulate_closed_loop_with_pid(tf, pid_params, reference=1.0)

# O ambas juntas
result_ol, result_cl = simulate_comparison(tf, pid_params)
```

**Implementación (Fase 4):**
```python
# src/simulation/simulator.py

class SimulationEngine:
    def __init__(self, tf, dt=0.01, t_max=50):
        self.tf = tf
        self.dt = dt
        self.t_max = t_max
        
        # Convertir función de transferencia a representación en espacio de estados
        # G(s) → (A, B, C, D)
        self.A, self.B, self.C, self.D = self._tf_to_ss()
    
    def open_loop(self, reference=1.0):
        """Simular lazo abierto: u(t) = reference × escalón"""
        def model(x, t):
            """dx/dt = Ax + B*u"""
            u = reference  # Entrada constante
            dxdt = self.A @ x + self.B * u
            return dxdt
        
        # Integrar ODE
        t_eval = np.arange(0, self.t_max, self.dt)
        x0 = np.zeros(self.A.shape[0])  # Condición inicial
        x_tray = odeint(model, x0, t_eval)
        
        # Salida
        y = (self.C @ x_tray.T + self.D * reference).flatten()
        
        return SimulationResult(
            time=t_eval,
            output=y,
            reference=np.full_like(t_eval, reference)
        )
    
    def closed_loop(self, controller, reference=1.0):
        """Simular lazo cerrado con PID"""
        pid = PIDController(
            Kp=controller.Kp,
            Ti=controller.Ti,
            Td=controller.Td,
            dt=self.dt
        )
        
        t_eval = np.arange(0, self.t_max, self.dt)
        x = np.zeros(self.A.shape[0])
        y_list = []
        u_list = []
        
        for t_k in t_eval:
            # Salida actual
            y_k = (self.C @ x + self.D * 0).item()
            y_list.append(y_k)
            
            # Error
            error = reference - y_k
            
            # Acción de control
            u_k = pid.update(error)
            u_list.append(u_k)
            
            # Actualizar estado: x(k+1) = x(k) + dt*(Ax + Bu)
            x = x + self.dt * (self.A @ x + self.B * u_k)
        
        return SimulationResult(
            time=t_eval,
            output=np.array(y_list),
            control_signal=np.array(u_list),
            reference=np.full_like(t_eval, reference)
        )
```

---

### Concepto 5: Métricas de Desempeño

**Teoría:**
- **Settling time (ts):** Tiempo para entrar en banda ±5% del valor final
- **Overshoot (Mp):** $M_p = \frac{y_{max} - y_\infty}{y_\infty} \times 100\%$
- **Error en estado estacionario (ess):** $e_{ss} = |r - y(\infty)|$
- **Rise time (tr):** Tiempo de 10% a 90% del salto

**API:**
```python
metrics = calculate_performance_metrics(
    time=result.time,
    response=result.output,
    reference=1.0,
    tolerance=0.05
)

# Comparar
metrics_ol, metrics_cl = calculate_metrics_for_comparison(
    time_ol, y_ol, time_cl, y_cl
)
```

**Implementación (Fase 5):**
```python
# src/simulation/metrics.py

class PerformanceMetrics:
    @staticmethod
    def settling_time(time, response, reference=1.0, tolerance=0.05):
        """
        Tiempo para entrar en ±tolerance del valor final.
        
        Teoría: ts = min(t) tal que |y(t) - ref| < tolerance × ref
        """
        band_lower = reference * (1 - tolerance)
        band_upper = reference * (1 + tolerance)
        
        # Encontrar primer tiempo donde entra en la banda
        inside_band = (response >= band_lower) & (response <= band_upper)
        
        # Buscar desde el final hacia atrás para evitar transitorios iniciales
        idx = np.where(inside_band)[0]
        if len(idx) > 0:
            # Verificar que se mantiene en la banda
            idx_settled = np.where(
                np.all(inside_band[idx[0]:], axis=0)
            )[0]
            if len(idx_settled) > 0:
                return time[idx[0]]
        
        return time[-1]  # No se estabiliza dentro del horizonte
    
    @staticmethod
    def overshoot(response, reference=1.0):
        """
        Sobreimpulso máximo en porcentaje.
        
        Teoría: Mp = (max(y) - ref) / ref × 100%
        """
        y_max = np.max(response)
        Mp = (y_max - reference) / reference * 100
        return max(0, Mp)  # No negativos
    
    @staticmethod
    def steady_state_error(response, reference=1.0):
        """
        Error final en estado estacionario (3 últimas muestras).
        """
        y_ss = np.mean(response[-3:])  # Promedio últimas 3 muestras
        ess = np.abs(reference - y_ss)
        return ess
    
    @staticmethod
    def rise_time(time, response, reference=1.0):
        """
        Tiempo de 10% a 90% del valor final.
        """
        y_max = np.max(response)
        y_10 = response[0] + 0.10 * (y_max - response[0])
        y_90 = response[0] + 0.90 * (y_max - response[0])
        
        # Encontrar tiempos
        idx_10 = np.argmin(np.abs(response - y_10))
        idx_90 = np.argmin(np.abs(response - y_90))
        
        tr = time[idx_90] - time[idx_10]
        return tr
```

---

## 2. Flujo Completo: Paso a Paso

### Ejemplo Práctico: Proceso FOPDT de Calentamiento

**Objetivo:** Diseñar PID para un sistema de calentamiento con K=2.0, L=2.0, T=10.0

```python
# PASO 1: Crear modelo FOPDT
model = FOPDTModel(K=2.0, L=2.0, T=10.0)

# PASO 2: Sintonizar - Método Ziegler-Nichols
pid_zn = tune_pid_ziegler_nichols(model, method="step_response", control_type="PID")
print(f"ZN: Kp={pid_zn.Kp:.3f}, Ti={pid_zn.Ti:.3f}, Td={pid_zn.Td:.3f}")
# Esperado: Kp=6.0, Ti=4.0, Td=1.0

# PASO 3: Sintonizar - Método Cohen-Coon
pid_cc = tune_pid_cohen_coon(model, criterion="IAE", control_type="PID")
print(f"CC: Kp={pid_cc.Kp:.3f}, Ti={pid_cc.Ti:.3f}, Td={pid_cc.Td:.3f}")
# Esperado: Kp=6.75, Ti=5.0, Td=0.74

# PASO 4: Crear función de transferencia FOPDT
# G(s) = 2.0 / (10s + 1) × e^(-2s)
# Aproximar sin el retardo para simplificar: G(s) = 2.0 / (10s + 1)
tf_fopdt = create_transfer_function(numerator=[2.0], denominator=[10.0, 1.0])

# PASO 5: Simular ambos métodos
result_zn_ol, result_zn_cl = simulate_comparison(tf_fopdt, pid_zn)
result_cc_ol, result_cc_cl = simulate_comparison(tf_fopdt, pid_cc)

# PASO 6: Calcular métricas
metrics_zn = calculate_performance_metrics(
    result_zn_cl.time, result_zn_cl.output, reference=2.0
)
metrics_cc = calculate_performance_metrics(
    result_cc_cl.time, result_cc_cl.output, reference=2.0
)

# PASO 7: Comparar resultados
print("\n=== COMPARACIÓN ZN vs CC ===")
print(f"\nZiegler-Nichols:")
print(f"  ts = {metrics_zn.settling_time:.2f} seg")
print(f"  Mp = {metrics_zn.overshoot:.2f} %")
print(f"  ess = {metrics_zn.steady_state_error:.6f}")

print(f"\nCohen-Coon:")
print(f"  ts = {metrics_cc.settling_time:.2f} seg")
print(f"  Mp = {metrics_cc.overshoot:.2f} %")
print(f"  ess = {metrics_cc.steady_state_error:.6f}")
```

---

## 3. Tablas de Referencia Rápida

### API por Etapa de Diseño

| Etapa | Función | Propósito |
|-------|---------|-----------|
| **Entrada** | `create_transfer_function()` | Ingresar G(s) |
| **Validación** | `is_transfer_function_stable()` | Verificar estabilidad |
| **Identificación** | `approximate_to_fopdt_from_*()` | Obtener K, L, T |
| **Sintonización** | `tune_pid_ziegler_nichols()` <br> `tune_pid_cohen_coon()` | Calcular Kp, Ti, Td |
| **Validación** | `validate_pid_parameters()` | Verificar parámetros |
| **Simulación** | `simulate_open_loop()` <br> `simulate_closed_loop_with_pid()` | Probar desempeño |
| **Análisis** | `calculate_performance_metrics()` | Calcular ts, Mp, ess, tr |
| **Exportación** | `export_results_to_csv()` <br> `export_figure_to_png()` | Guardar resultados |

### Fórmulas Resumidas

**Ziegler–Nichols (FOPDT):**
$$K_p = \frac{1.2T}{LK}, \quad T_i = 2L, \quad T_d = 0.5L$$

**Cohen–Coon (FOPDT, L/T < 0.3):**
$$K_p = \frac{1.35T}{LK}, \quad T_i = 2.5L, \quad T_d = 0.37L$$

---

## 4. Validaciones Críticas en Código

```python
# Validación 1: Parámetros FOPDT válidos
def validate_fopdt(K, L, T):
    assert K > 0, "K debe ser positivo"
    assert L >= 0, "L no puede ser negativo"
    assert T > 0, "T debe ser positivo"
    assert L / T < 1.0, "L/T debe ser < 1"

# Validación 2: Parámetros PID válidos
def validate_pid(Kp, Ti, Td):
    assert Kp > 0, "Kp debe ser positivo"
    assert Ti > 0, "Ti debe ser positivo"
    assert Td >= 0, "Td no puede ser negativo"
    assert Ti > 4 * Td, "Relación Ti/Td inusual"

# Validación 3: Simulación convergió
def validate_simulation(response, reference):
    ess = np.abs(response[-1] - reference)
    assert ess < 0.1 * reference, "Sistema no se estabiliza"
```

---

## 5. Estructura de Carpetas para Implementación

```
src/
├── core/
│   ├── transfer_function.py      # → Concepto 1
│   └── validation.py              # Validaciones
│
├── tuning/
│   ├── tuning_utils.py            # → Concepto 2
│   ├── ziegler_nichols.py         # → Concepto 3
│   └── cohen_coon.py              # → Concepto 3
│
└── simulation/
    ├── controller.py              # Controlador PID
    ├── simulator.py               # → Concepto 4
    └── metrics.py                 # → Concepto 5
```

---

## 6. Estimación de Líneas de Código por Módulo

| Módulo | Funciones | LOC Estimado | Tests |
|--------|-----------|--------------|-------|
| transfer_function.py | 4 | 100-150 | 20+ |
| tuning_utils.py | 1 | 80-100 | 10+ |
| ziegler_nichols.py | 3 | 100-150 | 15+ |
| cohen_coon.py | 3 | 120-150 | 15+ |
| controller.py | 2 | 60-80 | 8+ |
| simulator.py | 3 | 150-200 | 20+ |
| metrics.py | 5 | 120-150 | 25+ |
| **TOTAL** | **21** | **730-980** | **113+** |

---

## 7. Checklist de Implementación

### Semana 1 (Core)
- [ ] `src/core/transfer_function.py` implementado
- [ ] Pruebas de TransferFunction (polos, ceros, estabilidad)
- [ ] Validaciones robustas

### Semana 2 (Identificación + Sintonización)
- [ ] `approximate_to_fopdt_*()` funcionando
- [ ] Teste con ejemplos teóricos conocidos
- [ ] `ZieglerNichols` y `CohenCoon` implementados
- [ ] Validación cruzada contra MATLAB/WolframAlpha

### Semana 3 (Simulación + Métricas)
- [ ] Controlador PID discreto implementado
- [ ] Solver ODE funcionando para ambos escenarios
- [ ] Métricas calculadas correctamente

### Semana 4+
- [ ] Integración total
- [ ] Tests exhaustivos (80%+ cobertura)
- [ ] Ejemplo completo funcionando

---

## 8. Referencias para Verificación

### Ejemplo 1: Verifica transición de teoría a código

**Teoría:** Para G(s) = 1/(s+1), la respuesta al escalón es:
$$y(t) = 1 - e^{-t}$$

**Código que debe producir esto:**
```python
tf = create_transfer_function([1], [1, 1])
result = simulate_open_loop(tf, reference=1.0, t_final=5.0, dt=0.01)

# Verificar
t_test = 3.0
y_expected = 1 - np.exp(-t_test)
idx = np.argmin(np.abs(result.time - t_test))
y_actual = result.output[idx]

assert np.isclose(y_actual, y_expected, atol=0.01), \
    f"Expected {y_expected}, got {y_actual}"
print("✓ Simulación verificada contra teoría")
```

### Ejemplo 2: Verifica fórmulas de sintonización

**Teórico:** Para FOPDT(K=1, L=1, T=5):
- ZN: Kp = 1.2×5/(1×1) = 6.0

**Código:**
```python
model = FOPDTModel(K=1.0, L=1.0, T=5.0)
pid = tune_pid_ziegler_nichols(model)

assert np.isclose(pid.Kp, 6.0, rtol=0.01), "ZN Kp incorrecta"
print("✓ Fórmulas de sintonización verificadas")
```

---

## 6. Cálculo de Métricas de Desempeño

### Etapa 6: Métricas de Respuesta

**Teoría:**
Las métricas evaluán qué tan bueno es el desempeño:

1. **Tiempo de establecimiento (ts)** - ¿Qué tan rápido converge?
   - Definición: Último tiempo donde |y(t) - yref| > tolerancia × |yref|
   - Para sistemas de 2do orden: $t_s \approx \frac{-5}{\zeta \omega_n}$ (2% tolerance)
   - Interpretación: ts bajo = rápida convergencia

2. **Sobreimpulso (Mp %)** - ¿Cuánto se pasa de la referencia?
   - Definición: $M_p = \frac{\max(y) - y_{ref}}{|y_{ref}|} \times 100$
   - Para 2do orden: $M_p = e^{-\pi\zeta/\sqrt{1-\zeta^2}} \times 100$
   - Interpretación: ZN → 20-25%, Cohen-Coon → 10-15%, Crítico → 0-5%

3. **Error estacionario (ess)** - ¿Queda error en régimen permanente?
   - Definición: $e_{ss} = y_{ref} - y(t_{final})$
   - Controladores P: ess > 0
   - Controladores PI/PID: ess ≈ 0

**API:**
```python
# src/simulation/metrics.py
metricas = calcular_metricas_respuesta(
    t=time_vector,      # Vector de tiempo
    y=response_vector,  # Respuesta simulada
    yref=1.0,          # Referencia
    tolerance=0.02     # Banda ±2%
)

# Retorna:
# {
#   "ts": 18.7,              # Tiempo establecimiento [seg]
#   "Mp": 15.3,              # Sobreimpulso [%]
#   "ess": 0.0023,           # Error estacionario
#   "ess_percent": 0.23,     # Error relativo [%]
#   "y_max": 1.153,          # Valor máximo
#   "y_final": 1.0023        # Valor final
# }
```

**Implementación:**
```python
# Validar entrada y calcular métricas
y_final = y[-1]
y_max = np.max(y)
ess = yref - y_final
Mp = (y_max - yref) / np.abs(yref) * 100.0

# Encontrar ts: último índice fuera de banda de tolerancia
settling_band = tolerance * np.abs(yref)
error = np.abs(y - yref)
within_band = error <= settling_band
indices_out = np.where(~within_band)[0]

if len(indices_out) > 0:
    last_out = indices_out[-1]
    ts = t[last_out + 1] if last_out + 1 < len(t) else t[-1]
else:
    ts = t[-1]
```

**Ejemplo numérico:**
```
Sistema subamortiguado (ZN-like):
  ts = 28.62 seg    (tiempo establecimiento)
  Mp = 52.7 %       (sobreimpulso)
  ess = -0.0178     (error estacionario)

Sistema sobreamortiguado:
  ts = 3.92 seg
  Mp = 0.0 %        (sin overshoot)
  ess = 0.00005
```

---

## 7. Generación de Gráficos Comparativos

### Etapa 7: Visualización de Respuestas

**Teoría:**
La visualización permite evaluar cualitativamente:
- ¿Cuál método converge más rápido?
- ¿Cuál tiene menor overshoot?
- ¿Dónde está la banda de tolerancia ±2%?

**API:**
```python
# src/visualization/plotter.py

fig = graficar_respuestas(
    t_planta=t_lazo_abierto,      # Tiempo sin control
    y_planta=y_lazo_abierto,      # Respuesta sin control
    t_pid=t_lazo_cerrado,         # Tiempo con PID
    y_pid=y_lazo_cerrado,         # Respuesta con PID
    yref=1.0,                     # Referencia
    title="Compración: Lazo Abierto vs Lazo Cerrado",
    tolerance=0.02,               # Banda ±2%
    show_band=True                # Mostrar banda
)

# Usar en Streamlit:
st.pyplot(fig)

# O guardar en archivo:
fig.savefig('resultado.png', dpi=300)
```

**Implementación simplificada:**
```python
fig, ax = plt.subplots(figsize=(12, 6))

# Banda de tolerancia
if show_band:
    band_upper = yref + tolerance * np.abs(yref)
    band_lower = yref - tolerance * np.abs(yref)
    ax.fill_between([0, t_max], band_lower, band_upper,
                   alpha=0.2, color='gray')

# Curvas
ax.plot(t_planta, y_planta, 'b-', linewidth=2.5, label='Lazo abierto')
ax.plot(t_pid, y_pid, 'r-', linewidth=2.5, label='Con PID')
ax.axhline(y=yref, color='k', linestyle='--', linewidth=2)

# Formato
ax.set_xlabel('Tiempo [seg]', fontsize=12, fontweight='bold')
ax.set_ylabel('Salida [unidades]', fontsize=12, fontweight='bold')
ax.grid(True, alpha=0.3)
ax.legend(fontsize=11)
```

**Funciones adicionales:**
```python
# Gráfico individual
fig = graficar_respuesta_individual(t, y, yref=1.0)

# Comparación de múltiples métodos
fig = graficar_comparacion_metodos({
    "ZN": (t1, y_zn),
    "CC": (t1, y_cc),
    "Crítico": (t1, y_critico)
})
```

**Gráficos generados:**
```
✓ comparacion_basica.png     - Planta vs PID (banda ±2%)
✓ comparacion_50C.png        - Control de temperatura a 50°C
✓ comparacion_metodos.png    - ZN vs Cohen-Coon vs Crítico
✓ individual.png             - Respuesta individual

Todos son PNG alta resolución (DPI=150) listos para:
- Presentaciones en Powerpoint
- Reportes en PDF
- Aplicaciones Streamlit
- Publicaciones técnicas
```

---

**Fin de la Guía de Implementación**

Este documento es tu mapa para ir de la teoría al código. Síguelo fase a fase.

