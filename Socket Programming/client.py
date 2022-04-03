# Import socket module
from cmath import phase
from http import server
from resource import getpagesize
from socket import * 
import sys # In order to terminate the program
from struct import *
from random import randint
import time

serverName = 'localhost'
#serverName = '10.84.88.53'

# Assign a port number
serverPort = 12000

# Bind the socket to server address and server port
clientSocket = socket(AF_INET, SOCK_DGRAM)

#I was re using server and client a lot so I decided to maek them global vriables
client = 1
server = 2

def phase_a(serverName, serverPort, clientSocket):
    #data design and string padding
    msg = "Hello World!!!"
    #packet_data = pack('hhs', 0, 3, msg)
    
    #while calcsize(packet_data) % 4 != 0:
        #msg += '\0'
        #packet_data = pack('hhs', 0, 3, msg)

    
    msg = 'Hello World!!!00'
    #data_length = sys.getsizeof(msg)
    data_length = len(msg.encode())

    #pack and send data to the server
    #packet_data = pack('ihhs', data_length, 0, 3, msg)
    header_section = pack('!IHH', data_length, 0, 3)
    packet_data = header_section + msg.encode('utf-8')
    clientSocket.sendto(packet_data, (serverName, serverPort))

    #recieve data from the server and unpack
    recievedfromserver, serverAddress = clientSocket.recvfrom(2048)
    data = recievedfromserver
    server_data = unpack('!IHHIIHH', data)

    #print the data out
    print("Received packet from server: ", "data_len: ", server_data[0], "pcode: ", server_data[1], "entity: ",server_data[2], "repeat: ", server_data[3], "len: ", server_data[5], "udp_port: ", server_data[4], "codeA", server_data[6])

    #we neeed these values for future phases so return them
    codeA = server_data[6]
    repeat = server_data[3]
    udp_port = server_data[4]
    lenn = server_data[5]
    return codeA, repeat, lenn, udp_port

    #close the socket
    clientSocket.close()

def phase_b(serverName, serverPort, clientSocket, codeA, repeat, lenn):
    pcode = codeA
    entity = client
    packet_id = 0

    while(lenn % 4 == 0):
        lenn += 1
    
    byte_array = bytearray(lenn)
    data_length = 4 + len(byte_array) #length of the byte array plus length of the packet id

    while packet_id < repeat :
        clientSocket.settimeout(5)
        ack = -1
        wait_time = 0
        while ack != packet_id:
            if wait_time > 0:
                time.sleep(5)
            
            #send to server
            #data_part = pack('!IIHH{lenn}s', packet_id, data_length, pcode, client, byte_array)
            
                
            data_part = pack("!IHHI{}s".format(lenn), data_length, pcode, client, packet_id, byte_array)
            clientSocket.sendto(data_part, (serverName, serverPort))
            
            #recieve acknowledgement 
            try:
                recievedfromserver, serverAddress = clientSocket.recvfrom(2048)
                server_data = unpack('!IHHI', recievedfromserver)
                ack = server_data[3]
                print("Received acknowledgement packet from server: data_len: {} pcode:  {} entity: {} acknumber:  {}".format(server_data[0], server_data[1], server_data[2], server_data[3]))
                wait_time += 1
            except:
                print("socket timed out for phase b returning hard coded data")
                return data_for_c()
            

        packet_id += 1

    #recieve tcp info
    server_data, serverAddress = clientSocket.recvfrom(2048)
    data_length, pcode, tcp_port, codeB = unpack('!IHHII', server_data)

    return tcp_port, codeB
def data_for_c():
	#return tcp_port, codeB
	return 25200, 190


def phase_c(serverName, tcp_port, codeB):
    serverPort = tcp_port
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverName, serverPort))
    print("connected to tcp port: ", tcp_port)
    clientSocket.settimeout(3)

    # sentence = input(' Input lower case sentence: ')
    # clientSocket. send(sentence.encode())
    # modifiedSentence = clientSocket.recv(1024)
    # print('From server: ', modifiedSentence.decode())
    
    server_data = clientSocket.recv(1024)
    data_length, pcode, entity, repeat2, length2, codeC, char = unpack('IHHIIIB', server_data)

    print("Received packet from server: data_len: ", data_length,  "pcode: ", pcode, "entity: ", entity, "repeat2: ",repeat2,   "len2: ", length2,   "codeC:", codeC, "char: ", char)
    return length2, char, repeat2, pcode

def phase_d(serverName, len2, char, repeat2, pcode):
    serverPort = tcp_port
    clientSocket = socket(AF_INET, SOCK_STREAM)
    try:
        clientSocket.connect((serverName, serverPort))
    except:
        print("client socket refused connection")
        return
    print("connected to tcp port: ", tcp_port)
    clientSocket.settimeout(3)

    
 
    while len2 % 4 != 0:
        len2 += 1
    
    c_temp = [char] * len2

    char_filled_data = bytearray(c_temp)

    print("sending  {} to server for {} times".format(char_filled_data[:8], repeat2))

    for idx in range(repeat2):
        client_data = pack("!IHH{}s".format(len2), len2, 1, pcode, char_filled_data)
        clientSocket.send(client_data)

    
    server_data = clientSocket.recv(2048)

    server_data = clientSocket.recv(1024)
    data_length, entity, pcode, codeD = unpack('!IHHI', server_data)


    print("Received from server: data_len: {}  pcode: {}  entity: {e}  codeD: {}".format(data_length, pcode, entity, codeD))
    




print("------------ Starting Stage A  ------------")
codeA, repeat, lenn, udp_port = phase_a(serverName, serverPort, clientSocket)
print("------------ End of Stage A  ------------")
print()
print("------------ Starting Stage B  ------------")
tcp_port, codeB = phase_b(serverName, udp_port, clientSocket, codeA, repeat, lenn)
print("------------ End of Stage B  ------------")
print()
clientSocket.close()
print("------------ Starting Stage C  ------------")
len2, char, repeat2, pcode = phase_c(serverName, tcp_port, codeB)
print("------------ End of Stage C  ------------")
print()
print("------------ Starting Stage D  ------------")
phase_d(serverName, len2, char, repeat2, pcode)
print("------------ End of Stage D  ------------")

# #incase phase_b fails
# if tcp_port == 0:
#     tcp_port = 2001
# if codeB == 0:
#     codeB = 101

# #PHASE C
# print("------------ Starting Stage C  ------------")
# try:
#     tcp_port, codeB = phase_c(serverName, clientSocket, tcp_port, codeB)
# except:
#     print("Error check code")
# #phase_c(serverName, clientSocket, tcp_port, codeB)
# print("------------ End of Stage C  ------------")

# #PHASE D
# print("------------ Starting Stage D  ------------")
# print("------------ End of Stage D  ------------")


# # lenn =  76 
# # codeA = 99
# # repeat = 10
# # phase_b(serverName, serverPort, clientSocket, codeA, repeat, lenn)