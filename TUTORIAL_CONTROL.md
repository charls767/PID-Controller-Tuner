# Tutorial: Teoría de Control - PID, Ziegler–Nichols y Cohen–Coon

## 1. ¿Qué es un Controlador PID?

Un **controlador PID** (Proporcional–Integral–Derivativo) ajusta una acción de control en función del error para llevar el sistema hacia la referencia.

### Ecuación del PID

En **tiempo continuo**:

$$u(t) = K_p e(t) + K_i \int_0^t e(\tau) d\tau + K_d \frac{de(t)}{dt}$$

O con constantes de tiempo:

$$u(t) = K_p \left( e(t) + \frac{1}{T_i} \int_0^t e(\tau) d\tau + T_d \frac{de(t)}{dt} \right)$$

### Parámetros: Kp, Ti, Td

| Parámetro | Nombre | Función |
|-----------|--------|---------|
| **Kp** | Ganancia Proporcional | Reacciona al error actual |
| **Ti** | Tiempo Integral | Elimina error en estado estacionario |
| **Td** | Tiempo Derivativo | Amortigua oscilaciones |

## 2. FOPDT: Modelo de Primer Orden + Retardo

**FOPDT** = First Order Plus Dead Time

Función de transferencia:

$$G(s) = \frac{K}{Ts + 1} e^{-Ls}$$

Donde:
- **K**: Ganancia DC
- **L**: Retardo de transporte (segundos)
- **T**: Constante de tiempo (segundos)

## 3. Método Ziegler–Nichols

El método más clásico. Pasos:

1. Aplicar escalón unitario sin controlador
2. Extraer L (retardo), T (cte. tiempo), K (ganancia DC)
3. Aplicar fórmulas:

**Para PID:**
$$K_p = \frac{1.2T}{LK}, \quad T_i = 2L, \quad T_d = 0.5L$$

**Para PI:**
$$K_p = \frac{0.9T}{LK}, \quad T_i = 3.33L$$

## 4. Método Cohen–Coon

Mejora sobre Ziegler–Nichols. Fórmulas para IAE:

$$K_p = \frac{T}{LK} \left( \frac{4}{3} + \frac{1}{4} \frac{L}{T} \right)$$

$$T_i = L \frac{32 + 6 \frac{L}{T}}{13 + 8 \frac{L}{T}}$$

$$T_d = L \frac{4}{11 + 2 \frac{L}{T}}$$

**Para procesos lentos** (L/T < 0.3):

$$K_p = \frac{1.35T}{LK}, \quad T_i = 2.5L, \quad T_d = 0.37L$$

## 5. Ejemplo Práctico: Sistema de Calentamiento

**Parámetros:**
```
K = 2.0 (°C por % potencia)
L = 2.0 seg (retardo)
T = 10.0 seg (cte. tiempo)
```

**Ziegler–Nichols:**
```
Kp = 3.0,  Ti = 4.0 seg,  Td = 1.0 seg
```

**Cohen–Coon:**
```
Kp = 3.375,  Ti = 5.0 seg,  Td = 0.74 seg
```

## 6. Checklist de Validación

```python
# Validar parámetros FOPDT
assert L >= 0 and T > 0 and K > 0

# Validar parámetros PID
assert Kp > 0
assert Ti > 0
assert Td >= 0

# Validar ratio
if Ti < 4 * Td and Td > 0:
    print("⚠️ Ratio Ti/Td inusual")
```

## 7. Flujo Completo

```
ENTRADA: G(s) = K/(Ts+1) × e^(-Ls)
    ↓
ELEGIR MÉTODO (ZN o CC)
    ↓
CALCULAR (Kp, Ti, Td)
    ↓
SIMULAR (con y sin control)
    ↓
CALCULAR MÉTRICAS (ts, Mp, ess)
    ↓
VISUALIZAR Y EXPORTAR
```

## Referencias

- Ziegler & Nichols (1942)
- Cohen & Coon (1953)
- Ogata "Modern Control Engineering"
