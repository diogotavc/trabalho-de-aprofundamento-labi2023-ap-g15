#!/usr/bin/python3

import os
import sys
import socket
import json
import base64
from common_comm import send_dict, recv_dict, sendrecv_dict

from Cryptodome.Cipher import AES
from Cryptodome.Hash import SHA256

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
	

def main():
	# validate the number of arguments and eventually print error message and exit with error
	if len(sys.argv) < 2 or len(sys.argv) > 4:
		print("Usage: python client.py <client_id> <port>")
		sys.exit(1)
		
	# verify type of of arguments and eventually print error message and exit with error
	client_id = sys.argv[1]
	
	# obtain the port number
	if (sys.argv[2].isnumeric()):
		port = int(sys.argv[2])
	else:
		print("Error: The provided port argument is not valid.")
		sys.exit(2)

	# obtain the hostname that can be the localhost or another host
	if len(sys.argv) == 4:
		hostname = sys.argv[3]
	else:
		hostname = "localhost"

	client_socket = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
	client_socket.bind(("0.0.0.0", 0))
	client_socket.connect ((hostname, port))

	run_client (client_socket, sys.argv[1])

	client_socket.close ()
	sys.exit(0)

if __name__ == "__main__":
    main()
