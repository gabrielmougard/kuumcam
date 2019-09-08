import requests
import configparser

import  
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
            URL_PATH = self.networkParser.get("PLATFORM","FIRST_CONN_ROUTE")
            codeStr = ''
            codeStr.join(map(str,code)) #now code is string

            r = requests.post(URL_PATH,data= {'code': codeStr})
            response = r.json() # we'll a JSON as a response from the platform

            if (response['authorized']):
                # save the UUID
                uuid = response['UUID']
                self.networkParser.set("PLATFORM","UUID",uuid)
                with open('config/network.conf') as f_out:
                    self.networkParser.write(f_out)

            else:
                print("binding failed !")

        else: # `network.conf` has already been setup 
            
