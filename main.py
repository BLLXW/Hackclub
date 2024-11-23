from pygame_functions import *
import math, random, time
from leaderboardDatabase import *

displayInfo = pygame.display.Info()
userScreenWidth = displayInfo.current_w
userScreenHeight = displayInfo.current_h
screenSize(userScreenWidth, userScreenHeight, fullscreen=True)
screenCentre = [userScreenWidth/2, userScreenHeight/2]

backgroundSprite = makeSprite("background.png")
backgroundx = screenCentre[0]
backgroundy = screenCentre[1]
moveSprite(backgroundSprite, backgroundx, backgroundy, True)
showSprite(backgroundSprite)

frameCount = 0
flickingFrequency = 10
animationTime = 90
originalSize = 100

factorScale = min(userScreenWidth, userScreenHeight) / 1000  


class Creature:
    def __init__(self, x, y, size, xspeed, yspeed, image):
        self.x = x
        self.y = y
        self.sprite = makeSprite(image)
        self.size = size
         
        moveSprite(self.sprite, self.x, self.y)
        transformSprite(self.sprite, 0, (self.size/50) * factorScale)
        showSprite(self.sprite)
        
        self.xspeed = random.randint(-15, 15)
        self.yspeed = random.randint(-15, 15)
        
        while self.xspeed == 0 or self.yspeed == 0:
            self.xspeed = random.randint(-15, 15)
            self.yspeed = random.randint(-15, 15)
        
    def move(self, Player):
        self.x = (self.x + self.xspeed) % 2500
        self.y = (self.y + self.yspeed) % 2500
        moveSprite(self.sprite, screenCentre[0]+(self.x-Player.x), screenCentre[1]+(self.y-Player.y), centre=True)

class Player(Creature):
    def __init__(self, x, y, size, xspeed, yspeed, image):
        super().__init__(x, y, size, xspeed, yspeed, image)
        transformSprite(self.sprite, 0, (self.size/600) * factorScale)
        moveSprite(self.sprite, screenCentre[0], screenCentre[1], True)
        self.previousX = x
        self.previousY = y
        
        self.minX = 0
        self.maxX = worldWidth
        self.minY = 0
        self.maxY = worldHeight
    
    def move(self):
        global backgroundx, backgroundy
        self.previousX = self.x
        self.previousY = self.y
        
        self.pspeed = 7 * factorScale
        moved = False
        

        newX = self.x
        newY = self.y
        newbgX = backgroundx
        newbgY = backgroundy
        
        if keyPressed("W"):
            newY = self.y - self.pspeed
            newbgY = backgroundy + self.pspeed
            if newY >= self.minY:  
                self.y = newY
                backgroundy = newbgY
                moved = True
                
        if keyPressed("A"):
            newX = self.x - self.pspeed
            newbgX = backgroundx + self.pspeed
            if newX >= self.minX:  
                self.x = newX
                backgroundx = newbgX
                moved = True
                
        if keyPressed("S"):
            newY = self.y + self.pspeed
            newbgY = backgroundy - self.pspeed
            if newY <= self.maxY: 
                self.y = newY
                backgroundy = newbgY
                moved = True
                
        if keyPressed("D"):
            newX = self.x + self.pspeed
            newbgX = backgroundx - self.pspeed
            if newX <= self.maxX:  
                self.x = newX
                backgroundx = newbgX
                moved = True
            
        if moved:
            moveSprite(backgroundSprite, backgroundx, backgroundy, True)
    
    def checkTouch(self, spikes):
        if frameCount > 90:
            for spike in spikes:
                if touching(spike.sprite, self.sprite) and spike.visible:
                    
                    stopMusic()
                    
                    spikeSound = makeSound("spikeSound.mp3")
                    playSound(spikeSound)

                    time.sleep(1.75)
                    
                    stopMusic()
                    lossSound = makeSound("victoryTrack.mp3")
                    playSound(lossSound)
                    for spike in spikes:
                        hideSprite(spike.sprite)
                    hideSprite(self.sprite)
                    
                    backgroundSprite = makeSprite("win.png")
                    backgroundx = screenCentre[0]
                    backgroundy = screenCentre[1]
                    moveSprite(backgroundSprite, backgroundx, backgroundy, True)
                    showSprite(backgroundSprite)
                    updateDisplay()
                    time.sleep(4)
                    
                    getPlayerName()
                    showLeaderboard()
                    
                    return True
            return False

class Saver(Creature):
    def __init__(self, x, y, size, image):
        super().__init__(x, y, size, 0, 0, image)
        self.speed = 6 * factorScale
        self.active = True
    
    def move(self, Player, Spikes):
        if not self.active or  frameCount < 90:
            moveSprite(self.sprite, screenCentre[0] + (self.x - Player.x), screenCentre[1] + (self.y - Player.y), centre=True)
            return
    
        xdistance = Player.x - self.x
        ydistance = Player.y - self.y
        totalDistance = math.sqrt(xdistance ** 2 + ydistance ** 2)
  
        if touching(self.sprite, Player.sprite):
            stopMusic()
            lossSound = makeSound("lossTrack.mp3")
            playSound(lossSound)

            hideSprite(Player.sprite)
  
            loseScreen = makeSprite("lose.png")
            moveSprite(loseScreen, screenCentre[0], screenCentre[1], True)
            showSprite(loseScreen)

            updateDisplay()
            
            tick(120)  

            hideSprite(loseScreen)

            showLeaderboard()
            updateDisplay()

        if self.isNear(Player):
            self.speed = 6.5 * factorScale
        else:
            self.speed = 6 * factorScale
 
        if totalDistance > 0:
            self.x += (xdistance / totalDistance) * self.speed
            self.y += (ydistance / totalDistance) * self.speed
       
        for spike in Spikes:
            if spike.visible and self.isNear(spike):
                spikeXDistance = spike.x - self.x
                spikeYDistance = spike.y - self.y
                spikeDistance = math.sqrt(spikeXDistance ** 2 + spikeYDistance ** 2)
  
                if spikeDistance < totalDistance:
                    if spikeDistance > 0:
                        self.x += (spikeXDistance / spikeDistance) * self.speed
                        self.y += (spikeYDistance / spikeDistance) * self.speed

                    if touching(self.sprite, spike.sprite):
                        hideSprite(self.sprite)
                        hideSprite(spike.sprite)
                        spike.visible = False
                        self.active = False
                        return

        moveSprite(self.sprite,screenCentre[0] + (self.x - Player.x), screenCentre[1] + (self.y - Player.y), centre=True)
    
    def isNear(self, target):
        xdifference = self.x - target.x
        ydifference = self.y - target.y
        return math.sqrt(xdifference ** 2 + ydifference ** 2) < userScreenHeight / 4
        
    
class Spikes(Creature):
    def __init__(self, x, y, size, image):
        super().__init__(x, y, size, 0, 0, image)
        self.visible = False
        self.appearTime = random.randint(100,200)
        self.disappearTime = random.randint(100,200)
        self.timer = 0

    def update(self, Player):
        self.timer += 1
        if self.timer < self.appearTime:
            if not self.visible:
                self.x = random.randint(0, int(worldWidth))
                self.y = random.randint(0, int(worldHeight))
                moveSprite(self.sprite, screenCentre[0] + (self.x - Player.x), screenCentre[1] + (self.y - Player.y), centre=True)
                
                if not touching(self.sprite, Player.sprite):
                    self.visible = True
                    showSprite(self.sprite)
                else:
                    while touching(self.sprite, Player.sprite) == True:
                        self.x = random.randint(0, int(worldWidth))
                        self.y = random.randint(0, int(worldHeight))
                        moveSprite(self.sprite, screenCentre[0] + (self.x - Player.x), screenCentre[1] + (self.y - Player.y), centre=True)
                    self.visible = True
                    showSprite(self.sprite) 
                
        elif self.timer < self.appearTime + self.disappearTime:
            if self.visible:
                self.visible = False
                hideSprite(self.sprite)
        else:
            self.timer = 0
        
        moveSprite(self.sprite, screenCentre[0] + (self.x - Player.x), screenCentre[1] + (self.y - Player.y), centre=True)

setAutoUpdate(False)

worldWidth = userScreenWidth * 2.5
worldHeight = userScreenHeight * 2.5

thePlayer = Player(worldWidth/2, worldHeight/2, userScreenHeight/2, 10, 10, "Player.png")
    
allSpikes = []

for i in range(5):
    allSpikes.append(Spikes(random.randint(userScreenWidth, int(worldWidth)), random.randint(userScreenHeight, int(worldHeight)), userScreenHeight/35, "spike.png"))
 
allSavers = []

for i in range(3):
    allSavers.append(Saver(random.randint(0, int(worldWidth)), random.randint(0, int(worldHeight)), userScreenHeight / 35, "Saver.png"))

def spawnAnimation():
    global flickingFrequency, frameCount, thePlayer, animationTime

    if frameCount < animationTime:  
        
        if frameCount % flickingFrequency < flickingFrequency // 2:
            showSprite(thePlayer.sprite)
            
        else:
            hideSprite(thePlayer.sprite)
            
    else:
        showSprite(thePlayer.sprite) 
        
def showLeaderboard():
    backgroundSprite = makeSprite("blue.png")  
    moveSprite(backgroundSprite, screenCentre[0], screenCentre[1], True)
    showSprite(backgroundSprite)

    title = makeLabel("LEADERBOARD", 50, screenCentre[0] - 150, 50, 
                     fontColour='white', font='Arial Black', background='clear')
    showLabel(title)
    
    scores = getTopScores()
    scoreLabels = []
    startY = 150
    
    for i, (name, time) in enumerate(scores, 1):
        score_text = f"{i}. {name} - Time Survived: {time}s"
        label = makeLabel(score_text, 30, screenCentre[0] - 200, startY + (i * 40),
                         fontColour='white', font='Arial', background='clear')
        showLabel(label)
        scoreLabels.append(label)

def getPlayerName():
    backgroundSprite = makeSprite("blue.png")   
    moveSprite(backgroundSprite, screenCentre[0], screenCentre[1], True)
    showSprite(backgroundSprite)
    
    title = makeLabel("Enter Your Name:", 50, screenCentre[0] - 150, 100,
                     fontColour='white', font='Arial', background='clear')
    showLabel(title)

    inputBox = makeTextBox(screenCentre[0] - 100, 200, 200, 
                          startingText="Type name here", 
                          maxLength=15, 
                          fontSize=30)

    name = textBoxInput(inputBox)

    addScore(name, frameCount // 30)
    
    hideLabel(title)
    hideSprite(backgroundSprite)
    hideTextBox(inputBox)
    
l = makeLabel("Time Alive: " + str(frameCount // 30), 20, 15, 100, fontColour='black', font='Arial', background='clear')
showLabel(l)

def updateTime(framecount):
    howLong = framecount // 30
    changeLabel(l,"Time Alive: " + str(frameCount // 30))
    
spawnInSound = makeSound("spawnIn.mp3")
playSound(spawnInSound)
time.sleep(3)
makeMusic("bgmusic.mp3")
playMusic(-1)

while True:
    frameCount += 1
    showSprite(thePlayer.sprite)
    
    spawnAnimation()
    clearShapes()
    
    
    thePlayer.move()
    
    for spike in allSpikes:
        spike.update(thePlayer)

    for saver in allSavers:
        saver.move(thePlayer, allSpikes)

    if thePlayer.checkTouch(allSpikes):
        break
    
    updateTime(frameCount) 
    updateDisplay()
    tick(30)

endWait()