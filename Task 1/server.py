# Import socket module
from html.entities import codepoint2name
from operator import truediv
from socket import * 
import sys # In order to terminate the program
from struct import *
from random import randint
import time

# Assign a port number
serverPort = 12000
serverSocket = socket(AF_INET, SOCK_DGRAM)
#Bind the socket to server address and server port
serverSocket.bind(("", serverPort))

#I was re using server and client a lot so I decided to maek them global vriables
client = 1
server = 2


def verify_data_phaseA(data_length, pcode, entity, message):
	if (data_length % 4 == 0 or entity != client):
		return True
	return True
def phase_a(serverPort, serverSocket):
	#serverSocket.settimeout(3)
	while True:
		
		serverSocket.settimeout(3)
		client_data, clientAddress = serverSocket.recvfrom(1024)
		
		#original_data = unpack('!IHH16s', client_data) #byte data unpacked and in tuple form
		data_length, pcode, entity, message = unpack('!IHH16s', client_data)

		if not verify_data_phaseA(data_length, pcode, entity, message):
			serverSocket.close()
			print("server socket closed. wrong specification for input")
		
		
		#data_length, pcode, entity, message = original_data[0], original_data[1], original_data[2], original_data[3]

		message = message.decode('utf-8')

		#don't forget to strip message of padding
		print("Recieving from the client: ", "data_length: ", data_length, "code: ", pcode, "entity: ", entity, "Data: ", message[:-2])
			
		#data_length, pcode, entity,repeat i, udp_port i, len h, codeA h
		repeat = randint(5, 20)
		udp_port = randint(20000, 30000)
		len = randint(50, 100)
		codeA = randint(100, 400)

		print("Sending to client: ", "data_length: ", data_length, "code: ", pcode, "entity: ", entity, "udp port: ", udp_port, "len: ", len, "codeA: ", codeA)

		server_data = pack('!IHHIIHH', data_length, pcode, server, repeat, udp_port, len, codeA)
		serverSocket.sendto(server_data, clientAddress)

		
		#i'm returning these values because we need them for future phases
		return codeA, repeat, len, udp_port

def verify_data_phaseb(data_length, pcode, entity, packet_id, message, count, length):
	while length % 4 != 0:
		length += 1

	try:
		if (packet_id != count or data_length != (length + 4) or entity != client  or data_length % 4 != 0): 
			return False
		else:
			return True
	
	except:
		return False
	
	return True
def acknowledge_packet_phaseB(client_data, serverSocket, clientAddress):
	#packet_id, data_length, pcode, entity, data
	packet_id = client_data[0]
	data_length = client_data[1]
	pcode = client_data[2]
	entity = client_data[3]
	print("Server: received_packet_id =  {} data_len =  {}  pcode: {}".format(packet_id, data_length, pcode))

	#send back to client acknowledgement data
	try:
		acknowledgement_packet = pack("!IHHI", data_length, pcode, entity, packet_id)
		serverSocket.sendto(acknowledgement_packet, clientAddress)
	except:
		print("Error sending acknowledgement packet")
def phase_b(serverSocket, codeA, repeat, length):
	pcode = codeA
	count = 0

	while True:
		#recieve data from client
		try:
			client_data, clientAddress = serverSocket.recvfrom(1024)
			data_length, pcode, entity, packet_id, message = unpack('!IHHI{}s'.format(length), client_data)
		except:
			tcp_port, codeB = data_for_c()
			print("Problem unpacking data or socket timed out for phase b returning hard coded data tcp_port: {}, codeB: {}".format(tcp_port, codeB))
			return data_for_c()
	

		#verify client data
		if not verify_data_phaseb(data_length, pcode, entity, packet_id, message, count, length):
			serverSocket.close()
			print("Incorrect parameters")

		valid = True
		if valid:
			print("Server: Sending Ack packet to client for packet id: ", count)
			acknowledge_packet_phaseB(client_data, serverSocket, clientAddress)
			count += 1

		#stop when count as much as repeat
		if count == repeat:
			break

	#step B-2
	tcp_port = randint(20000, 30000)
	codeB = randint(100, 400)
	data_length = 8
	server_data = pack('!IHHII', data_length, pcode, tcp_port, codeB)
	serverSocket.sendto(server_data, clientAddress)
	print ("------------- B2: sending tcp_port: {} codeB: {}".format(tcp_port, codeB))
	return tcp_port, codeB
def data_for_c():
	#return tcp_port, codeB
	return 25200, 190

def phase_c(tcp_port, codeB):
	pcode = codeB
	
	serverSocket = socket(AF_INET, SOCK_STREAM)
	serverPort = tcp_port
	serverSocket.bind(("", serverPort))
	serverSocket.listen(5)
	
	while True:
		print('The server is ready to receive. Port: ', serverPort)
		connectionSocket, addr = serverSocket.accept()

	
	# sentence = connectionSocket.recv(1024).decode()
	# capitalizedSentence = sentence.upper()
	# connectionSocket.send(capitalizedSentence.encode())
	# connectionSocket.close()

		repeat2 = randint(5,20)
		length = randint(50, 100)
		codeC = randint(100, 400)
		char = 'w'
		char = char.encode('utf-8')
		#4x3 + 1 for char
		data_length = 13
		server_data = pack('IHHIIIc', data_length, pcode, server, repeat2, length, codeC, char)
		print('Server Sending to the client:  data_length: {} code: {}  entity: 2  repeat2: {}  len2: {} codeC:  {}'.format(data_length, pcode, repeat2, length, codeC))
		connectionSocket.send(server_data)
		connectionSocket.close()
		return repeat2, length, codeC, char

def verify_d(len2, entity, pcode):
	if (entity != 1):
		return False
	
	return True

def phase_d(tcp_port, repeat2, length, pcode, char):
	serverSocket = socket(AF_INET, SOCK_STREAM)
	serverPort = tcp_port
	try:
		serverSocket.bind(("", serverPort))
	
	except:
		print("Error: Server Socket in use")
		return

	
	serverSocket.listen(5)

	print("Starting to Receive packets from client")
	
	while length % 4 != 0:
		length += 1
	
	connectionSocket, addr = serverSocket.accept()

	for idx in range(repeat2):
		client_data = connectionSocket.recv(1024)
		len2, entity, pcode, char_filled_data = unpack("!IHH{}s".format(len2), client_data)
		if not verify_d(len2, entity, pcode):
			print("invalid packets recived")
		print(" i =  {} data_len:  {} pcode:  {} entity:  {} data:  {}".format(idx, len2, pcode, entity, char_filled_data))

	

	data_length = 4
	codeD = randint(100, 400)
	server_data = ('!IHHI', data_length, 2, pcode, codeD)
	connectionSocket.send(server_data)
	 
print("------------ Starting Stage A  ------------")
codeA, repeat, lenn, udp_port = phase_a(serverPort, serverSocket)
print("------------ End of Stage A  ------------")
serverSocket.close()
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(("", udp_port)) # use new udp port
serverSocket.settimeout(5) # keeps waiting forever move on if not working
print()
print("------------ Starting Stage B  ------------")
tcp_port, codeB = phase_b(serverSocket, codeA, repeat, lenn)
print("------------ End of Stage B  ------------")
serverSocket.close()
time.sleep(3)
print()
print("------------ Starting Stage C  ------------")
repeat2, len2, codeC, char = phase_c(tcp_port, codeB)
print("------------ End of Stage C  ------------")
serverSocket.close()
print()
print("------------ Starting Stage D  ------------")
phase_d(tcp_port, repeat2, len2, codeC, char)
print("------------ End of Stage D  ------------")


########################################################

# #incase phase_b fails
# if tcp_port == 0:
#     tcp_port = 2001
# if codeB == 0:
#     codeB = 101

# #PHASE C
# print("------------ Starting Stage C  ------------")
# try:
#     repeat2, length2, codeC, char = phase_c(serverSocket, tcp_port, codeB)
# except:
#     print("Error check code")
# #repeat2, length2, codeC, char = phase_c(serverSocket, tcp_port, codeB)
# print("------------ End of Stage C  ------------")

# #PHASE D
# print("------------ Starting Stage D  ------------")
# print("------------ End of Stage D  ------------")

# ###########


serverSocket.close()  
sys.exit()