from common import *

class Node:
    def __init__(self, ID, networksimulator, costs):
        self.myID = ID
        self.ns = networksimulator
        num = self.ns.NUM_NODES        
        self.distanceTable = [[0 for i in range(num)] for j in range(num)]
        self.routes = [0 for i in range(num)]
        
        # you implement the rest of constructor

        self.link = [[] for i in range(num)]
        self.node_neighbor = []

        #initialize distance table for each node
        for i in range(num):
            for j in range(num):
                # if we are at row for the current node
                if i == self.myID:
                    self.distanceTable[self.myID][j] = costs[j]
                #if source and destination are same
                elif i == j:
                    self.distanceTable[i][j] = 0
                #non existent connections
                else:
                    self.distanceTable[i][j] = self.ns.INFINITY

        for i in range(self.ns.NUM_NODES):
            if self.distanceTable[self.myID][i] == self.ns.INFINITY:
                self.link[i] = [i, False]
            else:
                #init link to neighbor nodes
                self.link[i] = [i, True]
                #this should init routes list
                self.routes[i] = i  

                
        # send distance to all the neighbours
        for i in self.link:
            if i[0] != self.myID and i[1] is True:
                pkt = RTPacket(self.myID, i[0], costs)
                self.ns.tolayer2(pkt)
                

    def recvUpdate(self, pkt):
        
        self.distanceTable[pkt.sourceid] = pkt.mincosts
        
        # you implement the rest of it  

        is_changed = 0

        for router in range(self.ns.NUM_NODES):
            #deal with non existants
            if self.distanceTable[pkt.sourceid][router] == self.ns.INFINITY:
                continue

            # how much it costs to go to temp using router path 
            cost = self.distanceTable[pkt.sourceid][router] + self.distanceTable[self.myID][pkt.sourceid] 

            #if cost is the cheaper path then use it
            if self.link[pkt.sourceid][1] and cost < self.distanceTable[self.myID][router]:
                self.distanceTable[self.myID][router] = cost
                #add next hop for node to router
                self.routes[router] = self.routes[pkt.sourceid]
                is_changed = 1

        # if changed send updated distance to all the neighbours
        if is_changed == 1:
            for i in self.link:
                if i[0] != self.myID and i[1] is True:
                    pkt = RTPacket(self.myID, i[0], self.distanceTable[self.myID])
                    self.ns.tolayer2(pkt)
          
        return 

    
    def printdt(self):
        print("   D"+str(self.myID)+" |  ", end="")
        for i in range(self.ns.NUM_NODES):
            print("{:3d}   ".format(i), end="")
        print()
        print("  ----|-", end="")
        for i in range(self.ns.NUM_NODES):            
            print("------", end="")
        print()    
        for i in range(self.ns.NUM_NODES):
            print("     {}|  ".format(i), end="" )
            
            for j in range(self.ns.NUM_NODES):
                print("{:3d}   ".format(self.distanceTable[i][j]), end="" )
            print()            
        print()
        
