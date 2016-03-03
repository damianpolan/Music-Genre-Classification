import math
import sys

import detectbeat_1f as dbeat


#############################################
#   METHOD 2:
#   Find the BPM which hits the most spikes and misses the least
#############################################


# non_zero_spikes = [e for e in energy_spikes if e >= 0.01 ]

# pick a period
#period =

# sum the distances of the closest peak
# if the sum is close to 0, we dont need to shift
# if the sum is not close to 0, we need to shift
# unless we have a large SD
# We want to reduce the SD
# local maximum search for (Sum of intersecting weights / SD)


def main(argv):

    knownperiod = 3
    beatpattern = [0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1]

    THRESHOLD = 1

    variations = []
    coverages = [] # number of beats hit
    periods = range(1, 10)

    for period in periods:
        differences = []
        coverage = 0
        # sum all distances to closest 1's
        for beatIndex in range (0, len(beatpattern), period):
            # beat -> index of a predicted beat
            for level in range(beatIndex, len(beatpattern)):
                if beatpattern[level] >= THRESHOLD:
                    differences.append(level - beatIndex)
                    hit_count += 1
                    break


        hit_counts.append(hit_count)
        variation = dbeat.standard_dev(differences, dbeat.average(differences))
        variations.append(variation)

    print periods
    print hit_counts
    print variations



if __name__ == "__main__":
    main(sys.argv[1:])
