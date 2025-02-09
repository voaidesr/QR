"""
FFT‐style (NTT) polynomial multiplication in GF(256).

We use GF(256) = GF(2^8) defined by the irreducible polynomial 0x11d.
Addition is bitwise XOR.
We assume that the generator for the multiplicative group is 2.
The multiplicative group is cyclic of order 255, so we may only choose FFT lengths
N that divide 255 (for example, N = 3, 5, 15, 17, 51, 85, or 255).
"""

# The irreducible polynomial for GF(256)
MOD_POLY = 0x11d

# We choose 2 as our generator (this is common in many RS code implementations)
generator = 2

# Precomputed tables for GF(256) arithmetic.
# EXP_TABLE will hold powers of the generator; LOG_TABLE gives logarithms.
EXP_TABLE = [0] * 512  # We duplicate the table so that indices >= 255 can be handled easily.
LOG_TABLE = [0] * 256

def gf_mul_no_table(a, b):
    """Multiply two GF(256) elements (represented as integers 0..255)
    using the “shift‐and‐reduce” method with modulus MOD_POLY."""
    result = 0
    while b:
        if b & 1:
            result ^= a  # addition in GF(256) is XOR
        b >>= 1
        a <<= 1
        if a & 0x100:  # if degree ≥ 8 then reduce modulo MOD_POLY
            a ^= MOD_POLY
    return result

def init_tables():
    """Initialize the exponentiation and logarithm tables for GF(256)."""
    x = 1
    for i in range(255):
        EXP_TABLE[i] = x
        LOG_TABLE[x] = i
        x = gf_mul_no_table(x, generator)
    # Duplicate the first 255 entries into indices 255..511 for easy modulus arithmetic.
    for i in range(255, 512):
        EXP_TABLE[i] = EXP_TABLE[i - 255]

# Initialize the tables (must be done before using gf_mul, gf_div, etc.)
init_tables()

def gf_mul(a, b):
    """Multiply two GF(256) elements using the log/exp tables."""
    if a == 0 or b == 0:
        return 0
    return EXP_TABLE[(LOG_TABLE[a] + LOG_TABLE[b]) % 255]

def gf_div(a, b):
    """Divide a by b in GF(256) (b must be nonzero)."""
    if a == 0:
        return 0
    if b == 0:
        raise ZeroDivisionError("Division by zero in GF(256)")
    return EXP_TABLE[(LOG_TABLE[a] - LOG_TABLE[b]) % 255]

def gf_pow(a, power):
    """Raise a (in GF(256)) to an integer power."""
    if power == 0:
        return 1
    if a == 0:
        return 0
    log_a = LOG_TABLE[a]
    exp = (log_a * power) % 255
    return EXP_TABLE[exp]

def gf_inv(a):
    """Multiplicative inverse in GF(256)."""
    return gf_div(1, a)

# --- DFT and Inverse DFT (naïve implementation) ---

def dft(poly, N, omega):
    """
    Compute the discrete Fourier transform (DFT) of a length-N vector 'poly'
    in GF(256). Here omega is a primitive N-th root of unity.
    
    That is, for k = 0,...,N-1:
       F[k] = sum_{j=0}^{N-1} poly[j] * (omega)^(j*k)
    """
    F = [0] * N
    for k in range(N):
        s = 0
        for j in range(N):
            # Compute omega^(j*k) in GF(256):
            # (j*k) is an integer exponent; gf_pow handles it via logarithms.
            term = gf_mul(poly[j], gf_pow(omega, j * k))
            s ^= term  # addition in GF(256) is XOR
        F[k] = s
    return F

def idft(F, N, omega):
    """
    Compute the inverse DFT of a length-N vector F in GF(256).
    The inverse is given by:
       poly[j] = (1/N) * sum_{k=0}^{N-1} F[k] * (omega^{-1})^(j*k)
    where 1/N is the multiplicative inverse of N in GF(256).
    (This requires that N is odd, which is the case for our allowed N.)
    """
    omega_inv = gf_div(1, omega)  # or equivalently, gf_pow(omega, 254)
    poly = [0] * N
    inv_N = gf_inv(N)  # N is treated as a GF(256) element (N < 256 and nonzero)
    for j in range(N):
        s = 0
        for k in range(N):
            s ^= gf_mul(F[k], gf_pow(omega_inv, j * k))
        poly[j] = gf_mul(s, inv_N)
    return poly

# --- FFT-based Polynomial Multiplication in GF(256) ---

def poly_multiply(a, b):
    """
    Multiply two polynomials a(x) and b(x) with coefficients in GF(256)
    using an FFT-style (actually, NTT) method.

    The polynomials are given as lists of coefficients (lowest degree first).
    The product will be computed by:
      1. Choosing an FFT length N (dividing 255) such that N >= len(a)+len(b)-1.
      2. Evaluating both polynomials at the N-th roots of unity.
      3. Multiplying the evaluations pointwise.
      4. Inverting the transform to recover the coefficients.
      
    If no suitable N exists, an exception is raised.
    """
    m = len(a)
    n = len(b)
    prod_len = m + n - 1

    # Allowed FFT lengths (divisors of 255)
    allowed_N = [d for d in [1, 3, 5, 15, 17, 51, 85, 255] if d >= prod_len]
    if not allowed_N:
        raise ValueError("Polynomials too long for available FFT lengths in GF(256)")
    N = min(allowed_N)

    # Pad polynomials to length N
    A = a + [0] * (N - m)
    B = b + [0] * (N - n)

    # Choose a primitive N-th root of unity:
    # Since the multiplicative group has order 255, set:
    #   omega = generator^(255/N)
    omega = gf_pow(generator, 255 // N)

    # Compute the DFT of both polynomials
    A_dft = dft(A, N, omega)
    B_dft = dft(B, N, omega)

    # Pointwise multiplication of the transforms
    C_dft = [gf_mul(A_dft[i], B_dft[i]) for i in range(N)]

    # Inverse DFT to get back to coefficient form
    C = idft(C_dft, N, omega)

    # Return only the first prod_len coefficients (the rest are zeros)
    return C[:prod_len]

# --- Example Usage ---

if __name__ == "__main__":
    # Example: Multiply a(x) = 1 + x    and  b(x) = 1 + 2x + 3x^2
    # (Coefficients are given as integers 0..255, representing elements in GF(256))
    poly_a = [1, 1]          # 1 + x
    poly_b = [1, 2, 3]       # 1 + 2x + 3x^2

    prod = poly_multiply(poly_a, poly_b)
    print("Product coefficients in GF(256):", prod)
    # The expected result (over the integers) would be:
    # 1 + (1+2)x + (1+2+3)x^2 + 3x^3, but note that in GF(256) addition is XOR.
    #
    # For instance, (1 + 2) in GF(256) is 1 XOR 2 = 3, so the result here is:
    # [1, 3, (1 XOR 2 XOR 3), 3] = [1, 3, (1^2^3), 3]
    # You can check the arithmetic in GF(256) accordingly.