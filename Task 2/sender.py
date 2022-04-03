from common import *
import struct

class sender:
    RTT = 20
    
    def isCorrupted (self, packet):
        '''Checks if a received packet (acknowledgement) has been corrupted
        during transmission.
        Return true if computed checksum is different than packet checksum.
        '''
        if (checksumCalc(str(packet.seqNum) + packet.payload + str(packet.ackNum))!= packet.checksum):
            return True

        else:
            return False

        return

    def isDuplicate(self, packet):
        '''checks if an acknowledgement packet is duplicate or not
        similar to the corresponding function in receiver side
        '''

        if (packet.seqNum != self.seqNum):
            return True
        else:
            return False

        return
 
    def getNextSeqNum(self):
        '''generate the next sequence number to be used.
        '''

        next_seq = (self.seqNum + 1) % 2
 
        return next_seq

    def __init__(self, entityName, ns):
        self.entity = entityName
        self.networkSimulator = ns
        print("Initializing sender: A: "+str(self.entity))

    def init(self):
        '''initialize the sequence number and the packet in transit.
        Initially there is no packet is transit and it should be set to None
        '''
        self.packetInTransit = None
        self.seqNum = 0
        
        return

    def timerInterrupt(self):
        '''This function implements what the sender does in case of timer
        interrupt event.
        This function sends the packet again, restarts the time, and sets
        the timeout to be twice the RTT.
        You never call this function. It is called by the simulator.
        '''

        newTimeout = 2 * self.RTT
        self.networkSimulator.startTimer(self.entity, newTimeout)
        self.networkSimulator.udtSend(self.entity, self.packetInTransit)
        
        return


    def output(self, message):
        '''prepare a packet and send the packet through the network layer
        by calling calling utdSend.
        It also start the timer.
        It must ignore the message if there is one packet in transit
        '''

        #packet = struct.pack(f'!IHH{length2}s', length2, pcode, CLIENT, data)
        # data = "message"
        # length = len(data.encode())
        # packet = struct.pack(f'!{length}s', data)
        # self.networkSimulator.udtSend(self.entity, A, packet)

        #if no packets currently in transit
        if(self.packetInTransit is None):
            checksum = checksumCalc(message.data  + str(self.seqNum) + str(self.seqNum))
            packet = Packet(self.seqNum, self.seqNum, checksum, message.data)

            self.packetInTransit = packet

            self.networkSimulator.startTimer(self.entity, self.RTT)
            self.networkSimulator.udtSend(self.entity, packet)

        return



        return
 
    
    def input(self, packet):

        '''If the acknowlegement packet isn't corrupted or duplicate, 
        transmission is complete. Therefore, indicate there is no packet
        in transition.
        The timer should be stopped, and sequence number  should be updated.

        In the case of duplicate or corrupt acknowlegement packet, it does 
        not do anything and the packet will be sent again since the
        timer will be expired and timerInterrupt will be called by the simulator.
        '''

        #first check if the packet is not corrupted and not a duplicate
        if(not self.isCorrupted(packet) and not self.isDuplicate(packet)):
            self.networkSimulator.stopTimer(self.entity) #stop timer
            self.seqNum = self.getNextSeqNum() #update sequence number
            self.packetInTransit = None
        #else:
            # In the case of duplicate or corrupt acknowlegement packet, it does not do anything
            #return


        return 
