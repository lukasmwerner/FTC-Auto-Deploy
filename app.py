import flask
from flask import Flask
from flask import request
from flask import jsonify
from flask_docs_api.api import Api
import subprocess
import os
import logging

app = Flask(__name__)
api = Api(app, "Github deploy to device")
api.route("/docs")
logging.basicConfig(filename="deploys.log", level=logging.INFO)

data = {}

os.environ['ANDROID_SDK_ROOT'] = "C:\\Users\\lukas\\AppData\\Local\\Android\\Sdk"

workDir = (os.getcwd() + "\\repos\\").replace("\\", "/")


import threading

@app.route("/payload", methods=['POST'])
def payload():
    '''Where Github will do a post request when an event is triggred'''
    jsData = request.get_json()
    trigger = request.headers.get('X-GitHub-Event')
    def deploy():
        if trigger == "push":
            repo = jsData['repository']
            print(jsData)
            data = jsData
            logging.info(f"Using {jsData['pusher']['name']} code for deployment")
            os.chdir(workDir)
            try:
                os.remove(f"{workDir}{repo['name']}")
            except Exception as e:
                pass
            x = subprocess.Popen(f"git clone {repo['clone_url']}", shell=True).wait()
            os.chdir(f"{workDir}{ repo['name'] }")
            if x != 0:
                subprocess.Popen(f"git pull origin", shell=True).wait()
            subprocess.Popen(f"gradlew installDebug", shell=True).wait()
    thread = threading.Thread(target=deploy)
    thread.start()
    return 'Thx!'
    
    

@app.route("/")
def retData():
    '''Returns the last data presented'''
    return jsonify(data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)