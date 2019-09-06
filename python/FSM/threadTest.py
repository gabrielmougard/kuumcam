import time
import threading 
import random 
import select
import os

class KeyboardListenerDaemon(object):
    def __init__(self,fifoName):
        self.stuff = 'hi there this is KeyboardListenerDaemon'
        self.fifoName = fifoName
   

    def setup_fifo(self):
        """setup the pipe"""

        global fifo

        if os.path.exists(self.fifoName):
            os.unlink(self.fifoName)
        os.mkfifo(self.fifoName,644)
        fifo = open(self.fifoName,"r+",0)

    
    def add_random_keys(self):
        keys = ["0","1","2","3","4","5","6","7","8","9","*","#"]
        global fifo

        while True:
            key = random.choice(keys)
            fifo.write(key+"\n")
            time.sleep(1)

class FifoReaderDaemon(object):
    def __init__(self,fifoName):
        self.stuff = 'hi there this is FifoReaderDaemon'
        self.fifoName = fifoName

    def fifoReader(self):
        with open(self.fifoName) as fifo:
            count = 0
            data = []
            while True:
                select.select([fifo], [], [fifo])
                data.append(fifo.read())
                count += 1
                if count % 4 == 0:
                    print(data)
                    data = []
                    count = 0



k = KeyboardListenerDaemon("/var/run/testQueue.fifo")
k.setup_fifo() #setup the pipe
f = FifoReaderDaemon("/var/run/ttp229-keypad.fifo")

t1 = threading.Thread(target=k.add_random_keys)
t2 = threading.Thread(target=f.fifoReader)
t1.setDaemon(True)
t2.setDaemon(True)
t1.start()
t2.start()
time.sleep(20)