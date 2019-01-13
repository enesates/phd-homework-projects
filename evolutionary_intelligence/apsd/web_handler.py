from urlparse import parse_qs
import uuid
import json

from app import Controller
from client_state import ClientState

# url: http://yzgrafik.ege.edu.tr/wh
# need action parameter

clients = dict()


def application(environment, start_response):
    """
    web application
    """

    status = '200 OK'
    responseHeaders = [('Content-type', 'application/json')]
    variables = parse_qs(environment['QUERY_STRING'])
    action = ""

    if variables.get('action') is not None:
        action = variables.get('action')[0]

        if action == 'init':
            start_response(status, responseHeaders)
            return init(variables)

        elif action == 'priority':
            start_response(status, responseHeaders)
            return priority(variables)
        
        elif action == "exit":
            start_response(status, responseHeaders)
            return exit_clean(variables)

    else:
        responseHeaders = [('Content-type', 'text/html')]

        start_response(status, responseHeaders)
        return "<html><body><h1>Usage Error!</h1><p>%s</p></body></html>" % variables


def init(variables):
    # generate uuid
    clientId = uuid.uuid4()
    controller = Controller()

    # read init parameters
    location = variables.get("location")[0]
    zoom = int(variables.get("zoom")[0])
    clusterCnt = int(variables.get("clusterCnt")[0])
    radius = int(variables.get("radius")[0])

    # create a state for the client and store important information
    clientState = ClientState(clientId, clusterCnt, radius)
    clientState.controller = controller

    clientState.controller.init_params(radius=radius)

    # load the image from google static maps
    clientState.controller.search_location(location, zoom)

    # execute the clustering using parameters
    clientState.controller.run_kmeans(clusterCnt)

    # generate JSON for the results
    cellsJs = []
    for grid in clientState.controller.sa.grids:
        cellsJs.append({"cellId": grid.gridId, "clusterId": int(grid.clusterNum)})
        clientState.clusters.append(grid.clusterNum)

    outputJs = [{"clientId": str(clientId), "cells": cellsJs}]

    output = json.dumps({"clustering": outputJs})

    # save the client state to the dictionary
    clients[str(clientId)] = clientState

    # return the JSON with clientId
    return "callback(%s)" %output


def priority(variables):

    clusterPrio = variables.get("clusterPrio")[0].split(",")
    sensorCnt = int(variables.get("sensorCnt")[0])
    clientId = variables.get("clientId")[0]
    
    clientState = clients.get(clientId)

    for i, j in enumerate(clusterPrio):
        clientState.controller.set_priority(i, int(j))

    clientState.controller.deploy_simulated_annealing(sensorCnt)

    sensorsJs = []
    for s in clientState.controller.sa.sensors:
        sensorsJs.append({"sensorId": s.sensorId, "priority": s.priority, "coordinates": [{"x": s.xPos, "y": s.yPos}]})

    outputJs = [{"sensors": sensorsJs}]

    output = json.dumps({"deployment": outputJs})

    return "callback(%s)" %output


def exit_clean(variables):
    global clients
    clientId = variables.get("clientId")[0]

    if clientId is None or clientId == "":
        clients = dict()
    else:
        del clients[clientId]
