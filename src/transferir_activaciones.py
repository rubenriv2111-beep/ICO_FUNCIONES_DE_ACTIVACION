# =============================================================
# Transferencia de Activaciones Descubiertas a Datos Geotermicos
# Importa componentes de pre_entrenamiento.py y entrena sobre datos geotermicos.
# =============================================================

import os
import sys
import numpy as np
import torch
import pandas as pd

import pre_entrenamiento as pe


def transferir_a_geotermia(
    ruta_csv="matriz_geotermica_pca_con_coordenadas.csv",
    ruta_activaciones="resultados_elgp_multidataset/activaciones_descubiertas.json",
    salida="resultados_geotermia"
):
    """Carga activaciones descubiertas y las evalua en el dataset geotermico."""
    os.makedirs(salida, exist_ok=True)
    if not os.path.exists(ruta_csv):
        print(f"[aviso] No se encontro el dataset geotermico: {ruta_csv}")
        return None

    # Buscar en ruta_activaciones o rutas alternativas conocidas
    rutas_candidatas = [
        ruta_activaciones,
        "resultados_elgp_multidataset/activaciones_descubiertas.json",
        "resultados_elgp/activaciones_descubiertas.json",
    ]
    ruta_valida = None
    for r in rutas_candidatas:
        if os.path.exists(r):
            ruta_valida = r
            break

    if ruta_valida is None:
        print(f"[aviso] No se encontro el archivo de activaciones en ninguna de las rutas esperadas.")
        return None

    cfg = dict(pe.CFG)
    cfg["SALIDA"] = salida
    datos = pe.preparar_dataset(cfg, csv=ruta_csv)
    try:
        from elgp_evolucion import cargar_activaciones
        mejor, ensamble = cargar_activaciones(ruta_valida)
    except Exception:
        mejor, ensamble = pe.cargar_activaciones(ruta_valida)

    print(f"Transferencia iniciada: {len(ensamble)} activaciones en ensamble, mejor={pe.formula(mejor)}")
    individuos = {"ELGP_Transferida": mejor}
    auc, ap = pe.evaluacion_final(datos, cfg, individuos, ensamble)
    pe.reporte_estadistico(auc, ap, refs=["ELGP_Transferida"])
    return auc, ap


if __name__ == "__main__":
    transferir_a_geotermia()
