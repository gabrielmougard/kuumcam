import threading
import RPi.GPIO as GPIO
import time
import queue
import random
import string

def pollKeys(id,size,in_q):
    count = 0
    while True:
        log_msg = in_q.get()
        if log_msg is None:
            break
        print("{0}%\t{1}".format(round(count/size*100,2), log_msg))
        count += 1
    print("Consumer #{0} shutting down".format(id))

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
    #
    while True:
        key=1
		time.sleep(CHARACTER_DELAY)

        while button < 17:
            sendedKey=key
            if (sendedKey == 17):
                sendedKey = 1
            

        ##
        item = in_q.get()
        if item is None:
            out_q.put(None)
            break
        out_q.put("#{0}\tThis string is long {1} characters".format(id, len(item)))
    print("Producer #{0} shutting down".format(id))

code_q = queue.Queue()
size_q = 7 # the code is 6 digits and the validation is the seventh character...

start = time.time()

pollWorker = threading.Thread(target=pollKeys, args=(0, size_q, code_q))
pollWorker.start()

keyboardListener = threading.Thread(target=keysProducer,args=(1,))
keyboardListener.start()


keyboardListener.join()
pollWorker.join()

print("keyboard Pub/Sub engine shutdown...")