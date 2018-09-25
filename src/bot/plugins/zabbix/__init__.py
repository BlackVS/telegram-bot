import sys
from tg_helpers import *

commands=dict()

@export
@log
def get_description():
	return "Zabbix module"

@export
@log
def get_commands():
	return []

@export
@log
def get_help(command):
	return ""
