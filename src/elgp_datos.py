# =============================================================
# ARCHIVO 3/5: elgp_datos.py
# Carga de datasets de la UCI (Suite de Evolucion y Suite de Generalizacion),
# binarizacion explicita documentada (B2), particion estratificada K-Fold
# con reserva de validacion interna (15%) y captura segura de ValueError (B8, B9)
# =============================================================

from elgp_config import *
from elgp_individuo import MLP, ActivacionLGP
from sklearn.datasets import load_breast_cancer, load_digits
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder, OrdinalEncoder
from sklearn.impute import SimpleImputer


# -------------------------------------------------------------
# CARGADORES: UTILIDAD DE CACHE Y DESCARGA SEGURA
# -------------------------------------------------------------
def _buscar_cache_existente(nombre_cache, salida="."):
    directorio_base = os.path.dirname(os.path.abspath(__file__))
    destino_dir = salida if salida != "." else directorio_base
    candidatos = [
        os.path.join(destino_dir, nombre_cache),
        os.path.join(directorio_base, "resultados_elgp_10datasets", nombre_cache),
        os.path.join(directorio_base, "resultados_elgp_multidataset", nombre_cache),
        os.path.join(directorio_base, nombre_cache),
    ]
    for ruta in candidatos:
        if os.path.exists(ruta):
            return ruta
    return None


def _cargar_npz_o_descargar(nombre_cache, uci_id, nombre_legible, tipo, clases, salida=".", usar_cache=True):
    directorio_base = os.path.dirname(os.path.abspath(__file__))
    destino_dir = salida if salida != "." else directorio_base
    ruta_cache = os.path.join(destino_dir, nombre_cache)

    if usar_cache:
        ruta_existente = _buscar_cache_existente(nombre_cache, salida=salida)
        if ruta_existente is not None:
            try:
                data = np.load(ruta_existente)
                return dict(X=data["X"].astype(np.float32), y=data["y"].astype(np.int64),
                            nombre=nombre_legible, tipo=tipo, clases=clases)
            except Exception:
                pass

    try:
        from ucimlrepo import fetch_ucirepo
        ds = fetch_ucirepo(id=uci_id)
        X_df = ds.data.features.copy()
        for col in X_df.select_dtypes(include=["object", "category", "string"]).columns:
            X_df[col] = X_df[col].fillna("missing")
            X_df[col] = OrdinalEncoder().fit_transform(X_df[[col]].astype(str))
        X = X_df.values.astype(np.float32)
        y_raw = ds.data.targets.iloc[:, 0].values
        if y_raw.dtype == object or str(y_raw.dtype).startswith(("str", "<U")):
            y_raw = np.array([str(v).strip().rstrip(".") for v in y_raw], dtype=object)
        y = LabelEncoder().fit_transform(y_raw).astype(np.int64)
    except Exception as err:
        ruta_base = _buscar_cache_existente(nombre_cache, salida=".")
        if ruta_base is not None:
            data = np.load(ruta_base)
            X, y = data["X"].astype(np.float32), data["y"].astype(np.int64)
        else:
            raise err

    try:
        os.makedirs(os.path.dirname(ruta_cache), exist_ok=True)
        np.savez_compressed(ruta_cache, X=X, y=y)
    except Exception:
        pass
    return dict(X=X, y=y, nombre=nombre_legible, tipo=tipo, clases=clases)


def cargar_credit_card(salida=".", usar_cache=True):
    return _cargar_npz_o_descargar("uci_350_cache.npz", 350, "UCI Credit Card (Finanzas, 30k)", "binario", 2, salida, usar_cache)


def cargar_german_credit(salida=".", usar_cache=True):
    return _cargar_npz_o_descargar("german_credit_cache.npz", 144, "UCI German Credit (Riesgo, 1k)", "binario", 2, salida, usar_cache)


def cargar_wine_quality(salida=".", usar_cache=True):
    """
    UCI Wine Quality (ID 186):
    Binarizacion canonica fijada explicitamente en el codigo (B2):
      Clase 1 (Alta Calidad): Calidad >= 6
      Clase 0 (Calidad Estandar/Baja): Calidad < 6
    """
    directorio_base = os.path.dirname(os.path.abspath(__file__))
    destino_dir = salida if salida != "." else directorio_base
    ruta_cache = os.path.join(destino_dir, "wine_quality_bin_cache.npz")

    if usar_cache:
        ruta_exist = _buscar_cache_existente("wine_quality_bin_cache.npz", salida=salida)
        if ruta_exist is not None:
            try:
                data = np.load(ruta_exist)
                y_raw = data["y"]
                y = (y_raw >= 6).astype(np.int64) if len(np.unique(y_raw)) > 2 else y_raw.astype(np.int64)
                return dict(X=data["X"].astype(np.float32), y=y,
                            nombre="UCI Wine Quality (Agro, 6.5k)", tipo="binario", clases=2)
            except Exception:
                pass

    try:
        from ucimlrepo import fetch_ucirepo
        ds = fetch_ucirepo(id=186)
        X = ds.data.features.values.astype(np.float32)
        y_raw = ds.data.targets.iloc[:, 0].values.astype(float)
        y = (y_raw >= 6.0).astype(np.int64)  # Binarizacion canonica: umbral calidad >= 6
    except Exception as err:
        ruta_base = _buscar_cache_existente("wine_quality_bin_cache.npz", salida=".")
        if ruta_base is not None:
            data = np.load(ruta_base)
            y_raw = data["y"]
            y = (y_raw >= 6).astype(np.int64) if len(np.unique(y_raw)) > 2 else y_raw.astype(np.int64)
            X = data["X"].astype(np.float32)
        else:
            raise err

    try:
        os.makedirs(os.path.dirname(ruta_cache), exist_ok=True)
        np.savez_compressed(ruta_cache, X=X, y=y)
    except Exception:
        pass
    return dict(X=X, y=y, nombre="UCI Wine Quality (Agro, 6.5k)", tipo="binario", clases=2)


def cargar_magic_gamma(salida=".", usar_cache=True):
    return _cargar_npz_o_descargar("magic_gamma_cache.npz", 159, "UCI Magic Gamma (Fisica, 19k)", "binario", 2, salida, usar_cache)


def cargar_vehicle(salida=".", usar_cache=True):
    """
    UCI Vehicle Silhouettes (ID 149):
    4 clases canonicas (van, saab, bus, opel) filtrando 1 muestra aislada de errata (B2, T6.c).
    """
    directorio_base = os.path.dirname(os.path.abspath(__file__))
    destino_dir = salida if salida != "." else directorio_base
    ruta_cache = os.path.join(destino_dir, "vehicle_cache.npz")

    if usar_cache:
        ruta_exist = _buscar_cache_existente("vehicle_cache.npz", salida=salida)
        if ruta_exist is not None:
            try:
                data = np.load(ruta_exist)
                X = data["X"].astype(np.float32)
                y = data["y"].astype(np.int64)
                clases_unq, counts_unq = np.unique(y, return_counts=True)
                print("  [UCI Vehicle Silhouettes]: Cargado desde cache ({})".format(ruta_exist))
                print("    - Filas: {}, Clases: {}".format(len(y), len(clases_unq)))
                print("    - Conteos por clase: {}".format(dict(zip(clases_unq, counts_unq))))
                return dict(X=X, y=y,
                            nombre="UCI Vehicle (Morfometria, 4 clases)", tipo="multiclase", clases=4)
            except Exception:
                pass

    try:
        from ucimlrepo import fetch_ucirepo
        ds = fetch_ucirepo(id=149)
        X = ds.data.features.values.astype(np.float32)
        y_raw = ds.data.targets.iloc[:, 0].values

        n_filas_antes = len(y_raw)
        clases_antes, conteos_antes = np.unique(y_raw, return_counts=True)
        dict_antes = dict(zip([str(c) for c in clases_antes], [int(c) for c in conteos_antes]))

        y_enc = LabelEncoder().fit_transform(y_raw).astype(np.int64)
        vals, counts = np.unique(y_enc, return_counts=True)
        valid_classes = vals[counts >= 10]
        mask = np.isin(y_enc, valid_classes)
        X_clean = X[mask]
        y_clean = LabelEncoder().fit_transform(y_enc[mask]).astype(np.int64)

        filas_eliminadas = n_filas_antes - len(y_clean)
        clases_despues, conteos_despues = np.unique(y_clean, return_counts=True)
        dict_despues = dict(zip([int(c) for c in clases_despues], [int(c) for c in conteos_despues]))

        print("  [UCI Vehicle Silhouettes (ID 149) - Verificacion de Filtrado (T6.c)]:")
        print("    - Filas antes del filtro: {}, Clases detectadas: {}".format(n_filas_antes, len(clases_antes)))
        print("    - Conteos por clase antes: {}".format(dict_antes))
        if n_filas_antes != 846 or len(clases_antes) != 4:
            print("    - AVISO METODOLOGICO: Lo descargado en bruto tiene {} filas y {} clases (esperado 846 filas y 4 clases).".format(
                n_filas_antes, len(clases_antes)))
            print("      Explicacion: En UCI ID 149 existe 1 muestra aislada/errata con clase espuria (conteo < 10),")
            print("      que genera una 5ta clase singleton ('204', conteo=1). Se filtra para restaurar las 4 clases canonicas.")
        print("    - Filas eliminadas por filtro: {}".format(filas_eliminadas))
        print("    - Filas despues del filtro: {}, Clases resultantes: {}".format(len(y_clean), len(clases_despues)))
        print("    - Conteos por clase despues: {}".format(dict_despues))
    except Exception as err:
        ruta_base = _buscar_cache_existente("vehicle_cache.npz", salida=".")
        if ruta_base is not None:
            data = np.load(ruta_base)
            X_clean, y_clean = data["X"].astype(np.float32), data["y"].astype(np.int64)
        else:
            raise err

    try:
        os.makedirs(os.path.dirname(ruta_cache), exist_ok=True)
        np.savez_compressed(ruta_cache, X=X_clean, y=y_clean)
    except Exception:
        pass
    return dict(X=X_clean, y=y_clean, nombre="UCI Vehicle (Morfometria, 4 clases)", tipo="multiclase", clases=4)


# -------------------------------------------------------------
# CARGADORES: SUITE DE GENERALIZACION (R2: NO VISTOS EN BUSQUEDA)
# -------------------------------------------------------------
def cargar_landsat(salida=".", usar_cache=True):
    return _cargar_npz_o_descargar("satellite_cache.npz", 146, "UCI Statlog Landsat (Satelital, 6.4k)", "multiclase", 6, salida, usar_cache)


def cargar_dry_bean(salida=".", usar_cache=True):
    return _cargar_npz_o_descargar("dry_bean_cache.npz", 602, "UCI Dry Bean (Agro, 13.6k)", "multiclase", 7, salida, usar_cache)


def cargar_digits(salida=".", usar_cache=True):
    """sklearn Digits (1,797 filas, 8x8) con 10 clases multiclase (B9)."""
    d = load_digits()
    X = d.data.astype(np.float32)
    y = d.target.astype(np.int64)
    return dict(X=X, y=y, nombre="sklearn Digits (1,797 filas, 8x8)", tipo="multiclase", clases=10)


def cargar_breast_cancer(salida=".", usar_cache=True):
    d = load_breast_cancer()
    X = d.data.astype(np.float32)
    y = d.target.astype(np.int64)
    return dict(X=X, y=y, nombre="UCI Breast Cancer (Medico)", tipo="binario", clases=2)


def cargar_spambase(salida=".", usar_cache=True):
    return _cargar_npz_o_descargar("spambase_cache.npz", 94, "UCI Spambase (Texto/NLP, 4.6k)", "binario", 2, salida, usar_cache)


def cargar_steel_plates_faults(salida=".", usar_cache=True):
    directorio_base = os.path.dirname(os.path.abspath(__file__))
    destino_dir = salida if salida != "." else directorio_base
    ruta = os.path.join(destino_dir, "steel_plates_cache.npz")
    if usar_cache:
        r_actual = _buscar_cache_existente("steel_plates_cache.npz", salida=salida)
        if r_actual is not None:
            d = np.load(r_actual)
            return dict(X=d["X"].astype(np.float32), y=d["y"].astype(np.int64),
                        nombre="UCI Steel Plates Faults (Materiales, 7 cl)", tipo="multiclase", clases=7)
    from ucimlrepo import fetch_ucirepo
    ds = fetch_ucirepo(id=198)
    X_df = ds.data.features.copy()
    for col in X_df.columns:
        if X_df[col].isnull().any():
            X_df[col] = X_df[col].fillna(X_df[col].median())
    X = X_df.values.astype(np.float32)
    y = np.argmax(ds.data.targets.values, axis=1).astype(np.int64)
    try:
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        np.savez_compressed(ruta, X=X, y=y)
    except Exception:
        pass
    return dict(X=X, y=y, nombre="UCI Steel Plates Faults (Materiales, 7 cl)", tipo="multiclase", clases=7)


def cargar_yeast(salida=".", usar_cache=True):
    directorio_base = os.path.dirname(os.path.abspath(__file__))
    destino_dir = salida if salida != "." else directorio_base
    ruta = os.path.join(destino_dir, "yeast_cache.npz")
    if usar_cache:
        r_actual = _buscar_cache_existente("yeast_cache.npz", salida=salida)
        if r_actual is not None:
            d = np.load(r_actual)
            return dict(X=d["X"].astype(np.float32), y=d["y"].astype(np.int64),
                        nombre="UCI Yeast (Biologia Celular, 9 cl)", tipo="multiclase", clases=9)
    from ucimlrepo import fetch_ucirepo
    ds = fetch_ucirepo(id=110)
    X_df = ds.data.features.copy()
    for col in X_df.columns:
        if X_df[col].isnull().any():
            X_df[col] = X_df[col].fillna(X_df[col].median())
    X = X_df.values.astype(np.float32)
    y_raw = ds.data.targets.iloc[:, 0].values
    y_enc = LabelEncoder().fit_transform(y_raw).astype(np.int64)
    vals, counts = np.unique(y_enc, return_counts=True)
    mask = np.isin(y_enc, vals[counts >= 10])
    X = X[mask]
    y = LabelEncoder().fit_transform(y_enc[mask]).astype(np.int64)
    try:
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        np.savez_compressed(ruta, X=X, y=y)
    except Exception:
        pass
    return dict(X=X, y=y, nombre="UCI Yeast (Biologia Celular, 9 cl)", tipo="multiclase", clases=9)


def cargar_sonar(salida=".", usar_cache=True):
    directorio_base = os.path.dirname(os.path.abspath(__file__))
    destino_dir = salida if salida != "." else directorio_base
    ruta = os.path.join(destino_dir, "sonar_cache.npz")
    if usar_cache:
        r_actual = _buscar_cache_existente("sonar_cache.npz", salida=salida)
        if r_actual is not None:
            d = np.load(r_actual)
            return dict(X=d["X"].astype(np.float32), y=d["y"].astype(np.int64),
                        nombre="UCI Sonar (Senales/Acustica, 2 cl)", tipo="binario", clases=2)
    from ucimlrepo import fetch_ucirepo
    ds = fetch_ucirepo(id=151)
    X = ds.data.features.values.astype(np.float32)
    y = LabelEncoder().fit_transform(ds.data.targets.iloc[:, 0].values).astype(np.int64)
    try:
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        np.savez_compressed(ruta, X=X, y=y)
    except Exception:
        pass
    return dict(X=X, y=y, nombre="UCI Sonar (Senales/Acustica, 2 cl)", tipo="binario", clases=2)


def cargar_heart_disease(salida=".", usar_cache=True):
    directorio_base = os.path.dirname(os.path.abspath(__file__))
    destino_dir = salida if salida != "." else directorio_base
    ruta = os.path.join(destino_dir, "heart_disease_cache.npz")
    if usar_cache:
        r_actual = _buscar_cache_existente("heart_disease_cache.npz", salida=salida)
        if r_actual is not None:
            d = np.load(r_actual)
            return dict(X=d["X"].astype(np.float32), y=d["y"].astype(np.int64),
                        nombre="UCI Heart Disease (Clinico, 2 cl)", tipo="binario", clases=2)
    from ucimlrepo import fetch_ucirepo
    ds = fetch_ucirepo(id=45)
    X_df = ds.data.features.copy()
    for col in X_df.columns:
        if X_df[col].dtype == object or str(X_df[col].dtype) == "category":
            X_df[col] = X_df[col].fillna("missing")
            X_df[col] = OrdinalEncoder().fit_transform(X_df[[col]].astype(str))
    # Valores faltantes numericos (ca, thal) se preservan como NaN para que
    # SimpleImputer se ajuste ESTRICTAMENTE sobre X_tr en cada pliegue (Regla B, T10.e)
    X = X_df.values.astype(np.float32)
    y_raw = ds.data.targets.iloc[:, 0].values
    y = (y_raw > 0).astype(np.int64)
    try:
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        np.savez_compressed(ruta, X=X, y=y)
    except Exception:
        pass
    return dict(X=X, y=y, nombre="UCI Heart Disease (Clinico, 2 cl)", tipo="binario", clases=2)


def cargar_blood_transfusion(salida=".", usar_cache=True):
    directorio_base = os.path.dirname(os.path.abspath(__file__))
    destino_dir = salida if salida != "." else directorio_base
    ruta = os.path.join(destino_dir, "blood_transfusion_cache.npz")
    if usar_cache:
        r_actual = _buscar_cache_existente("blood_transfusion_cache.npz", salida=salida)
        if r_actual is not None:
            d = np.load(r_actual)
            return dict(X=d["X"].astype(np.float32), y=d["y"].astype(np.int64),
                        nombre="UCI Blood Transfusion (Hematologia, 2 cl)", tipo="binario", clases=2)
    from ucimlrepo import fetch_ucirepo
    ds = fetch_ucirepo(id=176)
    X = ds.data.features.values.astype(np.float32)
    y = LabelEncoder().fit_transform(ds.data.targets.iloc[:, 0].values).astype(np.int64)
    try:
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        np.savez_compressed(ruta, X=X, y=y)
    except Exception:
        pass
    return dict(X=X, y=y, nombre="UCI Blood Transfusion (Hematologia, 2 cl)", tipo="binario", clases=2)


# -------------------------------------------------------------
# CARGADORES ADICIONALES PARA EXPANSION DE SUITE (10+ DATASETS)
# -------------------------------------------------------------
def cargar_bank_marketing(salida=".", usar_cache=True):
    return _cargar_npz_o_descargar("bank_marketing_cache.npz", 222, "UCI Bank Marketing (Banca, 45k)", "binario", 2, salida, usar_cache)


def cargar_australian_credit(salida=".", usar_cache=True):
    return _cargar_npz_o_descargar("australian_credit_cache.npz", 143, "UCI Australian Credit (Finanzas, 690)", "binario", 2, salida, usar_cache)


def cargar_raisin(salida=".", usar_cache=True):
    return _cargar_npz_o_descargar("raisin_cache.npz", 850, "UCI Raisin (Agro/Morfologia, 900)", "binario", 2, salida, usar_cache)


def cargar_obesity(salida=".", usar_cache=True):
    return _cargar_npz_o_descargar("obesity_cache.npz", 544, "UCI Obesity Levels (Salud, 7 cl)", "multiclase", 7, salida, usar_cache)


def cargar_ionosphere(salida=".", usar_cache=True):
    return _cargar_npz_o_descargar("ionosphere_cache.npz", 52, "UCI Ionosphere (Radar/Fisica, 351)", "binario", 2, salida, usar_cache)


def cargar_phishing(salida=".", usar_cache=True):
    return _cargar_npz_o_descargar("phishing_cache.npz", 327, "UCI Phishing Websites (Web, 11k)", "binario", 2, salida, usar_cache)


def cargar_taiwan_bankruptcy(salida=".", usar_cache=True):
    return _cargar_npz_o_descargar("taiwan_bankruptcy_cache.npz", 572, "UCI Taiwan Bankruptcy (Quiebra, 6.8k)", "binario", 2, salida, usar_cache)


def cargar_adult(salida=".", usar_cache=True):
    return _cargar_npz_o_descargar("adult_cache.npz", 2, "UCI Adult Census (Ingresos, 48k)", "binario", 2, salida, usar_cache)


def cargar_parkinsons(salida=".", usar_cache=True):
    return _cargar_npz_o_descargar("parkinsons_cache.npz", 174, "UCI Parkinsons (Biomedica/Voz, 195)", "binario", 2, salida, usar_cache)


# -------------------------------------------------------------
# PREPARACION DE SUITES CON VALIDACION INTERNA HONESTA (R3, Reglas A y B)
# -------------------------------------------------------------
def construir_suite(cargadores, cfg, k_folds=3, modo_busqueda=True):
    """
    Construye los pliegues con validacion interna honesta (~15% de reserva dentro
    del pliegue de entrenamiento). Todo escalado (StandardScaler) se ajusta
    ESTRICTAMENTE sobre el sub-entrenamiento y nunca ve datos de validacion o test.
    """
    suite = []
    max_filas = cfg.get("MAX_FILAS_BUSQUEDA", 4000)
    ratio_val = cfg.get("VAL_INTERNA_RATIO", 0.15)

    for cargador in cargadores:
        info = cargador()
        X, y = info["X"], info["y"]

        # Submuestreo estratificado para datasets grandes en fase de evolucion
        if modo_busqueda and len(y) > max_filas:
            y_strat = y if info["tipo"] == "multiclase" else np.asarray(y, dtype=int)
            X, _, y, _ = train_test_split(X, y, train_size=max_filas, stratify=y_strat, random_state=42)

        skf = StratifiedKFold(n_splits=k_folds, shuffle=True, random_state=42)
        y_strat = y if info["tipo"] == "multiclase" else np.asarray(y, dtype=int)

        pliegues = []
        for idx_tr_full, idx_te in skf.split(X, y_strat):
            X_tr_full, y_tr_full = X[idx_tr_full], y[idx_tr_full]
            X_te, y_te = X[idx_te], y[idx_te]

            # 1. Reserva estratificada de validacion interna (~15%)
            y_tr_strat = y_tr_full if info["tipo"] == "multiclase" else np.asarray(y_tr_full, dtype=int)
            X_tr, X_val, y_tr, y_val = train_test_split(
                X_tr_full, y_tr_full, test_size=ratio_val, stratify=y_tr_strat, random_state=42
            )

            # 2. Preprocesamiento: Imputacion y StandardScaler ajustados UNICAMENTE con X_tr (Regla B, T10.e)
            if np.isnan(X_tr).any() or np.isnan(X_val).any() or np.isnan(X_te).any():
                imputer = SimpleImputer(strategy="median").fit(X_tr)
                X_tr = imputer.transform(X_tr)
                X_val = imputer.transform(X_val)
                X_te = imputer.transform(X_te)

            scaler = StandardScaler().fit(X_tr)
            X_tr_norm = scaler.transform(X_tr)
            X_val_norm = scaler.transform(X_val)
            X_te_norm = scaler.transform(X_te)

            es_bin = (info["tipo"] == "binario")
            pliegues.append(dict(
                Xtr=torch.tensor(X_tr_norm, dtype=torch.float32, device=DEVICE),
                ytr=torch.tensor(y_tr, dtype=torch.float32 if es_bin else torch.long, device=DEVICE),
                Xval=torch.tensor(X_val_norm, dtype=torch.float32, device=DEVICE),
                yval_np=np.asarray(y_val),
                Xte=torch.tensor(X_te_norm, dtype=torch.float32, device=DEVICE),
                yte_np=np.asarray(y_te),
                scaler=scaler,
            ))

        suite.append(dict(
            nombre=info["nombre"],
            tipo=info["tipo"],
            clases=info["clases"],
            entradas=X.shape[1],
            muestras=len(y),
            pliegues=pliegues,
        ))

    return suite


# =============================================================
# CATALOGO COMPLETO Y SELECTOR MODULAR DE DATASETS
# =============================================================
CATALOGO_DATASETS = {
    # --- Suite Base Original (Evolucion) ---
    "credit_card":       cargar_credit_card,
    "german_credit":     cargar_german_credit,
    "wine_quality":      cargar_wine_quality,
    "magic_gamma":       cargar_magic_gamma,
    "vehicle":           cargar_vehicle,

    # --- Expansion a 10 Datasets de Entrenamiento ---
    "spambase":          cargar_spambase,
    "bank_marketing":    cargar_bank_marketing,
    "australian_credit": cargar_australian_credit,
    "raisin":            cargar_raisin,
    "obesity":           cargar_obesity,

    # --- Suite de Generalizacion (No Vistos) ---
    "steel_plates":      cargar_steel_plates_faults,
    "yeast":             cargar_yeast,
    "sonar":             cargar_sonar,
    "heart_disease":     cargar_heart_disease,
    "blood_transfusion": cargar_blood_transfusion,

    # --- Candidatos Opcionales Extra ---
    "ionosphere":        cargar_ionosphere,
    "phishing":          cargar_phishing,
    "taiwan_bankruptcy": cargar_taiwan_bankruptcy,
    "adult":             cargar_adult,
    "parkinsons":        cargar_parkinsons,

    # --- Suite de Chequeo de Cordura (Saturados) ---
    "landsat":           cargar_landsat,
    "dry_bean":          cargar_dry_bean,
    "digits":            cargar_digits,
    "breast_cancer":     cargar_breast_cancer,
}

# -------------------------------------------------------------
# 1. SELECTOR DE DATASETS PARA ENTRENAMIENTO (SUITE DE EVOLUCION)
# Para OMITIR cualquier dataset del entrenamiento, simplemente comenta
# su linea agregando '#' al inicio. Para incluirlo, quita el '#'.
# -------------------------------------------------------------
DATASETS_EVOLUCION = [
    # --- 5 Datasets Base (Experimento Original) ---
    "credit_card",          # UCI ID 350 | Finanzas (30k filas, 2 clases)
    "german_credit",        # UCI ID 144 | Riesgo crediticio (1k filas, 2 clases)
    "wine_quality",         # UCI ID 186 | Agro/Quimica (6.5k filas, 2 clases)
    "magic_gamma",          # UCI ID 159 | Fisica de particulas (19k filas, 2 clases)
    "vehicle",              # UCI ID 149 | Morfometria (845 filas, 4 clases)

    # --- 5 Datasets Adicionales (Completan los 10 de Entrenamiento) ---
    "spambase",             # UCI ID  94 | Texto/NLP spam (4.6k filas, 2 clases)
    "bank_marketing",       # UCI ID 222 | Banca/Marketing (45.2k filas, 2 clases)
    "australian_credit",    # UCI ID 143 | Credito Australia (690 filas, 2 clases)
    "raisin",               # UCI ID 850 | Morfologia agricola (900 filas, 2 clases)
    "obesity",              # UCI ID 544 | Salud/Habitos (2.1k filas, 7 clases)

    # --- Opcionales Adicionales (Comentados = Omitidos del entrenamiento) ---
    # "ionosphere",         # UCI ID  52 | Radar/Ionosfera (351 filas, 2 clases)
    # "phishing",           # UCI ID 327 | Ciberseguridad Web (11k filas, 2 clases)
    # "taiwan_bankruptcy",  # UCI ID 572 | Quiebra empresarial (6.8k filas, 2 clases)
    # "adult",              # UCI ID   2 | Censo/Ingresos >50k (48.8k filas, 2 clases)
    # "parkinsons",         # UCI ID 174 | Biomedica/Voz (195 filas, 2 clases)
]

# -------------------------------------------------------------
# 2. SELECTOR DE DATASETS NO VISTOS (SUITE DE GENERALIZACION)
# IMPORTANTE: Mantener disjunta de DATASETS_EVOLUCION para validacion honesta.
# Comenta con '#' los que quieras omitir en la evaluacion final.
# -------------------------------------------------------------
DATASETS_GENERALIZACION = [
    "steel_plates",         # UCI ID 198 | Fallas en acero (1.9k filas, 7 clases)
    "yeast",                # UCI ID 110 | Biologia celular (1.5k filas, 9 clases)
    "sonar",                # UCI ID 151 | Acustica/Sonar (208 filas, 2 clases)
    "heart_disease",        # UCI ID  45 | Diagnostico clinico (303 filas, 2 clases)
    "blood_transfusion",    # UCI ID 176 | Hematologia (748 filas, 2 clases)

    # --- Opcionales para ampliar Friedman a 10 no vistos (Comentados = Omitidos) ---
    # "ionosphere",         # UCI ID  52 | Radar/Ionosfera (351 filas, 2 clases)
    # "phishing",           # UCI ID 327 | Ciberseguridad Web (11k filas, 2 clases)
    # "taiwan_bankruptcy",  # UCI ID 572 | Quiebra empresarial (6.8k filas, 2 clases)
    # "adult",              # UCI ID   2 | Censo/Ingresos >50k (48.8k filas, 2 clases)
    # "parkinsons",         # UCI ID 174 | Biomedica/Voz (195 filas, 2 clases)
]

# -------------------------------------------------------------
# 3. SELECTOR DE DATASETS DE CORDURA (SATURADOS, EXCLUIDOS DE FRIEDMAN)
# -------------------------------------------------------------
DATASETS_CORDURA = [
    "landsat",              # UCI ID 146 | Satelital (6.4k filas, 6 clases)
    "dry_bean",             # UCI ID 602 | Agro (13.6k filas, 7 clases)
    "digits",               # sklearn    | Digitos 8x8 (1.8k filas, 10 clases)
    "breast_cancer",        # sklearn    | Medico (569 filas, 2 clases)
]


def _construir_cargadores(claves, cfg):
    salida = cfg.get("SALIDA", ".")
    cargadores = []
    for clave in claves:
        if clave not in CATALOGO_DATASETS:
            raise KeyError("Dataset '{}' no encontrado en CATALOGO_DATASETS.".format(clave))
        fn = CATALOGO_DATASETS[clave]
        cargadores.append(lambda f=fn, s=salida: f(s))
    return cargadores


def descargar_caches_activos(cfg):
    """Descarga y guarda en cache .npz todos los datasets seleccionados antes de enviar a Slurm."""
    salida = cfg.get("SALIDA", ".")
    os.makedirs(salida, exist_ok=True)
    claves_unicas = list(dict.fromkeys(DATASETS_EVOLUCION + DATASETS_GENERALIZACION + DATASETS_CORDURA))
    print("\n[Cache] Descargando/verificando {} datasets activos en '{}'...".format(len(claves_unicas), salida))
    for i, clave in enumerate(claves_unicas, 1):
        info = CATALOGO_DATASETS[clave](salida)
        print("  {:2d}. {:<20} -> {:<40} | Filas: {:6d} | Clases: {}".format(
            i, clave, info["nombre"][:40], len(info["y"]), info["clases"]))


def preparar_suite_evolucion(cfg, k_folds=3, modo_busqueda=True):
    """Construye la suite de entrenamiento a partir de los datasets activos en DATASETS_EVOLUCION."""
    if not DATASETS_EVOLUCION:
        raise ValueError("DATASETS_EVOLUCION esta vacio. Descomenta al menos 1 dataset.")
    cargadores = _construir_cargadores(DATASETS_EVOLUCION, cfg)
    return construir_suite(cargadores, cfg, k_folds=k_folds, modo_busqueda=modo_busqueda)


def preparar_suite_generalizacion(cfg, k_folds=5):
    """
    Construye la suite de generalizacion no vista a partir de DATASETS_GENERALIZACION (R2, T9.b).
    Verifica que no haya traslape con DATASETS_EVOLUCION.
    """
    traslape = set(DATASETS_EVOLUCION).intersection(set(DATASETS_GENERALIZACION))
    if traslape:
        raise ValueError("Fuga metodologica (R2): datasets repetidos entre evolucion y generalizacion: {}".format(traslape))
    cargadores = _construir_cargadores(DATASETS_GENERALIZACION, cfg)
    return construir_suite(cargadores, cfg, k_folds=k_folds, modo_busqueda=False)


def preparar_suite_cordura(cfg, k_folds=5):
    """
    Suite de Chequeo de Cordura (Sanity Check, T9.b).
    Contiene los datasets saturados (AUC ReLU > 0.985).
    Se reporta por separado y queda EXCLUIDA de Friedman y pruebas no parametricas.
    """
    cargadores = _construir_cargadores(DATASETS_CORDURA, cfg)
    return construir_suite(cargadores, cfg, k_folds=k_folds, modo_busqueda=False)


# -------------------------------------------------------------
# PROTOCOLO DE ENTRENAMIENTO CON EARLY STOPPING HONESTO (R3, B8)
# -------------------------------------------------------------
def entrenar_pliegue(make_act, ds_info, pliegue, semilla, cfg):
    """
    Entrena el MLP sobre Xtr.
    El early stopping y la eleccion de epoca se basan EXCLUSIVAMENTE en Xval (validacion interna).
    El pliegue de prueba externo (Xte) se evalua EXACTAMENTE UNA VEZ con los mejores pesos.
    Calcula AUC macro one-vs-rest en float64 para multiclase con probabilidades renormalizadas.
    Captura ValueError en roc_auc_score sin abortar la corrida (B8).
    Devuelve (modelo, score_test, divergencia_bool).
    """
    torch.manual_seed(semilla)
    gen = torch.Generator(device="cpu").manual_seed(semilla)

    es_binario = (ds_info["tipo"] == "binario")
    salidas = 1 if es_binario else ds_info["clases"]

    try:
        usa_bn = cfg.get("USA_BN", True)
        m = MLP(ds_info["entradas"], make_act, hidden=cfg.get("HIDDEN", 64),
                capas=cfg.get("CAPAS", 3), salidas=salidas, usa_bn=usa_bn).to(DEVICE)
    except Exception:
        return None, 0.50, True

    opt = torch.optim.Adam(m.parameters(), lr=cfg.get("LR", 0.002))

    Xtr, ytr = pliegue["Xtr"], pliegue["ytr"]
    n = Xtr.shape[0]
    if es_binario and ytr.ndim == 1:
        ytr_tensor = ytr.unsqueeze(1)
    else:
        ytr_tensor = ytr

    mejor_val_score, mejor_estado, espera = -1.0, None, 0
    epocas = cfg.get("EPOCAS", 40)
    paciencia = cfg.get("PACIENCIA", 6)
    batch_size = cfg.get("BATCH", 256)
    clip_val = cfg.get("CLIP", 5.0)

    for _ in range(epocas):
        m.train()
        perm = torch.randperm(n, generator=gen).to(DEVICE)
        for i in range(0, n, batch_size):
            idx = perm[i:i + batch_size]
            if len(idx) < 2:
                continue
            xb, yb = Xtr[idx], ytr_tensor[idx]
            out = m(xb)

            if not torch.isfinite(out).all():
                return None, 0.50, True

            if es_binario:
                loss = F.binary_cross_entropy_with_logits(out, yb)
            else:
                loss = F.cross_entropy(out, yb)

            if not torch.isfinite(loss):
                return None, 0.50, True

            opt.zero_grad()
            loss.backward()
            gn = torch.nn.utils.clip_grad_norm_(m.parameters(), clip_val)
            if not torch.isfinite(gn):
                return None, 0.50, True
            opt.step()

        # Evaluacion en validacion interna (Xval)
        m.eval()
        with torch.no_grad():
            out_va = m(pliegue["Xval"])
            if not torch.isfinite(out_va).all():
                return None, 0.50, True

            try:
                if es_binario:
                    probs_va = torch.sigmoid(out_va).squeeze(1).cpu().numpy().astype(np.float64)
                    val_score = roc_auc_score(pliegue["yval_np"], probs_va)
                else:
                    probs_va = F.softmax(out_va, dim=1).cpu().numpy().astype(np.float64)
                    probs_va /= np.maximum(np.sum(probs_va, axis=1, keepdims=True), 1e-12)
                    val_score = roc_auc_score(pliegue["yval_np"], probs_va, multi_class="ovr")
            except ValueError:
                return None, 0.50, True

        if val_score > mejor_val_score + 1e-4:
            mejor_val_score = val_score
            mejor_estado = copy.deepcopy(m.state_dict())
            espera = 0
        else:
            espera += 1
            if espera >= paciencia:
                break

    if mejor_estado is None:
        return None, 0.50, True

    # Evaluacion externa honesta (Xte medido UNA SOLA VEZ)
    m.load_state_dict(mejor_estado)
    m.eval()
    with torch.no_grad():
        out_te = m(pliegue["Xte"])
        if not torch.isfinite(out_te).all():
            return None, 0.50, True

        try:
            if es_binario:
                probs_te = torch.sigmoid(out_te).squeeze(1).cpu().numpy().astype(np.float64)
                test_score = float(roc_auc_score(pliegue["yte_np"], probs_te))
            else:
                probs_te = F.softmax(out_te, dim=1).cpu().numpy().astype(np.float64)
                probs_te /= np.maximum(np.sum(probs_te, axis=1, keepdims=True), 1e-12)
                test_score = float(roc_auc_score(pliegue["yte_np"], probs_te, multi_class="ovr"))
        except ValueError:
            return None, 0.50, True

    return m, test_score, False
