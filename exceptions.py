########## EXCEPTIONS TO BE THROWN WHEN REQUIRED PARAMETER ARE OF TYPE NONE
class NoneValuedPars(Exception):
    
    def __init__(self,varname,function,message='None valued parameter(s)'):
        self.varname = varname
        self.function = function
        self.message = message
        super().__init__(self.message)
    
    def __str__(self):
        return ' %s : %s in %s'%(self.message,self.varname,self.function)

########### THROWN WHEN DEFAULT ACCOUNT IS NOT SET ON THE BC CONNECTION
class EmptyDefaultAccount(Exception):
    
    def __init__(self,function,message='Deafult account not set for Blockchain Connection'):
        self.function = function
        self.message = message
        super().__init__(self.message)
    
    def __str__(self):
        return '%s in call %s'%(self.message,self.function)

########## THROWN WHEN INCOMPATIBLE FILE TYPE IS USED OF PASSED
class FileExtError(Exception):
    
    def __init__(self,required,function,message='File with in incompatible ext'):
        self.required = required
        self.function = function
        self.message = message
        super().__init__(self.message)
    
    def __str__(self):
        return ' %s :: required %s in %s'%(self.message,self.required,self.function)

########## THROWN WHEN MESSAGE SIZE IS TOO BIG TO FIT IN UDP PAYLOAD:
class PayloadExceedsUdpMtu(Exception):
    
    def __init__(self,size,function,message='Message size has exceeded upd payload size'):
        self.size = size
        self.function = function
        self.message = message
        super().__init__(self.message)
    
    def __str__(self):
        return ' %s :: current size %s (bytes) in %s'%(self.message,str(self.size),self.function)

######### THROWN WHEN THERE IS NONCE MISSMATCH ... HINTS POTENTIAL MESSAGE REPLAY ATTACK
class NonceMissMatch(Exception):
    
    def __init__(self,device,message='Message size has exceeded upd payload size'):
        self.device = device
        self.message = message
        super().__init__(self.message)
    
    def __str__(self):
        return ' %s :: nonce missmatch with device at :: %s'%(self.message,self.device)