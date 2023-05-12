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

# Support for colours and log levels


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


# Usage prompt


def usage():
	print(text.BOLD + f"Usage: python {sys.argv[0]} <client_id> <port> [<ipv4_address>]" + text.END)
	print("")
	print("Arguments:")
	print("  <client_id>      The ID of the client.")
	print("  <port>           The port number to use for the connection.")
	print("")
	print("Optional arguments:")
	print("  <ipv4_address>   The IPv4 address of the client.")
	print("                   If not specified, the client will connect to localhost.")
	sys.exit(2)


# Function to check whether an ipaddress is valid or otherwise

def valid_address(address):
	try:
		ipaddress.IPv4Address(address)
		return True
	except ipaddress.AddressValueError:
		return False

# Function to encript values for sending in json format
# return int data encrypted in a 16 bytes binary string coded in base64


def encrypt_intvalue(cipherkey, data):
	return None


# Function to decript values received in json format
# return int data decrypted from a 16 bytes binary strings coded in base64
def decrypt_intvalue(cipherkey, data):
	return None


# verify if response from server is valid or is an error message and act accordingly - já está implementada
def validate_response(client_sock, response):
	try:
		if not response["status"]:
			print(log_levels.WARN, response["error"])
			client_sock.close()
			sys.exit(3)
	except:
		print(log_levels.FATAL, "Failed to receive package from server.")
		print(log_levels.INFO, "Exiting..")
		client_sock.close()
		sys.exit(3)


# process START operation
def start_action(client_sock, client_id):
	request = { "op": "START", "client_id": client_id}
	response = sendrecv_dict(client_sock, request)
	validate_response(client_sock, response)

# process QUIT operation
def quit_action(client_sock):
	request = { "op": "QUIT"}
	response = sendrecv_dict(client_sock, request)
	validate_response(client_sock, response)
	# Once done, tell the system to exit
	print(log_levels.INFO, "Exiting..")
	client_sock.close()
	sys.exit(0)


# process NUMBER operation
def number_action(client_sock, number):
	request = { "op": "START", "number": number}
	response = sendrecv_dict(client_sock, request)
	validate_response(client_sock, response)


# process STOP operation
def stop_action(client_sock):
	request = { "op": "STOP" }
	response = sendrecv_dict(client_sock, request)
	validate_response(client_sock, response)
	value = response["value"]
	print(f"The chosen number is: {value}")
	guess_action(client_sock)


# process GUESS operation
def guess_action(client_sock):
	print("Valid options: min, max, first, last, median")
	choice = input("Guess: ").lower()
	request = { "op": "GUESS", "choice": choice}
	response = sendrecv_dict(client_sock, request)
	validate_response(client_sock, response)
	# Congratulate the user (or not)
	if response["result"]:
		print("Well done!")
	else:
		print("Better luck next time!")
	# Tell the system to exit
	print(log_levels.INFO, "Exiting..")
	client_sock.close()
	sys.exit(0)


# process UNKNOWN operation
def unknown_action(client_sock):
	request = { "op": "UNKNOWN"}
	response = sendrecv_dict(client_sock, request)
	validate_response(client_sock, response)



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
def run_client(client_sock, client_id):
	start_action(client_sock, client_id)

	while True:
		user_input = input("Input (q)uit, (s)top, (g)uess, or a number: ").lower()

		if user_input.isnumeric():
			number_action(client_sock, int(user_input))
		elif user_input == "stop" or user_input == "s":
			stop_action()
		elif user_input == "guess" or user_input == "g":
			choice = None	# Not yet implemented
			guess_action(client_sock, choice)
		elif user_input == "quit" or user_input == "q" or user_input == "":
			quit_action(client_sock)
		else:
			unknown_action(client_sock)


def main():
	print(log_levels.INFO, f"Starting..")
	# validate the number of arguments and eventually print error message and exit with error
	# verify type of of arguments and eventually print error message and exit with error
	if len(sys.argv) < 3 or len(sys.argv) > 4:
		print(log_levels.ERROR, "No arguments provided.\n")
		usage()
	
	# obtain the client_id
	client_id = sys.argv[1]

	# obtain the port number
	if (sys.argv[2].isnumeric()) and (1024 <= int(sys.argv[2]) <= 65535):
		port = int(sys.argv[2])
	else:
		print(log_levels.ERROR, "The provided port argument is not valid.\n")
		usage()

	# obtain the hostname that can be the localhost or another host
	if len(sys.argv) == 4 and valid_address(sys.argv[3]):
		hostname = sys.argv[3]
	elif len(sys.argv) == 4 and not valid_address(sys.argv[3]):
		print(log_levels.ERROR, "The provided ipv4_address argument is not valid.\n")
		usage()
	else:
		hostname = "127.0.0.1"  # aka. localhost

	print(log_levels.INFO, f"Attempting to connect to {hostname} at port {port}.")
	try:
		client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		client_socket.bind(("0.0.0.0", 0))
		client_socket.settimeout(5)
		client_socket.connect((hostname, port))
	except:
		print(log_levels.ERROR, f"Failed to connect to {hostname} at port {port}.")
		print(log_levels.INFO, "Exiting..")
		sys.exit(1)

	print(log_levels.INFO, f"Successfully connected to {hostname} at port {port}.")

	run_client(client_socket, client_id)

	client_socket.close()
	sys.exit(0)


if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		print("\n" + log_levels.INFO, "Exiting..")
		sys.exit(0)