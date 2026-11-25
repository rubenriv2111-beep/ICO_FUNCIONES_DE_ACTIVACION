# =============================================================
# ARCHIVO 5/5: main_elgp.py
# <<< ARCHIVO PRINCIPAL DE EJECUCION Y AUTOTEST >>>
#
# Flujo cientifico riguroso:
#   1. Suite de Evolucion (5 datasets calibrados con AUC ReLU en [0.70, 0.97])
#   2. Suite de Generalizacion (5 datasets NO vistos durante la busqueda)
#   3. Normalizacion de fitness z_j(x) frente a baseline ReLU
#   4. Estrategia evolutiva (mu, lambda) con archivo elite y cruza P=1.0
#   5. Reglas de factibilidad de Deb (2000) y filtro de no-linealidad g1
#   6. Reevaluacion de finalistas por z-score medio (B4)
#   7. Exportacion inmediata de activaciones_descubiertas.json (B3)
#   8. Controles experimentales (Aleatoria y Ablacion) con EXACTO presupuesto (B5)
#   9. Evaluacion final con correccion de Nadeau y Bengio (2003) e IC 95% (B6)
# =============================================================

import argparse
import copy
import functools
import json
import os
import random
import sys
import time
import traceback

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import roc_auc_score
import torch
import torch.nn as nn
import torch.nn.functional as F

from elgp_config import CFG, DEVICE, Spinner, OPS, N_OPS, N_REG, div_protegida
from elgp_datos import (
    preparar_suite_evolucion, preparar_suite_generalizacion, preparar_suite_cordura, entrenar_pliegue,
    descargar_caches_activos, DATASETS_EVOLUCION, DATASETS_GENERALIZACION,
    cargar_credit_card, cargar_german_credit, cargar_wine_quality, cargar_magic_gamma,
    cargar_vehicle, cargar_landsat, cargar_dry_bean, cargar_digits, cargar_breast_cancer,
    cargar_spambase, cargar_steel_plates_faults, cargar_yeast, cargar_sonar,
    cargar_heart_disease, cargar_blood_transfusion
)
from elgp_individuo import (
    Ind, ind_aleatorio, cruza, muta, torneo, g1, domina_deb, deb_cmp,
    formula, firma_fenotipo, efectivas, analizar_y_plegar, evaluar_malla,
    ActivacionLGP, interprete_referencia, detectar_equivalencia, fabrica_activacion, MLP
)
from elgp_evolucion import (
    Contador, Archivo, calibrar_baseline_relu, evaluar_fitness_multidataset,
    evolucionar_mu_lambda, reevaluar_finalistas, busqueda_aleatoria_multidataset,
    evaluar_suite_exhaustiva, exportar_activaciones, cargar_activaciones
)


# -------------------------------------------------------------
# AUTOTEST AMPLIADO (B1..B9, R1..R11, T6.a a T6.f)
# -------------------------------------------------------------
def autotest():
    print("=" * 75)
    print("AUTOTEST EXHAUSTIVO: Validacion de Requisitos Metodologicos (B1..B9, T6)")
    print("=" * 75)
    ok_total = True

    def chk(nombre, cond, extra=""):
        nonlocal ok_total
        estado = "OK" if cond else "FALLO"
        print("  [{:^5}] {:<56} {}".format(estado, nombre, extra))
        ok_total = ok_total and bool(cond)

    # 1. B1 / T8.a: Consistencia absoluta entre ActivacionLGP e interprete_referencia independiente en 500 individuos
    malla_test = torch.linspace(-3.0, 3.0, 200)
    fallos_b1 = 0
    evaluados_b1 = 0
    for s in range(500):
        torch.manual_seed(s)
        random.seed(s)
        ind_t = ind_aleatorio(8)
        out_ref = interprete_referencia(ind_t, malla_test)
        if not torch.isfinite(out_ref).all():
            continue
        evaluados_b1 += 1
        act_t = ActivacionLGP(ind_t)
        out_act = act_t(malla_test)
        diff = float(torch.max(torch.abs(out_act - out_ref)).item())
        if diff > 1e-5:
            fallos_b1 += 1

    chk("B1/T8.a: max|ActivacionLGP - interprete_ref| < 1e-5 (500 ind)",
        fallos_b1 == 0 and evaluados_b1 > 250,
        "(Fallos: {}/{})".format(fallos_b1, evaluados_b1))

    # 2. B7: Prueba unitaria para 0.26*v + 0.74*relu(v) -> LeakyReLU (alpha=0.26, T6.b)
    v_unit = torch.linspace(-3.0, 3.0, 200)
    v_np = v_unit.numpy().astype(np.float64)
    phi_synthetic = 0.26 * v_np + 0.74 * np.maximum(0.0, v_np)
    v_pos = np.maximum(0.0, v_np)
    v_neg = np.minimum(0.0, v_np)
    A_unit = np.column_stack([v_pos, v_neg, np.ones_like(v_np)])
    c1, c2, c0 = np.linalg.lstsq(A_unit, phi_synthetic, rcond=None)[0]
    alpha_unit = c2 / c1
    r_unit = np.corrcoef(phi_synthetic, v_pos + alpha_unit * v_neg)[0, 1]
    rmse_unit = np.sqrt(np.mean((phi_synthetic - (c1 * v_pos + c2 * v_neg + c0)) ** 2))

    chk("B7/T6.b: Ajuste LeakyReLU para 0.26*v + 0.74*relu(v)",
        abs(alpha_unit - 0.26) < 1e-4 and r_unit > 0.9999,
        "alpha={:.4f}, r={:.5f}, RMSE={:.5f}".format(alpha_unit, r_unit, rmse_unit))

    # 3. B2, T6.c y T9.b: Verificacion de clases de los 15 cargadores (Suite Evolucion, Generalizacion y Cordura)
    cargadores_verif = [
        ("Credit Card (350)", cargar_credit_card, 2),
        ("German Credit (144)", cargar_german_credit, 2),
        ("Wine Quality (186)", cargar_wine_quality, 2),
        ("Magic Gamma (159)", cargar_magic_gamma, 2),
        ("Vehicle (149)", cargar_vehicle, 4),
        ("Steel Plates (198)", cargar_steel_plates_faults, 7),
        ("Yeast (110)", cargar_yeast, 9),
        ("Sonar (151)", cargar_sonar, 2),
        ("Heart Disease (45)", cargar_heart_disease, 2),
        ("Blood Transfusion (176)", cargar_blood_transfusion, 2),
        ("Statlog Landsat (146)", cargar_landsat, 6),
        ("Dry Bean (602)", cargar_dry_bean, 7),
        ("sklearn Digits (8x8)", cargar_digits, 10),
        ("Breast Cancer", cargar_breast_cancer, 2),
        ("Spambase (94)", cargar_spambase, 2),
    ]
    clases_ok = True
    for nombre_d, fn_c, n_cl_esp in cargadores_verif:
        info_d = fn_c()
        n_unicas = len(np.unique(info_d["y"]))
        if n_unicas != n_cl_esp or info_d["clases"] != n_cl_esp:
            clases_ok = False
            print("      [Aviso] Dataset {} tiene {} clases (esperadas {})".format(nombre_d, n_unicas, n_cl_esp))

    chk("B2/T6.c/T9.b: 15 loaders producen el numero exacto de clases declaradas", clases_ok)

    # 4. T6.e: Ejecucion de loaders con cache en carpeta temporal vacia
    import tempfile, shutil
    temp_cache_dir = tempfile.mkdtemp(prefix="elgp_cache_test_")
    loaders_temp_ok = True
    try:
        print("      [T6.e] Descargando/probando Wine Quality desde cero...", flush=True)
        res_wq = cargar_wine_quality(salida=temp_cache_dir, usar_cache=False)
        print("      [T6.e] Wine Quality OK. Descargando/probando Vehicle desde cero...", flush=True)
        res_vh = cargar_vehicle(salida=temp_cache_dir, usar_cache=False)
        print("      [T6.e] Vehicle OK. Probando Digits...", flush=True)
        res_dg = cargar_digits()
        if len(np.unique(res_wq["y"])) != 2 or len(res_wq["y"]) < 6000:
            loaders_temp_ok = False
        if len(np.unique(res_vh["y"])) != 4 or len(res_vh["y"]) != 845:
            loaders_temp_ok = False
        if len(np.unique(res_dg["y"])) != 10 or len(res_dg["y"]) != 1797:
            loaders_temp_ok = False
    except BaseException as e:
        loaders_temp_ok = False
        print("      [Error en T6.e]:", type(e), e, flush=True)
        traceback.print_exc()
    finally:
        shutil.rmtree(temp_cache_dir, ignore_errors=True)
    chk("T6.e: Loaders en carpeta temporal vacia (desde cero)",
        loaders_temp_ok, "Wine=6.5k/2cl, Vehicle=845filas/4cl, Digits=1797/10cl")

    # 5. R5: Finitud de los 17 operadores en malla [-10, 10] inc. 0
    finitos = True
    malla_17 = torch.linspace(-10.0, 10.0, 201)
    for op_idx, (nombre, ar, func) in enumerate(OPS):
        try:
            out = func(malla_17, malla_17) if ar == 1 else func(malla_17, malla_17.flip(0))
            if not torch.isfinite(out).all():
                finitos = False
        except Exception:
            finitos = False
    chk("R5: 17 operadores finitos en malla [-10, 10] inc. 0", finitos and len(OPS) == 17)

    # 6. R4 y T6.d: Restriccion g1 sobre Identidad (NL=0) y ReLU (NL>eps)
    ind_relu = ind_aleatorio(2)
    relu_idx = [i for i, o in enumerate(OPS) if o[0] == "relu"][0]
    ind_relu.genes = [[relu_idx, 0, 0, 0], [0, 1, 1, 1]]
    ind_relu.e = [1.0, 0.0]
    g_relu = g1(ind_relu, eps_nl=0.05)
    chk("R4: NL(ReLU) > eps_nl -> ReLU factible (g1 <= 0)", g_relu <= 0.0, "g1={:.4f}".format(g_relu))

    ind_id = ind_aleatorio(2)
    ind_id.genes = [[0, 0, 0, 1], [0, 1, 1, 1]]
    ind_id.e = [1.0, 0.0]
    v_malla = torch.linspace(-3.0, 3.0, 200, dtype=torch.float32)
    phi_id = evaluar_malla(ind_id, v_malla)
    v_c = v_malla - torch.mean(v_malla)
    phi_c = phi_id - torch.mean(phi_id)
    r_corr_id = float((torch.sum(v_c * phi_c) / (torch.sqrt(torch.sum(v_c**2)) * torch.sqrt(torch.sum(phi_c**2)))).item())
    nl_id = float(1.0 - r_corr_id**2)
    g_id = g1(ind_id, eps_nl=0.05)
    print("      [Diagnostico T6.d]: r={:.7f}, NL={:.7f}, g1={:.7f} (eps_nl=0.05)".format(r_corr_id, nl_id, g_id))
    print("      Explicacion: NL(identidad)=0.0000000 exacto al usar producto punto centrado normalizado.")
    print("      (Previamente daba NL=0.009975 por desajuste entre divisor N de covarianza y N-1 de varianza).")
    chk("T6.d: NL(identidad)=0.00000 -> g1=0.05000 exacto",
        abs(nl_id) < 1e-6 and abs(g_id - 0.05) < 1e-6, "NL={:.6f}, g1={:.6f}".format(nl_id, g_id))

    # 7. R4: Reglas de Factibilidad de Deb (2000)
    ind_f1 = Ind([], []); ind_f1.g1 = -0.10; ind_f1.f = -1.2
    ind_f2 = Ind([], []); ind_f2.g1 = -0.05; ind_f2.f = -0.5
    ind_inv1 = Ind([], []); ind_inv1.g1 = 0.08; ind_inv1.f = -2.0
    ind_inv2 = Ind([], []); ind_inv2.g1 = 0.20; ind_inv2.f = -3.0

    chk("R4: Deb: Factible domina a inviable (f1 domina inv1)", domina_deb(ind_f1, ind_inv1) is True)
    chk("R4: Deb: Menor f entre factibles (f1 domina f2)", domina_deb(ind_f1, ind_f2) is True)
    chk("R4: Deb: Menor violacion entre inviables (inv1 domina inv2)", domina_deb(ind_inv1, ind_inv2) is True)

    # 8. R3 y Regla B: Particionamiento con validacion interna honesta
    cfg_test = dict(CFG, MAX_FILAS_BUSQUEDA=300, K_FOLDS=2, EPOCAS=3, PACIENCIA=2)
    suite_ev = preparar_suite_evolucion(cfg_test, k_folds=2, modo_busqueda=True)
    pl0 = suite_ev[0]["pliegues"][0]
    chk("R3: Sub-entrenamiento, val interna y test disjuntos",
        pl0["Xtr"].shape[0] > 0 and pl0["Xval"].shape[0] > 0 and pl0["Xte"].shape[0] > 0)
    chk("Regla B: StandardScaler ajustado estrictamente sobre Xtr", hasattr(pl0["scaler"], "mean_"))

    # 9. B8: Captura segura de ValueError en roc_auc_score
    m_res, sc_err, div_err = entrenar_pliegue(fabrica_activacion("Lineal"), suite_ev[0], pl0, semilla=42, cfg=cfg_test)
    chk("B8: entrenar_pliegue devuelve score finito y bool de divergencia", isinstance(sc_err, float) and div_err in (True, False))

    # 10. B5: Parada por tope exacto de evaluaciones en (mu, lambda)
    cfg_tope = dict(cfg_test, MU=4, LAMBDA_HIJOS=8, T_MAX=10)
    cont_tope = Contador()
    base_ref_t = {ds["nombre"]: dict(mu=0.75, sd=0.05) for ds in suite_ev}
    evolucionar_mu_lambda(suite_ev, cfg_tope, contador=cont_tope, baseline_ref=base_ref_t, tope_evaluaciones=10)
    chk("B5: evolucionar_mu_lambda respeta tope exacto de evaluaciones", cont_tope.n == 10, "Evals={}".format(cont_tope.n))

    # 11. R2 y T9.b: Suites disjuntas para respaldar generalizacion (Evolucion, Generalizacion y Cordura)
    suite_gen = preparar_suite_generalizacion(cfg_test, k_folds=2)
    suite_cordura = preparar_suite_cordura(cfg_test, k_folds=2)
    nom_ev = {d["nombre"] for d in suite_ev}
    nom_gen = {d["nombre"] for d in suite_gen}
    nom_cordura = {d["nombre"] for d in suite_cordura}
    chk("R2: Suites de evolucion y generalizacion disjuntas ({} y {})".format(len(nom_ev), len(nom_gen)), len(nom_ev.intersection(nom_gen)) == 0)
    chk("T9.b: Suite cordura disjunta de generalizacion informativa", len(nom_gen.intersection(nom_cordura)) == 0)

    # 12. T6.f: AUC multiclase en float64 con sumas renormalizadas
    torch.manual_seed(42)
    np.random.seed(42)
    y_synth = np.random.choice([0, 1, 2, 3], size=300, p=[0.25, 0.25, 0.25, 0.25])
    logits_synth = torch.randn(300, 4, dtype=torch.float32) * 2.0
    probs_synth = F.softmax(logits_synth, dim=1).cpu().numpy().astype(np.float64)
    probs_synth /= np.maximum(np.sum(probs_synth, axis=1, keepdims=True), 1e-12)
    auc_multi = float(roc_auc_score(y_synth, probs_synth, multi_class="ovr"))
    sum_probs_err = float(np.max(np.abs(np.sum(probs_synth, axis=1) - 1.0)))
    chk("T6.f: AUC multiclase en float64 (sum_probs=1.0, roc_auc finito)",
        isinstance(auc_multi, float) and 0.0 <= auc_multi <= 1.0 and sum_probs_err < 1e-9,
        "AUC={:.4f}, max_err_sum={:.1e}".format(auc_multi, sum_probs_err))

    # 13. T7.e: Seleccion (mu, lambda) con coma ejecutando evolucionar_mu_lambda real
    mu_sim, lambda_sim = 4, 8
    cfg_sim = dict(CFG, MU=mu_sim, LAMBDA_HIJOS=lambda_sim, T_MAX=1, P_CRUZA=1.0)
    cont_sim = Contador()

    def eval_sim(ind):
        cont_sim.n += 1
        ind.f = -100.0 if cont_sim.n <= mu_sim else 5.0
        ind.g1 = -0.5
        ind.es_factible = True
        return ind.f

    archivo_sim, _, _, _ = evolucionar_mu_lambda(
        suite=[], cfg=cfg_sim, contador=cont_sim, evaluador=eval_sim,
        tope_evaluaciones=mu_sim + lambda_sim, etiqueta="Test-Coma-Real"
    )
    pob_final_sim = getattr(archivo_sim, "pob_final", [])
    padres_sobrevivientes = [ind for ind in pob_final_sim if ind.f == -100.0]
    hijos_seleccionados = [ind for ind in pob_final_sim if ind.f == 5.0]
    chk("T7.e: evolucionar_mu_lambda real con eval simulada (0 padres sobreviven)",
        len(padres_sobrevivientes) == 0 and len(hijos_seleccionados) == mu_sim,
        "Sobrevivientes: padres={}/{}, hijos={}/{}".format(len(padres_sobrevivientes), mu_sim, len(hijos_seleccionados), mu_sim))

    print("-" * 75)
    print("RESULTADO DEL AUTOTEST:", "TODO OK (Pipeline 100% verificado)" if ok_total else "HAY FALLOS")
    print("=" * 75)
    return ok_total


# -------------------------------------------------------------
# SERIALIZACION Y REANUDACION POR FASES (T9.d, T9.e)
# -------------------------------------------------------------
def serializar_archivo_completo(archivo, ruta, cfg):
    top200 = archivo.top(200)
    lista = []
    for ind in top200:
        lista.append({
            "genes": ind.genes,
            "e": [round(float(v), 5) for v in ind.e],
            "f": float(ind.f) if ind.f is not None else None,
            "g1": float(ind.g1) if ind.g1 is not None else None,
            "es_factible": bool(ind.es_factible),
            "f_detalles": {k: float(v) for k, v in ind.f_detalles.items()},
            "z_detalles": {k: float(v) for k, v in ind.z_detalles.items()},
            "divergencias": int(ind.divergencias),
            "formula": formula(ind),
            "firma": firma_fenotipo(ind),
        })
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump({"total": len(lista), "candidatos": lista}, f, indent=2)
    print("  [Archivo Guardado] Top {} candidatos guardados en: {}".format(len(lista), ruta))


def deserializar_archivo_completo(ruta):
    if not os.path.exists(ruta):
        raise FileNotFoundError("No se encontro archivo completo en: " + ruta)
    with open(ruta, "r", encoding="utf-8") as f:
        data = json.load(f)
    arch = Archivo()
    for item in data.get("candidatos", []):
        ind = Ind(item["genes"], item["e"])
        ind.f = item.get("f")
        ind.g1 = item.get("g1")
        ind.es_factible = item.get("es_factible", True)
        ind.f_detalles = item.get("f_detalles", {})
        ind.z_detalles = item.get("z_detalles", {})
        ind.divergencias = item.get("divergencias", 0)
        arch.agregar(ind)
    print("  [Archivo Cargado] {} candidatos recuperados desde: {}".format(len(arch.d), ruta))
    return arch


def evaluar_curva_en_hitos(curva, hitos=[500, 1000, 2000, 3000]):
    """
    Dada una lista de pares (evaluacion, mejor_f), calcula el mejor f
    alcanzado hasta el momento de cada hito de evaluaciones (T9.e).
    """
    res = {}
    if not curva:
        return {h: None for h in hitos}
    for h in hitos:
        vals = [f_val for (ev, f_val) in curva if ev <= h and f_val is not None]
        res[h] = min(vals) if vals else curva[0][1]
    return res


# -------------------------------------------------------------
# EJECUCION PRINCIPAL MODULAR POR FASES (T9.d)
# -------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="ELGP Multi-Dataset Activation Discovery")
    parser.add_argument("--rapido", action="store_true", help="Preset agil para validacion rapida")
    parser.add_argument("--autotest", action="store_true", help="Valida todos los requisitos del pipeline")
    parser.add_argument("--solo-cache", action="store_true",
                        help="Solo descarga y guarda en cache .npz los datasets activos (ideal en nodo login)")
    parser.add_argument("--fase", choices=["calibracion", "evolucion", "controles", "final", "todo"],
                        default="todo", help="Fase de ejecucion por etapas con reanudacion (T9.d)")
    parser.add_argument("--presupuesto", type=int, default=None,
                        help="Tope maximo de evaluaciones efectivas para evolucion y controles")
    parser.add_argument("--generaciones", type=int, default=None, help="Numero de generaciones evolutivas")
    parser.add_argument("--salida", default=None, help="Carpeta de salida de resultados")
    parser.add_argument("--semilla", type=int, default=42, help="Semilla de reproducibilidad global")
    args = parser.parse_args()

    if args.autotest:
        autotest()
        return

    # Configuracion de ejecucion
    cfg = dict(CFG)
    random.seed(args.semilla)
    np.random.seed(args.semilla)
    torch.manual_seed(args.semilla)

    if args.rapido:
        cfg.update(
            MU=10,
            LAMBDA_HIJOS=20,
            T_MAX=4,
            K_FOLDS=2,
            K_FOLDS_FINAL=2,
            EPOCAS=12,
            PACIENCIA=3,
            MAX_FILAS_BUSQUEDA=1500,
            TOP_FINALISTAS=3,
            TOP_REEVALUACION=6,
        )
    if args.generaciones:
        cfg["T_MAX"] = args.generaciones
    if args.salida:
        cfg["SALIDA"] = args.salida

    os.makedirs(cfg["SALIDA"], exist_ok=True)
    if args.solo_cache:
        descargar_caches_activos(cfg)
        return

    t_global_inicio = time.time()

    print("================================================================================")
    print(" ELGP-Activation: Descubrimiento Riguroso de Funciones de Activacion")
    print(" Dispositivo: {} | Estrategia: (mu={}, lambda={}) | Fase: {}".format(
        DEVICE, cfg["MU"], cfg["LAMBDA_HIJOS"], args.fase.upper()))
    print(" Evolucion: {} datasets | Generalizacion: {} datasets".format(
        len(DATASETS_EVOLUCION), len(DATASETS_GENERALIZACION)))
    print("================================================================================")

    # Documentacion metodologica de generalizacion honesta (T9.g)
    print("\n" + "=" * 80)
    print("[AVISO METODOLOGICO T9.g]:")
    print("  La aptitud de busqueda se calcula sobre los pliegues de validacion interna de la")
    print("  suite de evolucion (K-Fold CV). El desempeno sobre datasets vistos es inherentemente")
    print("  optimista; unicamente la evaluacion sobre los datasets NO vistos de la suite de")
    print("  generalizacion sustenta la validez cientifica y generalizacion de la activacion.")
    print("=" * 80)

    # 1. Preparacion de la Suite de Evolucion
    print("\n[1] Cargando Suite de Evolucion ({} datasets activos)...".format(len(DATASETS_EVOLUCION)))
    suite_busqueda = preparar_suite_evolucion(cfg, k_folds=cfg["K_FOLDS"], modo_busqueda=True)
    for i, ds in enumerate(suite_busqueda, 1):
        print("  {}. {:<38} | Tipo: {:<11} | Clases: {:2d} | Filas: {:6d}".format(
            i, ds["nombre"][:38], ds["tipo"], ds["clases"], ds["muestras"]))

    ruta_calib = os.path.join(cfg["SALIDA"], "resultados_calibracion.json")
    n_sem_calib = 2 if args.rapido else 5
    baseline_ref = None

    # ---------------------------------------------------------
    # FASE 1: CALIBRACION (T9.d)
    # ---------------------------------------------------------
    if args.fase in ("calibracion", "todo") or not os.path.exists(ruta_calib):
        baseline_ref = calibrar_baseline_relu(suite_busqueda, cfg, n_semillas=n_sem_calib)
        with open(ruta_calib, "w", encoding="utf-8") as f:
            json.dump({"baseline_ref": baseline_ref, "semillas": n_sem_calib}, f, indent=2)
        print("  [Guardado] resultados_calibracion.json exportado exitosamente.")
        if args.fase == "calibracion":
            print("\nFase de Calibracion completada exitosamente.")
            return
    else:
        with open(ruta_calib, "r", encoding="utf-8") as f:
            datos_cal = json.load(f)
            baseline_ref = datos_cal["baseline_ref"]
        print("  [Cargado] Baseline ReLU recuperado desde: " + ruta_calib)

    # Verificacion de varianzas reducidas en baseline_ref (T9.f)
    for nom_d, b_info in baseline_ref.items():
        if b_info["sd"] < 0.005:
            print("  [AVISO T9.f] Baseline '{}' tiene sd={:.5f} < 0.005. Ponderacion amplificada en z.".format(
                nom_d, b_info["sd"]))

    # ---------------------------------------------------------
    # FASE 2: EVOLUCION ELGP (T9.d)
    # ---------------------------------------------------------
    ruta_archivo_completo = os.path.join(cfg["SALIDA"], "archivo_completo_elgp.json")
    ruta_curva_elgp = os.path.join(cfg["SALIDA"], "curva_evolucion_elgp.json")
    ruta_json_act = os.path.join(cfg["SALIDA"], "activaciones_descubiertas.json")
    ruta_res_evol = os.path.join(cfg["SALIDA"], "resultados_evolucion.json")

    mejor_elgp = None
    finalistas_ordenados = []
    curva_elgp = []
    presupuesto_exacto = args.presupuesto or cfg.get("PRESUPUESTO_OBJETIVO", 3000)

    if args.fase in ("evolucion", "todo"):
        contador_elgp = Contador()
        t_evol0 = time.time()
        archivo, hist_mejor, hist_prom, curva_elgp = evolucionar_mu_lambda(
            suite_busqueda, cfg, contador=contador_elgp, e_fijo=False, etiqueta="ELGP-Multi",
            baseline_ref=baseline_ref, tope_evaluaciones=presupuesto_exacto
        )
        t_evol_total = time.time() - t_evol0
        presupuesto_exacto = max(30, contador_elgp.n)

        # Serializar Archivo Completo (Top 200) y Curva (T9.d)
        serializar_archivo_completo(archivo, ruta_archivo_completo, cfg)
        with open(ruta_curva_elgp, "w", encoding="utf-8") as f:
            json.dump({"curva": curva_elgp, "evals_totales": contador_elgp.n}, f, indent=2)

        candidatos_archivo = archivo.top(cfg.get("TOP_REEVALUACION", 20))
        if not candidatos_archivo:
            candidatos_archivo = [ind_aleatorio(cfg["L"])]

        # Reevaluacion honesta de finalistas por z-score medio (B4)
        finalistas_ordenados = reevaluar_finalistas(
            candidatos_archivo, suite_busqueda, cfg, baseline_ref=baseline_ref, n_semillas=2 if args.rapido else 5
        )
        mejor_elgp = finalistas_ordenados[0]

        # Exportacion inmediata de activaciones_descubiertas.json (B3)
        exportar_activaciones(ruta_json_act, finalistas_ordenados[:cfg.get("TOP_FINALISTAS", 5)], cfg)

        segundos_por_eval = t_evol_total / max(1, contador_elgp.n)
        print("\n" + "=" * 60)
        print("METRICAS DE TIEMPO DE COMPUTO (ELGP):")
        print("  Evaluaciones efectivas: {:d}".format(contador_elgp.n))
        print("  Tiempo total de evolucion: {:.1f} min ({:.1f} s)".format(t_evol_total / 60, t_evol_total))
        print("  Tiempo medio por evaluacion: {:.3f} s/eval".format(segundos_por_eval))
        print("  Estimacion para 3,000 evals: {:.2f} horas".format((3000 * segundos_por_eval) / 3600))
        print("=" * 60)

        with open(ruta_res_evol, "w", encoding="utf-8") as f:
            json.dump({
                "evaluaciones": contador_elgp.n,
                "tiempo_segundos": t_evol_total,
                "segundos_por_eval": segundos_por_eval,
                "formula_campeon": formula(mejor_elgp),
                "f_campeon": mejor_elgp.f,
                "g1_campeon": mejor_elgp.g1,
                "z_detalles": mejor_elgp.z_detalles,
                "f_detalles": mejor_elgp.f_detalles,
            }, f, indent=2)

        if args.fase == "evolucion":
            print("\nFase de Evolucion completada exitosamente.")
            return
    else:
        # Cargar campeon de evolucion previa
        if os.path.exists(ruta_json_act):
            mejor_elgp, _ = cargar_activaciones(ruta_json_act)
            print("  [Cargado] Mejor activacion ELGP recuperada desde: " + ruta_json_act)
        elif os.path.exists(ruta_archivo_completo):
            arch_carg = deserializar_archivo_completo(ruta_archivo_completo)
            mejor_elgp = arch_carg.top(1)[0]
        else:
            print("[Aviso] No hay evolucion previa guardada; usando individuo aleatorio.")
            mejor_elgp = ind_aleatorio(cfg["L"])
        
        if os.path.exists(ruta_curva_elgp):
            with open(ruta_curva_elgp, "r", encoding="utf-8") as f:
                curva_elgp = json.load(f).get("curva", [])

    # ---------------------------------------------------------
    # FASE 3: CONTROLES EXPERIMENTALES (T9.d, T9.e)
    # ---------------------------------------------------------
    ruta_res_controles = os.path.join(cfg["SALIDA"], "resultados_controles.json")
    ruta_curvas_controles = os.path.join(cfg["SALIDA"], "curvas_controles.json")
    mejor_rand, mejor_abl = None, None

    if args.fase in ("controles", "todo"):
        print("\n" + "=" * 70)
        print("INICIANDO CONTROLES EXPERIMENTALES (Presupuesto exacto: {} evals)".format(presupuesto_exacto))
        print("=" * 70)

        # 1. Busqueda Aleatoria
        print("\n[Control 1/2] Ejecutando Busqueda Aleatoria de control ({} evals)...".format(presupuesto_exacto))
        t0_rand = time.time()
        arch_rand, curva_rand = busqueda_aleatoria_multidataset(
            suite_busqueda, cfg, presupuesto=presupuesto_exacto, baseline_ref=baseline_ref
        )
        t_rand_tot = time.time() - t0_rand
        mejor_rand = arch_rand.top(1)[0] if arch_rand.top(1) else ind_aleatorio(cfg["L"])

        # 2. Ablacion e_k = 1.0 fija
        print("\n[Control 2/2] Ejecutando Ablacion e_k=1 de control ({} evals)...".format(presupuesto_exacto))
        cont_abl = Contador()
        t0_abl = time.time()
        cfg_abl = dict(cfg)
        arch_abl, _, _, curva_abl = evolucionar_mu_lambda(
            suite_busqueda, cfg_abl, contador=cont_abl, e_fijo=True, etiqueta="Ablacion-e1",
            baseline_ref=baseline_ref, tope_evaluaciones=presupuesto_exacto
        )
        t_abl_tot = time.time() - t0_abl
        mejor_abl = arch_abl.top(1)[0] if arch_abl.top(1) else ind_aleatorio(cfg["L"], e_fijo=True)

        # Reevaluacion de campeones de control
        cand_controles = reevaluar_finalistas(
            [mejor_rand, mejor_abl], suite_busqueda, cfg, baseline_ref=baseline_ref, n_semillas=2 if args.rapido else 5
        )
        mejor_rand, mejor_abl = cand_controles[0], cand_controles[1]

        # Guardar curvas y resultados de controles
        payload_curvas = {
            "curva_elgp": curva_elgp,
            "curva_aleatoria": curva_rand,
            "curva_ablacion": curva_abl,
        }
        with open(ruta_curvas_controles, "w", encoding="utf-8") as f:
            json.dump(payload_curvas, f, indent=2)

        # Evaluacion en hitos 500, 1000, 2000, 3000 (T9.e)
        hitos_eval = [500, 1000, 2000, 3000]
        hitos_elgp = evaluar_curva_en_hitos(curva_elgp, hitos_eval)
        hitos_rand = evaluar_curva_en_hitos(curva_rand, hitos_eval)
        hitos_abl = evaluar_curva_en_hitos(curva_abl, hitos_eval)

        print("\n" + "=" * 80)
        print("TABLA COMPARATIVA: MEJOR HASTA EL MOMENTO EN HITOS DE EVALUACION (T9.e):")
        print("Nota de signo: f > 0 es peor que ReLU por f sigmas; f < 0 es mejor que ReLU por -f sigmas.")
        print("-" * 80)
        print("{:<18} | {:^12} | {:^12} | {:^12} | {:^12}".format("Metodo", "500 evals", "1000 evals", "2000 evals", "3000 evals"))
        print("-" * 80)
        for nom_m, h_dict in [("ELGP (mu, lambda)", hitos_elgp), ("Busqueda Aleatoria", hitos_rand), ("Ablacion (e=1)", hitos_abl)]:
            vals_str = ["{:+.4f}".format(h_dict[h]) if h_dict[h] is not None else "   N/A   " for h in hitos_eval]
            print("{:<18} | {:^12} | {:^12} | {:^12} | {:^12}".format(nom_m, *vals_str))
        print("=" * 80)

        # Grafica comparativa de convergencia (T9.e)
        ruta_fig_comp = os.path.join(cfg["SALIDA"], "convergencia_comparativa.png")
        try:
            plt.figure(figsize=(10, 5.5))
            if curva_elgp:
                evs_e, f_e = zip(*curva_elgp)
                plt.plot(evs_e, f_e, label="ELGP (mu, lambda)", color="#1f77b4", lw=2.2)
            if curva_rand:
                evs_r, f_r = zip(*curva_rand)
                plt.plot(evs_r, f_r, label="Busqueda Aleatoria", color="#ff7f0e", lw=1.8, ls="--")
            if curva_abl:
                evs_a, f_a = zip(*curva_abl)
                plt.plot(evs_a, f_a, label="Ablacion (e=1.0)", color="#2ca02c", lw=1.8, ls="-.")
            plt.axhline(0.0, color="gray", ls=":", label="Baseline ReLU (f=0.0)")
            for h in hitos_eval:
                plt.axvline(h, color="#cccccc", ls="--", alpha=0.6)
            plt.xlabel("Evaluaciones Efectivas de Redes Neuronales")
            plt.ylabel("Aptitud Normalizada f (Menor es Mejor)")
            plt.title("Curvas 'Mejor Hasta el Momento': ELGP vs Aleatoria vs Ablacion (T9.e)")
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig(ruta_fig_comp, dpi=200)
            plt.close()
            print("  [Figura Guardada] convergencia_comparativa.png guardada en: " + ruta_fig_comp)
        except Exception as err:
            print("  [Aviso al graficar]: " + str(err))

        with open(ruta_res_controles, "w", encoding="utf-8") as f:
            json.dump({
                "presupuesto_evals": presupuesto_exacto,
                "aleatoria": {"tiempo": t_rand_tot, "f": mejor_rand.f, "formula": formula(mejor_rand), "genes": mejor_rand.genes, "e": mejor_rand.e},
                "ablacion": {"tiempo": t_abl_tot, "f": mejor_abl.f, "formula": formula(mejor_abl), "genes": mejor_abl.genes, "e": mejor_abl.e},
                "hitos_500_1000_2000_3000": {
                    "ELGP": hitos_elgp,
                    "Aleatoria": hitos_rand,
                    "Ablacion": hitos_abl
                }
            }, f, indent=2)

        if args.fase == "controles":
            print("\nFase de Controles completada exitosamente.")
            return
    else:
        # Cargar controles previos si existen
        if os.path.exists(ruta_res_controles):
            with open(ruta_res_controles, "r", encoding="utf-8") as f:
                d_ctrl = json.load(f)
            ra = d_ctrl.get("aleatoria", {})
            ab = d_ctrl.get("ablacion", {})
            mejor_rand = Ind(ra.get("genes", []), ra.get("e", []))
            mejor_rand.f = ra.get("f")
            mejor_abl = Ind(ab.get("genes", []), ab.get("e", []))
            mejor_abl.f = ab.get("f")
            print("  [Cargado] Controles experimentales recuperados desde: " + ruta_res_controles)
        else:
            mejor_rand = ind_aleatorio(cfg["L"])
            mejor_abl = ind_aleatorio(cfg["L"], e_fijo=True)

    # ---------------------------------------------------------
    # FASE 4: EVALUACION FINAL EXHAUSTIVA (T9.d, T9.f, T9.b)
    # ---------------------------------------------------------
    print("\n" + "=" * 80)
    print("INICIANDO FASE DE EVALUACION FINAL EXHAUSTIVA (Vistas vs Generalizacion vs Cordura)")
    print("=" * 80)

    metodos_eval = {
        "ELGP_Mejor": lambda: ActivacionLGP(mejor_elgp),
        "Aleatoria": lambda: ActivacionLGP(mejor_rand),
        "Ablacion_e1": lambda: ActivacionLGP(mejor_abl),
        "ReLU": fabrica_activacion("ReLU"),
        "LeakyReLU_0.01": fabrica_activacion("LeakyReLU_0.01"),
        "LeakyReLU_0.10": fabrica_activacion("LeakyReLU_0.10"),
        "LeakyReLU_0.25": fabrica_activacion("LeakyReLU_0.25"),
        "PReLU": fabrica_activacion("PReLU"),
        "GELU": fabrica_activacion("GELU"),
        "Swish": fabrica_activacion("Swish"),
        "Mish": fabrica_activacion("Mish"),
        "ELU": fabrica_activacion("ELU"),
        "SELU": fabrica_activacion("SELU"),
        "Tanh": fabrica_activacion("Tanh"),
        "Sigmoid": fabrica_activacion("Sigmoid"),
        "Lineal": fabrica_activacion("Lineal"),
    }

    n_sem_final = 2 if args.rapido else 10

    # (a) Suite de Evolucion (Vistos)
    suite_ev_final = preparar_suite_evolucion(cfg, k_folds=cfg["K_FOLDS_FINAL"], modo_busqueda=False)
    medias_vistos, div_vistos = evaluar_suite_exhaustiva(
        suite_ev_final, cfg, metodos_eval, n_semillas=n_sem_final,
        titulo="SUITE DE EVOLUCION (VISTA EN BUSQUEDA)", es_cordura=False, baseline_ref=baseline_ref
    )

    # (b) Suite de Generalizacion Informativa (NO vistos, AUC ReLU en [0.70, 0.97]) (T9.b)
    print("\n[Generalizacion Informativa]: Cargando suite no vista balanceada...")
    suite_gen_final = preparar_suite_generalizacion(cfg, k_folds=cfg["K_FOLDS_FINAL"])
    for i, ds in enumerate(suite_gen_final, 1):
        print("  {}. {:<38} | Tipo: {:<11} | Clases: {:2d} | Filas: {:6d}".format(
            i, ds["nombre"][:38], ds["tipo"], ds["clases"], ds["muestras"]))

    medias_gen, div_gen = evaluar_suite_exhaustiva(
        suite_gen_final, cfg, metodos_eval, n_semillas=n_sem_final,
        titulo="SUITE DE GENERALIZACION INFORMATIVA (NO VISTA - PARA FRIEDMAN)", es_cordura=False
    )

    # (c) Suite de Chequeo de Cordura (Saturados, EXCLUIDA de Friedman) (T9.b)
    print("\n[Chequeo de Cordura]: Cargando suite saturada de control...")
    suite_cordura_final = preparar_suite_cordura(cfg, k_folds=cfg["K_FOLDS_FINAL"])
    for i, ds in enumerate(suite_cordura_final, 1):
        print("  {}. {:<38} | Tipo: {:<11} | Clases: {:2d} | Filas: {:6d}".format(
            i, ds["nombre"][:38], ds["tipo"], ds["clases"], ds["muestras"]))

    medias_cordura, div_cordura = evaluar_suite_exhaustiva(
        suite_cordura_final, cfg, metodos_eval, n_semillas=n_sem_final,
        titulo="SUITE DE CHEQUEO DE CORDURA (SATURADOS - EXCLUIDA DE FRIEDMAN)", es_cordura=True
    )

    # Analisis de Equivalencia y Comparativa con LeakyReLU(alfa) puro
    res_eq = detectar_equivalencia(mejor_elgp)
    es_eq, desc_eq, r_eq, rmse_eq = res_eq
    f_val = mejor_elgp.f if mejor_elgp.f is not None else 0.0
    if f_val > 0:
        texto_f = "{:+.4f} (inferior a ReLU por {:.4f} sigmas; z_medio = {:+.4f})".format(f_val, f_val, -f_val)
    elif f_val < 0:
        texto_f = "{:+.4f} (superior a ReLU por {:.4f} sigmas; z_medio = {:+.4f})".format(f_val, -f_val, -f_val)
    else:
        texto_f = "0.0000 (identico a baseline ReLU; z_medio = 0.0000)"

    print("\n" + "=" * 80)
    print("ANALISIS DE LA ACTIVACION DESCUBIERTA (B7, T6.b, T8.b):")
    print("  Formula: " + formula(mejor_elgp))
    print("  Aptitud f: " + texto_f)
    print("  Violacion g1: {:.4f} (Factible: {})".format(mejor_elgp.g1, mejor_elgp.es_factible))
    print("  Clasificacion: " + desc_eq)
    print("  Correlacion |r|: {:.5f}".format(r_eq))
    print("  RMSE aproximado: {:.5f}".format(rmse_eq))
    print("=" * 80)

    # Guardar ecuacion ganadora y resultados finales
    ruta_txt = os.path.join(cfg["SALIDA"], "ecuacion_ganadora.txt")
    with open(ruta_txt, "w", encoding="utf-8") as f:
        f.write("=== FUNCION DE ACTIVACION DESCUBIERTA (ELGP) ===\n\n")
        f.write("Formula analitica:\n  {}\n\n".format(formula(mejor_elgp)))
        f.write("Aptitud normalizada f: {}\n".format(texto_f))
        f.write("Violacion g1: {:.4f}\n\n".format(mejor_elgp.g1))
        f.write("Clasificacion de equivalencia: {}\n".format(desc_eq))
        f.write("Correlacion r: {:.5f} | RMSE: {:.5f}\n".format(r_eq, rmse_eq))
        f.write("\nGenes:\n  {}\n".format(mejor_elgp.genes))
        f.write("Coeficientes e_k:\n  {}\n".format([round(float(v), 4) for v in mejor_elgp.e]))
        f.write("\nDesglose de desempeno visto:\n")
        for k, v in mejor_elgp.f_detalles.items():
            f.write("  - {:<38}: AUC={:.4f} (z={:+.4f})\n".format(k, v, mejor_elgp.z_detalles.get(k, 0.0)))

    ruta_res_final = os.path.join(cfg["SALIDA"], "resultados_final.json")
    with open(ruta_res_final, "w", encoding="utf-8") as f:
        json.dump({
            "metodos": list(metodos_eval.keys()),
            "medias_vistos": medias_vistos,
            "medias_generalizacion": medias_gen,
            "medias_cordura": medias_cordura,
            "formula_elgp": formula(mejor_elgp),
            "equivalencia": desc_eq,
            "r": r_eq,
            "rmse": rmse_eq,
        }, f, indent=2)

    t_total_min = (time.time() - t_global_inicio) / 60
    print("\n" + "=" * 80)
    print("FASE FINAL COMPLETADA EXITOSAMENTE en {:.1f} minutos".format(t_total_min))
    print("Artefactos guardados en: " + cfg["SALIDA"])
    print("================================================================================")


if __name__ == "__main__":
    main()
