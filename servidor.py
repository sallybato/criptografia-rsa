import json
import threading
import urllib.request
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from rsa import gerar_chaves, cifrar, decifrar

# ============================================================
# CONFIGURAÇÃO
# ============================================================

MINHA_PORTA   = 5000   # porta que eu escuto
PORTA_CLIENTE = 5001   # porta que o cliente escuta

chave_publica, chave_privada = gerar_chaves(bits=512)
chave_publica_cliente = None  # será preenchida quando o cliente conectar


# ============================================================
# SERVIDOR HTTP — recebe mensagens e chave pública do cliente
# ============================================================

class Handler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        pass  # silencia os logs do servidor

    def do_POST(self):
        global chave_publica_cliente

        tamanho = int(self.headers.get('Content-Length', 0))
        corpo   = self.rfile.read(tamanho)
        dados   = json.loads(corpo)

        # Rota: cliente enviando sua chave pública
        if self.path == '/chave':
            chave_publica_cliente = (dados['e'], dados['n'])
            self.responder(200, {'status': 'ok', 'e': chave_publica[0], 'n': chave_publica[1]})

        # Rota: cliente enviando mensagem cifrada
        elif self.path == '/mensagem':
            cifrada   = dados['mensagem']
            decifrada = decifrar(cifrada, chave_privada)
            print(f"\n[Cliente]: {decifrada}")
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
# ENVIO DE MENSAGENS — envia mensagens cifradas pro cliente
# ============================================================

def enviar_mensagem(texto):
    """Cifra e envia uma mensagem pro cliente."""
    if chave_publica_cliente is None:
        print("  Aguardando o cliente conectar...")
        return

    cifrada = cifrar(texto, chave_publica_cliente)
    dados   = json.dumps({'mensagem': cifrada}).encode()

    try:
        req = urllib.request.Request(
            f'http://localhost:{PORTA_CLIENTE}/mensagem',
            data=dados,
            headers={'Content-Type': 'application/json'}
        )
        urllib.request.urlopen(req)
    except Exception:
        print("  Erro ao enviar mensagem. O cliente está conectado?")


# ============================================================
# LOOP DE ENVIO — roda em thread separada
# ============================================================

def loop_envio():
    """Fica pedindo mensagens pro usuário e enviando pro cliente."""
    while chave_publica_cliente is None:
        pass  # espera o cliente conectar

    print("  Cliente conectado! Pode começar a digitar.\n")

    while True:
        texto = input("Você: ")
        if texto.strip():
            enviar_mensagem(texto)


# ============================================================
# MAIN
# ============================================================

if __name__ == '__main__':
    print("=" * 50)
    print("  CHAT RSA — SERVIDOR")
    print("=" * 50)
    print(f"  Gerando chaves RSA...", end=" ", flush=True)
    print("pronto!")
    print(f"  Escutando na porta {MINHA_PORTA}...")
    print(f"  Aguardando o cliente conectar...\n")

    # Inicia o servidor HTTP em thread separada
    servidor = HTTPServer(('localhost', MINHA_PORTA), Handler)
    t_servidor = threading.Thread(target=servidor.serve_forever, daemon=True)
    t_servidor.start()

    # Inicia o loop de envio em thread separada
    t_envio = threading.Thread(target=loop_envio, daemon=True)
    t_envio.start()

    # Mantém o programa rodando
    try:
        t_servidor.join()
    except KeyboardInterrupt:
        print("\n  Encerrando servidor...")
        servidor.shutdown()