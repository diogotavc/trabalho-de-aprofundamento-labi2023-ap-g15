#!/usr/bin/python3

import os
import sys
import socket
import json
import base64
import ipaddress
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

# Function to encript values for sending in json format
# return int data encrypted in a 16 bytes binary string coded in base64
def encrypt_intvalue (cipherkey, data):
	return None


# Function to decript values received in json format
# return int data decrypted from a 16 bytes binary strings coded in base64
def decrypt_intvalue (cipherkey, data):
	return None


# verify if response from server is valid or is an error message and act accordingly - já está implementada
def validate_response (client_sock, response):
	if not response["status"]:
		print (response["error"])
		client_sock.close ()
		sys.exit (3)




# process QUIT operation
def quit_action (client_sock, attempts):
	return None


# Outcomming message structure:
# { op = "START", client_id, [cipher] }
# { op = "QUIT" }
# { op = "NUMBER", number }
# { op = "STOP", [shasum] }
# { op = "GUESS", choice }
#
# Incomming message structure:
# { op = "START", status }
# { op = "QUIT" , status }
# { op = "NUMBER", status }
# { op = "STOP", status, value }
# { op = "GUESS", status, result }

#
# Suport for executing the client pretended behaviour
#
def run_client (client_sock, client_id):
	# Send client ID to server
	client_sock.sendall(str(client_id).encode())

	numbers = []
	for num in numbers:
		client_sock.sendall(str(num).encode())

	client_sock.sendall(b"Foram enviados todos os numeros")

	nrescolhido = client_sock.recv(1024).decode()

	print(f"Numbers sent: {numbers}")
	print(f"Chosen number: {nrescolhido}")

	if int(nrescolhido) == numbers[0]:
		print("O numero escolhido foi o primeiro numero")
	elif int(nrescolhido) == numbers[-1]:
		print("O numero escolhido foi o ultimo numero")
	elif int(nrescolhido) == min(numbers):
		print("O numero escolhido foi o minimo")
	elif int(nrescolhido) == max(numbers):
		print("O numero escolhido foi o maximo")
	elif len(numbers) % 2 != 0 and int(nrescolhido) == sorted(numbers)[len(numbers)//2]:
		print("O numero escolhido foi @ mediana")

def valid_address(address):
    try:
        ipaddress.IPv4Address(address)
        return True
    except ipaddress.AddressValueError:
        return False

def bad_usage():
    print("Usage: python {} <client_id> <port> [<ipv4_address>]".format(sys.argv[0]))
    print("")
    print("Arguments:")
    print("  <client_id>      The ID of the client.")
    print("  <port>           The port number to use for the connection.")
    print("")
    print("Optional arguments:")
    print("  <ipv4_address>   The IPv4 address of the client.")
    print("                   If not specified, the client will connect to localhost.")
    sys.exit(2)

def main():
	# validate the number of arguments and eventually print error message and exit with error
	if len(sys.argv) < 3 or len(sys.argv) > 4:
		bad_usage()
		
	# verify type of of arguments and eventually print error message and exit with error
	client_id = sys.argv[1]
	
	# obtain the port number
	if (sys.argv[2].isnumeric()) and (1024 <= int(sys.argv[2]) <= 65535):
		port = int(sys.argv[2])
	else:
		print(text.YELLOW + "Error: The provided port argument is not valid.\n" + text.END)
		bad_usage()

	# obtain the hostname that can be the localhost or another host
	if len(sys.argv) == 4 and valid_address(sys.argv[3]):
		hostname = sys.argv[3]
	elif len(sys.argv) == 4 and not valid_address(sys.argv[3]):
		print(text.YELLOW + "Error: The provided ipv4_address argument is not valid.\n" + text.END)
		bad_usage()
	else:
		hostname = "127.0.0.1" # aka. localhost

	client_socket = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
	client_socket.bind(("0.0.0.0", 0))
	client_socket.connect ((hostname, port))

	run_client (client_socket, sys.argv[1])

	client_socket.close ()
	sys.exit(0)

if __name__ == "__main__":
    main()