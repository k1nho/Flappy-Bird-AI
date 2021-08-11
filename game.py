# Author: Kin NG
# Purpose: Flappy bird game based on the concept of genetic algorithm for the creation of an AI.

# import important modules
import pygame, math
import random
import neat
import os

pygame.font.init()
# create window for the game
HEIGHT = 800
WIDTH = 500
WIN = pygame.display.set_mode((WIDTH, HEIGHT))

#caption for the game
pygame.display.set_caption("Flappy Bird AI")

# animation sequences of the bird
BIRD_FRAMES =[pygame.transform.scale2x(pygame.image.load(os.path.join("animations", "fbird1.png")))
            ,pygame.transform.scale2x(pygame.image.load(os.path.join("animations", "fbird2.png")))
            ,pygame.transform.scale2x(pygame.image.load(os.path.join("animations", "fbird3.png")))]

# background, pipe and base animations
BG = pygame.transform.scale2x(pygame.image.load(os.path.join("animations", "bg.png")))
PIPE = pygame.transform.scale2x(pygame.image.load(os.path.join("animations", "pipe.png")))
BASE = pygame.transform.scale2x(pygame.image.load(os.path.join("animations", "base.png")))

# Letter font for the game
FONT = pygame.font.SysFont("comicsans", 50)
gen = 0

# bird object
class Bird:
    # animations and speed coordinations
    ANIMATIONS = BIRD_FRAMES
    ROT_SPEED = 20
    ROTATION = 25
    FPS = 5
    
    def __init__(self, x, y):
        self.x =x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.speed = 0
        self.height = self.y
        self.imgCount = 0
        self.animation = self.ANIMATIONS[0]
        
    # function to make the bird jump
    def jump(self):
        self.height = self.y
        self.speed = -10.5 
        self.tick_count = 0
        
    
    # function to move horizontally
    def move(self):
        self.tick_count += 1
        # calculates the frames upward the bird needs to move at an specific time 
        upwardMov = self.speed * self.tick_count + (1.5 * math.pow(self.tick_count,2))
        
        # if we reach the base, then don't accelerate more
        if upwardMov >= 16:
            upwardMov = 16
        # if we are moving up then increase the y-axis movement
        if upwardMov < 0:
            upwardMov -= 2
        
        # change the position of the bird
        self.y = self.y + upwardMov
        
        #check the position of the bird in current motion
        if upwardMov < 0 or self.y < self.height + 50:
            # make rotation if the bird jumped but its not in rotation
            if self.tilt < self.ROTATION:
                self.tilt = self.ROTATION
        # make the bird fall if the bird is not jumping
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_SPEED
    
    # function to draw the bird in screen
    def draw(self, window):
        self.imgCount +=1
        
        # flapping motion according to the frames per second
        if self.imgCount <= self.FPS:
            self.animation = self.ANIMATIONS[0]
        elif self.imgCount <= self.FPS*2:
            self.animation = self.ANIMATIONS[1]
        elif self.imgCount <= self.FPS*3:
            self.animation = self.ANIMATIONS[2]
        elif self.imgCount <= self.FPS*4:
            self.animation = self.ANIMATIONS[1]
        elif self.imgCount == self.FPS*4 +1:
            self.animation = self.ANIMATIONS[0]
            self.imgCount = 0
        
        # Do not make motion while going downward
        if self.imgCount <= -80:
            self.animation = self.ANIMATIONS[1]
            self.imgCount = self.FPS * 2
            
        # rotate the the bird in its center
        RotatedBird = pygame.transform.rotate(self.animation, self.tilt)
        newRect = RotatedBird.get_rect(center = self.animation.get_rect(topleft = (self.x, self.y)).center)  
         
        window.blit(RotatedBird, newRect.topleft)
        
    # function to identify collsion of objects
    def getMask(self):
        return pygame.mask.from_surface(self.animation)

# Pipe object
class Pipe:
    PIPEDIST = 200
    SPEED = 5
    
    def __init__(self, x):
        self.x = x
        self.height = 0
        self.top = 0
        self.bottom = 0
        self.pipeTop = pygame.transform.flip(PIPE, False, True)
        self.pipeBottom = PIPE
        self.passed = 0
        self.getHeight()
        
    def getHeight(self):
        # height of the pipe will be a random integer between 50 and 450
        self.height = random.randrange(50,450)
        self.top = self.height - self.pipeTop.get_height()
        self.bottom = self.height + self.PIPEDIST
    
    # function to move the pipe object based on the velocity
    def movePipe(self):
        self.x -= self.SPEED
    # function to draw the top and bottom pipe
    def drawPipe(self, window):
        # draw the top pipe
        window.blit(self.pipeTop, (self.x, self.top))
        # draw the bottom pipe
        window.blit(self.pipeBottom, (self.x, self.bottom))
    
    # function to detect collision between the bird and the pipe
    def collision(self, flappyBird, window):
        
        # collect all the game objects mask
        flappyBirdMask = flappyBird.getMask()
        topPipeMask = pygame.mask.from_surface(self.pipeTop)
        bottomPipeMask = pygame.mask.from_surface(self.pipeBottom)
        
        # offsets to see how far away each mask is from each other
        topOffset = (self.x - flappyBird.x, self.top - round(flappyBird.y))
        bottomOffset = (self.x - flappyBird.x, self.bottom - round(flappyBird.y))
        
        #detect collision
        bottomCollision = flappyBirdMask.overlap(bottomPipeMask, bottomOffset)
        topCollision = flappyBirdMask.overlap(topPipeMask, topOffset)
        
        # check for collision
        if(topCollision or bottomCollision):
            return True
        else:
            return False
# object for the floor of the game
class Base:
    # set the speed to the same as the pipe
    SPEED = 5
    WIDTH = BASE.get_width()
    IMG = BASE 
    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH
    
    # function to scroll the base
    def moveBase(self):
        # the base will move according to the speed
        self.x1 -= self.SPEED
        self.x2 -= self.SPEED
        
        '''
        if we reach the end of a scrol, the coordinate gets repositioned to the coordinate of x2 and
        the constant value of the width. The same process is applied to x2 to keep the base scrolling
        '''
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
        
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH
        
    # function to draw the base on screen
    def drawBase(self, window):
        # The base will be the same, but the two images move together
        window.blit(self.IMG, (self.x1, self.y))
        window.blit(self.IMG, (self.x2, self.y))
        
        
# function to draw the current state of game
def drawGame(window, birdPopulation, pipes, base, score, gen):
    # draw the background to display and bird in that background
    window.blit(BG, (0,0))
    
    if gen == 0:
        gen = 1
    
    for pipe in pipes:
        pipe.drawPipe(window)
    
    base.drawBase(window)
    
    for flappyBird in birdPopulation:
        flappyBird.draw(window)
    
    # Display score points to the screen
    scoreDisplay = FONT.render("Score: " +str(score) , 1, (255,255,255))
    window.blit(scoreDisplay, (WIDTH - 10 - scoreDisplay.get_width(), 10))
    
    # display generations ran to the screen
    score_label = FONT.render("Gens: " + str(gen-1),1,(255,255,255))
    window.blit(score_label, (10, 10))
    # update the display
    pygame.display.update()

    
def main(genomes, config):
    
    global gen
    gen +=1
    
    ''' Implementation of AI '''
    # population of birds and  neat controllers
    neuralControllers = []
    birdPopulation = []
    birdsAI = []
    
    # create neural controller for each bird and set initial fitness to 0
    for bird_id , bird in genomes:
        bird.fitness = 0
        network = neat.nn.FeedForwardNetwork.create(bird, config)
        neuralControllers.append(network)
        birdPopulation.append(Bird(230,350))
        birdsAI.append(bird)
        
    # pipes array object, base object, gameloop, and clock control
    base = Base(730)
    pipes = [Pipe(700)]
    score = 0
    gameLoop = True
    gameClock = pygame.time.Clock()
    
    while(gameLoop) and len(birdPopulation) > 0:
        gameClock.tick(30)
        # handle game events 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                gameLoop = False
                pygame.quit()
                break
        
        
        indexPipe = 0
        # Percepts of the bird should be the pipe coming up in the screen, not the one passed
        if len(birdPopulation) > 0:
            if len(pipes) > 1 and  birdPopulation[0].x > pipes[0].x + pipes[0].pipeTop.get_width():
                indexPipe = 1
        
        for x, flappyBird in enumerate(birdPopulation):
            flappyBird.move()
            birdsAI[x].fitness += 0.1
            
            # make the bird AI agent act accordingly to the percepts
            neuralOutput = neuralControllers[birdPopulation.index(flappyBird)].activate((flappyBird.y ,
                                                                                        abs(flappyBird.y - pipes[indexPipe].height),
                                                                                        abs(flappyBird.y - pipes[indexPipe].bottom)))
            
            # If the value yield from the activation function (Tanh) is greater tahn 0.5, then the action of the agent should be jump
            if neuralOutput[0] > 0.5: 
                flappyBird.jump()
                

        base.moveBase()
        recycle = []
        addPipe = False
        for pipe in pipes:
            for flappyBird in birdPopulation:
                # check collision with the bird
                if pipe.collision(flappyBird, WIN):
                    # reduce fitness performance on collision
                    birdsAI[birdPopulation.index(flappyBird)].fitness -= 1
                    neuralControllers.pop(birdPopulation.index(flappyBird))
                    birdsAI.pop(birdPopulation.index(flappyBird))
                    birdPopulation.pop(birdPopulation.index(flappyBird))
                    
            # check if the bird has passed the pipe
            if not pipe.passed and pipe.x < flappyBird.x:
                pipe.passed = True
                addPipe = True
                    
            # remove the pipe if it is out of the screen
            if pipe.x + pipe.pipeTop.get_width() < 0:
                recycle.append(pipe)
                
            pipe.movePipe()
        
        '''
        if a pipe is passed by the bird, then the score gets increased
        and a new pipe gets generated. Increase the fitness of the AI as well
        '''
        if addPipe == True:
            score += 1
            # increase fitness function
            for flappyBird in birdsAI:
                flappyBird.fitness += 5
            pipes.append(Pipe(600))
        
        for removed in recycle:
            pipes.remove(removed)
        
        for x, flappyBird in enumerate(birdPopulation):
            if flappyBird.y + flappyBird.animation.get_height() - 10 >= 730 or flappyBird.y < -50:
                # Eliminate the bird and all its associations from the current generation
                neuralControllers.pop(x)
                birdsAI.pop(x)
                birdPopulation.pop(x)
                
                
        drawGame(WIN, birdPopulation, pipes, base, score,gen)
        
        
        '''Goal test'''
        if score > 200:
            print("Goal state achieved! Terminating the game")
            break
        
    
# Setup function to run NEAT configuration file using main 
def run(configurationPath):
    # load configuration file of NEAT
    configFile = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, 
                      neat.DefaultStagnation, configurationPath)
    
    # create population
    birdPopulation = neat.Population(configFile)
    
    # experimental data of the bird population in the game
    birdPopulation.add_reporter(neat.StdOutReporter(True))
    experimentResult = neat.StatisticsReporter()
    birdPopulation.add_reporter(experimentResult)
    
    # Check if the goal is fullfilled and run 50 generations
    goalTest = birdPopulation.run(main,50)
    

if __name__ == "__main__":
    localDirectory = os.path.dirname(__file__)
    configurationPath = os.path.join(localDirectory, "configFB.txt")
    run(configurationPath)
    
    
    