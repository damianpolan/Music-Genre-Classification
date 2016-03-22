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


def standard_deviation(l, mean=None):
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


def avg_around_index(i, c, list):
    """
    Square averages the values around i +/- c

    :param i:
    :param list:
    :return: (average, x) where x is the index which had the highest value
    """

    start_i = i - c
    end_i = i + c # inclusive

    if start_i < 0:
        start_i = 0
    if end_i >= len(list):
        end_i = len(list) - 1

    max_i = start_i
    sum = 0
    for x in range(start_i, end_i + 1):
        sum += list[x] ** 2
        if list[x] >= list[max_i]:
            max_i = x

    return sum / (end_i - start_i + 1), max_i


def squared(ilist):
    """
    Squares each element in the list. Returns a new list.

    isLR -> whether the list has left/right sound data. ie. list is in format [ [l0,r0], ... [ln,rn]]
    """
    new_list = []
    for sample in ilist:
        new_list.append(pow(sample, 2))

    return new_list


def linear_dev(ilist, avg):
    # calculates that average difference of the values in ilist from avg.
    if not avg:  # calculate average if its not already calculated
        avg = average(ilist)

    summ = 0
    for item in ilist:
        summ += abs(item - avg)

    return math.sqrt(float(summ) / (len(ilist) - 1))
