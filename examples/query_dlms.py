#!/usr/bin/env python3

from dlms import *

if __name__ == "__main__":
    meter = Dlms("/dev/ttyUSB0")

    values = meter.query()
    print("%16s: %s" % ("identifier", values[0]))
    print("")
    for i in values[1]:
        j = values[1][i]
        if len(j) == 2:
            print("%16s: %s [%s]" % (i, j[0], j[1]))
        else:
            print("%16s: %s" % (i, j[0]))
