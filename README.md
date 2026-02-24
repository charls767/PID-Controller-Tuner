# 🎛️ PID Controller Tuner

**Herramienta interactiva para sintonización automática de controladores PID**

[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.0%2B-FF4B4B?style=flat-square&logo=streamlit)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

## 🎯 Características

- **Métodos de sintonización:** Ziegler-Nichols y Cohen-Coon
- **Visualización:** Simulaciones con/sin control y gráficos interactivos
- **Métricas:** Cálculo de ts, Mp, ess, tr
- **Exportación:** TXT, CSV, PNG

## 🚀 Inicio Rápido (3 min)

```bash
# Clonar y setup
git clone <repo> && cd "PID-Controller-Tuner"
python -m venv venv && venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Ejecutar
streamlit run app/main.py
```

Abre: `http://localhost:8501`

## 📖 Documentación

| Archivo | Contenido |
|---------|-----------|
| [GUIA_RAPIDA.md](GUIA_RAPIDA.md) | Primeros pasos |
| [ARQUITECTURA_MODULOS.md](ARQUITECTURA_MODULOS.md) | Estructura del código |
| [ESPECIFICACION.md](ESPECIFICACION.md) | Requisitos funcionales |
| [TUTORIAL_CONTROL.md](TUTORIAL_CONTROL.md) | Teoría PID y métodos |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Guía de contribución |

## 🧪 Desarrollo

```bash
# Tests
pip install pytest pytest-cov
pytest tests/ -v --cov=src

# Debug
streamlit run app/main.py --logger.level=debug
```

## 📝 Licencia

MIT - Ver [LICENSE](LICENSE)
