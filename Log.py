import time
import inspect
import os

class Logger:
    def __init__(self,logfilename):
        self.filename = logfilename
        self.logpath = logfilename[0:logfilename.rfind("/")]
        if not os.path.exists(self.logpath):
            os.makedirs(self.logpath)
        
    def put(self,log):
        text = time.ctime() + "    "
        stack = inspect.stack()
        s = stack[1]
        text += str(s[1]) + "  " + str(s[2]) + "  " + str(s[3]) + ": " + log
        f = open(self.filename,"a")
        f.write(text + "\n")    
        f.close()
        print(text)

    def __exit__(self):
        f = open(self.filename,"a")
        f.write("Whoah what... logger exits.\n")    
        print("Whoah what... logger exits.")
        f.close()

