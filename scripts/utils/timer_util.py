"""Utility functions for displaying progress of a long task over time."""
import sys
import time

start = time.time()

def ping (txts):
    txt = ' '.join([str(t) for t in txts])
    print "[Info    ]>>> " + txt + "..."
    global start
    start = time.time()

def pong ():
    t_spent = int(time.time() - start)
    print "[Timer   ]>>> Done in", t_spent, "secondes."

def displayProgress (index, nbMax, tempo):
    if index % tempo != 0 and index < nbMax-1: return
    sys.stdout.write("\r[Process ]>>> " + str(int(index / float(nbMax) * 100)) + " % done.")
    sys.stdout.flush()
    if index >= nbMax-1: print