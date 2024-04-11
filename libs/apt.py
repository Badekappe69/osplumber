import utils

def check_tool(name:str, package_name:str) -> None :
    [stdout, stderr] = utils.exec_bash("whereis " + name)
    if len(stderr) != 0:
        raise Exception("Error within bash!")
    
    if str(stdout)[-1] == ":":
        utils.exec_bash("apt-get install -y " + package_name)