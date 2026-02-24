# Resumen Visual del Proyecto

## 1. Diagrama de Flujo del Sistema Completo

```
╔════════════════════════════════════════════════════════════════════════════╗
║                    SINTONIZADOR DE CONTROLADORES PID                       ║
║                          (Flujo Completo)                                  ║
╚════════════════════════════════════════════════════════════════════════════╝

                              ┌─────────────────┐
                              │  USUARIO FINAL  │
                              └────────┬────────┘
                                       │
                    ┌──────────────────┴──────────────────┐
                    │                                     │
            ┌───────▼────────┐              ┌────────────▼──────────┐
            │  WEB BROWSER   │              │  INTERFAZ STREAMLIT   │
            │   (localhost)  │◄────────────►│                       │
            └────────────────┘   HTTP       │  • Página 1: Inicio   │
                                            │  • Página 2: Diseñador│
                                            │  • Página 3: Result.  │
                                            │  • Página 4: Docs     │
                                            └────────────┬──────────┘
                                                         │
                                            ┌────────────▼──────────┐
                                            │   BACKEND PYTHON      │
                                            │                       │
                                   ┌────────┼───────────────────────┤
                                   │        │                       │
                    ┌──────────────▼─┐      │  ┌──────────────────┐ │
                    │  INPUT         │      │  │  core/           │ │
                    │ • Numerador [] │      │  │ • Transfer Fn    │ │
                    │ • Denominador[]│      │  │ • Validation     │ │
                    └─────┬──────────┘      │  └──────────────────┘ │
                          │                │                        │
                    ┌─────▼──────────┐     │  ┌──────────────────┐ │
                    │ VALIDACIÓN     │     │  │  tuning/         │ │
                    │ • Sintaxis OK? │     │  │ • BaseTuner      │ │
                    │ • Valores OK?  │     │  │ • ZieglerNichols │ │
                    │ • G(s) válida? │     │  │ • CohenCoon      │ │
                    └─────┬──────────┘     │  └──────────────────┘ │
                          │                │                        │
                    ┌─────▼──────────┐     │  ┌──────────────────┐ │
                    │  SELECCIÓN     │     │  │  simulation/     │ │
                    │ • ZN (default) │     │  │ • Controller     │ │
                    │ • CC           │     │  │ • SimulationEng  │ │
                    └─────┬──────────┘     │  │ • Metrics        │ │
                          │                │  └──────────────────┘ │
                    ┌─────▼──────────┐     │                        │
                    │  SINTONIZACIÓN │     │  ┌──────────────────┐ │
                    │                │     │  │  visualization/  │ │
                    │ calculate_PID()│     │  │ • Plotter        │ │
                    │ ↓              │     │  │ • Styles         │ │
                    │ (Kp,Ti,Td)     │     │  └──────────────────┘ │
                    └─────┬──────────┘     │                        │
                          │                │  ┌──────────────────┐ │
                    ┌─────▼──────────┐     │  │  utils/          │ │
                    │  SIMULACIÓN    │     │  │ • Export         │ │
                    │                │     │  │ • Logger         │ │
                    │ • Sin control  │     │  │ • Constants      │ │
                    │ • Con PID      │     │  └──────────────────┘ │
                    │                │     │                        │
                    │ ↓              │     │                        │
                    │ [y(t), u(t)]   │     │                        │
                    └─────┬──────────┘     └────────────────────────┘
                          │
                    ┌─────▼──────────┐
                    │  CALCULO DE    │
                    │  MÉTRICAS      │
                    │                │
                    │ • ts (settle)  │
                    │ • Mp (overshoot)
                    │ • ess (error)  │
                    │ • tr (rise)    │
                    └─────┬──────────┘
                          │
                    ┌─────▼──────────┐
                    │  GENERACIÓN    │
                    │  DE GRÁFICOS   │
                    │                │
                    │ comparativo.png│
                    │ parámetros.txt │
                    └─────┬──────────┘
                          │
                    ┌─────▼──────────┐
                    │  RESULTADOS    │
                    │  EN STREAMLIT  │
                    │                │
                    │  [Gráfico]     │
                    │  [Tabla]       │
                    │  [Botones]     │
                    │                │
                    │  [Exportar]    │
                    └────────────────┘
```

---

## 2. Ciclo de Vida del Desarrollo (7 Semanas)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    TIMELINE DE DESARROLLO                           │
└─────────────────────────────────────────────────────────────────────┘

SEMANA 1: INFRAESTRUCTURA Y CORE
┌───────────────────────────────────────────────────────────────────┐
│ ✓ Setup inicial (directorios, venv, requirements)                 │
│ ✓ TransferFunction (clase principal)                              │
│ ✓ Validation (funciones de validación)                            │
│ ✓ Pruebas unitarias core/                                         │
│                                                                     │
│ RESULTADO: Backend core testeable y funcional ✓                   │
└───────────────────────────────────────────────────────────────────┘

SEMANA 2: MÉTODOS DE SINTONIZACIÓN
┌───────────────────────────────────────────────────────────────────┐
│ ✓ BaseTuner (clase abstracta)                                     │
│ ✓ ZieglerNichols (implementación completa)                        │
│ ✓ CohenCoon (implementación completa)                             │
│ ✓ Pruebas de sintonización                                        │
│                                                                     │
│ RESULTADO: Métodos de sintonización validados v0.2 ✓             │
└───────────────────────────────────────────────────────────────────┘

SEMANA 3: SIMULACIÓN Y MÉTRICAS
┌───────────────────────────────────────────────────────────────────┐
│ ✓ PIDController (controlador digital)                             │
│ ✓ SimulationEngine (motor de simulación ODE)                      │
│ ✓ PerformanceMetrics (cálculo de ts, Mp, ess, tr)               │
│ ✓ Integración: Tuning → Simulación → Métricas                   │
│                                                                     │
│ RESULTADO: Pipeline completo backend v0.3 ✓                      │
└───────────────────────────────────────────────────────────────────┘

SEMANA 4: VISUALIZACIÓN
┌───────────────────────────────────────────────────────────────────┐
│ ✓ Plotter (gráficos interactivos con Plotly)                     │
│ ✓ Styles (temas y colores)                                        │
│ ✓ Pruebas de visualización                                        │
│                                                                     │
│ RESULTADO: Gráficos listos para Streamlit v0.4-alpha ✓           │
└───────────────────────────────────────────────────────────────────┘

SEMANA 5: FRONTEND STREAMLIT
┌───────────────────────────────────────────────────────────────────┐
│ ✓ app/main.py (punto de entrada)                                  │
│ ✓ pages/1_Inicio.py, 2_Diseñador.py, 3_Resultados.py, 4_Docs    │
│ ✓ components/ (input_form, results_display, sidebar)              │
│ ✓ Session state e integración                                     │
│ ✓ Exportación (CSV, PNG)                                          │
│                                                                     │
│ RESULTADO: Aplicación web funcional v0.5-beta ✓                  │
└───────────────────────────────────────────────────────────────────┘

SEMANA 6: TESTING Y QA
┌───────────────────────────────────────────────────────────────────┐
│ ✓ Tests exhaustivos (80%+ cobertura)                              │
│ ✓ Casos edge cases y degenerados                                  │
│ ✓ Performance profiling                                           │
│ ✓ Testing de interfaz (manual)                                    │
│ ✓ Documentación de bugs                                           │
│                                                                     │
│ RESULTADO: Calidad asegurada v0.8-rc ✓                           │
└───────────────────────────────────────────────────────────────────┘

SEMANA 7: DOCUMENTACIÓN Y RELEASE
┌───────────────────────────────────────────────────────────────────┐
│ ✓ README.md profesional                                           │
│ ✓ Manual de usuario (docs/)                                       │
│ ✓ API backend documentada                                         │
│ ✓ Docstrings 100% en código                                       │
│ ✓ GitHub setup + tags de release                                  │
│ ✓ Últimos pulido y optimización                                  │
│                                                                     │
│ RESULTADO: v1.0 RELEASE ✓✓✓ LISTO PARA PORTAFOLIO              │
└───────────────────────────────────────────────────────────────────┘
```

---

## 3. Dependencias Entre Módulos (Gráfico de Red)

```
                    ┌─────────────────┐
                    │   app/          │ (Streamlit UI)
                    │   (Frontend)    │
                    └────────┬────────┘
                             │
                ┌────────────┼────────────┐
                │            │            │
        ┌───────▼─────┐ ┌────▼────┐ ┌────▼────┐
        │visualization│ │simulation│ │ tuning/ │
        │    /        │ │  /       │ │         │
        └───────┬─────┘ └────┬─────┘ └────┬────┘
                │            │            │
                │            │      ┌─────▼────┐
                │            │      │ core/    │◄─── Dependencia
                │            │      │ (base)   │
                └────┬────────┴──────┤          │
                     │               └──────────┘
                ┌────▼────┐
                │ utils/  │
                │(export) │
                └─────────┘


Orden de Implementación:
1. core/              (independiente)
2. tuning/            (depende de core)
3. simulation/        (depende de core)
4. visualization/     (depende de simulation)
5. utils/export       (depende de visualization)
6. app/               (integra todo)
```

---

## 4. Estados de Usuario en la Interfaz

```
USUARIO:
  Nuevo?
    │
    ├─► SÍ ──► [LEER DOCUMENTACIÓN] ──► Ir a Diseñador
    │
    └─► NO ──► [COMENZAR] ──────────┐
                                    ▼
              ┌─────────────────────────────────┐
              │  DISEÑADOR: Ingreso de G(s)     │
              │  Estado: ESPERANDO_ENTRADA      │
              └────────────┬────────────────────┘
                           │
                    ┌──────▼─────┐
                    │ ¿Entrada OK?│
                    └──┬──────┬───┘
                       │NO    │SÍ
                    ┌──▼─┐    │
                    │ERR │    ▼
                    │MSG │  [Habilitar Siguiente]
                    │    │    │
                    └────┘    ▼
                         ┌──────────────────────┐
                         │ DISEÑADOR: Método    │
                         │ Estado: ESPERANDO    │
                         │ METODO               │
                         └────────┬─────────────┘
                                  │
                           [Seleccionar ZN/CC]
                                  │
                              ┌───▼───┐
                              │ CLICK │
                              │SINTON │
                              └───┬───┘
                                  │
                              ┌───▼────────────────┐
                              │ Estado: CALCULANDO │
                              │ Spinner activo     │
                              └───┬────────────────┘
                                  │ 1-2 seg
                                  │
                     ┌────────────┬┴────────────┐
                     │            │            │
                   SUCCESS      TIMEOUT      ERROR
                     │            │            │
                     ▼            ▼            ▼
              ┌─────────────┐ ┌──────────┐ ┌────────────┐
              │RESULTADOS:  │ │REINTENTAR│ │MENSAJE ERR │
              │• Kp, Ti, Td │ │          │ │            │
              │• Gráfico    │ └──────────┘ └────────────┘
              │• Métricas   │
              │• Exportar   │
              └─────────────┘
```

---

## 5. Matriz de Requisitos vs Módulos

```
┌──────────────────┬──────┬────┬────┬──────┬───┬───┐
│ REQUISITO        │Core  │Tune│Sim │Visual│Exp│App│
├──────────────────┼──────┼────┼────┼──────┼───┼───┤
│RF1: Input G(s)   │ ✓✓✓  │    │    │      │   │ ✓ │
│RF2: ZN tuning    │      │✓✓✓ │    │      │   │ ✓ │
│RF3: CC tuning    │      │✓✓✓ │    │      │   │ ✓ │
│RF4: Simulation   │      │    │✓✓✓ │      │   │ ✓ │
│RF5: Metrics      │      │    │✓✓✓ │      │   │ ✓ │
│RF6: Graphics     │      │    │    │✓✓✓   │   │ ✓ │
│RF7: Export       │      │    │    │      │✓✓✓│ ✓ │
│                  │      │    │    │      │   │   │
│RNF1: Performance │✓     │✓   │✓   │✓     │   │ ✓ │
│RNF2: Usability   │      │    │    │      │   │✓✓ │
│RNF3: Reliability │✓✓    │✓   │✓   │      │   │✓  │
│RNF4: Escalab.    │✓✓✓   │    │    │      │   │   │
│RNF5: Maintain.   │✓     │✓   │✓   │      │   │✓  │
│RNF6: Compat.     │✓     │✓   │✓   │✓     │✓  │✓  │
└──────────────────┴──────┴────┴────┴──────┴───┴───┘

Leyenda: ✓✓✓ = Módulo crítico, ✓✓ = Importante, ✓ = Contribuye
```

---

## 6. Típico Session en Streamlit (Estado)

```
SESSION STATE EN STREAMLIT
(Persiste durante toda la sesión del usuario)

Inicial (Página 1: Inicio)
├─ transfer_function: None
├─ kp, ti, td: None
├─ simulation_results: None
├─ metrics: None
└─ theme: "light"

Después de validar G(s) (Página 2: Step 1)
├─ transfer_function: TransferFunction([1, 2], [1, 3, 2])
├─ tf_is_valid: True
└─ [resto igual]

Después de elegir método y sintonizar
├─ [anterior]
├─ tuning_method: "ziegler_nichols"
├─ kp: 2.34
├─ ti: 1.56
├─ td: 0.39
├─ tuning_success: True
└─ [resto igual]

Después de simular (Página 3: Resultados)
├─ [anterior]
├─ simulation_results: {
│    "time": [0, 0.01, ..., 20],
│    "y_open_loop": [0, 0.01, ..., 1.0],
│    "y_closed_loop": [0, 0.05, ..., 1.0],
│  }
├─ metrics: {
│    "ts_open": 5.2,
│    "ts_closed": 1.8,
│    "mp_open": 0.25,
│    "mp_closed": 0.12,
│    "ess_open": 0.05,
│    "ess_closed": 0.001,
│    "tr_open": 3.1,
│    "tr_closed": 0.9,
│  }
├─ figure_comparison: <plotly Figure>
└─ [resto igual]
```

---

## 7. Checklist de Calidad (DoD - Definition of Done)

Para cada módulo/feature:

```
☐ Código escrito (siguiendo PEP 8)
☐ Tests unitarios (>90% cobertura para ese módulo)
☐ Tests pasan localmente
☐ Docstrings completos
☐ Sin warnings en linter
☐ Documentado en README si público
☐ Commit descriptivo en Git
☐ Code review (si aplicable)
☐ Integración sin romper nada
☐ Performance aceptable
```

---

## 8. Arquitectura de Alto Nivel

```
┌────────────────────────────────────────────────────────────┐
│                  STREAMLIT APP (main.py)                    │
│                  └─ Coordina páginas                        │
├────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ PRESENTATION LAYER (app/pages, components)          │   │
│  │ • Manejo de UI                                       │   │
│  │ • Session state                                      │   │
│  │ • Llamadas a Backend                                │   │
│  └────────────────────┬────────────────────────────────┘   │
│                       │ API Interna                         │
│  ┌────────────────────▼────────────────────────────────┐   │
│  │ BUSINESS LOGIC LAYER (src/)                         │   │
│  │                                                     │   │
│  │ ┌──────────────────────────────────────────────┐   │   │
│  │ │ Transfer Function Analysis (core/)           │   │   │
│  │ ├─ TransferFunction: Polos, ceros, estabilidad│   │   │
│  │ ├─ Validation: Validaciones de entrada        │   │   │
│  │ └─ Exceptions: Errores personalizados         │   │   │
│  │                                                │   │   │
│  │ ┌──────────────────────────────────────────────┐   │   │
│  │ │ PID Tuning (tuning/)                         │   │   │
│  │ ├─ BaseTuner: Interfaz para métodos           │   │   │
│  │ ├─ ZieglerNichols: Implementación ZN          │   │   │
│  │ ├─ CohenCoon: Implementación CC               │   │   │
│  │ └─ Utils: Cálculos auxiliares                │   │   │
│  │                                                │   │   │
│  │ ┌──────────────────────────────────────────────┐   │   │
│  │ │ Simulation (simulation/)                     │   │   │
│  │ ├─ PIDController: Controlador digital         │   │   │
│  │ ├─ SimulationEngine: ODE + comparativa        │   │   │
│  │ └─ Metrics: Cálculo de desempeño              │   │   │
│  │                                                │   │   │
│  │ ┌──────────────────────────────────────────────┐   │   │
│  │ │ Visualization & Export (visualization/, ...) │   │   │
│  │ ├─ Plotter: Gráficos Plotly                   │   │   │
│  │ ├─ Styles: Temas                              │   │   │
│  │ └─ Export: CSV, PNG                           │   │   │
│  │                                                │   │   │
│  │ ┌──────────────────────────────────────────────┐   │   │
│  │ │ Utilities (utils/)                           │   │   │
│  │ ├─ Logger, Constants, Export                  │   │   │
│  │ └─ Helpers                                     │   │   │
│  │                                                │   │   │
│  └──────────────────────────────────────────────┘   │
│                       │                             │
└───────────────────────┼─────────────────────────────┘
                        │
           ┌────────────▼──────────┐
           │ EXTERNAL LIBRARIES    │
           │                       │
           │ • python-control      │
           │ • scipy.integrate     │
           │ • numpy               │
           │ • plotly              │
           │                       │
           └───────────────────────┘
```

---

## 9. Ejemplo de Flujo de Datos Completo

```
USUARIO ingresa:
├─ Numerador: [1, 2]
├─ Denominador: [1, 3, 2]
├─ Método: "Ziegler-Nichols"
└─ Clic: "Sintonizar"
             │
             ▼
  ┌──────────────────────┐
  │ 1. VALIDACIÓN        │
  │ validation.py        │
  ├──────────────────────┤
  │ ✓ Sintaxis OK        │
  │ ✓ Valores numéricos  │
  │ ✓ Polinomios válidos │
  └────────┬─────────────┘
           │
           ▼
  ┌──────────────────────┐
  │ 2. CREAR TF          │
  │ TransferFunction()   │
  ├──────────────────────┤
  │ G(s) = (s+2)/(s²+3s+2)
  │ Polos: [-1, -2]      │
  │ Estable: SÍ          │
  └────────┬─────────────┘
           │
           ▼
  ┌──────────────────────┐
  │ 3. SINTONIZACIÓN     │
  │ ZieglerNichols.tune()│
  ├──────────────────────┤
  │ i) Extraer L, T, K   │
  │ ii) Calcular Kp,Ti,Td
  │ Resultado:           │
  │ Kp = 2.34            │
  │ Ti = 1.56            │
  │ Td = 0.39            │
  └────────┬─────────────┘
           │
           ▼
  ┌──────────────────────┐
  │ 4. SIMULACIÓN        │
  │ SimulationEngine     │
  ├──────────────────────┤
  │ Open-loop:           │
  │ y1(t) = tf_response()│
  │                      │
  │ Closed-loop:         │
  │ control = PID(Kp,Ti,Td)
  │ y2(t) = sim_with_ctrl()
  └────────┬─────────────┘
           │
           ▼
  ┌──────────────────────┐
  │ 5. MÉTRICAS          │
  │ PerformanceMetrics   │
  ├──────────────────────┤
  │ ts: 5.2 s vs 1.8 s   │
  │ Mp: 25% vs 12%       │
  │ ess: 0.05 vs 0.001   │
  │ tr: 3.1 s vs 0.9 s   │
  └────────┬─────────────┘
           │
           ▼
  ┌──────────────────────┐
  │ 6. VISUALIZACIÓN     │
  │ Plotter.compare()    │
  ├──────────────────────┤
  │ Gráfico interactivo  │
  │ azul: sin control    │
  │ rojo: con PID        │
  │ Anotaciones de ts,Mp │
  └────────┬─────────────┘
           │
           ▼
  ┌──────────────────────┐
  │ 7. MOSTRAR EN        │
  │ STREAMLIT            │
  ├──────────────────────┤
  │ st.plotly_chart()    │
  │ st.dataframe(metrics)│
  │ st.download_button() │
  └──────────────────────┘
             │
             ▼
   ┌──────────────────┐
   │ USUARIO ve:      │
   ├──────────────────┤
   │ ✓ Gráfico        │
   │ ✓ Tabla métricas │
   │ ✓ Botón descargar│
   └──────────────────┘
```

---

## 10. Matriz de Riesgos y Mitigación

```
┌──────────────────────┬──────────┬──────────────────────┐
│ Riesgo               │ Severidad│ Mitigación           │
├──────────────────────┼──────────┼──────────────────────┤
│ Método ZN no         │ ALTA     │ Validación de        │
│ converge             │          │ aplicabilidad, try   │
│                      │          │ -catch con fallback  │
├──────────────────────┼──────────┼──────────────────────┤
│ Performance lento    │ MEDIA    │ Profiling temprano,  │
│ en Streamlit         │          │ optimización de      │
│                      │          │ gráficos             │
├──────────────────────┼──────────┼──────────────────────┤
│ Precisión numérica   │ MEDIA    │ Usar double float,   │
│ insuficiente         │          │ Comparación con      │
│                      │          │ valores teóricos     │
├──────────────────────┼──────────┼──────────────────────┤
│ UI confusa para      │ BAJA     │ User testing,        │
│ usuario              │          │ feedback temprano    │
├──────────────────────┼──────────┼──────────────────────┤
│ Dependencias         │ BAJA     │ Fijar versiones      │
│ incompatibles        │          │ específicas en       │
│                      │          │ requirements.txt     │
└──────────────────────┴──────────┴──────────────────────┘
```

---

**Fin del Resumen Visual**

Este documento es una brújula visual para navegar el proyecto.  
Úsalo para:
- Entender la arquitectura rápidamente
- Comunicar el proyecto a otros
- Rastrear progreso contra estos diagramas

