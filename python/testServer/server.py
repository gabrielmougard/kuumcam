from flask import Flask
from flask import request 
from flask import jsonify
from flask import Response

import random 
import queue
import time 
import uuid 

IPDATA_API_KEY = "726f1a11992e5894aa77aa2cd300d24444e9cad58ec347d511e64370" #for geolocalisation purpose (free plan => 1500 API call/month)
global message_q 
message_q = dict() #store the code with the timestamp

app = Flask(__name__)
 
@app.route('/', methods=['GET']) #in the web browser
def generate_code():
    visitorIP = jsonify({'ip':request.remote_addr})
    IPDATA_ENDPOINT ="https://api.ipdata.co/"+visitorIP+"?api-key="+IPDATA_API_KEY
    rawGeoData = requests.get(IPDATA_ENDPOINT).content
    filteredGeoData = [rawGeoData["city"],rawGeoData["region"],rawGeoData["country_name"],rawGeoData["latitude"],rawGeoData["longitude"],rawGeoData["postal"]]

    code = ""
    codeLength = 6
    for i in range(codeLength):
        code += random.randint(0,9)

    message_q[code] = [time.time(),filteredGeoData]
    #Save the generated code in a queue with the timestamp
    #Expire in 1 min after generation.
    return code

@app.route('/bind',methods=['GET']) #called by the endpoint
def binding():
    '''
    if everything is right, return UUID and notify the backend
    that a new route must be created paired with this UUID.
    Else, just return error message.
    '''
    #recover the request
    data = request.get_json()
    sendedCode = data['code']
    endpointGeoData = data['geo'] #json containing the same structure as in `generate_code` function.

    if sendedCode in message_q.keys():
        if time.time() - message_q[sendedCode] < 60:
            # check geocalisation data
            if checkGeoData(message_q[sendedCode][1],endpointGeoData):
                
                data = {'authorized':True,'UUID': generateUUID()}
                js = json.dumps(data)
                resp = Response(js,status=200,mimetype='application/json')
                return resp

            return "wrong geolocalisation !"

        else:
            #expired
            return "code expired !"

        del message_q[sendedCode] #delete this element
    else:
        # not the good code
        print("code not validated !")


def checkGeoData(webclientData,endpointData):
    """
    both parameters are list of the same structure
    [0] -> city
    [1] -> region
    [2] -> country_name
    [3] -> latitude
    [4] -> longitude
    [5] -> postal
    """
    if abs(webclientData[3]-endpointData[3]) <= 1e-3 and abs(webclientData[4]-endpointData[4]) <= 1e-3:
        return True
    return False

def generateUUID():
    '''
    make a UUID based on the host ID and current time
    '''
    return uuid.uuid1()
