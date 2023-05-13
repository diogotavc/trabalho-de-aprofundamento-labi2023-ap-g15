from subprocess import Popen, PIPE
import subprocess
import signal
import os

def run_server(args=""):
	# Argument parser for server.py
	proc = Popen(f"python server.py {args}", stdout=PIPE, shell=True)
	for line in iter(proc.stdout.readline, b''):
		# Return the first line of the output
		return line.decode("utf-8").rstrip()

def test_server_invalid_arguments():
	# Test that the server prints the correct usage message when invalid arguments are given
	assert "\x1b[91m[ERROR]\x1b[0m Wrong usage." in run_server("")
	assert "\x1b[91m[ERROR]\x1b[0m Wrong usage." in run_server("user invalid_port")
	assert "\x1b[91m[ERROR]\x1b[0m Wrong usage." in run_server("arg1 arg2 arg3")

def test_server_invalid_port():
	# Test that the server prints the correct usage message when an invalid port is given
	assert "\x1b[91m[ERROR]\x1b[0m The provided port argument is not valid." in run_server("user")
	assert "\x1b[91m[ERROR]\x1b[0m The provided port argument is not valid." in run_server("-1")
	assert "\x1b[91m[ERROR]\x1b[0m The provided port argument is not valid." in run_server("65536")
	assert "\x1b[91m[ERROR]\x1b[0m The provided port argument is not valid." in run_server("1023")
	assert "\x1b[91m[ERROR]\x1b[0m The provided port argument is not valid." in run_server("0")

def test_run_server():
	# Runs the server when testing and returns the process
	global test_server
	test_server = subprocess.Popen(["python3","server.py","1024"], stdin=None, stdout=PIPE, stderr=None, shell=False)

def test_shutdown_server():
	# Shuts down the server using its PID
	global test_server
	os.kill(test_server.pid, signal.SIGTERM)