'''
module for the backend side. simple flask app, responses to GET requests from the front.
currently loads JSON data from local files and sends application/json responses
'''
from flask import Flask, request, jsonify
import os
import json

#from dotenv import load_dotenv
#dotenv_path = os.path.join(os.getcwd(),'server.env')
#load_dotenv(dotenv_path)

HOST = os.getenv('HOST_NAME',None)
PORT = os.getenv('PORT',5000)
DEBUG = os.getenv('RUN_DEBUG',"False") == "True"
ENCODING = os.getenv('ENCODING','utf-16')
BASEDIR = os.getcwd()

app = Flask(__name__)


def import_file(dir:str,filename:str, ext:str):
    global BASEDIR
    global ENCODING
    path1 = os.path.abspath(os.path.join(BASEDIR, dir, filename))
    path2 = os.path.abspath(os.path.join(BASEDIR, dir, filename+ext))
    if os.path.isfile(path1):
        with open(path1, 'r', encoding=ENCODING) as confile:
            imported_data = confile.read()
        return imported_data
    elif os.path.isfile(path2):
        with open(path2, 'r', encoding=ENCODING) as confile:
            imported_data = confile.read()
        return imported_data
    else:
        raise FileNotFoundError


def apply_context_filter(to_resolve:dict, context:dict) -> dict:
        if to_resolve is None:
            return None
        if context is None:
            return to_resolve
        for element in to_resolve:
            assume_OK = True
            for key, value in context.items():
                if element[key] != value:
                    assume_OK = False
                    break
            if assume_OK == True:
                return element


@app.route('/api/ui/<page>', methods = ['GET'])
def get_ui(page:str):
    '''
    this function is called when GET request is done to the server
    so, in return it merely loads needed file (here it is a json string)
    the string is later parsed in the app
    somehow, the load is faster when in is requested then during in-app load
    i can assume this happens as 2 apps are run in separate threads
    as laptop i am running them is 4C/8T
    it may also happen bc of a complicated exception handling i used
    '''
    FILE = json.loads(import_file('page/ui/', page,'.json'))
    CONTEXT = dict(request.args.items())
    if CONTEXT == {}:
        CONTEXT = None
    FILTERED = apply_context_filter(FILE, CONTEXT)
    return (jsonify(FILTERED))


@app.route('/api/content/<page>', methods = ['GET'])
def get_content(page:str):
    FILE = json.loads(import_file('page/content/', page,'.json'))
    CONTEXT = dict(request.args.items())
    if CONTEXT == {}:
        CONTEXT = None
    FILTERED = apply_context_filter(FILE, CONTEXT)
    return (jsonify(FILTERED))


if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=DEBUG)