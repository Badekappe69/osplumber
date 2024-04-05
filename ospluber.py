#!/usr/bin/python3

import os
import sys

def main():
    if os.geteuid() != 0:
        exit("You need to have root privileges to run this script.\nPlease try again, this time using 'sudo'. Exiting.")

    if sys.argv[1] == "update":
        update()
    elif sys.argv[1] == "init":
        init(sys.argv[2])
    elif sys.argv[1] == "mkpipeline":
        make_pipeline(sys.argv[1])

def update():
    print("Downloading Modules")

def init(path:str):
    pass

def make_pipeline(path:str):
    pass

if __name__ == "__main__":
    main()
