import os
import subprocess

def if_not_there_create_folder(name:str):
    if not os.pardir(name):
        os.mkdir(name)

def exec_bash(cmd:str):
    process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
    return process.communicate()