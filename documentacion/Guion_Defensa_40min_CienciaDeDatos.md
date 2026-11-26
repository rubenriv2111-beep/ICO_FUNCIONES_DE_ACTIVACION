# Guion Maestro de Exposición y Defensa Oral (40 Minutos)
## Clasificación Geoespacial Multivariada para la Identificación de Zonas Geotérmicas

**Programa:** Posgrado en Ciencias de la Computación, CICESE  
**Asignatura:** Ciencia de Datos (Semestre 2026-3)  
**Autor y Expositor:** Rubén Rivera García  
**Profesores y Evaluadores:** Dr. Irvin Hussein López Nava, M.C. Joan Raygoza Romero, Dr. Jesús Guillermo Falcón-Cardona  
**Duración Total Calibrada:** 40 minutos (distribuidos en 10 diapositivas / módulos temáticos)  
**Ritmo sugerido:** ~115 a 125 palabras por minuto, tono académico de defensa de posgrado, analítico, seguro y orientado a la física del problema.

---

## Estructura y Distribución Temporal (Cronograma de 40 Minutos)

| Diapositiva | Título / Tema Principal | Tiempo Estimado | Minuto Acumulado |
| :--- | :--- | :---: | :---: |
| **Diapositiva 1** | Portada e Introducción Institucional | 2.5 min | 00:00 – 02:30 |
| **Diapositiva 2 (Pág. 1)** | Contexto y Desafío: Geotermia, Desbalance y Preguntas de Investigación | 4.5 min | 02:30 – 07:00 |
| **Diapositiva 3 (Pág. 2)** | Perfil del Dataset, Curaduría Multifuente e Ingeniería de Características | 4.5 min | 07:00 – 11:30 |
| **Diapositiva 4 (Pág. 3)** | Arquitectura Metodológica y Protocolos de Validación Espacial | 4.5 min | 11:30 – 16:00 |
| **Diapositiva 5 (Pág. 4)** | Resultados Globales: Colapso del Falso Optimismo y Paridad Lineal | 5.0 min | 16:00 – 21:00 |
| **Diapositiva 6 (Pág. 5)** | Desglose por Pliegue e Inestabilidad Patológica del Umbral de Youden | 5.0 min | 21:00 – 26:00 |
| **Diapositiva 7 (Pág. 6)** | Diagnósticos de Control: Coordenadas Puras, Placebos y Firmas Hídricas | 5.0 min | 26:00 – 31:00 |
| **Diapositiva 8 (Pág. 7)** | Inferencia Regional, Área de Aplicabilidad (AOA) y El Chinero | 4.5 min | 31:00 – 35:30 |
| **Diapositiva 9 (Pág. 8)** | Conclusiones Centrales y las Seis Limitaciones Metodológicas | 3.5 min | 35:30 – 39:00 |
| **Diapositiva 10** | Referencias Bibliográficas y Apertura de Preguntas | 1.0 min | 39:00 – 40:00 |

---

## Diapositiva 1: Portada e Introducción Institucional
* **Tiempo asignado:** 2 minutos y 30 segundos (Minuto 00:00 a 02:30)
* **Objetivo:** Presentar formalmente el proyecto, establecer el marco institucional del CICESE, definir el tono crítico-diagnóstico del trabajo y enunciar la tesis central: *el aprendizaje automático en geociencias debe auditarse contra la geografía para no confundir autocorrelación con señales físicas reales*.

### Guion en Voz Alta:
> *"Muy buenos días, estimados profesores Dr. Irvin Hussein López Nava, M.C. Joan Raygoza Romero, Dr. Guillermo Falcón-Cardona, compañeros y miembros del comité evaluador.*  
> 
> *Mi nombre es Rubén Rivera García, estudiante del Posgrado en Ciencias de la Computación de este Centro de Investigación Científica y de Educación Superior de Ensenada (CICESE). El día de hoy tengo el honor de presentar ante ustedes la defensa del proyecto final de la asignatura de Ciencia de Datos, titulado formalmente: **'Clasificación geoespacial multivariada para la identificación de zonas geotérmicas: Alcances y Limitaciones del Aprendizaje Automático Regional'**.*
> 
> *Tradicionalmente, la literatura de aprendizaje automático aplicado a las ciencias de la Tierra ha seguido una narrativa triunfalista, reportando con frecuencia precisiones y áreas bajo la curva superiores al 98 o 99% mediante modelos complejos de ensamble o redes neuronales profundas. Sin embargo, cuando estos modelos se trasladan al terreno real para guiar inversiones de millones de dólares, la tasa de éxito colapsa drásticamente.*
> 
> *El trabajo que hoy expongo no fue concebido como un ejercicio ingenuo de ajuste de hiperparámetros o maximización artificial de métricas, sino como un **estudio forense y metodológico riguroso**. Nuestro propósito central ha sido desarmar la 'ilusión predictiva' que se genera cuando se aplican algoritmos de clasificación estándar a datos espaciales continuos en el Rift de Baja California, determinando con precisión matemática qué parte de las predicciones proviene de relaciones físicas del subsuelo y qué parte es un artefacto derivado de la proximidad geográfica, la actividad industrial humana en superficie o defectos propios de la cartografía pública.*
> 
> *A lo largo de los próximos 38 minutos, revisaremos en detalle los datos, la experimentación pareada, el descubrimiento de la paridad de modelos lineales y la auditoría espacial que nos permitió reevaluar por completo anomalías térmicas regionales históricas como la de El Chinero."*

---

## Diapositiva 2 (Pág. 1): Contexto y Desafío: Geotermia y Retos de Ciencia de Datos
* **Tiempo asignado:** 4 minutos y 30 segundos (Minuto 02:30 a 07:00)
* **Objetivo:** Contextualizar la importancia energética y económica de la geotermia, definir los 3 grandes retos de ciencia de datos (cobertura ínfima, desbalance extremo y la Primera Ley de Tobler), y presentar con precisión las 3 Preguntas de Investigación formales ($P_1, P_2, P_3$).
* **Qué señalar en pantalla:**
  - El ícono del pozo y el costo de 5 a 10 millones de USD.
  - La balanza del desbalance de clases (0.5% vs 99.5%).
  - La antena/satélite y la fórmula conceptual de Tobler.
  - Las tres preguntas de investigación en el panel derecho.

### Guion en Voz Alta:
> *"Comencemos situando el problema físico y económico en la Diapositiva 2.*  
> 
> *La energía geotérmica representa uno de los pilares más atractivos de la transición energética moderna. A diferencia de la energía solar o eólica, que son inherentemente intermitentes y dependen de ciclos diurnos o condiciones atmosféricas, la geotermia ofrece **energía limpia de carga base**: una generación continua, constante y predecible las 24 horas del día durante los 365 días del año.*
> 
> *Sin embargo, el talón de Aquiles de la geotermia radica en su fase exploratoria. La perforación profunda en roca consolidada y ambientes hidrotermales hostiles demanda inversiones de capital colosales: perforar un solo pozo exploratorio de 2.5 a 3.5 kilómetros de profundidad oscila entre los **5 y 10 millones de dólares**. Lo crítico es que, en etapas de frontera sin geofísica invasiva previa, la probabilidad de perforar un 'pozo seco' o estéril supera con frecuencia el 50%. En consecuencia, cualquier herramienta analítica o de ciencia de datos que permita guiar la perforación con alta confiabilidad tiene un valor económico monumental.*
> 
> *No obstante, cuando el científico de datos intenta modelar este problema mediante aprendizaje supervisado, se estrella contra tres murallas metodológicas:*
> 
> *1. **Cobertura territorial ínfima:** En todo el Valle de Mexicali y el rift continental, el Complejo Geotérmico Cerro Prieto es el **único campo activo y comercialmente probado**. Su polígono superficial abarca aproximadamente 22.33 km², lo cual representa menos del 0.075% de los casi 30,000 km² de la cuenca continental. Esto da origen al denominado **Single-Field Problem (Problema del Campo Único)**: estamos entrenando algoritmos con un solo ejemplo positivo real.*
> 
> *2. **Desbalance de clases masivo:** La relación natural entre terreno con anomalía comercial y terreno de fondo estéril es de más de 1 contra 1,300.*
> 
> *3. **Autocorrelación espacial y la Ley de Tobler:** En 1970, Waldo Tobler formuló la Primera Ley de la Geografía: 'Todas las cosas están relacionadas entre sí, pero las cosas cercanas están más relacionadas que las cosas lejanas'. Los datos satelitales, topográficos y geofísicos no son variables aleatorias independientes e idénticamente distribuidas (i.i.d.). Dos píxeles vecinos a 30 metros de distancia comparten casi idéntica temperatura, elevación y campo magnético.*
> 
> *Si aplicamos una partición aleatoria convencional tipo 70/30, como hace la gran mayoría de la literatura, estamos colocando celdas casi gemelas en entrenamiento y en prueba, lo que constituye una **fuga masiva de información por autocorrelación espacial**.*
> 
> *Para someter este fenómeno a un análisis científico formal, formulamos tres preguntas de investigación concretas:*
> - **Pregunta 1 ($P_1$):** ¿En qué medida las variables físicas y ambientales permiten identificar las zonas geotérmicas de Cerro Prieto independientemente de los patrones de proximidad espacial al campo?
> - **Pregunta 2 ($P_2$):** ¿En qué magnitud la validación aleatoria sobreestima el desempeño predictivo respecto a una validación espacial por bloques contiguos con una zona de exclusión de 500 metros?
> - **Pregunta 3 ($P_3$):** ¿Aportan los modelos complejos de caja negra —como Random Forest o redes neuronales profundas— mejoras estadísticamente significativas en discriminación, calibración de probabilidades y estabilidad de umbrales frente a una regresión logística regularizada con interacciones físicas?"*

---

## Diapositiva 3 (Pág. 2): Perfil del Dataset, Curaduría Multifuente e Ingeniería de Características
* **Tiempo asignado:** 4 minutos y 30 segundos (Minuto 07:00 a 11:30)
* **Objetivo:** Explicar el diseño muestral (89,815 celdas a 30 m), el control de calidad anti-fuga (estratificación por bandas de distancia concéntricas B1, B2, B3), las fuentes institucionales (INEGI, USGS, SGM), la corrección del datum geodésico de 197.8 metros y los descriptores físicos $R_{TE}$ e $I_{TT}$.
* **Qué señalar en pantalla:**
  - La fila del dominio: 24,814 celdas positivas vs. 65,001 negativas (21,667 por banda B1, B2, B3).
  - El recuadro de blindaje: CERO SMOTE, cero manipulación de pesos de clase.
  - La corrección geodésica de NAD27 a WGS84 (197.8 m).
  - Las ecuaciones de $R_{TE}$ e $I_{TT}$ al pie de la tabla.

### Guion en Voz Alta:
> *"Pasemos a la Diapositiva 3, donde detallamos la arquitectura y curaduría de la matriz de datos.*  
> 
> *Para construir un conjunto de entrenamiento y evaluación representativo, delimitamos una malla regular en coordenadas proyectadas UTM Zona 11N bajo el elipsoide WGS84, con una resolución espacial de 30 metros por píxel. La base de datos reúne **89,815 celdas**.*
> 
> *Prestemos atención al diseño del muestreo negativo: no extrajimos puntos al azar en todo el estado, porque eso haría trivial la clasificación (un modelo aprendería simplemente a distinguir la sierra de la costa). En su lugar, dividimos el espacio no geotérmico en tres bandas concéntricas estandarizadas con exactamente **21,667 celdas por banda**:*
> - **Banda 1 (B1, Inmediata):** De 500 metros a 2 kilómetros de distancia del perímetro de Cerro Prieto.
> - **Banda 2 (B2, Intermedia):** De 2 a 5 kilómetros.
> - **Banda 3 (B3, Regional de Llanura):** A más de 5 kilómetros de distancia, extendiéndose hasta la llanura aluvial y San Felipe.
> 
> *Nótese un aspecto de integridad metodológica cardinal: **no aplicamos SMOTE ni sobremuestreo sintético**. Trabajos previos suelen generar vectores ficticios interpolados en el hiperespacio euclidiano; sin embargo, en un sistema de información geográfica, inventar observaciones georreferenciadas que no existen físicamente en las coordenadas correspondientes es una pésima práctica científica que destruye la calibración probabilística real. Asimismo, no alteramos los pesos de clase (`class_weight`) para permitir que la función sigmoide final conserve las probabilidades a posteriori calibradas según el diseño muestral.*
> 
> *En cuanto a las covariables físicas, integramos datos de cuatro agencias científicas oficiales:*
> 1. **Relieve (INEGI):** Continuo de Elevaciones Mexicano (CEM 3.0), del cual derivamos elevación ortométrica ($z$) y pendiente topográfica en grados.
> 2. **Superficie Satelital (USGS / NASA Landsat 9):** Extrajimos Temperatura Superficial Terrestre diurna (LST) del sensor TIRS-2 y el Índice de Vegetación de Diferencia Normalizada (NDVI) del sensor OLI-2, correspondientes a una escena estival despejada. De manera crucial, calculamos el índice modificado de agua MNDWI propuesto por Xu (2006); no lo usamos para entrenar, sino como variable de control para auditar si los modelos estaban detectando calor profundo o simplemente las lagunas de salmuera de la planta de CFE.
> 3. **Estructura Tectónica (Servicio Geológico Mexicano):** Digitalizamos las fallas geológicas regionales a escala 1:250,000. Aquí descubrimos y corregimos un error crítico presente en proyectos previos: las cartas originales del SGM se encontraban en el datum histórico norteamericano NAD27. Al reproyectarlas rigurosamente a WGS84, **resolvimos un desplazamiento espacial medio de 197.8 metros**. Si no se realiza esta corrección, los algoritmos miden distancias a fracturas desplazadas dos cuadras respecto a la falla real.
> 4. **Geofísica de Basamento:** Anomalía aeromagnética residual en nanoteslas (nT) del mosaico aeromagnético del SGM.
> 
> *Finalmente, en lugar de recurrir a transformaciones ciegas, adoptamos la formulación de ingeniería de características propuesta por Wang et al. (2025) en Energy, inyectando dos relaciones no lineales controladas:*
> - El **Ratio Termo-Estructural ($R_{TE}$):** que divide la temperatura superficial entre el logaritmo natural de la distancia a fallas más 10 metros: $R_{TE} = \frac{\text{LST}}{\ln(d + 10.0)}$.
> - El **Índice Topo-Térmico ($I_{TT}$):** que relaciona la temperatura con la cota orográfica: $I_{TT} = \frac{\text{LST}}{z + 50.0}$.
> *Estos índices permiten que un modelo lineal interprete que una alta temperatura solo es indicativa de geotermia si ocurre a baja cota y adyacente a una fractura tectónica permeable."*

---

## Diapositiva 4 (Pág. 3): Arquitectura Metodológica y Protocolos de Validación Espacial
* **Tiempo asignado:** 4 minutos y 30 segundos (Minuto 11:30 a 16:00)
* **Objetivo:** Describir la tubería de modelado en 4 pasos, contrastar matemáticamente el Protocolo A (aleatorio estratificado) frente al Protocolo B (espacial en 5 bloques Norte-Sur con buffer de exclusión de 500 m) y justificar el uso de PR-AUC, Brier Score y el Área de Aplicabilidad (AOA).
* **Qué señalar en pantalla:**
  - Los 4 bloques numerados del diagrama.
  - El esquema gráfico del Protocolo B: los 5 bloques contiguos y el buffer de 500 m.
  - La definición del ensamble de 3 semillas para RF y MLP.
  - El índice de disimilitud (DI $\le 2.13$) para el AOA.

### Guion en Voz Alta:
> *"La Diapositiva 4 ilustra la arquitectura experimental que diseñamos para responder con rigor a las preguntas de investigación, organizada en cuatro fases:*
> 
> *En la **Fase 1 (Insumos y Blindaje)**, establecimos un aislamiento absoluto: el escalador `StandardScaler` se ajustó estricta y exclusivamente sobre el conjunto de entrenamiento de cada pliegue, proyectándolo después sobre validación y prueba para garantizar cero fuga de distribución.*
> 
> *En la **Fase 2**, implementamos el corazón experimental de nuestra tesis: **la comparación pareada entre dos protocolos de validación**.*
> - **Protocolo A (Validación Aleatoria Estratificada):** Es la partición clásica 70% entrenamiento, 15% validación y 15% prueba. Este protocolo ignora por completo la ubicación espacial de los píxeles; como los puntos de entrenamiento y prueba están intercalados en el espacio, este protocolo mide principalmente la capacidad de interpolación del modelo.
> - **Protocolo B (Validación Cruzada Espacial por Bloques con Buffer de 500 m):** Aquí dividimos el polígono de Cerro Prieto en **cinco sectores geográficos contiguos orientados de norte a sur**. En cada iteración, un sector completo se reserva exclusivamente como conjunto de prueba, y se entrenan los modelos con los cuatro sectores restantes. Pero además, introdujimos un **buffer de exclusión perimetral de 500 metros** alrededor del bloque de prueba: ninguna celda dentro de esa franja de medio kilómetro puede entrar al entrenamiento. Esto corta de raíz cualquier fuga por difusión térmica o autocorrelación espacial inmediata, obligando a los modelos a predecir sobre territorio geológicamente contiguo pero no visto.
> 
> *En la **Fase 3 (Modelado Pareado)**, seleccionamos cuatro familias algorítmicas evaluadas bajo idénticas condiciones:*
> 1. Un **Clasificador Dummy de Referencia**, que predice la probabilidad a priori de la clase positiva (0.2763).
> 2. Una **Regresión Logística L2**, regularizada con optimizador L-BFGS ($C=1.0$), alimentada con las 8 variables normalizadas (incluyendo los índices $R_{TE}$ e $I_{TT}$).
> 3. Un ensamble de **Random Forest** de 100 árboles con profundidad máxima acotada a 12, promediando tres semillas aleatorias independientes (42, 43 y 44).
> 4. Un **Perceptrón Multicapa (MLP)** profundo desarrollado en PyTorch con topología 8–64–64–32–1, activaciones LeakyReLU ($\alpha = 0.25$), capas de `BatchNorm1d`, `Dropout(0.10)` y optimizador AdamW durante 15 épocas, promediando los logits continuos de tres semillas.
> 
> *Finalmente, en la **Fase 4**, seleccionamos métricas adecuadas. Dado que las clases están desbalanceadas, el ROC-AUC convencional puede ser engañosamente optimista; por ello, nuestra métrica primaria es el **Área Bajo la Curva de Precisión y Exhaustividad (PR-AUC)**, respaldada por el **Brier Score** para evaluar la calibración real de las probabilidades.*  
> *Para la proyección regional sobre 1.2 millones de celdas continentales a 120 metros, incorporamos la metodología del **Área de Aplicabilidad (AOA)** de Meyer y Pebesma (Methods in Ecology and Evolution, 2021). Calculamos el Índice de Disimilitud (DI) multidimensional ponderado por la importancia de permutación de variables; cualquier celda del territorio regional con $DI > 2.1339$ se clasifica formalmente como 'zona de extrapolación no confiable', impidiendo emitir juicios sobre áreas geológicas no cubiertas por el dominio de entrenamiento."*

---

## Diapositiva 5 (Pág. 4): Resultados Cuantitativos Globales: Colapso del Falso Optimismo y Paridad Lineal
* **Tiempo asignado:** 5 minutos (Minuto 16:00 a 21:00)
* **Objetivo:** Analizar en profundidad el Cuadro I, explicar por qué el Protocolo A genera un falso optimismo (PR-AUC > 0.999), detallar la caída en el Protocolo B (PR-AUC 0.952-0.962), y demostrar el hallazgo cardinal de la Paridad Lineal y la superioridad de calibración de la Regresión Logística.
* **Qué señalar en pantalla:**
  - Cuadro I: comparar la columna de Prot. A frente a Prot. B.
  - La fila de Regresión Logística: PR-AUC 0.9527 $\pm$ 0.0398 vs. RF 0.9555 $\pm$ 0.0686 y MLP 0.9624 $\pm$ 0.0702.
  - Las desviaciones estándar (la de Logística es casi la mitad).
  - El Brier Score de Logística (0.0486) superando a RF (0.0649) y MLP (0.0665).
  - Los tres recuadros de conclusiones en la parte inferior.

### Guion en Voz Alta:
> *"Llegamos a la Diapositiva 5, que contiene la tabla medular de nuestro artículo científico: el Cuadro I.*  
> 
> *Examinemos con detenimiento la mitad izquierda de la tabla, correspondiente al **Protocolo A (Partición Aleatoria)**:*
> *Si hubiéramos concluido la investigación en esta etapa, como desafortunadamente ocurre en múltiples publicaciones, estaríamos afirmando que Random Forest y las Redes Neuronales resuelven el mapeo geotérmico de manera perfecta, alcanzando un ROC-AUC de 1.0000, un PR-AUC de 0.9999 y errores de Brier prácticamente nulos de 0.0003 a 0.0010. Este es el arquetipo del **optimismo espurio**: el algoritmo no aprendió la física del reservorio, sino que memorizó la firma espacial de los vecinos.*
> 
> *Ahora, dirijamos la mirada a la mitad derecha: el **Protocolo B (Validación Espacial en 5 Bloques con Buffer de 500 m)**:*
> *En cuanto forzamos a los algoritmos a evaluar sobre un sector geográfico no visto y aislado por medio kilómetro de exclusión, **la ilusión predictiva se desmorona**:*
> - El PR-AUC de Random Forest se desploma de 1.0000 a **0.9555**.
> - El PR-AUC del MLP cae de 0.9998 a **0.9624**.
> - La dispersión entre bloques se dispara: la desviación estándar del PR-AUC pasa de valores casi despreciables a magnitudes de $\pm 0.0686$ en Random Forest y $\pm 0.0702$ en el MLP.
> 
> *Pero el hallazgo científico más contundente de este cuadro es lo que denominamos el **Principio de Paridad Lineal**.*
> *Observemos la fila de la Regresión Logística regularizada:*
> *Al dotarla de los índices físicos $R_{TE}$ e $I_{TT}$, la simple regresión lineal alcanza un PR-AUC medio de **0.9527 $\pm$ 0.0398** y un ROC-AUC de **0.9819 $\pm$ 0.0166**.*
> 
> *Hagamos un análisis estadístico riguroso de esta comparación:*
> *La diferencia en discriminación entre la Regresión Logística (0.9527) y Random Forest (0.9555) es de apenas **0.0028**, y frente al MLP (0.9624) es de **0.0097**. En ambos casos, las diferencias son inferiores a un centésimo y quedan completamente cubiertas dentro del intervalo de una sola desviación estándar ($\pm 0.04$ a $\pm 0.07$). Es decir: **no existe superioridad estadística significativa de los modelos de caja negra sobre el modelo lineal**.*
> 
> *Más aún: cuando auditamos la **calidad de la calibración probabilística** mediante el Brier Score —donde un valor menor indica probabilidades mejor ajustadas a la realidad—, **la Regresión Logística supera a todos los modelos complejos**:*
> - Regresión Logística: **0.0486 $\pm$ 0.0270**
> - Random Forest: **0.0649 $\pm$ 0.0699**
> - MLP PyTorch: **0.0665 $\pm$ 0.0894**
> 
> *¿Por qué ocurre esto? Porque Random Forest y el MLP sobreajustan a las variaciones microscópicas de cada bloque local (como las lagunas de salmuera o el ruido del sensor), generando probabilidades polarizadas hacia 0 y 1. La regresión lineal regularizada, al restringir su hipótesis a una frontera suave basada en física, actúa como un regularizador natural, logrando **la mitad de la varianza inter-bloque y una calibración de probabilidad un 27% superior**.*
> 
> *La implicación práctica para la industria energética es directa: **desplegar una red neuronal profunda multimillonaria no se justifica en este dominio**, pues una regresión logística interpretable ofrece el mismo poder discriminativo con mayor robustez y menor incertidumbre."*

---

## Diapositiva 6 (Pág. 5): Desglose Espacial por Pliegue e Inestabilidad Patológica del Umbral de Youden
* **Tiempo asignado:** 5 minutos (Minuto 21:00 a 26:00)
* **Objetivo:** Auditar el Cuadro II pliegue por pliegue, explicar la catástrofe del Pliegue 5 (Sector Sur), demostrar la inestabilidad patológica del umbral óptimo de Youden en el MLP (rango de 0.8857) y explicar las consecuencias de ingeniería en exploración de campo.
* **Qué señalar en pantalla:**
  - Cuadro II: la fila del Pliegue 5 (Sur).
  - La caída en PR-AUC de RF (0.8352) y MLP (0.8381) frente a la solidez de Regresión Logística (0.9149).
  - El Brier Score del MLP en el Pliegue 5 (0.2231, pésimo).
  - La columna del Umbral de Youden ($J$): contrastar el salto del MLP (de 0.0165 a 0.9022) frente a la estabilidad de la Logística (0.1652 a 0.3540).

### Guion en Voz Alta:
> *"Para entender por qué las desviaciones estándar fueron tan elevadas en el Protocolo B, en la Diapositiva 6 abrimos la 'caja de cristal' y analizamos el comportamiento pliegue por pliegue en el Cuadro II.*
> 
> *Observemos los pliegues 1, 2, 3 y 4, correspondientes a los sectores Norte y Centro del campo de Cerro Prieto:*
> *En estos cuatro bloques, todos los modelos exhiben un desempeño sobresaliente, con PR-AUC superiores a 0.97 y hasta 1.0000. Sin embargo, al llegar al **Pliegue 5 (el extremo Sur del complejo)**, ocurre una verdadera catástrofe predictiva en los modelos no lineales:*
> - Random Forest se derrumba de 1.0000 a **0.8352** de PR-AUC, y su error de Brier salta a 0.1900.
> - El MLP colapsa a **0.8381** de PR-AUC, y su Brier Score se degrada hasta un alarmante **0.2231** (prácticamente igual al baseline dummy aleatorio de 0.2210).
> - En contraste, la **Regresión Logística mantiene su compostura**, reteniendo un PR-AUC de **0.9149** y un Brier de **0.0952**.*
> 
> *¿Qué hace tan particular al Pliegue 5? Es la transición geológica hacia el sur del valle, donde la cobertura sedimentaria cambia y la planta no posee lagunas de evaporación superficiales. Los modelos complejos, que dependían fuertemente de patrones superficiales aprendidos en los sectores 1 a 4, fracasaron al generalizar en este bloque.*
> 
> *Pero el hallazgo más crítico para la ingeniería de decisión se muestra en la última columna del Cuadro II: **la inestabilidad del umbral óptimo de decisión de Youden ($J = \text{Sensibilidad} + \text{Especificidad} - 1$)**.*
> 
> *En cualquier despliegue operativo, el modelo debe convertir su probabilidad continua $P(x)$ en una decisión binaria: 'perforar' o 'no perforar'. Tradicionalmente se asume un umbral por defecto de $P \ge 0.50$.*
> *Veamos qué le sucede al Perceptrón Multicapa:*
> - En el Pliegue 2, el umbral óptimo de Youden es de **0.0165**. Es decir, para balancear falsos positivos y falsos negativos en el sector norte, cualquier píxel con apenas 1.6% de probabilidad debe ser catalogado como positivo.
> - Pero en el Pliegue 5, el umbral óptimo salta hasta **0.9022**. ¡Ahora se requiere más del 90% de probabilidad para tomar la misma decisión!
> 
> *El rango de variación del umbral en el MLP es de **0.8857**, lo que significa que el corte óptimo se desplaza a lo largo del **88.6% de toda la escala de probabilidad** entre sectores contiguos de un mismo yacimiento.*  
> *En contraste, la Regresión Logística oscila en una ventana moderada de apenas 0.24 (de 0.16 a 0.40).*
> 
> *¿Cuál es la consecuencia directa de esto en el mundo real?*
> *Si un equipo de exploración toma el modelo de red neuronal entrenado en Cerro Prieto y aplica un umbral rígido de 0.50 para prospectar una nueva cuenca en Baja California, el resultado será desastroso:*
> - En zonas como el Pliegue 2, un umbral de 0.50 generará una pérdida masiva de exhaustividad, **descartando el yacimiento real por completo**.
> - En zonas como el Pliegue 5, el modelo inundará el mapa de falsas alarmas, conduciendo a **perforaciones estériles millonarias**.*
> *Este análisis demuestra que las probabilidades emitidas por redes complejas sin calibración local son no estacionarias y no deben emplearse para cortes duros de decisión."*

---

## Diapositiva 7 (Pág. 6): Diagnósticos de Control: Coordenadas Puras, Placebos de Fallas y Firmas Hídricas
* **Tiempo asignado:** 5 minutos (Minuto 26:00 a 31:00)
* **Objetivo:** Exponer la batería de experimentos de control negativo que desmontan la ilusión física: el modelo de coordenadas puras UTM, el experimento de placebos de fallas desplazadas ($\pm 10$ km y rotadas $90^\circ$), y la firma hídrica antrópica de MNDWI (49.15% de lagunas de salmuera).
* **Qué señalar en pantalla:**
  - Panel izquierdo: el mapa regional con las 3 bandas concéntricas y el zoom del panel (b) con los 5 sectores y el buffer de 500 m.
  - Panel superior derecho: la curva Log-ROC en escala logarítmica ($10^{-5}$ a $10^0$).
  - Panel inferior derecho: la gráfica de barras de F1-Score en el umbral de Youden.
  - Mencionar los números clave: Coordenadas solas = 0.8426 en Pliegue 5; Placebo de fallas a 10 km Este = 0.8905 vs 0.6424 real.

### Guion en Voz Alta:
> *"La Diapositiva 7 presenta la fase más rigurosa de nuestra investigación: **los diagnósticos dirigidos de control negativo**.*  
> *En ciencia, para probar que una variable física causa la predicción, es indispensable ejecutar experimentos de falsación o 'placebos'. Implementamos tres pruebas de control clave:*
> 
> *1. **El Experimento de Coordenadas Puras $(X_{\text{UTM}}, Y_{\text{UTM}})$:**  
> *Nos preguntamos: ¿cuánto del acierto del modelo proviene de las leyes físicas de la roca y cuánto de la simple memoria de la latitud y longitud? Entrenamos un Random Forest despojándolo de toda la física: sin elevación, sin temperatura, sin magnetometría y sin fallas; únicamente con las coordenadas cartesianas.*  
> *Los resultados fueron reveladores:*
> - En la Banda 2 (a 3.6 km) y Banda 3 (a más de 10 km), el modelo con solo coordenadas alcanzó un ROC-AUC y PR-AUC perfectos de **1.0000**.*
> - Y en el difícil Pliegue 5 (Sur), ¡el modelo con solo coordenadas obtuvo un PR-AUC de **0.8426**! Es decir, igualó e incluso superó numéricamente a Random Forest (0.8352) y al MLP (0.8381) alimentados con las ocho variables físicas completas.*
> *Esto demuestra que a distancias intermedias y regionales, el modelo no clasifica por termodinámica, sino porque aprende la silueta geográfica de la cuenca sedimentaria de Mexicali.*
> 
> *2. **El Experimento de Fallas Placebo (Falsas Fallas Desplazadas):**  
> *La distancia a fallas geológicas del SGM suele citarse como el predictor de fracturamiento por excelencia. Diseñamos un experimento de control perturbando la geología:*
> - Desplazamos las fallas artificialmente 10 km al Oeste, 10 km al Este y las rotamos 90 grados alrededor de Cerro Prieto.*
> *Si el modelo estuviera capturando una relación causal entre fallas reales y permeabilidad, el uso de fallas falsas debería destruir su desempeño.*
> *¿Qué ocurrió en realidad?*
> - En el Pliegue 1, el placebo desplazado 10 km al Oeste superó a las fallas reales (PR-AUC 0.5978 vs. 0.5916).*
> - Y en el Pliegue 5, **el placebo desplazado 10 km al Este superó masivamente a las fallas verdaderas**, logrando un PR-AUC de **0.8905** frente a **0.6424** de la falla real, y un ROC-AUC de 0.9592 frente a 0.8725.*
> *Este resultado es extraordinario desde el punto de vista metodológico: prueba de forma concluyente que la variable 'distancia a fallas' no está actuando como un descriptor geotérmico causal, sino como un **indicador proxies de posición relativa respecto al eje del valle**.*
> 
> *3. **El Sesgo de Superficie Hídrica (MNDWI y Lagunas de Evaporación):**  
> *Auditamos las firmas espectrales de Cerro Prieto mediante el índice de agua modificada MNDWI. Descubrimos que el **49.15% de todas las celdas positivas del campo (12,195 celdas)** presentan firmas espectrales de agua superficial o lodos saturados ($\text{MNDWI} > 0$ o $\text{NDVI} < 0$).*  
> *Esto se debe a la infraestructura operativa de la central de CFE: las enormes lagunas de evaporación y salmueras residuales. En un yacimiento geotérmico virgen no perforado, no existen lagunas de salmuera superficiales. En consecuencia, un modelo que use sensores multiespectrales corre el gravísimo riesgo de aprender a buscar agua industrial en el desierto en lugar de prospectos geotérmicos vírgenes.*
> 
> *No obstante, cuando aislamos el 50.85% de celdas positivas secas, el modelo completo retuvo un PR-AUC de 0.9273 apoyándose en la topografía y el basamento magnético, demostrando que existe una señal física recuperable una vez que se neutraliza el sesgo de agua."*

---

## Diapositiva 8 (Pág. 7): Inferencia Regional, Área de Aplicabilidad (AOA) y El Chinero
* **Tiempo asignado:** 4 minutos y 30 segundos (Minuto 31:00 a 35:30)
* **Objetivo:** Presentar la cartografía predictiva regional sobre 1.2M de celdas a 120 m, explicar el mapa del Área de Aplicabilidad (AOA), desarmar la costura aeromagnética del paralelo 32° N y presentar el caso de estudio de El Chinero desmitificándolo como prospecto ciego.
* **Qué señalar en pantalla:**
  - Los 4 paneles cartográficos de la Figura 2: (a) Regresión Logística, (b) Random Forest, (c) MLP Ensamble y (d) Área de Aplicabilidad (AOA).
  - La línea blanca punteada del paralelo 32° N (costura magnética).
  - El rombo magenta que marca la ubicación de El Chinero en los mapas.
  - El mapa de AOA: verde (62.8% confiable) vs naranja (37.2% fuera de dominio).
  - La tabla diagnóstica de El Chinero al pie de la diapositiva.

### Guion en Voz Alta:
> *"En la Diapositiva 8 proyectamos nuestros modelos a la escala del territorio regional completo: una malla continental continua de **1.2 millones de píxeles a 120 metros de resolución**, cubriendo desde la frontera internacional con Estados Unidos hasta San Felipe y el Golfo de California.*
> 
> *Observemos primero el **Panel (d): el mapa del Área de Aplicabilidad (AOA)**:*
> *Siguiendo a Meyer y Pebesma (2021), establecimos un umbral de Índice de Disimilitud de $DI \le 2.1339$. El resultado muestra que el **62.82% del territorio regional (en color verde)** cae dentro del espacio multivariado entrenado; mientras que el **37.18% (en color naranja)** se encuentra en régimen de extrapolación no confiable, abarcando las cadenas graníticas de la Sierra Cucapá y la depresión magnética meridional.*
> 
> *Ahora comparemos las predicciones de los tres modelos en los paneles (a), (b) y (c):*
> *En el campo de Cerro Prieto (recuadro rojo), los tres modelos coinciden con alta afinidad ($P > 0.90$). Sin embargo, en el resto de la cuenca surgen discrepancias cualitativas fundamentales:*
> - La **Regresión Logística (Panel a)** activa falsas alarmas preferentemente sobre zonas de alta humedad y parcelas irrigadas del delta del Río Colorado, debido al acoplamiento de LST y baja cota.
> - **Random Forest (Panel b)** presenta un patrón alarmante: el **66.4% de todas sus falsas alarmas regionales** se concentran a más de 100 km de distancia, en las inmediaciones de San Felipe, generando manchones de probabilidad de borde artificial.*
> - El **MLP en PyTorch (Panel c)** genera una superficie más continua y amortiguada.*
> 
> *¿A qué se debe el falso positivo masivo de Random Forest en San Felipe?*
> *Al auditar los metadatos geofísicos descubrimos un artefacto cartográfico instrumental:*
> *El Servicio Geológico Mexicano ensambló el mosaico aeromagnético uniendo dos vuelos independientes en el **paralelo 32° Norte** (marcado con la línea punteada blanca en los mapas). En la hoja norte (Mexicali H11-12), el 35.8% de las celdas tiene gradiente magnético nulo; pero en la hoja sur (San Felipe H11-3), **el 69.45% de todo el mapa tiene gradiente magnético exactamente nulo (0 nT/30 m)**. Es una meseta artificial producida por el procesamiento y remuestreo del vuelo. Los árboles de decisión de Random Forest aprendieron que una meseta magnética plana separaba clases, activando falsos positivos a lo largo de la costura cartográfica.*
> 
> *Esto nos lleva al caso de estudio más relevante de la región: **la anomalía de El Chinero** (marcada con el rombo magenta).*
> *Estudios previos basados en modelos no auditados habían catalogado a El Chinero como un 'prospecto geotérmico ciego no identificado' con probabilidades superiores al 90% ($P > 0.90$).*
> *Nuestra evaluación multidisciplinaria demuestra de manera contundente que **El Chinero es un falso positivo geofísico**:*
> 1. **Puntuación Real Colapsada:** En nuestros modelos multivariados, la mediana de probabilidad en El Chinero baja a apenas **0.033** (con percentil 95 de 0.81). Pero si removemos la temperatura superficial LST y el NDVI (es decir, si eliminamos el calor del sol), la probabilidad colapsa a **0.0038** (menos de 4 milésimas).*
> 2. **Magnetometría Totalmente Incompatible:** La firma magnética de Cerro Prieto es fuertemente positiva (+110 a +350 nT), asociada a intrusiones basálticas profundas. En contraste, El Chinero presenta una anomalía negativa de **-225 nT**, ubicándose en el **percentil 0.00%** respecto a la distribución del reservorio.*
> 3. **Extrapolación Fuera del AOA:** Como observamos en el Panel (d), El Chinero cae exactamente en una franja geomorfológica de transición clasificada como **fuera del Área de Aplicabilidad**, con un 33.79% de extrapolación en su entorno local.*
> *En conclusión: la pretendida 'anomalía' de El Chinero no era calor magmático a 2 km de profundidad, sino el calentamiento solar extremo de arenas desérticas de baja inercia térmica (54.08 °C a mediodía) combinado con el sesgo artificial de la costura magnética del paralelo 32° N."*

---

## Diapositiva 9 (Pág. 8): Conclusiones Generales y las Seis Limitaciones Metodológicas
* **Tiempo asignado:** 3 minutos y 30 segundos (Minuto 35:30 a 39:00)
* **Objetivo:** Sintetizar las 3 conclusiones cardinales y asumir con madurez científica las 6 limitaciones metodológicas que impiden declarar descubrimiento de yacimientos sin geofísica 3D profunda.
* **Qué señalar en pantalla:**
  - Las 3 Conclusiones en la parte superior.
  - Las 3 Limitaciones en la parte inferior.
  - La imagen satelital del rift con la ubicación de Cerro Prieto, El Chinero y San Felipe.

### Guion en Voz Alta:
> *"Llegamos a las conclusiones y limitaciones en la Diapositiva 9.*
> 
> *A manera de síntesis, este trabajo aporta tres conclusiones fundamentales a la ciencia de datos aplicada a geociencias:*
> 
> *1. **La Validación Espacial es Obligatoria e Ineludible:** La partición aleatoria convencional infla el PR-AUC por encima de 0.999 debido a la autocorrelación de Tobler. La validación en bloques espaciales con buffer de exclusión de 500 m es indispensable para corregir este optimismo y revelar el rendimiento real en el rango de 0.95 a 0.96.*
> 
> *2. **Paridad Lineal y Superioridad de Calibración:** Con ingeniería de características guiada por física ($R_{TE}$ e $I_{TT}$), una simple Regresión Logística regularizada iguala estadísticamente la discriminación de Random Forest y redes neuronales profundas (0.9527 frente a 0.9555 y 0.9624), superándolos de manera contundente en calibración de Brier (0.0486 frente a 0.0665) y con la mitad de varianza inter-sectorial.*
> 
> *3. **Reevaluación Definitiva de Falsos Prospectos:** La combinación de controles de coordenadas, placebos de fallas y el Área de Aplicabilidad permite desenmascarar artefactos cartográficos y descartar sitios como El Chinero, evitando costosos errores de perforación en zonas que solo reflejan insolación solar superficial.*
> 
> *Asimismo, actuando con la máxima honestidad intelectual que exige la investigación de posgrado, reconocemos **seis limitaciones metodológicas críticas** que impiden usar estos modelos como sustituto de la exploración de campo:*
> 1. **El Problema del Campo Único (Single-Field):** Al existir un solo yacimiento activo de referencia, ningún modelo supervisado puede garantizar generalización regional absoluta a otros sistemas geotérmicos ciegos.*
> 2. **Prevalencia Artificial del Muestreo:** La proporción positiva del 27.6% en nuestra matriz responde a un diseño estratificado; las salidas del modelo son índices relativos de similitud geográfica y no probabilidades absolutas de ocurrencia natural (que en la región es de ~0.075%).*
> 3. **Sesgo por Infraestructura Hídrica:** El satélite captura lagunas de evaporación y salmueras operativas de la propia planta (49.15%), una señal que no existirá en prospectos vírgenes.*
> 4. **Defectos de Empalme Cartográfico:** Las costuras en los mapas aeromagnéticos del SGM en el paralelo 32° N actúan como clasificadores espurios entre cuencas.*
> 5. **Datos Restringidos a Superficie (2D):** Los sensores satelitales y trazas 1:250k son planos y no miden buzamiento, permeabilidad activa, fracturamiento 3D ni gradiente hidrotermal a 2 km.*
> 6. **Muestra Reducida de Bloques:** Con 5 pliegues espaciales, la varianza intrínseca entre sectores geológicos supera las diferencias entre algoritmos, impidiendo declarar ganadores absolutos a nivel de décimas.*
> 
> *El aprendizaje automático superficial es un valioso filtro de primera etapa, pero **jamás reemplazará a la magnetotelúrica 3D, la sísmica de reflexión profunda ni la barrena de perforación exploratoria**."*

---

## Diapositiva 10: Referencias Bibliográficas y Cierre Formal
* **Tiempo asignado:** 1 minuto (Minuto 39:00 a 40:00)
* **Objetivo:** Respaldar bibliográficamente el trabajo y abrir formalmente la sesión de preguntas y respuestas.
* **Qué señalar en pantalla:**
  - Las referencias clave de Elders (1984), Meyer & Pebesma (2021), Ploton et al. (2020 Nature Comm), Roberts et al. (2017 Ecography), Tobler (1970) y Wang et al. (2025 Energy).

### Guion en Voz Alta:
> *"En la Diapositiva 10 se listan las principales referencias bibliográficas en geología hidrotermal, validación espacial, teoría de la autocorrelación y aprendizaje supervisado que sustentaron con solidez metodológica cada sección de esta investigación.*
> 
> *Agradezco cumplidamente la dedicación, guía y retroalimentación del Dr. Irvin Hussein López Nava, del M.C. Joan Raygoza Romero y del Dr. Guillermo Falcón-Cardona a lo largo de este semestre en el Posgrado en Ciencias de la Computación.*
> 
> *Habiendo completado el tiempo reglamentario de 40 minutos, concluyo formalmente mi exposición y quedo a su entera disposición para dar paso a la sesión de preguntas, observaciones y discusión técnica. Muchas gracias."*

---

# Banco de Preguntas Clave del Jurado y Respuestas Maestras (Para la Sesión de Discusión)

### P1: ¿Por qué eligieron un buffer de exclusión de 500 metros en el Protocolo B y no de 1 km o 2 km?
* **Respuesta recomendada:**  
  > *"Excelente pregunta, Dr. López Nava. La elección de 500 metros se fundamentó en el análisis del semivariograma empírico espacial de la elevación y la temperatura superficial en el Valle de Mexicali. El rango espacial de autocorrelación local más pronunciado decae sustancialmente antes de los 450 metros. Si hubiéramos empleado un buffer mayor, por ejemplo de 2 km, habríamos eliminado una porción excesiva de celdas de entrenamiento de los sectores adyacentes de Cerro Prieto, impidiendo que el modelo tuviera suficientes muestras positivas para converger. El buffer de 500 metros representó el compromiso óptimo entre desacoplamiento espacial efectivo según la literatura (Roberts et al., 2017) y masa crítica de entrenamiento."*

### P2: Si la Regresión Logística y Random Forest empatan en PR-AUC (~0.95), ¿por qué afirman categóricamente que la Regresión Logística es superior?
* **Respuesta recomendada:**  
  > *"Nuestra afirmación se sostiene en dos criterios metodológicos cardinales: parsimonia y calibración. Primero, bajo el principio de la Navaja de Ockham, ante dos modelos con idéntico poder discriminativo (0.9527 vs 0.9555), siempre debe preferirse el más simple, ya que posee un riesgo intrínseco menor de sobreajuste estructural. Segundo y más importante: el Brier Score de la Regresión Logística fue de 0.0486 frente a 0.0649 en Random Forest y 0.0665 en el MLP, con una desviación estándar que es la mitad ($\pm 0.0398$ vs $\pm 0.0702$). Esto demuestra que la Regresión Logística no solo predice igual de bien, sino que sus probabilidades continuas son mucho más confiables y estables entre sectores geológicos que las probabilidades polarizadas de los ensambles de árboles o redes profundas."*

### P3: ¿Cómo explica que el placebo de fallas a 10 km al Este haya superado a las fallas reales en el Pliegue 5?
* **Respuesta recomendada:**  
  > *"Ese es uno de los hallazgos diagnósticos más reveladores del trabajo. Las fallas del SGM son trazas 2D digitalizadas a escala 1:250,000; no contienen información de profundidad, buzamiento ni permeabilidad activa. En el Valle de Mexicali, el valle desciende topográficamente hacia el centro de la cuenca sedimentaria. Al desplazar la falla 10 km al Este, la nueva línea virtual quedó posicionada exactamente a lo largo del gradiente topográfico más marcado de la cuenca sur. El algoritmo no estaba buscando fracturas hidrotermales activas; estaba utilizando la distancia como una métrica proxy de proximidad al eje estructural del rift. Al mover la falla a una posición geométricamente más correlacionada con la depresión local del Pliegue 5, el modelo aumentó artificialmente su PR-AUC de 0.64 a 0.89. Esto prueba que la variable distancia a fallas 2D en aprendizaje automático actúa como coordenada geográfica y no como ley física de permeabilidad."*

### P4: ¿Qué le recomendaría a una empresa de exploración geotérmica que quiera usar Machine Learning a partir de sus resultados?
* **Respuesta recomendada:**  
  > *"Le daría tres recomendaciones indispensables: primero, nunca validar modelos con partición aleatoria estándar; siempre exigir validación espacial por bloques con zonas de exclusión para no tomar decisiones sobre métricas ilusorias. Segundo, no descartar modelos lineales bien calibrados con variables de interacción física; la interpretabilidad y calibración superan a la complejidad de las redes profundas. Y tercero, delimitar siempre el Área de Aplicabilidad (AOA) antes de interpretar un mapa regional: si un supuesto prospecto ciego como El Chinero cae fuera del AOA o sus anomalías se disuelven al remover la radiación solar superficial diurna, perforar un pozo de 7 millones de dólares allí sería una catástrofe financiera basada en un artefacto algorítmico."*
