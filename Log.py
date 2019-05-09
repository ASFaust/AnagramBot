import time
import inspect

class Logger:
 def __init__(self,logfilename):
  self.filename = logfilename
 
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
  self.put("Whoah what... logger exits.")







