import math
import pygame
import pongUtil
import neuralNetwork
import time
import random
pygame.display.SDL_VIDEODRIVER = 'directx'
pygame.init()
PI = 3.141592653
verbose = False

# Define Colors
BLACK    = (   0,   0,   0)
WHITE    = ( 255, 255, 255)
GREEN    = (   0, 255,   0)
RED      = ( 255,   0,   0)
BLUE     = (   0,   0, 255)

# Define game states into 5 categories
INIT = 0
P2HIT = 1
P1HIT = 2
P2WIN = 3
P1WIN = 4


# Creates and runs the pong simulation
def run(network, outFilename, drawGame, maxTime, learningBot):
    
    if (network.isNetworkEmpty()):
        print("Network is uninitialized, cannot run simulation")
        return
    
    global verbose
    outputFile = open(outFilename, 'w')
    startingTime = time.time()
    
    marginWidth = 90
    # gameWidth%15 needs to be 0
    gameWidth = 795
    
    fontSize = 40
    
    draw = drawGame
    useClock = drawGame
    p1Bot = True
    p1LearningBot = learningBot
    p1BotUseNetwork = True
    p2Bot = True
    clockValue = 60
    maxTime = maxTime

    gameLeft = marginWidth
    gameRight = gameWidth + marginWidth
    
    size = (gameWidth + marginWidth*2, gameWidth)
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("Pong Bots")
    clock = pygame.time.Clock()
    # Keypress refresh rate
    pygame.key.set_repeat(15,15)
    
    screenFont = pygame.font.SysFont("Lucida Console", fontSize)
    halfScreenFont = pygame.font.SysFont("Lucida Console", fontSize//2)
    
    if(gameWidth%15 != 0):
        print("ERROR: Game width not divisible by 15")


    # paddle width%15 needs to be 0
    p1RectWidth = 120
    p1RectHeight = 20
    startingIndex = int(gameWidth/15//2*15) - p1RectWidth/2
    p1RectX = marginWidth + startingIndex
    p1RectY = size[1] - 2.5 * p1RectHeight
    p1Rect = pygame.Rect(p1RectX, p1RectY, p1RectWidth, p1RectHeight)
    
    p2RectWidth = 120
    p2RectHeight = 20
    startingIndex = int(gameWidth/15//2*15) - p2RectWidth/2
    p2RectX = marginWidth + startingIndex
    p2RectY = 1.5*p2RectHeight
    p2Rect = pygame.Rect(p2RectX, p2RectY, p2RectWidth, p2RectHeight)
    
    leftWall = pygame.Rect(gameLeft - 5, 0, 5, size[1])
    rightWall = pygame.Rect(gameRight, 0, 5, size[1])
    
    # Surfaces the ball can bounce off of
    bouncers = [p1Rect, p2Rect, leftWall, rightWall]
    
    ballR = 32
    initBallX = size[0]//2 - ballR
    initBallY = size[1]//2 - ballR
    
    # Max Y speed = 12
    initV = pongUtil.randomVelocity()
    ballV = initV[:]
    
    rectList = [ pygame.Rect(initBallX, initBallY, ballR*2, ballR*2),   # Ball
                 bouncers[0],                                           # P1 paddle
                 bouncers[1],                                           # P2 paddle
                 pygame.Rect(gameLeft - 2, 0, 3, size[1]),              # Left Barrier
                 pygame.Rect(gameRight, 0, 3, size[1])]                 # Right Barrier

    # ballMask is a smaller rect used for collision detection
    # ballMask = pygame.Rect(ballX+3, ballY+3, 24, 24)
    ballMask = pygame.Rect(initBallX, initBallY, ballR*2, ballR*2)
    rectListOld = rectList
    
    surfaceList = [ pygame.Surface((ballR*2, ballR*2)),
                    pygame.Surface((p1RectWidth, p1RectHeight)),
                    pygame.Surface((p2RectWidth, p2RectHeight)),
                    pygame.Surface((3, size[1])),
                    pygame.Surface((3, size[1]))]
                                       
    for i in surfaceList:
        i.fill(WHITE)
   
    pygame.draw.circle( surfaceList[0], BLUE, (ballR, ballR) , ballR )   
    pygame.draw.rect( surfaceList[1], RED  , (0,0, p1RectWidth, p1RectHeight ) )
    pygame.draw.rect( surfaceList[2], RED  , (0,0, p2RectWidth, p2RectHeight ) )
    pygame.draw.line( surfaceList[3], BLACK, (1,0) , (1, size[1]), 3 )
    pygame.draw.line( surfaceList[4], BLACK, (1,0) , (1, size[1]), 3 )
     
    
    isMoving = [0, 0]
    testLine = [0,0,25,25]    
    testRect = rectList[0]
    testCircle = [0,0]
    p1Score = 0
    p2Score = 0
    p1Bounces = 0
    p2Bounces = 0
    fitness = 0
    
    paddleBounces = 0
    totalGames = 0
    ballState = INIT
    pongUtil.startTimer()
    network.clearPreviousStates(ballV, 
                                rectList[0].center[0], 
                                rectList[1].center[0], 
                                ballState)
    ballXAtFail = 'Error'
    p1XAtFail = 'Error'
    ballVXAtFail = 'Error'
    previousVX = 'Error'
    redrawBall = False
    recordFailState = True
    maxVX = 0
    
    screenRect = screen.get_rect()
    
    screen.fill(WHITE)
    if not draw:
        screen.blit( screenFont.render('Simulating...', True, BLACK), (0,0) ) 
    
    pygame.display.flip()
    
    collided = [False, False, False, False]
    
    # Inner Function - Moves an object indicated by index the rect list, by a tuple (x,y)
    def moveObject(index, moveBy):
        
        if index == 0:
            ballMask.center = pygame.Rect(ballMask.move(moveBy)).center            

        else:
            
            if rectList[index].right + moveBy[0] > gameRight:
                moveBy = (gameRight - rectList[index].right, 0)
            elif rectList[index].left + moveBy[0] < gameLeft:
                moveBy = (-1*(rectList[index].left - gameLeft), 0)
            
            bouncers[index-1] =  bouncers[index-1].move(moveBy)            
            
            if moveBy[0] > 0:
                isMoving[index-1] = 1
            elif moveBy[0] < 0:
                isMoving[index-1] = -1
            else:
                isMoving[index-1] = 0
         
            
        rectList[index] = rectList[index].move(moveBy)    
        
        return   
    
    # Inner Function - Reset all game variables
    def resetGame():
        nonlocal fitness
        nonlocal p1Bounces
        nonlocal p2Bounces
        nonlocal paddleBounces
        rectList[0].center = (initBallX + ballR, initBallY + ballR)
        ballMask.center = (initBallX +ballR, initBallY + ballR)
        ballV = pongUtil.randomVelocity()
        testRect = rectList[0]
        collided = [False, False, False, False] 
        fitness += p1Bounces
        paddleBounces += p1Bounces + p2Bounces
        p1Bounces = 0
        p2Bounces = 0  
        recordFailState = True
        ballState = INIT
        if p1Bot:
            network.clearPreviousStates(ballV, 
                                        rectList[0].center[0], 
                                        rectList[1].center[0], 
                                        ballState)
    
            
    done = False   
         
    ## Simulation loop ##            
    while not done:
        

        
        rectListOld = [ pygame.Rect(rectList[0]), pygame.Rect(rectList[1]), pygame.Rect(rectList[2]) ]
        for i in range(2):
            isMoving[i] = 0
      
        ## Key capture ##
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_RIGHT:
                    moveObject(1, (15,0) )
                if event.key == pygame.K_LEFT:
                    moveObject(1, (-15,0) )
                if event.key == pygame.K_d:
                    moveObject(2, (15,0) )
                if event.key == pygame.K_a:
                    moveObject(2, (-15,0) )                    
                if event.key == pygame.K_SPACE:
                    resetGame()
                if event.key == pygame.K_c:    # Toggle fast-mode by ignoring clock restriction
                    useClock = not useClock
                if event.key == pygame.K_z:    # Toggle drawing during simulation                
                    useClock = not useClock
                    draw = not draw
                    screen.fill(WHITE)
                    
                    if not draw:
                        screen.blit( screenFont.render('Simulating...', True, BLACK), (0,0) )
                        
                        if totalGames > 0:
                            
                            screen.blit( screenFont.render(
                                'Player 1: '+ str(p1Score)+ '  ' + str(round(p1Score/totalGames*100,1))+'%', True, BLUE), (0,50) ) 
                            
                            screen.blit( screenFont.render(
                                'Player 2: '+ str(p2Score)+ '  ' + str(round(p2Score/totalGames*100,1))+'%', True, BLUE), (0,100) )                         
                        
                        pygame.display.flip()
                        
                if event.key == pygame.K_ESCAPE:  
                    done = True
                    
        ## Game logic ##
        
        # Reset an infinite game
        if p1Bounces > 5000:
            resetGame()
        
        if not rectList[0].colliderect(screenRect): # Ball is off-screen
            
            if(rectList[0].center[1] > size[1]): # p2 win
                p2Score += 1
            
                if p1Bot and p1LearningBot:
                    network.evaluateDecision(ballV, 
                                             ballXAtFail, 
                                             rectList[1].center[0], 
                                             P2WIN, 
                                             p1XAtFail)                

            else:                                # p1 win
                p1Score += 1
                fitness += 100
                
                if p1Bot and p1LearningBot:
                    network.evaluateDecision(ballV, 
                                             rectList[0].center[0], 
                                             rectList[1].center[0], 
                                             P1WIN)
            
            outputFile.write(str(p1Bounces) + " " + str(p2Bounces) +"\n")
            # account for ball passing paddle without bouncing
            fitness += p1Bounces
            paddleBounces += p1Bounces + p2Bounces + 1
            p1Bounces = 0
            p2Bounces = 0
            totalGames += 1
            ballState = INIT
            if(totalGames%500 == 0):
                print('Games Played = ' + str(totalGames) )
                if not draw:
                    screen.fill(WHITE)
                    screen.blit( screenFont.render(
                        'Simulating...', True, BLACK), (0,0) ) 
                    
                    screen.blit( screenFont.render(
                        'Player 1: '+ str(p1Score)+ '  ' + str(round(p1Score/totalGames*100,1))+'%', True, BLUE), (0,50) ) 
                    
                    screen.blit( screenFont.render(
                        'Player 2: '+ str(p2Score)+ '  ' + str(round(p2Score/totalGames*100,1))+'%', True, BLUE), (0,100) ) 
                    pygame.display.flip()
    
            rectList[0].center = (initBallX + ballR, initBallY + ballR)
            ballMask.center = (initBallX +  ballR, initBallY + ballR)
            ballV = pongUtil.randomVelocity()
            testRect = rectList[0]
            collided = [False, False, False, False]
            recordFailState = True
            if p1Bot:
                network.clearPreviousStates(ballV, 
                                            rectList[0].center[0], 
                                            rectList[1].center[0], 
                                            ballState)
            
        # Prevent 0 horizontal velocity, to prevent infinite games
        if ballV[0] == 0:
            ballV[0] = random.randint(-1,1)
            
        # Move ball
        moveObject(0, ballV )
        testRect = testRect.move(ballV)
        
        # Store coordinates when the ball is passing p1 paddle space
        if recordFailState  and  rectList[0].bottom > rectList[1].top  and  rectList[0].bottom < rectList[1].top + ballR + 1:
            
            ballXAtFail = rectList[0].center[0]
            ballVXAtFail = ballV[0]
            p1XAtFail = rectList[1].center[0]
            recordFailState = False

        # check collision of ball with paddles
        index = rectList[0].collidelist(bouncers)    

        if index == 0 or index == 1:
            trueCollision = checkCollision(rectList[0], rectList[index+1])
            if not trueCollision:
                index = -1

        if index == 0 and not collided[0]: 
            ballX = rectList[0].center[0]
            ballY = rectList[0].center[1]
            collided[0] = True
            collided[1] = False
            collided[2] = False
            collided[3] = False
            
            
            # This code changes the ball's behavior based on where it hits a 
            # given paddle.  Hitting the right makes the ball move more to the 
            # right, etc.
            if ballY < rectList[1].top:  # Ball hit p1 paddle
                
                if ballX < rectList[1].left:
                    intersectLine = (ballX - rectList[1].left) + rectList[1].top
                    if verbose:
                        print('upper left')                
                    
                    if ballY <= intersectLine:                        
                        ballV[1] = ballV[1]*-1
                        ballV[0] -= 2
                        p1Bounces += 1
                        ballState = P1HIT
                        if verbose:
                            print('bounce up!')                                                 

                    else:
                        if ballV[0] > 0:
                            ballV[0] *= -1                        
                        if isMoving[0] < 0:
                            ballV[0] -= 15
                        if verbose:
                            print('bounce left')

                elif ballX > rectList[1].right:
                    intersectLine = -1*(ballX - rectList[1].right) + rectList[1].top

                    if verbose:
                        print('upper right')
                    if ballY <= intersectLine:
                        ballV[1] = ballV[1]*-1
                        ballV[0] += 2
                        p1Bounces += 1
                        ballState = P1HIT
                        if verbose:
                            print('bounce up!')
                                                
                    else:
                        if ballV[0] < 0:
                            ballV[0] *= -1   
                        if isMoving[0] > 0:
                            ballV[0] += 15
                        if verbose:
                            print('bounce right')

                else:
                    if verbose:
                        print('above')
                    p1Bounces += 1
                    ballState = P1HIT
                    ballV[1] = ballV[1]*-1
                    offset = ballX - rectList[1].center[0]
                    
                    if offset > 10 and offset <= 35:
                        ballV[0] += 1
                    elif offset > 35:
                        ballV[0] += 2
                    elif offset < -10 and offset >= -35:
                        ballV[0] -= 1
                    elif offset < -35:
                        ballV[0] -= 2
                           
                
            elif ballX >= rectList[1].center[0]:
                if verbose:
                    print('right')
                if ballV[0] < 0:
                    ballV[0] *= -1
                if isMoving[0] > 0:
                    ballV[0] += 15
                    
            elif ballX < rectList[1].center[0]:
                if verbose:
                    print('left')
                if ballV[0] > 0:
                    ballV[0] *= -1
                if isMoving[0] < 0:
                    ballV[0] -= 15 
            
            if ballState == P1HIT:
                previousVX = ballV[0]
                if p1Bot and p1LearningBot:
                    network.evaluateDecision(ballV, 
                                             rectList[0].center[0], 
                                             rectList[1].center[0], 
                                             ballState)
                else:
                    network.updatePreviousStates(ballV, 
                                                 rectList[0].center[0], 
                                                 rectList[1].center[0], 
                                                 ballState)
                
        elif index == 1 and not collided[1]:            
            ballX = rectList[0].center[0]
            ballY = rectList[0].center[1]
            collided[0] = False
            collided[1] = True
            collided[2] = False
            collided[3] = False

            
            if ballY > rectList[2].bottom: # Ball hit p2 paddle
                if verbose:
                    print( 'below')
                
                if ballX < rectList[2].left:
                    intersectLine = -1*(ballX - rectList[2].left) + rectList[2].bottom

                    if verbose:
                        print('lower left')
                    if ballY >= intersectLine:
                        ballV[1] = ballV[1]*-1
                        ballV[0] -= 2
                        p2Bounces += 1
                        ballState = P2HIT
                        if verbose:
                            print('bounce down!')                     
                    else:
                        if ballV[0] > 0:
                            ballV[0] *= -1   
                        if isMoving[1] < 0:
                            ballV[0] -= 15
                        if verbose:
                            print('bounce left')                                               
                elif ballX > rectList[2].right:
                    intersectLine = (ballX - rectList[2].right) + rectList[2].bottom
                                  
                    if verbose:
                        print('lower right')
                    if ballY >= intersectLine:
                        ballV[1] = ballV[1]*-1
                        ballV[0] += 2
                        p2Bounces += 1
                        ballState = P2HIT
                        if verbose:
                            print('bounce down!')                                                
                    else:
                        if ballV[0] < 0:
                            ballV[0] *= -1   
                        if isMoving[1] > 0:
                            ballV[0] += 15
                        if verbose:
                            print('bounce right')                                               
                    
                else:
                    p2Bounces += 1
                    ballState = P2HIT
                    ballV[1] = ballV[1]*-1
                    offset = ballX - rectList[2].center[0]
                    if offset > 10 and offset <= 35:
                        ballV[0] += 1
                    elif offset > 35:
                        ballV[0] += 2
                    elif offset < -10 and offset >= -35:
                        ballV[0] -= 1
                    elif offset < -35:
                        ballV[0] -= 2                          
                
            elif ballX >= rectList[2].center[0]:
                if verbose:
                    print('right')
                ballV[0] *= -1
                if isMoving[1] > 0:
                    ballV[0] += 15                      
            elif ballX < rectList[2].center[0]:
                if verbose:
                    print('left')
                ballV[0] *= -1
                if isMoving[1] < 0:
                    ballV[0] -= 15                      
            
            if ballState == P2HIT:
                recordFailState = True
                outX = rectList[0].center[0]
                outV = ballV
                ballTop = rectList[0].top
                rectBottom = rectList[2].bottom
                
                # Deal with a ball edge case where it bounces against the wall 
                # and paddle at the same time
                if ballTop != rectBottom and ballV[0] != 0:

                    outX = int(round(rectList[0].center[0] - 
                                     (ballTop - rectBottom)/ (ballV[1]/ballV[0])))

                    if outX < marginWidth:
                        outX = marginWidth + (marginWidth-outX)
                        outV = [-1*ballV[0], ballV[1]]
                    elif outX > marginWidth + gameWidth:
                        outX = marginWidth + gameWidth - (outX - (marginWidth + gameWidth))
                        outV = [-1*ballV[0], ballV[1]]
                    
                if p1Bot and p1LearningBot:
                    network.evaluateDecision(outV, 
                                             outX, 
                                             rectList[1].center[0], 
                                             ballState)
                else:
                    network.updatePreviousStates(outV, 
                                                 outX, 
                                                 rectList[1].center[0], 
                                                 ballState)
                
                    
            
        # Ball hits a wall        
        elif index == 2 and not collided[2]:
            ballV[0] = ballV[0]*-1                         
            collided[0] = False
            collided[1] = False            
            collided[2] = True
            collided[3] = False
        elif index == 3 and not collided[3]:
            ballV[0] = ballV[0]*-1                         
            collided[0] = False
            collided[1] = False            
            collided[2] = False
            collided[3] = True            

        
        ## bot player 2 code ##
        # Player 2 bot tracks the ball and stays under it at all times
        if(p2Bot):            

            value = rectList[2].center[0] - rectList[0].center[0]
            if value < -15:
                moveObject(2, (15,0) )            
            elif value > 15:
                moveObject(2, (-15,0) )
        
        ## bot player 1 code ##
        if(p1Bot):
            if(p1BotUseNetwork):    # Use neural network to play
                decision = network.getDecision(rectList[1].center[0])
                if decision > 0:
                    moveObject(1, (15,0) )      
                elif decision < 0:
                    moveObject(1, (-15,0) )
                          
            else:                   # Track ball like player 2
                value = rectList[1].center[0] - rectList[0].center[0]
                if value < -15:
                    moveObject(1, (15,0) )            
                elif value > 15:
                    moveObject(1, (-15,0) )        
        
        
        ## Drawing ##

        if(draw):
            for i in rectListOld:
                screen.fill(WHITE,i)       

            if redrawBall:
                pygame.draw.circle(surfaceList[0], BLUE, (ballR, ballR) , ballR )
                redrawBall = False
                
            if index == 2:
                pygame.draw.rect( surfaceList[0], 
                                  WHITE, 
                                  (0,0, gameLeft - rectList[0].left, ballR*2 ) )
                redrawBall = True
            elif index == 3:
                pygame.draw.rect( surfaceList[0], WHITE, 
                                  (ballR*2 - (rectList[0].right - gameRight),
                                   0, 
                                   rectList[0].right - gameRight, 
                                   ballR*2 ) )
                redrawBall = True            
        
        
            for i in range(5):
                screen.blit(surfaceList[i], rectList[i])
            
            screen.fill(WHITE, pygame.Rect(gameRight+20, size[1]-100 - fontSize/2, size[0] - gameRight, fontSize*1.5) )
            screen.fill(WHITE, pygame.Rect(gameRight+20, 100                     , size[0] - gameRight, fontSize*1.5) )
            
            screen.blit( screenFont.render(str(p1Score), True, BLACK), (gameRight+20,size[1]-100) ) 
            screen.blit( screenFont.render(str(p2Score), True, BLACK), (gameRight+20,100) ) 
            screen.blit( halfScreenFont.render(str(p1Bounces), True, BLUE), (gameRight+20, 700 - fontSize/2 - 5) ) 
            screen.blit( halfScreenFont.render(str(p2Bounces), True, BLUE), (gameRight+20, 100 + fontSize ) )             
            
            # Update screen
            pygame.display.flip()             

        # Time limit check
        if time.time() - startingTime >= maxTime:
            done = True        
            
        # Frame-rate
        if useClock:
            clock.tick(clockValue)
        
        # Limit speed of ball
        if abs(ballV[0]) > maxVX:
            maxVX = abs(ballV[0])
        
        

    print( pongUtil.calcAverageSpeed(paddleBounces, 'paddle bounce' ) )
    print("Games Played = " + str(totalGames))

    if totalGames > 0:
        print( 'player 1:', p1Score, ' ', round(p1Score/totalGames*100,1),'%' )
        print( 'player 2:', p2Score, ' ', round(p2Score/totalGames*100,1),'%' )
        print('\nAverage Fitness = ' + str(round(fitness/totalGames,2))  + '\n' )        
        #print('random moves = ', network.totalRandomMoves)
        
        outputFile.write( '\nplayer 1: ' +  str(p1Score) + ' ' + str(round(p1Score/totalGames*100,1)) + ' %\n' )
        outputFile.write( 'player 2: ' +  str(p2Score) + ' ' + str(round(p2Score/totalGames*100,1)) + ' %\n' )
        outputFile.write('\nAverage Fitness = ' + str(round(fitness/totalGames,2)) )
        outputFile.close()
        return str(round(fitness/totalGames,2))
        
    outputFile.close()    
    return fitness


# Checks if the ball is actually colliding with something, or if just the 
# rectangle defining the ball is colliding (false collision)
def checkCollision(ball, rect):
    global verbose
    radius = ball.width/2
    ballX = ball.center[0]
    ballY = ball.center[1]
    rectX = rect.center[0]
    rectY = rect.center[1]
    output = True
    

    if ballX >= rect.left and ballX <= rect.right:
        if verbose:
            print('** center')
        return output  
    elif ballY <= rect.bottom and ballY >= rect.top:
        if verbose:
            print(' ** sides')
        return output  
    

    if ballX > rectX:
        if ballY < rectY:
            xDist = math.fabs(ballX - rect.right)
            yDist = math.fabs(ballY - rect.top)
        else:
            xDist = math.fabs(ballX - rect.right)
            yDist = math.fabs(ballY - rect.bottom)          
    else:
        if ballY < rectY:
            xDist = math.fabs(ballX - rect.left)
            yDist = math.fabs(ballY - rect.top)
        else:
            xDist = math.fabs(ballX - rect.left)
            yDist = math.fabs(ballY - rect.bottom)       
    

    distance = math.sqrt( xDist*xDist + yDist*yDist)
    if distance > radius:
        output = False
        if verbose:
            print( '>> false collision' )    

    
    return output
    
    

#if __name__ == '__main__':
#  main()
