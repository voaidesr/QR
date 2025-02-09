import numpy as np

# The irreducible polynomial for GF(256)
MOD_POLY = 0x11d

gf_exp = np.ones(512, dtype=int)
gf_log = np.zeros(256, dtype=int)

def create_gf_tables() -> None:
    x = 1
    for i in range(255):
        gf_exp[i] = x
        gf_log[x] = i
        x <<= 1
        if x & 0x100:
            x ^= MOD_POLY
    
    for i in range(255, 512):
        gf_exp[i] = gf_exp[i - 255]

def gf_mult(x: int, y: int, field_size: int = 256) -> int:
    if x == 0 or y == 0:
        return 0
    return gf_exp[(gf_log[x] + gf_log[y]) % (field_size - 1)]

def gf_poly_mult(p1: np.ndarray, p2: np.ndarray) -> np.ndarray:
    res = np.zeros(len(p1) + len(p2) - 1, dtype=int)
    for i in range(len(p1)):
        for j in range(len(p2)):
            res[i + j] ^= gf_mult(p1[i], p2[j])
    return res

def gf_poly_gen(degree: int) -> np.ndarray:
    gen = np.array([1], dtype=int)
    for i in range(degree):
        gen = gf_poly_mult(gen, np.array([1, gf_exp[i]], dtype=int))
    return gen

def gf_poly_div(dividend: np.ndarray, divisor: np.ndarray) -> np.ndarray:
    msg_out = list(dividend)
    divisor_degree = len(divisor) - 1

    for i in range(len(dividend) - divisor_degree):
        coef = msg_out[i]
        if coef != 0:
            for j in range(len(divisor)):
                msg_out[i + j] ^= gf_mult(divisor[j], coef)

    remainder = msg_out[-divisor_degree:]
    return remainder

