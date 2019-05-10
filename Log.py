import time
import inspect
import os

class Logger:
    def __init__(self,logfilename):
        self.filename = logfilename
        self.logpath = logfilename[0:logfilename.rfind("/")]
        self.last_log = ""
        if not os.path.exists(self.logpath):
            os.makedirs(self.logpath)
        self.last_log_counter = 0
        
    def put(self,log):
        if(log == self.last_log):
            if(self.last_log_counter == 0):
                print(".")
            print("\rrepeat " + str(self.last_log_counter))
            self.last_log_counter += 1
        else:
            if(self.last_log_counter > 0):
                f = open(self.filename,"a")
                f.write("last log repeated " + str(self.last_log_counter) + " times." + "\n")   
                f.close() 
            self.last_log_counter = 0
        text = time.ctime() + "    "
        stack = inspect.stack()
        s = stack[1]
        text += str(s[1]) + "  " + str(s[2]) + "  " + str(s[3]) + ": " + log
        f = open(self.filename,"a")
        f.write(text + "\n")    
        f.close()
        print(text)
        self.last_log = log
    
    def __exit__(self):
        f = open(self.filename,"a")
        f.write("Whoah what... logger exits.\n")    
        print("Whoah what... logger exits.")
        f.close()

