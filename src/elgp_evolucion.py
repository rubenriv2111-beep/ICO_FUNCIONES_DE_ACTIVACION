# =============================================================
# ARCHIVO 4/5: elgp_evolucion.py
# Motor evolutivo (mu, lambda) con tope de evaluaciones exacto (B5),
# reevaluacion por z-score medio (B4) y evaluacion estadistica con correccion
# de Nadeau y Bengio (2003), intervalos de confianza 95% y Holm (B6)
# =============================================================

import functools
from scipy import stats
from elgp_config import *
from elgp_individuo import (
    Ind, ind_aleatorio, cruza, muta, torneo, g1, domina_deb, deb_cmp,
    formula, firma_fenotipo, ActivacionLGP, detectar_equivalencia, fabrica_activacion
)
from elgp_datos import entrenar_pliegue


# -------------------------------------------------------------
# CONTADOR Y REGISTRO DE HISTORIAL
# -------------------------------------------------------------
class Contador:
    def __init__(self):
        self.n = 0


class Archivo:
    """Archivo elite que almacena los mejores fenotipos factibles encontrados."""
    def __init__(self):
        self.d = {}

    def agregar(self, ind):
        if ind.g1 is None or ind.g1 > 0.0 or ind.f is None:
            return
        fp = firma_fenotipo(ind)
        if fp not in self.d or ind.f < self.d[fp].f:
            self.d[fp] = ind.copia()

    def top(self, k):
        return sorted(self.d.values(), key=lambda i: i.f)[:k]


# -------------------------------------------------------------
# CALIBRACION DEL BASELINE RELU DE REFERENCIA (R1)
# -------------------------------------------------------------
def calibrar_baseline_relu(suite, cfg, n_semillas=5):
    """
    Entrena ReLU con n_semillas x pliegues en cada dataset de evolucion.
    Calcula media mu_j y desviacion sd_j para estandarizar los scores:
    z_j(x) = (score_j(x) - mu_j) / max(sd_j, 0.002).
    """
    print("\n[Calibracion] Calculando desempeno base de ReLU en suite de evolucion ({} semillas)...".format(n_semillas))
    baseline_ref = {}
    act_relu = fabrica_activacion("ReLU")

    for ds in suite:
        scores_ds = []
        for s_idx in range(n_semillas):
            semilla = 1000 + s_idx * 17
            for pliegue in ds["pliegues"]:
                _, score, div = entrenar_pliegue(act_relu, ds, pliegue, semilla=semilla, cfg=cfg)
                if not div:
                    scores_ds.append(score)

        mu_j = float(np.mean(scores_ds)) if scores_ds else 0.50
        sd_j = float(max(np.std(scores_ds), 0.002)) if scores_ds else 0.05
        baseline_ref[ds["nombre"]] = dict(mu=mu_j, sd=sd_j)
        print("  - {:<38} | ReLU AUC base: {:.4f} +/- {:.4f}".format(ds["nombre"][:38], mu_j, sd_j))

    return baseline_ref


# -------------------------------------------------------------
# FUNCION OBJETIVO MULTI-DATASET NORMALIZADA (R1, R4)
# -------------------------------------------------------------
def evaluar_fitness_multidataset(ind, suite, cfg, contador, baseline_ref):
    """
    Evalua el individuo ind sobre la suite multi-dataset:
      - Fast-Fail: Si g1(x) > 0 (no cumple restriccion de no-linealidad),
        NO se entrena y se devuelve inmediatamente como inviable.
      - Para cada dataset j: z_j = clip((score_j - mu_j)/sd_j, -3.0, 3.0).
      - f(x) = - (1/M) * sum(z_j)  (a minimizar; negativo indica superioridad a ReLU).
      - Divergencia: score=0.50 en el pliegue y se incrementa ind.divergencias.
    """
    violacion = g1(ind, cfg.get("EPS_NL", 0.05))
    if violacion > 0.0:
        ind.f = None
        ind.es_factible = False
        return ind.f

    contador.n += 1
    z_scores = []
    ind.f_detalles = {}
    ind.z_detalles = {}
    ind.divergencias = 0

    for ds in suite:
        scores_pliegues = []
        for pliegue in ds["pliegues"]:
            res, score, div = entrenar_pliegue(
                lambda: ActivacionLGP(ind), ds, pliegue, semilla=42, cfg=cfg
            )
            if div:
                ind.divergencias += 1
            scores_pliegues.append(score)

        score_ds = float(np.mean(scores_pliegues))
        ind.f_detalles[ds["nombre"]] = round(score_ds, 4)

        mu_j = baseline_ref[ds["nombre"]]["mu"]
        sd_j = baseline_ref[ds["nombre"]]["sd"]
        sd_eff = max(sd_j, 0.002)
        z_j = float(np.clip((score_ds - mu_j) / sd_eff, -3.0, 3.0))
        ind.z_detalles[ds["nombre"]] = round(z_j, 4)
        z_scores.append(z_j)

    ind.f = float(-np.mean(z_scores))
    ind.es_factible = True
    return ind.f


def ind_factible_aleatorio(cfg):
    """Genera un individuo aleatorio con garantia estructural de no-linealidad g1 <= 0."""
    for _ in range(100):
        ind = ind_aleatorio(cfg["L"])
        if g1(ind, cfg.get("EPS_NL", 0.05)) <= 0.0:
            return ind
    return ind_aleatorio(cfg["L"])


# -------------------------------------------------------------
# ESTRATEGIA EVOLUTIVA (mu, lambda) CON TOPE DE PRESUPUESTO (B5)
# -------------------------------------------------------------
def evolucionar_mu_lambda(suite, cfg, contador=None, e_fijo=False, etiqueta="ELGP-Multi",
                          baseline_ref=None, tope_evaluaciones=None, evaluador=None):
    """
    Estrategia evolutiva (mu, lambda) con coma:
      - Padres de la generacion t+1 se seleccionan UNICAMENTE de los hijos de la generacion t.
      - Archivo elite historico participa en el torneo de apareamiento.
      - Cruza siempre (P_CRUZA = 1.0).
      - Tope de evaluaciones exacto (B5): si contador.n >= tope_evaluaciones, detiene la busqueda.
    """
    if contador is None:
        contador = Contador()
    if baseline_ref is None and evaluador is None:
        baseline_ref = calibrar_baseline_relu(suite, cfg, n_semillas=5)

    mu = cfg.get("MU", 30)
    lambda_hijos = cfg.get("LAMBDA_HIJOS", 60)
    assert lambda_hijos > mu, "Requisito violado: LAMBDA_HIJOS ({}) debe ser estrictamente mayor que MU ({})".format(lambda_hijos, mu)

    archivo = Archivo()

    def evaluar(i):
        if evaluador is not None:
            evaluador(i)
        else:
            evaluar_fitness_multidataset(i, suite, cfg, contador, baseline_ref)
        if i.es_factible:
            archivo.agregar(i)
        return i

    # Poblacion inicial de padres
    pob = [ind_factible_aleatorio(cfg) for _ in range(mu)]
    with Spinner("  [Gen 0] Evaluando poblacion inicial (mu={}) en suite de evolucion".format(mu)):
        for ind in pob:
            if tope_evaluaciones is not None and contador.n >= tope_evaluaciones:
                break
            evaluar(ind)
    pob.sort(key=functools.cmp_to_key(deb_cmp))

    hist_mejor, hist_prom = [], []
    mejor_global_f = float("inf")
    sin_mejora = 0
    curva_evals_f = []
    t0 = time.time()

    print("\n--- INICIO DE CORRIDA EVOLUTIVA ({}) ---".format(etiqueta))
    print("  Estrategia: (mu={}, lambda={}) con coma | Tmax={} | Cruza P={}".format(
        mu, lambda_hijos, cfg["T_MAX"], cfg["P_CRUZA"]))

    for gen in range(1, cfg["T_MAX"] + 1):
        if tope_evaluaciones is not None and contador.n >= tope_evaluaciones:
            break

        t_gen0 = time.time()
        elite_actual = archivo.top(1)[0] if archivo.top(1) else pob[0]

        # 1. Generacion de lambda hijos mediante cruza y mutacion
        mating_pool = pob + [elite_actual]
        hijos = []
        while len(hijos) < lambda_hijos:
            p1 = torneo(mating_pool, 3)
            p2 = torneo(mating_pool, 3)
            h1, h2 = cruza(p1, p2, cfg.get("P_CRUZA", 1.0))
            hijos.append(muta(h1, cfg, e_fijo))
            if len(hijos) < lambda_hijos:
                hijos.append(muta(h2, cfg, e_fijo))

        # 2. Evaluacion de hijos con respeto a tope_evaluaciones (B5)
        fastfails = 0
        with Spinner("  [Gen {:2d}] Evaluando descendientes (lambda={})".format(gen, len(hijos))):
            for h in hijos:
                if tope_evaluaciones is not None and contador.n >= tope_evaluaciones:
                    break
                evaluar(h)
                if not h.es_factible:
                    fastfails += 1

        # 3. Supervivencia estricta (mu, lambda): los padres salen SOLO DE LOS HIJOS
        hijos_evaluados = [h for h in hijos if h.es_factible or h.g1 is not None]
        if hijos_evaluados:
            hijos_evaluados.sort(key=functools.cmp_to_key(deb_cmp))
            pob = [h.copia() for h in hijos_evaluados[:mu]]
            # Si hubo menos hijos evaluados que mu, completar con factibles
            while len(pob) < mu:
                pob.append(ind_factible_aleatorio(cfg))

        mejor_pob = pob[0]
        f_pob = [i.f for i in pob if i.f is not None]
        prom_f = float(np.mean(f_pob)) if f_pob else 0.0

        hist_mejor.append(mejor_pob.f if mejor_pob.f is not None else 9.0)
        hist_prom.append(prom_f)

        elite_archivo = archivo.top(1)[0] if archivo.top(1) else mejor_pob
        curva_evals_f.append((contador.n, elite_archivo.f))

        # Deteccion de mejora en el archivo
        if elite_archivo.f is not None and elite_archivo.f < mejor_global_f - 1e-4:
            mejor_global_f = elite_archivo.f
            sin_mejora = 0
            equiv, desc_eq, r_eq, _ = detectar_equivalencia(elite_archivo)
            print("  -> [NUEVO CAMPEON en Gen {:2d}] f={:+.4f} | Evals={:d} | {}".format(
                gen, elite_archivo.f, contador.n, desc_eq))
            print("     Formula: " + formula(elite_archivo))
        else:
            sin_mejora += 1

        dt_gen = time.time() - t_gen0
        print("  [Gen {:2d}/{:2d}] mejor f={:+.4f} | prom f={:+.4f} | fastfails={:2d} | evals={:d} | {:.1f}s".format(
            gen, cfg["T_MAX"], (mejor_pob.f if mejor_pob.f is not None else 9.0),
            prom_f, fastfails, contador.n, dt_gen))

        guardar_checkpoint_archivo(archivo, cfg, gen, contador.n)

        # 4. Mecanismo de reinyeccion por estancamiento
        if sin_mejora >= cfg.get("T_EST", 5):
            print("  [Estancamiento: reinyectando {} individuos aleatorios factibles]".format(cfg.get("N_REEMPLAZO", 15)))
            for k in range(1, min(cfg.get("N_REEMPLAZO", 15) + 1, len(pob))):
                if tope_evaluaciones is not None and contador.n >= tope_evaluaciones:
                    break
                pob[-k] = ind_factible_aleatorio(cfg)
                evaluar(pob[-k])
            pob.sort(key=functools.cmp_to_key(deb_cmp))
            sin_mejora = 0

    print("  Evolucion completada: {} evaluaciones efectivas en {:.1f} min".format(
        contador.n, (time.time() - t0) / 60))
    archivo.pob_final = pob
    return archivo, hist_mejor, hist_prom, curva_evals_f


def guardar_checkpoint_archivo(archivo, cfg, gen, evals):
    try:
        os.makedirs(cfg.get("SALIDA", "."), exist_ok=True)
        ruta = os.path.join(cfg.get("SALIDA", "."), "campeon_parcial_multidataset.json")
        top_ind = archivo.top(1)
        if top_ind:
            campeon = top_ind[0]
            with open(ruta, "w", encoding="utf-8") as f:
                json.dump(dict(
                    generacion=gen,
                    evaluaciones=evals,
                    f=campeon.f,
                    g1=campeon.g1,
                    formula=formula(campeon),
                    f_detalles=campeon.f_detalles,
                    genes=campeon.genes,
                    e=[round(float(v), 4) for v in campeon.e],
                ), f, indent=2)
    except Exception:
        pass


# -------------------------------------------------------------
# REEVALUACION DE FINALISTAS POR Z-SCORE MEDIO (B4)
# -------------------------------------------------------------
def reevaluar_finalistas(candidatos, suite, cfg, baseline_ref, n_semillas=5):
    """
    Reevalua los candidatos finalistas con n_semillas independientes nuevas
    y los ordena estrictamente por z-score medio normalizado (con baseline_ref),
    identico al criterio de fitness (B4).
    """
    print("\n[Reevaluacion] Evaluando Top-{} candidatos con {} nuevas semillas (orden por z-score)...".format(
        len(candidatos), n_semillas))
    resultados_reeval = []

    for idx, ind in enumerate(candidatos, 1):
        z_scores_ds = []
        raw_scores_ds = {}
        raw_z_ds = {}

        for ds in suite:
            scores_pliegues = []
            for s in range(n_semillas):
                semilla = 5000 + s * 37
                for pliegue in ds["pliegues"]:
                    _, score, _ = entrenar_pliegue(lambda: ActivacionLGP(ind), ds, pliegue, semilla=semilla, cfg=cfg)
                    scores_pliegues.append(score)

            score_medio_ds = float(np.mean(scores_pliegues))
            raw_scores_ds[ds["nombre"]] = round(score_medio_ds, 4)
            mu_j = baseline_ref[ds["nombre"]]["mu"]
            sd_j = baseline_ref[ds["nombre"]]["sd"]
            sd_eff = max(sd_j, 0.002)
            z_j = float(np.clip((score_medio_ds - mu_j) / sd_eff, -3.0, 3.0))
            raw_z_ds[ds["nombre"]] = round(z_j, 4)
            z_scores_ds.append(z_j)

        z_medio = float(np.mean(z_scores_ds))
        f_reeval = float(-z_medio)
        ind.f = f_reeval
        ind.f_detalles = raw_scores_ds
        ind.z_detalles = raw_z_ds

        resultados_reeval.append((ind, z_medio, f_reeval))
        print("  Candidato {:2d} | z-medio={:+.4f} (f={:+.4f}) | AUC={:.4f} | {}".format(
            idx, z_medio, f_reeval, float(np.mean(list(raw_scores_ds.values()))), formula(ind)[:55]))

    # Ordenar por f_reeval ascendente (menor f = mayor z-medio = mejor desempeno)
    resultados_reeval.sort(key=lambda item: item[2])
    return [item[0] for item in resultados_reeval]


# -------------------------------------------------------------
# CONTROLES CON EXACTO PRESUPUESTO DE EVALUACIONES (B5)
# -------------------------------------------------------------
def busqueda_aleatoria_multidataset(suite, cfg, presupuesto, baseline_ref):
    """Control de Busqueda Aleatoria pura evaluada hasta agotar el exacto presupuesto."""
    random.seed(777)
    cont = Contador()
    archivo = Archivo()
    t0 = time.time()
    curva_rand = []

    with Spinner("  [Aleatoria] Evaluando {} candidatos efectivos".format(presupuesto)):
        while cont.n < presupuesto:
            ind = ind_aleatorio(cfg["L"])
            if g1(ind, cfg.get("EPS_NL", 0.05)) > 0.0:
                continue
            evaluar_fitness_multidataset(ind, suite, cfg, cont, baseline_ref)
            if ind.es_factible:
                archivo.agregar(ind)
                curva_rand.append((cont.n, archivo.top(1)[0].f))

    print("  Busqueda aleatoria finalizada: {} evals en {:.1f} min".format(cont.n, (time.time() - t0) / 60))
    return archivo, curva_rand


# -------------------------------------------------------------
# EVALUACION EXHAUSTIVA Y ESTADISTICA RIGUROSA (B6)
# -------------------------------------------------------------
def holm(pvals):
    """Ajuste de Holm paso a paso (step-down)."""
    m = len(pvals)
    orden = np.argsort(pvals)
    aj = np.zeros(m)
    mx = 0.0
    for rank, i in enumerate(orden):
        v = (m - rank) * pvals[i]
        mx = max(mx, v)
        aj[i] = min(1.0, mx)
    return aj


def evaluar_suite_exhaustiva(suite, cfg, metodos_dict, n_semillas=5, titulo="", es_cordura=False, baseline_ref=None):
    """
    Evalua los metodos en una suite dada sobre n_semillas x pliegues.
    Aplica rigurosamente la metodologia estadistica para K-Fold (B6, T9.f):
      1. Promedia sobre semillas DENTRO de cada pliegue, evitando pseudoreplicacion.
      2. Reporta SIEMPRE AUC crudo y z-scores por dataset (T9.f).
      3. Alerta cuando un dataset tiene varianza reducida (sd < 0.005) (T9.f).
      4. Aplica prueba t remuestreada corregida de Nadeau y Bengio (2003) sobre los pliegues.
      5. Reporta intervalos de confianza al 95% para la diferencia media.
      6. Aplica prueba pareada de Wilcoxon sobre pliegues y ajuste de Holm.
      7. Prueba no parametrica de Friedman entre datasets (excluida si es_cordura=True) (Demsar, 2006).
      8. Contador explicito de divergencias numericas.
    """
    print("\n" + "=" * 90)
    print("EVALUACION EXHAUSTIVA: {} ({} semillas x K-Fold)".format(titulo, n_semillas))
    print("=" * 90)

    # Estructura: tabla_pliegues[ds_nombre][metodo][pliegue_idx] = lista de scores por semilla
    tabla_pliegues = {ds["nombre"]: {m: [[] for _ in ds["pliegues"]] for m in metodos_dict} for ds in suite}
    divergencias = {m: 0 for m in metodos_dict}

    for ds in suite:
        K = len(ds["pliegues"])
        for s_idx in range(n_semillas):
            semilla = 7000 + s_idx * 23
            for p_idx, pliegue in enumerate(ds["pliegues"]):
                for m_nombre, act_fn in metodos_dict.items():
                    _, sc, div = entrenar_pliegue(act_fn, ds, pliegue, semilla=semilla, cfg=cfg)
                    if div:
                        divergencias[m_nombre] += 1
                    tabla_pliegues[ds["nombre"]][m_nombre][p_idx].append(sc)

    # 1. Medias por pliegue y medias globales
    fold_means = {ds["nombre"]: {} for ds in suite}
    medias_por_dataset = {ds["nombre"]: {} for ds in suite}

    for ds in suite:
        for m in metodos_dict:
            f_means = [float(np.mean(tabla_pliegues[ds["nombre"]][m][p])) for p in range(len(ds["pliegues"]))]
            fold_means[ds["nombre"]][m] = np.array(f_means)
            medias_por_dataset[ds["nombre"]][m] = float(np.mean(f_means))

    # 1.a Tabla de Rendimiento Medio (AUC Crudo)
    headers = ["Dataset"] + list(metodos_dict.keys())
    print("\n[T9.f] Tabla de Rendimiento Medio (Score = AUC Crudo float64):")
    fmt = "{:<36}" + "{:>11}" * len(metodos_dict)
    print("-" * (36 + 11 * len(metodos_dict)))
    print(fmt.format(*headers))
    print("-" * (36 + 11 * len(metodos_dict)))

    for ds_nombre in medias_por_dataset:
        fila = [ds_nombre[:34]]
        for m in metodos_dict:
            fila.append("{:.4f}".format(medias_por_dataset[ds_nombre][m]))
        print(fmt.format(*fila))
    print("-" * (36 + 11 * len(metodos_dict)))

    # 1.b Tabla de z-scores normalizados (T9.f)
    print("\n[T9.f] Tabla Normalizada de z-Scores (frente a ReLU, clip [-3, 3]):")
    print("-" * (36 + 11 * len(metodos_dict)))
    print(fmt.format(*headers))
    print("-" * (36 + 11 * len(metodos_dict)))

    avisos_sd = []
    z_por_dataset = {ds["nombre"]: {} for ds in suite}
    for ds in suite:
        nom = ds["nombre"]
        fila_z = [nom[:34]]
        # Calcular mu y sd de ReLU
        if baseline_ref and nom in baseline_ref:
            mu_ref = baseline_ref[nom]["mu"]
            sd_ref = baseline_ref[nom]["sd"]
        elif "ReLU" in fold_means[nom]:
            mu_ref = float(np.mean(fold_means[nom]["ReLU"]))
            sd_ref = float(np.std(fold_means[nom]["ReLU"]))
        else:
            mu_ref = float(np.mean(list(medias_por_dataset[nom].values())))
            sd_ref = 0.02
        
        sd_eff = max(sd_ref, 0.002)
        if sd_ref < 0.005:
            avisos_sd.append("  [AVISO T9.f] Dataset '{}' tiene sd={:.5f} < 0.005; domina z-score ponderado por sd_eff={:.4f}.".format(
                nom, sd_ref, sd_eff))

        for m in metodos_dict:
            sc_m = medias_por_dataset[nom][m]
            z_val = float(np.clip((sc_m - mu_ref) / sd_eff, -3.0, 3.0))
            z_por_dataset[nom][m] = z_val
            fila_z.append("{:+7.4f}".format(z_val))
        print(fmt.format(*fila_z))
    print("-" * (36 + 11 * len(metodos_dict)))

    if avisos_sd:
        print("\nAlertas de varianza metodologica reducida (T9.f):")
        for av in avisos_sd:
            print(av)

    # Divergencias
    print("\nContador de Divergencias Numericas:")
    for m, c in divergencias.items():
        print("  - {:<20}: {:d} divergencias".format(m, c))

    # 2. Inferencia Estadistica: Nadeau & Bengio (2003) e Intervalos de Confianza (B6)
    ref = list(metodos_dict.keys())[0]
    print("\nInferencia Estadistica Pareada por Pliegue (vs {}) con Correccion de Nadeau & Bengio (2003):".format(ref))
    for ds in suite:
        ds_nombre = ds["nombre"]
        K = len(ds["pliegues"])
        print("  * Dataset: " + ds_nombre)
        otros = [m for m in metodos_dict if m != ref]
        pvals_t = []
        difs_list = []
        ic_list = []

        ratio_val = cfg.get("VAL_INTERNA_RATIO", 0.15)
        factor_nb = (1.0 / K) + (1.0 / max(1, K - 1))

        for o in otros:
            arr_ref = fold_means[ds_nombre][ref]
            arr_o = fold_means[ds_nombre][o]
            dif_pliegues = arr_ref - arr_o
            bar_d = float(np.mean(dif_pliegues))
            s_d = float(np.std(dif_pliegues, ddof=1)) if K > 1 else 0.0

            se_corr = float(np.sqrt(factor_nb * (s_d ** 2))) if s_d > 1e-12 else 1e-6
            t_stat = bar_d / se_corr
            df = max(1, K - 1)
            p_t = float(2.0 * (1.0 - stats.t.cdf(abs(t_stat), df=df)))
            t_crit = float(stats.t.ppf(0.975, df=df))
            ci_low = bar_d - t_crit * se_corr
            ci_high = bar_d + t_crit * se_corr

            pvals_t.append(p_t)
            difs_list.append(bar_d)
            ic_list.append((ci_low, ci_high))

        p_holm = holm(pvals_t)
        for o, dif, (cil, cih), pt, ph in zip(otros, difs_list, ic_list, pvals_t, p_holm):
            sig = "SI" if ph < 0.05 else "no"
            print("      vs {:<14} Dif: {:+.4f} | IC 95%: [{:+.4f}, {:+.4f}] | p-corr: {:.4f} | p-Holm: {:.4f} | Sig: {}".format(
                o, dif, cil, cih, pt, ph, sig))

    # 3. Prueba de Friedman entre datasets (Demsar, 2006)
    if es_cordura:
        print("\n[Chequeo de Cordura T9.b]: Datasets saturados. Reportados aparte y EXCLUIDOS de la prueba de Friedman.")
    elif len(suite) >= 3 and len(metodos_dict) >= 3:
        matrices = [np.array([medias_por_dataset[ds["nombre"]][m] for ds in suite]) for m in metodos_dict]
        try:
            stat_f, p_f = stats.friedmanchisquare(*matrices)
            print("\nPrueba No Parametrica de Friedman entre Datasets (Demsar, 2006):")
            print("  Estadistico Chi2: {:.4f} | p-valor: {:.4f}".format(stat_f, p_f))
            if len(suite) < 8:
                print("  [Nota de Potencia Estadistica]: N_datasets = {} < 8 (potencia reducida; interpretese con cautela descriptiva).".format(len(suite)))
        except Exception:
            pass

    return medias_por_dataset, divergencias


# -------------------------------------------------------------
# COMPATIBILIDAD CON EXPORTACION E IMPORTACION (R11)
# -------------------------------------------------------------
def exportar_activaciones(ruta_json, top_inds, cfg):
    """
    Exporta las mejores activaciones descubiertas para su transferencia
    a Geotermia o analisis externo.
    """
    os.makedirs(os.path.dirname(os.path.abspath(ruta_json)), exist_ok=True)
    lista_export = []
    for rank, ind in enumerate(top_inds, 1):
        equiv, desc_eq, r_eq, rmse_eq = detectar_equivalencia(ind)
        lista_export.append(dict(
            rango=rank,
            formula=formula(ind),
            f=ind.f,
            g1=ind.g1,
            equivalente=equiv,
            clasificacion_equivalencia=desc_eq,
            correlacion=r_eq,
            rmse=rmse_eq,
            genes=ind.genes,
            e=[round(float(v), 4) for v in ind.e],
            f_detalles=ind.f_detalles,
            z_detalles=ind.z_detalles,
        ))

    payload = dict(
        timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
        top_activaciones=lista_export,
        mejor=lista_export[0] if lista_export else None,
        ensamble=lista_export,
    )
    with open(ruta_json, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print("  [Exportacion] Activaciones guardadas en: " + ruta_json)


def cargar_activaciones(ruta_json):
    """
    Carga activaciones desde JSON aceptando formato nuevo y formato legacy.
    Devuelve (mejor_ind, lista_ensamble).
    """
    with open(ruta_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    def _dict_a_ind(d):
        ind = Ind(d["genes"], d["e"])
        ind.f = d.get("f")
        ind.g1 = d.get("g1", 0.0)
        ind.es_factible = True
        return ind

    if "top_activaciones" in data and len(data["top_activaciones"]) > 0:
        inds = [_dict_a_ind(d) for d in data["top_activaciones"]]
        return inds[0], inds
    elif "mejor" in data and "ensamble" in data:
        mejor = _dict_a_ind(data["mejor"])
        ensamble = [_dict_a_ind(d) for d in data["ensamble"]]
        return mejor, ensamble
    raise ValueError("Formato de JSON de activaciones no reconocido.")
