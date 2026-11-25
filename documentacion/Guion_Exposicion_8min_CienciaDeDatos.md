# Guion Ejecutivo de 8 Minutos: Clasificación Geoespacial para Geotermia

**Proyecto Final de Ciencia de Datos**  
**Posgrado en Ciencias de la Computación — CICESE**  
**Expositor:** Rubén Rivera García  
**Asesores:** Dr. Irvin Hussein López Nava | M.C. Joan Raygoza Romero  
**Duración Total:** 8 minutos exactos (~45-50 segundos por diapositiva)  

---

### Portada (20 segundos)
> *"Buenos días, profesores y compañeros. Presento el proyecto: **'Clasificación geoespacial multivariada para la identificación de zonas geotérmicas'**, desarrollado bajo la asesoría del Dr. Irvin López Nava y el M.C. Joan Raygoza. El objetivo central fue evaluar si modelos de aprendizaje automático pueden identificar prospectos geotérmicos reales en Baja California sin caer en trampas de autocorrelación espacial ni falsos positivos."*

---

### Pág. 1: Contexto y Desafío (45 segundos)
> *"La energía geotérmica es renovable y continua, pero perforar un pozo profundo cuesta entre 5 y 10 millones de dólares con alto riesgo de resultar estéril.  
> Desde la ciencia de datos enfrentamos tres problemas graves:  
> 1. Cobertura territorial mínima: los yacimientos ocupan menos del 0.5% del área.  
> 2. Desbalance severo de clases.  
> 3. Autocorrelación espacial: los puntos cercanos se parecen entre sí por la Primera Ley de Tobler.  
> Con esto planteamos: ¿pueden las variables físicas detectar el recurso sin depender de la cercanía al campo? ¿Cuánto sobreestima la validación aleatoria tradicional? ¿Y realmente justifican los modelos complejos frente a un modelo lineal con física?"*  
* **Señalar:** Las 3 preguntas al pie.

---

### Pág. 2: Perfil y Calidad del Dataset (45 segundos)
> *"Construimos una muestra de 89,815 celdas de 30 metros: 24,814 de Cerro Prieto y 65,000 de fondo estratificadas en 3 bandas concéntricas hasta más de 10 kilómetros. Todo con datos 100% reales, sin inventar datos con SMOTE.  
> Integramos topografía de INEGI, temperatura superficial (LST) y vegetación de Landsat 9, magnetometría del SGM y distancia a fallas geológicas corregidas de NAD27 a WGS84 resolviendo un desfase de 198 metros.  
> Además, calculamos los índices RTE e ITT de Wang (2025) para inyectar relaciones físicas, y confinamos el StandardScaler estrictamente a entrenamiento para garantizar cero fugas de información."*  
* **Señalar:** La tabla de variables y la corrección geodésica.

---

### Pág. 3: Metodología y Protocolos (50 segundos)
> *"Diseñamos un experimento pareado bajo cuatro pilares:  
> Primero, blindaje de datos sin balanceo artificial.  
> Segundo, dos protocolos de evaluación: el **Protocolo A**, que es la partición aleatoria clásica 70/15/15; y el **Protocolo B**, una validación espacial en 5 bloques Norte-Sur con una zona de amortiguamiento de 500 metros para cortar la fuga por proximidad.  
> Tercero, evaluamos cuatro modelos: Dummy, Regresión Logística L2, Random Forest y un MLP en PyTorch con ensamble de 3 semillas.  
> Y cuarto, proyectamos la inferencia sobre 1.2 millones de celdas regionales filtradas por el Área de Aplicabilidad (AOA) para evitar extrapolar a ciegas."*  
* **Señalar:** Los 4 recuadros de metodología.

---

### Pág. 4: Resultados: Aleatorio vs. Espacial (55 segundos)
> *"En la tabla observamos dos hallazgos contundentes:  
> Primero, el **colapso del falso optimismo**: en validación aleatoria, Random Forest y la Red Neuronal dan un PR-AUC perfecto de 0.999. Pero al aplicar validación espacial por bloques, el desempeño real cae al rango de 0.95 a 0.96. La partición aleatoria inflaba los resultados por recordar píxeles vecinos.  
> Segundo, la **paridad lineal**: la Regresión Logística con los índices físicos alcanza 0.9527 de PR-AUC, empatando estadísticamente a Random Forest (0.9555) y al MLP (0.9624).  
> Además, la logística tuvo la mitad de dispersión ($\pm 0.039$ vs $\pm 0.070$) y mejor calibración de Brier (0.048 vs 0.066). En este problema, la complejidad de caja negra no aporta ventaja real."*  
* **Señalar:** La caída en la columna de Prot. B y la paridad de LogReg.

---

### Pág. 5: Desglose por Pliegue e Inestabilidad de Youden (55 segundos)
> *"Al desglosar los 5 bloques espaciales descubrimos dos problemas críticos en los modelos no lineales:  
> 1. En el Pliegue 5 (el sector Sur del campo), Random Forest y el MLP colapsan a 0.83 de PR-AUC con un error de Brier pésimo de 0.22, mientras la Logística se mantiene sólida en 0.91.  
> 2. **Inestabilidad extrema del umbral óptimo:** en la red neuronal, el corte de Youden salta de 0.016 en el bloque 2 a 0.902 en el bloque 5. ¡Varía en un 88% de la escala! La logística, en cambio, es muy estable.  
> Impacto real: si usas una red neuronal con un umbral fijo de 0.5 para explorar una zona nueva, vas a omitir yacimientos o perforar pozos secos millonarios por falta de calibración."*  
* **Señalar:** La fila del Pliegue 5 y los saltos de Youden del MLP.

---

### Pág. 6: Diagnósticos de Control (40 segundos)
> *"En la curva Log-ROC de la izquierda vemos cómo al evaluar falsos positivos en escala logarítmica ($10^{-5}$ a $10^0$), los modelos complejos se despegan ligeramente solo en umbrales muy estrictos, pero en F1 macro se mantienen virtualmente empatados en 0.99.  
> En el mapa de la derecha se aprecia la arquitectura de nuestro Protocolo B: los 5 sectores independientes y el buffer perimetral de 500 metros en gris, que fue el filtro que desarmó la ilusión predictiva generada por la autocorrelación de Tobler."*  
* **Señalar:** El buffer de 500 m en el mapa derecho.

---

### Pág. 7: Inferencia Regional y Caso El Chinero (55 segundos)
> *"Mapeamos la probabilidad en todo el rift y calculamos el Área de Aplicabilidad (AOA), donde el 62.8% del territorio resultó válido.  
> Un punto clave fue reevaluar **El Chinero**, que en estudios previos aparecía como un supuesto prospecto ciego con probabilidad mayor al 90%.  
> Nuestro análisis físico demostró que es un falso positivo:  
> 1. Su puntuación real cae a una mediana de 0.033 (0.004 si quitamos temperatura y vegetación). Era solo arena caliente de mediodía.  
> 2. Su magnetometría es de -225 nT, sin firma de intrusión ígnea.  
> 3. Queda completamente fuera del AOA por estar afectado por la costura del mosaico aeromagnético en el paralelo 32° Norte."*  
* **Señalar:** El mapa de AOA en naranja/verde y la tabla diagnóstica de El Chinero.

---

### Pág. 8: Conclusiones y Limitaciones (50 segundos)
> *"Concluyendo el trabajo:  
> 1. La **validación espacial es obligatoria**: la aleatoria crea una ilusión de desempeño que no generaliza en territorio real.  
> 2. **Paridad y parsimonia**: la Regresión Logística con descriptores físicos iguala a las redes profundas con mayor estabilidad y mejor calibración.  
> 3. Descartamos científicamente El Chinero como prospecto geotérmico.  
> 
> Y señalamos tres limitaciones honestas:  
> - El sesgo de campo único, al entrenar solo con Cerro Prieto.  
> - El sesgo superficial: el satélite mide radiación solar y humedad de salmueras operativas, no calor a 2 km.  
> - Y que el aprendizaje automático en 2D jamás sustituye a la geofísica profunda ni a la perforación."*  
* **Señalar:** Los 3 puntos de conclusiones y limitaciones.

---

### Cierre (15 segundos)
> *"En la última lámina quedan las referencias que sustentaron la metodología. Agradezco a mis profesores y quedo a su disposición para sus preguntas. Muchas gracias."*
