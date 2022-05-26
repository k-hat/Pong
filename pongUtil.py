import math
import random
import time

random.seed()
startingTime = 0

def startTimer():
    global startingTime
    startingTime = time.time()
    return

# Calculates generic units/ms speed
def calcAverageSpeed( units, unitType):
    global startingTime
    
    if units <= 0:
        return 'UNITS OUT OF RANGE - CANNOT CALCULATE SPEED'
    
    finishTime = time.time()
    totalTime = finishTime - startingTime
    timePerUnit = '%.3f'%((totalTime)/units * 1000)
    
    output = '\n' + 'Total time = ' + str('%.3f'%totalTime) + 's\n' + str(timePerUnit) + 'ms per ' + unitType +'\n'
    
    
    return output


def randomVelocity():
    

    xVel = random.randint(-7, 6)
    yVel = random.randint(-12, 5)
    if xVel >= 0:
        xVel += 1
    if yVel >= -3:
        yVel += 7
    

    #output = [xVel, random.randint(-12, -4) ]
    output = [xVel, random.randint(4, 12) ]
    #output = [xVel, yVel]    
    
    
    return output
    #return [-3, -9]