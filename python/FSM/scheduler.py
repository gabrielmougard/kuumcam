import threading
import RPi.GPIO as GPIO
import time
import queue
import random
import string
import ConfigParser

"""
The `Scheduler` class handle the I/O operation with the TTP229 keyboard
and call the `Binder` class when it's ready to be connected to the platform.
"""
class Scheduler:
    def __init__(self):
        self.code_q = queue.Queue() # queue containing the digit
        self.size_q = 7             # the code is 6 digits and the validation is the seventh character...

    def run(self):
        parser = ConfigParser.RawConfigParser()
        parser.read('config/ttp229-keypad.conf')
        read_config(parser)

        pollWorker = threading.Thread(target=pollKeys, args=(0, self.size_q, self.code_q))
        keyboardListener = threading.Thread(target=keysProducer,args=(1,self.code_q))

        pollWorker.start()
        keyboardListener.start()

        keyboardListener.join()
        pollWorker.join()

    def pollKeys(self,id,size,in_q):
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

    def keysProducer(self,id,out_q):

        #Config keyboard (the hardcoded values with be replaced by a call to a config file)
        GPIO.setMode(GPIO.BCM)
        CHARACTER_DELAY=5*HALF_BIT_TIME

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

    def visualNotification(code,key=None,interruptPending=None):
        """
        LED animation for notifying the user according to the specified code (we will have 3 LEDs on the prototype : RED, YELLOW, GREEN)
        Ultimately, we should have only one RGB led to do all the color that we want.
        """
        if (code == "init"):

            start = time.time()
            while True:
                end = time.time()
                if (end - start > 3):
                    #shutdown the GREEN and YELLOW and quit (let the RED switch on)
                    GPIO.output(GREEN,GPIO.LOW)
                    GPIO.output(YELLOW,GPIO.LOW)
                    GPIO.output(RED,GPIO.HIGH)
                    break

                GPIO.output(GREEN,GPIO.HIGH)
                GPIO.output(YELLOW,GPIO.LOW)
                GPIO.output(RED,GPIO.LOW)

                time.sleep(LED_BLINKING)

                GPIO.output(GREEN,GPIO.LOW)
                GPIO.output(YELLOW,GPIO.HIGH)
                GPIO.output(RED,GPIO.LOW)

                time.sleep(LED_BLINKING)

                GPIO.output(GREEN,GPIO.LOW)
                GPIO.output(YELLOW,GPIO.LOW)
                GPIO.output(RED,GPIO.HIGH)

                time.sleep(LED_BLINKING)

                GPIO.output(GREEN,GPIO.LOW)
                GPIO.output(YELLOW,GPIO.HIGH)
                GPIO.output(RED,GPIO.LOW)

                time.sleep(LED_BLINKING)

        elif (code == "clear"):
            #TODO : LEDs animation for queue/keyboard clearing
            #just switch off all the LEDs (just like a "sleep" mode)
            GPIO.output(GREEN,GPIO.LOW)
            GPIO.output(YELLOW,GPIO.LOW)
            GPIO.output(RED,GPIO.LOW)

        elif (code == "pending"): #need to be executed in a new thread ==> threading.Thread(target=visualNotification,args=("pending")).start() 
            #TODO : LEDs animation for trying to reach the platform once the code is entered  
            while (interruptPending is None):
                GPIO.output(YELLOW,GPIO.HIGH)
                time.sleep(LED_BLINKING)

        else: #meaning it's "key" and that key=sendKey
            #TODO : LEDs animation for key typing
            if (key == VALIDATION):

            elif (key == CORRECTION):

            elif (key == CANCEL):

            else: #digits

    def shutdown(self):
        print("keyboard Pub/Sub engine shutdown...")

    def read_config(parser):
        global GREEN,YELLOW,RED,SCLPin,SDOPin,HALF_BIT_TIME,NUM_BITS,VALIDATION,CORRECTION,CANCEL,POLL_KEYS_DELAY,LED_BLINKING

        #parse config file (PINS)
        GREEN  = parser.getint("PINS","GREEN")
        YELLOW = parser.getint("PINS","YELLOW")
        RED    = parser.getint("PINS","RED")
        SCLPin = parser.getint("PINS","SCL_PIN")
        SDOPin = parser.getint("PINS","SDO_PIN")

        #parse config file (tempo)
        HALF_BIT_TIME   = parser.getfloat("TEMPO","HALF_BIT_TIME")
        POLL_KEYS_DELAY = parser.getfloat("TEMPO","POLL_KEYS_DELAY")
        LED_BLINKING    = parser.getfloat("TEMPO","LED_BLINKING")

        #parse config file (special keys)
        VALIDATION = parser.getint("KEYS","VALIDATION")
        CORRECTION = parser.getint("KEYS","CORRECTION")
        CANCEL     = parser.getint("KEYS","CANCEL")

        #parse config file (number of bits)
        NUM_BITS = parser.getint("GLOBAL","NUM_BITS")
