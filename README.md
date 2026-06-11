# RSA

Implementação do algoritmo RSA do zero em Python, sem bibliotecas de criptografia.

Este repositório contém dois programas independentes que utilizam a mesma implementação do RSA:

---

## Arquivos

| Arquivo | Descrição |
|---|---|
| `rsa.py` | Implementação pura do RSA |
| `servidor.py` | Aplicação de chat — lado servidor |
| `cliente.py` | Aplicação de chat — lado cliente |

> Os programas são independentes e estão na mesma pasta. `servidor.py` e `cliente.py` importam o `rsa.py` para cifrar e decifrar as mensagens.

---

## rsa.py — RSA Puro

Implementação completa do algoritmo RSA do zero, incluindo:

1. **Geração de primos** — teste de Miller-Rabin para primos de 512 bits
2. **Geração de chaves** — calcula `n`, `phi`, `e` e `d`
3. **Cifrar** — `c = m^e mod n`
4. **Decifrar** — `m = c^d mod n`

### Como rodar

```
python rsa.py
```

O programa gera um par de chaves, pede uma mensagem, cifra e decifra mostrando o resultado.

**Exemplo:**
```
Gerando chaves RSA... pronto!

Chave pública  (e, n): e=65537, n=9823...
Chave privada  (d, n): d=4521...

Digite uma mensagem para cifrar: oi professor
Original : oi professor
Cifrado  : [23847, 91823, ...]
Decifrado: oi professor
OK? True
```

---

## servidor.py e cliente.py — Chat com RSA

Chat bidirecional entre duas aplicações com mensagens criptografadas usando RSA.

**Como funciona:**
- Cada lado gera seu próprio par de chaves RSA
- Na conexão, os dois trocam as chaves públicas automaticamente
- Cada mensagem é cifrada com a chave pública de quem vai receber
- Só quem tem a chave privada consegue decifrar

### Como rodar

Abra **dois terminais** na mesma pasta e execute:

**Terminal 1 — Servidor:**
```
python servidor.py
```

**Terminal 2 — Cliente:**
```
python cliente.py
```

Após a conexão, basta digitar nos dois terminais para trocar mensagens.

### Exemplo

```
# Terminal 1 (Servidor)         # Terminal 2 (Cliente)
CHAT RSA — SERVIDOR             CHAT RSA — CLIENTE
Gerando chaves RSA... pronto!   Gerando chaves RSA... pronto!
Aguardando o cliente...         Conectado ao servidor!

Você: olá!                      [Servidor]: olá!
[Cliente]: tudo bem?            Você: tudo bem?
```

---

## Bibliotecas utilizadas

| Biblioteca | Uso |
|---|---|
| `random` | Geração de números aleatórios para os primos |
| `json` | Serialização das mensagens entre servidor e cliente |
| `threading` | Execução paralela de envio e recebimento |
| `urllib` | Envio de requisições HTTP entre as aplicações |
| `http.server` | Servidor HTTP nativo para receber mensagens |

> Nenhuma biblioteca de criptografia foi utilizada. O algoritmo RSA é implementado inteiramente do zero.
