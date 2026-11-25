# Guion Oficial Ejecutivo: Búsqueda Evolutiva de Funciones de Activación mediante ELGP

**Centro de Investigación Científica y de Educación Superior de Ensenada (CICESE)**  
**Posgrado en Ciencias de la Computación**  
**Curso:** Inteligencia Computacional para Optimización (ICO 2026-3)  
**Instructor:** Dr. Jesús Guillermo Falcón-Cardona  
**Asesores:** Dr. Jesús Guillermo Falcón-Cardona & Dr. Carlos Brizuela  
**Expositor:** Rubén Rivera García  
**Duración Total Calibrada:** 15 – 18 minutos (~45 segundos promedio por diapositiva)  

---

## Diapositiva 1: Portada (30 s)
> "Muy buenos días, Dr. Guillermo Falcón y compañeros. Mi nombre es Rubén Rivera García, del Posgrado en Ciencias de la Computación. Presento la defensa del proyecto final: **'Búsqueda Evolutiva de Funciones de Activación mediante Programación Genética Lineal Epigenética y su Aplicación a la Geotermia'**, asesorado por el Dr. Guillermo Falcón y el Dr. Carlos Brizuela. Abordaremos la síntesis evolutiva de operadores no lineales, su interacción con normalización por lotes y un examen estadístico riguroso a gran escala."

---

## Diapositiva 2: Contenido (20 s)
> "La exposición se divide en 7 bloques: motivación en Deep Learning; formulación matemática y cromosómica de ELGP; infraestructura HPC y partición de datos; morfología descubierta frente a controles pareados; inferencia estadística y límite de Demšar; el Teorema de Absorción en Batch Normalization; y la inferencia masiva en 29.35 millones de píxeles en Baja California."

---

## Diapositiva 3: Papel de las Funciones de Activación en Deep Learning (45 s)
> "En cualquier red neuronal, la no linealidad $y = \varphi(Wx + b)$ es indispensable para evitar el colapso a una simple regresión lineal. Históricamente transitamos de funciones saturables como Sigmoide y Tanh, a la revolución de ReLU en 2010 por su gradiente positivo constante, hasta variantes suaves como GELU y Swish en Transformers modernos.  
> Sin embargo, como muestra la Tabla 1, **todas fueron diseñadas mediante heurística e intuición humana**. La pregunta científica es: ¿puede el cómputo evolutivo sintetizar funciones de activación competitivas de forma automatizada y sin sesgo humano?"  
* **Señalar:** Transición en Tabla 1 y pregunta al pie.

---

## Diapositiva 4: De la Heurística al Cómputo Evolutivo (45 s)
> "AutoML y la Programación Genética permiten evolucionar estructuras simbólicas mediante grafos o secuencias de instrucciones elementales, como mostraron AutoML-Zero en Google Brain y los trabajos de Bingham y Miikkulainen.  
> No obstante, enfrentamos tres grandes cuellos de botella:  
> 1. Un **espacio de búsqueda híbrido**, que combina topología simbólica discreta con constantes continuas;  
> 2. Un **alto costo computacional**, al requerir entrenar redes neuronales por cada evaluación;  
> 3. Y el **riesgo de sobreajuste**, cuando una función se especializa patológicamente en un solo conjunto de datos."  
* **Señalar:** Los tres retos en la columna derecha.

---

## Diapositiva 5: Objetivos y Preguntas de Investigación (40 s)
> "Para responder a esto, formulamos tres preguntas de investigación:  
> 1. **Estructura y Diversidad:** ¿Cómo cambia la morfología de la función al evolucionar con 1, 5 o 10 conjuntos de datos diversos?  
> 2. **Rigor Estadístico:** ¿Supera la función descubierta al estado del arte en conjuntos nunca vistos bajo pruebas pareadas con corrección de comparaciones múltiples?  
> 3. **Transferencia Real:** ¿Cómo generaliza la activación al transferirse a un problema de prospección geotérmica de 29.35 millones de píxeles?"

---

## Diapositiva 6: Representación Cromosómica: ELGP (50 s)
> "Nuestra propuesta es la **Programación Genética Lineal Epigenética (ELGP)**. Empleamos una máquina de registros lineal con 4 registros de trabajo ($r_0$ a $r_3$) y una longitud fija de $L=8$ instrucciones.  
> La innovación central es la **Operación Epigenética**: cada instrucción posee un peso continuo $e_k \in [0, 1]$, actualizando el registro de destino según:  
> $$r_{\text{dest}} \leftarrow (1 - e_k) r_{\text{dest}} + e_k \cdot \text{op}(r_{\text{src1}}, r_{\text{src2}})$$  
> Si $e_k = 0$, la instrucción actúa como bypass neutro; si $e_k = 1$, sobreescribe el registro; y con valores intermedios permite ponderar combinaciones lineales y pendientes fraccionarias, cerrando la brecha entre optimización discreta y continua."  
* **Señalar:** Bifurcación $(1-e_k)$ y $e_k$ en la Figura 2.

---

## Diapositiva 7: Dinámica Poblacional y Operadores (45 s)
> "Implementamos una estrategia evolutiva generacional $(\mu=30, \lambda=60)$ con 44 generaciones y un archivo élite externo.  
> La selección utiliza un **torneo de tamaño $k=3$ con reglas de factibilidad de Deb (2000)** para priorizar soluciones viables sin depender de parámetros de penalización artificiales.  
> Diseñamos variación dual: **mutación estructural discreta** ($p_m = 0.20$) para explorar topologías simbólicas, y **mutación epigenética continua** con ruido gaussiano $\mathcal{N}(0, 0.1^2)$ truncado a $[0, 1]$ para el ajuste fino de coeficientes, junto con cruza uniforme posicional."

---

## Diapositiva 8: Restricciones y Teorema de Factibilidad (55 s)
> "La función objetivo minimiza $f(\mathbf{x}) = -\bar{z}(\mathbf{x})$, donde $\bar{z}$ es la ganancia normalizada de AUC frente a ReLU en $M$ conjuntos de búsqueda. La estandarización $Z$-score impide que los datasets fáciles dominen la selección.  
> Incorporamos la restricción de no linealidad mínima: $g_1(\mathbf{x}) = 0.05 - (1 - R^2) \le 0$ en el intervalo $[-3, 3]$.  
> **Aportación teórica:** Demostramos formalmente que para cualquier función tipo LeakyReLU con razón de pendientes $\alpha$, la no linealidad es:  
> $$\text{NL}(\alpha) = \frac{(1-\alpha)^2}{5 + 6\alpha + 5\alpha^2} \ge 0.05 \implies \mathbf{\alpha \lesssim 0.371}$$  
> Esto garantiza analíticamente que la restricción $g_1$ elimina toda función cuasi-lineal degenerada, asegurando un quiebre angular no lineal."  
* **Señalar:** La desigualdad $\alpha \lesssim 0.371$.

---

## Diapositiva 9: Estrategia Evolutiva y Filtro Fast-Fail (40 s)
> "Para mitigar el costo de entrenamiento, incorporamos un filtro **Fast-Fail**: si en la primera época de entrenamiento el gradiente se desvanece o la función de pérdida diverge produciendo `NaN` o infinitos, la evaluación se aborta de inmediato asignando $f = +\infty$.  
> Esto permitió **podar más del 65% de los candidatos disfuncionales**, permitiendo concentrar el cómputo en evaluar redes MLP con Batch Normalization y optimizador Adam únicamente en soluciones prometedoras."

---

## Diapositiva 10: Infraestructura HPC en Clúster Ixachi (40 s)
> "Los experimentos se ejecutaron en el **Clúster Ixachi de CICESE** en nodos Intel Xeon Gold 5320 bajo Slurm, acumulando **41.1 horas de cómputo ininterrumpido** y 2,647 evaluaciones en ELGP.  
> Para garantizar máxima validez científica, ejecutamos dos controles pareados bajo idéntico presupuesto: una **Búsqueda Aleatoria pura** (11.7 h) y una **Ablación Epigenética** fijando $e_k = 1.0$ (12.3 h), más 5.4 horas de reevaluación rigurosa."  
* **Señalar:** La tabla de las 5 fases y presupuestos de cómputo.

---

## Diapositiva 11: Partición Estricta UCI (40 s)
> "Para evitar sesgos y fuga de información (*data leakage*), dividimos 19 conjuntos tabulares de la UCI en tres bancos totalmente disjuntos:  
> 1. **Búsqueda ($N=10$):** Datasets como Credit Card y Spambase en 3 pliegues para guiar la optimización.  
> 2. **Prueba Disjunto ($N=5$):** Conjuntos nunca vistos durante la evolución —Yeast, Steel, Sonar, Heart y Blood— evaluados bajo 10 semillas y 5 pliegues ($N=50$ corridas independientes).  
> 3. **Estabilidad ($N=4$):** Conjuntos con $\text{AUC} \ge 0.985$ apartados para evitar distorsiones por efecto techo."

---

## Diapositiva 12: Morfología y Redescubrimiento de LeakyReLU (55 s)
> "En la Diapositiva 12 observamos que con $N=10$ conjuntos, ELGP convergió a la expresión analítica:  
> $$\varphi(v) = 0.85 \cdot \bigl(0.25 \, v + 0.75 \max(0, v)\bigr) + 0.15$$  
> La pendiente positiva es $m_+ = 0.85$ y la negativa es $m_- = 0.2125$. La razón de pendientes es exactamente $\alpha = m_- / m_+ = 1 - e_k \approx \mathbf{0.2500}$, generada por el gen epigenético continuo $e_k = 0.7524$.  
> **ELGP redescubrió de forma autónoma una LeakyReLU ($\alpha = 0.25$)**.  
> Sin embargo, notamos algo intrigante: en la búsqueda, la ablación discreta parecía superar a ELGP, pero al reevaluarla con múltiples semillas, colapsa sustancialmente."  
* **Señalar:** La curva de convergencia y la tabla de Búsqueda vs. Reevaluación.

---

## Diapositiva 13: Controles Pareados y la 'Maldición del Ganador' (50 s)
> "Este fenómeno ilustra la **Maldición del Ganador en AutoML**: al seleccionar al mejor individuo entre más de 2,600 candidatos bajo una sola semilla, el algoritmo sobreajusta a la inicialización estocástica de pesos y al orden de los mini-batches.  
> Al reevaluar con 5 semillas independientes, todos pierden aptitud ($\Delta f > 0$), pero la **Ablación Discreta ($e_k=1$) sufre la mayor caída ($+0.4532$)** por su rigidez estructural. En contraste, la plasticidad epigenética de ELGP amortigua esta degradación.  
> Conclusión metodológica: evaluar AutoML con una sola semilla genera falsos descubrimientos."

---

## Diapositiva 14: Evaluación de Generalización en Datasets No Vistos (40 s)
> "Al evaluar en los 5 datasets disjuntos nunca vistos a lo largo de 50 corridas por método, el AUC promedio fue de **0.8701 para ReLU**, **0.8690 para ELGP**, **0.8697 para LeakyReLU**, **0.8665 para Búsqueda Aleatoria** y **0.8675 para Ablación**.  
> Las diferencias se encuentran en el tercer decimal. ELGP compite al nivel del estado del arte, pero sin una ventaja empírica evidente a simple vista."

---

## Diapositiva 15: Inferencia Estadística Pareada y Límite de Demšar (50 s)
> "Sometimos los resultados a pruebas $t$ pareadas y Wilcoxon con corrección secuencial de Holm.  
> Con $p_{\text{Holm}} = 1.0000$, **no se rechaza la hipótesis nula de equivalencia**; el intervalo de confianza al 95% de la diferencia es $[-0.0146, +0.0125]$.  
> Esto responde a un principio estadístico fundamental: como demostró Janez Demšar (2006), con $N=5$ datasets el $p$-valor mínimo teórico en Wilcoxon bilateral es $2/2^5 = 0.0625$, haciendo matemáticamente imposible rechazar $H_0$ al nivel $\alpha = 0.05$. Se requieren más de 30 datasets para detectar diferencias de esta magnitud."  
* **Señalar:** La columna de $p_{\text{Holm}} = 1.0000$ y el intervalo de confianza.

---

## Diapositiva 16: Teorema de Absorción en Batch Normalization (55 s)
> "La explicación definitiva a esta equivalencia es nuestro **Teorema de Absorción en BatchNorm**:  
> Si la función aprendida es $\tilde{\varphi}(v) = a \, \varphi(v) + b$ con $a=0.85$ y $b=0.15$, al pasar por la siguiente capa con normalización por lotes:  
> El sesgo aditivo $b$ se cancela exactamente en el numerador al restar la media del lote: $h - \mu_{\mathcal{B}}(h) = a (W\varphi - \mu_{\mathcal{B}})$.  
> Y el factor de escala $a$ se extrae de la varianza en el denominador: $\sqrt{a^2 \sigma^2 + \epsilon}$, cancelándose mutuamente:  
> $$\text{BN}(h) \approx \text{BN}(W \varphi)$$  
> **Conclusión:** BatchNorm absorbe completamente la escala y el sesgo afín. Por tanto, el espacio de hipótesis de ELGP es idéntico al de LeakyReLU ($\alpha=0.25$)."

---

## Diapositiva 17: Inferencia Espacial Masiva y Caso El Chinero (1 min)
> "Llevamos el modelo a la prospección geotérmica regional sobre **29.35 millones de píxeles** en el rift de Baja California, desde Cerro Prieto hasta San Felipe.  
> En las cartas cartográficas generadas con retícula WGS84, escala y norte, todas las arquitecturas delimitan con alta precisión el campo geotérmico de Cerro Prieto con $\text{AUC} > 0.999$.  
> En la zona no anómala de **El Chinero** observamos una discrepancia puntual de $\Delta = 0.3617$ entre ELGP ($P=0.5489$) y ReLU ($P=0.1287$). Sin embargo, LeakyReLU predijo $P=0.9106$. Siendo ELGP y LeakyReLU equivalentes por el Teorema de Absorción, la discrepancia en El Chinero no es de la función, sino producto de la **varianza estocástica de inicialización en SGD bajo una sola semilla**, sumada a la alta temperatura del desierto (54 °C)."  
* **Señalar:** Las 9 cartas cartográficas, el mapa de México y el panel Delta de El Chinero.

---

## Diapositiva 18: Conclusiones Principales (50 s)
> "En síntesis, aportamos cuatro conclusiones fundamentales:  
> 1. **Convergencia y Plasticidad:** Al escalar la diversidad de datos, ELGP convergió de formas cuasi-lineales a una lineal a tramos, donde $e_k = 0.7524$ ajustó autónomamente $\alpha \approx 0.25$, redescubriendo LeakyReLU.  
> 2. **Acotamiento Analítico:** La restricción $g_1 \le 0$ acota analíticamente $\alpha \lesssim 0.371$, impidiendo el colapso lineal.  
> 3. **Teorema de Absorción:** Demostramos que BatchNorm neutraliza traslaciones y escalamientos afines.  
> 4. **Rigor Estadístico:** Evidenciamos que la Maldición del Ganador y el sesgo mono-semilla invalidan muchas afirmaciones de AutoML; la inferencia pareada multisemilla es indispensable."

---

## Diapositiva 19: Trabajo Futuro (35 s)
> "Como trabajo futuro proponemos:  
> 1. Evaluar ELGP en arquitecturas sin capas de normalización afín, como PINNs o Transformers autorregresivos, donde las constantes afines sí influyen en el gradiente;  
> 2. Formular un frente de Pareto multiobjetivo explícito entre el AUC y la latencia computacional;  
> 3. Y explorar activaciones heterogéneas diferenciadas por profundidad de capa."

---

## Diapositiva 20: Cierre y Preguntas (20 s)
> "En la Diapositiva 20 se listan las referencias bibliográficas que sustentaron este trabajo.  
> Agradezco sinceramente la atención del Dr. Guillermo Falcón y de los presentes, y quedo a su disposición para su sesión de preguntas y comentarios. Muchas gracias."

---

# Respuestas Rápidas para el Jurado

* **P1: ¿Por qué convergió a LeakyReLU y no a Swish o GELU?**  
  > *"Por parsimonia y regularización: al optimizar sobre 10 datasets heterogéneos bajo la aptitud agregada $\bar{z}$, las funciones complejas sobreajustaban y eran penalizadas. LeakyReLU ($\alpha = 0.25$) ofreció el compromiso óptimo entre linealidad por tramos y generalización."*

* **P2: ¿Por qué $p_{\text{Holm}} = 1.0000$ en prueba si en la búsqueda $\bar{z}$ era alto?**  
  > *"Por la Maldición del Ganador: la aparente ventaja en búsqueda provino del sobreajuste a la semilla inicial en SGD. Al evaluar con 10 semillas independientes en datasets no vistos, la diferencia se disuelve. Además, según Demšar (2006), con $N=5$ datasets el $p$-valor mínimo de Wilcoxon es $0.0625$, imposibilitando rechazar $H_0$ a un nivel de significancia del 5%."*

* **P3: Si BatchNorm absorbe escala y sesgo, ¿sirvió de algo ELGP?**  
  > *"Sí: primero, descubrió autónomamente la razón óptima de pendientes $\alpha \approx 0.25$ respetando la restricción $g_1$; y segundo, aporta un resultado teórico clave para AutoML al demostrar formalmente que muchas pretendidas mejoras en la literatura quedan neutralizadas por capas de normalización."*

* **P4: ¿A qué se debió la discrepancia en El Chinero?**  
  > *"A la varianza estocástica de inicialización de pesos en SGD y a la extrema temperatura superficial de las arenas (54 °C). Como ELGP y LeakyReLU son matemáticamente equivalentes por el Teorema de Absorción, la discrepancia entre ellas confirma la necesidad de ensambles multisemilla en prospección geoespacial."*
