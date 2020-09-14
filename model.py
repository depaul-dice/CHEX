from __future__ import division

#from msilib import Binary

from pyomo.environ import *
from pyomo.solvers import *
from pyomo.opt import ProblemFormat
from six.moves import cPickle as pickle

from pyomo.core import SymbolMap
from pyomo.opt import (ReaderFactory,
                       ResultsFormat)

#from pyomo.repn.plugins.baron_writer import *

CACHESIZE = 1
import ExecutionTree


def DFScomputeCost(node,extree):

    for child in extree.children(node.identifier):
        DFScomputeCost(child,extree)

    if (node.is_leaf()):
        node.data.y = 1
    else:
        # compute y value for all children
        for (child) in extree.children(node.identifier):
            node.data.y = node.data.y + (1 + (child.data.y-1) * (1 - (1 if (child.data.x_in_cache) else 0)))

    return

def write_nl(model, nl_filename, **kwds):
    """
    Writes a Pyomo model in NL file format and stores
    information about the symbol map that allows it to be
    recovered at a later time for a Pyomo model with
    matching component names.
    """
    symbol_map_filename = nl_filename+".symbol_map.pickle"

    # write the model and obtain the symbol_map
    _, smap_id = model.write(nl_filename,
                             format=ProblemFormat.nl,
                             io_options=kwds)
    symbol_map = model.solutions.symbol_map[smap_id]

    # save a persistent form of the symbol_map (using pickle) by
    # storing the NL file label with a ComponentUID, which is
    # an efficient lookup code for model components (created
    # by John Siirola)
    tmp_buffer = {} # this makes the process faster
    symbol_cuid_pairs = tuple(
        (symbol, ComponentUID(var_weakref(), cuid_buffer=tmp_buffer))
        for symbol, var_weakref in symbol_map.bySymbol.items())
    with open(symbol_map_filename, "wb") as f:
        pickle.dump(symbol_cuid_pairs, f)

    return symbol_map_filename

def read_sol(model, sol_filename, symbol_map_filename, suffixes=[".*"]):
    """
    Reads the solution from the SOL file and generates a
    results object with an appropriate symbol map for
    loading it into the given Pyomo model. By default all
    suffixes found in the NL file will be extracted. This
    can be overridden using the suffixes keyword, which
    should be a list of suffix names or regular expressions
    (or None).
    """
    if suffixes is None:
        suffixes = []

    # parse the SOL file
    with ReaderFactory(ResultsFormat.sol) as reader:
        results = reader(sol_filename, suffixes=suffixes)

    # regenerate the symbol_map for this model
    with open(symbol_map_filename, "rb") as f:
        symbol_cuid_pairs = pickle.load(f)
    symbol_map = SymbolMap()
    symbol_map.addSymbols((cuid.find_component(model), symbol)
                          for symbol, cuid in symbol_cuid_pairs)

    # tag the results object with the symbol_map
    results._smap = symbol_map

    return results

def optimal(extree):
    costsum = 0
    model = AbstractModel()

    model.cachesize = Param(within=NonNegativeReals,initialize=CACHESIZE)

    model.n = Param(within=NonNegativeIntegers,initialize=extree.size())

    model.j = RangeSet(1,len(extree.paths_to_leaves()))


    def path_init(model,j):
        l = extree.paths_to_leaves()
        path = l[j-1]
        return path
    model.path = Param(model.j,within=Any,initialize=path_init)

    #Pyomo Sets are 1-indexed: valid index values for Sets are [1 .. len(Set)]
    # so all indexes have to be subtracted from 1 for extree
    model.I = RangeSet(1,model.n)

    model.one = Param(model.I,within=PositiveIntegers,initialize=1)

    def recost_init(model,i):
        return extree.get_node("n" + str(model.I[i]-1)).data.r_cost
    model.recost = Param(model.I, within=NonNegativeIntegers, initialize=recost_init)

    def storage_init(model,i):
        return extree.get_node("n" + str(model.I[i]-1)).data.c_size
    model.storagecost = Param(model.I, within=NonNegativeIntegers,initialize=storage_init)



    #def Y_init(model,i):
    #    return extree.get_node("n"+str(model.I[i]-1)).data.y
    #model.Y = Param(model.I, within=PositiveIntegers,initialize=Y_init)


    model.Y = Var(model.I,within=PositiveIntegers)

    def X_init(model,i):
        return 0
    model.X = Var(model.I, within=Binary, initialize=X_init)



    def pathconstraint(model,j):
        #print(len(model.path[j]))
        storageinpath = 0
        for k in model.path[j]:
             print(k)
             nodeinpath = int(k[1:])+int(1)
             print(nodeinpath)
        #     #nodeinpath = nodeinpath[1:]
             storageinpath = storageinpath + model.storagecost[nodeinpath] * model.X[nodeinpath]
        return (0 <= storageinpath <= model.cachesize)

    model.storageConstraint = Constraint(model.j,rule=pathconstraint)

    def ycompute(model,i):
        if extree.get_node("n" + str(model.I[i]-1)).is_leaf():
            return (model.Y[i] == 1)
        else:
            node = extree.get_node("n" + str(model.I[i] - 1))
            print(extree.children(node.identifier))
            expr1 = sum(1 + (model.Y[int(child.identifier[1:])+int(1)] - 1) * (1 - model.X[int(child.identifier[1:])+int(1)]) for (child) in extree.children(node.identifier))
            return (model.Y[i] == expr1)

    #node = extree.get_node("n" + str(1 - 1))
    #print(extree.children(node.identifier))
    model.Yconstraint = Constraint(model.I,rule=ycompute)

    extree.show()
    model.construct()
    model.pprint()
    model.totalcost = Objective(expr=sum((model.recost[i]*(model.Y[i]-1)*(1-model.X[i])) for i in range(1,extree.size()+1)), sense=minimize)
    symbol_map_filename = write_nl(model,'instance.nl')

    sol_filename = 'instance.sol'
    results = read_sol(model, sol_filename, symbol_map_filename)
    if results.solver.termination_condition != TerminationCondition.optimal:
        raise RuntimeError("Solver did not terminate with status = optimal")
    model.solutions.load_from(results)
    print("Objective: %s" % (model.X.display()))

    #model.write('instance.nl',)
    #solver = SolverFactory('ipopt')
    #solver.solve(model).write('instance.nl')
    #model.pprint()
    #opt.solve(model)

