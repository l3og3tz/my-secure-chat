#!/usr/bin/env python

"""
@author: L3o G3tz
@email : l3og3tz@gmail.com
@version: 1.0
@attention: Tested under python 2.7+
"""

import socket
import SecureUtils as secure_utils
from SecureThreadManager import ThreadManager

HOST_NAME = "localhost"
PORT_NUMBER = 1234

# encryption variables
MODULUS_N = 10 ** 100
EXPONENT = 10 ** 101
MULTIPLICATIVE_INVERSE = 50


def set_host_name():
    '''
    Sets the host name to Secure Chat server/other party
    '''
    global HOST_NAME
    try:
        print('[*] Current Host Name: %s' % HOST_NAME)
        tmp_host = raw_input('Enter Host IP Address: (Leave Blank To Not Change)\n>> ')
        if(tmp_host == ''):
            print '[*] Host Name/IP Address Not Changed'
        else:
            HOST_NAME = str(tmp_host)
            print'[+] Host Name/IP Successfully Set.'
        raw_input("Press [ENTER] To Return To The Main Menu...\n")
        return
    except Exception as the_e:
        print the_e
        # print the_e[1]
        pass


def set_port_number():
    '''
    Changes the port number used by the Secure Chat
    '''
    global PORT_NUMBER
    try:
        print('[*] Current Port Number: %i' % PORT_NUMBER)
        tmp_port = raw_input('New Port Number: (Leave Blank To Not Change)\n>> ')
        if(tmp_port == ''):
            print '[*] Port Number Not Changed'
        else:
            PORT_NUMBER = int(tmp_port)
            print'[+] Port Number Successfully Changed.'
        raw_input("Press [ENTER] To Return To The Main Menu...\n")
        return
    except Exception as the_e:
        print the_e[1]
        pass


def display_client_menu():
    
    '''
    Displays a program menu for user to choose an option
    
    '''

    try:
        # Clears the screen
        secure_utils.clear_screen()
        while True:
            # Display My Logo
            secure_utils.draw_client_logo()
            print '----------------------------------\n'
            print'1.  Set Host Name/IP To Use\n2.  Set Port Number To Use\n3.  Connect To Secure Chat Session\n4.  Program Information\n99. Exit Program\n'
            print '----------------------------------\n'
            user_chosen_option = raw_input('Enter an option >> ')
            secure_utils.clear_screen()
            
            if(user_chosen_option == '1'):
                set_host_name()
            elif(user_chosen_option == '2'):
                set_port_number()
            elif(user_chosen_option == '3'):
                connect_to_server()
            elif(user_chosen_option == '4'):
                secure_utils.program_info()
            elif(user_chosen_option == '5'):
                print "Coming Soon"
            elif(user_chosen_option == '6'):
                print "Coming Soon"
            elif(user_chosen_option == '98'):
                print "Coming Soon"
            elif(user_chosen_option == '99'):
                break
            else:
                print('[--] ERROR: Invalid Option.')
                raw_input("Press [ENTER] To Return To The Main Menu...\n")
            secure_utils.clear_screen()
                
    except KeyboardInterrupt:
        print'[--] CTRL+C Pressed.'
    except Exception, e:
        print'[--] ERROR: %s' % str(e)
    return 0


def print_welcome_message(the_host_name, the_user_address):
    
    print"\033[1;43m\n[+] Hello {0} at {1}\033[1;m\n\033[1;43m[+] You are now connected to the Secure Chat Server\033[1;m".format(the_host_name, the_user_address)
    
def exchange_keys_with_server(the_connection):
        '''
        Prompts as to whether to send keys or not
        If keys are not sent, program terminates because it is
        impossible to encrypt and decrypt messages
        '''
        try:
            
            # wait to receive client's public public_key
        
            secure_utils.display_processing_cursor("Generating And Exchanging Keys")
            (n, e, d) = secure_utils.generate_my_keys(MODULUS_N, EXPONENT, MULTIPLICATIVE_INVERSE)
        
            print "[+] Your TRUNCATED Public Key is (****{0},****{1})".format(str(n)[0:5], str(e)[0:5])
            print "[+] Your Private Key is hidden"
            
            generated_public_key = str(n) + ',' + str(e)
            the_connection.send(generated_public_key)
            print "[+] Sent Your Public Key To Your Secure Chat Partner"
        
            message_received = the_connection.recv(8192)
        
            if(message_received == "Send Keys"):
            
                message_received = the_connection.recv(8192)
                servers_public_key = message_received.split(",")
                servers_public_key_tuple = (servers_public_key[0], servers_public_key[1])
                print '[+] Server\'s Public Key Received\n'
                client_private_key_tuple = (n, d)        
                return ((servers_public_key_tuple), (client_private_key_tuple))
            else:
                
                print "\n\033[1;41m[+] Message Received from server : {0}\033[1;m".format(message_received)
                secure_utils.display_processing_cursor("Returning to main menu")
                return ((None, None), (None, None))    
        except Exception, e:
                secure_utils.clear_screen()
                print "\n\033[1;41m[+] Error connecting to server or exchanging keys\033[1;m"
                pass

def connect_to_server():
    '''
    Starts a connection to the server 
    '''
    try:
        
        secure_utils.clear_screen()  # clear screen for nice output
        secure_utils.draw_client_logo()  # 
        
        my_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        my_client_socket.connect((HOST_NAME, PORT_NUMBER))

        print_welcome_message(socket.gethostname(), my_client_socket.getsockname()[0])
    
        # wait to receive server's public key . WILL RETURN NO KEYS IF SERVER HAS BANNED YOU FROM CONNECTING
        (publicKeyTuple, privateKeyTuple) = exchange_keys_with_server(my_client_socket)
         
        # checks whether server accepted or refused connection. RETURNS NONE IF BANNED
        if((publicKeyTuple, privateKeyTuple) == ((None, None), (None, None))):
            my_client_socket.close()  # close the connection or session as you cannot carry on.

        else:  # begin interaction with other party.
            
            print '\n\033[1;42m*******Type your message below and hit enter to send. Type \'EXIT\' to end conversation.*******\033[1;m\n'
        
            ReadAndDecryptThread = ThreadManager('read', my_client_socket, publicKeyTuple, privateKeyTuple)  # Thread for reading in data and decrypting
            WriteAndEncryptThread = ThreadManager('write', my_client_socket, publicKeyTuple, privateKeyTuple)  # Thread for writing data and encrypting


            ReadAndDecryptThread.start()
            WriteAndEncryptThread.start()

            ReadAndDecryptThread.join()
            print '[+] Your partner has left the conversation. Press any key to continue...\n'

            # stop the write thread
            WriteAndEncryptThread.stop_write_loop()
            WriteAndEncryptThread.join()
    

            # shut down client connection
            secure_utils.display_processing_cursor('Shutting client down...')

    except socket.error as socket_error:
        secure_utils.clear_screen()
        print socket_error[1] + "\n"
        raw_input("Press [ENTER] To Return To The Main Menu...\n")
        return
        pass
    
    
def main():
    display_client_menu()
    
if __name__ == "__main__":
    main()
        

