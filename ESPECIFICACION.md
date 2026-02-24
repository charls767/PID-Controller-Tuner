# Especificación de Software: Sintonizador de Controladores PID

## 1. Visión General
Sistema de análisis y sintonización de controladores PID basado en métodos clásicos de control automático. Permite a ingenieros diseñadores sintonizar parámetros de controladores (Kp, Ti, Td) a partir de funciones de transferencia del sistema utilizando métodos Ziegler–Nichols y Cohen–Coon, y visualizar el desempeño con y sin control.

---

## 2. Especificación Funcional (RF)

### RF1: Ingreso de Función de Transferencia
- **Descripción**: El usuario debe poder ingresar la función de transferencia del sistema en forma de coeficientes de polinomios.
- **Entrada**: Numerador y denominador como listas de coeficientes [an, an-1, ..., a0]
- **Validación**: 
  - Ambos polinomios deben ser válidos (no vacíos)
  - El denominador no puede ser cero
  - Se debe validar el orden relativo de los polinomios

### RF2: Sintonización Ziegler–Nichols
- **Descripción**: Calcular parámetros Kp, Ti, Td usando el método Ziegler–Nichols.
- **Entrada**: Función de transferencia G(s)
- **Salida**: Tupla (Kp, Ti, Td)
- **Métodos soportados**:
  - Método de respuesta al escalón
  - Método del lazo cerrado (oscilaciones sostenidas)
- **Validaciones**: Detectar si el sistema permite aplicar el método sin inestabilidad

### RF3: Sintonización Cohen–Coon
- **Descripción**: Calcular parámetros Kp, Ti, Td usando el método Cohen–Coon.
- **Entrada**: Función de transferencia G(s)
- **Salida**: Tupla (Kp, Ti, Td)
- **Características**: Aplicable a sistemas con retardo de transporte

### RF4: Simulación de Respuesta del Sistema
- **Descripción**: Simular y graficar respuesta al escalón unitario.
- **Salidas**:
  - Respuesta sin controlador
  - Respuesta con controlador PID (para cada conjunto de parámetros)
- **Tiempo de simulación**: Configurable, mínimo 5 segundos o tiempo necesario para estabilización

### RF5: Cálculo de Métricas de Desempeño
- **Tiempo de establecimiento (ts)**: Tiempo para entrar en banda ±5% del valor final
- **Sobreimpulso (Mp)**: Máximo porcentaje de sobrepaso sobre el valor final
- **Error en estado estacionario (ess)**: Diferencia final respecto a referencia
- **Tiempo de levantamiento (tr)**: Tiempo de 10% a 90% del valor final

### RF6: Visualización Gráfica
- **Gráficos interactivos en Streamlit**:
  - Comparación de respuestas (sin control vs con PID)
  - Tabla de métricas de desempeño
  - Parámetros del controlador PID sintonizado
  - Diagrama de polos y ceros (opcional avanzado)

### RF7: Exportación de Resultados
- **Formatos**: CSV con parámetros y métricas
- **Exportación de gráficos**: PNG de la respuesta al escalón

---

## 3. Especificación No Funcional (RNF)

### RNF1: Rendimiento
- **Tiempo de cálculo**: Sintonización en < 2 segundos
- **Simulación**: Gráficos actualizables en < 3 segundos
- **Responsividad**: Interfaz reactiva con feedback inmediato

### RNF2: Usabilidad
- **Interfaz intuitiva**: Sin necesidad de instalación adicional
- **Ayuda integrada**: Tooltips y descripción de métodos
- **Idioma**: Español principalmente; estructura preparada para multiidioma

### RNF3: Confiabilidad
- **Manejo de errores**: Mensajes claros si los parámetros son inválidos
- **Validación robusta**: Prevenir estados inconsistentes
- **Pruebas de casos extremos**: Sistemas inestables, órdenes altas

### RNF4: Escalabilidad
- **Arquitectura modular**: Fácil agregar nuevos métodos de sintonización
- **Separación frontend-backend**: Independencia entre lógica de control y presentación

### RNF5: Mantenibilidad
- **Documentación del código**: Docstrings en español e inglés
- **Pruebas unitarias**: Cobertura mínima 80%
- **Versionamiento**: Seguir SemVer

### RNF6: Compatibilidad
- **Python**: 3.8+
- **Librerías**: python-control, numpy, matplotlib, streamlit
- **Plataformas**: Windows, macOS, Linux

---

## 4. Restricciones y Suposiciones

### Restricciones
- Sistemas lineales invariantes en el tiempo (LTI)
- Solo entradas de escalón unitario para simulación
- Máximo orden 10 en numerador/denominador
- Métodos de sintonización orientados a control PID estándar

### Suposiciones
- El usuario entiende control automático básico
- Funciones de transferencia bien definidas y físicamente realizables
- No se consideran retardos de transporte en la versión 1.0

---

## 5. Criterios de Aceptación

- [ ] Ingresa G(s) y calcula Kp, Ti, Td correctamente
- [ ] Gráficos comparativos correctos (sin control vs con PID)
- [ ] Métricas calculadas con precisión (ts, Mp, ess, tr)
- [ ] Interfaz responde en menos de 3 segundos
- [ ] Manejo robusto de entradas inválidas
- [ ] Exportación de resultados en CSV y PNG
- [ ] Documentación y pruebas completas

---

## 6. Priorización (MoSCoW)

- **Must Have** (Lanzamiento v1.0):
  - RF1, RF2, RF3, RF4, RF5, RF6

- **Should Have** (v1.1):
  - RF7, diagrama de polos/ceros
  - Método del lugar de raíces discreto

- **Could Have** (Futuro):
  - Multiidioma completo
  - Tolerancias personalizadas en métricas
  - Exportación a MATLAB/Simulink

- **Won't Have** (v1.0):
  - Control adaptativo
  - Sistemas no lineales
  - Retardos de transporte complejos
