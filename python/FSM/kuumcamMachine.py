from transitions import Machine
import urllib.request
import os

class KuumcamMachine(object):
    #Define the states of the kuumcam (the endpoint)
    states = ['connected','asleep','not-connected','pending']

    def __init__(self,name):
        #we give our kuumcam a name ! Before the 'connected' state, the name is 'kuumcam', then onece connected it could be personnalized
        self.name = name

        #initialize the state machine
        self.machine = Machine(model=self, states=KuumcamMachine.states, initial='asleep') #when we create the machine, we don't know if the endpoint had been connected
                                                                                           # to the platform, so we put the initial state as 'asleep'
        #We now add all our transitions
        self.machine.add_transition(trigger='connection_lost',source='connected',dest='pending')

        self.machine.add_transition(trigger='first_use',source='asleep',dest='not-connected')
        self.machine.add_transition(trigger='reboot',source='asleep',dest='pending')

        self.machine.add_transition(trigger='first_connection',source='not-connected',dest='pending')

        self.machine.add_transition(trigger='connection_found',source='pending',dest='connected')
        self.machine.add_transition(trigger='connection_failed',source='pending',dest='not-connected')

    def isFirstUse(self):
        """
        Check if its the first time that you boot the endpoint (check data persistence)
        """
        if os.path.exists("keys.dat"):
            return False
        return True


def mainLoop()

    while True:
        
    




    






