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

def gen_powerline(
	content, background="white", color="black", left="", right=""
):
	"""
	Generates a powerline style string
	"""
	return (
		f'<span color="{background}">{left}</span>'
		+ f'<span background="{background}" color="{color}"> {content} </span>'
		+ f'<span color="{background}">{right}</span>'
	)

def akamodoro_sendcmd(cmd):
	sock = socket.socket(socket.AF_UNIX)

	sock.connect(SOCKET_PATH)
	sock.sendall(f"{cmd}\n".encode())

	return sock.recv(1024).decode("utf-8").strip()


def run_applet(x, y):
	window_size = (368, 324)
	layout = [
		[TITLE],
		[sg.Button("Re-START", key="start", **BTN)],
		[
			sg.Button("Short Brk", key="short_brk", **BTN),
			sg.Button("Long Brk", key="long_brk", **BTN)
		],
		[sg.Button("Next", key="next", **BTN)],
		[
			sg.Button("Stop", key="stop", **BTN),
			sg.Button("Resume", key="resume", **BTN)
		]
	]

	window = sg.Window(
		'AKAMODORO - applet',
		layout,
		font=("JetBrainsMonoNL Nerd Font Mono", 10),
		finalize=True,
		location=(x - (window_size[0] // 2), y + 30)
	)
	event, values = window.read()

	window.close()
	if event != "resume":
		akamodoro_sendcmd(event)


def main():
	argv = sys.argv
	if len(argv) <= 1:
		print("please add cmd")
		return

	print(akamodoro_sendcmd(argv[1]))

	if len(argv) == 4:
		run_applet(int(argv[2]), int(argv[3]))

if __name__ == '__main__':
    main()