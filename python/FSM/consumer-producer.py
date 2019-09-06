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

def pollKeys(id,size,in_q):
    code = [] #contain the code to be sent to the platform
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
    oldKey=18
    #
    startTime = time.time() # we want to implement a queue cleaning mechanism when nothing is typed for 10 seconds.

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