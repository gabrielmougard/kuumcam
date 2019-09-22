import threading
import RPi.GPIO as GPIO
import time
import queue
import random
import string
import configparser

from platform import Binder #the `Binder` class for platform connection

"""
The `Scheduler` class handle the I/O operation with the TTP229 keyboard
and call the `Binder` class when it's ready to be connected to the platform.
"""
class Scheduler:
    def __init__(self):
        self.code_q = queue.Queue() # queue containing the digit
        self.notification_q = queue.Queue()
        self.size_q = 7             # the code is 6 digits and the validation is the seventh character...
        self.engineON = False

    def run(self):
        parserKeypad = configparser.RawConfigParser()
        parserKeypad.read('config/ttp229-keypad.conf')
        self.__read_config(parserKeypad)

        pollWorker = threading.Thread(target=self.__pollKeys, args=(0, self.size_q, self.code_q,self.notification_q))
        keyboardListener = threading.Thread(target=self.__keysProducer,args=(1,self.code_q))
        notificationWorker = threading.Thread(target=self.__notificationPollWorker,args=(2,self.notification_q))
        #check for existing network connection
        parserNetwork = configparser.RawConfigParser()
        parserNetwork.read('config/network.conf')
        self.__checkConnection(parserNetwork) # if the checking is successful, no need to enter an other code, we have already the information stored on the device, so we can begin to stream.
        #

        pollWorker.start()
        keyboardListener.start()
        notificationWorker.start()

        keyboardListener.join()
        pollWorker.join()
        notificationWorker.join()

    def __pollKeys(self,id,size,in_q,notification_q):
        code = [] #contain the code to be sent to the platform
        boardMapping = {1:1,2:2,3:3,4:"correction",5:4,6:5,7:6,8:"cancel",9:7,10:8,11:9,12:"validate",14:0}
        while True:
            if (not in_q.empty()):
                key = in_q.get()
                if key == 13 or key == 15 or key == 16:
                    mappedKey = -1
                else:
                    mappedKey = boardMapping[key]
                if (mappedKey == "validate"): #error : the code must be 6 digits before being validated
                    #TODO : handle the error case where codeis not length 6
                    if len(code) < 6:
                        print("code must be 6 digits")
                        code = []
                        #clear the queue
                        with in_q.mutex:
                            in_q.queue.clear()
                        notification_q.put("cancel")
                    else:
                        print("validated !")
                        print(code)
                        notification_q.put("validate")
                        # bind to platform code
                        #platformBinder = Binder(code=code) #create a `Binder` object for platform connection

                        #try:
                        #    platformBinder.bind() #if the bind is successful, it return a new conf to be saved on the system which will be used for automated connection if the camera if switch off

                        #except BindingKuumbaError: #https://www.programiz.com/python-programming/user-defined-exception
                        #TODO : if an error occur during the binding
                        #    print("Kuumba binding error")            
                        #
                        code = []
                elif (mappedKey == "correction"):
                    #notification_q.put(key)
                    if (len(code) > 0):
                        keyToDelete = code[-1]
                        del code[-1] #delete the last one
                        print("key : "+str(keyToDelete)+" deleted.")
                    else:
                        print("nothing to delete")
                    notification_q.put("correction")

                elif (mappedKey == "cancel"):
                    notification_q.put("cancel")
                    code = [] #empty it
                    #clear the queue
                    with in_q.mutex:
                        in_q.queue.clear()
                    
                elif (mappedKey == -1):
                    print("unused key")
                else:
                    notification_q.put(mappedKey)
                    code.append(mappedKey)
                    print(str(mappedKey)+" appended to queue")
                    if len(code) == 7:
                        print("too much digits.")
                        notification_q.put("cancel")
                        code = []
                        #clear the queue
                        with in_q.mutex:
                            in_q.queue.clear()
            time.sleep(HALF_BIT_TIME) #slowing down the process to avoid perf drop

    def __keysProducer(self,id,out_q):
        #Config keyboard the hardcoded values with be replaced by a call to a config file)
        CHARACTER_DELAY=5*HALF_BIT_TIME

        GPIO.output(SCL,GPIO.HIGH)
        time.sleep(HALF_BIT_TIME)
        oldKey=18
        #
        startTime = time.time() # we want to implement a queue cleaning mechanism when nothing is typed for 10 seconds.
        visualNotification("init") # notify the user with some LEDs animation (initialization message)

        while True:
            key=1
            time.sleep(CHARACTER_DELAY)

            while key < 17:
                sendedKey=key
                if (sendedKey == 17):
                    sendedKey = 1

                GPIO.output(SCL,GPIO.LOW)
                time.sleep(HALF_BIT_TIME)
                keyval=GPIO.input(SD0)

                if not keyval:
                    pressed=True
                    end = time.time()
                    if (oldKey != key) or end-startTime > 0.3:

                        if (end-startTime >= 10): #cleaning mechanism enabled above 10 seconds for the queue (thread-safe way)
                            out_q.put(CANCEL) #indicating that we want to delete code
                            print("Queue cleared due to keyboard inactivity")
                            startTime = time.time()
                        else: #just append the queue
                            out_q.put(sendedKey) # send it to the queue for being consummed by the pollKeys worker
                            startTime = time.time()
                        oldKey=key

                GPIO.output(SCL,GPIO.HIGH)
                time.sleep(HALF_BIT_TIME)
                key += 1

            pressed=False

    def __visualNotification(self,code,key=None,interruptPending=None):
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

        elif (code == "pending"): #need to be executed in a new thread ==> threading.Thread(target=visualNotification,args=("pending")).start() 
            #TODO : LEDs animation for trying to reach the platform once the code is entered  
            while (interruptPending is None):
                GPIO.output(YELLOW,GPIO.HIGH)
                time.sleep(LED_BLINKING)
                GPIO.output(YELLOW,GPIO.LOW)
                time.sleep(LED_BLINKING)
            GPIO.output(YELLOW,GPIO.LOW) #when interrupt signal occurs

        else: #meaning it's "key" and that key=sendKey
            #TODO : LEDs animation for key typing
            if (key == "validate"):
                GPIO.output(GREEN,GPIO.HIGH)
                GPIO.output(YELLOW,GPIO.LOW)
                GPIO.output(RED,GPIO.LOW)
                time.sleep(LED_BLINKING)
                GPIO.output(GREEN,GPIO.LOW)
                GPIO.output(YELLOW,GPIO.LOW)
                GPIO.output(RED,GPIO.LOW)

            elif (key == "correction"):
                GPIO.output(GREEN,GPIO.LOW)
                GPIO.output(YELLOW,GPIO.HIGH)
                GPIO.output(RED,GPIO.LOW)
                time.sleep(LED_BLINKING)            
                GPIO.output(GREEN,GPIO.LOW)
                GPIO.output(YELLOW,GPIO.LOW)
                GPIO.output(RED,GPIO.LOW)

            elif (key == "cancel"):
                GPIO.output(GREEN,GPIO.HIGH)
                GPIO.output(YELLOW,GPIO.HIGH)
                GPIO.output(RED,GPIO.HIGH)
                time.sleep(LED_BLINKING)
                GPIO.output(GREEN,GPIO.LOW)
                GPIO.output(YELLOW,GPIO.LOW)
                GPIO.output(RED,GPIO.LOW)

            else: #digits
                GPIO.output(GREEN,GPIO.LOW)
                GPIO.output(YELLOW,GPIO.LOW)
                GPIO.output(RED,GPIO.HIGH)
                time.sleep(LED_BLINKING)
                GPIO.output(GREEN,GPIO.LOW)
                GPIO.output(YELLOW,GPIO.LOW)
                GPIO.output(RED,GPIO.LOW)

    def __notificationPollWorker(self,id,notification_q):
        WORKER_DELAY = 0.001
        while True:
            if (not notification_q.empty()):
                key = notification_q.get()
                self.__visualNotification("key",key)
            time.sleep(WORKER_DELAY)

    def __read_config(parser):
        global GREEN,YELLOW,RED,SCL,SD0,HALF_BIT_TIME,LED_BLINKING

        #parse config file (PINS)
        GREEN  = parser.getint("PINS","GREEN")
        YELLOW = parser.getint("PINS","YELLOW")
        RED    = parser.getint("PINS","RED")
        BLUE   = parser.getint("PINS","BLUE")

        SCL = parser.getint("PINS","SCL_PIN")
        SD0 = parser.getint("PINS","SDO_PIN")

        #parse config file (tempo)
        HALF_BIT_TIME   = parser.getfloat("TEMPO","HALF_BIT_TIME")
        LED_BLINKING    = parser.getfloat("TEMPO","LED_BLINKING")

        #pin config
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(GREEN,GPIO.OUT)
        GPIO.setup(YELLOW,GPIO.OUT)
        GPIO.setup(RED,GPIO.OUT)
        GPIO.setup(BLUE,GPIO.OUT)
        GPIO.setup(SCL,GPIO.OUT)
        GPIO.setup(SD0,GPIO.IN)

    def __checkConnection(self,parser):
        """
        check the `network.conf` file for existing connection. If successful, it'll bypass the keyboard process
        and directly connect to the platform. However, the Pub/Sub engine for the keyboard will be active for 
        further potential needs (i.e: special update from the platform to the endpoint.)
        """
        uuid = parser.get("PLATFORM","UUID")
        print("[ENDPOINT UUID] : "+uuid)
        
        if (uuid != ''): #has already been connected to the platform  
            platformBinder = Binder()
            
            
            self.engineON = platformBinder.bind() #we don't need a code in argument since we have already the UUID

            

        
