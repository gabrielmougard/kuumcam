from scheduler import Scheduler

"""
main routine which will lauch the many processes of the endpoint in calling the Scheduler.
"""

s = Scheduler()

try:
    s.run()
except KeyboardInterrupt:
    print(s.shutdown()) #shutdown the keyboard Pub/Sub engine
















    

