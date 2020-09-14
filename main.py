# The objective of this program is to store nodes of a tree in a cache
# such that the time to compute the graph is minimized.
# Input is a tree with nodes labels of compute cost (cost to compute the node)
# and storage cost (cost of storing a NodeData).

import ExecutionTree as exT
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

    for child in extree.children(node.identifier):
        GreedyDFScomputeCost(child,extree)

    if (node.is_leaf()):
        node.data.y = 1
    else:
        # compute y value for all children
        node.data.y = 0  # reinitialize for repeated runs
        for (child) in extree.children(node.identifier):
            node.data.y = node.data.y + (1 + (child.data.y-1) * (1 - (1 if (child.data.x_in_cache) else 0)))

    extree.totalccost = extree.totalccost + node.data.r_cost * (node.data.y - 1) * (1 - (1 if (node.data.x_in_cache) else 0))
    #print("id:" + node.identifier +  " y: " + str(node.data.y) + " cost " + str(extree.totalccost))
    return extree.totalccost

def main():
    cCost = 0
    cache = Cache(20)

    # create a tree
    # possible types: FIXED, BRANCH, KARY
    # ex_tree = exT.create_tree('FIXED')
    # ex_tree = exT.create_tree('BRANCH', 7, 5)
    ex_tree = exT.create_tree('KARY', 2, 2)

    # ex_tree.show()

    # run algorithms
    # possible types: optimal, greedy1, greedy2

    # Algo: OPTIMAL
    #optimal(ex_tree)
    # (rp,np) = paths(ex_tree.get_node("n0"),ex_tree)
    # print(rp)
    # print(np)

    #ALGO: GREEDY1
    nodeinCache = 0



    paths = ex_tree.paths_to_leaves()
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
                 budget = budget + ex_tree.get_node(node).data.c_size * ex_tree.get_node(node).data.x_in_cache

             if (budget >= cache.cSize):
                 inFeasiblePath = True
                 break;
         if inFeasiblePath:
             return False #not a candidate for caching
         return True


    while True:
         minComputeCost = 100000
         candidates = []
         for i in ex_tree.all_nodes():
             if i.is_leaf() or i.data.x_in_cache == True:
                 continue
             else:
                 if (isCandidateforCaching(i.identifier)):
                    candidates.append(i.identifier)

         #for i in range(ex_tree.size()):
         #   if ex_tree.get_node("n"+str(i)).is_leaf() or ex_tree.get_node("n" + str(i)).data.x_in_cache == True:
         #       continue
         #   else:
         #       if (isCandidateforCaching(i)):
         #           candidates.append(i)
         print(candidates)

         if not candidates:
            break

         for i in candidates:
            #ignore leaves; they will never be in cache
            ex_tree.totalccost = 0
            if ex_tree.get_node(i).is_leaf() or ex_tree.get_node(i).data.x_in_cache == True:
                 continue
            else:
                 ex_tree.get_node(i).data.x_in_cache = True   #set the node to be x_in_cache temporarily
                 cCost = GreedyDFScomputeCost(ex_tree.get_node("n0"), ex_tree)
                 if (cCost < minComputeCost):
                     minComputeCost = cCost
                     mincostNode = i
                 ex_tree.get_node(i).data.x_in_cache = False
            #print("id: n" + str(i) + " ccost: " + str(cCost) + " minCost: " + str(minComputeCost))
         print(" minCost: " + str(minComputeCost) + " mincostnode: " + mincostNode)
    #     #if (cache.hasSpace(ex_tree.get_node(mincostNode).data.c_size)):
    #     cache.insert(ex_tree.get_node(mincostNode).data.c_size)

         ex_tree.get_node(mincostNode).data.x_in_cache = True

       #else:
    #        print("minCost:" + str(minComputeCost))
    #        break


    #cCost = DFSv1(ex_tree.get_node("n0"), ex_tree,cache)
    #print(cCost)



    #ex_tree.show(data_property=lambda x: x.NodeData.numChildren)
    ex_tree.show(data_property='x_in_cache')
    #ex_tree.show()

    #ex_tree.reset()
    #DFScomputeCost(ex_tree.get_node("n0"),ex_tree)
    optimal(ex_tree)

if __name__ == '__main__':
    main()