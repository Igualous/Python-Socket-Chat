import socket
import threading
import sys

# --- Configurações do Cliente ---
# Se o servidor estiver rodando na mesma máquina, use 127.0.0.1
HOST = '192.168.0.88' # <----  ENDEREÇO IP DA MÁQUINA QUE RODA O SERVIDOR
PORT = 55555      # Deve ser a mesma porta configurada no server.py

# Variáveis globais
cliente_socket = None
nickname = ""

# --- Funções do Cliente ---

def receive_messages():
    """
    Função rodando em uma thread separada para receber e exibir
    mensagens do servidor no terminal.
    """
    while True:
        try:
            # Tenta receber dados do servidor
            mensagem = cliente_socket.recv(1024).decode('utf-8')
            
            if not mensagem:
                # Se não receber dados, o servidor provavelmente fechou a conexão
                print("\n[ERRO] Conexão perdida com o servidor. Fechando...")
                cliente_socket.close()
                sys.exit(0) # Encerra o programa
            
            if mensagem == 'NICK':
                # Mensagem especial do servidor solicitando o nickname
                # O servidor espera a resposta para este comando
                cliente_socket.send(nickname.encode('utf-8'))
                
            else:
                # Mensagem normal do chat: imprime no terminal
                # sys.stdout.write e flush são usados para garantir que a mensagem 
                # seja impressa imediatamente e não interfira na linha de 'input'
                sys.stdout.write(f"\n{mensagem}\n> ")
                sys.stdout.flush() 

        except ConnectionResetError:
            # Tratamento específico para quando o servidor é abruptamente fechado
            print("\n[ERRO] Conexão redefinida pelo host (servidor fechou).")
            cliente_socket.close()
            sys.exit(0)
        except Exception as e:
            # Tratamento genérico de outros erros de conexão
            print(f"\n[ERRO] Ocorreu um erro na recepção: {e}")
            cliente_socket.close()
            sys.exit(0)
            
            

def write_messages():
    """
    Função rodando na thread principal para ler a entrada do usuário
    e enviar as mensagens para o servidor.
    """
    global cliente_socket
    while True:
        try:
            # Solicita a entrada do usuário, apresentando um prompt
            mensagem = input('> ')
            
            # --- Tratamento de comandos locais (opcional) ---
            if mensagem.lower() == '/quit':
                print("[SAÍDA] Desconectando do servidor...")
                cliente_socket.send(mensagem.encode('utf-8')) # Informa o servidor
                cliente_socket.close()
                sys.exit(0)
            
            # Envia a mensagem para o servidor
            cliente_socket.send(mensagem.encode('utf-8'))
            
        except EOFError:
            # Tratamento para Ctrl+D (fim do arquivo) no Linux/Mac
            print("\n[SAÍDA] Desconectando por EOF.")
            cliente_socket.close()
            break
        except Exception as e:
            # Se o socket fechar enquanto tenta enviar
            print(f"[ERRO] Falha ao enviar a mensagem. Desconectando...")
            break


def iniciar_cliente():
    """
    Função principal que configura o socket e inicia as threads.
    """
    global cliente_socket
    global nickname
    
    # 1. Obter Nickname
    while not nickname:
        nickname = input("Escolha seu nickname (não pode ser vazio): ")
    
    # 2. Configurar Socket e Conexão
    try:
        cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cliente_socket.connect((HOST, PORT))
        
        print(f"=============================================")
        print(f" Conectado ao servidor IRC em {HOST}:{PORT}")
        print(f" Digite '/quit' para sair. Mensagens:\n")
        
    except ConnectionRefusedError:
        print(f"[ERRO] Conexão recusada. Verifique se o servidor está ativo em {HOST}:{PORT}.")
        sys.exit(1)
    except Exception as e:
        print(f"[ERRO] Ocorreu um erro na conexão: {e}")
        sys.exit(1)

    # 3. Iniciar Threads
    
    # Thread de Recepção: Roda em segundo plano para ouvir o servidor
    receive_thread = threading.Thread(target=receive_messages)
    receive_thread.daemon = True # Define como daemon para fechar automaticamente com o programa principal
    receive_thread.start()

    # Thread de Escrita: Roda na thread principal (para manter o 'input')
    write_messages()
    
# --- Chamada Principal ---
if __name__ == '__main__':
    iniciar_cliente()