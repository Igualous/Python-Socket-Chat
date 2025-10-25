## 🚀 Python Socket Chat

Um projeto de chat simples e minimalista baseado no protocolo TCP/IP, desenvolvido em **Python 3** utilizando a arquitetura Cliente-Servidor e o módulo `socket`. Este projeto simula a funcionalidade básica de troca de mensagens de um servidor IRC (*Internet Relay Chat*) em um ambiente de terminal (CLI).

-----

### 🌟 Visão Geral do Projeto

Este chat é uma demonstração prática dos conceitos de **Programação de Sockets** e **Concorrência** em redes de computadores.

| Característica | Detalhes |
| :--- | :--- |
| **Arquitetura** | Cliente-Servidor |
| **Protocolo** | **TCP** (*Transmission Control Protocol*) - Garantindo entrega *confiável* de mensagens. |
| **Linguagem** | Python 3 |
| **Módulos Chave** | `socket` e `threading` |
| **Funcionalidade** | Chat multiusuário em tempo real, com **broadcast** de mensagens para todos os clientes conectados. |

### 🛠️ Como Funciona

O projeto é dividido em dois componentes principais:

#### 1\. `server.py` (O Servidor)

  * **Bind e Listen:** Inicia um socket TCP na porta padrão (`55555`) e aguarda por conexões.
  * **Multithreading:** Utiliza o módulo `threading` para aceitar e gerenciar **múltiplos clientes** simultaneamente, dedicando uma thread para cada conexão ativa.
  * **Broadcast:** Retransmite mensagens recebidas de um cliente para todos os demais na rede.

#### 2\. `client.py` (O Cliente)

  * **Concorrência:** Emprega *duas* threads para garantir a usabilidade no terminal:
      * **Thread de Escrita:** Gerencia a entrada do usuário (`input()`) e envia os dados para o servidor.
      * **Thread de Leitura:** Recebe, em tempo real, as mensagens do servidor e as exibe no terminal.
  * **Comando de Saída:** Suporta o comando `/quit` para encerrar a sessão de forma limpa.

-----

### ⚙️ Instruções de Uso

Para que o chat funcione em duas máquinas diferentes, a configuração de rede é um passo **obrigatório**.

#### 1\. Pré-requisitos

  * Certifique-se de ter o **Python 3** instalado em todas as máquinas.
  * O *Servidor* e o *Cliente* devem estar conectados à **mesma rede** (ex: mesma rede Wi-Fi).

#### 2\. Configuração de Rede (Passo Crucial\!)

Você deve descobrir o **Endereço IP Local** da máquina que irá rodar o `server.py`.

**A. Encontre o IP do Servidor:**

Na máquina do servidor, execute o comando apropriado no terminal:

| Sistema Operacional | Comando no Terminal | Exemplo de IP Local |
| :--- | :--- | :--- |
| **Windows** | `ipconfig` | `192.168.1.10` |
| **Linux/macOS** | `ifconfig` ou `ip a` | `10.0.0.5` |

**B. Ajuste o Cliente:**

Abra o arquivo **`client.py`** e altere a variável `HOST` para o endereço IP local que você acabou de encontrar (o IP da máquina do Servidor).

```python
# client.py

# ATENÇÃO: Substitua '127.0.0.1' pelo IP REAL da máquina do SERVIDOR
HOST = '192.168.1.10' 
PORT = 55555
```

#### 3\. Execução

Abra **terminais diferentes** nas máquinas da sua rede:

**Terminal 1 (Máquina do Servidor):**

Inicie o servidor primeiro.

```bash
python server.py
```

**Terminal 2, 3, etc. (Máquinas Cliente):**

Inicie os clientes.

```bash
python client.py
```

> Após iniciar, cada cliente será solicitado a escolher um *nickname*.

-----

### 🚨 Condições para Funcionamento Correto

1.  **Ordem:** O **servidor** (`server.py`) deve estar **ativo e rodando** antes que qualquer cliente tente se conectar.
2.  **IP e Porta:** As configurações de `HOST` e `PORT` no `client.py` devem corresponder ao IP da máquina do servidor e à porta que ele está escutando.
3.  **Firewall:** Este é o erro de rede **mais comum**.
      * **Sintoma:** O cliente recebe erro de *Connection Refused* ou *Timeout*.
      * **Solução:** É necessário **abrir a porta `55555`** no **Firewall** da máquina que está executando o **Servidor**. Certifique-se de permitir o tráfego de entrada (Inbound) para o protocolo **TCP**.