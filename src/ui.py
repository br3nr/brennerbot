import sys
import time
import asyncio
import os


class ui:

    error_count = 0
    ping = 0
    gcount = 0

    def __init__(self):
        self.ping = 0
        self.gcount = 0
        self.error_count = 0

    def boot_title(self):
        for line in title:
            for char in line:
                sys.stdout.write(colors.OKCYAN + char)
                sys.stdout.flush()
                time.sleep(0.001)
            print()
        print()
        os.system("clear")
            

    async def init_vars(self, ping):
        self.ping = ping

    async def menu(self): 

        for line in title:
            print(colors.OKCYAN + line)
        
        print("\n")

        self.conn_icon()

        print("Most recent command: %s by %s")
        print("Number of errors: %d" % self.error_count)
        print("Bot ping: %f" % self.ping)


    def conn_icon(self):
        
        if self.gcount == 5:
            self.gcount = 0
           
        print(colors.OKGREEN + net[self.gcount] + colors.ENDC + "  Bot connected :)") 
        
        self.gcount += 1


class colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    UNDERLINE = '\033[4m'


title =["brenner bot"]
   
net = [":)",":[",":p","c:",":|"]




