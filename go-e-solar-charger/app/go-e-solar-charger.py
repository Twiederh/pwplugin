""" Gateway to Go-E Wallboxes: Reads power values from pwplugin and sends them to the Go-E Wallbox defined in the GoE environment variable
"""
import logging
import os
import sys
from http import HTTPStatus
from threading import Lock
from typing import Callable
import json
import time

import requests
import urllib3
from fastapi import FastAPI, HTTPException

logger = logging.getLogger("uvicorn.error")

def get_environ(var: str) -> str:
    """ Gets an environment variable and exits the program, if
    the variable doesn't exist.

    Args:
        var (str): Name of the variable.
    Returns:
        str: The value of the variable.
    """
    val = os.environ.get(var)
    if not val:
        logger.error("Environment %s not set.", var)
        sys.exit(-1)

    return val

# GoE = get_environ("GoE")
# pwPlugin = get_environ("pwPlugin")
GoE = "192.168.7.66"
pwPlugin = "192.168.1.120:8081"
intervall = get_environ("Intervall")
#TZ = get_environ("TZ")
TZ = "Europe/Berlin"

TIMEOUT = 10

# app = FastAPI()
logger.info("starting Go-E-Solar-Charger (%s, %s)", GoE, pwPlugin)

# Ignore warnings for not validated access to the PW-API
urllib3.disable_warnings()

def check_http_error(response: requests.Response):
    """Checks if the response of the HTTP server is OK.
    If not, an exception is thrown.

    Args:
        response (requests.Response): The response of the HTTP server.

    Raises:
        HTTPException: Exception, if the response is not OK.
    """
    if response.status_code != HTTPStatus.OK:
        raise HTTPException(
            HTTPStatus.INTERNAL_SERVER_ERROR,
            f"Powerwall returned error ({response.status_code}: {response.json()['error']})")
    
def post_aggregates(ids):
    """ Gets an environment variable and exits the program, if
    the variable doesn't exist.

    Args:
        var (str): Name of the variable.
    Returns:
        str: The value of the variable.
    """
    logger.info("put_ids")
    url = f"http://{GoE}/api/set?ids="+ids
    response = requests.get(
        url=url,
        verify=False,
        timeout=TIMEOUT)
    check_http_error(response)

def get_aggregates() -> dict[str, int]:
    """ Gets the values from pwplugin and calls the routine to send
    them to the Go-E Wallbox

    Args:
        var (str): Name of the variable.
    Returns:
        n/a
    """
    logger.info("get_power")
    url = f"http://{pwPlugin}/aggregates"
    response = requests.get(
        url=url,
        verify=False,
        timeout=TIMEOUT)
    check_http_error(response)
    res = response.json()
    ids = {"pPv": res['solar'], "pGrid": res['site'], "pAkku": res['battery'] }
    ids = json.dumps(ids)
    post_aggregates(ids)
    print(ids)
    

while True:
    get_aggregates()
    time.sleep(intervall)