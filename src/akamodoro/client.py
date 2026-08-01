#!/usr/bin/python

import PySimpleGUI as sg
import socket
import os
import sys

SOCKET_PATH = os.environ["XDG_RUNTIME_DIR"] + "/akamodoro.sock"
TITLE = sg.Text(
	"AKAMDORO",
	font=("JetBrainsMonoNL Nerd Font Mono", 45),
)
BTN = {
	"font" : ("JetBrainsMonoNL Nerd Font Mono", 20),
	"expand_x" : True,
}

def run_applet():
	layout = [
		[TITLE],
		[sg.Button("Re-START", **BTN)],
		[
			sg.Button("Short Brk", **BTN),
			sg.Button("Long Brk", **BTN)
		],
		[sg.Button("Work", **BTN)],
		[
			sg.Button("Stop", **BTN),
			sg.Button("Resume", **BTN)
		]
	]

	mouse_pos = sg.Window.mouse_location()

	window = sg.Window(
		'AKAMODORO - applet',
		layout,
		font=("JetBrainsMonoNL Nerd Font Mono", 10),
		location=(mouse_pos[0] - 100, mouse_pos[1] + 30)
	)
	event, values = window.read()
	window.close()
	
	print(event)
	print(values)

def main():
	argv = sys.argv
	if len(argv) <= 1:
		print("please add cmd")
		return
	# run_applet()

	sock = socket.socket(socket.AF_UNIX)
	sock.connect(SOCKET_PATH)
	sock.sendall(f"{argv[1]}\n".encode())
	print(sock.recv(1024).decode("utf-8").strip())

if __name__ == '__main__':
    main()