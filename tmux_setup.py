#!/usr/bin/env python
# coding: utf-8
from os import system
import sys
import argparse


global IP
global PATH

ACTIVATE_VENV = '. path_to_your_virtualenv/bin/activate'
IP = 'none'
PATH = 'none'


def tmux(command):
    system('tmux %s' % command)


def tmux_shell(command):
    tmux('send-keys "%s" "C-m"' % command)

# example: one tab with vim, other tab with two consoles (vertical split)
# with virtualenvs on the project, and a third tab with the server running
'''
# vim in project
tmux('select-window -t 0')
tmux_shell('cd %s' % PROJECT_PATH)
tmux_shell('vim')
tmux('rename-window "vim"')

# console in project
tmux('new-window')
tmux('select-window -t 1')
tmux_shell('cd %s' % PROJECT_PATH)
tmux_shell(ACTIVATE_VENV)
tmux('rename-window "consola"')
# second console as split
tmux('split-window -v')
tmux('select-pane -t 1')
tmux_shell('cd %s' % PROJECT_PATH)
tmux_shell(ACTIVATE_VENV)
tmux('rename-window "consola"')

# local server
tmux('new-window')
tmux('select-window -t 2')
tmux_shell('cd %s' % PROJECT_PATH)
tmux_shell(ACTIVATE_VENV)
tmux_shell('python manage.py runserver')
tmux('rename-window "server"')

# go back to the first window
tmux('select-window -t 0')
'''

def default_scan(port):
	# nmap -Pn -sC IP -oA PATH/tcp_IP
	# nmap -Pn -p- IP -oA PATH/full_IP
	# nmap -Pn -F -sU -oA PATH/udp_IP

	# Window
	tmux('new-window')
	tmux('rename-window "default"')


	# Split
	tmux('split-window -h')
	tmux('split-window -v')
	
	# Scans
	tmux('select-pane -t 0')
	tmux_shell('cd %s' % PATH)
	tmux_shell('clear')
	tmux_shell('nmap -Pn -sC {0} -oA tcp_{0}'.format(IP,IP.replace('.','_')))
	tmux('select-pane -t 1')
	tmux_shell('cd %s' % PATH)
	tmux_shell('clear')
	tmux_shell('nmap -Pn -p- {0} -oA full_{0}'.format(IP,IP.replace('.','_')))
	tmux('select-pane -t 2')
	tmux_shell('cd %s' % PATH)
	tmux_shell('clear')
	tmux_shell('nmap -Pn -F -sU {0} -oA udp_{0}'.format(IP,IP.replace('.','_')))

def port_80(port):
	# panel 0: nmap -Pn -A -p PORT IP -oA PATH/IP_PORT
	# panel 1: nikto -host IP -output PATH/nikto_PORT_IP
	# panel 2: dirb http://IP -o PATH/dirb_PORT_IP
	
	# Window
	tmux('new-window')
	tmux('rename-window "port_80"')

	# Split
	tmux('split-window -h')
	tmux('split-window -v')

	# Scans
	tmux('select-pane -t 0')
	tmux_shell('cd %s' % PATH)
	tmux_shell('clear')
	tmux_shell('nmap -Pn -A -p {0} {1} -oA {1}_{0}'.format(port,IP,IP.replace('.','_')))
	tmux('select-pane -t 1')
	tmux_shell('cd %s' % PATH)
	tmux_shell('clear')
	tmux_shell('nikto -host {1} -output nikto_{0}_{2}.txt'.format(port,IP,IP.replace('.','_')))
	tmux('select-pane -t 2')
	tmux_shell('cd %s' % PATH)
	tmux_shell('clear')
	tmux_shell('dirb http://{1} -o dirb_{0}_{2}'.format(port,IP,IP.replace('.','_')))

def port_443(port):
	# panel 0: nmap -Pn -A -p PORT IP -oA PATH/IP_PORT
	# panel 1: nikto -host IP -output PATH/nikto_PORT_IP
	# panel 2: dirb https://IP -o PATH/dirb_PORT_IP
	# panel 3: nmap -Pn -A -p PORT --script ssl* IP -oA PATH/IP_PORT
	
	# Window
	tmux('new-window')
	tmux('rename-window "port_443"')

	# Split
	tmux('split-window -h')
	tmux('split-window -v')
	tmux('select-pane -t 0')
	tmux('split-window -v')

	# Scans
	tmux('select-pane -t 0')
	tmux_shell('cd %s' % PATH)
	tmux_shell('clear')
	tmux_shell('nmap -Pn -A -p {0} {1} -oA {1}_{0}'.format(port,IP,IP.replace('.','_')))
	tmux('select-pane -t 1')
	tmux_shell('cd %s' % PATH)
	tmux_shell('clear')
	tmux_shell('nikto -host {1}:443 -output nikto_{0}_{2}.txt'.format(port,IP,IP.replace('.','_')))
	tmux('select-pane -t 2')
	tmux_shell('cd %s' % PATH)
	tmux_shell('clear')
	tmux_shell('dirb http://{1} -o dirb_{0}_{2}'.format(port,IP,IP.replace('.','_')))
	tmux('select-pane -t 3')
	tmux_shell('cd %s' % PATH)
	tmux_shell('clear')
	tmux_shell('nmap -Pn -A -p {0} --script ssl* {1} -oA {1}_{0}'.format(port,IP,IP.replace('.','_')))


def main(ports):
	print 'ip: ' + IP
	print 'path: ' + PATH
	print 'port: ' + str(ports)

	if '0' in ports:
		default_scan('0')

	if '80' in ports:
		port_80('80')

	if '443' in ports:
		port_443('443')

if __name__ == '__main__':
	
	parser = argparse.ArgumentParser()
	parser.add_argument('-p',help='Port to analyze (default no specific ports)',nargs='+',default=['0'],required=False)
	requiredNamed = parser.add_argument_group('required arguments')
	requiredNamed.add_argument('-ip',help='Target IP',required=True)
	requiredNamed.add_argument('-path',help='Project path',required=True)
	args = parser.parse_args()

	IP = args.ip
	PATH = args.path
	ports = args.p

	# Session
	tmux('new -A -d -s {}_automatic_scans'.format(IP.replace('.','_')))

	main(ports)

