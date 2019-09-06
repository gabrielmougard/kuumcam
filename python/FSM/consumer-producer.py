import threading
import RPi.GPIO as GPIO
import time
import queue
import random
import string


def visualNotification(code,key=None):
    """
    all the LEDs animation for notifying the user according to the specified code
    """
    if (code == "init"):
        #TODO : LEDs animation for keyboard init

    elif (code == "clear"):
        #TODO : LEDs animation for queue/keyboard clearing

    elif (code == "pending"): #need to be executed in a new thread ==> threading.Thread(target=visualNotification,args=("pending")).start() 
        #TODO : LEDs animation for trying to reach the platform once the code is entered  

    else: #meaning it's "key" and that key=sendKey
        #TODO : LEDs animation for key typing


def pollKeys(id,size,in_q):
    code = [] #contain the code to be sent to the platform

    while True:
        if ((len(code) == 7) and code[-1] == VALIDATION): #we have 6 digits and the last character is the validation one.
            platformBinder = platform.Binder(code)

            try:
                newConf = platformBinder.bind() #if the bind is successful, it return a new conf to be saved on the system which will be used for automated connection if the camera if switch off

            except BindingKuumbaError: #https://www.programiz.com/python-programming/user-defined-exception
                #TODO : if an error occur during the binding
                print("Kuumba binding error")
            
            #clean the queue (thread-safe)
            with in_q.mutex:
                in_q.queue.clear()
            print("Queue cleared due to complete validated message")

        else: #retreive char in the queue while checking if it's empty and append the data to the `code` list
            if (not in_q.empty()):
                key = in_q.get()

                if (key == VALIDATION and len(code) < 6): #error : the code must be 6 digits before being validated
                    #TODO : handle this error case
                elif (key == CORRECTION):
                    if (len(code) > 0):
                        del code[-1] #delete the last one
                    
                elif (key == CANCEL):
                    if (len(code) > 0): #if the list is not empty
                        code = [] #empty it
                    
                else: # a digit
                    code.append(key)
        time.sleep(POLL_KEYS_DELAY) #slowing down the process to avoid perf drop


            

def keysProducer(id,out_q):

    #Config keyboard (the hardcoded values with be replaced by a call to a config file)
    GPIO.setMode(GPIO.BCM)
    SCLPin=17
    SDOPin=4

    HALF_BIT_TIME=.001
    CHARACTER_DELAY=5*HALF_BIT_TIME

    NUM_BITS=16

    GPIO.setup(SCLPin,GPIO.OUT)
    GPIO.setup(SDOPin,GPIO.IN)

    GPIO.output(SCLPin,GPIO.HIGH)
    time.sleep(HALF_BIT_TIME)
    oldKey=18
    #
    startTime = time.time() # we want to implement a queue cleaning mechanism when nothing is typed for 10 seconds.
    visualNotification("init") # notify the user with some LEDs animation (initialization message)

    while True:
        key=1
		time.sleep(CHARACTER_DELAY)

        while button < 17:
            sendedKey=key
            if (sendedKey == 17):
                sendedKey = 1
            
            GPIO.output(SCLPin,GPIO.LOW)
			time.sleep(HALF_BIT_TIME)
			keyval=GPIO.input(SDOPin)

            if not keyval:
                pressed=True
                if (oldKey != key):
                    end = time.time()
                    if (end-start >= 10): #cleaning mechanism enabled above 10 seconds for the queue (thread-safe way)
                        with out_q.mutex:
                            out_q.queue.clear()
                        print("Queue cleared due to keyboard inactivity")
                        visualNotification("clear") # notify the user with some LEDs animation (clearing message)
                    else: #just append the queue
                        out_q.put(sendedKey) # send it to the queue for being consummed by the pollKeys worker
                        print("key #"+str(sendedKey)+" sended to queue.")
                        visualNotification("key",key=sendedKey) # notify the user with some LEDs animation (for the specified key)
                    oldKey=key
            
            GPIO.output(SCLPin,GPIO.HIGH)
            time.sleep(HALF_BIT_TIME)
            key += 1

        pressed=False



code_q = queue.Queue() # queue containing the digit
size_q = 7 # the code is 6 digits and the validation is the seventh character...

pollWorker = threading.Thread(target=pollKeys, args=(0, size_q, code_q))
pollWorker.start()

keyboardListener = threading.Thread(target=keysProducer,args=(1,code_q))
keyboardListener.start()


keyboardListener.join()
pollWorker.join()

print("keyboard Pub/Sub engine shutdown...")