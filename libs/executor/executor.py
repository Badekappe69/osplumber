def execute(configuration:list, location:str):
    print("Not implemented yet.")
    exit()
    #
    index = 0
    for module_name in configuration:
        print("Starting module: " + list(module_name)[0])
        try:
            tmp_code = open(location + "modules/" + str(list(module_name)[0]) + "/mod.py", "r")
        except:
            print("Could not read mod.py.\n"
                "Path: " + location + "modules/" + str(list(module_name)[0]) + "/mod.py\n" +
                "It is not readable or missing.")
        insert = dict()
        insert["configuration"] = configuration[index][list(module_name)[0]]
        try:
            exec(tmp_code.read(), insert, dict())
        except:
            print("Could not parse mod.py.\n" + 
                "Path: " + location + "modules/" + str(list(module_name)[0]) + "/mod.py\n" + 
                "It is not valid Python code.")
        index=index+1
        print("Finished module: " + list(module_name)[0])

