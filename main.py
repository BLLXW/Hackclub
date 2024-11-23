from pygame_functions import *
import math, random, time

displayInfo = pygame.display.Info()
userScreenWidth = displayInfo.current_w
userScreenHeight = displayInfo.current_h
screenSize(userScreenWidth, userScreenHeight, fullscreen=True)
screenCentre = [userScreenWidth/2, userScreenHeight/2]

backgroundSprite = makeSprite("background.png")
bg_x = screenCentre[0]
bg_y = screenCentre[1]
moveSprite(backgroundSprite, bg_x, bg_y, True)
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
        self.prev_x = x
        self.prev_y = y
        
        self.minX = 0
        self.maxX = worldWidth
        self.minY = 0
        self.maxY = worldHeight
    
    def move(self):
        global bg_x, bg_y
        self.prev_x = self.x
        self.prev_y = self.y
        
        self.pspeed = 7 * factorScale
        moved = False
        

        new_x = self.x
        new_y = self.y
        new_bg_x = bg_x
        new_bg_y = bg_y
        
        if keyPressed("W"):
            new_y = self.y - self.pspeed
            new_bg_y = bg_y + self.pspeed
            if new_y >= self.minY:  
                self.y = new_y
                bg_y = new_bg_y
                moved = True
                
        if keyPressed("A"):
            new_x = self.x - self.pspeed
            new_bg_x = bg_x + self.pspeed
            if new_x >= self.minX:  
                self.x = new_x
                bg_x = new_bg_x
                moved = True
                
        if keyPressed("S"):
            new_y = self.y + self.pspeed
            new_bg_y = bg_y - self.pspeed
            if new_y <= self.maxY: 
                self.y = new_y
                bg_y = new_bg_y
                moved = True
                
        if keyPressed("D"):
            new_x = self.x + self.pspeed
            new_bg_x = bg_x - self.pspeed
            if new_x <= self.maxX:  
                self.x = new_x
                bg_x = new_bg_x
                moved = True
            
        if moved:
            moveSprite(backgroundSprite, bg_x, bg_y, True)
    
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
                    label = makeLabel("You Won!", 100, screenCentre[0]-150, screenCentre[1]-100, fontColour='black', font='Arial', background='clear')
                    
                    showLabel(label)
                    updateDisplay()
                    time.sleep(2)
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
            
            time.sleep(0.75)
            hideSprite(Player.sprite)
            label = makeLabel("You Lost!", 100, screenCentre[0]-150, screenCentre[1]-100, 
                            fontColour='black', font='Arial', background='clear')
            showLabel(label)
            updateDisplay()
            time.sleep(2)
            end()

        if self.isNear(Player):
            self.speed = 6.5 * factorScale
        else:
            self.speed = 6 * factorScale
 
        if totalDistance > 0:
            self.x += (xdistance / totalDistance) * self.speed
            self.y += (ydistance / totalDistance) * self.speed
       
        for spike in Spikes:
            if spike.visible and self.isNear(spike):
                spike_xdistance = spike.x - self.x
                spike_ydistance = spike.y - self.y
                spikeDistance = math.sqrt(spike_xdistance ** 2 + spike_ydistance ** 2)
  
                if spikeDistance < totalDistance:
                    if spikeDistance > 0:
                        self.x += (spike_xdistance / spikeDistance) * self.speed
                        self.y += (spike_ydistance / spikeDistance) * self.speed

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
        self.appear_time = random.randint(100,200)
        self.disappear_time = random.randint(100,200)
        self.timer = 0

    def update(self, Player):
        self.timer += 1
        if self.timer < self.appear_time:
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
                
        elif self.timer < self.appear_time + self.disappear_time:
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


def boundary(thePlayer):
    drawRect(worldWidth, worldHeight,10000,10000,"black",5)
    
allSpikes = []

for i in range(5):
    allSpikes.append(Spikes(random.randint(0, int(worldWidth)), random.randint(0, int(worldHeight)), userScreenHeight/35, "spike.png"))
 
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
    boundary(thePlayer)
    
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