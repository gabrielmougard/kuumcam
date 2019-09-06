import camConfig # class for reading config
import networkHealth # check network health
import keyboardUtil # launch fifo queue of the keyboard

import threading
import time
import queue

def waitForConfig(config):









q = queue.Queue()
threads = []
num_of_threads = 2

# Check for existing config
conf = camConfig.Config().read() # if device has never been connected, return None. Else, return a JSON object with the params in it
k = keyboardUtil.KeyboardListenerDaemon(camConfig.QUEUE_PATH)
k.setup_fifo() #setup the queue pipeline
f = FifoReaderDaemon(camConfig.QUEUE_PATH) #setup the reader







if (conf is not None): #existing configuration
    beginStreamingService(conf)

else: #the device has never been connected to the platform
    waitForConfig(conf) # mutator of config in the case where we managed to create a connection 
    if (conf is not None):
        beginStreamingService(conf)
    

