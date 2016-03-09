import math


def average(l):
    """
    Computes the average of a list of values
    :rtype: object
    :param l:
    :return:
    """
    total = 0
    for item in l:
        total += item

    return total / float(len(l))


def standard_deviation(l, mean):
    """
    Computes the standard deviation (SD) of a list of values.
    :param l: the values to compute the SD of.
    :param mean: (optional) the mean value to use. Computed if not provided
    :return: the SD as a float
    """
    if type(l) is not list:
        raise str("Invalid input.")

    n = len(l)
    if n == 0:
        return 0

    if not mean:
        mean = average(l)

    total = 0
    for v in l:
        total += math.pow(v - mean, 2)

    sd = math.sqrt(total / float(n))
    return sd



