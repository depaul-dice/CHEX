# The objective of this program is to store nodes of a tree in a cache
# such that the time to compute the graph is minimized.
# Input is a tree with nodes labels of compute cost (cost to compute the node)
# and storage cost (cost of storing a NodeData).

import ExecutionTree as exT
from ExecutionTree import Node
from itertools import compress, product
from model import DFScomputeCost, optimal
computeCost = 0

class Cache(object):
    cSize = -1
    currentSize = 0
    def __init__(self,cachesize):
        self.cSize = cachesize
        print(self.cSize)


    def insert(self,size):
        self.currentSize = self.currentSize + size

    def hasSpace(self,size):
        if (self.currentSize + size) < self.cSize:
            return True
        return False

def GreedyDFScomputeCost(node,extree):

    for child in extree.tree.children(node.identifier):
        GreedyDFScomputeCost(child,extree)

    if (node.is_leaf()):
        node.data.y = 1
    else:
        # compute y value for all children
        node.data.y = 0  # reinitialize for repeated runs
        for (child) in extree.tree.children(node.identifier):
            node.data.y = node.data.y + (1+ (child.data.y-1)*(1-(1 if (child.data.inCache) else 0)))

    extree.totalccost = extree.totalccost + node.data.reCost*(node.data.y -1)*(1-(1 if (node.data.inCache) else 0))
    #print("id:" + node.identifier +  " y: " + str(node.data.y) + " cost " + str(extree.totalccost))
    return extree.totalccost

def main():
    cCost = 0
    cache = Cache(20)

    #initialize class
    exTree = exT.ExecutionTree()

    # create a tree
    # possible types: KARY, BRANCH, FIXED
    exTree = exTree.createTree(7,5,'BRANCH')
    #exTree = exTree.createTree(3, 7, 'KARY')
    #exTree.tree.show()
    # run algorithms
    # possible types: optimal, greedy1, greedy2

    # Algo: OPTIMAL
    #optimal(exTree)
    # (rp,np) = paths(exTree.tree.get_node("n0"),exTree.tree)
    # print(rp)
    # print(np)

    #ALGO: GREEDY1
    nodeinCache = 0



    paths = exTree.tree.paths_to_leaves()
    #print(paths)

    def filterPaths(i,paths):
        pathswithnode = []
        for path in paths:
            if ("n"+str(i)) in path:
                pathswithnode.append(path)
        return pathswithnode

    def isCandidateforCaching(i):
         pathswithnode = filterPaths(i,paths)
         inFeasiblePath = False
         for path in pathswithnode:
             budget = 0
             for node in path:
                 budget = budget + exTree.tree.get_node(node).data.size * exTree.tree.get_node(node).data.inCache

             if (budget >= cache.cSize):
                 inFeasiblePath = True
                 break;
         if inFeasiblePath:
             return False #not a candidate for caching
         return True


    while True:
         minComputeCost = 100000
         candidates = []
         for i in exTree.tree.all_nodes():
             if i.is_leaf() or i.data.inCache == True:
                 continue
             else:
                 if (isCandidateforCaching(i.identifier)):
                    candidates.append(i.identifier)

         #for i in range(exTree.tree.size()):
         #   if exTree.tree.get_node("n"+str(i)).is_leaf() or exTree.tree.get_node("n" + str(i)).data.inCache == True:
         #       continue
         #   else:
         #       if (isCandidateforCaching(i)):
         #           candidates.append(i)
         print(candidates)

         if not candidates:
            break

         for i in candidates:
            #ignore leaves; they will never be in cache
            exTree.totalccost = 0
            if exTree.tree.get_node(i).is_leaf() or exTree.tree.get_node(i).data.inCache == True:
                 continue
            else:
                 exTree.tree.get_node(i).data.inCache = True   #set the node to be inCache temporarily
                 cCost = GreedyDFScomputeCost(exTree.tree.get_node("n0"), exTree)
                 if (cCost < minComputeCost):
                     minComputeCost = cCost
                     mincostNode = i
                 exTree.tree.get_node(i).data.inCache = False
            #print("id: n" + str(i) + " ccost: " + str(cCost) + " minCost: " + str(minComputeCost))
         print(" minCost: " + str(minComputeCost) + " mincostnode: " + mincostNode)
    #     #if (cache.hasSpace(exTree.tree.get_node(mincostNode).data.size)):
    #     cache.insert(exTree.tree.get_node(mincostNode).data.size)

         exTree.tree.get_node(mincostNode).data.inCache = True

       #else:
    #        print("minCost:" + str(minComputeCost))
    #        break


    #cCost = DFSv1(exTree.tree.get_node("n0"), exTree,cache)
    #print(cCost)



    #exTree.show(data_property=lambda x: x.NodeData.numChildren)
    exTree.tree.show(data_property='inCache')
    #exTree.tree.show()

    #exTree.reset()
    #DFScomputeCost(exTree.tree.get_node("n0"),exTree)
    #optimal(exTree)

if __name__ == '__main__':
    main()