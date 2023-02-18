import logging
import sys 
import os

class BrennerLog:
    __instance = None

    @staticmethod 
    def get_instance(filename="logs/bot.log"):
        if BrennerLog.__instance == None:
            BrennerLog(filename)
        return BrennerLog.__instance

    def __init__(self, filename):
        if BrennerLog.__instance != None:
            raise Exception("Singleton is already initialised.")
        else:
            self.logger = logging.getLogger('brenner_log')
            self.logger.setLevel(logging.INFO)
            try:
                # Create file handler to write log messages
                handler = logging.FileHandler(filename)
            except FileNotFoundError:
                print("Log file not found. Creating a new file...")
                open(filename, 'a').close()
                handler = logging.FileHandler(filename)
            
            handler.setLevel(logging.INFO)
            # Set the log format
            formatter = logging.Formatter('%(asctime)s %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            
            # Create console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.DEBUG)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

            # Create singleton            
            BrennerLog.__instance = self

    def log_command(self, user_id, command, full_command):
        # Log the user's command usage
        message = f'User {user_id} used command: {command} with full command: {full_command}'
        self.logger.info(message)
        
    def log_exception(self, exception):
        # Log the caught exception
        self.logger.exception(exception)
        
