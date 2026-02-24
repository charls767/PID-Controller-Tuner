# Guía Rápida: Primeros Pasos

**Sistema:** PID Controller Tuner  
**Versión:** 1.0

## ✅ Instalación (5 minutos)

```bash
# 1. Clonar repositorio
git clone <repo-url>
cd "PID-Controller-Tuner"

# 2. Entorno virtual (Windows)
python -m venv venv
venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar
streamlit run app/main.py
```

Abre: `http://localhost:8501`

## 📖 Archivos Principales

| Archivo | Propósito |
|---------|-----------|
| [README.md](README.md) | Visión general y características |
| [ARQUITECTURA_MODULOS.md](ARQUITECTURA_MODULOS.md) | Estructura del código backend |
| [ESPECIFICACION.md](ESPECIFICACION.md) | Requisitos funcionales |
| [TUTORIAL_CONTROL.md](TUTORIAL_CONTROL.md) | Teoría PID y métodos de sintonización |

## 🔧 Estructura del Proyecto

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

## 🏗️ Estructura de Carpetas

```
pid-controller-tuner/
├── src/                    # Backend Python
│   ├── core/              # Funciones de transferencia
│   ├── tuning/            # Métodos ZN y Cohen-Coon
│   ├── simulation/        # Simulación y métricas
│   ├── visualization/     # Gráficos
│   └── utils/             # Utilidades
├── app/                    # Frontend Streamlit
│   ├── main.py
│   └── pages/
├── tests/                  # Tests unitarios
└── requirements.txt        # Dependencias
```

## 📋 Tareas Comunes

```bash
# Ver todos los tests
pytest tests/ -v

# Ver cobertura de tests
pytest tests/ --cov=src

# Ejecutar app con debug
streamlit run app/main.py --logger.level=debug
```

## 🔗 Enlaces Útiles

- [python-control docs](https://python-control.readthedocs.io/)
- [Streamlit docs](https://docs.streamlit.io/)
- [PEP 8 Style Guide](https://pep8.org/)

