import json
import threading
import networkx as nx
from fastapi.responses import JSONResponse
from fastapi import APIRouter, HTTPException
from itertools import chain, count
from networkx.utils import to_tuple
import simpy
from ..controllers.serialiser import serialize_graph

import sys
import os
from pathlib import Path
# Construct the path to the "s" directory
s_directory = os.path.join(Path(__file__).parents[3], "simulator")
# Add the "s" directory to the Python path
sys.path.append(s_directory)
n_directory = os.path.join(Path(__file__).parents[2])
# Add the "s" directory to the Python path
sys.path.append(n_directory)
# from run import get_sim_json
from adapter import *
#
# from adapter import sim_params, run_sim

router = APIRouter(prefix="/network",
                   tags=["network"], responses={404: {"description": "Not found"}})

# env = simpy.Environment()
env = simpy.Environment()
simulation_thread = None
simulation_speed = 1.0

@router.get("/")
async def read_items():
    return "Hello World"

@router.get("/graph")
async def get_graph():
    global simulation_thread, env
    if simulation_thread is not None:
        simulation_thread.join()
        raise HTTPException(
            status_code=400, detail="Simulation already running")
    
    print('init',env)
    res= []
    evaluation = create_sim(env, res=res, start_time=0, finish_time= 4,checkpoints=[1,2],  new_network=True)
    simulation_thread = threading.Thread(target=env.run, args=(([2])))
    simulation_thread.start()
    simulation_thread.join()
    print("res lenght", len(res))
    graph_data = serialize_graph(evaluation.get_network().graph)
    return JSONResponse(content=graph_data)
    
@router.get("/graphDevEnd")
async def stop_graph():
    global simulation_thread, env
    if simulation_thread is None:
        raise HTTPException(status_code=400, detail=f"No simulation running and is alive : {simulation_thread.is_alive()}")
    env.timeout(0)
    simulation_thread.join()
    simulation_thread = None
    env = simpy.Environment()  # create a new environment
    return JSONResponse(content="Simulation stopped", status_code=400)
    
@router.get("/testGraph")
async def get_sim():
    '''The function `get_sim()` starts a simulation thread and returns the results in a serialized graph
    format.
    
    Returns
    -------
        The code is returning a JSON response containing graph data.
    
    '''
    global simulation_thread, env
    res = []
    if simulation_thread is not None:
        simulation_thread.join()
        raise HTTPException(
            status_code=400, detail="Simulation already running")
    
    print('init',env)
    res= []
    # Todo switch to kwargs
    simulation_thread = threading.Thread(target=create_sim_test, kwargs={'env':env,'res':res,'start_time':0,'finish_time':4,'checkpoints':[1,2,3],'new_network':True })
    simulation_thread.start()
    simulation_thread.join()
    simulation_thread = None
    print("res lenght", len(res))
    graph_data =  {index: serialize_graph(data) for index, data in enumerate(res)}
    return JSONResponse(content=graph_data)
