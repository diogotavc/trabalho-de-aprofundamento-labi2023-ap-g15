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


# Dicionário com a informação relativa aos clientes
users = {}

# return the client_id of a socket or None


def find_client_id(client_sock):
	for client_id in users:
		if users[client_id]["sock"] == client_sock:
			return client_id
	return None


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
def generate_hash(client_id):
	numbers = users[client_id]['numbers']
	
	string = str(numbers)
	hash_object = SHA256.new(data=string.encode('utf-8'))
	hash_value = hash_object.hexdigest()
	return hash_value


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
		response = quit_client(client_sock)
	elif op == "NUMBER":
		response = number_client(client_sock, request)
	elif op == "STOP":
		response = stop_client(client_sock, request)
	elif op == "GUESS":
		response = guess_client(client_sock, request)

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

	if "cipher" in request:
		cipher = base64.b64decode(request["cipher"])
	else:
		cipher = None

	if find_client_id(client_sock) is not None or client_id in users:
		print(log_levels.WARN, f"Another user with the client_id {client_id} tried to connect, but failed.")
		return { "op": "START", "status": False, "error": "User is already registered."}
	else:
		users[client_id] = { "sock": client_sock, "cipher": cipher, "numbers": [] }
		print(log_levels.INFO, f"User {client_id} has successfully connected.")
		print(log_levels.DEBUG, users[client_id])
		return { "op": "START", "status": True }


#
# Suporte da eliminação de um cliente - já está implementada
#
# obtain the client_id from his socket and delete from the dictionary
def clean_client(client_sock):
	client_id = find_client_id(client_sock)
	if client_id != None:
		print(log_levels.INFO, f"Client {client_id} is no longer connected.")
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
	client_id = find_client_id(client_sock)
	numbers = users[client_id]['numbers']
	if client_id is None:
		return { "op": "QUIT", "status": False, "error": "Client is not registered."}
	else:
		print(log_levels.INFO, "Updating the report file.")
		update_file(client_id, len(numbers), [])
		clean_client(client_sock)
		return { "op": "QUIT", "status": True}


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
def update_file(client_id, size=0, guess=[]):
	with open("result.csv", "a") as csvfile:
		write = csv.writer(csvfile, delimiter=',')
		write.writerow([client_id, size, guess])


#
# Suporte do processamento do número de um cliente - operação NUMBER
#
# obtain the client_id from his socket
# verify the appropriate conditions for executing this operation
# return response message with or without error message
def number_client(client_sock, request):
	client_id = find_client_id(client_sock)
	cipher = users[client_id]["cipher"]
	numbers = users[client_id]['numbers']
	number = request["number"]
	if client_id is None:
		return { "op": "NUMBER", "status": False, "error": "Client is not registered."}
	
	if cipher is not None:
		number = decrypt_intvalue(cipher, number)

	numbers.append(number)
	return { "op": "NUMBER", "status": True }


#
# Suporte do pedido de terminação de um cliente - operação STOP
#
# obtain the client_id from his socket
# verify the appropriate conditions for executing this operation
# randomly generate a value to return using the function generate_result
# process the report file with the result
# return response message with result or error message
def stop_client(client_sock, request):
	client_id = find_client_id(client_sock)
	numbers = users[client_id]['numbers']
	cipher = users[client_id]["cipher"]
	
	if len(numbers) == 0:
		print(log_levels.WARN, f"The client {client_id} requested to stop, but failed.")
		return { "op": "STOP", "status": False, "error": "This client hasn't sent any numbers yet."}

	users[client_id]['generated_result'] = generate_result(numbers)
	result = users[client_id]['generated_result']
	value = result[0]

	if client_id is None:
		return { "op": "STOP", "status": False, "error": "Client is not registered."}
	
	if "shasum" in request:
		shasum = generate_hash(client_id)
		print(log_levels.DEBUG, shasum)
		if request["shasum"] != shasum:
			print(log_levels.WARN, "The hashes don't match.")
			return { "op": "STOP", "status": False, "error": "The hashes don't match."}
		else:
			print(log_levels.DEBUG, "The hashes match correctly.")
	else:
		print(log_levels.DEBUG, f"The user {client_id} decided not to send a hash, skipping.")
		
	print(log_levels.INFO, "Updating the report file.")
	update_file(client_id, len(numbers), result[1])
	print(log_levels.DEBUG, users[client_id])
	if cipher is not None:
		value = encrypt_intvalue(cipher, value)
	return { "op": "STOP", "status": True, "value": value }



#
# Suporte da adivinha de um cliente - operação GUESS
#
# obtain the client_id from his socket
# verify the appropriate conditions for executing this operation
# eliminate client from dictionary
# return response message with result or error message
def guess_client(client_sock, request):
	client_id = find_client_id(client_sock)
	user_guess = request['choice']
	guess = users[client_id]['generated_result'][1]
	if client_id is None:
		return { "op": "GUESS", "status": False, "error": "Client is not registered."}
	else:
		if user_guess in guess:
			return { "op": "GUESS", "status": True, "result": True }
		else:
			return { "op": "GUESS", "status": True, "result": False }


def main():
	# validate the number of arguments and eventually print error message and exit with error
	# verify type of of arguments and eventually print error message and exit with error
	if len(sys.argv) < 2:
		print(log_levels.ERROR, "No arguments provided.\n")
		usage()
	elif len(sys.argv) > 2:
		print(log_levels.ERROR, "Too many arguments provided.\n")

	# obtain the port number
	if (sys.argv[1].isnumeric()) and (1024 <= int(sys.argv[1]) <= 65535):
		port = int(sys.argv[1])
	else:
		print(log_levels.ERROR, "The provided port argument is not valid.\n")
		usage()

	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		server_socket.bind(("127.0.0.1", port))
	except:
		print(log_levels.ERROR, "Address is already in use.")
		print(log_levels.INFO, "Exiting..")
		sys.exit(3)

	print(log_levels.INFO, f"Successfully started, and listening on port {port}.")
	server_socket.listen()

	clients = []
	print(log_levels.INFO, "Creating the report file.")
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
	try:
		main()
	except KeyboardInterrupt:
		print("\n" + log_levels.INFO, "Exiting..")
		sys.exit(0)