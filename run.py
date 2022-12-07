import os
import sys
from bottle import run, response
import gunicorn
                     
import model
import view
import controller


# https://127.0.0.1:8081

host = 'localhost'
port = 8081
# Turn this off for production
debug = True

# cert and private key
certfile='certs/info2222.test.crt'
keyfile='certs/info2222.test.key'


def run_server():    
    '''
        run_server
        Runs a bottle server
    '''
    #run(host=host, port=port, debug=debug)
    run(host=host, port=port, debug=debug, server='gunicorn', certfile=certfile, keyfile=keyfile)


#-----------------------------------------------------------------------------
def manage_db():
    '''
        Blank function for database support, use as needed
    '''
    pass
#-----------------------------------------------------------------------------

# What commands can be run with this python file
# Add your own here as you see fit

command_list = {
    'manage_db' : manage_db,
    'server'       : run_server
}

# The default command if none other is given
default_command = 'server'

def run_commands(args):
    '''
        run_commands
        Parses arguments as commands and runs them if they match the command list

        :: args :: Command line arguments passed to this function
    '''
    commands = args[1:]

    # Default command
    if len(commands) == 0:
        commands = [default_command]

    for command in commands:
        if command in command_list:
            command_list[command]()
        else:
            print("Command '{command}' not found".format(command=command))

#-----------------------------------------------------------------------------

run_commands(sys.argv)