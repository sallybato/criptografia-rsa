import random


# ============================================================
# FUNÇÕES MATEMÁTICAS AUXILIARES
# ============================================================

def mdc(a, b):
    """Máximo divisor comum (algoritmo de Euclides)."""
    while b:
        a, b = b, a % b
    return a

def inverso_modular(e, phi):
    """
    Calcula o inverso modular de e em relação a phi.
    Ou seja, encontra d tal que (e * d) % phi == 1.
    Usa o algoritmo de Euclides estendido.
    """
    original_phi = phi
    x0, x1 = 0, 1

    if phi == 1:
        return 0

    while e > 1:
        q = e // phi
        phi, e = e % phi, phi
        x0, x1 = x1 - q * x0, x0

    if x1 < 0:
        x1 += original_phi

    return x1

def eh_primo(n, testes=20):
    """
    Verifica se n é primo usando o teste de Miller-Rabin.
    Quanto mais testes, maior a certeza.
    """
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False

    # Escreve n-1 como 2^r * d
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2

    # Realiza os testes
    for _ in range(testes):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)

        if x == 1 or x == n - 1:
            continue

        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False

    return True

def gerar_primo(bits=512):
    """Gera um número primo aleatório com o número de bits especificado."""
    while True:
        n = random.getrandbits(bits)
        n |= (1 << bits - 1) | 1  # garante que tem o tamanho certo e é ímpar
        if eh_primo(n):
            return n


# ============================================================
# GERAÇÃO DE CHAVES
# ============================================================

def gerar_chaves(bits=512):
    """
    Gera um par de chaves RSA (pública e privada).

    Retorna:
        chave_publica  = (e, n)
        chave_privada  = (d, n)
    """
    # 1. Escolhe dois primos grandes p e q
    p = gerar_primo(bits)
    q = gerar_primo(bits)
    while q == p:
        q = gerar_primo(bits)

    # 2. Calcula n = p * q
    n = p * q

    # 3. Calcula phi(n) = (p-1) * (q-1)
    phi = (p - 1) * (q - 1)

    # 4. Escolhe e tal que 1 < e < phi e mdc(e, phi) == 1
    e = 65537  # valor padrão amplamente usado
    if mdc(e, phi) != 1:
        # Se não for coprimo, procura outro e
        e = 3
        while mdc(e, phi) != 1:
            e += 2

    # 5. Calcula d, o inverso modular de e em relação a phi
    d = inverso_modular(e, phi)

    chave_publica  = (e, n)
    chave_privada  = (d, n)

    return chave_publica, chave_privada


# ============================================================
# CIFRAR E DECIFRAR
# ============================================================

def cifrar(mensagem: str, chave_publica: tuple) -> list:
    """
    Cifra uma mensagem usando a chave pública (e, n).
    Cada caractere é cifrado individualmente.
    Retorna uma lista de inteiros.
    """
    e, n = chave_publica
    return [pow(ord(c), e, n) for c in mensagem]

def decifrar(mensagem_cifrada: list, chave_privada: tuple) -> str:
    """
    Decifra uma mensagem usando a chave privada (d, n).
    Retorna a string original.
    """
    d, n = chave_privada
    return ''.join(chr(pow(c, d, n)) for c in mensagem_cifrada)


# ============================================================
# TESTE
# ============================================================

if __name__ == '__main__':
    print("Gerando chaves RSA... (pode demorar alguns segundos)")
    publica, privada = gerar_chaves(bits=512)

    print(f"\nChave pública  (e, n): e={publica[0]}, n={str(publica[1])[:30]}...")
    print(f"Chave privada  (d, n): d={str(privada[0])[:30]}...\n")

    texto = input("Digite uma mensagem para cifrar: ")

    cifrado  = cifrar(texto, publica)
    decifrado = decifrar(cifrado, privada)

    print(f"\nOriginal : {texto}")
    print(f"Cifrado  : {cifrado[:5]}...") # mostra só os 5 primeiros números
    print(f"Decifrado: {decifrado}")
    print(f"\nOK? {texto == decifrado}")