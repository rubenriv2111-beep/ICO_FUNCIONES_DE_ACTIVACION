# Búsqueda Evolutiva de Funciones de Activación mediante Programación Genética Lineal Epigenética (ELGP)
### *Observaciones sobre Diversidad de Datos, Comparación Estadística y Transferencia Geotérmica*

**Centro de Investigación Científica y de Educación Superior de Ensenada (CICESE)**  
**Posgrado en Ciencias de la Computación**  
**Curso:** Inteligencia Computacional para Optimización (ICO 2026-3)  
**Profesor:** Dr. Jesús Guillermo Falcón-Cardona  
**Asesores:** Dr. Jesús Guillermo Falcón-Cardona & Dr. Carlos Brizuela  
**Autor:** Rubén Rivera García (`ruben.rivera@cicese.edu.mx`)  
**Fecha:** Noviembre de 2026  

---

## 1. Resumen del Proyecto

Este repositorio contiene el código fuente, la formulación matemática y los experimentos del proyecto final de **Inteligencia Computacional para Optimización (ICO)**. 

El trabajo investiga la síntesis evolutiva de funciones de activación en redes neuronales profundas mediante **Programación Genética Lineal Epigenética (ELGP)**. Se formuló un problema de **optimización mono-objetivo con restricciones** basado en la aptitud normalizada agregada ($\bar{z}$) frente a una red base ReLU sobre múltiples conjuntos de datos de UCI Machine Learning Repository, resuelto mediante una estrategia generacional $(\mu=30, \lambda=60)$ con las **reglas de factibilidad de Deb (2000)**, selección por torneo ($k=3$) y archivo élite.

### Principales Hallazgos y Aportaciones:
1. **Convergencia Analítica a LeakyReLU ($\alpha = 0.25$):** Con $N=10$ conjuntos de entrenamiento (2,647 evaluaciones efectivas en el clúster Ixachi de CICESE), el algoritmo convergió a:
   $$\varphi(v) = 0.85 \cdot \bigl(0.25 \, v + 0.75 \, \max(0, v)\bigr) + 0.15$$
   donde la razón de pendientes $\alpha = 0.25$ emerge analíticamente del peso epigenético continuo $e_k = 0.7524$ sobre el bloque $\max(0, v)$.
2. **Efecto de la Restricción $g_1$:** Se demuestra analíticamente que la restricción de no linealidad mínima impone $\alpha \lesssim 0.371$, forzando un quiebre angular marcado y descartando funciones cuasi-lineales.
3. **Maldición del Ganador en Controles:** En la reevaluación multisemilla (5 semillas), tanto ELGP como los controles pareados (Búsqueda Aleatoria y Ablación $e_k=1.0$) experimentaron una pérdida sustancial de aptitud, evidenciando sobreajuste a la semilla estocástica de exploración.
4. **Generalización Estadística Inconclusa:** En 5 conjuntos de prueba disjuntos no vistos, la prueba pareada con ajuste secuencial de Holm arrojó $p_{\text{Holm}} = 1.0000$ en todas las comparaciones. Con $n=5$ datasets, los intervalos de confianza del 95% no descartan diferencias de $\pm 0.013$ ni distinguen una red lineal.
5. **Teorema de Absorción en BatchNorm y Transferencia Geotérmica:** Se demuestra algebraicamente que $\text{BatchNorm}(a\varphi(v) + b) = \text{BatchNorm}(\varphi(v))$, volviendo a ELGP representacionalmente idéntica a LeakyReLU ($\alpha = 0.25$). En la cartografía ráster de Baja California (29.35 millones de píxeles), la discrepancia en puntos como El Chinero ($\Delta = 0.3617$) es compatible con la varianza estocástica de inicialización en SGD bajo una sola semilla.

---

## 2. Instrucciones de Uso y Reproducción en Plataformas Linux

El proyecto fue diseñado para ejecutarse de manera autónoma y reproducible en cualquier distribución de Linux (Ubuntu, Debian, Fedora, Arch Linux, CentOS, WSL2) o clústeres de supercómputo basados en Linux (Slurm / PBS).

### Paso 1: Clonar el Repositorio
```bash
git clone https://github.com/rubenriv2111-beep/ICO_FUNCIONES_DE_ACTIVACION.git
cd ICO_FUNCIONES_DE_ACTIVACION
```

### Paso 2: Creación del Entorno Virtual e Instalación de Dependencias
Se recomienda utilizar Python 3.10 o 3.11:
```bash
# Crear entorno virtual aislado
python3 -m venv venv_elgp
source venv_elgp/bin/activate

# Actualizar pip e instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt
```

### Paso 3: Ejecución del Jupyter Notebook Maestro (Opción Recomendada)
Todo el flujo analítico, las demostraciones matemáticas y los gráficos están contenidos de forma autónoma en el notebook:
```bash
jupyter notebook ELGP_Optimizacion_Funciones_Activacion.ipynb
```
*Si se ejecuta en un servidor remoto o instancia sin interfaz gráfica (headless):*
```bash
# Ejecutar y re-generar el notebook guardando las salidas
jupyter nbconvert --to notebook --execute ELGP_Optimizacion_Funciones_Activacion.ipynb --output ELGP_Optimizacion_Funciones_Activacion.ipynb
```

### Paso 4: Ejecución Modular vía Línea de Comandos (Scripts CLI)
Para reproducir la búsqueda evolutiva completa o lanzar tareas en un gestor de trabajos Slurm (nodo Linux con GPU/CPU):
```bash
# Ejecutar búsqueda ELGP con estrategia (mu=30, lambda=60)
python src/main_elgp.py --mu 30 --lambda 60 --evals 2647

# Evaluar transferencia geoespacial y absorción en BatchNorm
python src/transferir_activaciones.py
```

---

## 3. Estructura del Repositorio

```
ICO_FUNCIONES_DE_ACTIVACION/
│
├── ELGP_Optimizacion_Funciones_Activacion.ipynb # Jupyter Notebook MAESTRO ejecutable con salidas completas
├── README.md                                    # Guía técnica maestra de reproducibilidad en Linux
├── requirements.txt                             # Dependencias estrictas del entorno
├── .gitignore                                   # Filtro estricto para excluir cachés y temporales
│
├── src/                                         # Código fuente modular en Python
│   ├── elgp_config.py                           # Parámetros globales, operadores continuos y división protegida
│   ├── elgp_individuo.py                        # Clase Individuo, no-linealidad g1 y reglas de Deb (2000)
│   ├── elgp_datos.py                            # Gestión de datasets UCI y protocolo de entrenamiento
│   ├── elgp_evolucion.py                        # Estrategia evolutiva (mu, lambda), archivo élite y controles
│   ├── main_elgp.py                             # Script de ejecución CLI para clústeres HPC (Slurm)
│   └── transferir_activaciones.py               # Demostración de absorción en BatchNorm y métricas
│
├── figures/                                     # Figuras de alta calidad
│   ├── convergencia_comparativa.png             # Curvas de convergencia pareadas (2,647 evals)
│   └── comparativa_mapas_activaciones_qgis.png  # Cartografía regional comparativa en QGIS
│
├── results/                                     # Registros numéricos y metadatos de soporte
│   ├── metricas_geotermia_elgp.json             # Métricas en prueba geotérmica
│   ├── metricas_comparativa_activaciones_qgis.json # Comparativa multimodelo
│   └── ecuacion_ganadora.txt                    # Expresión ganadora del ensamble
│
└── documentacion/                               # Documentos formales del posgrado
    ├── Reporte_Final_ELGP_ICO.tex               # Código fuente del artículo científico en LaTeX
    └── Presentacion_ICO_Ruben Rivera Garcia.pptx# Diapositivas oficiales de la exposición
```

---

## 4. Formulación del Problema y Teoremas Analíticos

### 4.1 Problema de Optimización Mono-Objetivo con Restricciones
$$\min_{\mathbf{x}} f(\mathbf{x}) = -\bar{z}(\mathbf{x}) = -\frac{1}{M}\sum_{j=1}^M \frac{\text{AUC}_j(\mathbf{x}) - \mu_j}{\sigma_j}$$
$$\text{sujeto a:} \quad g_1(\mathbf{x}) = \epsilon_{\text{nl}} - \text{NL}(\mathbf{x}) \le 0, \quad \text{con } \epsilon_{\text{nl}} = 0.05$$
donde $\text{NL}(\mathbf{x}) = 1 - R^2$ proviene de la regresión lineal de $\varphi_{\mathbf{x}}(v)$ contra $v$ sobre una malla uniforme en $[-3, 3]$.

### 4.2 Teorema de Factibilidad para LeakyReLU
Para una función $\text{LeakyReLU}$ con pendiente negativa relativa $\alpha \in [0, 1]$ evaluada en $[-L, L]$:
$$\text{NL}(\alpha) = \frac{(1-\alpha)^2}{5 + 6\alpha + 5\alpha^2} \ge 0.05 \implies \mathbf{\alpha \lesssim 0.371}$$
Este resultado prueba analíticamente que la restricción $g_1$ descarta de manera rigurosa cualquier función cuasi-lineal.

### 4.3 Teorema de Absorción en Batch Normalization
Para cualquier transformación afín de la activación $\tilde{\varphi}(v) = a \, \varphi(v) + b$ con $a > 0$:
$$\mu_{\mathcal{B}} = a \, \mu_{\varphi} + b, \quad \sigma^2_{\mathcal{B}} = a^2 \, \sigma^2_{\varphi}$$
$$\widehat{\tilde{\varphi}}(v) = \frac{(a\varphi(v) + b) - (a\mu_\varphi + b)}{\sqrt{a^2\sigma^2_\varphi + \epsilon}} = \frac{a(\varphi(v) - \mu_\varphi)}{a\sqrt{\sigma^2_\varphi + \epsilon/a^2}} \approx \widehat{\varphi}(v)$$
Por lo tanto, la escala global $0.85$ y el sesgo $0.15$ descubiertos por ELGP son neutralizados en redes con normalización por lotes.

---

## 5. Tablas de Resultados Experimentales

### 5.1 Generalización en Conjuntos Disjuntos (50 Corridas: 10 Semillas $\times$ 5 Folds)
| Conjunto de Prueba | Base (ReLU) | ELGP ($\bar{z}$) | Random Search | Ablación ($e_k=1.0$) |
|:-------------------|:-----------:|:----------------:|:-------------:|:--------------------:|
| Bank Marketing     | 0.9348      | 0.9348           | 0.9348        | 0.9348               |
| Blood Transfusion  | 0.7410      | 0.7410           | 0.7410        | 0.7410               |
| Sonar              | 0.8805      | 0.8805           | 0.8805        | 0.8805               |
| Spambase           | 0.9856      | 0.9856           | 0.9856        | 0.9856               |
| Yeast              | 0.7182      | 0.7182           | 0.7182        | 0.7182               |
| **Promedio AUC**   | **0.8520**  | **0.8520**       | **0.8520**    | **0.8520**           |

### 5.2 Pruebas de Hipótesis Pareadas (Wilcoxon + Holm-Bonferroni, $\alpha = 0.05$)
| Comparación Pareada | Estadístico $W$ | $p$-valor Crudo | $p$-valor Ajustado (Holm) | Decisión Estadística |
|:--------------------|:---------------:|:---------------:|:-------------------------:|:--------------------:|
| ELGP vs ReLU        | 0.0             | 1.0000          | 1.0000                    | No Rechazar $H_0$    |
| ELGP vs Random      | 0.0             | 1.0000          | 1.0000                    | No Rechazar $H_0$    |
| ELGP vs Ablación    | 0.0             | 1.0000          | 1.0000                    | No Rechazar $H_0$    |

---

## 6. Requisitos y Dependencias

- Python $\ge$ 3.10
- PyTorch $\ge$ 2.0.0
- NumPy $\ge$ 1.24.0
- SciPy $\ge$ 1.10.0
- Scikit-Learn $\ge$ 1.2.0
- Matplotlib $\ge$ 3.7.0
- Pandas $\ge$ 2.0.0
- Jupyter Notebook / nbconvert
