import datetime
import os
#import sys

class Loger():
    def __init__(self, filename):
        self.filename = os.path.basename(filename)
    
    
    def prnt(self, message):
        # Использовать вместо print function
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{now}] - [{self.filename}] - {message}")