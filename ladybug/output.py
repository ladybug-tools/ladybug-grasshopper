"""Collection of methods for dealing with DataTrees in Grasshopper."""
from collections import namedtuple
try:
    from Grasshopper import DataTree
    from Grasshopper.Kernel.Data import GH_Path as Path
    from Grasshopper.Kernel.Types import GH_ObjectWrapper as Goo
except ImportError:
    raise ImportError(
        "Failed to import Grasshopper. Make sure the path is added to sys.path.")
try:
    from System import Object
    from System.Drawing import Color
except ImportError:
    print "Failed to import System."


def flattenDataTree(input):
    """Flatten and clean a grasshopper DataTree.

    Args:
        input: A Grasshopper DataTree.

    Returns:
        allData: All data in DataTree as a flattened list.
        pattern: A dictonary of patterns as namedtuple(path, index of last item
        on this path, path Count). Pattern is useful to unflatten the list back
        to DataTree.
    """
    Pattern = namedtuple('Pattern', 'path index count')
    pattern = dict()
    allData = []
    index = 0  # Global counter for all the data
    for i, path in enumerate(input.Paths):
        count = 0
        data = input.Branch(path)

        for d in data:
            if d is not None:
                count += 1
                index += 1
                allData.append(d)

        pattern[i] = Pattern(path, index, count)

    return allData, pattern


def unflattenToDataTree(allData, pattern):
    """Create DataTree from a flattrn list based on the pattern.

    Args:
        allData: A flattened list of all data
        pattern: A dictonary of patterns
            Pattern = namedtuple('Pattern', 'path index count')

    Returns:
        dataTree: A Grasshopper DataTree.
    """
    dataTree = DataTree[Object]()
    for branch in xrange(len(pattern)):
        path, index, count = pattern[branch]
        dataTree.AddRange(allData[index - count:index], path)

    return dataTree


def dataTreeToList(input):
    """Convert a grasshopper DataTree to list.

    Args:
        input: A Grasshopper DataTree.

    Returns:
        listData: A list of namedtuples (path, dataList)
    """
    allData = range(len(input.Paths))
    Pattern = namedtuple('Pattern', 'path list')

    for i, path in enumerate(input.Paths):
        data = input.Branch(path)
        branch = Pattern(path, [])

        for d in data:
            if d is not None:
                branch.list.append(d)

        allData[i] = branch

    return allData


def listToTree(input, rootCount=0):
    """Transforms nestings of lists or tuples to a Grasshopper DataTree"""

    def proc(input, tree, track):
        for i, item in enumerate(input):
            if hasattr(item, '__iter__'):  # if list or tuple
                track.append(i)
                proc(item, tree, track)
                track.pop()
            else:
                tree.Add(item, Path(*track))

    if input is not None:
        t = DataTree[object]()
        proc(input, t, [rootCount])
        return t


def wrap(input):
    """Wrap honeybee objects as Grasshopper generic objects.

    Pass output lists through this object if the items are custom types.
    Args:
        input: A list of values to be wrapped as GOO.
    """
    if not input:
        return input
    try:
        return (Goo(i) for i in input)
    except Exception as e:
        raise ValueError('Failed to wrap {}:\n{}.'.format(input, e))


def colorTocolor(colors):
    """Convert a ladybug color into Dynamo color."""
    if not hasattr(colors, '__iter__'):
        colors = (colors,)
    try:
        return tuple(Color.FromArgb(255, col.r, col.g, col.b) for col in colors)
    except AttributeError as e:
        raise AttributeError('Inputs must be of type of Color:\n{}'.format(e))
