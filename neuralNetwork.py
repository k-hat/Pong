import math
import random
#from array import array  # used for deprecated function
PI = math.pi

random.seed()

# Define the game states
INIT = 0
P2HIT = 1
P1HIT = 2
P2WIN = 3
P1WIN = 4

# Define directions for key presses
LEFT = -1
RIGHT = 1

verbose = False
displayNetwork = False


# The ball and paddles' x coordinates are mapped to a new set of x coordinates that are less granular.
# By reducing the total x coordinates, the neural network size is reduced.  
# All coordinates used in the neuralNetwork class are the new x-coordinates.

# These variables define the granularity of the new x coordinates
BALLDIV = 2
PADDIV = 15

# New bounds for the game space defined in the new coordinates.
minXB = int(60/BALLDIV)
maxXB = int(915/BALLDIV)
minXP = int(150/PADDIV)
maxXP = int(825/PADDIV)+1


class NeuralNetwork:
    
    # The Neural Network maps data on the ball's initial angle of bounce, 
    # its initial x-velocity, where the p1 paddle attempted to hit the incoming shot,
    # and the current game state to a value.  This value indicates wether this state
    # has been seen before, and if the previous experience was a miss, hit, or a hit
    # that led to a win.  A higher value indicates a more desirable outcome.
    #
    #
    # network maps (angle, ballX, p1PaddleX_at_hit, ball state) -> value
    #       values: 0 = not seen before 
    #               -1 = miss
    #               1 = hit
    #               >1 = is a win or leads to a win
    #
    network = {}
    # previousState stores that last two states before the current one. With f[0]
    # being one state removed and f[1] being two states removed. 
    previousState = [[0,0,0,0],[0,0,0,0]]
    currentGameHits = []
    angleTable = {}
    angleList = []
    totalGames = 0
    currentFocus = 0
    createNewDecision = True
    #genetic algorithm rate or entropy - see below
    RANDOM_MOVE = 0
    totalRandomMoves = 0
    
    def __init__(self):
        # Pre-calculate a table of angles to reduce repetitive calculations later on.
        for Vx in range(-40,41):
            for Vy in range(-12,13):            
                self.angleTable[(Vx, Vy)] = self.calcAngle(Vx, Vy)
        self.angleList = self.angleTable.values()
        self.angleList = list(set(self.angleList))
    
    # Use the network to provide a decision to player 1 bot, given the paddle position.
    def getDecision(self, p1XPos):  
        
        p1XPos = int(round(p1XPos/PADDIV))

        if self.createNewDecision == True:
            self.createNewDecision = False
            previous = self.previousState[0][3]

            if  previous == P2HIT or previous == INIT:
                
                # If we have no data on this game state, choose at random.
                if self.allZeroCheck(self.previousState[0][0],
                                     self.previousState[0][1],
                                     self.previousState[0][3]):
                    self.currentFocus = random.randint(minXP, maxXP)
                    if verbose: print('chose at random:', self.currentFocus,'\n')
                    self.totalRandomMoves += 1
                
                # Use the network to find the best position.
                else:
                    hits = []
                    maxValue = 0
                    xOfMax = -1
                    for x in range(minXP, maxXP):
                        networkValue = self.network[( self.previousState[0][0],
                                            self.previousState[0][1],
                                            x,
                                            self.previousState[0][3])]                          
                        if  networkValue >= 1:
                            hits.append(x)
                            if networkValue > maxValue:
                                maxValue = networkValue
                                xOfMax = x
                            #if verbose: print(x, networkValue)
                        
                        
                    # Use an optional genetic-algorithm.  This will sometimes 
                    # choose a currently sub-par alternative to potentially find
                    # that it can evolve into a better solution.
                    randomInt = random.randint(1,10)
                    if randomInt <= self.RANDOM_MOVE or maxValue == 1:                    
                        self.currentFocus = hits[ random.randint(0, len(hits)-1)]                        
                    else:
                        self.currentFocus = xOfMax
                    #if verbose: print('chose:', self.currentFocus,'\n')
            else:           
                self.currentFocus = 480/PADDIV
        

        # Tell paddle to go left or right, based on the chosen solution.
        offset = p1XPos - self.currentFocus
        if offset == 0:
            output = 0
        elif offset > 0:                            
            output = -1
        else:
            output = 1

        return output
    
    
    # This evaluates an outcome based on the current state.  It also saves all 
    # hits for the current game. 
    def evaluateDecision(self, ballV, ballX, p1XPos, ballState, previousP1X = 'none'):
        
        self.createNewDecision = True


        if ballState == P1HIT:
            self.currentGameHits.append((   self.previousState[0][0],
                                            self.previousState[0][1],
                                            round(p1XPos/PADDIV),
                                            self.previousState[0][3]))  
            
            # This checks if we have data for the previous state.  If not, we store
            # the new info.
            
            if self.allZeroCheck(self.previousState[0][0],
                                 self.previousState[0][1],
                                 self.previousState[0][3]):                                        
                self.propogateLearning( self.previousState[0][0],
                                        self.previousState[0][1],
                                        self.previousState[0][2],
                                        self.previousState[0][3],
                                        ballX,
                                        P2HIT)      
                
        elif ballState == P1WIN: 
            self.totalGames += 1
            self.propogateLearning( self.previousState[1][0],
                                    self.previousState[1][1],
                                    self.previousState[1][2],
                                    self.previousState[1][3],
                                    self.previousState[0][1]*BALLDIV,
                                    P1WIN)     
            self.currentGameHits.clear()     
            
        elif ballState == P2WIN:
            self.totalGames += 1        
            self.propogateLearning( self.previousState[0][0],
                                    self.previousState[0][1],
                                    self.previousState[0][2],
                                    self.previousState[0][3],
                                    ballX,
                                    P2WIN,
                                    previousP1X)     
            self.currentGameHits.clear()                      
            
        self.previousState[1] = self.previousState[0][:]
        self.previousState[0] = [self.angleTable[ballV[0], 
                                                 ballV[1]], 
                                                 int(round(ballX/BALLDIV)), 
                                                 int(round(p1XPos/PADDIV)), ballState]        
        return

    # Clears the previous two saved states.  Both are set to the input state.
    def clearPreviousStates(self, ballV, ballX, p1XPos, ballState):
        self.createNewDecision = True    
        self.previousState[0] = [self.angleTable[ballV[0], 
                                                 ballV[1]], 
                                                 int(round(ballX/BALLDIV)), 
                                                 int(round(p1XPos/PADDIV)), ballState]
        
        self.previousState[1] = self.previousState[0][:]
        
    # Updates the previous two saved states.
    def updatePreviousStates(self, ballV, ballX, p1XPos, ballState):
        self.createNewDecision = True            
        self.previousState[1] = self.previousState[0][:]
        self.previousState[0] = [self.angleTable[ballV[0], 
                                                 ballV[1]], 
                                                 int(round(ballX/BALLDIV)), 
                                                 int(round(p1XPos/PADDIV)), ballState]                

    # Stores learned information.  It also propogates learned information to all
    # hits that lead to a win.
    def propogateLearning( self, angle, ballX, p1XPos, ballState, 
                           currentBallX, currentState, previousP1X = -1):        
        # ball x in paddle coordinates
        currentBallX = int(round(currentBallX/PADDIV))
      
       
        if currentState == P1HIT or ( currentState == P2WIN and self.allZeroCheck(angle, ballX, ballState) ):            
            if verbose: print('p1 new hit, or new loss state')
            focus = ( max(currentBallX-3, minXP), min(currentBallX+3, maxXP) )
            for x in range(minXP, maxXP): 
                if x < focus[0] or x > focus[1]:
                    self.network[(angle, ballX, x, ballState)] = -1
                else:
                    self.network[(angle, ballX, x, ballState)] = 1
                    
        elif currentState == P1WIN:
            #if verbose: print('p1 win')
            # Update past hits in the network for a win
            hits = len(self.currentGameHits)
            if hits > 0:
                for i in range(0, hits):
                    oldValue = self.network[self.currentGameHits[i]]
                    
                    # This equation incentivizes winning faster, and rewards all
                    # hits leading to a win. The winning shot is rewarded the most
                    # while the first shot is rewarded the least.               
                    self.network[self.currentGameHits[i]] = max( oldValue, round(100*(i+1)/hits,2) )
                    
                    #if verbose: print( i, self.currentGameHits[i], oldValue, self.network[self.currentGameHits[i]])
            
        elif currentState == P2WIN:
            if verbose: print('p2 win, update erroneous hit data')
            self.network[(angle, ballX, previousP1X, ballState)] = -1
            
        return
        
    # Creates a network of all 0's
    def createBlankNetwork(self):
        self.network.clear()
        iter = 0
        print('Creating network', end="")
        for a in self.angleList:
            #print(a)        
            for ballX in range(minXB, maxXB):                    
                for paddleXPos in range(minXP, maxXP):
                    for ballState in range(0,2):
                        self.network[(a, ballX, paddleXPos, ballState)] =  0
                        iter += 1
                        if iter%500000 == 0:
                            print('.', end = "")                            
                            #print(iter)                        

        print()                    
        print('Blank network created','\n')            
        return                 
 
    # Writes network to a text file
    def writeNetwork(self, filename):
        print('writing network', end="")
        outputFile = open(filename, 'w')
        outputFile.write( str(self.totalGames) + " games played\n" )
        iter = 0
        value = 0
        for a in self.angleList:
            #print(a) 
            for ballX in range(minXB, maxXB):                    
                for paddleXPos in range(minXP, maxXP):
                    for ballState in range(0,2):
                        value = self.network[(a, ballX, paddleXPos, ballState)]
                        if value == 0:
                            outputFile.write('0\n')
                        else:                        
                            outputFile.write( str(self.network[(a, ballX, paddleXPos, ballState)]) + '\n') 
                        iter += 1
                        if iter%500000 == 0:
                            print('.', end = "")
                            #print(iter)
                            
        print()
        outputFile.close()
        print('Network written to ' + filename + ' with ' + str(self.totalGames) + ' games played','\n' )                          
        return


    # Reads a network from a text file        
    def readNetwork(self, filename):

        self.network.clear()
        
        try:
            with open(filename,'r') as file:
                print('Reading network', end="")        
                firstLine = file.readline()
                weightList = file.readlines()            
                if len(weightList) == 0:
                    print('\n ERROR: INPUT FILE EMPTY \n')
                    return
                    
                firstLineList = firstLine.split()
                self.totalGames = int(firstLineList[0])
        
                iter = 0        
                for a in self.angleList:
                    #print(a) 
                    for ballX in range(minXB, maxXB):                    
                        for paddleXPos in range(minXP, maxXP):
                            for ballState in range(0,2):    
                                self.network[(a, ballX, paddleXPos, ballState)] = float(weightList[iter])
                                iter += 1
                                if iter%500000 == 0:
                                    print('.', end = "")                            
                                    #print(iter)
                      
                print('\nNetwork read from ' + filename,'\n')
        except:
            print('Could not read file: ', filename)
                     
        return       
        

    def getNetwork():    
        return network

        
    # Calculates an angle given a vector
    def calcAngle(self, ballX, ballY):
        #print(ballV)
        angle = 0
        if ballX > 0:
            x = ballX
            y = abs(ballY)
            angle = PI - math.atan(y/x) 
        elif ballX < 0:
            x = -1 * ballX
            y = abs(ballY)
            angle = math.atan(y/x)             
        elif ballX == 0:
            angle = PI/2
        angle = float('%.2f'%angle)
        return angle
    
    # Checks if the value for a given state is zero.  This is checked for all 
    # paddleX values.  If all are zero, then there is no information on this game 
    # state
    def allZeroCheck(self, angle, ballX, ballState):
    
        if(displayNetwork):
            self.printNetworkRow(angle, ballX, ballState)
        
        for x in range(minXP, maxXP):
            networkValue = self.network[angle, ballX, x, ballState]
            if self.network[angle, ballX, x, ballState] != 0: 
                #print('not all zeroes - false')
                return False
        
        #print('all zeroes - true')
        return True
    
    
    def setEntropy(self,input):
        self.RANDOM_MOVE = input
        
    # Displays a row of the network.  Used for diagnostic testing.
    def printNetworkRow(self, angle, ballX, ballState):
        
        output = str(angle) + " " + str(ballX) + " " + str(ballState) + "\n"
        for x in range(minXP, maxXP):
            output += str(int(self.network[angle, ballX, x, ballState])) + " "
    
        print(output)
    
    # Sums all the values of the network to get a rough estimate of the network
    # size.
    def printNetworkSize(self):
        print("Tallying network size", end = '')
        total = 0
        iter = 0
        for a in self.angleList:
            #print(a) 
            for ballX in range(minXB, maxXB):                    
                for paddleXPos in range(minXP, maxXP):
                    for ballState in range(0,2):
                        total += abs(self.network[(a, ballX, paddleXPos, ballState)])
                        iter += 1
                    if iter%500000 == 0:
                            print('.', end = "")   
        print()                
        print("Network size:", float('%.2f'%total),'\n')
 
    # Checks if network has been initialized
    def isNetworkEmpty(self):
        
        if(len(self.network) == 0):
            return True
        else:
            return False
   
    # Deprecated test to store as binary floats vs a text file
    # def writeNetworkFloats(self, filename):
    #     print('Writing network (floats)', end="")
    #     outputFile = open(filename, 'wb')
    #
    #     networkFloats = array('f', [])
    #     networkFloats.append( float(self.totalGames) )# Games Played
    #     iter = 0
    #     value = 0
    #     for a in self.angleList:
    #         #print(a) 
    #         for ballX in range(minXB, maxXB):                    
    #             for paddleXPos in range(minXP, maxXP):
    #                 for ballState in range(0,2):
    #                     value = self.network[(a, ballX, paddleXPos, ballState)]
    #                     networkFloats.append(float(value))
    #                     iter += 1
    #                     if iter%500000 == 0:
    #                         print('.', end = "")                            
    #
    #     print()
    #     networkFloats.tofile(outputFile)
    #     outputFile.close()
    #     print('Network written to ' + filename + ' with ' + str(self.totalGames) + ' games played','\n' )                          
    #     return        
        