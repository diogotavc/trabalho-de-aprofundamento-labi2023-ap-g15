#!/usr/bin/python3

import os
import sys
import socket
import json
import base64
import ipaddress
import time
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

# Lista com os números
numbers = []

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
	# Create a cipher object using the AES algorithm and ECB mode
	cipher = AES.new(cipherkey, AES.MODE_ECB)

	# Convert the data to a string with 16 digits and encode it as UTF-8
	data_string = "%16d" % (data)
	data_bytes = bytes(data_string, "utf-8")

	# Encrypt the data using the cipher object
	encrypted_data_bytes = cipher.encrypt(data_bytes)

	# Encode the encrypted data as base64 and convert it to a string
	encrypted_data_str = str(base64.b64encode(encrypted_data_bytes), "utf-8")

	# Return the encrypted data as a string
	return encrypted_data_str


# Function to decript values received in json format
# return int data decrypted from a 16 bytes binary strings coded in base64
def decrypt_intvalue(cipherkey, data):
	# Create a cipher object using the AES algorithm and ECB mode
	cipher = AES.new(cipherkey, AES.MODE_ECB)

	# Decode the base64-encoded data
	data_bytes = base64.b64decode(data)

	# Decrypt the data using the cipher object
	decrypted_data_bytes = cipher.decrypt(data_bytes)

	# Convert the decrypted data to an integer
	decrypted_data_int = int(decrypted_data_bytes.decode("utf-8"))

	# Return the decrypted data as an integer
	return decrypted_data_int


# Function to generate a hash from a list of numbers
def generate_hash(numbers):
	string = str(numbers)
	hash_object = SHA256.new(data=string.encode('utf-8'))
	hash_value = hash_object.hexdigest()
	return hash_value

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
def start_action(client_sock, client_id, cipher):
	if cipher is None:
		request = { "op": "START", "client_id": client_id }
	else:
		cipher = str(base64.b64encode(cipher), "utf-8")
		request = { "op": "START", "client_id": client_id, "cipher": cipher }
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
def number_action(client_sock, number, cipher):
	numbers.append(number)
	print(log_levels.DEBUG, numbers)
	if cipher is not None:
		number = encrypt_intvalue(cipher, number)
	request = { "op": "NUMBER", "number": number}
	response = sendrecv_dict(client_sock, request)
	validate_response(client_sock, response)


# process STOP operation
def stop_action(client_sock, cipher):
	print("Do you want to send a SHA256 hash to the server? Valid options:\n(Y)es to confirm.")
	user_input = input("Input: ").lower()
	if user_input == "y" or user_input == "yes":
		shasum = generate_hash(numbers)
		print(log_levels.DEBUG, shasum)
		request = { "op": "STOP", "shasum": shasum}
	else:
		print(log_levels.WARN, "In case of a list mismatch, this client won't be notified.")
		request = { "op": "STOP" }
	response = sendrecv_dict(client_sock, request)
	validate_response(client_sock, response)
	value = response["value"]
	if cipher is not None:
		value = decrypt_intvalue(cipher, value)
	print(f"The chosen number is: {value}")
	guess_action(client_sock)


# process GUESS operation
def guess_action(client_sock):
	while True:
		print("Valid options: Min, Max, First, Last, Median, or (Q)uit.")
		choice = input("Guess: ").lower()
		if choice in ['min', 'max', 'first', 'last', 'median']:
			break
		elif choice in ['q', 'quit']:
			print("Are you sure you want to quit? Valid options:\n(Y)es to confirm.")
			user_input = input("Input: ").lower()
			if user_input == "yes" or user_input == "y":
				choice = ""
				break
		else:
			print(log_levels.WARN, "Invalid input.")
			continue

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
def run_client(client_sock, client_id, cipher=None):
	last_action_time = 0
	start_action(client_sock, client_id, cipher)
	print(log_levels.INFO, "Registering client.")
	time.sleep(0.25)	# This is to prevent a hash mismatch due to fast inputs

	while True:
		print("What do you want to do? Valid options:\n(Q)uit, (S)top, (G)uess, or a number.")
		user_input = input("Input: ").lower()
		current_time = time.monotonic()
		if current_time - last_action_time < 0.25:
			print(log_levels.WARN, "Too many fast inputs. Server may not be able to process all requests in time.")	# This is to prevent a hash mismatch due to fast inputs
			last_action_time = current_time
		else:
			last_action_time = current_time
			if user_input.isnumeric():
				number_action(client_sock, int(user_input),cipher)
			elif user_input == "stop" or user_input == "s":
				stop_action(client_sock, cipher)
			elif user_input == "guess" or user_input == "g":
				stop_action(client_sock, cipher)
			elif user_input == "quit" or user_input == "q" or user_input == "":
				print("Are you sure you want to quit? Valid options:\n(Y)es to confirm.")
				user_input = input("Input: ").lower()
				if user_input == "yes" or user_input == "y":
					quit_action(client_sock)
			else:
				print(log_levels.WARN, "Unknown operation.")


def main():
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
	
	# Ask whether the connection should be secure or not
	print("Do you want to enable encription? Valid options:\n(Y)es to confirm.")
	
	enable_cipher = input("Input: ").lower()
	if enable_cipher == "y" or enable_cipher == "yes":
		cipher = os.urandom(16)
		run_client(client_socket, client_id, cipher)
	else:
		print(log_levels.WARN, "The connection is now insecure.")
		run_client(client_socket, client_id)

	client_socket.close()
	sys.exit(0)


if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		print("\n" + log_levels.INFO, "Exiting..")
		sys.exit(0)