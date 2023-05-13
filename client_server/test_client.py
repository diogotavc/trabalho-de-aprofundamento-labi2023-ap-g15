from subprocess import Popen, PIPE

def run_client(args=""):
	# Argument parser for client.py
	proc = Popen(f"python client.py {args}", stdout=PIPE, shell=True)
	for line in iter(proc.stdout.readline, b''):
		# Return the first line of the output
		return line.decode("utf-8").rstrip()

def test_client_invalid_arguments():
	# Test that the client prints the correct usage message when invalid arguments are given
	assert "\x1b[91m[ERROR]\x1b[0m Wrong usage." in run_client("")
	assert "\x1b[91m[ERROR]\x1b[0m Wrong usage." in run_client("user")
	assert "\x1b[91m[ERROR]\x1b[0m Wrong usage." in run_client("user arg1 arg2 arg3")

def test_client_invalid_port():
	# Test that the client prints the correct usage message when an invalid port is given
	assert "\x1b[91m[ERROR]\x1b[0m The provided port argument is not valid." in run_client("user invalid_port")
	assert "\x1b[91m[ERROR]\x1b[0m The provided port argument is not valid." in run_client("user -1")
	assert "\x1b[91m[ERROR]\x1b[0m The provided port argument is not valid." in run_client("user 65536")
	assert "\x1b[91m[ERROR]\x1b[0m The provided port argument is not valid." in run_client("user 1023")
	assert "\x1b[91m[ERROR]\x1b[0m The provided port argument is not valid." in run_client("user 0")

def test_client_invalid_address():
	# Test that the client prints the correct usage message when an invalid address or ip or port is given
	assert "\x1b[91m[ERROR]\x1b[0m The provided ipv4_address argument is not valid." in run_client("user 1234 invalid_address")
	assert "\x1b[91m[ERROR]\x1b[0m The provided ipv4_address argument is not valid." in run_client("user 1234 192.168..1")
	assert "\x1b[91m[ERROR]\x1b[0m The provided ipv4_address argument is not valid." in run_client("user 1234 450.168.xa.1")
	assert "\x1b[91m[ERROR]\x1b[0m The provided ipv4_address argument is not valid." in run_client("user 1234 192.168.1.256")
	assert "\x1b[91m[ERROR]\x1b[0m The provided ipv4_address argument is not valid." in run_client("user 1234 -somehostname")
	assert "\x1b[91m[ERROR]\x1b[0m The provided ipv4_address argument is not valid." in run_client("user 1234 !somehostname")
	assert "\x1b[91m[ERROR]\x1b[0m The provided ipv4_address argument is not valid." in run_client("user 1234 somerandom.com")
	assert "\x1b[91m[ERROR]\x1b[0m The provided ipv4_address argument is not valid." in run_client("user 1234 maomv.rocks")

def test_client_valid_input():
	# Test that the client sends the correct input and receives the expected output
	assert "\x1b[92m[INFO]\x1b[0m Attempting to connect to 127.0.0.1 at port 1234." in run_client("user 1234 127.0.0.1")
	assert "\x1b[92m[INFO]\x1b[0m Attempting to connect to 127.0.0.1 at port 1234." in run_client("user 1234 localhost")
	assert "\x1b[92m[INFO]\x1b[0m Attempting to connect to 127.0.0.1 at port 1234." in run_client("user 1234 127.0.0.1")
	assert "\x1b[92m[INFO]\x1b[0m Attempting to connect to 127.0.0.1 at port 1234." in run_client("user 1234 localhost")
