#!/bin/python3

import math
import os
import random
import re
import sys


if __name__ == '__main__':
    n = int(input().strip())
    if (n % 2 == 1) or (n % 2 == 0 and n in range(5, 21)):
        print("Weird")
    elif (n % 2 == 0) or (n in range(1, 6) or (n > 20)):
        print("Not Weird")
        