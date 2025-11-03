import socket
import threading
import sys
# O Lock para sincronismo é mantido
lock_recursos = threading.Lock() 

# --- Configurações do Servidor ---
HOST = '0.0.0.0'
PORT = 55555

# --- Variáveis Globais (Recursos Compartilhados) ---
clientes = []
nomes_usuarios = []


# --- Funções Auxiliares de Resposta ---

def enviar_resposta(cliente, status_code, status_text, corpo=""):
    """
    Formata e envia uma resposta no formato HTTP simplificado.
    Ex: '200 OK\nMensagem de Status\nCorpo da Mensagem'
    """
    resposta = f"{status_code} {status_text}\n{corpo}"
    try:
        cliente.send(resposta.encode('utf-8'))
    except:
        remover_cliente(cliente) # Se falhar, remove o cliente

def broadcast(mensagem, cliente_excecao=None):
    """
    Envia uma mensagem de chat (sem código HTTP) para todos os clientes, exceto o remetente.
    """
    # ... (código mantido, pois é uma funcionalidade interna do chat)
    lock_recursos.acquire()
    clientes_copia = list(clientes)
    lock_recursos.release()
    
    for cliente in clientes_copia:
        if cliente != cliente_excecao:
            try:
                # O servidor envia o conteúdo da mensagem de chat (não a resposta HTTP)
                cliente.send(mensagem)
            except:
                remover_cliente(cliente)

def remover_cliente(cliente):
    """
    Remove um cliente das listas com acesso protegido por Lock.
    """
    lock_recursos.acquire()
    try:
        if cliente in clientes:
            index = clientes.index(cliente)
            nickname = nomes_usuarios[index]
            
            clientes.remove(cliente)
            nomes_usuarios.remove(nickname)
            cliente.close()
            
            saida_msg = f"[{nickname}] saiu do chat."
            print(saida_msg)
            broadcast(saida_msg.encode('utf-8'))
            
    finally:
        lock_recursos.release()

# --- Funções de Requisição (Análise do Protocolo de Chat) ---

def processar_requisicao(cliente, nickname, requisicao):
    """
    Analisa a requisição do cliente e responde com um código HTTP.
    Formato esperado: COMANDO [Argumentos]
    """
    partes = requisicao.split(' ', 1)
    comando = partes[0].upper()
    argumento = partes[1] if len(partes) > 1 else ""

    if comando == 'MSG':
        # Comando MSG <mensagem>
        if argumento:
            mensagem_chat = f"[{nickname}]: {argumento}"
            print(f"[MSG] {mensagem_chat}")
            broadcast(mensagem_chat.encode('utf-8'), cliente)
            # Resposta ao cliente: 200 OK
            enviar_resposta(cliente, "200", "OK", "Mensagem enviada com sucesso.")
        else:
            # Resposta ao cliente: 400 Bad Request
            enviar_resposta(cliente, "400", "Bad Request", "Formato: MSG <mensagem>")
            
    elif comando == 'LIST':
        # Comando LIST (Lista de usuários)
        lock_recursos.acquire()
        lista_usuarios = ", ".join(nomes_usuarios)
        lock_recursos.release()
        
        # Resposta ao cliente: 200 OK
        enviar_resposta(cliente, "200", "OK - User List", f"Usuários online: {lista_usuarios}")

    elif comando == 'QUIT':
        # Comando QUIT
        enviar_resposta(cliente, "200", "OK - Disconnecting", "Sessão encerrada.")
        return True # Sinaliza para o handler desconectar
    
    else:
        # Resposta ao cliente: 404 Not Found
        enviar_resposta(cliente, "404", "Not Found", f"Comando desconhecido: {comando}")
        
    return False # Não desconectar

def handle_client(cliente):
    """
    Gerencia a autenticação e o loop de requisições/respostas.
    """
    nickname = ""
    # ... (Lógica de Autenticação NICK e adição à lista - mantida com Lock)
    try:
        cliente.send('NICK'.encode('utf-8'))
        nickname_bruto = cliente.recv(1024).decode('utf-8')
        
        # O cliente envia o nickname, que é tratado como uma 'requisição' inicial.
        nickname = nickname_bruto.split(' ', 1)[0] # Pega apenas a primeira palavra
        
        lock_recursos.acquire()
        try:
            nomes_usuarios.append(nickname)
        finally:
            lock_recursos.release()
            
        entrada_msg = f"{nickname} entrou no chat!"
        print(f"[NOVO] {entrada_msg}")
        broadcast(entrada_msg.encode('utf-8'), cliente)
        
        # Confirmação de conexão com código 200
        enviar_resposta(cliente, "200", "OK - Connected", f"Bem-vindo(a), {nickname}.")

    except:
        remover_cliente(cliente)
        return

    # Loop principal de requisições
    while True:
        try:
            requisicao = cliente.recv(1024).decode('utf-8').strip()
            
            if not requisicao:
                break 

            if processar_requisicao(cliente, nickname, requisicao):
                break # Se processar_requisicao retornar True (QUIT)

        except:
            break

    remover_cliente(cliente)

# ... (restante do código iniciar_servidor() mantido com Lock)

def iniciar_servidor():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        servidor.bind((HOST, PORT))
        servidor.listen()
    except Exception as e:
        print(f"Erro ao iniciar o servidor: {e}")
        return

    print(f" Servidor IRC Simplificado (HTTP-like) rodando em {HOST}:{PORT}")

    while True:
        try:
            cliente, endereco = servidor.accept()
            print(f"\n[INFO] Nova conexão de {endereco[0]}:{endereco[1]}")
            
            lock_recursos.acquire()
            try:
                clientes.append(cliente) 
            finally:
                lock_recursos.release()
            
            thread = threading.Thread(target=handle_client, args=(cliente,))
            thread.start()
            
        except KeyboardInterrupt:
            print("\nServidor encerrado pelo usuário.")
            servidor.close()
            break
        except Exception as e:
            print(f"\nErro no loop principal do servidor: {e}")
            break

if __name__ == '__main__':
    iniciar_servidor()