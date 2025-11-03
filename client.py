import socket
import threading
import sys

# --- Configurações do Cliente ---
HOST = '192.168.0.88' 
PORT = 55555      

cliente_socket = None
nickname = ""

# Cores ANSI para o terminal (opcional, mas ajuda a visualizar o status)
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
ENDC = '\033[0m' # Reset de cor

# --- Funções do Cliente ---

def formatar_resposta(mensagem_bruta):
    """
    Processa a mensagem bruta do servidor, separando o código de status.
    """
    partes = mensagem_bruta.split('\n', 1)
    
    # 1. Tenta extrair o código de status da primeira linha
    primeira_linha = partes[0]
    if primeira_linha.startswith(('200', '400', '404')):
        # É uma resposta de status do protocolo
        status = primeira_linha
        corpo = partes[1] if len(partes) > 1 else ""
        
        if status.startswith('200'):
            return f"{GREEN}[200 OK]{ENDC} {status.split(' ', 1)[1]}: {corpo}"
        elif status.startswith('404'):
            return f"{RED}[404 Not Found]{ENDC} {corpo}"
        elif status.startswith('400'):
            return f"{YELLOW}[400 Bad Request]{ENDC} {corpo}"
        else:
            # Caso não seja uma das esperadas
            return f"{YELLOW}[STATUS]{ENDC} {mensagem_bruta}"
    
    # 2. Se não começar com código, é uma mensagem de chat de BROADCAST
    return mensagem_bruta

def receive_messages():
    """
    Thread de recepção, agora formatando as respostas HTTP.
    """
    global nickname
    while True:
        try:
            mensagem = cliente_socket.recv(1024).decode('utf-8')
            
            if not mensagem: 
                print("\n[ERRO] Conexão perdida com o servidor. Fechando...")
                cliente_socket.close()
                sys.exit(0)
            
            if mensagem == 'NICK':
                # No NICK, o cliente envia apenas a palavra (o servidor trata como 'requisição')
                cliente_socket.send(nickname.encode('utf-8'))
                
            else:
                mensagem_formatada = formatar_resposta(mensagem)
                sys.stdout.write(f"\n{mensagem_formatada}\n> ")
                sys.stdout.flush() 

        except Exception as e:
            # print(f"[ERRO na recepção]: {e}") # Debug
            cliente_socket.close()
            sys.exit(0)
            
            

def write_messages():
    """
    Thread de escrita, enviando comandos no formato de protocolo.
    """
    global cliente_socket
    while True:
        try:
            entrada_bruta = input('> ')
            
            # Padroniza para comandos MAIÚSCULOS
            entrada_processada = entrada_bruta.strip()
            
            # --- Tratamento de comandos locais e envio ---
            if entrada_processada.lower() == '/quit':
                comando_envio = "QUIT"
            elif entrada_processada.lower().startswith('/list'):
                 comando_envio = "LIST"
            elif entrada_processada.startswith('/'):
                # Qualquer outro comando com barra ('/') é um erro de sintaxe
                 comando_envio = entrada_processada[1:].upper()
            else:
                # Se não tem barra, é uma mensagem de chat padrão
                comando_envio = f"MSG {entrada_processada}" 
            
            cliente_socket.send(comando_envio.encode('utf-8'))
            
            if comando_envio == "QUIT":
                sys.exit(0) # Encerra após enviar o QUIT

        except EOFError:
            cliente_socket.send("QUIT".encode('utf-8'))
            sys.exit(0)
        except Exception as e:
            # print(f"[ERRO no envio]: {e}") # Debug
            break


def iniciar_cliente():
    """
    Função principal que configura o socket e inicia as threads.
    """
    global cliente_socket
    global nickname
    
    while not nickname:
        nickname = input("Escolha seu nickname (não pode ser vazio): ")
    
    try:
        cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cliente_socket.connect((HOST, PORT))
        
        print(f" Conectado ao servidor IRC (HTTP-like) em {HOST}:{PORT}")
        
    except Exception:
        print(f"[ERRO] Falha ao conectar. Verifique o servidor e o IP/Porta.")
        sys.exit(1)

    receive_thread = threading.Thread(target=receive_messages)
    receive_thread.daemon = True 
    receive_thread.start()

    write_messages()
    
if __name__ == '__main__':
    iniciar_cliente()