import random
from treelib import Node, Tree

class NodeData(object):

    def __init__(self, rcost, size, inCache):
        self.reCost = rcost   # corresponds to r in equation
        self.size = size      # corresponds to c in equation
        self.inCache = inCache  # corresponds to x in equation
        self.y = 0              # corresponds to y in equation
        self.marked = False
        self.numChildren = 0

    def reset(self):
        self.inCache = False
        self.y = 0
        self.itBit = 0
        self.numChildren = 0

    #def __getattr__(self, item):

class ExecutionTree(Tree):

    TYPE = ['FIXED','BRANCH','KARY']
    CCOST = 100
    STORAGE = 100
    totalccost = 0
    def __init__(self):
        self.tree = Tree()

    def computeCost(self,height):
        ccost = self.CCOST / height
        ccost = random.randrange(0 if (ccost-10) < 0 else int(ccost-10),int(ccost+10))
        if ccost > 0: return ccost
        else: return 0

    def storageCost(self,height):
        scost = self.STORAGE * height
        scost =  random.randrange(0 if (scost - 10) < 0 else int(scost -10), int(scost + 10))
        if scost > 0: return scost
        else: return 0

    def createTree(self, k, height,type):

        if (type == self.TYPE[0]):
            self.tree.create_node("A", "a", data=NodeData(1, 10, False))  # root node\n",
            self.tree.create_node("B", "b", parent="a", data=NodeData(1, 10, False))
            self.tree.create_node("C", "c", parent="b", data=NodeData(1, 10, False))
            self.tree.create_node("D", "d", parent="b", data=NodeData(1, 10, False))
            self.tree.create_node("E", "e", parent="d", data=NodeData(1, 10, False))
            self.tree.create_node("F", "f", parent="d", data=NodeData(1, 10, False))
            self.tree.create_node("G", "g", parent="f", data=NodeData(1, 10, False))
            self.tree.create_node("H", "h", parent="f", data=NodeData(1, 10, False))
            self.tree.create_node("I", "i", parent="f", data=NodeData(1, 10, False))
            self.tree.create_node("J", "j", parent="h", data=NodeData(1, 10, False))
            self.tree.create_node("K", "k", parent="j", data=NodeData(1, 10, False))
            self.tree.create_node("L", "l", parent="k", data=NodeData(1, 10, False))
            self.tree.create_node("M", "m", parent="j", data=NodeData(1, 10, False))
            self.tree.create_node("N", "n", parent="i", data=NodeData(1, 10, False))
            self.tree.create_node("O", "o", parent="n", data=NodeData(1, 10, False))
            return self
        elif (type == self.TYPE[1]):
            currheight = 0
            nodelist = []
            #nodelist = random.sample(range(int((pow(k,(height+1))-1)/(k-1))),numbranchnodes)
            #nodelist.sort()
            #print(nodelist)
            self.tree.create_node("N0", "n0", data=NodeData(1, 10, False))
            nodelist.append(0)
            #print(nodelist)
            for i in range(1,int((pow(k,(height+1))-1)/(k-1))):
                if i < int((pow(k, (currheight + 1)) - 1) / (k - 1)):
                    currheight = currheight
                else:
                    currheight = currheight + 1
                if (random.randint(0, 1)):
                    if ((int((i - 1) / k) in nodelist)):
                        self.tree.create_node("N" + str(i), "n" + str(i), parent="n" + str(int((i - 1) / k)),
                                              data=NodeData(self.computeCost(currheight), self.storageCost(currheight), False))
                        #self.tree.create_node("N" + str(i), "n" + str(i), parent="n" + str(int((i - 1) / k)),
                        #                      data = NodeData(1, 10, False))
                        nodelist.append(i)
                    else:
                        continue
            return self
        else:
            currheight = 0
            self.tree.create_node("N0", "n0", data=NodeData(1, 1, False))
            currheight = currheight + 1
            for i in range(1,int((pow(k,(height+1))-1)/(k-1))):
                if i < int((pow(k,(currheight+1))-1)/(k-1)):
                    currheight = currheight
                else:
                    currheight = currheight + 1
                #print(i, str(int((i-1)/k)))
                self.tree.create_node("N" + str(i), "n" + str(i), parent="n" + str(int((i-1)/k)),
                                    data=NodeData(1, 1, False))
            return self

            # for i in range(0,depth):
            #     for j in range(0,k):
            #         self.tree.create_node("N"+str(cnt),"n"+str(cnt),parent="n"+str((i)),data=NodeData(1,10,False))
            #         cnt = cnt + 1
            # return self

    def reset(self):
        for node in self.tree.all_nodes():
            node.data.reset()

