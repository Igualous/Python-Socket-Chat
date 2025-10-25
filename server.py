import socket
import threading

# --- Configurações do Servidor ---
HOST = '0.0.0.0'  # Aceita conexões de qualquer interface de rede
PORT = 55555      # Porta escolhida para o chat (pode ser 6667 ou outra livre)

# Listas globais para armazenar os clientes conectados e seus respectivos nomes
clientes = []
nomes_usuarios = []

# --- Funções do Servidor ---

def broadcast(mensagem, cliente_excecao=None):
    """
    Envia uma mensagem (em bytes) para todos os clientes,
    opcionalmente excluindo um cliente específico (o remetente).
    """
    for cliente in clientes:
        if cliente != cliente_excecao:
            try:
                # O servidor envia a mensagem já formatada (string -> bytes)
                cliente.send(mensagem)
            except:
                # Se houver erro ao enviar, remove o cliente (provavelmente desconectou)
                remover_cliente(cliente)

def remover_cliente(cliente):
    """
    Remove um cliente das listas e notifica a todos sobre a saída.
    """
    if cliente in clientes:
        # Encontra o índice do cliente para obter o nickname
        index = clientes.index(cliente)
        nickname = nomes_usuarios[index]
        
        # Remove das listas
        clientes.remove(cliente)
        nomes_usuarios.remove(nickname)
        
        # Fecha o socket
        cliente.close()
        
        # Notifica a todos
        saida_msg = f"[{nickname}] saiu do chat."
        print(saida_msg)
        broadcast(saida_msg.encode('utf-8'))


def handle_client(cliente):
    """
    Função executada em uma thread separada para cada cliente.
    Gerencia a autenticação e a recepção contínua de mensagens.
    """
    
    # 1. Autenticação do Nickname
    try:
        # Envia a solicitação de NICK para o cliente
        cliente.send('NICK'.encode('utf-8'))
        
        # Recebe o nickname (máximo 1024 bytes)
        nickname = cliente.recv(1024).decode('utf-8')
        
        # Adiciona às listas globais
        nomes_usuarios.append(nickname)
        
    except:
        # Se não conseguir obter o nickname, remove e encerra a thread
        remover_cliente(cliente)
        return

    # Notificação de entrada
    entrada_msg = f"{nickname} entrou no chat!"
    print(f"[NOVO] {entrada_msg}")
    broadcast(entrada_msg.encode('utf-8'), cliente) # Notifica a todos, exceto ao próprio recém-chegado

    # 2. Loop principal de mensagens
    while True:
        try:
            # Recebe a mensagem do cliente
            mensagem = cliente.recv(1024)
            
            if not mensagem: 
                # Se não há mensagem, o cliente desconectou
                break 
            
            # Decodifica e formata a mensagem
            mensagem_decodificada = mensagem.decode('utf-8')

            # Tratar comandos do cliente, se houver (ex: /quit)
            if mensagem_decodificada.lower() == '/quit':
                break

            # Mensagem para o chat
            mensagem_formatada = f"[{nickname}]: {mensagem_decodificada}"
            print(f"[MSG] {mensagem_formatada}")
            
            # Faz o broadcast (o servidor envia a mensagem formatada para todos os outros)
            broadcast(mensagem_formatada.encode('utf-8'), cliente)
            
        except:
            # Quebra do loop em caso de erro de conexão
            break

    # 3. Tratamento de desconexão
    remover_cliente(cliente)


def iniciar_servidor():
    """
    Configura e inicia o socket do servidor para aceitar conexões.
    """
    
    # Cria o socket TCP
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Faz o bind no host e porta
    try:
        servidor.bind((HOST, PORT))
    except Exception as e:
        print(f"Erro ao fazer bind: {e}")
        return

    # Entra no modo de escuta
    servidor.listen()
    
    print(f"=============================================")
    print(f" Servidor IRC Simplificado rodando em {HOST}:{PORT}")
    print(f" Aguardando conexões...")
    print(f"=============================================")

    # Loop de aceitação de clientes
    while True:
        try:
            # Espera e aceita uma nova conexão
            cliente, endereco = servidor.accept()
            print(f"\n[INFO] Nova conexão de {endereco[0]}:{endereco[1]}")
            
            # Adiciona o novo cliente à lista ANTES da thread (para evitar race conditions)
            clientes.append(cliente) 
            
            # Inicia uma thread para manipular a comunicação com o novo cliente
            thread = threading.Thread(target=handle_client, args=(cliente,))
            thread.start()
            
        except KeyboardInterrupt:
            # Permite interromper o servidor com Ctrl+C
            print("\nServidor encerrado pelo usuário.")
            servidor.close()
            break
        except Exception as e:
            print(f"\nErro no loop principal do servidor: {e}")
            break

# --- Chamada Principal ---
if __name__ == '__main__':
    iniciar_servidor()