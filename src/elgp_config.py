# =============================================================
# ARCHIVO 1/5: elgp_config.py
# Configuracion global, operadores con division protegida (epsilon),
# constantes evolutivas para estrategia (mu, lambda) y suite multi-dataset
# =============================================================

import os
os.environ["PANDAS_USE_PYARROW"] = "0"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import copy
import json
import random
import sys
import tempfile
import threading
import time

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from scipy.stats import wilcoxon, friedmanchisquare
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.preprocessing import StandardScaler

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# -------------------------------------------------------------
# PRIMITIVAS MATEMATICAS Y DIVISION PROTEGIDA CON EPSILON
# -------------------------------------------------------------
def div_protegida(a, b, eps=1e-5):
    """Division protegida diferenciable con epsilon: a / (b + sign(b)*eps)."""
    signo = torch.sign(b)
    signo = torch.where(signo == 0, torch.ones_like(signo), signo)
    return a / (b + signo * eps)


# Conjunto ampliado de primitivas matematicas (R5)
# Cada elemento es (nombre, aridad, funcion_callable)
OPS = [
    ("+",          2, lambda a, b: a + b),
    ("*",          2, lambda a, b: a * b),
    ("pdiv",       2, lambda a, b: div_protegida(a, b)),
    ("max",        2, lambda a, b: torch.maximum(a, b)),
    ("sin",        1, lambda a, b: torch.sin(a)),
    ("cos",        1, lambda a, b: torch.cos(a)),
    ("sigmoid",    1, lambda a, b: torch.sigmoid(a)),
    ("tanh",       1, lambda a, b: torch.tanh(a)),
    ("relu",       1, lambda a, b: torch.relu(a)),
    ("leaky_relu", 1, lambda a, b: F.leaky_relu(a, negative_slope=0.1)),
    ("gelu",       1, lambda a, b: F.gelu(a)),
    ("elu",        1, lambda a, b: F.elu(a)),
    ("selu",       1, lambda a, b: F.selu(a)),
    ("softplus",   1, lambda a, b: F.softplus(a)),
    ("swish",      1, lambda a, b: F.silu(a)),
    ("sq",         1, lambda a, b: a * a),
    ("expneg",     1, lambda a, b: torch.exp(-torch.clamp(a * a, max=20.0))),
]

N_OPS = len(OPS)
N_REG = 3
UMBRAL_E = 0.05

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# -------------------------------------------------------------
# CONFIGURACION DEL ALGORITMO EVOLUTIVO (mu, lambda)
# -------------------------------------------------------------
CFG = dict(
    L=8,                      # instrucciones por cromosoma
    MU=30,                    # tamano de poblacion de padres (mu)
    LAMBDA_HIJOS=60,          # numero de descendientes por generacion (lambda > mu)
    T_MAX=50,                 # generaciones objetivo para corrida profunda
    P_CRUZA=1.0,              # cruza siempre (recomendacion de GP)
    P_MUT=0.20,               # probabilidad de mutacion estructural
    SIGMA_E=0.10,             # desviacion estandar de ruido epigenetico
    T_EST=5,                  # generaciones de estancamiento para reinyeccion
    N_REEMPLAZO=15,           # individuos aleatorios factibles reinyectados si se estanca
    EPS_NL=0.05,              # umbral minimo de no-linealidad g1 = eps_nl - NL(x)
    K_FOLDS=3,                # validacion cruzada durante la evolucion
    K_FOLDS_FINAL=5,          # validacion cruzada para evaluacion final
    VAL_INTERNA_RATIO=0.15,   # reserva interna estratificada (15%) para early stopping honesto
    TOP_FINALISTAS=5,         # mejores candidatos finales
    TOP_REEVALUACION=20,      # candidatos del archivo sometidos a reevaluacion con nuevas semillas
    HIDDEN=64,                # neuronas por capa oculta
    CAPAS=3,                  # capas ocultas del MLP
    USA_BN=True,              # normalizacion por lotes para estabilidad numerica (T3)
    LR=0.002,                 # tasa de aprendizaje Adam
    BATCH=256,                # tamano de lote
    EPOCAS=40,                # epocas maximas por entrenamiento
    PACIENCIA=6,              # paciencia de early stopping honesto
    CLIP=5.0,                 # recorte de gradiente
    MAX_FILAS_BUSQUEDA=4000,  # submuestra estratificada para datasets >10k en busqueda
    PRESUPUESTO_OBJETIVO=3000,# evaluaciones efectivas objetivo en corrida profunda
    SALIDA=os.path.join(BASE_DIR, "resultados_elgp_10datasets"),  # carpeta separada para no sobrescribir resultados previos de 5 datasets
)

# -------------------------------------------------------------
# SPINNER DE PROGRESO
# -------------------------------------------------------------
class Spinner:
    def __init__(self, mensaje=""):
        self.mensaje = mensaje
        self.activo = False
        self.hilo = None

    def _girar(self):
        chars = ["|", "/", "-", "\\"]
        i = 0
        while self.activo:
            sys.stdout.write("\r" + self.mensaje + " " + chars[i % 4])
            sys.stdout.flush()
            i += 1
            time.sleep(0.12)

    def start(self):
        self.activo = True
        self.hilo = threading.Thread(target=self._girar, daemon=True)
        self.hilo.start()

    def stop(self):
        self.activo = False
        if self.hilo:
            self.hilo.join(timeout=1.0)
        sys.stdout.write("\r" + " " * 110 + "\r")
        sys.stdout.flush()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()
        return False
