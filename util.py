# a simple DFS with some cost checking

def DFSv1(node,extree,cache):
    #if node.is_root():
        # First print the data of node
    if (node.data.inCache == False):
        extree.totalccost = extree.totalccost + node.data.reCost
        if (cache.hasSpace(node.data.size)):
            node.data.inCache = True

    #print(node.identifier),
    cnt = 0
    for child in extree.tree.is_branch(node.identifier):
        cnt = cnt +1
        #extree.totalccost = extree.totalccost + node.data.reCost
        DFSv1(extree.tree.get_node(child),extree,cache)
        print("Cost: " + str(extree.totalccost))
        extree.tree.get_node(child)
    node.data.numChildren = cnt
    return extree.totalccost

def paths(node,tree):
  #Helper function
  #receives a tree and
  #returns all paths that have this node as root and all other paths

  if node is None:
    return ([], [])
  else: #tree is a node
    root = node.identifier
    rooted_paths = [[root]]
    unrooted_paths = []
    for child in tree.children(node.identifier):
        (useable, unuseable) = paths(child,tree)
        for path in useable:
            unrooted_paths.append(path)
            rooted_paths.append([root]+path)
        for path in unuseable:
            unrooted_paths.append(path)
    return (rooted_paths, unrooted_paths)

def combinations(items):
    return (set(compress(items,mask)) for mask in product(*[[0,1]]*len(items)))

#def enumeratepaths(tree):

# take each path of the tree and see if the size constraint is met with object being in cache
# generate
# def configurations(tree,size):
