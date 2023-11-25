'''----------------------------------------------------------------------------------------
Title:          serverConnection.py
Description:    This module contains the server connection and the functions that will be
                called when the server receives data from the client.
Author:         Jake Mark Perez, Johnfil Initan, and Vincent Abella
Date:           November 2023
Version:        1.0
Revision History:
----------------------------------------------------------------------------------------'''

#libraries
import socket
import threading
import os
import sys
import logging
from datetime import datetime

from concurrent.futures import ThreadPoolExecutor
from Server.serverDprosa import serverDprosa

#Global Variables
MAX_THREADS = 10  # Maximum number of threads in the thread pool
thread_pool = ThreadPoolExecutor(max_workers=MAX_THREADS)

timegap_dict = {}
cluster_dict = {}
global_var_lock = threading.Lock()
checkCompiledData = False
isSorting = True
customerCount = 0

globalDirectory = ''


'''----------------------------------------------------------------------------------------
def name:      server
Description:   This function is used to start the server.
Params:        None
Returns:       None
----------------------------------------------------------------------------------------'''  
def server():
    SERVER_ADDRESS = ('localhost', 8080)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        server_socket.bind(SERVER_ADDRESS)
        server_socket.listen(10)
        print("Server is listening on", SERVER_ADDRESS)
    except socket.error as e:
        print("Unable to start server:", str(e))
        return
    

    with thread_pool:
        while True:
            client_socket, client_address = server_socket.accept()
            print("Accepted connection from", client_address)
            thread_pool.submit(handle_client, client_socket)


'''----------------------------------------------------------------------------------------
def name:      start_server
Description:   This function is used to start the server.
Params:        None
Returns:       None
----------------------------------------------------------------------------------------'''      
def start_server():

    server_thread = threading.Thread(target=server)
    server_thread.start()

'''----------------------------------------------------------------------------------------
def name:       perform_cluster
Description:    This function is used to perform the clustering of the data.
Params:         client_socket - the socket of the client
                directory - the directory of the data
Returns:        None
----------------------------------------------------------------------------------------'''  
def perform_cluster(client_socket,directory):
    # Perform action 1 based on the received data
    print("Performing cluster with directory:", directory)
    #client_socket.send(directory.encode('utf-8'))
    global timegap_dict
    global cluster_dict
    global checkCompiledData
    global globalDirectory
    sD = serverDprosa()

    if sD.compilereadCSV(directory) == True:
        checkCompiledData = True
        sD.cluster_event(directory)
        sD.storeClusterTimeDict(directory)
        timegap_dict,cluster_dict = sD.timegap_cluster()
        sD.print_data()

    else :
        checkCompiledData = False
        sD.print_data()

    print("Clustering Done..")
    print("*****************************************")
    print("*****************************************")
    client_socket.send("DONE.".encode('utf-8'))
    clientID = client_socket

    globalDirectory = directory


'''----------------------------------------------------------------------------------------
def name:      perform_normal
Description:   This function is used to perform the FALSE sorting of the data.
Params:        client_socket - the socket of the client
               data - the data to be sorted
Returns:       None
----------------------------------------------------------------------------------------'''  
def perform_normal(client_socket,data):
    global isSorting
    isSorting = False
    perform_sorting(client_socket,data)
    isSorting = True

'''----------------------------------------------------------------------------------------
def name:      perform_sort
Description:   This function is used to perform the TRUE sorting of the data.
Params:        client_socket - the socket of the client
               data - the data to be sorted
Returns:       None
----------------------------------------------------------------------------------------'''  
def perform_sort(client_socket,data):
    global isSorting
    isSorting = True
    perform_sorting(client_socket,data)
    isSorting = False

'''----------------------------------------------------------------------------------------
def name:      perform_sorting
Description:   This function is used to perform the sorting of the data.
Params:        client_socket - the socket of the client
               data - the data to be sorted
Returns:       None
----------------------------------------------------------------------------------------'''  
def perform_sorting(client_socket,data):
    global timegap_dict
    global cluster_dict
    global checkCompiledData
    global isSorting
    global customerCount
    # Perform action 2 based on the received data
    print("Performing sorting with list:", data)

    stage, data = data.split('^')
    data = data.strip()

    if stage == "start":
        X = None
        customerCount, data = data.split('/')
        customerCount = int(customerCount)
        print(f'Costumer Count: {customerCount}')
    elif stage == "mid":
        X, data = data.split('/')
        data = data.strip()
        data = X + ',' + data

    elif stage == "end":
        X = None
    else:
        print("Unknown stage description:", stage)

    sD = serverDprosa()
    itemList = sD.convertData(data)

    if not isSorting:
        print("#################NOT SORTING######################")
        notsortedList = itemList.copy()
        print(notsortedList)
        #if stage == "start":
            #notsortedList.pop(0)
        if stage == "mid":
            notsortedList.pop(0)
        notsorted = ', '.join(notsortedList)
        print(notsorted)
        print("################################################")

    if stage == "start":

        sortedList, timegap_dict, cluster_dict = sD.sort_shoppingList(X, itemList, timegap_dict, cluster_dict, customerCount)
        sortedItem = ', '.join(sortedList)

        #add the first item of the itemList into the sortedItem
        sortedItem = itemList[0] + ', ' + sortedItem

    elif stage == "end":
        sortedItem = ' '.join(itemList)
    else:
        sortedList, timegap_dict, cluster_dict = sD.sort_shoppingList(X, itemList, timegap_dict, cluster_dict,  customerCount)
        sortedItem = ', '.join(sortedList)
        
    print(sortedItem)

    print("*****************************************")
    print("*****************************************")
    print(f'isSorting: {isSorting}')
    if isSorting:
        print('SORTING PERFORMED....')
        client_socket.send(sortedItem.encode('utf-8'))
    elif not isSorting:
        print('SORTING NOT PERFORMED.... :( :( :( ')
        client_socket.send(notsorted.encode('utf-8'))
    print("*****************************************")


'''----------------------------------------------------------------------------------------
def name:      handle_client
Description:   This function is used to handle the client connection.
Params:        client_socket - the socket of the client
Returns:       None
----------------------------------------------------------------------------------------'''  
def handle_client(client_socket):

    thread_number = threading.get_ident()
    print(f"Thread {thread_number}: Handling client connection.")

    while True:
        # Receive data and description from the client
        received_data = client_socket.recv(1024).decode('utf-8')
        if not received_data:
            break

        # Split the received data into description and data
        description, data = received_data.split('|')
        description = description.strip()

        # Check if the description corresponds to a known action
        if description in ACTION_FUNCTIONS:
            # Call the appropriate function based on the description
            action_function = ACTION_FUNCTIONS[description]
            action_function(client_socket,data)
            
            break
            thread_pool.submit(action_function, client_socket, data)

            client_socket.close()
        else:
            print("Unknown action description:", description)
                
    # Close the client socket when the connection is closed
    client_socket.close()


'''----------------------------------------------------------------------------------------
Class name:     LoggerWriter
Description:    This class is used to redirect the stdout to the logger.
Params:         logger - the logger object
Returns:        None
----------------------------------------------------------------------------------------'''    

class LoggerWriter:
    '''----------------------------------------------------------------------------------------
    def name:      __init__
    Description:   This function is the constructor of the LoggerWriter class.
    Params:        logger - the logger object
    Returns:       None
    ----------------------------------------------------------------------------------------'''  
    def __init__(self, logger, level=logging.INFO):
        self.logger = logger
        self.level = level
    '''----------------------------------------------------------------------------------------
    def name:      write
    Description:   This function is used to write the message to the logger.
    Params:        message - the message to be written to the logger  
    Returns:       None
    ----------------------------------------------------------------------------------------'''  
    def write(self, message):
        if message.rstrip():  # Avoid logging blank lines
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_message = f"{timestamp} - {message.rstrip()}"
            self.logger.log(self.level, log_message)
    '''----------------------------------------------------------------------------------------
    def name:      flush
    Description:   This function is used to flush the logger.
    Params:        None
    Returns:       None
    ----------------------------------------------------------------------------------------'''  
    def flush(self):
        pass

# Define a mapping of descriptions to functions
ACTION_FUNCTIONS = {
    "cluster": perform_cluster,
    "sort": perform_sort,
    "notsort": perform_normal
}

# Create a "Logs" directory if it doesn't exist
logs_dir = "Logs"
os.makedirs(logs_dir, exist_ok=True)

# Create a logger with a timestamp in the name
log_name = os.path.join(logs_dir, f"serverLogs_{datetime.now().strftime('%Y%m%d%H%M%S')}.log")
logging.basicConfig(filename=log_name, level=logging.INFO)
logger = logging.getLogger()

# Redirect stdout to the logger
sys.stdout = LoggerWriter(logger, logging.INFO)

print("Logs, logs, logs!")