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
MAX_CLIENTS = 2

# encryption variables
MODULUS_N = 10 ** 100
EXPONENT = 10 ** 101
MULTIPLICATIVE_INVERSE = 50

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

def display_server_menu():
    
    '''
    Displays a program menu for user to choose an option
    
    '''

    try:
        # Clears the screen
        secure_utils.clear_screen()
        while True:
            # Display My Logo
            secure_utils.draw_server_logo() 
            print '----------------------------------\n'
            print'1.  Change Port To Use\n2.  Run Server\n3.  View/Add Blocked IPs\n4.  Remove Blocked IPC\n5.  Program Information\n99. Exit Program\n'
            print '----------------------------------\n'
            user_chosen_option = raw_input('Enter an option>> ')
            secure_utils.clear_screen()
            
            if(user_chosen_option == '1'):
                set_port_number()
            elif(user_chosen_option == '2'):
                start_server_listener()
            elif(user_chosen_option == '3'):
                secure_utils.add_ip_to_ban_list()
            elif(user_chosen_option == '4'):
                secure_utils.remove_ip_from_ban_list()
            elif(user_chosen_option == '5'):
                secure_utils.program_info()
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

def send_welcome_message(the_client_connection, the_host_name, the_user_address):
    
    the_client_connection.send("\n[+] Hello {0} at {1}\n[+]You are now connected to the Secure Chat Server".format(the_host_name, the_user_address))
    

def exchange_keys_with_client(the_connection):
        '''
        Prompts as to whether to send keys or not
        If keys are not sent, program terminates because it is
        impossible to encrypt and decrypt messages
        '''
        try:
            
            # wait to receive client's public key
            key = the_connection.recv(8192)
            key = key.split(',')
            public_key_tuple = (key[0], key[1])
            print '[+] Secure Chat Partner\'s Public Key Received\n'

            secure_utils.display_processing_cursor("Generating And Exchanging Your Keys")
            (n, e, d) = secure_utils.generate_my_keys(MODULUS_N, EXPONENT, MULTIPLICATIVE_INVERSE)
        
            print "[+] Your TRUNCATED Public Key is (****{0},****{1})".format(str(n)[0:5], str(e)[0:5])
            print "[+] Your Private Key is hidden"
            
            public_key = str(n) + ',' + str(e)
            the_connection.send(public_key)
            print '[+] Your Public Key Has Been Sent To The Other Party'
        
            private_key_tuple = (n, d)
        
            return ((public_key_tuple), (private_key_tuple))
        except Exception, e:
                secure_utils.clear_screen()
                print "\n\033[1;41m[+] Error connecting to server or exchanging keys\033[1;m"
                raw_input("\nPress [ENTER] To Return To The Main Menu...\n")
                return
                pass


def start_server_listener(the_host_name=HOST_NAME, the_max_clients=MAX_CLIENTS):
    '''
    Starts the Secure Server, if successfully also starts listening or a client/chat partner to connect.
    '''    
    try:
        secure_utils.clear_screen()  # clear screen for nice output
        secure_utils.draw_server_logo()  # draws logo 
        
        my_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        my_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
        my_server_socket.bind(('', PORT_NUMBER))
        my_server_socket.listen(the_max_clients)
                                                                       
        
        print "\033[1;43m[+] The Chat Server Successfully Started\033[1;m"
        print "\033[1;43m[+] Now accepting chat clients\033[1;m\n"
        
        # Blocking call to accept connections
        
        (my_client_connection, my_client_address) = my_server_socket.accept()
        
        print "[+] User {0} at {1} is now connected to the server".format(socket.gethostname(), my_client_address[0])

        if (my_client_address[0] in secure_utils.populated_banned_list()):  # check if this user is banned from connecting, send appropriate msg
            print "[+] User at {0} is banned from this server... disconnecting".format(my_client_address[0])
            my_client_connection.send("Its unfortunate, but you are banned from connecting to this server")
            return 0
        
        else:
            my_client_connection.send("Send Keys")  # Tell other party to send their public keys.
            
            # wait to receive client's public key
            (publicKeyTuple, privateKeyTuple) = exchange_keys_with_client(my_client_connection) 
        
           
            print '\n\033[1;42m*******Type your message below and hit enter to send. Type \'EXIT\' to end conversation.*******\033[1;m\n'

            ReadAndDecryptThread = ThreadManager('read', my_client_connection, publicKeyTuple, privateKeyTuple)  # Thread for reading data and decrypting
            WriteAndEcnryptThread = ThreadManager('write', my_client_connection, publicKeyTuple, privateKeyTuple)  # Thread for writing data and decrypting

            ReadAndDecryptThread.start()  # Start the read and decrypt thread
            WriteAndEcnryptThread.start()  # Starts the writing and encrypting thread

            # wait until client dc's
            ReadAndDecryptThread.join()
            print '[+] Your partner has left the conversation. Press any key to continue...\n'

            # stop the write thread
            WriteAndEcnryptThread.stop_write_loop()
            WriteAndEcnryptThread.join()

            # shut down client connection
            try:
                my_client_connection.shutdown(socket.SHUT_RDWR)
                my_client_connection.close()
            except:
                # connection already closed
                pass

            # shut down server
            secure_utils.display_processing_cursor('Shutting server down...')
            my_server_socket.shutdown(socket.SHUT_RDWR)
            my_server_socket.close()
 
            return 0 
                
    except socket.error as socket_error:
        print socket_error[1]
        raw_input("\nPress [ENTER] To Return To The Main Menu...\n")
        # print "[-] There was problem starting the server"
        pass

def main():
    display_server_menu()
    
if __name__ == "__main__":
    main()
        
