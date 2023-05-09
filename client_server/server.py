#!/usr/bin/python3

import sys
import socket
import select
import json
import base64
import csv
import random
from common_comm import send_dict, recv_dict, sendrecv_dict

from Cryptodome.Cipher import AES
from Cryptodome.Hash import SHA256


class text:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


class log_levels:
    FATAL = text.RED + "[FATAL]" + text.END
    ERROR = text.RED + "[ERROR]" + text.END
    WARN = text.YELLOW + "[WARN]" + text.END
    INFO =  text.GREEN + "[INFO]" + text.END
    DEBUG = text.GREEN + "[DEBUG]" + text.END
    TRACE = text.GREEN + "[TRACE]" + text.END


# Dicionário com a informação relativa aos clientes
users = {}


# return the client_id of a socket or None


def find_client_id(client_sock):
    # Devolve o id através do sock
    for client_id in users:
        if users[client_id]["socket"] == client_sock:
            return client_id

    return "Not found"


# Função para encriptar valores a enviar em formato json com codificação base64
# return int data encrypted in a 16 bytes binary string and coded base64
def encrypt_intvalue(cipherkey, data):

    intToBytes = data.to_bytes((data.bit_length() + 7) // 8, byteorder='big')
    
    sixteenByteData = intToBytes.ljust(16 * ((len(intToBytes) + 15) // 16), b'\0')
    
    cipher = AES.new(cipherkey, AES.MODE_ECB)
    
    encrypted = cipher.encrypt(sixteenByteData)

    base64 = base64.b64encode(encrypted).decode('ascii')
    
    return base64


# Função para desencriptar valores recebidos em formato json com codificação base64
# return int data decrypted from a 16 bytes binary string and coded base64
def decrypt_intvalue(cipherkey, data):

    encrypted = base64.b64decode(data)
    
    cipher = AES.new(cipherkey, AES.MODE_ECB)
    
    decrypted = cipher.decrypt(encrypted)
    
    finalData = decrypted.rstrip(b'\0')

    int = int.from_bytes(finalData, byteorder='big')
    
    return int


# Função auxiliar para gerar o resultado - já está implementada
# return int value and list of description strings identifying the characteristic of the value
def generate_result(list_values):
    if len(list_values) % 2 == 1:
        test = 4
    else:
        test = 3

    minimal = min(list_values)
    maximal = max(list_values)
    first = list_values[0]
    last = list_values[-1]

    choice = random.randint(0, test)
    if choice == 0:
        if minimal == first:
            return first, ["min", "first"]
        elif maximal == first:
            return first, ["max", "first"]
        else:
            return first, ["first"]
    elif choice == 1:
        if minimal == last:
            return last, ["min", "last"]
        elif maximal == last:
            return last, ["max", "last"]
        else:
            return last, ["last"]
    elif choice == 2:
        if minimal == first:
            return first, ["min", "first"]
        elif minimal == last:
            return last, ["min", "last"]
        else:
            return minimal, ["min"]
    elif choice == 3:
        if maximal == first:
            return first, ["max", "first"]
        elif maximal == last:
            return last, ["max", "last"]
        else:
            return maximal, ["max"]
    elif choice == 4:
        list_values.sort()
        median = list_values[len(list_values) // 2]
        if median == first:
            return first, ["median", "first"]
        elif median == last:
            return last, ["median", "last"]
        else:
            return median, ["median"]
    else:
        return None


# Incomming message structure:
# { op = "START", client_id, [cipher] }
# { op = "QUIT" }
# { op = "NUMBER", number }
# { op = "STOP", [shasum] }
# { op = "GUESS", choice }
#
# Outcomming message structure:
# { op = "START", status }
# { op = "QUIT" , status }
# { op = "NUMBER", status }
# { op = "STOP", status, value }
# { op = "GUESS", status, result }


#
# Suporte de descodificação da operação pretendida pelo cliente - já está implementada
#
def new_msg(client_sock):
    request = recv_dict(client_sock)
    # print( "Command: %s" % (str(request)) )

    op = request["op"]
    if op == "START":
        response = new_client(client_sock, request)
    elif op == "QUIT":
        response = quit_client(client_sock, request)
    elif op == "NUMBER":
        response = number_client(client_sock, request)
    elif op == "STOP":
        response = stop_client(client_sock, request)
    elif op == "GUESS":
        response = guess_client(client_sock, request)
    else:
        response = {"op": op, "status": False, "error": "Operação inexistente"}

    # print (response)
    send_dict(client_sock, response)


#
# Suporte da criação de um novo cliente - operação START
#
# detect the client in the request
# verify the appropriate conditions for executing this operation
# process the client in the dictionary
# return response message with or without error message


def new_client(client_sock, request):
    client_id = request["client_id"]
    # Verifica se a ligação é segura
    if request["cipher"] is None:
        cipher = None
    else:
        cipher = base64.b64decode(request["cipher"])

    # Verifica se o cliente já está ligado, e adiciona-o caso contrário
    if client_id not in users:
        users[client_id] = {"socket": client_sock, "cipher": cipher, "numbers": []}
        return {"op": "START", "status": True}
    else:
        return {"op": "START", "status": False, "error": "Cliente já registado"}


#
# Suporte da eliminação de um cliente - já está implementada
#
# obtain the client_id from his socket and delete from the dictionary
def clean_client(client_sock):
    client_id = find_client_id(client_sock)
    if client_id != None:
        print("Client %s removed\n" % client_id)
        del users[client_id]


#
# Suporte do pedido de desistência de um cliente - operação QUIT
#
# obtain the client_id from his socket
# verify the appropriate conditions for executing this operation
# process the report file with the QUIT result
# eliminate client from dictionary using the function clean_client
# return response message with or without error message
def quit_client(client_sock):
    if find_client_id(client_sock) in users:
        clean_client(client_sock)
        return {"op": "QUIT", "status": True}
    else:
        return {"op": "QUIT", "status": False, "error": "Client not registered"}


#
# Suporte da criação de um ficheiro csv com o respectivo cabeçalho - já está implementada
#
def create_file():
    with open("result.csv", "w", newline="") as csvfile:
        columns = ["client_id", "number_of_numbers", "guess"]

        fw = csv.DictWriter(csvfile, delimiter=",", fieldnames=columns)
        fw.writeheader()


#
# Suporte da actualização de um ficheiro csv com a informação do cliente
#
# update report csv file with the simulation of the client
def update_file(client_id, size, guess):
    return None


#
# Suporte do processamento do número de um cliente - operação NUMBER
#
# obtain the client_id from his socket
# verify the appropriate conditions for executing this operation
# return response message with or without error message
def number_client(client_sock, request):
    # Como o cliente já está registado (à partida),
    # acho que é melhor usar find_client_id ao invés de request
    client_id = find_client_id(client_sock)

    # Se não estiver registado, dá erro:
    if client_id not in users:
        return {"op": "NUMBER", "status": False, "error": "Cliente ainda não está registado"}

    # Se estiver registado:
    else:
        try:
            # Se a ligação não for segura, guarda o que recebe sem decriptar
            if users[client_id]["cipher"] == None:
                users[client_id]["numbers"].append(int(request["number"]))
            else:
                # Decripta a informação antes de a guardar
                users[client_id]["numbers"].append(decrypt_intvalue(
                    users[client_id]["cipher"], request["number"]))

            return {"op": "NUMBER", "status": True}

        except:
            return {"op": "NUMBER", "status": False, "error": "Número inválido"}


#
# Suporte do pedido de terminação de um cliente - operação STOP
#
# obtain the client_id from his socket
# verify the appropriate conditions for executing this operation
# randomly generate a value to return using the function generate_result
# process the report file with the result
# return response message with result or error message
def stop_client(client_sock, request):
    # ...
    # value, solution = generate_result (users[client_id]["numbers"])
    # ...
    return None


#
# Suporte da adivinha de um cliente - operação GUESS
#
# obtain the client_id from his socket
# verify the appropriate conditions for executing this operation
# eliminate client from dictionary
# return response message with result or error message

def guess_client(client_sock, request):

    client_id = get_client_id(client_sock)


    if client_id not in clients:
        return create_error_response(f"Client {client_id} not found")
    if not clients[client_id]["finished"]:
        return create_error_response(f"Client {client_id} has not finished sending data")

    client_data = clients.pop(client_id)

    chosen_value = client_data["chosen_value"]
    if chosen_value is None:
        return create_error_response(f"Client {client_id} has not received chosen value")

    client_values = client_data["values"]
    result = None
    if chosen_value == client_values[0]:
        result = "O numero escolhido foi o primeiro numero"
    elif chosen_value == client_values[-1]:
        result = "O numero escolhido foi o ultimo numero"
    elif chosen_value == min(client_values):
        result = "O numero escolhido foi o minimo"
    elif chosen_value == max(client_values):
        result = "O numero escolhido foi o maximo"
    elif len(client_values) % 2 != 0 and int(chosen_value) == sorted(numbers)[len(numbers) // 2]:
        result = "O numero escolhido foi @ mediana"

    with open("report.csv", "a") as f:
        f.write(f"{client_id},{len(client_values)},{result}\n")

    response = {
        "type": "response",
        "status": "success",
        "message": f"Chosen value was {chosen_value}. Guessed {result}" if result else f"Chosen value was {chosen_value}. Could not guess"
    }
    return json.dumps(response).encode()



def bad_usage():
    print(f"Usage: python {sys.argv[0]} <port>")
    print("")
    print("Arguments:")
    print("  <port>           The port number to use for the connection.")
    sys.exit(2)


def main():
    # validate the number of arguments and eventually print error message and exit with error
    # verify type of of arguments and eventually print error message and exit with error

    if len(sys.argv) < 2:
        print(log_levels.ERROR, "No arguments provided.\n")
        bad_usage()
    elif len(sys.argv) > 2:
        print(log_levels.ERROR, "Too many arguments provided.\n")
        bad_usage()

    # obtain the port number
    if (sys.argv[1].isnumeric()) and (1024 <= int(sys.argv[1]) <= 65535):
        port = int(sys.argv[1])
    else:
        print(log_levels.ERROR, "The provided port argument is not valid.\n")
        bad_usage()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("127.0.0.1", port))
    server_socket.listen()

    clients = []
    create_file()

    while True:
        try:
            available = select.select([server_socket] + clients, [], [])[0]
        except ValueError:
            # Sockets may have been closed, check for that
            for client_sock in clients:
                if client_sock.fileno() == -1:
                    clients.remove(client_sock)  # closed
            continue  # Reiterate select

        for client_sock in available:
            # New client?
            if client_sock is server_socket:
                newclient, addr = server_socket.accept()
                clients.append(newclient)
            # Or an existing client
            else:
                # See if client sent a message
                if len(client_sock.recv(1, socket.MSG_PEEK)) != 0:
                    # client socket has a message
                    # print ("server" + str (client_sock))
                    new_msg(client_sock)
                else:  # Or just disconnected
                    clients.remove(client_sock)
                    clean_client(client_sock)
                    client_sock.close()
                    break  # Reiterate select


if __name__ == "__main__":
    main()
