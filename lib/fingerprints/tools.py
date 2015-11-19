import struct

def packSongArray(data):
    """
        packs a song array with struct.pack.

        The song array must be an array where each element of the array is another array of two elements. i.e [ [1,2],[3,4],[5,6] ]


        Uses packed format: 
        <length>:::<packed data>
            ** length must be stored for unpacking
    """
    left = []
    right = []
    for pair in data:
        left.append(pair[0])
        right.append(pair[1])

    left.extend(right)
    packed = struct.pack("%sf" % len(left), *left)

    return packed


def unpackSongArray(packed):
    """
    unpacks packed data from packSongArray()
    """
    length = len(packed) / 4 # (4 is length of float)
    unpacked = struct.unpack("%sf" % length, packed)

    data = []

    realLength = int(length) / 2
    for i in range(realLength):
        data.append([unpacked[i], unpacked[i + realLength]])

    return data



def chunks(l, n):
    """Yield successive n-sized chunks from l.
    From: http://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks-in-python
    """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]