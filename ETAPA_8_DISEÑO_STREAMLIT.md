# ETAPA 8: Diseño de Interfaz Streamlit

## 1. Propuesta de Layout Detallado

### Arquitectura de Páginas

```
📱 PID TUNER - Aplicación Streamlit
├─ 📄 1_🏠_Inicio.py
│  └─ Bienvenida + Tutorial rápido
├─ 📄 2_🔧_Diseñador.py
│  └─ Ingreso de parámetros + Sintonización
├─ 📄 3_📊_Resultados.py
│  └─ Visualización de gráficos + Métricas
├─ 📄 4_📚_Documentación.py
│  └─ Ayuda integrada + Teoría
└─ 🎨 utils/
   ├─ styles.py (CSS personalizado)
   ├─ helpers.py (funciones auxiliares)
   └─ __init__.py
```

---

## 2. Página 1: Inicio 🏠

### Layout Visual

```
╔════════════════════════════════════════════════════════════════════════╗
║                                                                        ║
║                   🎛️  PID CONTROLLER TUNER                           ║
║                                                                        ║
║          Bienvenido al Sintonizador de Controladores PID              ║
║                                                                        ║
║  Esta herramienta te ayuda a diseñar y optimizar controladores PID   ║
║  para cualquier proceso industrial usando métodos clásicos.          ║
║                                                                        ║
╠════════════════════════════════════════════════════════════════════════╣
║  ¿Cómo Funciona?                                                       ║
║                                                                        ║
║  1️⃣  Ingresa la función de transferencia (numerador/denominador)     ║
║  2️⃣  Elige el método: Ziegler-Nichols o Cohen-Coon                  ║
║  3️⃣  Presiona "Calcular PID"                                         ║
║  4️⃣  Visualiza resultados y descarga reportes                        ║
║                                                                        ║
╠════════════════════════════════════════════════════════════════════════╣
║  Métodos Disponibles                                                   ║
║                                                                        ║
║  ✓ Ziegler-Nichols - Respuesta rápida (~20% overshoot)              ║
║  ✓ Cohen-Coon - Menos oscilación (~15% overshoot)                   ║
║  ✓ Amortiguado Crítico - Sin overshoot (experimental)                ║
║                                                                        ║
╠════════════════════════════════════════════════════════════════════════╣
║  Tipología de Procesos                                                 ║
║                                                                        ║
║  📌 FOPDT (First Order Plus Dead Time)                                ║
║     G(s) = K / (Ts+1) × e^(-Ls)                                       ║
║                                                                        ║
║     K = Ganancia DC                                                   ║
║     T = Constante de tiempo                                           ║
║     L = Retardo de transporte                                         ║
║                                                                        ║
╚════════════════════════════════════════════════════════════════════════╝
```

### Elementos Streamlit

```python
st.set_page_config(
    page_title="PID Tuner",
    page_icon="🎛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título y descripción
st.title("🎛️ PID Controller Tuner")
st.markdown("### Sistema Inteligente de Sintonización de Controladores")

# Información en pestañas
tab1, tab2, tab3 = st.tabs(["¿Cómo Funciona?", "Métodos", "Ejemplos"])

with tab1:
    st.markdown("""
    ## Flujo de Trabajo
    
    1. **Ingreso**: Proporciona la función de transferencia
    2. **Selección**: Elige método de sintonización
    3. **Cálculo**: Sistema calcula parámetros óptimos
    4. **Análisis**: Visualiza resultados y métricas
    5. **Descarga**: Exporta reportes en PDF
    """)

with tab2:
    # Cards de métodos
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Ziegler-Nichols", "20-25%", "Rápido")
    with col2:
        st.metric("Cohen-Coon", "10-15%", "Balanceado")
    with col3:
        st.metric("Crítico", "0-5%", "Lento")

with tab3:
    st.write("Ejemplos precargados...")
```

---

## 3. Página 2: Diseñador 🔧

### Layout con Sidebar + Main

```
├─ SIDEBAR (25% ancho)                    │ MAIN (75% ancho)
│                                        │
│ 🔧 INGRESO DE PARÁMETROS              │ 📊 VISTA PREVIA
│                                        │
│ ┌──────────────────────────┐          │ ┌──────────────────────────┐
│ │ FUNCIÓN DE TRANSFERENCIA │          │ │ Entrada de Números       │
│ ├──────────────────────────┤          │ │                          │
│ │ Método                   │          │ │ 🔍 Verificador           │
│ │ [Ziegler-Nichols    ▼]   │          │ │  ✓ G(s) válida          │
│ │ [Cohen-Coon         ]    │          │ │  ✗ Parámetros inv.      │
│ │ [Amortiguado Crítico]    │          │ │                          │
│ │                          │          │ │ 📈 Representación        │
│ │ Tipo de Controlador  │          │
│ │ [PI            ▼]        │          │ N(s) = num[0]s + num[1]  │
│ │ [PID           ]         │          │ D(s) = den[0]s² + ...    │
│ │                          │          │                          │
│ │ ┌─ Criterio (solo CC) ──┐│          │ 🔘 Lazo Abierto          │
│ │ │ [IAE          ▼]     ││          │ │ Estable: ✓              │
│ │ │ [ISE          ]      ││          │ │ Polos: -0.5, -2.3       │
│ │ │ [ITAE         ]      ││          │ │                         │
│ │ └────────────────────── ┘│          │ └──────────────────────────┘
│ │                          │          │
│ │ ┌─ Opciones Avanzadas ─┐│          │
│ │ │ [x] Mostrar banda     ││          │
│ │ │ [ ] Perturbaciones    ││          │
│ │ │ [ ] Export PDF        ││          │
│ │ └────────────────────── ┘│          │
│ │                          │          │
│ │     [🔄 CALCULAR PID]   │          │
│ │                          │          │
│ └──────────────────────────┘          │
│                                        │
```

### Estructura de Datos (Session State)

```python
# En la sesión de Streamlit se guardan:
st.session_state.numerador = [1.0]           # Coeficientes del numerador
st.session_state.denominador = [10.0, 1.0]   # Coeficientes del denominador
st.session_state.metodo = "Ziegler-Nichols"  # Método seleccionado
st.session_state.tipo_controlador = "PID"    # PI o PID
st.session_state.criterio = "IAE"            # Para Cohen-Coon
st.session_state.transfer_function = None    # Objeto G(s)
st.session_state.pid_params = None           # {Kp, Ti, Td}
st.session_state.metricas = None             # {ts, Mp, ess}
st.session_state.mostrar_banda = True        # Para gráficos
```

---

## 4. Página 3: Resultados 📊

### Layout Tabular

```
╔════════════════════════════════════════════════════════════════════════╗
║                                                                        ║
║                     ✅ CÁLCULO COMPLETADO                             ║
║                                                                        ║
╠════════════════════════════════════════════════════════════════════════╣
║  PARÁMETROS PID CALCULADOS                                             ║
║                                                                        ║
║  ┌────────────────┬──────────────┬─────────────────┐                  ║
║  │ Kp (Ganancia)  │ Ti (Integral)│ Td (Derivativo) │                  ║
║  ├────────────────┼──────────────┼─────────────────┤                  ║
║  │   3.000        │   4.000 seg  │   1.000 seg     │                  ║
║  └────────────────┴──────────────┴─────────────────┘                  ║
║                                                                        ║
║  ECUACIÓN DEL CONTROLADOR:                                             ║
║                                                                        ║
║  C(s) = Kp × (1 + 1/(Ti×s) + Td×s)                                   ║
║       = 3.0 × (1 + 1/(4.0×s) + 1.0×s)                                ║
║                                                                        ║
╠════════════════════════════════════════════════════════════════════════╣
║  MÉTRICAS DE DESEMPEÑO                                                 ║
║                                                                        ║
║  ┌─────────────────────┬──────────────┬─────────────────┐              ║
║  │ Métrica             │ Valor        │ Clasificación   │              ║
║  ├─────────────────────┼──────────────┼─────────────────┤              ║
║  │ Tiempo Establecim.  │ 18.7 seg     │ ✓ Bueno         │              ║
║  │ Sobreimpulso        │ 15.3 %       │ ✓ Aceptable     │              ║
║  │ Error Estacionario  │ 0.0023 units │ ✓ Excelente     │              ║
║  └─────────────────────┴──────────────┴─────────────────┘              ║
║                                                                        ║
╠════════════════════════════════════════════════════════════════════════╣
║  🎨 GRÁFICOS COMPARATIVOS                                              ║
║                                                                        ║
║  ┌─────────────────────────────────────────────────────────────────┐   ║
║  │                                                                 │   ║
║  │  1.2 ┤                         ╭───────────                    │   ║
║  │       │ ▬▬▬ Com PID            │                               │   ║
║  │  1.0 ┤ ―――― Plan (lazo abierto)│╭─────────────                │   ║
║  │       │                        ││                             │   ║
║  │  0.8 ┤                         ││                             │   ║
║  │       │                        ╰╯                             │   ║
║  │  0.6 ┤                                                        │   ║
║  │       │                                                        │   ║
║  │  0.4 ┤  ╭────────────────────────────────────────────────   │   ║
║  │       │ ╭╯                                                    │   ║
║  │  0.2 ┤│                                                      │   ║
║  │       ╯                                                       │   ║
║  │  0.0 ┴───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬────────│   ║
║  │       0   5  10  15  20  25  30  35  40  45  50    t[seg] │   ║
║  │                                                                 │   ║
║  │ Area gris: Banda de tolerancia ±2%                           │   ║
║  │                                                                 │   ║
║  └─────────────────────────────────────────────────────────────────┘   ║
║                                                                        ║
║  [📥 Descargar PNG] [📄 Descargar PDF] [📋 Copiar números]           ║
║                                                                        ║
╚════════════════════════════════════════════════════════════════════════╝
```

---

## 5. Página 4: Documentación 📚

```
Pestañas con:
- Teoría PID (¿qué es Kp? ¿Ti? ¿Td?)
- Métodos (ZN vs CC)
- FOPDT (modelo industrial)
- Ejemplos (3-4 casos predeterminados)
- API Reference (para devs)
```

---

## 6. Archivo: config.py (Configuración Global)

```python
# Estilos y configuración
COLORES = {
    "principal": "#0066CC",      # Azul
    "éxito": "#00CC66",          # Verde
    "advertencia": "#FF9900",    # Naranja
    "error": "#CC0000"           # Rojo
}

TEMAS = {
    "light": "light",
    "dark": "dark"
}

# Validaciones
LIMITES = {
    "K_min": 0.01,
    "K_max": 100.0,
    "L_min": 0.0,
    "L_max": 1000.0,
    "T_min": 0.01,
    "T_max": 1000.0
}

GRADO_POLINOMIO_MAX = 5
PRECISION_DECIMAL = 4
```

