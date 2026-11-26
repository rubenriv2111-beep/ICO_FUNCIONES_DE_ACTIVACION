# Guion Oficial Cronometrado en Segundos: 8 Minutos Exactos (480 s)
## Clasificación Geoespacial Multivariada para Zonas Geotérmicas

**Expositor:** Rubén Rivera García  
**Posgrado en Ciencias de la Computación — CICESE**  
**Profesores:** Dr. Irvin Hussein López Nava | M.C. Joan Raygoza Romero | Dr. Jesús Guillermo Falcón-Cardona  
**Tiempo Total:** 8 minutos exactos (480 segundos)  
**Tiempo neto de discurso:** 7 minutos 20 segundos (440 s) + 40 s de margen de seguridad para transiciones.

---

### Tabla Cronómetro General

| Diapositiva | Tiempo (segundos) | Intervalo Cronómetro |
| :--- | :---: | :---: |
| **1. Portada** | **25 s** | 00:00 – 00:25 |
| **2. Pág. 1: Contexto y Desafío** | **45 s** | 00:25 – 01:10 |
| **3. Pág. 2: Perfil del Dataset y Variables** | **45 s** | 01:10 – 01:55 |
| **4. Pág. 3: Metodología y Protocolos A vs B** | **45 s** | 01:55 – 02:40 |
| **5. Pág. 4: Resultados Cuantitativos (Cuadro I)** | **55 s** | 02:40 – 03:35 |
| **6. Pág. 5: Desglose Pliegue 5 y Youden (Cuadro II)**| **55 s** | 03:35 – 04:30 |
| **7. Pág. 6: Diagnósticos de Control Negativo** | **45 s** | 04:30 – 05:15 |
| **8. Pág. 7: Inferencia Regional, AOA y El Chinero** | **55 s** | 05:15 – 06:10 |
| **9. Pág. 8: Conclusiones y Limitaciones** | **50 s** | 06:10 – 07:00 |
| **10. Referencias y Cierre** | **20 s** | 07:00 – 07:20 |
| **Margen de reserva y preguntas** | **40 s** | 07:20 – 08:00 |

---

### Diapositiva 1: Portada
⏱️ **Duración:** 25 segundos [00:00 – 00:25]
> *"Buenos días profesores y compañeros. Presento el proyecto: **'Clasificación geoespacial multivariada para la identificación de zonas geotérmicas'**, asesorado por el Dr. Irvin López Nava y el M.C. Joan Raygoza. El objetivo central fue evaluar si el aprendizaje automático identifica prospectos geotérmicos reales sin caer en la trampa de la autocorrelación espacial ni en falsos descubrimientos."*

---

### Diapositiva 2 (Pág. 1): Contexto y Desafío
⏱️ **Duración:** 45 segundos [00:25 – 01:10]  
👉 *Señalar: Costo de 5-10 MDD y las 3 preguntas a la derecha.*
> *"La geotermia aporta energía limpia continua de carga base, pero perforar un pozo exploratorio cuesta de 5 a 10 millones de dólares con alto riesgo de salir seco.  
> En ciencia de datos enfrentamos tres problemas graves:  
> Primero, cobertura territorial mínima: Cerro Prieto es el único campo activo y ocupa menos del 0.075% del rift.  
> Segundo, severo desbalance de clases.  
> Y tercero, la Ley de Tobler: los píxeles vecinos se parecen entre sí.  
> Con esto evaluamos: ¿pueden las variables físicas identificar el recurso sin depender de la posición? ¿Cuánto sobreestima la validación aleatoria? ¿Y realmente se justifican las redes complejas frente a un modelo lineal con física?"*

---

### Diapositiva 3 (Pág. 2): Perfil y Calidad del Dataset
⏱️ **Duración:** 45 segundos [01:10 – 01:55]  
👉 *Señalar: 89,815 celdas, corrección de 197.8 m en fallas y fórmulas $R_{TE}$ e $I_{TT}$.*
> *"Construimos una muestra de 89,815 celdas a 30 metros: 24,814 de Cerro Prieto y 65,000 negativas repartidas en 3 bandas concéntricas de distancia. Cero datos sintéticos con SMOTE.  
> Integramos relieve del INEGI, temperatura superficial y vegetación de Landsat 9, magnetometría de basamento y fallas del Servicio Geológico Mexicano, corrigiendo un desfase de 197.8 metros de NAD27 a WGS84.  
> Incorporamos los índices físicos $R_{TE}$ e $I_{TT}$ de Wang (2025) y blindamos el escalador ajustándolo exclusivamente en entrenamiento para garantizar cero fuga de datos."*

---

### Diapositiva 4 (Pág. 3): Metodología y Protocolos
⏱️ **Duración:** 45 segundos [01:55 – 02:40]  
👉 *Señalar: Protocolo A (aleatorio) vs B (bloques espaciales con buffer 500 m).*
> *"Diseñamos cuatro pilares:  
> Primero, blindaje estricto sin alterar pesos de clase.  
> Segundo, dos protocolos pareados: el **Protocolo A**, que es la partición aleatoria convencional; y el **Protocolo B**, una validación espacial en 5 bloques contiguos Norte-Sur con un buffer perimetral de exclusión de 500 metros para cortar la fuga por vecindad.  
> Tercero, evaluamos cuatro modelos: Dummy, Regresión Logística L2, Random Forest y un MLP profundo en PyTorch con ensamble de 3 semillas.  
> Y cuarto, evaluamos la inferencia sobre 1.2 millones de celdas filtradas por el Área de Aplicabilidad (AOA) para evitar extrapolar a ciegas."*

---

### Diapositiva 5 (Pág. 4): Resultados Cuantitativos (Cuadro I)
⏱️ **Duración:** 55 segundos [02:40 – 03:35]  
👉 *Señalar: Caída en Prot. B y fila de Regresión Logística con menor error Brier.*
> *"El Cuadro I muestra dos hallazgos contundentes:  
> Primero, el **colapso del optimismo falso**: en validación aleatoria, Random Forest y el MLP superan 0.999 en PR-AUC. Pero en validación espacial por bloques, el desempeño real cae al rango de 0.95 a 0.96. La partición aleatoria sobreestimaba el rendimiento por memorizar vecinos.  
> Segundo, la **paridad lineal**: la Regresión Logística con los índices físicos alcanza 0.9527 de PR-AUC, empatando estadísticamente a Random Forest (0.9555) y al MLP (0.9624), pues la diferencia de menos de 0.01 queda dentro de la desviación estándar.  
> Además, la logística tiene la mitad de variabilidad ($\pm 0.039$ vs $\pm 0.070$) y mejor Brier Score (0.048 vs 0.066). La complejidad de caja negra no se justifica en este dominio."*

---

### Diapositiva 6 (Pág. 5): Desglose por Pliegue e Inestabilidad de Youden
⏱️ **Duración:** 55 segundos [03:35 – 04:30]  
👉 *Señalar: Caída del Pliegue 5 y salto de Youden en MLP (0.0165 a 0.9022).*
> *"Al desglosar los 5 bloques espaciales individuales surgen dos alertas críticas:  
> 1. En el Pliegue 5 (sector Sur), Random Forest y el MLP colapsan a 0.83 de PR-AUC con un error de Brier pésimo de 0.22, mientras la Logística resiste con 0.91 y Brier de 0.09.  
> 2. **Inestabilidad extrema del umbral óptimo de Youden ($J$):** en la red neuronal, el corte óptimo salta de 0.0165 en el bloque 2 a 0.9022 en el bloque 5. Varía en el 88.6% de toda la escala de probabilidad, mientras que la logística es mucho más estable.  
> La implicación en campo es directa: aplicar un corte fijo de 0.5 con redes neuronales sobre zonas nuevas sin recalibración descartará yacimientos reales o provocará pozos secos millonarios."*

---

### Diapositiva 7 (Pág. 6): Diagnósticos de Control Negativo
⏱️ **Duración:** 45 segundos [04:30 – 05:15]  
👉 *Señalar: Buffer de 500 m en el mapa derecho y curvas Log-ROC a la izquierda.*
> *"Ejecutamos tres pruebas de falsación científica:  
> 1. **Coordenadas puras:** Un modelo entrenado solo con $X$ e $Y$ UTM igualó al modelo de 8 variables físicas en el Pliegue 5 (PR-AUC 0.8426), probando que a escala regional se memoriza la geometría de la cuenca.  
> 2. **Placebos de fallas:** Desplazamos las fallas 10 km al Este y el modelo mejoró artificialmente su PR-AUC de 0.64 a 0.89 en el Pliegue 5, confirmando que la distancia a fallas actúa como proxy de posición dentro del valle y no como ley de fracturamiento.  
> 3. **Firmas de agua:** El 49.15% del campo presenta firmas hídricas por lagunas de evaporación de la planta de CFE; sin embargo, al evaluar celdas secas, el modelo retiene un PR-AUC de 0.9273 apoyándose en relieve y basamento."*

---

### Diapositiva 8 (Pág. 7): Inferencia Regional, AOA y El Chinero
⏱️ **Duración:** 55 segundos [05:15 – 06:10]  
👉 *Señalar: Mapa AOA (verde vs naranja) y la tabla diagnóstica de El Chinero.*
> *"Proyectamos la probabilidad sobre 1.2 millones de celdas y delimitamos el Área de Aplicabilidad (AOA), donde el 62.8% del territorio resultó confiable.  
> Un aporte clave fue auditar **El Chinero**, catalogado en estudios previos como supuesto prospecto ciego con probabilidad mayor al 90%.  
> Demostramos cuantitativamente que es un falso positivo:  
> Primero, su probabilidad real colapsa a una mediana de 0.033, y a 0.0038 si quitamos temperatura y vegetación. Era solo arena caliente de mediodía a 54 °C.  
> Segundo, su magnetometría es de -225 nT, percentil cero frente a Cerro Prieto (+110 a +350 nT).  
> Y tercero, cae fuera del AOA por estar acoplado al defecto de costura del mapa aeromagnético en el paralelo 32° Norte."*

---

### Diapositiva 9 (Pág. 8): Conclusiones y Limitaciones
⏱️ **Duración:** 50 segundos [06:10 – 07:00]  
👉 *Señalar: Las 3 conclusiones arriba y las 3 limitaciones abajo.*
> *"Concluyendo el trabajo:  
> 1. La **validación espacial es obligatoria**: la aleatoria crea una ilusión de desempeño que no generaliza en terreno real.  
> 2. **Principio de parsimonia**: la Regresión Logística con variables físicas iguala a las redes profundas con mayor estabilidad y mejor calibración.  
> 3. Descartamos científicamente El Chinero como prospecto geotérmico.  
> 
> Y reconocemos tres limitaciones honestas:  
> - El sesgo de campo único, al contar solo con Cerro Prieto.  
> - El sesgo superficial: el satélite mide insolación solar y lagunas operativas, no calor a 2 km de profundidad.  
> - Y que el aprendizaje automático 2D jamás sustituye a la geofísica profunda ni a la perforación exploratoria."*

---

### Diapositiva 10: Referencias y Cierre
⏱️ **Duración:** 20 segundos [07:00 – 07:20]
> *"En la última lámina quedan las referencias que sustentaron la metodología. Agradezco sinceramente a mis profesores por su retroalimentación y quedo listo para responder sus preguntas. Muchas gracias."*

---
*(Minuto 07:20 a 08:00: Margen de 40 segundos para pausas naturales y apertura de la sesión de preguntas).*
