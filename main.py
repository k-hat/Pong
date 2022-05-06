import pong
import neuralNetwork
import pongUtil


# My bank of different tests.
def main():
    
    network = neuralNetwork.NeuralNetwork()
    
    #network.setEntropy(1)
    #runBlankNetworkTest(network, 600, 'output network600E1.txt', False)
    
    runBlankNetworkTest(network, 30, "output network.txt", '30 second Network Creation.txt', False)    
    testCurrentNetwork(network, "testing the network.txt", 15)
    
    #network.createBlankNetwork()
    #network.readNetwork('output network.txt')
    #network.readNetwork('output network600E1.txt')
    #network.printNetworkSize()

    #pong.run(network, 'output.txt',True, 10000, True)
    
    #network.setEntropy(0)
    #pong.run(network, 'test 10 minutes1.txt',False, 30, False)
    #pong.run(network, 'test 10 minutes2.txt',False, 30, False)
    #pong.run(network, 'test 10 minutes3.txt',False, 30, False)
    
    #network.writeNetwork('output network.txt') 
    #network.readNetwork('output network.txt')
    #pong.run(network, 'output.txt',False, 3, False)
    #network.writeNetwork('output network.txt')    
    
    #runBlankNetworkTest(network, 360, 'output network.txt', False)
    
    #runSingleTest(network, 20, 'output network.txt', False, False, False)
    
    #runMultiTest(network, 30, False, 8)
    
    #runEntropySweep(network, 120, False, 7, False)
    
    return

# Run a test with a completely blank network.
def runBlankNetworkTest(network, time, networkFile, outputFile, displayWindow):    
    
    network.createBlankNetwork()        
    pong.run(network, outputFile, displayWindow, time, True)    
    network.writeNetwork(networkFile) 
    network.printNetworkSize()   
    return    


# Run a test with an existing network read from a file.    
def runSingleTest(network, time, networkFile, displayWindow, saveNetwork, useLearningBot):

    network.readNetwork(networkFile) 

    if len(network.network) == 0:
        network.createBlankNetwork()
       
    pong.run(network, 'output.txt', displayWindow, time, useLearningBot)
    
    if saveNetwork:  
        network.writeNetwork(networkFile)    
    
    network.printNetworkSize()   
    
    return

# Evaluate the current network without learning.
def testCurrentNetwork(network, outputFile, time):
    
    print("Testing current network for ", time, "seconds" )
    
    pong.run(network, outputFile, False, time, False)
    
    return


# Creates multiple networks and tests each one.  Does not save the network to a file.
# Each network is developed for a different amount of time.
def runMultiTest(network, interval, displayWindow, repeatCount):
    
    # Each Network is created for interval * number of repeats
    
    for i in range(1,repeatCount+1):
        # Create Network
        runBlankNetworkTest(network, interval * i, "output.txt", displayWindow)            
        
        outputFile = "output - " + str(interval*i) + " Seconds test.txt"
        # Test network
        pong.run(network, outputFile, displayWindow, 15, False)   
        
    return


# Run multiple tests with differing entropy values (from 0 to  repeat count - 1)
# Entropy inserts a random chance that the most optimal choice is not always taken.
# This allows more optimal paths to be found for more developed networks.
def runEntropySweep(network, time, displayWindow, repeatCount, writeAtRepeat):

    
    recordFitness = []
    
    entropy = 0
    for i in range(0,repeatCount):
        network.createBlankNetwork()            
        network.setEntropy(entropy)
        pong.run(network, 'output.txt', displayWindow, time, True)
        
        network.setEntropy(0)
        outputFile = "output - " + str(entropy) + " entropy.txt"
        recordFitness.append( pong.run(network, outputFile, displayWindow, 15, False) )
        
        if writeAtRepeat:
            network.writeNetwork(networkFile)  
            
        entropy += 1
        
    
    print("")
    for i in range(0, repeatCount):
        print("Entropy:", i, "Fitness:", recordFitness[i])
        
    return
    
    
if __name__ == '__main__':
  main()
