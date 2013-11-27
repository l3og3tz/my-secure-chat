#!/usr/bin/env python"""

"""
@author: L3o G3tz
@email : l3og3tz@gmail.com
@version: 1.0
@attention: Tested under python 2.7+
"""

import threading
import sys
import socket
import RSA
import SecureUtils as secure_utils

MODULUS_N = 10 ** 100
EXPONENT = 10 ** 1001
MULTIPLICATIVE_INVERSE = 50

screenlock = threading.Semaphore(value=1)

class ThreadManager(threading.Thread):
    '''
    Creates Threads for managing client and server reading and writing.
    
    '''

    def __init__(self, the_action, the_connection, the_public_key, the_private_key):
        '''
        Constructor
        args: action, connection
        action = the desired action - can be read or write
                 the keyword  used either "read" or "write"
        connection = a client connection object.
        
        '''
        threading.Thread.__init__(self)  # initialize super class constructor.
        self.my_action = the_action.lower()
        self.my_connection = the_connection
        self.my_continue_to_write = True
        self.my_exit_code = "EXIT"
        # self.my_filein_code = "FILE_IN" #if you intend on implementing file excahnge
        # self.my_fileout_code = "FILE_OUT" #if you intend on implementing file exchange
        
        self.my_public_key = the_public_key
        self.my_private_key = the_private_key
        
    def set_public_key(self, the_public_key):
        '''
        Sets public key from other party for encryption
        '''
        self.my_public_key = the_public_key
        
    def set_private_key(self, the_private_key):
        '''
        Sets private key for decryption
        '''
        self.my_private_key = the_private_key
    
    def run(self):
        '''
        Invoked when new thread is executed
        '''

        if (self.my_action == 'read'):
            self.read_data(int(self.my_private_key[0]), int(self.my_private_key[1]))
        else:
            self.write_data(int(self.my_public_key[0]), int(self.my_public_key[1]))
    
    def stop_write_loop(self):
        '''
        Terminates writing to client 
        '''
        self.my_continue_to_write = False
    
    
    
    def read_data(self, n, d): 
        '''
        Reads in data from client to be sent and displayed to server.
        
        '''
        try:
            my_incoming_message = secure_utils.recv_end(self.my_connection)  # receive incoming data
            my_incoming_message = secure_utils.unpack_cipherblocks_from_transmit(my_incoming_message)  # unpack the combined cipher blocks
            my_incoming_message = RSA.decrypt(my_incoming_message, n, d, len([my_incoming_message]))  # decrypt the cipher

            while my_incoming_message.strip() != self.my_exit_code and len(my_incoming_message) > 0:
                print "\r\033[1;34m<< {0}\033[1;m".format(my_incoming_message.strip())
                my_incoming_message = secure_utils.recv_end(self.my_connection)  # continue receiving more messages
                my_incoming_message = secure_utils.unpack_cipherblocks_from_transmit(my_incoming_message)  # continue unpacking the cipher blocks
                my_incoming_message = RSA.decrypt(my_incoming_message, n, d, len([my_incoming_message]))  # continue decrypting
                # client disconnected
            self.stop_write_loop() 
        except:
            pass

    def write_data(self, n, e):
        '''
        Reads in data from prompt and sending out to client 
        ''' 
        try:
            
            while self.my_continue_to_write:
                my_original_message = sys.stdin.readline()  # read input from user
                my_outgoing_message = RSA.encrypt(my_original_message, n, e, len([my_original_message]))  # encrypt the users input
                
                my_outgoing_message = secure_utils.combine_cipherblocks_for_transmit(my_outgoing_message) + ";;"  # add the ";;" delimeter. This indicates the end of a user's input. A fix for not knowing the buffer size. 
                self.my_connection.send(my_outgoing_message)  # send out message to the user.
            
                # check to see if my outgoing message is EXIT to quit the chat
                if (my_original_message.strip() == self.my_exit_code):
                    self.my_connection.shutdown(socket.SHUT_RDWR)
                    self.my_connection.close()
                    self.stop_write_loop()
        except:
            pass
    
    
    
