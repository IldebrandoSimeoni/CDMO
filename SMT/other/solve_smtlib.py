from argparse import ArgumentParser
from pathlib import Path
import glob
from smt_utils import VLSI_Instance
import logging
import os
import multiprocessing
import time
import math
import numpy as np
import json
import os
import subprocess

def start_solving(instance : Path, solver, timeout):
    # Read json file
    inst_info = {}
    with open(instance, "r") as f:
        inst_info = json.load(f)

    smt_file = instance[:instance.rfind(".")] + ".smt2"
    cmd = f"SMT/smt_opt.sh {smt_file} {inst_info['obj_var']} {inst_info['initial_bound']} {solver} min"
    print("-"*20)
    print("Solving " + instance)
    start = time.time()
    result = subprocess.run(cmd, stdout=subprocess.PIPE, cwd=os.getcwd(), shell=True, universal_newlines=True, text=True,timeout=timeout)
    print(result.stdout)
    print(f"Time elapsed:{time.time()-start}")

if __name__ == "__main__":
    parser = ArgumentParser(description='Solve one or more VLSI instances')

    parser.add_argument("instance", nargs=1, type=Path, help="Path to the instance or instance folder")
    parser.add_argument("-t", "--timeout", nargs=1, default=300, type=int, help="How many seconds to wait before timeout for each instance")
    parser.add_argument("-f", "--folder", action="store_true", help="If passed the input data will be considered a folder containing multiple instances")
    parser.add_argument("solver", choices=["z3","cvc4","cvc5"])
    args = vars(parser.parse_args())
    simplify_list = lambda x : x[0] if isinstance(x, list) else x
    args = {k:simplify_list(args[k]) for k in args}

    # Get all instances in the folder
    if args["folder"]:
        #os.chdir(args["instance"])
        for file in glob.glob(str(args["instance"]/"*.json")):
            try:
                start_solving(file, args["solver"], args["timeout"])
            except Exception as e:
                logging.error(f"File:{file} is malformed\n" + str(e))
    else:
        try:
            start_solving(args["instance"], args["solver"], args["timeout"])
        except Exception as e:
            logging.error(f"File:{args['instance']} is malformed\n" + str(e))
        
