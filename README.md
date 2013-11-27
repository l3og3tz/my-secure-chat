my-secure-chat
==============

RSA implemented simple peer-to-peer chat

This is a simple chat application in python. It was written as a LAN chat, but can easily be converted into a WAN chat. In fact, i use it as a WAN chat.

The idea behind this was to create a simple medium of a secure communication between two parties that uses standard RSA encryption. As such, there are no "fancy" features, but can easily be added if you please. You however have the ability to do simple things such as change the port numbers, add some IP address that cannot connecto to you if you are the party running the server.

So far it is built to cater for just one client. That is only you and one person can chat at a time.

How To Use:

Server

If you wish to be the party running the server, just run the SecureChatServer.py module. The application is pretty interactive. It is important for the party running the server to note their port of choice and also if this is run over a WAN, should configure the appropriate port forward.

When server starts successfully, it will wait for approrpiate connection and confirm when a connection has been established. If a client establishes a connection(assuming that hostname or IP is not banned), the client automatically sends the server their Public Key, asking the server to exchange their Public Key as well.

Client To connect to the server, just run the SecureChatClient.py module.

Once a connection is established, you RSA keys are automatically generated and the public key is exchanged with the server. Your private key is always kept private.

ENJOY YOUR CONVERSATION

Note: There is no logging of any sort, the RSA keys are randomly generated on the fly, and are not repeated. They are not written to a file for reference. EVERYTHING IS IN MEMORY and discarded once the conversation is closed.

KNOWN BUGS: initially wanted to add a simple text file exchange ability, haven't quite gotten it to work yet and you are welcome to try to fix that, let me know how it goes.There is a function in the SecureUtils.py module for receiving and sending file. Take a look at those if you are interested.

l3og3tz
