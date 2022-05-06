----- Overview -----

    This program is the game pong, one of the earliest computer games.  I recreated
the game from scratch.  Then I created a bot that can learn how to play the game
from zero previous knowledge.  Within 2 minutes, it will emulate 36000 games and 
my bot will have a 90% win rate.  The bot creates a neural network that remembers 
every past game and weights its options for striking the ball.  It refines this 
network with each experience and improves its play.

A jpeg "Simulation in progess" displays what the program looks like.


----- How to Use the Program -----

The program can be played like a normal pong game by one or two users if the bot
flags are disabled.   

Left, Right arrow - moves player 1
A, D - moves player 2
Space Bar - Resets the game.
Escape - Quits the program
C - Toggles the frame rate limit.  Illustrates how fast the simulation moves.
Z - Toggles between drawing the game or a display giving statistics on the simulation.  

Note: C and Z are touchy given a limit of the pygame module.

Use the methods in main.py to run the desired type of test.  Each method
requires a network object to run.

If desired, the neural network created can be written to file.  This "bot's 
brain" can be used later for other tests. Another output file is created that
summarizes the simulation.  It documents every game, how many hits each bot had,
and the total win percentage and fitness of the learning bot.

The network output files are quite large, from 20-30mb.  Though they can be much
smaller with any type of zip compresssion.


----- Code Structure -----

main.py:

This file contains many methods to run different types of tests of the simulation.

pong.py:

This file is the basis for the pong simulation.  It contains the simulation loop,
game logic, and key capture code.  It also draws to the screen (if enabled).
Player 1 is either the user or the learning bot.  Player 2 is either a second user or
a bot that cheats and is very difficult to beat.


pongUtil.py:

It contains generic utility functions.


neuralNetwork.py:

This file houses all the code for managing and updating the neural
network within a class.  This includes code that stores learning from past games
and provides decisions based on a current game state.  It also has functions
that can read from and write the network to a file.

The neural network itself maps data on the ball's initial angle of bounce, 
its initial x-velocity, where the player 1 paddle attempted to hit the incoming shot,
and the current game state to a value.  This value indicates wether this state
has been seen before, and if the previous experience was a miss, hit, or a hit
that led to a win.  A higher value indicates a more desirable outcome.

The neural network class translates the x values of the screen to a new
set of x coordinates. For the ball it collapses the coordinates by half, and for
the paddle the values are divided by 15.  This corresponds to how the paddles move,
by 15 pixels at a time, and reduces the size of the neural network dramatically.
Reducing the size of the network allows for faster learning.


----- Bot Performance -----

My learning bot's opponent, player 2, is a difficult opponent to defeat.  As 
player 2 tracks the ball at all times and stays underneath.

The learning bot achieves ~30% win rate at 30 sec and ~12000 games played.
It achives ~90% win rate at 120 sec and ~ 36000 games played.

I use a metric called fitness that measures the performance of the bot for each
game.  It gains 1 point for each successful hit and 100 points for a win.

Here's an example of the bot's learning progression.

30 seconds
player 1: 1421 31.6 %
player 2: 3074 68.4 %
Average Fitness = 38.29

60 seconds
player 1: 2243 66.8 %
player 2: 1116 33.2 %
Average Fitness = 75.52

90 seconds
player 1: 2481 82.2 %
player 2: 537 17.8 %
Average Fitness = 91.92

120 seconds 
player 1: 2619 88.0 %
player 2: 358 12.0 %
Average Fitness = 98.26

150 seconds
player 1: 2235 89.3 %
player 2: 267 10.7 %
Average Fitness = 102.1


After 2 minutes, learning slows dramatically.  This can be increased by using
a low level of entropy in decision making.  This is implemented as occasionally
choosing a less optimal option.  This currently less optimal decision can 
sometimes lead to a more optimal decision than before. 

Entropy scale: 1  = 10% random
               10 = 100% random
           
Here is a test of a network that was run for 10 minutes and 129285 games played 
at an entropy level of 1:           
    
600 seconds
player 1: 6893 98.0 %
player 2: 144 2.0 %
Average Fitness = 105.68

A high level of success can be achieved.  Though approaching a 100% win rate is
logarithmic and will take an exceedingly long time with this model. 


----- Packages used -----

Pygame
math
time
random


Pygame is a package created for coding games.  It's used in this code to
facilitate drawing to the screen, managing and computing geometry of shapes, and
handling user input.

This version is intended for Windows and is untested on macOS. It will most
likely not run correctly.

Some exe files are provided in the dist folder.
These exe files work for windows 8 and 10, but not for Windows 7.  It should work
for Windows 11, though it is untested.  This is a limitation of the pygame module.



