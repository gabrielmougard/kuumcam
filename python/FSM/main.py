import camConfig # class for reading config
import networkHealth # check network health

def waitForConfig(config):
    





# Check for existing config
conf = camConfig.Config().read() # if device has never been connected, return None. Else, return a JSON object with the params in it

if (conf is not None): #existing configuration
    beginStreamingService(conf)

else: #the device has never been connected to the platform
    waitForConfig(conf) # mutator of config in the case where we managed to create a connection 
    if (conf is not None):
        beginStreamingService(conf)
    

