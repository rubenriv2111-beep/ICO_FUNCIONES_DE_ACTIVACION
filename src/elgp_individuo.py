# =============================================================
# ARCHIVO 2/5: elgp_individuo.py
# Individuo ELGP, analisis de dependencias ejecutable, plegado de constantes,
# restriccion de no-linealidad g1(x), reglas de factibilidad de Deb (2000),
# detector de familias parametricas de equivalencia (LeakyReLU, ELU, Swish)
# y catalogo exhaustivo de baselines (B1, B7)
# =============================================================

import functools
import math
from elgp_config import *


# -------------------------------------------------------------
# ESTRUCTURA DE DATOS DEL INDIVIDUO ELGP
# -------------------------------------------------------------
class Ind:
    """
    Individuo ELGP:
      - genes: lista de L instrucciones [op, d, s1, s2]
      - e: coeficientes epigeneticos continuos e_k en [0, 1]
      - f: aptitud normalizada (z-score medio invertido; minimizar; puede ser negativo)
      - g1: violacion de restriccion de no-linealidad (factible si g1 <= 0)
      - f_detalles: diccionario con AUC crudo por dataset
      - z_detalles: diccionario con z-scores por dataset
      - divergencias: contador de divergencias numericas
    """
    def __init__(self, genes, e):
        self.genes = genes
        self.e = e
        self.f = None
        self.g1 = None
        self.es_factible = False
        self.f_detalles = {}
        self.z_detalles = {}
        self.divergencias = 0

    def clave(self):
        return (tuple(tuple(g) for g in self.genes), tuple(round(v, 4) for v in self.e))

    def copia(self):
        nuevo = Ind([list(g) for g in self.genes], list(self.e))
        nuevo.f = self.f
        nuevo.g1 = self.g1
        nuevo.es_factible = self.es_factible
        nuevo.f_detalles = dict(self.f_detalles)
        nuevo.z_detalles = dict(self.z_detalles)
        nuevo.divergencias = self.divergencias
        return nuevo


def e_tilde(e):
    """Transformacion epigenetica con umbral de silenciamiento."""
    return e if e > UMBRAL_E else 0.0


def instr_aleatoria():
    return [random.randrange(N_OPS), random.randrange(N_REG),
            random.randrange(N_REG), random.randrange(N_REG)]


def ind_aleatorio(L, e_fijo=False):
    genes = [instr_aleatoria() for _ in range(L)]
    e = [1.0 if e_fijo else random.random() for _ in range(L)]
    return Ind(genes, e)


# -------------------------------------------------------------
# INSTRUCCIONES EJECUTABLES: ANALISIS HACIA ATRAS ESTANDAR (B1.a)
# -------------------------------------------------------------
def instrucciones_ejecutables(ind):
    """
    Analisis de dependencias hacia atras estandar desde r0 (sin tratamiento especial de constantes).
    Toda instruccion que influye estructuralmente en la salida r0 se marca como ejecutable.
    Garantiza que la red neuronal ejecute exactamente todo el flujo de computo.
    """
    L = len(ind.genes)
    needed = {0}
    eff = [False] * L
    for k in reversed(range(L)):
        et = e_tilde(ind.e[k])
        if et <= 0.0:
            continue
        op, d, s1, s2 = ind.genes[k]
        if d not in needed:
            continue
        eff[k] = True
        if et >= 1.0:
            needed.discard(d)
        needed.add(s1)
        if OPS[op][1] == 2:
            needed.add(s2)
    return eff


def efectivas(ind):
    """Alias compatible para instrucciones ejecutables."""
    return instrucciones_ejecutables(ind)


# -------------------------------------------------------------
# ACTIVACION LGP EVOLUCIONADA EN PYTORCH (B1.a)
# -------------------------------------------------------------
class ActivacionLGP(nn.Module):
    """
    Modulo PyTorch diferenciable correspondiente al fenotipo ejecutable del cromosoma.
    Ejecuta todas las instrucciones efectivas que influyen en r0.
    """
    def __init__(self, ind):
        super().__init__()
        eff = instrucciones_ejecutables(ind)
        self.prog = []
        for k in range(len(eff)):
            if eff[k]:
                op, d, s1, s2 = ind.genes[k]
                self.prog.append((op, d, s1, s2, e_tilde(ind.e[k])))

    def forward(self, x):
        z = torch.zeros_like(x)
        r = [x, z, z]
        for op, d, s1, s2, et in self.prog:
            out = OPS[op][2](r[s1], r[s2])
            r[d] = out if et >= 1.0 else (1.0 - et) * r[d] + et * out
        return r[0]


def interprete_referencia(ind, x):
    """
    Interprete de referencia canonico e independiente (T8.a):
    Ejecuta secuencialmente TODAS las instrucciones del cromosoma con e_tilde > 0,
    en orden estricto k = 0 .. L-1, sobre los registros r = [x, 0, 0].
    No aplica eliminacion de codigo muerto ni optimizaciones de grafos.
    Devuelve r[0].
    """
    z = torch.zeros_like(x)
    r = [torch.clone(x), torch.clone(z), torch.clone(z)]
    for k in range(len(ind.genes)):
        et = e_tilde(ind.e[k])
        if et <= 0.0:
            continue
        op, d, s1, s2 = ind.genes[k]
        out = OPS[op][2](r[s1], r[s2])
        r[d] = out if et >= 1.0 else (1.0 - et) * r[d] + et * out
    return r[0]


def evaluar_malla(ind, grid=None):
    """
    Evalua phi_x(v) sobre una malla tensorial 1D usando el interprete de referencia (T8.a).
    """
    if grid is None:
        grid = torch.linspace(-3.0, 3.0, 200, dtype=torch.float32)
    return interprete_referencia(ind, grid)


# -------------------------------------------------------------
# PLEGADO DE CONSTANTES Y EXPRESION ANALITICA (B1.b, B1.c)
# -------------------------------------------------------------
def analizar_y_plegar(ind):
    """
    Plegado de constantes:
    Rastrea hacia adelante que registros son constantes escalares y cuales
    dependen de la variable de entrada v (r0 inicial).
    Se usa UNICAMENTE para formula(), para contar operadores que dependen de v
    y para la firma fenotipica. NO altera las instrucciones ejecutadas en la red.
    """
    L = len(ind.genes)
    es_const = [False, True, True]        # r0=v (variable), r1=0.0 (const), r2=0.0 (const)
    val_const = [None, 0.0, 0.0]
    expr_reg = ["v", "0", "0"]
    dep_v = [False] * L

    for k in range(L):
        et = e_tilde(ind.e[k])
        if et <= 0.0:
            continue

        op, d, s1, s2 = ind.genes[k]
        nombre, ar, func = OPS[op]

        s1_c = es_const[s1]
        s2_c = es_const[s2] if ar == 2 else True

        if s1_c and s2_c:
            # Ambos operandos son constantes conocidas
            c1 = val_const[s1]
            c2 = val_const[s2] if ar == 2 else 0.0
            try:
                t1 = torch.tensor(c1, dtype=torch.float32)
                t2 = torch.tensor(c2, dtype=torch.float32)
                res = float(func(t1, t2).item())
            except Exception:
                res = 0.0

            if not np.isfinite(res):
                res = 0.0

            if es_const[d]:
                new_c = (1.0 - et) * val_const[d] + et * res
                es_const[d] = True
                val_const[d] = new_c
                expr_reg[d] = "{:.2f}".format(new_c)
            else:
                if et >= 1.0:
                    es_const[d] = True
                    val_const[d] = res
                    expr_reg[d] = "{:.2f}".format(res)
                else:
                    es_const[d] = False
                    val_const[d] = None
                    expr_reg[d] = "{:.2f}*({})+{:.2f}*{:.2f}".format(1.0 - et, expr_reg[d], et, res)
            dep_v[k] = False
        elif nombre == "pdiv" and (s1 == s2 or (expr_reg[s1] == expr_reg[s2] and not es_const[s1])):
            # pdiv(x, x) = x / (x + sign(x)*eps) ~ 1.00 para todo x != 0 (T7.f)
            # Simplificacion analitica como constante escalar
            res = 1.0
            if es_const[d]:
                new_c = (1.0 - et) * val_const[d] + et * res
                es_const[d] = True
                val_const[d] = new_c
                expr_reg[d] = "{:.2f}".format(new_c)
            else:
                if et >= 1.0:
                    es_const[d] = True
                    val_const[d] = res
                    expr_reg[d] = "1.00"
                elif expr_reg[d] == "0":
                    es_const[d] = True
                    val_const[d] = et * res
                    expr_reg[d] = "{:.2f}".format(et * res)
                else:
                    es_const[d] = False
                    val_const[d] = None
                    expr_reg[d] = "{:.2f}*({})+{:.2f}*1.00".format(1.0 - et, expr_reg[d], et)
            dep_v[k] = False
        else:
            # Al menos un operando depende de v
            dep_v[k] = True
            es_const[d] = False
            val_const[d] = None

            op1_str = "{:.2f}".format(val_const[s1]) if es_const[s1] else expr_reg[s1]
            if ar == 2:
                op2_str = "{:.2f}".format(val_const[s2]) if es_const[s2] else expr_reg[s2]
                if nombre in ["+", "*"]:
                    ex = "({} {} {})".format(op1_str, nombre, op2_str)
                else:
                    ex = "{}({}, {})".format(nombre, op1_str, op2_str)
            else:
                ex = "{}({})".format(nombre, op1_str)

            if et >= 0.999:
                expr_reg[d] = ex
            elif expr_reg[d] == "0":
                expr_reg[d] = "{:.2f}*{}".format(et, ex)
            else:
                expr_reg[d] = "{:.2f}*({})+{:.2f}*{}".format(1.0 - et, expr_reg[d], et, ex)

    return dep_v, val_const, expr_reg[0], es_const[0]


def formula(ind):
    """
    Expresion analitica simplificada de phi(v) con correcta colocacion
    de parentesis, plegado de constantes y reduccion de pdiv(x, x) ~ 1 (T7.f).
    """
    _, val_const, expr_0, es_c0 = analizar_y_plegar(ind)
    if es_c0:
        return "phi(v) = {:.4f} (constante degenerada)".format(val_const[0] if val_const[0] is not None else 0.0)
    import re
    expr_0 = re.sub(r"pdiv\(([^,]+),\s*\1\)", r"1.00", expr_0)
    return "phi(v) = " + expr_0


def firma_fenotipo(ind):
    """
    Firma canonica del fenotipo simplificado para el archivo de Pareto/elite.
    Incluye las instrucciones ejecutables que dependen de v y los valores
    plegados de las constantes (redondeados a 2 decimales) (B1.c).
    """
    eff = instrucciones_ejecutables(ind)
    dep_v, val_const, _, _ = analizar_y_plegar(ind)
    sig = []
    for k in range(len(eff)):
        if eff[k]:
            op, d, s1, s2 = ind.genes[k]
            sig.append((op, d, s1, s2 if OPS[op][1] == 2 else -1,
                        round(e_tilde(ind.e[k]), 2), dep_v[k]))
    const_sig = tuple(round(c, 2) if c is not None else None for c in val_const)
    return (tuple(sig), const_sig)


# -------------------------------------------------------------
# RESTRICCION DE NO-LINEALIDAD g1(x) (R4, T6.d)
# -------------------------------------------------------------
def g1(ind, eps_nl=0.05):
    """
    Restriccion de No-Linealidad g1(x) = eps_nl - NL(x) (Leshno et al., 1993).
    NL(x) = 1 - R^2 de la regresion lineal de phi_x(v) contra v en una malla
    de 200 puntos uniformemente distribuidos en [-3.0, 3.0].

    Factible si g1 <= 0 (es decir, NL(x) >= eps_nl).
    Si phi_x no es finita o es constante, es inviable con violacion severa (g1 = 1.0).

    NOTA METODOLOGICA (T6.d): El calculo de correlacion de Pearson utiliza directamente
    el coseno entre vectores centrados (producto punto normalizado). Previamente, usar
    torch.mean(...) para covarianza (divisor N) y torch.var(...) para varianza (divisor N-1)
    introducia un desajuste artificial de (N-1)/N = 199/200 = 0.995 para N=200, produciendo
    r^2=0.9900 y NL=0.0100 en la identidad pura. Al usar normalizacion consistente,
    para la identidad pura r=1.0000000, NL=0.0000000 y g1 = eps_nl - NL = 0.0500000 exacto.
    """
    try:
        v = torch.linspace(-3.0, 3.0, 200, dtype=torch.float32)
        phi = evaluar_malla(ind, v)

        if not torch.isfinite(phi).all():
            ind.g1 = 1.0
            ind.es_factible = False
            return ind.g1

        v_c = v - torch.mean(v)
        phi_c = phi - torch.mean(phi)
        norm_v = torch.sqrt(torch.sum(v_c ** 2))
        norm_phi = torch.sqrt(torch.sum(phi_c ** 2))

        if norm_phi < 1e-7:  # Constante o cuasi-constante degenerada
            ind.g1 = 1.0
            ind.es_factible = False
            return ind.g1

        r_corr = float((torch.sum(v_c * phi_c) / (norm_v * norm_phi)).item())
        r_corr = float(np.clip(r_corr, -1.0, 1.0))
        r2 = float(r_corr ** 2)

        nl = float(1.0 - r2)
        ind.g1 = float(eps_nl - nl)
        ind.es_factible = (ind.g1 <= 0.0)
        return ind.g1
    except Exception:
        ind.g1 = 1.0
        ind.es_factible = False
        return 1.0


# -------------------------------------------------------------
# REGLAS DE FACTIBILIDAD DE DEB (2000) (R4)
# -------------------------------------------------------------
def domina_deb(ind_a, ind_b):
    """
    Reglas de Factibilidad de Deb (2000):
      1. Todo individuo factible (g1 <= 0) domina a cualquier inviable (g1 > 0).
      2. Entre dos individuos factibles, domina el de menor funcion objetivo f.
      3. Entre dos inviables, domina el de menor violacion de restriccion g1.
    """
    a_fac = (ind_a.g1 is not None and ind_a.g1 <= 0.0)
    b_fac = (ind_b.g1 is not None and ind_b.g1 <= 0.0)

    if a_fac and not b_fac:
        return True
    if not a_fac and b_fac:
        return False
    if a_fac and b_fac:
        fa = ind_a.f if ind_a.f is not None else float("inf")
        fb = ind_b.f if ind_b.f is not None else float("inf")
        return fa < fb

    ga = ind_a.g1 if ind_a.g1 is not None else float("inf")
    gb = ind_b.g1 if ind_b.g1 is not None else float("inf")
    return ga < gb


def deb_cmp(ind_a, ind_b):
    """Comparador compatible con functools.cmp_to_key para ordenamiento Deb."""
    if domina_deb(ind_a, ind_b):
        return -1
    elif domina_deb(ind_b, ind_a):
        return 1
    return 0


class ResultadoEquivalencia(tuple):
    """
    Tupla de 4 elementos (es_equiv, desc, r, rmse) compatible con desempaquetado estándar,
    con atributos adicionales .familia y .alpha (T6.b).
    """
    def __new__(cls, es_equiv, desc, mejor_r, mejor_rmse, familia=None, alpha=None):
        return super().__new__(cls, (es_equiv, desc, mejor_r, mejor_rmse))

    def __init__(self, es_equiv, desc, mejor_r, mejor_rmse, familia=None, alpha=None):
        self.es_equiv = es_equiv
        self.desc = desc
        self.r = mejor_r
        self.rmse = mejor_rmse
        self.familia = familia
        self.alpha = alpha


# -------------------------------------------------------------
# DETECTOR DE FAMILIAS PARAMETRICAS DE EQUIVALENCIA (B7, T6.b)
# -------------------------------------------------------------
def detectar_equivalencia(ind, grid=None):
    """
    Ajusta familias parametricas (LeakyReLU con pendiente libre, ELU con alfa libre,
    Swish con beta libre) y baselines fijos (ReLU, GELU, Tanh, Sigmoide, SELU, Mish, Lineal)
    por minimos cuadrados sobre una malla de 200 puntos en [-3.0, 3.0] (B7, T6.b).

    Guarda SIEMPRE el nombre de la funcion mas cercana, correlacion r con 5 decimales y RMSE.
    Salida: (es_equivalente, descripcion, mejor_r, mejor_rmse)
    donde descripcion dice 'variante de <familia> (parametro=..., r=..., RMSE=...)'.
    """
    if grid is None:
        grid = torch.linspace(-3.0, 3.0, 200, dtype=torch.float32)

    try:
        phi = evaluar_malla(ind, grid).cpu().numpy().astype(np.float64)
        if not np.isfinite(phi).all() or np.std(phi) < 1e-7:
            return ResultadoEquivalencia(False, "Degenerada/Invalida", 0.0, 1.0)

        v = grid.cpu().numpy().astype(np.float64)
        v_pos = np.maximum(0.0, v)
        v_neg = np.minimum(0.0, v)

        candidatos_ajuste = []

        # 1. Familia LeakyReLU (alpha libre: pendiente negativa continua)
        try:
            A_lre = np.column_stack([v_pos, v_neg, np.ones_like(v)])
            coeffs, _, _, _ = np.linalg.lstsq(A_lre, phi, rcond=None)
            c1, c2, c0 = coeffs
            if abs(c1) > 1e-6:
                alpha_lre = float(c2 / c1)
                psi_lre = v_pos + alpha_lre * v_neg
                r_lre = float(np.corrcoef(phi, psi_lre)[0, 1])
                pred_lre = c1 * v_pos + c2 * v_neg + c0
                rmse_lre = float(np.sqrt(np.mean((phi - pred_lre) ** 2)))
                if np.isfinite(r_lre) and r_lre > 0:
                    candidatos_ajuste.append((r_lre, rmse_lre, "LeakyReLU", "alpha={:.4f}".format(alpha_lre), alpha_lre))
        except Exception:
            pass

        # 2. Familia ELU (alpha libre: escala exponencial negativa)
        try:
            v_elu_exp = np.exp(np.clip(v_neg, -20.0, 0.0)) - 1.0
            A_elu = np.column_stack([v_pos, v_elu_exp, np.ones_like(v)])
            coeffs_elu, _, _, _ = np.linalg.lstsq(A_elu, phi, rcond=None)
            c1_e, c2_e, c0_e = coeffs_elu
            if abs(c1_e) > 1e-6:
                alpha_elu = float(c2_e / c1_e)
                psi_elu = v_pos + alpha_elu * v_elu_exp
                r_elu = float(np.corrcoef(phi, psi_elu)[0, 1])
                pred_elu = c1_e * v_pos + c2_e * v_elu_exp + c0_e
                rmse_elu = float(np.sqrt(np.mean((phi - pred_elu) ** 2)))
                if np.isfinite(r_elu) and r_elu > 0:
                    candidatos_ajuste.append((r_elu, rmse_elu, "ELU", "alpha={:.4f}".format(alpha_elu), alpha_elu))
        except Exception:
            pass

        # 3. Familia Swish (beta libre: parametro de escala)
        try:
            mejor_r_sw = -1.0
            mejor_beta = 1.0
            mejor_rmse_sw = 1.0
            for beta_cand in np.linspace(0.1, 4.0, 40):
                psi_sw = v / (1.0 + np.exp(-np.clip(beta_cand * v, -20.0, 20.0)))
                r_sw = float(np.corrcoef(phi, psi_sw)[0, 1])
                if r_sw > mejor_r_sw:
                    mejor_r_sw = r_sw
                    mejor_beta = beta_cand
                    A_sw = np.column_stack([psi_sw, np.ones_like(v)])
                    c_sw = np.linalg.lstsq(A_sw, phi, rcond=None)[0]
                    pred_sw = c_sw[0] * psi_sw + c_sw[1]
                    mejor_rmse_sw = float(np.sqrt(np.mean((phi - pred_sw) ** 2)))
            if mejor_r_sw > 0:
                candidatos_ajuste.append((mejor_r_sw, mejor_rmse_sw, "Swish", "beta={:.4f}".format(mejor_beta), mejor_beta))
        except Exception:
            pass

        # 4. Baselines fijos de la literatura
        erf_vec = np.vectorize(math.erf)
        fijos = {
            "ReLU": np.maximum(0.0, v),
            "GELU": 0.5 * v * (1.0 + erf_vec(v / np.sqrt(2.0))),
            "Tanh": np.tanh(v),
            "Sigmoid": 1.0 / (1.0 + np.exp(-np.clip(v, -20.0, 20.0))),
            "SELU": 1.0507009873554804934193349852946 * np.where(v > 0, v, 1.6732632423543772848170429916717 * (np.exp(np.clip(v, -20.0, 0.0)) - 1.0)),
            "Mish": v * np.tanh(np.log1p(np.exp(np.clip(v, -20.0, 20.0)))),
            "Lineal": v,
        }
        for nom, psi_fijo in fijos.items():
            if np.std(psi_fijo) > 1e-7:
                r_fijo = float(np.corrcoef(phi, psi_fijo)[0, 1])
                if np.isfinite(r_fijo):
                    A_f = np.column_stack([psi_fijo, np.ones_like(v)])
                    c_f = np.linalg.lstsq(A_f, phi, rcond=None)[0]
                    pred_f = c_f[0] * psi_fijo + c_f[1]
                    rmse_f = float(np.sqrt(np.mean((phi - pred_f) ** 2)))
                    candidatos_ajuste.append((r_fijo, rmse_f, nom, None, None))

        # Seleccionar la aproximacion con mayor correlacion absoluta
        candidatos_ajuste.sort(key=lambda item: abs(item[0]), reverse=True)
        if not candidatos_ajuste:
            return ResultadoEquivalencia(False, "variante Desconocida (r=0.00000, RMSE=1.00000)", 0.0, 1.0)

        mejor_r, mejor_rmse, mejor_familia, param_str, extra_val = candidatos_ajuste[0]
        if mejor_r >= 0.999:
            es_equiv = True
            if param_str:
                desc = "variante de {} ({}, r={:.5f}, RMSE={:.5f})".format(mejor_familia, param_str, mejor_r, mejor_rmse)
            else:
                desc = "variante de {} (r={:.5f}, RMSE={:.5f})".format(mejor_familia, mejor_r, mejor_rmse)
        else:
            es_equiv = False
            desc = "no equivalente a una función conocida; más cercana: {} (r={:.5f}, RMSE={:.5f})".format(
                mejor_familia, mejor_r, mejor_rmse
            )

        alpha_ret = extra_val if mejor_familia == "LeakyReLU" else None
        return ResultadoEquivalencia(es_equiv, desc, mejor_r, mejor_rmse, familia=mejor_familia, alpha=alpha_ret)
    except Exception:
        return ResultadoEquivalencia(False, "ErrorAnalisis (r=0.00000, RMSE=1.00000)", 0.0, 1.0)


# -------------------------------------------------------------
# CATALOGO DE ACTIVACIONES BASELINE DE LA LITERATURA (R6)
# -------------------------------------------------------------
# NOTA METODOLOGICA: La funcion escalon (Heaviside) se excluye rigurosamente
# debido a que su derivada es nula en casi todo su dominio (nabla = 0 para v != 0),
# lo cual imposibilita el aprendizaje por descenso de gradiente (backpropagation).
def fabrica_activacion(nombre):
    """Fabrica constructora de modulos de activacion PyTorch (T6.a)."""
    if nombre == "ReLU":
        return lambda: nn.ReLU()
    if nombre in ["LeakyReLU_0.10", "LeakyReLU_0.1", "LeakyReLU"]:
        return lambda: nn.LeakyReLU(negative_slope=0.10)
    if nombre == "LeakyReLU_0.01":
        return lambda: nn.LeakyReLU(negative_slope=0.01)
    if nombre == "LeakyReLU_0.25":
        return lambda: nn.LeakyReLU(negative_slope=0.25)
    if isinstance(nombre, str) and nombre.startswith("LeakyReLU_"):
        try:
            sl = float(nombre.split("_")[1])
            return lambda: nn.LeakyReLU(negative_slope=sl)
        except Exception:
            pass
    if nombre == "PReLU":
        return lambda: nn.PReLU(num_parameters=1, init=0.25)  # Pendiente aprendible
    if nombre == "ELU":
        return lambda: nn.ELU(alpha=1.0)
    if nombre == "SELU":
        return lambda: nn.SELU()
    if nombre == "GELU":
        return lambda: nn.GELU()
    if nombre == "Swish" or nombre == "SiLU":
        return lambda: nn.SiLU()
    if nombre == "Mish":
        return lambda: nn.Mish()
    if nombre == "Tanh":
        return lambda: nn.Tanh()
    if nombre == "Sigmoid":
        return lambda: nn.Sigmoid()
    if nombre == "Logistica" or nombre == "Lineal":
        return lambda: nn.Identity()  # Referencia lineal (regresion logistica equivalente)
    raise ValueError("Activacion desconocida en catalogo: " + str(nombre))


# -------------------------------------------------------------
# RED NEURONAL MLP ADAPTABLE (Binaria y Multiclase)
# -------------------------------------------------------------
class MLP(nn.Module):
    """
    Arquitectura MLP configurable por capas y neuronas.
    Soporta clasificacion binaria (salida 1 logit) y multiclase (salida C logits).
    """
    def __init__(self, entradas, make_act, hidden=64, capas=3, salidas=1, usa_bn=True):
        super().__init__()
        self.salidas = salidas
        bloques = []
        n_in = entradas
        for _ in range(capas):
            bloques.append(nn.Linear(n_in, hidden))
            if usa_bn:
                bloques.append(nn.BatchNorm1d(hidden))
            bloques.append(make_act())
            n_in = hidden
        self.cuerpo = nn.Sequential(*bloques)
        self.cabeza = nn.Linear(hidden, salidas)

    def forward(self, x):
        h = self.cuerpo(x)
        return self.cabeza(h)  # Retorna logits en ambos casos


# -------------------------------------------------------------
# OPERADORES GENETICOS CON FACTIBILIDAD DE DEB
# -------------------------------------------------------------
def torneo(pob, k=3):
    """Torneo por reglas de factibilidad de Deb (2000)."""
    aspirantes = random.sample(pob, k)
    ganador = aspirantes[0]
    for c in aspirantes[1:]:
        if domina_deb(c, ganador):
            ganador = c
    return ganador


def cruza(a, b, p_cruza=1.0):
    """Cruza de dos puntos en genes y coeficientes epigeneticos."""
    h1, h2 = a.copia(), b.copia()
    if random.random() < p_cruza:
        L = len(a.genes)
        i, j = sorted(random.sample(range(L + 1), 2))
        for k in range(i, j):
            h1.genes[k], h2.genes[k] = list(b.genes[k]), list(a.genes[k])
            h1.e[k], h2.e[k] = b.e[k], a.e[k]
    h1.f, h1.g1, h1.es_factible = None, None, False
    h2.f, h2.g1, h2.es_factible = None, None, False
    return h1, h2


def muta(ind, cfg, e_fijo=False):
    """Mutacion estructural uniforme y perturbacion epigenetica gaussiana."""
    for k in range(len(ind.genes)):
        if random.random() < cfg["P_MUT"]:
            campo = random.randrange(4)
            ind.genes[k][campo] = (random.randrange(N_OPS) if campo == 0
                                   else random.randrange(N_REG))
        if not e_fijo and random.random() < cfg["P_MUT"]:
            ind.e[k] = float(np.clip(ind.e[k] + random.gauss(0, cfg["SIGMA_E"]), 0.0, 1.0))
    ind.f, ind.g1, ind.es_factible = None, None, False
    ind.f_detalles = {}
    ind.z_detalles = {}
    return ind
