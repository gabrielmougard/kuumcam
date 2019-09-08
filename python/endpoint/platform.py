import request

"""
`Binder` handle the I/O operations between the endpoint and the platform.
"""
class Binder:
    __init__(self,code=None): #when auto-connection, no need for the code since we have the UUID in `network.conf`
        self.code = code
        if (code is not None):
            

    def bind(self):
