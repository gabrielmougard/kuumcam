import requests
import configparser
import socket
import os 
from subprocess import Popen
"""
`Binder` handle the I/O operations between the endpoint and the platform.
"""
class Binder:
    __init__(self,code=None): #when auto-connection, no need for the code since we have the UUID in `network.conf`
        self.code = code
        self.networkParser = configparser.RawConfigParser().read('config/network.conf')
            
    def bind(self):
        if (self.code is not None): #first connection
            #get the URL root of the platform
            URL_PATH_FIRST_CONN = self.networkParser.get("PLATFORM","FIRST_CONN_ROUTE")
            codeStr = ''
            del code[-1] #delete the VALIDATION character
            codeStr.join(map(str,code)) #now code is string

            r = requests.post(URL_PATH_FIRST_CONN,data= {'code': codeStr})
            response = r.json() # we'll a JSON as a response from the platform

            if (response['authorized']):
                # save the UUID
                uuid = response['UUID']
                self.networkParser.set("PLATFORM","UUID",uuid)
                with open('config/network.conf') as f_out:
                    self.networkParser.write(f_out)

                
                if (isOnline() and isUUID(uuid)):
                    #launch the streaming engine with the right parameters
                    Popen(['python3','../streaming-engine/kuumcamV2.py',uuid]) #just pass uuid as args[0] in order that the program know where to send the stream 
                

            else:
                print("binding failed !")

        else: # `network.conf` has already been setup 
            URL_PATH_CONN = self.networkParser.get("PLATFORM","CONN_ROUTE")

            #by security measure, check the UUID in the file and it's integrity
            uuid = self.networkParser.get("PLATFORM","UUID")
            if (isUUID(uuid)):
                r = requests.post(URL_PATH_CONN,data= {'uuid': uuid})
                response = r.json()

                if (response["authorized"]):
                    #launch the streaming engine with the right parameters
                    Popen(['python3','../streaming-engine/kuumcamV2.py',uuid]) #just pass uuid as args[0] in order that the program know where to send the stream 
                
                else:
                    print("connection not authorized")


    def isOnline():
        """
        check network health
        """
        hostname = self.networkParser.get("HEALTH","REMOTE_SERVER")
        try:
            host = socket.gethostbyname(hostname)
            s = socket.create_connection((host, 80), 2)
            s.close()
            return True
        except:
            pass
        print("connection offline")
        return False

    def isUUID(u):
        """
        check if the shape of `u` is like an UUID (RFC 4122)
        i.e : 12345678-1234-5678-1234-567812345678  ==> 128 bits, 32 digits on 4 bits
        """
        if (len(u) == 36):
            for digits in u.split('-'):
                try:
                    int(digits)
                except ValueError:
                    return False
            return True
        print("wrong uuid")
        return False



