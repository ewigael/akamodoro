#!/usr/bin/python
import socket
import time
import os
from pathlib import Path
import subprocess
from importlib.resources import files

SOCKET_PATH = os.environ["XDG_RUNTIME_DIR"] + "/akamodoro.sock"
ICON_PATH = files("akamodoro.assets") / "akamodoro_50x60.png"

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

class AkaTimer():
	status_times = {
		"work1": 25 * 60,
		"work2": 25 * 60,
		"short_brk": 5 * 60,
		"long_brk": 15 * 60,
	}
	status_times = {
		"work1": 5,
		"work2": 5,
		"short_brk": 5,
		"long_brk": 5,
	}
	status_inline = {
		"standby": "",
		"work1": "WRK-1",
		"work2": "WRK-2",
		"short_brk": "BRK-1",
		"long_brk": "BRK-2",
	}
	status_name = {
		"standby": "Standing by",
		"work1": "Focus phase",
		"work2": "Focus phase",
		"short_brk": "Short Break",
		"long_brk": "Long Break",
	}
	sequence = [
		"work1",
		"short_brk",
		"work2",
		"long_brk"
	]

	def __init__(self, status = "standby", remaining = 0):
		self.status = status
		self.end_time = time.monotonic() + remaining if status != "standby" else 0

	def set_timer(self, s):
		self.status = s
		self.end_time = time.monotonic() + self.status_times[s]
	
	def start(self):
		self.set_timer(self.sequence[0])
	
	def stop(self):
		self.status = "standby"
		self.end_time = 0
	
	def next(self):
		self.set_timer(self.sequence[(self.sequence.index(self.status) + 2) % len(self.sequence) - 1])
	
	def get_remaining(self):
		return(max(0, int(self.end_time - time.monotonic())))
	
	def get_inline(self, pli=False):
		result = self.status_inline[self.status] if pli else self.status
		if self.status != "standby":
			m, s = divmod(self.get_remaining(), 60)
			result += f" {m:02}:{s:02}"
		return gen_powerline(" ".join(["", result]).strip(), "#c52233", "#360713") if pli else result

	def notify(self, message, title="AKAMDORO"):
		subprocess.run([
			"notify-send",
			"--app-name=akamodoro-daemon",
			f"--icon={ICON_PATH}",
			title,
			message
		])

	def update(self):
		if self.status not in self.sequence:
			return

		if self.get_remaining() == 0:
			current = self.sequence.index(self.status)
			nxt = self.sequence[current + 1] if current + 1 < len(self.sequence) else self.sequence[0]
			self.notify(f"{self.status_name[self.status]} ended!\nStarting {self.status_name[nxt]}")
			self.set_timer(nxt)

def exec_cmd(timer, cmd):
	'''
		possible commands:
			inline
			inlinepli
			status
			work1
			work2
			short_brk
			long_brk
			next
			remaining
			start
			stop
	'''

	result = "OK"
	match cmd:
		case "inline":
			result = timer.get_inline()
		case "status":
			result = timer.status
		case "inlinepli":
			result = timer.get_inline(pli=True)
		case "work1" | "work2" | "short_brk" | "long_brk":
			timer.set_timer(cmd)
		case "start":
			timer.start()
		case "stop":
			timer.stop()
		case "next":
			timer.next()
		case "remaining":
			result = timer.get_remaining()
		case _:
			result = "unknown cmd"
	
	return result

def main():
	timer = AkaTimer()

	# Remove stale socket
	try:
		os.unlink(SOCKET_PATH)
	except FileNotFoundError:
		pass

	sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
	sock.settimeout(1.0)
	sock.bind(SOCKET_PATH)
	sock.listen()

	while True:

		# Receive command
		try:
			# Timeout for connection is 1 second
			conn, _ = sock.accept()

		except socket.timeout:
			# run rest of the program
			timer.update()
			time.sleep(0.5)

		else:
			# Connection established,
			# Interpreting command

			cmd = conn.recv(1024).decode().strip()
			answer = exec_cmd(timer, cmd)

			if answer:
				try:
					conn.sendall(f"{answer}\n".encode("utf-8"))
				except BrokenPipeError:
					pass


if __name__ == "__main__":
	main()