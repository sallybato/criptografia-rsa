import json
import threading
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler
from rsa import gerar_chaves, cifrar, decifrar

# ============================================================
# CONFIGURAÇÃO
# ============================================================

MINHA_PORTA   = 5001  # porta que eu escuto
PORTA_SERVIDOR = 5000  # porta do servidor

chave_publica, chave_privada = gerar_chaves(bits=512)
chave_publica_servidor = None  # será preenchida ao conectar


# ============================================================
# SERVIDOR HTTP — recebe mensagens do servidor
# ============================================================

class Handler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        pass  # silencia os logs

    def do_POST(self):
        tamanho = int(self.headers.get('Content-Length', 0))
        corpo   = self.rfile.read(tamanho)
        dados   = json.loads(corpo)

        if self.path == '/mensagem':
            cifrada   = dados['mensagem']
            decifrada = decifrar(cifrada, chave_privada)
            print(f"\n[Servidor]: {decifrada}")
            print("Você: ", end="", flush=True)
            self.responder(200, {'status': 'ok'})

        else:
            self.responder(404, {'status': 'não encontrado'})

    def responder(self, codigo, dados):
        corpo = json.dumps(dados).encode()
        self.send_response(codigo)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(corpo))
        self.end_headers()
        self.wfile.write(corpo)


# ============================================================
# CONEXÃO — troca chaves públicas com o servidor
# ============================================================

def conectar():
    """Envia a chave pública pro servidor e recebe a dele."""
    global chave_publica_servidor

    dados = json.dumps({'e': chave_publica[0], 'n': chave_publica[1]}).encode()

    try:
        req = urllib.request.Request(
            f'http://localhost:{PORTA_SERVIDOR}/chave',
            data=dados,
            headers={'Content-Type': 'application/json'}
        )
        resposta = urllib.request.urlopen(req)
        resp     = json.loads(resposta.read())
        chave_publica_servidor = (resp['e'], resp['n'])
        print("  Conectado ao servidor! Pode começar a digitar.\n")
    except Exception:
        print("  Erro ao conectar. O servidor está rodando?")
        exit(1)


# ============================================================
# ENVIO DE MENSAGENS
# ============================================================

def enviar_mensagem(texto):
    """Cifra e envia uma mensagem pro servidor."""
    cifrada = cifrar(texto, chave_publica_servidor)
    dados   = json.dumps({'mensagem': cifrada}).encode()

    try:
        req = urllib.request.Request(
            f'http://localhost:{PORTA_SERVIDOR}/mensagem',
            data=dados,
            headers={'Content-Type': 'application/json'}
        )
        urllib.request.urlopen(req)
    except Exception:
        print("  Erro ao enviar mensagem.")


# ============================================================
# LOOP DE ENVIO
# ============================================================

def loop_envio():
    while True:
        texto = input("Você: ")
        if texto.strip():
            enviar_mensagem(texto)


# ============================================================
# MAIN
# ============================================================

if __name__ == '__main__':
    print("=" * 50)
    print("  CHAT RSA — CLIENTE")
    print("=" * 50)
    print("  Gerando chaves RSA...", end=" ", flush=True)
    print("pronto!")
    print(f"  Conectando ao servidor na porta {PORTA_SERVIDOR}...")

    # Inicia o servidor HTTP em thread separada
    servidor = HTTPServer(('localhost', MINHA_PORTA), Handler)
    t_servidor = threading.Thread(target=servidor.serve_forever, daemon=True)
    t_servidor.start()

    # Troca chaves com o servidor
    conectar()

    # Inicia o loop de envio em thread separada
    t_envio = threading.Thread(target=loop_envio, daemon=True)
    t_envio.start()

    # Mantém o programa rodando
    try:
        t_servidor.join()
    except KeyboardInterrupt:
        print("\n  Encerrando cliente...")
        servidor.shutdown()