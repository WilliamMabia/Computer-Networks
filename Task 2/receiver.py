from common import *

class receiver:
    
    def isCorrupted(self, packet):
        ''' Checks if a received packet has been corrupted during transmission.
        Return true if computed checksum is different than packet checksum.'''

        if (checksumCalc(str(packet.seqNum) + packet.payload + str(packet.ackNum))!= packet.checksum):
            return True

        else:
            return False
   
    def isDuplicate(self, packet):
        '''checks if packet sequence number is the same as expected sequence number'''

        if (packet.seqNum != self.expectedSeqNum):
            return True
        else:
            return False

        return
    
    def getNextExpectedSeqNum(self):
        '''The expected sequence numbers are 0 or 1'''

        next_exp_seq = (self.expectedSeqNum + 1) % 2
 
        return next_exp_seq
    
    
    def __init__(self, entityName, ns):
        self.entity = entityName
        self.networkSimulator = ns
        print("Initializing receiver: B: "+str(self.entity))


    def init(self):
        '''initialize expected sequence number'''
        self.expectedSeqNum = 0
        self.ack_dup = None
        return
         

    def input(self, packet):
        '''This method will be called whenever a packet sent 
        from the sender arrives at the receiver. If the received
        packet is corrupted or duplicate, it sends a packet where
        the ack number is the sequence number of the  last correctly
        received packet. Since there is only 0 and 1 sequence numbers,
        you can use the sequence number that is not expected.
        
        If packet is OK (not a duplicate or corrupted), deliver it to the
        application layer and send an acknowledgement to the sender
        '''

        if(not self.isCorrupted(packet) and not self.isDuplicate(packet)):
            self.networkSimulator.deliverData(self.entity, packet.payload) #deliver
            self.networkSimulator.udtSend(self.entity, packet) #send

            self.expectedSeqNum = self.getNextExpectedSeqNum()
            self.ack_dup = packet
            

        elif(self.ack_dup is not None):
            #If the received packet is corrupted or duplicate it sends a packet
            self.networkSimulator.udtSend(self.entity, self.ack_dup)

        return
