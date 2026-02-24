"""
Módulo de Visualización de Respuestas

Genera gráficos comparativos de respuestas en lazo abierto vs lazo cerrado
usando matplotlib y plotly para diversas aplicaciones (terminal, Streamlit).
"""

from typing import Tuple, Optional, List, Dict
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


class VisualizacionError(Exception):
    """Se levanta cuando hay error en la visualización."""
    pass


def graficar_respuestas(
    t_planta: np.ndarray,
    y_planta: np.ndarray,
    t_pid: np.ndarray,
    y_pid: np.ndarray,
    yref: float = 1.0,
    title: str = "Comparación: Planta vs Sistema Controlado",
    tolerance: float = 0.02,
    figsize: Tuple[int, int] = (12, 6),
    show_band: bool = True
) -> plt.Figure:
    """
    Genera gráfico comparativo de respuestas en lazo abierto y cerrado.
    
    ============================================================================
    TEORÍA
    ============================================================================
    
    La visualización permite comparar:
    
    1. RESPUESTA EN LAZO ABIERTO (Planta sin control)
       - Comportamiento natural del sistema sin realimentación
       - Típicamente lenta y sin capacidad de tracking
       - Sirve como baseline para evaluar mejora del control
    
    2. RESPUESTA EN LAZO CERRADO (Con PID)
       - Comportamiento del sistema con realimentación y controlador
       - Más rápida pero con posible overshoot
       - Muestra capacidad de seguimiento de referencia
    
    3. BANDA DE TOLERANCIA (±2% o configurable)
       - Define cuándo el sistema "ha llegado" a la referencia
       - Usada para calcular tiempo de establecimiento
       - Visualización clara del régimen permanente
    
    ============================================================================
    ELEMENTOS GRÁFICOS
    ============================================================================
    
    - Línea azul: Respuesta de planta (lenta)
    - Línea roja: Respuesta controlada (rápida)
    - Línea negra punteada: Referencia (setpoint)
    - Área gris: Banda de tolerancia (±2%)
    - Grid: Para lectura fácil de valores
    - Leyenda: Identificación clara de curvas
    - Títulos en español: Ejes etiquetados
    
    ============================================================================
    
    Parameters:
        t_planta (np.ndarray):
            Vector de tiempo para la respuesta sin control [seg]
            - Debe tener al menos 10 elementos
            - Típicamente 300-500 puntos para buena resolución
        
        y_planta (np.ndarray):
            Respuesta de la planta sin control
            - Mismo tamaño que t_planta
            - Valores numéricos
        
        t_pid (np.ndarray):
            Vector de tiempo para la respuesta controlada [seg]
            - Puede tener diferente tamaño que t_planta
            - Típicamente más corto si converge más rápido
        
        y_pid (np.ndarray):
            Respuesta del sistema con controlador PID
            - Mismo tamaño que t_pid
            - Valores numéricos
        
        yref (float):
            Valor de referencia (setpoint) [unidades]
            - Default: 1.0
            - Debe ser distinto de cero
            - Mostrado como línea horizontal negra
        
        title (str):
            Título del gráfico
            - Default: "Comparación: Planta vs Sistema Controlado"
            - Versión en español
        
        tolerance (float):
            Tolerancia para banda de establecimiento [%]
            - Default: 0.02 (±2%)
            - Rango típico: 0.01 (1%) a 0.05 (5%)
            - Mostrado como área gris
        
        figsize (Tuple[int, int]):
            Tamaño de la figura en pulgadas (ancho, alto)
            - Default: (12, 6)
            - Ajustar según pantalla
        
        show_band (bool):
            Si mostrar la banda de tolerancia
            - Default: True
            - Establecer False para gráfico más limpio
    
    Returns:
        plt.Figure:
            Objeto Figura de matplotlib listo para:
            - Mostrar en terminal: plt.show()
            - Guardar en archivo: fig.savefig('nombre.png')
            - Usar en Streamlit: st.pyplot(fig)
    
    Raises:
        VisualizacionError:
            - Si len(t_planta) < 10 o len(t_pid) < 10
            - Si len(t_planta) != len(y_planta) o len(t_pid) != len(y_pid)
            - Si yref == 0
            - Si tolerance <= 0 o tolerance >= 1
            - Si hay NaN o Inf en vectores
    
    Examples:
        ===== Ejemplo 1: Comparación básica =====
        
        >>> import numpy as np
        >>> import matplotlib.pyplot as plt
        >>> 
        >>> # Planta sin control (lenta, G(s) = 1/(10s+1))
        >>> t_planta = np.linspace(0, 50, 300)
        >>> y_planta = 1.0 - np.exp(-t_planta/10)
        >>> 
        >>> # Con PID (rápida, con overshoot ~20%)
        >>> t_pid = np.linspace(0, 20, 200)
        >>> y_pid = 1.0 - np.exp(-0.2*t_pid) * np.cos(0.2*t_pid)
        >>> 
        >>> fig = graficar_respuestas(t_planta, y_planta, t_pid, y_pid)
        >>> plt.show()
        
        [Se despliega gráfico con dos curvas comparadas]
        
        ===== Ejemplo 2: Diferentes referencias =====
        
        >>> # Referencia = 50°C (en lugar de 1.0)
        >>> y_planta_50 = 50.0 * (1.0 - np.exp(-t_planta/10))
        >>> y_pid_50 = 50.0 * (1.0 - np.exp(-0.2*t_pid) * np.cos(0.2*t_pid))
        >>> 
        >>> fig = graficar_respuestas(
        ...     t_planta, y_planta_50,
        ...     t_pid, y_pid_50,
        ...     yref=50.0,
        ...     title="Control de Temperatura a 50°C"
        ... )
        
        ===== Ejemplo 3: Con banda de tolerancia =====
        
        >>> fig = graficar_respuestas(
        ...     t_planta, y_planta,
        ...     t_pid, y_pid,
        ...     yref=1.0,
        ...     tolerance=0.05,  # ±5% en lugar de ±2%
        ...     show_band=True
        ... )
        
        ===== Ejemplo 4: Guardar en archivo =====
        
        >>> fig = graficar_respuestas(t_planta, y_planta, t_pid, y_pid)
        >>> fig.savefig('comparacion_pid.png', dpi=300, bbox_inches='tight')
        >>> print("Gráfico guardado a comparacion_pid.png")
        
        ===== Ejemplo 5: Integración con Streamlit =====
        
        >>> import streamlit as st
        >>> 
        >>> # En la aplicación Streamlit:
        >>> fig = graficar_respuestas(t_planta, y_planta, t_pid, y_pid)
        >>> st.pyplot(fig)
        >>> 
        >>> # Descarga de imagen
        >>> buf = io.BytesIO()
        >>> fig.savefig(buf, format='png')
        >>> st.download_button("Descargar gráfico", buf.getvalue())
    """
    
    # ====================================================================
    # VALIDACIÓN DE ENTRADA
    # ====================================================================
    
    t_planta = np.asarray(t_planta, dtype=np.float64)
    y_planta = np.asarray(y_planta, dtype=np.float64)
    t_pid = np.asarray(t_pid, dtype=np.float64)
    y_pid = np.asarray(y_pid, dtype=np.float64)
    
    if len(t_planta) < 10:
        raise VisualizacionError(f"t_planta debe tener al menos 10 elementos, recibido: {len(t_planta)}")
    
    if len(t_pid) < 10:
        raise VisualizacionError(f"t_pid debe tener al menos 10 elementos, recibido: {len(t_pid)}")
    
    if len(t_planta) != len(y_planta):
        raise VisualizacionError(f"t_planta y y_planta deben tener mismo tamaño: {len(t_planta)} != {len(y_planta)}")
    
    if len(t_pid) != len(y_pid):
        raise VisualizacionError(f"t_pid y y_pid deben tener mismo tamaño: {len(t_pid)} != {len(y_pid)}")
    
    if yref == 0.0:
        raise VisualizacionError("yref debe ser distinto de 0")
    
    if tolerance <= 0 or tolerance >= 1:
        raise VisualizacionError(f"tolerance debe estar en (0, 1), recibido: {tolerance}")
    
    if np.any(~np.isfinite(t_planta)) or np.any(~np.isfinite(y_planta)):
        raise VisualizacionError("t_planta o y_planta contienen NaN o Inf")
    
    if np.any(~np.isfinite(t_pid)) or np.any(~np.isfinite(y_pid)):
        raise VisualizacionError("t_pid o y_pid contienen NaN o Inf")
    
    # ====================================================================
    # CREAR FIGURA
    # ====================================================================
    
    fig, ax = plt.subplots(figsize=figsize, dpi=100)
    
    # ====================================================================
    # DIBUJAR BANDA DE TOLERANCIA
    # ====================================================================
    
    if show_band:
        band_upper = yref + tolerance * np.abs(yref)
        band_lower = yref - tolerance * np.abs(yref)
        t_max = max(t_planta[-1], t_pid[-1])
        ax.fill_between(
            [0, t_max],
            band_lower, band_upper,
            alpha=0.2,
            color='gray',
            label=f'Banda ±{tolerance*100:.0f}%'
        )
    
    # ====================================================================
    # DIBUJAR CURVAS
    # ====================================================================
    
    # Respuesta sin control (planta)
    ax.plot(
        t_planta, y_planta,
        linewidth=2.5,
        color='#0066CC',
        label='Planta (lazo abierto)',
        linestyle='-'
    )
    
    # Respuesta con controlador
    ax.plot(
        t_pid, y_pid,
        linewidth=2.5,
        color='#CC0000',
        label='Sistema con PID (lazo cerrado)',
        linestyle='-'
    )
    
    # Línea de referencia
    t_max = max(t_planta[-1], t_pid[-1])
    ax.axhline(
        y=yref,
        color='black',
        linestyle='--',
        linewidth=2,
        label=f'Referencia (Setpoint = {yref})',
        alpha=0.7
    )
    
    # ====================================================================
    # FORMATEO GRÁFICO
    # ====================================================================
    
    # Etiquetas y título
    ax.set_xlabel('Tiempo [seg]', fontsize=12, fontweight='bold')
    ax.set_ylabel('Salida [unidades]', fontsize=12, fontweight='bold')
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    
    # Grid
    ax.grid(True, which='major', alpha=0.3, linestyle='-', linewidth=0.5)
    ax.grid(True, which='minor', alpha=0.1, linestyle=':', linewidth=0.3)
    
    # Leyenda
    ax.legend(
        loc='right',
        fontsize=11,
        framealpha=0.9,
        edgecolor='black',
        frameon=True
    )
    
    # Márgenes
    ax.set_xlim(0, t_max)
    y_min = min(np.min(y_planta), np.min(y_pid))
    y_max = max(np.max(y_planta), np.max(y_pid))
    margin = 0.1 * (y_max - y_min)
    ax.set_ylim(y_min - margin, y_max + margin)
    
    # Layout ajustado
    plt.tight_layout()
    
    return fig


def graficar_respuesta_individual(
    t: np.ndarray,
    y: np.ndarray,
    yref: float = 1.0,
    title: str = "Respuesta del Sistema",
    figsize: Tuple[int, int] = (10, 6),
    color: str = '#0066CC'
) -> plt.Figure:
    """
    Gráfico individual de una respuesta (sin comparación).
    
    Parameters:
        t: Vector de tiempo
        y: Vector de respuesta
        yref: Referencia
        title: Título del gráfico
        figsize: Tamaño de figura
        color: Color de la línea
    
    Returns:
        Figura de matplotlib
    
    Example:
        >>> t = np.linspace(0, 30, 300)
        >>> y = 1.0 - np.exp(-0.1*t)
        >>> fig = graficar_respuesta_individual(t, y, title="Mi Sistema")
    """
    
    t = np.asarray(t, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    
    fig, ax = plt.subplots(figsize=figsize, dpi=100)
    
    # Respuesta
    ax.plot(t, y, linewidth=2.5, color=color, label='Respuesta', marker='o', markersize=2)
    
    # Referencia
    ax.axhline(y=yref, color='black', linestyle='--', linewidth=2, label=f'Referencia = {yref}', alpha=0.7)
    
    # Formato
    ax.set_xlabel('Tiempo [seg]', fontsize=12, fontweight='bold')
    ax.set_ylabel('Salida [unidades]', fontsize=12, fontweight='bold')
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=11)
    
    plt.tight_layout()
    
    return fig


def graficar_comparacion_metodos(
    resultados: Dict[str, Tuple[np.ndarray, np.ndarray]],
    yref: float = 1.0,
    title: str = "Comparación de Métodos de Sintonización",
    figsize: Tuple[int, int] = (14, 7)
) -> plt.Figure:
    """
    Compara múltiples métodos de sintonización en un solo gráfico.
    
    Parameters:
        resultados: Diccionario con {"ZN": (t, y), "CC": (t, y), ...}
        yref: Referencia
        title: Título
        figsize: Tamaño
    
    Returns:
        Figura con múltiples curvas
    
    Example:
        >>> t1 = np.linspace(0, 30, 300)
        >>> y_zn = 1.0 - np.exp(-0.2*t1) * np.cos(0.2*t1)
        >>> y_cc = 1.0 - 0.8*np.exp(-0.15*t1)
        >>> 
        >>> resultados = {
        ...     "ZN": (t1, y_zn),
        ...     "CC": (t1, y_cc)
        ... }
        >>> fig = graficar_comparacion_metodos(resultados)
    """
    
    fig, ax = plt.subplots(figsize=figsize, dpi=100)
    
    colors = {
        "ZN": "#0066CC",
        "CC": "#CC0000",
        "Crítica": "#FF9900",
        "Cohen": "#00CC66"
    }
    
    for i, (label, (t, y)) in enumerate(resultados.items()):
        color = colors.get(label, f'C{i}')
        ax.plot(t, y, linewidth=2.5, label=label, color=color, marker='o', markersize=2)
    
    # Referencia
    t_max = max(np.max(t) for t, y in resultados.values())
    ax.axhline(y=yref, color='black', linestyle='--', linewidth=2, label='Referencia', alpha=0.7)
    ax.fill_between([0, t_max], yref*0.98, yref*1.02, alpha=0.2, color='gray')
    
    ax.set_xlabel('Tiempo [seg]', fontsize=12, fontweight='bold')
    ax.set_ylabel('Salida [unidades]', fontsize=12, fontweight='bold')
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=11, loc='best')
    
    plt.tight_layout()
    
    return fig


if __name__ == "__main__":
    print("=" * 70)
    print("MÓDULO: Visualización de Respuestas")
    print("=" * 70)
    
    # ========== EJEMPLO 1: Comparación básica ==========
    print("\n" + "=" * 70)
    print("EJEMPLO 1: Comparación Planta vs Sistema Controlado")
    print("=" * 70)
    
    # Planta sin control (lenta)
    t_planta = np.linspace(0, 50, 300)
    y_planta = 1.0 - np.exp(-t_planta / 10)
    
    # Sistema con PID (rápido con overshoot)
    t_pid = np.linspace(0, 20, 200)
    y_pid = 1.0 - np.exp(-0.2*t_pid) * np.cos(0.2*t_pid)
    
    fig = graficar_respuestas(
        t_planta, y_planta,
        t_pid, y_pid,
        yref=1.0,
        title="Comparación: Sistema sin Control vs con PID",
        show_band=True
    )
    
    print("✓ Figura generada: comparacion_basica.png")
    fig.savefig('comparacion_basica.png', dpi=150, bbox_inches='tight')
    plt.close(fig)
    
    # ========== EJEMPLO 2: Diferentes referencias ==========
    print("\n" + "=" * 70)
    print("EJEMPLO 2: Referencia Escalada (50°C)")
    print("=" * 70)
    
    t_planta_50 = np.linspace(0, 50, 300)
    y_planta_50 = 50.0 * (1.0 - np.exp(-t_planta_50 / 10))
    
    t_pid_50 = np.linspace(0, 20, 200)
    y_pid_50 = 50.0 * (1.0 - np.exp(-0.2*t_pid_50) * np.cos(0.2*t_pid_50))
    
    fig = graficar_respuestas(
        t_planta_50, y_planta_50,
        t_pid_50, y_pid_50,
        yref=50.0,
        title="Control de Temperatura a Setpoint = 50°C",
    )
    
    print("✓ Figura generada: comparacion_50C.png")
    fig.savefig('comparacion_50C.png', dpi=150, bbox_inches='tight')
    plt.close(fig)
    
    # ========== EJEMPLO 3: Comparación de métodos ==========
    print("\n" + "=" * 70)
    print("EJEMPLO 3: Comparación de Métodos de Sintonización")
    print("=" * 70)
    
    t = np.linspace(0, 20, 300)
    
    # Ziegler-Nichols (más overshoot)
    y_zn = 1.0 - 1.2*np.exp(-0.2*t) * np.cos(0.25*t)
    
    # Cohen-Coon (menos overshoot)
    y_cc = 1.0 - 0.9*np.exp(-0.18*t)
    
    # Amortiguado crítico (sin overshoot)
    y_critica = 1.0 - (1.0 + 0.1*t)*np.exp(-0.15*t)
    
    resultados = {
        "Ziegler-Nichols": (t, y_zn),
        "Cohen-Coon": (t, y_cc),
        "Amortiguado crítico": (t, y_critica)
    }
    
    fig = graficar_comparacion_metodos(
        resultados,
        yref=1.0,
        title="Comparación: ZN vs Cohen-Coon vs Amortiguado Crítico"
    )
    
    print("✓ Figura generada: comparacion_metodos.png")
    fig.savefig('comparacion_metodos.png', dpi=150, bbox_inches='tight')
    plt.close(fig)
    
    # ========== EJEMPLO 4: Gráfico individual ==========
    print("\n" + "=" * 70)
    print("EJEMPLO 4: Gráfico Individual")
    print("=" * 70)
    
    t = np.linspace(0, 20, 300)
    y = 1.0 - np.exp(-0.1*t) * np.cos(0.12*t)
    
    fig = graficar_respuesta_individual(
        t, y,
        yref=1.0,
        title="Respuesta Individual del Sistema",
        color='#00CC66'
    )
    
    print("✓ Figura generada: individual.png")
    fig.savefig('individual.png', dpi=150, bbox_inches='tight')
    plt.close(fig)
    
    # ========== RESUMEN ==========
    print("\n" + "=" * 70)
    print("RESUMEN: Gráficos Generados")
    print("=" * 70)
    print("""
    ✓ comparacion_basica.png     - Planta vs PID (banda ±2%)
    ✓ comparacion_50C.png        - Control de temperatura
    ✓ comparacion_metodos.png    - ZN vs CC vs Crítico
    ✓ individual.png             - Respuesta individual
    
    Todos los gráficos son producción-ready para:
    - Presentaciones (PNG alta resolución)
    - Reportes (embed en PDF)
    - Aplicación Streamlit (st.pyplot)
    - Publicaciones (DPI ≥ 150)
    """)
