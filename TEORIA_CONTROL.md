# Teoría de Control: PID, Ziegler–Nichols y Cohen–Coon

## 1. ¿Qué es un Controlador PID?

### Concepto General

Un **controlador PID** (Proporcional–Integral–Derivativo) es un dispositivo que ajusta una acción de control basándose en el **error** (diferencia entre el valor deseado y el actual) para llevar el sistema hacia la referencia.

```
ENTRADA (Referencia r)
        │
        ├───[+]────┐
        │          │
        │      ┌───▼────┐
        │      │ ERROR  │  e(t) = r(t) - y(t)
        │      └───┬────┘
        │          │
        │      ┌───▼──────────────────────┐
        │      │   CONTROLADOR PID        │
        │      │                          │
        │      │  u(t) = Kp·e(t)          │
        │      │        + Ki·∫e(t)dt      │
        │      │        + Kd·de(t)/dt     │
        │      └───┬──────────────────────┘
        │          │
                   u(t) (Acción de control)
        │          │
        │      ┌───▼──────┐
        │      │ PROCESO  │
        │      │  G(s)    │
        │      └───┬──────┘
        │          │
        └──────┬───┘  y(t) (Salida medida)
               │
          [Retroalimentación]
```

### La Ecuación del PID

En **tiempo continuo**:

$$u(t) = K_p \cdot e(t) + K_i \int_0^t e(\tau) d\tau + K_d \frac{de(t)}{dt}$$

O equivalentemente, con constantes de tiempo:

$$u(t) = K_p \left( e(t) + \frac{1}{T_i} \int_0^t e(\tau) d\tau + T_d \frac{de(t)}{dt} \right)$$

En **tiempo discreto** (para implementación digital):

$$u[k] = K_p \cdot e[k] + K_i \sum_{j=0}^{k} e[j] + K_d (e[k] - e[k-1])$$

---

## 2. Significado de los Parámetros: Kp, Ti, Td

| Parámetro | Nombre | Función | Efecto en el Sistema |
|-----------|--------|---------|----------------------|
| **Kp** | Ganancia Proporcional | Reacciona al error actual | ↑ Kp: Respuesta más rápida, pero puede oscilar |
| **Ti** | Tiempo Integral (segundos) | Eliminador de error en estado estacionario | ↑ Ti: Mejor rechazo a perturbaciones, pero más lento |
| **Td** | Tiempo Derivativo (segundos) | Amortigua las oscilaciones | ↑ Td: Mayor amortiguamiento, reduce overshoot |

### Analogía Intuitiva

Imagina conducir un auto que debe mantener velocidad constante:

- **Kp (Proporcional):** Si vas lento, pisas el acelerador proporcional a cuánto lento vas
- **Ti (Integral):** Si constantemente te encuentras lento, aumentas la presión del acelerador más y más
- **Td (Derivativo):** Si dedices frenar, reducimos aceleración para evitar pasarte del objetivo

### Rango Recomendado

```
Kp: 0.1 a 100 (depende de ganancia DC del proceso)
Ti: 0.01 a 100 segundos
Td: 0.001 a 10 segundos

Relación típica: Kp >> Ki >> Kd (en términos de aporte a la acción)
```

---

## 3. FOPDT: Modelo de Primer Orden + Retardo

### ¿Qué es FOPDT?

**FOPDT** = **First Order Plus Dead Time**

Es el modelo más usado en procesos industriales. Captura:
- Un **retardo puro** (L): Tiempo muerto del proceso
- Una **dinámica de 1er orden** (T): Constante de tiempo
- Una **ganancia DC** (K): Valor final normalizado

### Función de Transferencia FOPDT

$$G(s) = \frac{K}{Ts + 1} e^{-Ls}$$

Donde:

| Parámetro | Símbolo | Significado | Unidad | Rango Típico |
|-----------|---------|------------|--------|--------------|
| **Ganancia DC** | K | Cambio en salida por cambio unitario en entrada | adimensional o °C/% | 0.5 - 5 |
| **Retardo de Transporte** | L | Tiempo muerto del proceso (tuberías, sensores) | segundos | 0.1 - 10 |
| **Constante de Tiempo** | T | Velocidad de respuesta de la dinámica | segundos | 1 - 100 |

### Interpretación Física

```
Entrada (escalón)
      │
      │  ┌─────────────────── Valor final = K
      │  │
 1 ┤  └──┼─────────┐
      │  │ retardo │  dinámica
      │  L         T
      │  ──────────┴─────────
      │
      └─────────────────────── tiempo
      0  L         L+T
```

**Ejemplo real:** Calentador de agua
- **K = 2:** Por cada 1% de aumento en potencia → 2°C más en estado estacionario
- **L = 5 seg:** Demora 5 segundos para que el calor llegue al sensor
- **T = 20 seg:** Una vez llegue el calor, tarda 20 seg más para estabilizarse

---

## 4. Métodos de Sintonización: Ziegler–Nichols y Cohen–Coon

### 4.1 Ziegler–Nichols (ZN) - Método de la Curva de Reacción

Es el **método más clásico** y usado en industria por su simplicidad.

#### Pasos del Método

**Paso 1:** Aplicar escalón unitario al sistema sin controlador

```
Entrada: escalón
    │
  1 ┤       ┐
    │       │ ┌────────────────→ y(t)
    │       └─┘
    │  L    T
    └────────────────────── t
```

**Paso 2:** Extraer 3 parámetros de la respuesta

```
Procedimiento:
1. L = tiempo en que la curva comienza a cambiar (retardo)
2. T = tiempo desde L hasta estabilización (constante de tiempo aparente)
   - En rigor: T = (t₆₃% - L) donde 63% = 1 - 1/e
3. K = valor final de la respuesta (ganancia DC)
```

#### Fórmulas de Sintonía ZN

**Para control PID:**

$$K_p = \frac{1.2T}{LK}$$

$$T_i = 2L$$

$$T_d = 0.5L$$

**Para control PI (sin derivativo):**

$$K_p = \frac{0.9T}{LK}$$

$$T_i = 3.33L$$

**Ventajas:**
✓ Simple de aplicar
✓ Funciona en la mayoría de procesos
✓ Se puede hacer experimentalmente

**Desventajas:**
✗ A veces produce overshoot de 20-25%
✗ No óptimo para sistemas muy lentos

---

### 4.2 Cohen–Coon (CC) - Mejoras sobre Ziegler–Nichols

Cohen y Coon propusieron **correcciones** a los parámetros ZN usando el mismo modelo FOPDT.

#### Fórmulas de Sintonía Cohen–Coon

**Para minimizar IAE (Integral de Error Absoluto):**

$$K_p = \frac{T}{LK} \left( \frac{4}{3} + \frac{1}{4} \frac{L}{T} \right)$$

$$T_i = L \frac{32 + 6 \frac{L}{T}}{13 + 8 \frac{L}{T}}$$

$$T_d = L \frac{4}{11 + 2 \frac{L}{T}}$$

#### Simplificación para Procesos Lentos

Cuando $\frac{L}{T} < 0.3$ (proceso dominado por constante de tiempo):

$$K_p = \frac{1.35T}{LK}$$

$$T_i = 2.5L$$

$$T_d = 0.37L$$

#### Comparación Numérica

Para un proceso: **K=1, L=1, T=5**

| Parámetro | Ziegler–Nichols | Cohen–Coon |
|-----------|-----------------|-----------|
| $K_p$ | $1.2 \times \frac{5}{1 \times 1} = 6.0$ | $1.35 \times \frac{5}{1 \times 1} = 6.75$ |
| $T_i$ | $2 \times 1 = 2.0$ seg | $2.5 \times 1 = 2.5$ seg |
| $T_d$ | $0.5 \times 1 = 0.5$ seg | $0.37 \times 1 = 0.37$ seg |

**Interpretación:**
- **CC es más agresiva** (Kp mayor)
- **CC tiene menos overshoot** (Td menor)
- **CC recomienda integral más suave** (Ti mayor)

---

## 5. Tabla de Fórmulas Completa

### Extracción de Parámetros FOPDT de Respuesta al Escalón

| Paso | Operación | Resultado |
|------|-----------|-----------|
| 1 | Identificar inicio de cambio en respuesta | $L$ = retardo de transporte |
| 2 | Encontrar 63.2% del valor final: $y(t_{63}) = 0.632 \times K$ | $(t_{63} - L)$ = constante de tiempo aparente $T$ |
| 3 | Valor final de la respuesta | $K$ = ganancia DC |

### Fórmulas Ziegler–Nichols

| Tipo de Control | $K_p$ | $T_i$ (seg) | $T_d$ (seg) |
|-----------------|-------|------------|-----------|
| **P** | $\frac{T}{LK}$ | ∞ | 0 |
| **PI** | $\frac{0.9T}{LK}$ | $3.33L$ | 0 |
| **PID** | $\frac{1.2T}{LK}$ | $2L$ | $0.5L$ |

### Fórmulas Cohen–Coon (IAE - Minimización)

| Tipo de Control | $K_p$ | $T_i$ (seg) | $T_d$ (seg) |
|-----------------|-------|------------|-----------|
| **PI** | $\frac{0.9T}{LK}\left(1 + \frac{L}{12T}\right)$ | $L\frac{30 + 3\frac{L}{T}}{9 + 20\frac{L}{T}}$ | 0 |
| **PID** | $\frac{T}{LK}\left(\frac{4}{3} + \frac{1}{4}\frac{L}{T}\right)$ | $L\frac{32 + 6\frac{L}{T}}{13 + 8\frac{L}{T}}$ | $L\frac{4}{11 + 2\frac{L}{T}}$ |

### Regla de Transición (Cohen–Coon Simplificado)

Si $L/T < 0.3$:

| Parámetro | Fórmula |
|-----------|---------|
| $K_p$ | $\frac{1.35T}{LK}$ |
| $T_i$ | $2.5L$ |
| $T_d$ | $0.37L$ |

---

## 6. Ejemplo de Proceso FOPDT Típico

### Caso 1: Sistema de Calentamiento (RECOMENDADO PARA PRUEBAS)

**Descripción física:**
Un tanque de agua se calienta mediante una resistencia. Se mide la temperatura con un sensor.

**Parámetros identificados:**
```
K = 2.0          (°C por % de potencia)
L = 2.0 seg      (retardo del sensor)
T = 10.0 seg     (constante de tiempo térmica)
```

**Función de transferencia FOPDT:**
$$G(s) = \frac{2.0}{10s + 1} e^{-2s}$$

**Sintonización Ziegler–Nichols:**
```
Kp = 1.2 × (10 / (2 × 2)) = 3.0
Ti = 2 × 2 = 4.0 seg
Td = 0.5 × 2 = 1.0 seg
```

**Sintonización Cohen–Coon:**
```
Ratio = L/T = 2/10 = 0.2 < 0.3 → Usar simplificado

Kp = 1.35 × (10 / (2 × 2)) = 3.375
Ti = 2.5 × 2 = 5.0 seg
Td = 0.37 × 2 = 0.74 seg
```

**Comparativa esperada:**
| Métrica | Sin PID | Con ZN | Con CC |
|---------|---------|--------|--------|
| ts (10%-90%) | ~15 seg | ~4 seg | ~3.5 seg |
| Overshoot | 0% | 20-25% | 10-15% |
| ess | ≈0.1°C | <0.01°C | <0.01°C |

---

### Caso 2: Sistema de Primer Orden Simple (educativo)

```
K = 1.0
L = 0.5 seg
T = 2.0 seg

G(s) = 1.0 / (2s + 1) × e^(-0.5s)
```

**Ziegler–Nichols PID:**
```
Kp = 1.2 × (2 / (0.5 × 1)) = 4.8
Ti = 2 × 0.5 = 1.0 seg
Td = 0.5 × 0.5 = 0.25 seg
```

---

### Caso 3: Sistema Lento (Industrial)

```
K = 0.5
L = 5.0 seg      (sensor remoto)
T = 50.0 seg     (proceso muy inercial)

G(s) = 0.5 / (50s + 1) × e^(-5s)
```

**Cohen–Coon (mejor para sistemas lentos):**
```
Ratio = 5/50 = 0.1 < 0.3

Kp = 1.35 × (50 / (5 × 0.5)) = 27.0
Ti = 2.5 × 5 = 12.5 seg
Td = 0.37 × 5 = 1.85 seg
```

---

## 7. Método Alternativo: Identificación Online (Opcional)

Para sistemas en operación, se puede usar el **método del lazo cerrado**:

1. **Aumentar Kp desde 0** hasta que el sistema oscile sostenidamente
2. **Registrar:** 
   - Kcr = Kp crítica (ganancia que produce oscilación)
   - Pcr = período crítico (período de oscilación en segundos)

3. **Fórmulas ZN completas:**

$$K_p = 0.6 \times K_{cr}$$

$$T_i = \frac{P_{cr}}{2}$$

$$T_d = \frac{P_{cr}}{8}$$

**Ventaja:** No necesita modelo experimental  
**Desventaja:** Peligroso si el proceso no es robusto

---

## 8. Validaciones Críticas en la Implementación

### Antes de Calcular Parámetros

```python
# Validar que el modelo sea FOPDT realizable
if L < 0 or T <= 0 or K <= 0:
    raise InvalidFOPDTError("Parámetros negativos o cero")

if L / T > 0.5:
    print("⚠️  Advertencia: Retardo muy grande (L/T > 0.5)")
    print("   Cohen-Coon puede no ser óptimo")
    print("   Considera métodos de control con predictor (Smith Predictor)")
```

### Después de Calcular PID

```python
# Verificar que los parámetros sean realizables
if Kp <= 0:
    raise TuningError("Kp debe ser positivo")

if Ti <= 0 or Td < 0:
    raise TuningError("Ti debe ser positivo, Td no negativo")

# Validar ratio Ti/Td (típicamente Ti > 4×Td)
if Ti < 4 * Td and Td > 0:
    print("⚠️  Advertencia: Ratio Ti/Td inusual")
    print(f"   Ti/Td = {Ti/Td:.2f} (típicamente > 4)")
```

---

## 9. Convergencia y Estabilidad

### Criterio de Nyquist Simplificado

Para que el PID sea estable en lazo cerrado:

$$|G(jω) \times C(jω)| < 1 \text{ en la frecuencia donde } \angle G \times C = -180°$$

En la práctica, usar margen de ganancia > 1.7 (~4.6 dB).

### Verificación en Simulación

```python
# Después de sintonizar, simular y validar:
y_closed_loop = simulate_with_pid(G, Kp, Ti, Td)

# Criterios de éxito
ts = settling_time(y_closed_loop)
Mp = overshoot(y_closed_loop)
ess = steady_state_error(y_closed_loop)

assert ts < 5 * L, "Tiempo de establecimiento muy lento"
assert Mp < 25, "Overshoot excesivo (>25%)"
assert ess < 0.01, "Error en estado estacionario grande"
```

---

## 10. Resumen: Flujo de Diseño Completo

```
USUARIO INGRESA: G(s) = K/(Ts+1) × e^(-Ls)
        ↓
VALIDAR parámetros FOPDT
        ↓
        ├─ Elegir ZN ─→ Aplicar fórmulas ZN
        │
        └─ Elegir CC ─→ Calcular L/T → Fórmulas apropiadas
        ↓
OBTENER: (Kp, Ti, Td)
        ↓
CREAR: PID(Kp, Ti, Td)
        ↓
SIMULAR:
   ├─ Sin control: y₁(t)
   └─ Con PID: y₂(t)
        ↓
CALCULAR MÉTRICAS:
   ├─ ts (10-90%)
   ├─ Mp (overshoot)
   ├─ ess (error final)
   └─ tr (rise time)
        ↓
VISUALIZAR:
   ├─ Gráfico comparativo
   ├─ Tabla de métricas
   └─ Parámetros PID
```

---

## Referencias Teóricas

- **Ziegler, J.G., Nichols, N.B.** "Optimum Settings for Automatic Controllers" (1942)
- **Cohen, G.H., Coon, G.A.** "Theoretical Consideration of Retarded Control" (1953)
- **Ogata, K.** "Modern Control Engineering" (5ta edición)
- **Franklin, Powell, Emami-Naeini** "Feedback Control of Dynamic Systems" (7ma edición)

