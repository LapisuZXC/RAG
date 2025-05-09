import logging
import os
#import sys

class Loger:
    def __init__(self, filename: str):
        self.filename = os.path.basename(filename)
        
        logging.basicConfig(
            level=logging.INFO,
            format='[%(asctime)s] [%(name)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            force=True
        )
        self.logger = logging.getLogger(self.filename)
        
    def prnt(self, message):
        # Использовать вместо print function
        #now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        #print(f"[{now}] - [{self.filename}] - {message}")
        self.logger.info(message)