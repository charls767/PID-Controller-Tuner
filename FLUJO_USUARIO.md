# Flujo de Usuario y Experiencia de Interfaz

## 1. Flujo General del Usuario

```
┌─────────────────────────────────────────────────────────────────┐
│                    INICIO                                       │
│              (Página de Bienvenida)                             │
│  • Logo del proyecto                                            │
│  • Descripción breve                                            │
│  • Botones: "Comenzar" / "Ver Documentación"                   │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ↓
            ┌────────────────────┐
            │ ¿Nuevo usuario?    │
            └────────┬───────────┘
                     │
         ┌───────────┴───────────┐
         ↓                       ↓
    [Leer Docs]           [Ir a Diseñador]
         │                       │
         ↓                       │
    Tutorial PID            ┌────┴──────────────────┐
    Métodos ZN/CC           │  DISEÑADOR (Paso 1)   │
    Ejemplos                │  Ingreso de G(s)      │
         │                  │  • Campo num[]        │
         └──────────┬───────┤  • Campo den[]        │
                    │       │  • Validación auto    │
                    ↓       │  • Ayuda (?)          │
            ┌──────────────────────────────────────┐
            │  DISEÑADOR (Paso 2)                  │
            │  Método de Sintonización             │
            │  ◯ Ziegler–Nichols (por defecto)    │
            │  ◯ Cohen–Coon                       │
            │  • Botón: "Sintonizar"              │
            └────────────┬─────────────────────────┘
                         │
          [Validación fallida]
                ├─→ Mensaje error claro
                └─→ Volver a Paso 1
                         │ ✓ Éxito
                         ↓
            ┌──────────────────────────────────────┐
            │  DISEÑADOR (Paso 3)                  │
            │  Parámetros Sintonizados             │
            │  • Kp = 2.34                         │
            │  • Ti = 1.56 seg                     │
            │  • Td = 0.39 seg                     │
            │  • Método usado: ZN                  │
            │  • Botón: "Simular"                 │
            └────────────┬─────────────────────────┘
                         │
                         ↓
            ┌──────────────────────────────────────┐
            │  RESULTADOS                          │
            │  (Nueva página o tab)                │
            │                                      │
            │  [Gráfico Interactivo]               │
            │  • Respuesta sin control (azul)      │
            │  • Respuesta con PID (rojo)          │
            │  • Referencias y bandas ±5%          │
            │                                      │
            │  [Tabla de Métricas]                 │
            │  ┌────────────────────────────────┐ │
            │  │ Métrica   │ Sin Control│Con PID│ │
            │  ├────────────────────────────────┤ │
            │  │ ts (seg)  │    5.2    │  1.8   │ │
            │  │ Mp (%)    │    25     │  12    │ │
            │  │ ess       │   0.05    │  0.001 │ │
            │  │ tr (seg)  │    3.1    │  0.9   │ │
            │  └────────────────────────────────┘ │
            │                                      │
            │  [Botones de Acción]                │
            │  • Exportar CSV                     │
            │  • Descargar Gráfico (PNG)          │
            │  • Nueva Simulación                 │
            │  • Ver Parámetros Alternativos      │
            └──────────────────────────────────────┘
```

---

## 2. Estructura de Páginas (Streamlit Multi-Page)

### **Página 1: Inicio (`1_Inicio.py`)**

**Contenido:**
- Encabezado con logo
- Descripción del proyecto (2-3 párrafos)
- Características principales en cards
- Botón "Comenzar" → redirige a Diseñador
- Sección "Recursos":
  - Link a "Documentación completa"
  - Link a "Ejemplos"

**Ejemplo de renderización:**
```
╔════════════════════════════════════════════════════════════════╗
║           🎛️ SINTONIZADOR DE CONTROLADORES PID                ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║ Diseña controladores PID optimizados para tu sistema.         ║
║ Utiliza métodos clásicos: Ziegler–Nichols y Cohen–Coon.     ║
║                                                                ║
║ ┌─────────────────┬──────────────┬───────────────────┐        ║
║ │ 📊 Ingresa G(s) │ 🔧 Sintoniza │ 📈 Visualiza      │        ║
║ │ Función de      │ parámetros   │ resultados y      │        ║
║ │ transferencia   │ automáticos  │ métricas          │        ║
║ └─────────────────┴──────────────┴───────────────────┘        ║
║                                                                ║
║                    [COMENZAR] [VER DOCS]                      ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
```

---

### **Página 2: Diseñador (`2_Diseñador.py`)**

**Sección 1: Entrada de Función de Transferencia**
```
╔═══════════════════════════════════════════════════════════════╗
║ PASO 1: Ingresa tu Función de Transferencia                  ║
║ (Ayuda: G(s) = N(s) / D(s))                                  ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║ Numerador N(s):    [input: "1,2"]                            ║
║ Denominador D(s):  [input: "1,3,2"]                          ║
║                                                               ║
║ Ejemplo: En forma polyval del más alto al menor grado        ║
║ G(s) = (s + 2) / (s² + 3s + 2)                              ║
║ Numerador:   [1, 2]                                          ║
║ Denominador: [1, 3, 2]                                       ║
║                                                               ║
║ [Ayuda] [Cargar Ejemplo] [Validar]                           ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

**Componente: Input Form**
- Campos de texto para numerador y denominador
- Validación en tiempo real (con toggle)
- Botón "Validar G(s)"
- Retroalimentación visual (✓ válido / ✗ inválido)
- Desplegable con ejemplos predefinidos

**Sección 2: Selección de Método**
```
╔═══════════════════════════════════════════════════════════════╗
║ PASO 2: Elige Método de Sintonización                        ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║ Ziegler–Nichols (Recomendado)                                ║
║ ◯ Método de respuesta al escalón                             ║
║ ◯ Método del lazo cerrado                                    ║
║                                                               ║
║ ─────────────────────────────────────────────────────────    ║
║                                                               ║
║ Cohen–Coon                                                    ║
║ ◯ Método Cohen–Coon                                          ║
║                                                               ║
║ [INFO] [COMPARAR MÉTODOS]                                    ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

**Componente: Method Selector**
- Radio buttons para elegir método principal
- Sub-opciones en acordeón
- Enlaces a información sobre cada método
- Botón "Comparar": muestra parámetros de ambos métodos

**Sección 3: Botón "Sintonizar"**
```
╔═══════════════════════════════════════════════════════════════╗
║                   [SINTONIZAR]                                ║
║              (Presiona para calcular)                         ║
╚═══════════════════════════════════════════════════════════════╝
```

**Estados:**
- Default: habilitado si G(s) es válida
- Loading: spinner + "Calculando parámetros..."
- Success: mostrar resultado (PASO 3)
- Error: mensaje descriptivo

---

### **Página 3: Resultados (`3_Resultados.py`)**

**Sección 1: Parámetros Sintonizados**
```
╔═══════════════════════════════════════════════════════════════╗
║ PARÁMETROS SINTONIZADOS                                       ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║ Método: Ziegler–Nichols (Respuesta al Escalón)              ║
║                                                               ║
║ ┌─────────────┬──────────────────────────────────────────┐  ║
║ │   Kp (Ganancia Proporcional)      │  2.34              │  ║
║ │   Ti (Tiempo Integral)            │  1.56 seg          │  ║
║ │   Td (Tiempo Derivativo)          │  0.39 seg          │  ║
║ │   Controlador PID: u = Kp(e +....) │                   │  ║
║ └─────────────┴──────────────────────────────────────────┘  ║
║                                                               ║
║ [Copiar Parámetros] [Probar Otros Métodos]                  ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

**Sección 2: Gráfico Interactivo**
```
╔═══════════════════════════════════════════════════════════════╗
║ COMPARACIÓN DE RESPUESTAS                                     ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  1.0 ┤                               ╱───→ Con PID          ║
║      │        ╱───────────→         ╱                        ║
║      │       ╱  Sin Control        ╱                         ║
║  0.8 ┤      ╱                      ╱                         ║
║      │                            ╱                          ║
║      │                           ╱  ts = 1.8s               ║
║  0.6 ┤                          ╱    Mp = 12%               ║
║      │                         ╱                             ║
║      │                        ╱                              ║
║  0.4 ┤─────┬───────┬─────────╱──────┬────────────            ║
║      │     2       4         6       8       10       t(seg) ║
║                                                               ║
║ (Visualización interactiva con zoom, hover info, etc.)       ║
║ [Descargar PNG] [Ver Tabla Completa]                        ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

**Componente: Results Display**
- Gráfico interactivo con Plotly
- Paleta de colores clara
- Leyendas y anotaciones
- Zoom, pan, hover con información

**Sección 3: Tabla de Métricas**
```
╔═══════════════════════════════════════════════════════════════╗
║ MÉTRICAS DE DESEMPEÑO                                         ║
╠═════════════════════════╦════════════════╦═══════════════════╣
║ Métrica                 ║ Sin Controlador║ Con Controlador   ║
╠═════════════════════════╬════════════════╬═══════════════════╣
║ Tiempo de Establecimiento (ts) │ 5.2 s  │ 1.8 s             ║
║ Sobreimpulso (Mp)              │ 25%    │ 12%               ║
║ Error en Est. Estacionario     │ 0.05   │ 0.001             ║
║ Tiempo de Levantamiento (tr)   │ 3.1 s  │ 0.9 s             ║
╚═════════════════════════╩════════════════╩═══════════════════╝
```

**Componente: Metrics Table**
- Tabla comparativa (2 columnas)
- Colores verde/rojo para mejor/peor
- Iconos de mejora (↓↓ mejora, ↑↑ empeora)
- Unidades claras

**Sección 4: Opciones de Exportación**
```
╔═══════════════════════════════════════════════════════════════╗
║ EXPORTAR RESULTADOS                                           ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║ [📥 Descargar CSV] [🖼️ Descargar Gráfico (PNG)]             ║
║                                                               ║
║ Generado: 2026-02-24 14:32:15                               ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

**Sección 5: Acciones Secundarias**
```
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║ [← Volver a Diseñador] [Nueva Simulación] [Ver Diagrama PZ]  ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

---

### **Página 4: Documentación (`4_Documentacion.py`)**

**Contenido (pestañas):**

1. **Conceptos Básicos**
   - ¿Qué es un controlador PID?
   - Parámetros Kp, Ti, Td
   - Métricas de desempeño

2. **Métodos de Sintonización**
   - Ziegler–Nichols (teoría y pasos)
   - Cohen–Coon (mejoras, cuándo usar)
   - Comparación

3. **Ejemplos Prácticos**
   - Sistema de 1er orden
   - Sistema de 2do orden
   - Sistema más complejo

4. **Preguntas Frecuentes**
   - "¿Por qué mi sistema es inestable?"
   - "¿Qué método debo usar?"
   - etc.

---

## 3. Barra Lateral (Sidebar Común)

```
╔════════════════════════════════════╗
║   SINTONIZADOR PID                 ║
╠════════════════════════════════════╣
║                                    ║
║ 📄 Página actual                   ║
║ 🏠 Inicio                          ║
║ 🔧 Diseñador                       ║
║ 📊 Resultados                      ║
║ 📚 Documentación                   ║
║                                    ║
║ ────────────────────────────────   ║
║                                    ║
║ ⚙️  Configuración                  ║
║ 🌙 Tema: Light / Dark              ║
║ 📏 Precisión: 2 decimales          ║
║ ⏱️ Tiempo máx: 20 segundos         ║
║                                    ║
║ ────────────────────────────────   ║
║                                    ║
║ ℹ️ Acerca de                       ║
║ v1.0.0                             ║
║ Desarrollado: 2026                 ║
║                                    ║
╚════════════════════════════════════╝
```

---

## 4. Flujo de Errores y Validación

### **Validación de Entrada (en tiempo real)**
- ✗ Numerador vacío → "Numerador requerido"
- ✗ Valores no numéricos → "Solo números permitidos"
- ✗ Denominador = 0 → "Denominador no válido"
- ✗ Sistema inestable → "Advertencia: Sistema inestable. Algunos métodos pueden fallar"

### **Errores de Sintonización**
- ✗ Método no aplicable → "Este método requiere que el sistema sea estable"
- ✗ Parámetros sin convergencia → "Error en cálculo de parámetros. Intenta otro método"

### **Manejo Graceful**
Todos los errores muestran:
1. **Mensaje claro** en lenguaje del usuario
2. **Causa probable** (ej: "El denominador es cero")
3. **Acción sugerida** (ej: "Ajusta los coeficientes")

---

## 5. Experiencia de Usuario - Detalles UX

### **Responsividad**
- Calculación < 2 seg: sin spinner
- Calculación 2-5 seg: spinner con "Calculando..."
- > 5 seg: mostrar progreso

### **Accesibilidad**
- Contraste suficiente (WCAG AA)
- Labels claros en todos los campos
- Ayuda con iconos (?)

### **Feedback Visual**
- Colores: Verde (éxito), Rojo (error), Azul (info)
- Iconos descriptivos
- Animaciones suaves (sin distracciones)

### **Estructura Lógica**
- **Inicio** → Tutorial rápido
- **Diseñador** → Paso a paso (nunca 3+ campos simultáneos)
- **Resultados** → Conclusiones y exportación
- **Documentación** → Referencias cuando sea necesario

---

## 6. Estadías Persistentes (Session State)

En Streamlit, guardar en `st.session_state`:
```python
# Después de validar G(s)
st.session_state['tf_num'] = [1, 2]
st.session_state['tf_den'] = [1, 3, 2]
st.session_state['tf_valid'] = True

# Después de sintonizar
st.session_state['kp'] = 2.34
st.session_state['ti'] = 1.56
st.session_state['td'] = 0.39
st.session_state['method'] = 'ziegler_nichols'

# Después de simular
st.session_state['results'] = {...}
```

Esto permite navegar sin perder datos entre páginas.

---

## 7. Resumen del Flujo de Dolor ("Happy Path")

1. **Usuario llega** → Página Inicio
2. **Lee descripción rápida** → Entiende de qué se trata
3. **Hace click "Comenzar"** → Va a Diseñador
4. **Ingresa G(s)** → El campo bajo valida automáticamente
5. **Elige método** → Por defecto ZN (radiobotón pre-seleccionado)
6. **Click "Sintonizar"** → 1-2 segundos de espera
7. **Ve parámetros PID** → aparecen en la misma página (Step 3)
8. **Click automático "Ver Resultados"** → Va a Resultados
9. **Visualiza gráficos + métricas** → Entiende mejora del controlador
10. **Exporta CSV/PNG** → Guarda documentación
11. **Opcional: Intenta otro método** → Vuelve a Diseñador, comparación inmediata

**Tiempo total**: ~2-3 minutos  
**Clics mínimos**: 5-6

