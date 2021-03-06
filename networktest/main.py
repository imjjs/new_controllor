import sys

import subprocess
import multiprocessing

import test
import time
import random
import config
import os

CoreNumber = multiprocessing.cpu_count()

TestPeriod = 36000
testRange = (0, 30)
stepLength = 1
EPS = 0.1

dim = 16

def mytestWarp(tup):
    para = tup[1]
    idx = tup[2]
    name = tup[3]
    para[idx] = tup[0]
    speed = 0.0
    for map in config.maps:
        while True:
            try:
                speed += float(subprocess.check_output(["python", "test.py", str(para).replace(' ',''), map, name]))#, stdout= DEVNULL, stderr = DEVNULL)
            except subprocess.CalledProcessError as grepexc:
                print "error code", grepexc.returncode, grepexc.output
                continue
            break
	print "speed, len: ", speed, len(config.maps)
    return (float(speed)/len(config.maps), int(tup[0]))


def start_process():
    pass

def find_opt(para, filter, name, iter, secnario):
    direct = secnario + '_' + name + str(iter)
    paraList = list(para)
    try:
        os.makedirs(direct)
    except OSError:
        pass
    count = 0
    # for i in range(dim):
    #    paraList.append(testRange[0])
    meta_param = test.findPhase()
    idx = 0
    mark_opt = False
    optimum = -float('inf')
    while mark_opt == False:
        mark_opt = True
        for idx in range(dim):
            # if not meta_param[idx].controller in config.blue:
            #    continue
            if filter(meta_param[idx]) == False:
                continue
            print idx
            pool = multiprocessing.Pool(processes=CoreNumber,
                                        initializer=start_process)
            inputList = []

            for i in range(testRange[0], testRange[1], stepLength):
                inputList.append((i, paraList, idx, name))

            result = pool.map(mytestWarp, inputList)
            #result = map(mytestWarp, inputList)
            pool.close()
            pool.join()

            f = open(direct + "/intersection" + str(idx) + ".txt", "a")
            for i in result:
                print i[0], i[1]
                f.write(str(i[0]) +','+ str(i[1]) + '\n')

            maxSpeed, maxThreshold = max(result, key=lambda x: x[0])
            f.write("final:" + str(maxSpeed) + ',' + str(maxThreshold) + ',' + str(paraList))

            # minDuration, minWeThreshold, minNsThreshold = min(result, key = lambda x: x[0])
            # f.write("final:"+ str(minDuration) + ',' + str(minWeThreshold) + ',' + str(minNsThreshold))
            if  maxSpeed - optimum > EPS:
                print "current opt:", optimum
                optimum = maxSpeed
                paraList[idx] = maxThreshold
                print "paraList[idx]:", paraList[idx]
                print "maxThreshold:", maxThreshold
                print "mark_opt == False"
                mark_opt = False
            else:
                print "mark unchanged:",mark_opt
            f.flush()
            time.sleep(10)
            print "sleeping at loot--------"
        print "One round, Mark:", mark_opt
    return paraList[:]
if __name__ == '__main__':
    #log.LogTime = time.time()
    #with open('logtime','w') as f:
    #    f.write(str(log.LogTime))

    def isBlue(state):
        return state.controller in config.blue

    def isOrange(state):
        return state.controller in config.orange

    def isRed(state):
        return state.controller in config.red

    def isGloable(state):
        return True

    filters = {
        'red': isRed,
        'orange': isOrange,
        'blue': isBlue,
        'global' : isGloable,
    }

    para = (29, 0, 26, 0, 8, 0, 23, 14, 27, 14, 27, 19, 24, 13, 23, 7)
#(1, 0, 9, 1, 0, 0, 25, 15, 14, 5, 8, 0, 0, 18, 0, 10, 1, 20, 0, 0, 0, 0, 0)
    #para = (3, 0, 9, 1, 0, 0, 10, 7, 0, 6, 5, 5, 0, 12, 0, 20, 0, 14, 0)
    #players = ['blue', 'red']    #, 'orange']
    players = ['global']
    i = 0
    mark_equilibrium = False
    while False == mark_equilibrium:
        mark_equilibrium = True
        for p in players:
            new_para = tuple(find_opt(para, filters[p], p, i, 'rand'))
            if new_para != para:
                mark_equilibrium = False
            para = new_para
        i += 1
