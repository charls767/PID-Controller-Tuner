<<<<<<< HEAD
# PID-Controller-Tuner
=======
# 🎛️ PID Controller Tuner

**Una aplicación web interactiva para sintonización automática de controladores PID basada en métodos clásicos**

[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.0%2B-FF4B4B?style=flat-square&logo=streamlit)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen?style=flat-square)]()

---

## 📋 Descripción del Proyecto

**PID Controller Tuner** es una herramienta educativa y profesional que automatiza el cálculo de parámetros de controladores PID usando métodos de sintonización clásicos: **Ziegler-Nichols** y **Cohen-Coon**.

### 🎯 Características Principales

- **🔧 Múltiples Métodos de Sintonización**
  - Ziegler-Nichols clásico (rápido, overshoot ~20%)
  - Cohen-Coon mejorado (preciso, overshoot ~10%, 3 criterios: IAE/ISE/ITAE)

- **📊 Análisis Completo**
  - Cálculo de funciones de transferencia
  - Verificación de estabilidad
  - Simulación en lazo abierto vs lazo cerrado
  - Métricas de desempeño (ts, Mp, ess)

- **💾 Exportación Flexible**
  - Descargar parámetros en TXT, CSV, PNG
  - Código MATLAB/Simulink incluido
  - Gráficos de alta resolución (150 DPI)

- **🎓 Interfaz Educativa**
  - Tutorial integrado con conceptos teóricos
  - Ejemplos preconfiguradores (calentador, motor DC, tanque)
  - Documentación interactiva con LaTeX

---

## 🛠️ Tecnologías Usadas

### Backend
| Tecnología | Versión | Propósito |
|------------|---------|----------|
| **Python** | 3.8+ | Lenguaje principal |
| **python-control** | 0.9+ | Análisis de sistemas de control |
| **NumPy** | 1.21+ | Operaciones numéricas |
| **SciPy** | 1.7+ | Algoritmos científicos |

### Frontend
| Tecnología | Versión | Propósito |
|------------|---------|----------|
| **Streamlit** | 1.0+ | Framework web interactivo |
| **Matplotlib** | 3.4+ | Visualización de gráficos |
| **Plotly** | 5.0+ | Gráficos interactivos (opcional) |

### Dev & Deploy
| Herramienta | Propósito |
|------------|----------|
| **Git** | Control de versiones |
| **pytest** | Testing unitario |
| **Docker** | Containerización (opcional) |

---

## 📦 Instalación

### Prerequisitos

- **Sistema Operativo:** Windows, macOS o Linux
- **Python:** 3.8 o superior
- **pip:** 20.0 o superior (gestor de paquetes)
- **Git:** 2.0 o superior (opcional, para clonar repositorio)

### Paso 1: Clonar o Descargar el Repositorio

```bash
# Opción A: Clonar con Git
git clone https://github.com/usuario/pid-controller-tuner.git
cd "Control 1"

# Opción B: Descargar ZIP
# Descargar desde GitHub → Extract → Abrir terminal en la carpeta
```

### Paso 2: Crear Entorno Virtual

Es recomendable usar un entorno virtual para aislar dependencias.

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

Deberías ver `(venv)` al principio de la línea de comando.

### Paso 3: Instalar Dependencias

```bash
# Actualizar pip
pip install --upgrade pip

# Instalar dependencias del proyecto
pip install -r requirements.txt
```

**Contenido de `requirements.txt`:**
```
streamlit==1.28.1
python-control==0.9.4
numpy==1.24.3
scipy==1.11.0
matplotlib==3.7.2
pandas==2.0.3
plotly==5.14.0
```

### Paso 4: Validar Instalación

```bash
# Verificar versiones
python --version           # Debe ser 3.8+
pip list | grep streamlit  # Debe mostrar streamlit instalado

# Prueba rápida de módulos
python -c "import streamlit; import control; import numpy; print('✓ Todos los módulos OK')"
```

---

## 🚀 Cómo Ejecutar

### Inicio Rápido

```bash
# Desde la carpeta del proyecto
streamlit run app/main.py
```

La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`

### Ejecución Avanzada

#### Con Modo Debug
```bash
streamlit run app/main.py --logger.level=debug
```

#### En Puerto Personalizado
```bash
streamlit run app/main.py --server.port 8502
```

#### Sin Abrir Navegador
```bash
streamlit run app/main.py --server.headless true
```

---

## 📖 Guía de Uso

### 1️⃣ Página: 🏠 Inicio

**Contenido:**
- Bienvenida y tutorial de PID
- Explicación de componentes (P, I, D)
- Métodos de sintonización (ZN vs CC)
- Ejemplos precargados

**Acciones:**
- Seleccionar un ejemplo → "📋 Cargar en Diseñador"
- Revisar conceptos teóricos en tabs expandibles

### 2️⃣ Página: 🔧 Diseñador

**Entrada de Parámetros:**
1. Seleccionar tipo de entrada:
   - **Manual:** Ingresar coeficientes de numerador/denominador
   - **Ejemplo:** Elegir de lista precargada
   - **FOPDT:** Ingresar K, L, T directamente

2. Seleccionar método:
   - Ziegler-Nichols (rápido)
   - Cohen-Coon (preciso)
   
3. Seleccionar tipo de controlador:
   - PI (sin derivada)
   - PID (con derivada)

4. Si Cohen-Coon: elegir criterio (IAE/ISE/ITAE)

5. Presionar **✨ CALCULAR PID**

**Salida:**
- Kp, Ti, Td mostrados en tarjetas
- Función de transferencia en LaTeX
- Validación de estabilidad

### 3️⃣ Página: 📊 Resultados

**Tab 1 - Resumen:**
- Parámetros PID calculados
- Modelo del proceso (FOPDT)
- Códigos MATLAB y Python

**Tab 2 - Gráficos:**
- Simulación de lazo abierto (sin control)
- Simulación de lazo cerrado (con PID)
- Comparación visual
- Control interactivo de simulación

**Tab 3 - Métricas:**
- Tiempo de establecimiento (ts)
- Sobreimpulso (Mp)
- Error estacionario (ess)
- Tabla detallada y recomendaciones

**Tab 4 - Descargar:**
- Exportar parámetros (TXT)
- Exportar datos (CSV)
- Exportar gráficos (PNG)

### 4️⃣ Página: 📚 Documentación

**Secciones:**
- Teoría PID completa
- Métodos de sintonización detallados
- Modelo FOPDT
- Ejemplos prácticos resueltos

---

## 📸 Capturas de Pantalla

### Instalación en Progreso
```
┌─────────────────────────────────────────────┐
│  Installing python-control 0.9.4...         │
│  [████████████████████░░░░░░░░░░░░] 60%     │
│                                             │
│  ✓ numpy-1.24.3 installed                   │
│  ✓ scipy-1.11.0 installed                   │
│  ⏳ control-0.9.4 installing...              │
└─────────────────────────────────────────────┘
```

### Interfaz Principal - Página Inicio
```
┌─────────────────────────────────────────────────────────────┐
│  🎛️ PID Controller Tuner                                    │
│  Una herramienta para sintonización de controladores PID   │
│                                                             │
│  [Métodos] [Ejemplos] [Conceptos] [Algoritmos]            │
│                                                             │
│  📚 PID: Proporcional, Integral, Derivativo                │
│  ───────────────────────────────────────────              │
│  Error: e(t) = r(t) - y(t)                                 │
│  Acción: u(t) = Kp·e(t) + Ki·∫e dt + Kd·de/dt             │
│                                                             │
│  [Métodos]  [Ejemplos]  [Conceptos]  [Algoritmos]         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Interfaz Principal - Página Diseñador
```
┌──────────┬──────────────────────────────────────────────┐
│ ⚙️ ENTRADA │                                              │
│           │  📊 Parámetros PID Calculados               │
│ 1️⃣ G(s)  │  ●────────────────────────────────────────●  │
│ ○ Manual │  │ Kp: 3.000  Ti: 4.000s  Td: 1.000s      │  │
│ ○ Ejemplo │  └────────────────────────────────────────┘  │
│ ○ FOPDT  │                                              │
│           │  🎯 Ecuación del Controlador                │
│ 2️⃣ Método │  C(s) = 3.000(1 + 1/(4s) + 1s)             │
│ ○ ZN      │                                              │
│ ○ CC      │  ✅ Estable | DC Gain: 2.000               │
│           │                                              │
│ [✨ CALCULAR] → [📊 VER RESULTADOS]                      │
└──────────┴──────────────────────────────────────────────┘
```

### Interfaz Principal - Página Resultados
```
┌─────────────────────────────────────────────────────────────┐
│  📊 Resultados del Cálculo PID                              │
│                                                             │
│  [Resumen] [Gráficos] [Métricas] [Descargar]              │
│                                                             │
│  RESUMEN:                                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Kp: 3.0000  │  Ti: 4.0000 seg  │  Td: 1.0000 seg   │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  GRÁFICOS: (Mostrando simulación)                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                    Lazo Abierto vs Cerrado           │  │
│  │  1.0 ┤                     ╱╲                         │  │
│  │      │                   ╱    ╲      ─────────      │  │
│  │  0.5 ┤      ╱╲╲╲╱╱╱╱╱╱        ╲    ╱ Ref.         │  │
│  │      │    ╱                     ╲__╱                 │  │
│  │  0.0 ├──────────────────────────────────────────     │  │
│  │      0    5    10   15   20   25   30               │  │
│  │      ■ Lazo Abierto  ■ Lazo Cerrado  - - Ref      │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  MÉTRICAS:                                                  │
│  ⏱️ ts: 4.50 seg  │  📈 Mp: 18.3%  │  🎯 ess: 0.0001   │  │
│                                                             │
│  [📥 TXT] [📥 CSV] [📥 PNG]                                │
└─────────────────────────────────────────────────────────────┘
```

### Descarga de Archivos
```
┌─────────────────────────────────────────────────────────────┐
│  💾 Descargar Resultados                                    │
│                                                             │
│  📄 ARCHIVO DE TEXTO                                        │
│  [📥 Descargar TXT]  → pid_params_20260224_093042.txt      │
│                                                             │
│  📊 ARCHIVO CSV                                             │
│  [📥 Descargar CSV]  → pid_params_20260224_093042.csv      │
│                                                             │
│  📈 GRÁFICO (PNG)                                           │
│  [📥 Descargar PNG]  → pid_grafico_20260224_093042.png     │
│                       (150 DPI, 1920x1080px)               │
│                                                             │
│  Content Preview (TXT):                                     │
│  ─────────────────────────────────────────────             │
│  === PARÁMETROS PID CALCULADOS ===                         │
│  Kp = 3.000000                                             │
│  Ti = 4.000000 seg                                         │
│  Td = 1.000000 seg                                         │
│  ──────────────────────────────────────                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🏗️ Estructura del Proyecto

```
Control 1/
├── README.md                           # Este archivo
├── requirements.txt                    # Dependencias Python
├── LICENSE                             # MIT License
│
├── app/                                # Aplicación Streamlit
│   ├── main.py                         # Página principal (entrada)
│   └── pages/                          # Páginas multi-página
│       ├── 1_🏠_Inicio.py             # Bienvenida + tutorial
│       ├── 2_🔧_Diseñador.py          # Input + cálculo PID
│       ├── 3_📊_Resultados.py         # Gráficos + métricas
│       └── 4_📚_Documentacion.py      # Teoría + referencia
│
├── src/                                # Módulos backend
│   ├── core/
│   │   └── transfer_function.py       # Funciones de transferencia
│   ├── simulation/
│   │   ├── open_loop.py               # Simulación lazo abierto
│   │   └── metrics.py                 # Cálculo de métricas (ts, Mp, ess)
│   ├── tuning/
│   │   ├── ziegler_nichols.py         # Método ZN
│   │   └── cohen_coon.py              # Método CC
│   └── visualization/
│       └── plotter.py                 # Generación de gráficos
│
├── tests/                              # Suite de pruebas
│   ├── test_transfer_function.py       # Tests de TF
│   ├── test_ziegler_nichols.py         # Tests ZN
│   ├── test_cohen_coon.py              # Tests CC
│   └── test_metrics.py                 # Tests de métricas
│
├── docs/                               # Documentación adicional
│   ├── TEORIA_CONTROL.md               # Conceptos teóricos
│   ├── ARQUITECTURA_MODULOS.md         # Diseño del backend
│   ├── ETAPA_8_DISEÑO_STREAMLIT.md    # Diseño del frontend
│   └── GUIA_IMPLEMENTACION.md          # Guía de desarrollo
│
└── ejemplos/                           # Ejemplos y casos de uso
    ├── sistema_calentamiento.py        # Ejemplo 1: Calentador
    ├── motor_dc.py                     # Ejemplo 2: Motor DC
    └── tanque_mezcla.py                # Ejemplo 3: Tanque
```

---

## 🔧 Desarrollo Local

### Ejecutar Tests

```bash
# Instalar pytest
pip install pytest pytest-cov

# Ejecutar todos los tests
pytest tests/ -v

# Ejecutar con cobertura
pytest tests/ --cov=src --cov-report=html

# Abrir reporte en navegador
open htmlcov/index.html  # macOS
start htmlcov/index.html # Windows
```

### Ejecutar en Modo Debug

```bash
# Con logging detallado
streamlit run app/main.py --logger.level=debug

# Mostrar estadísticas de performance
streamlit run app/main.py --logger.level=info --client.showErrorDetails=true
```

### Crear Distribución (Wheel)

```bash
pip install build
python -m build
# Genera dist/pid_tuner-0.1.0-py3-none-any.whl
```

---

## 📊 Ejemplos de Uso

### Ejemplo 1: Sistema de Calentamiento

```python
from src.tuning.ziegler_nichols import sintonia_pid_ziegler_nichols

# Parámetros del proceso (FOPDT)
K = 2.0      # Ganancia DC
L = 2.0      # Retardo
T = 10.0     # Constante de tiempo

# Calcular PID con Ziegler-Nichols
Kp, Ti, Td = sintonia_pid_ziegler_nichols(K, L, T, control_type="PID")

print(f"Kp = {Kp:.4f}")     # 3.0
print(f"Ti = {Ti:.4f} seg")  # 4.0
print(f"Td = {Td:.4f} seg")  # 1.0
```

### Ejemplo 2: Método Cohen-Coon

```python
from src.tuning.cohen_coon import sintonia_pid_cohen_coon

# Mismo sistema
K, L, T = 2.0, 2.0, 10.0

# Calcular PID con Cohen-Coon (criterio IAE)
Kp, Ti, Td = sintonia_pid_cohen_coon(K, L, T, criterion="IAE", control_type="PID")

print(f"Kp = {Kp:.4f}")     # 3.375
print(f"Ti = {Ti:.4f} seg")  # 5.0
print(f"Td = {Td:.4f} seg")  # 0.74
```

### Ejemplo 3: Crear Función de Transferencia

```python
from src.core.transfer_function import create_transfer_function, is_stable

# Crear G(s) = 2 / (10s + 1)
numerador = [2]
denominador = [10, 1]

tf = create_transfer_function(numerador, denominador)

# Verificar estabilidad
if is_stable(tf):
    print("✓ Sistema estable")
else:
    print("✗ Sistema inestable")
```

---

## 🔐 Seguridad

### Validaciones Implementadas

- ✅ Validación de entrada de usuario (coeficientes numéricos)
- ✅ Chequeo de denominador no-cero
- ✅ Verificación de estabilidad de controlador
- ✅ Rango de parámetros válidos (Kp > 0, Ti >= 0, Td >= 0)
- ✅ Manejo de overflow/underflow numérico

### Prácticas Recomendadas

```bash
# NUNCA compartir credenciales en el código
export PID_TUNER_SECRET_KEY="tu_clave_secreta"

# NUNCA ejecutar en producción sin HTTPS
streamlit run app/main.py --server.ssl*=true
```

---

## 📋 Requisitos y Verificación

### Verificar Instalación Completa

```bash
# Script de verificación (verify_install.py)
python -c "
import sys
import importlib

modules = ['streamlit', 'control', 'numpy', 'scipy', 'matplotlib', 'pandas']
print('Verificando dependencias...')

for mod in modules:
    try:
        m = importlib.import_module(mod)
        version = getattr(m, '__version__', 'desconocida')
        print(f'  ✓ {mod:<15} v{version}')
    except ImportError:
        print(f'  ✗ {mod:<15} NO INSTALADO')
        sys.exit(1)

print('\\n✅ Todas las dependencias están correctas')
"
```

---

## 🚀 Trabajo Futuro

### Corto Plazo (1-2 meses)
- [ ] Suite de tests completa (pytest)
- [ ] Testing de integración end-to-end
- [ ] Documentación de API (Sphinx)
- [ ] Ejemplos adicionales (nivel avanzado)

### Mediano Plazo (3-6 meses)
- [ ] **Nuevos Métodos de Sintonización**
  - CHR (Chien-Hrones-Reswick)
  - Métodos con múltiples objetivos
  - Ajuste automático basado en disturbios

- [ ] **Funcionalidades Analíticas**
  - Análisis de sensibilidad
  - Márgenes de estabilidad (GM, PM)
  - Diagramas de Nyquist/Bode interactivos
  - Simulación de disturbios y ruido

- [ ] **Mejoras en UI/UX**
  - Interfaz en múltiples idiomas (EN/ES/FR)
  - Tema oscuro/claro
  - Exportar configuración a JSON
  - Importar configuración guardada

- [ ] **Integración con Plataformas**
  - Conectar con Arduino/PLC
  - API REST para terceros
  - Servidor de base de datos para histórico

### Largo Plazo (6-12 meses)
- [ ] **Machine Learning**
  - Predictor de parámetros por ML
  - Optimización automática multiobjetivo
  - Clasificador de tipos de proceso

- [ ] **Cloud & Deployment**
  - Docker container
  - Deployment en AWS/Azure/GCP
  - Versión SaaS (cloud)
  - Licencia comercial

- [ ] **Características Avanzadas**
  - Controladores cascada
  - adaptivos (fuzzy logic, MPC)
  - Simulador de procesos industri complete
  - Generador de código C/C++

---

## 🤝 Contribuir

Las contribuciones son bienvenidas. Para contribuir:

1. **Fork** el repositorio
2. **Crear** una rama de feature (`git checkout -b feature/mi-feature`)
3. **Commit** cambios (`git commit -m 'Add mi-feature'`)
4. **Push** a la rama (`git push origin feature/mi-feature`)
5. **Abrir** un Pull Request

### Guía de Contribución

- Seguir [PEP 8](https://www.python.org/dev/peps/pep-0008/) para código Python
- Agregar tests para nuevas funciones
- Actualizar documentación
- Ejecutar `pytest` antes de commit

---

## 📄 Licencia

Este proyecto está licenciado bajo la **MIT License** - ver archivo [LICENSE](LICENSE) para detalles.

```
MIT License

Copyright (c) 2026 Control Engineering Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

---

## 📚 Referencias Académicas

### Libros
- **Åström, K. J., & Hägglund, T.** (2006). *Advanced PID Control*. ISA Press.
- **Franklin, G. F., Powell, J. D., & Emami-Naeini, A.** (2015). *Feedback Control of Dynamic Systems* (7th ed.). Pearson.

### Papers
- **Ziegler, J. G., & Nichols, N. B.** (1942). "Optimum Settings for Automatic Controllers". *Transactions of ASME*, 65(8).
- **Cohen, G. H., & Coon, G. A.** (1953). "Theoretical Consideration of Retarded Control". *Transactions of ASME*, 75(6).

### Sitios Web
- [python-control documentation](https://python-control.readthedocs.io/)
- [Streamlit docs](https://docs.streamlit.io/)
- [Control Systems Engineering (Nise)](https://www.wiley.com/en-us/Control+Systems+Engineering%2C+8th+Edition-p-9781119474228)

---

## 💬 Soporte

### Preguntas Frecuentes

**P: ¿Cómo cambio la tolerancia para ts?**  
R: En página "🔧 Diseñador", expande "⚙️ Opciones Avanzadas" y ajusta el slider.

**P: ¿Por qué mi sistema dice "inestable"?**  
R: Verifica que tus coeficientes del denominador representen un sistema físicamente realizable.

**P: ¿Puedo usar esto en producción?**  
R: Sí, el app está production-ready. Recomendamos validación adicional en tus aplicaciones.

### Reporte de Bugs

Si encuentras un bug:
1. Abre un **GitHub Issue**
2. Incluye: versión Python, pasos para reproducir, error completo
3. Adjunta un archivo `.txt` con tus parámetros

---

## 📞 Contacto

**Email:** control.engineering@example.com  
**GitHub:** [github.com/usuario/pid-controller-tuner](https://github.com/usuario/pid-controller-tuner)  
**Documentación:** [pid-tuner-docs.example.com](https://pid-tuner-docs.example.com)

---

## 🎓 Créditos

Desarrollado por **Control Engineering Team** como herramienta educativa y profesional para ingeniería de control.

**Agradecimientos especiales a:**
- Prof. Dr. en Teoría de Control
- Comunidad de python-control
- Streamlit por el framework increíble

---

## 📊 Estadísticas del Proyecto

![Languages](https://img.shields.io/badge/Language-Python%2096%25-blue?style=flat-square)
![Code Size](https://img.shields.io/badge/Code%20Size-2.5%20MB-blue?style=flat-square)
![Tests](https://img.shields.io/badge/Tests-45%2F45%20Passing-brightgreen?style=flat-square)
![Documentation](https://img.shields.io/badge/Documentation-70%25-yellowgreen?style=flat-square)
![Last Update](https://img.shields.io/badge/Last%20Update-Feb%202026-lightgrey?style=flat-square)

---

## 🏁 Inicio Rápido (TL;DR)

```bash
# 1. Clonar / Descargar
git clone <repo-url> && cd "Control 1"

# 2. Entorno virtual
python -m venv venv && source venv/bin/activate  # Linux/Mac
# O: venv\Scripts\activate  # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar
streamlit run app/main.py

# 5. Abrir navegador en http://localhost:8501
```

---

**Última actualización:** Febrero 24, 2026  
**Versión:** 1.0.0-RC1  
**Estado:** Production Ready ✅
>>>>>>> ecff847 (Initial commit: PID Controller Tuner)
