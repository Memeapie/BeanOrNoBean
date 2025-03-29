_GAME_FULLSCREEN = False
_SKIP_INTRO = True
_OBJECTS = []
_NO_BEANS = 11
_BEANS = ["1", "2", "5", "8", "13", "21", "36", "55", "100", "200", "500"]
_DECISION_MUSIC_COOLDOWN = 0
_BEANS_REMOVED = 0
_LAST_WIZARD_CALL = 0
_WIZARD_SUMMONED = False
_BEAN_OR_NO_BEAN = False
_GAME_STATE = 'HOLD'
_BEAN_ACCEPTED = False

import pygame as p
from pygame import mixer as m
import moviepy.editor as e
import random as rnd

if _GAME_FULLSCREEN:
    screen = p.display.set_mode((1920, 1080), p.FULLSCREEN)
else:
    screen = p.display.set_mode((1920, 1080), p.RESIZABLE)

font = p.font.SysFont('Arial Bold', 40)

class FadingBeanBox:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.x = -1000
        self.y = 0
        self.direction = 1
        self.alpha = 100
        self.image = p.image.load('assets/Logo-Large.png').convert_alpha()
        self.image.set_alpha(self.alpha)

        _OBJECTS.append(self)

    def process(self):
        self.x += self.direction

        if self.x > (self.width / 2) and self.direction == 1:
            self.alpha -= 1
            self.image.set_alpha(self.alpha)
        if self.x < (screen.get_width() - self.width*2) and self.direction == -1:
            self.alpha -= 1
            self.image.set_alpha(self.alpha)

        if self.alpha == 0:
            self.alpha = 100
            self.image.set_alpha(self.alpha)
            if self.direction == 1:
                self.direction = -1
                self.x = screen.get_width() + 1000
            elif self.direction == -1:
                self.direction = 1
                self.x = -1500

        screen.blit(self.image, (self.x, self.y))

class BeanBox:
    def __init__(self, x, y, width, height):
        self.x = x - (width / 2)
        self.y = y - (height / 2)
        self.image = p.transform.scale(p.image.load('assets/Logo-Large.png'), (width, height)).convert_alpha()
        self.animationTimer = 0

        _OBJECTS.append(self)

    def process(self):
        if not self.animationTimer == 255:
            self.animationTimer += 1

        if not _BEAN_OR_NO_BEAN and not _WIZARD_SUMMONED:
            alpha = self.animationTimer
            if alpha <= 0: alpha = 0
            self.image.set_alpha(alpha)
            screen.blit(self.image, (self.x, self.y))

        if _BEAN_OR_NO_BEAN and not _WIZARD_SUMMONED:
            self.animationTimer = -500
            self.image.set_alpha(255)
            screen.blit(self.image, (self.x, self.y))

class Background:
    def __init__(self):
        self.circleColours = [(8,8,8), (16,16,16), (24,24,24), (32,32,32), (40,40,40), (48,48,48), (56,56,56), (64,64,64), (72,72,72), (80,80,80)]
        self.surface = p.Surface(screen.get_size(), p.SRCALPHA, 32)
        self.res = screen.get_size()
        self.render()

    def render(self):
        iterations = len(self.circleColours)
        nextFrame = p.Surface(screen.get_size(), p.SRCALPHA, 32)
        for colour in self.circleColours:
            radius = ((screen.get_height() / len(self.circleColours)) * iterations)
            p.draw.circle(nextFrame, colour, (screen.get_width() / 2, screen.get_height() / 2), radius)
            iterations -= 1
        self.surface = p.transform.box_blur(nextFrame, 15)

    def process(self):
        if not self.res == screen.get_size():
            self.res = screen.get_size()
            self.render()
        screen.fill('Black')
        screen.blit(self.surface, (0,0))

class ParticleEmitter:
    def __init__(self, maxSpeed, reducer):
        self.particles = []
        self.maxSpeed = maxSpeed
        self.reducer = reducer
        self.colours = [(250, 250, 210), (238, 232, 170), (240, 230, 140), (218, 165, 32), (255, 215, 0), (255, 165, 0), (255, 140, 0), (205, 133, 63), (210, 105, 30), (139, 69, 19), (160, 82, 45)]

    def process(self):
        if self.particles:
            self.clean()
            for particle in self.particles:
                particle[0][1] += particle[2][0]
                particle[0][0] += particle[2][1]
                particle[1] -= self.reducer
                a = int(particle[1] * 15)
                if a < 0: a = 0
                surf = p.Surface((30,30), p.SRCALPHA, 32)
                p.draw.circle(surf, p.Color(particle[3]), [15,15], int(particle[1]))
                surf.set_alpha(a)
                screen.blit(surf, particle[0])

    def spawn(self):
        pos_x = rnd.randint(100, screen.get_width() - 100)
        pos_y = rnd.randint(100, screen.get_height() - 100)
        direction = [rnd.randint(-self.maxSpeed,self.maxSpeed),rnd.randint(-self.maxSpeed,self.maxSpeed)]
        if direction == [0,0]: direction = [1,1]
        radius = rnd.randint(3, 12)
        particle_circle = [[pos_x,pos_y],radius,direction,self.colours[rnd.randint(0,len(self.colours)-1)]]
        self.particles.append(particle_circle)

    def clean(self):
        particle_copy = [particle for particle in self.particles if particle[1] > 0]
        self.particles = particle_copy

class Button:
    def __init__(self, x, y, width, height, button_text='Button', onclick_function=None, one_press=False):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.onclickFunction = onclick_function
        self.onePress = one_press
        self.alreadyPressed = False

        self.fillColors = {
            'normal': '#5adbb5',
            'hover': '#5dbea3',
            'pressed': '#33b249',
        }

        self.buttonSurface = p.Surface((self.width, self.height))
        self.buttonRect = p.Rect(self.x, self.y, self.width, self.height)
        self.buttonSurf = font.render(button_text, True, (20, 20, 20))

        _OBJECTS.append(self)

    def process(self):
        mouse_pos = p.mouse.get_pos()
        self.buttonSurface.fill(self.fillColors['normal'])
        if self.buttonRect.collidepoint(mouse_pos):
            self.buttonSurface.fill(self.fillColors['hover'])
            if p.mouse.get_pressed(num_buttons=3)[0]:
                self.buttonSurface.fill(self.fillColors['pressed'])
                if self.onePress:
                    self.onclickFunction()
                elif not self.alreadyPressed:
                    self.onclickFunction()
                    self.alreadyPressed = True
            else:
                self.alreadyPressed = False

        if (_GAME_STATE == 'HOLD') or _BEAN_OR_NO_BEAN:
            self.buttonSurface.blit(self.buttonSurf, [
                self.buttonRect.width / 2 - self.buttonSurf.get_rect().width / 2,
                self.buttonRect.height / 2 - self.buttonSurf.get_rect().height / 2
            ])
            screen.blit(self.buttonSurface, self.buttonRect)

class AmountSlider:
    def __init__(self, x, y, width, height, amount, bean, iteration):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.amount = amount
        self.bean = bean
        self.pressed = False
        self.iteration = str(iteration+1)
        self.animationTimer = -1
        self.state = "hiya"

        self.sliderImage = p.image.load("assets/" + self.bean + "-" + self.iteration + ".png").convert_alpha()
        self.sliderRect = p.Rect(self.x, self.y, self.width, self.height)
        self.sliderText = font.render(self.amount + " BEAN", True, (255, 255, 255))
        self.fontSizeWidth, self.fontSizeHeight = font.size(self.amount + " BEAN")
        self.sliderTextRect = p.Rect(self.x + (self.width / 2) - (self.fontSizeWidth / 2), self.y + (self.height / 2) - (self.fontSizeHeight / 2), self.width, self.height)

        _OBJECTS.append(self)

    def update(self):
        self.sliderRect = p.Rect(self.x, self.y, self.width, self.height)
        self.sliderText = font.render(self.amount + " BEAN", True, (255, 255, 255))
        self.fontSizeWidth, self.fontSizeHeight = font.size(self.amount + " BEAN")
        self.sliderTextRect = p.Rect(self.x + (self.width / 2) - (self.fontSizeWidth / 2), self.y + (self.height / 2) - (self.fontSizeHeight / 2), self.width, self.height)

    def process(self):
        global _DECISION_MUSIC_COOLDOWN, _BEANS_REMOVED
        if not self.pressed and not _BEAN_OR_NO_BEAN and not _WIZARD_SUMMONED:
            mouse_pos = p.mouse.get_pos()
            if self.sliderRect.collidepoint(mouse_pos):
                if p.mouse.get_pressed(num_buttons=3)[0]:
                    self.pressed = True
                    if self.iteration == _BEANS[len(_BEANS)-1]:
                        play_sound_effect('assets/big_beans_gone.mp3')
                    else:
                        play_sound_effect('assets/box_open.mp3')
                    self.animationTimer = 200
                    self.state = "bye bye"

        if self.animationTimer > 0 and self.state == "bye bye":
            self.animationTimer -= 1
            if self.animationTimer == 0:
                play_sound_effect('assets/woosh.mp3')
                self.state = "woosh"
                self.animationTimer = 100

        if self.animationTimer > 0 and self.state == "woosh":
            self.animationTimer -= 1
            if self.x < (screen.get_width() / 2):
                self.x -= 8
            else:
                self.x += 8
            self.update()

            if self.animationTimer == 0:
                self.state = "gone"
                _DECISION_MUSIC_COOLDOWN = 480
                _BEANS_REMOVED += 1

        if not self.state == "gone":
            screen.blit(self.sliderImage, self.sliderRect)
            screen.blit(self.sliderText, self.sliderTextRect)

class FireworkParticle:

    def __init__(self, pos, colour, direction, velocity, size, lifetime,
                 hasTrail=False, shrink=False,
                 trailColour=None, trailPercent=0.4, gravity=0.005):
        self.pos = [float(pos[0]), float(pos[1])]
        self.colour = colour
        self.direction = direction
        self.velocity = velocity
        self.size = size
        self.hasTrail = hasTrail
        self.lifetime = lifetime
        self.age = 0
        self.shrink = shrink
        self.gravity = gravity

        self.surface = p.Surface((size, size))
        self.surface.fill(self.colour)

        if hasTrail and rnd.uniform(0, 1) < trailPercent:
            self.spawn_trail(trailColour)

        _OBJECTS.append(self)

    def process(self):
        for axis in (0, 1):
            self.pos[axis] += self.direction[axis] * self.velocity * 0.5
        self.direction[1] += self.gravity * 0.5
        self.age += 0.1
        if self.age > self.lifetime:
            self.die()
            return

        if self.shrink:
            newSurfSize = self.size*(1 - self.age/self.lifetime)
            self.surface = p.Surface((newSurfSize, newSurfSize))
            self.surface.fill(self.colour)
        screen.blit(self.surface, self.pos)

    def die(self):
        if self in _OBJECTS:
            _OBJECTS.remove(self)

    def spawn_trail(self, trailColour):
        FireworkParticle(self.pos, trailColour, self.direction, self.velocity*2, self.size*0.25, lifetime=self.lifetime*2.5)

class Firework:
    def __init__(self, pos, colour, velocity, particleSize, sparsity, hasTrail, lifetime):
        # sparsity is between 0 and 1, higher values mean fewer particles
        trailColour = [rnd.uniform(0, 255),
                       rnd.uniform(0, 255),
                       rnd.uniform(0, 255)]
        xDir = -0.5
        while xDir <= 0.5:
            yDir = -0.5
            while yDir <= 0.5:
                if xDir == yDir == 0:
                    continue
                if (xDir * xDir + yDir * yDir) <= 0.5*0.5:
                    FireworkParticle(pos=pos,
                             colour=colour,
                             direction=[xDir, yDir],
                             velocity=velocity + rnd.uniform(-2, 2),
                             size=particleSize,
                             hasTrail=hasTrail,
                             lifetime=lifetime + rnd.uniform(-3, 3),
                             shrink=True,
                             trailColour=trailColour)
                yDir += sparsity
            xDir += sparsity

class Bean:
    def __init__(self, bean):
        self.x = screen.get_width() / 2
        self.y = screen.get_height() / 2
        self.animationTimer = 200
        self.image = p.image.load('assets/'+ bean +'.png').convert_alpha()
        self.x -= self.image.get_width() / 2

        _OBJECTS.append(self)

    def process(self):
        self.y -= 1
        self.animationTimer -= 1
        self.image.set_alpha(self.animationTimer)
        screen.blit(self.image, (self.x, self.y))

        if self.animationTimer == 0:
            _OBJECTS.remove(self)

class BeanWizard:
    def __init__(self):
        self.image = p.image.load("assets/bean_wizard_"+ str(rnd.randint(0,3)) + ".png").convert_alpha()
        self.fog = p.image.load("assets/fog.png").convert_alpha()
        self.pos = [(screen.get_width() / 2) - (self.image.get_width() / 2), (screen.get_height() / 2) - (self.image.get_height() / 2)]
        self.animationTimer = 0
        self.fogAnimationTimer = 255

        _OBJECTS.append(self)

    def process(self):
        self.animationTimer += 1
        alpha = self.animationTimer
        if self.animationTimer > 250:
            alpha = 250 - (self.animationTimer - 250)
            self.fogAnimationTimer -= 1
        if self.animationTimer >= 500:
            _OBJECTS.remove(self)

        self.image.set_alpha(alpha)
        screen.blit(self.image, self.pos)

        self.fog.set_alpha(self.fogAnimationTimer)
        screen.blit(self.fog, ((self.animationTimer * 2) - self.fog.get_width(), screen.get_height() - self.fog.get_height()))
        screen.blit(p.transform.flip(self.fog, True, False), (screen.get_width() - (self.animationTimer * 2), screen.get_height() - self.fog.get_height()))

def spawn_firework(pos_x, pos_y):
    Firework(pos=(pos_x, pos_y),
             colour=[rnd.uniform(0, 255), rnd.uniform(0, 255), rnd.uniform(0, 255)],
             velocity=rnd.uniform(40, 60),
             particleSize=rnd.uniform(10, 15),
             sparsity=rnd.uniform(0.05, 0.15),
             hasTrail=True,
             lifetime=rnd.uniform(10, 20))

def intro():
    clip = e.VideoFileClip('assets/intro_video.mp4')

    if _GAME_FULLSCREEN:
        clip.preview(fullscreen=True)
    else:
        clip.preview()

def ready_up():
    global _GAME_STATE
    _GAME_STATE = 'BEAN'

def init_holding():
    spawn_firework(screen.get_width() / 2, screen.get_height() / 2)
    Button(screen.get_width() / 2 - 100, screen.get_height() / 2 - 50, 200, 100, 'Ready!', ready_up)
    game_loop()

def decision_music():
    global _DECISION_MUSIC_COOLDOWN
    if not _WIZARD_SUMMONED and not _BEAN_OR_NO_BEAN:
        if _DECISION_MUSIC_COOLDOWN > 0:
            _DECISION_MUSIC_COOLDOWN -= 1
        if _DECISION_MUSIC_COOLDOWN == 1:
            m.music.stop()
            m.music.load("assets/decision_" + str(rnd.randint(1,3)) + ".mp3")
            m.music.set_volume(0.4)
            m.music.play()

def play_sound_effect(sound_effect, loop = 0):
    m.music.stop()
    m.music.load(sound_effect)
    m.music.set_volume(1)
    m.music.play(loop)

def deal():
    global _BEAN_OR_NO_BEAN, _BEAN_ACCEPTED
    _BEAN_OR_NO_BEAN = False
    _BEAN_ACCEPTED = True
    spawn_firework(screen.get_width() / 2, screen.get_height() / 2)
    spawn_firework(screen.get_width() / 4, (screen.get_width() / 4) * 3)
    spawn_firework((screen.get_width() / 4) * 3, (screen.get_width() / 4) * 3)
    play_sound_effect("assets/deal.mp3")
    Bean("bean")

def no_deal():
    global _BEAN_OR_NO_BEAN
    _BEAN_OR_NO_BEAN = False
    Bean("no_bean")

def wizard_rings():
    global _BEANS_REMOVED, _LAST_WIZARD_CALL, _DECISION_MUSIC_COOLDOWN, _WIZARD_SUMMONED, _BEAN_OR_NO_BEAN
    if not(_BEANS_REMOVED == _LAST_WIZARD_CALL) and not _BEAN_ACCEPTED:
        if (_BEANS_REMOVED % 3 == 0) and (_DECISION_MUSIC_COOLDOWN < 50):
            print(_BEAN_ACCEPTED)
            _LAST_WIZARD_CALL = _BEANS_REMOVED
            play_sound_effect('assets/phone_ring.mp3')
            m.music.set_volume(1)
            _WIZARD_SUMMONED = True
            BeanWizard()

    if _WIZARD_SUMMONED and not m.music.get_busy():
        play_sound_effect('assets/bean_wizard.mp3', -1)
        m.music.set_volume(0.7)
        _WIZARD_SUMMONED = False
        _BEAN_OR_NO_BEAN = True
        _DECISION_MUSIC_COOLDOWN = 400

def init_bean():
    global _GAME_STATE

    FadingBeanBox(412, 412)
    BeanBox(screen.get_width() / 2, screen.get_height() / 2, 256, 256)

    sliderOffset = (screen.get_height() - (len(_BEANS) * 100)) / 2
    beanCounter = 0
    for bean in _BEANS:
        AmountSlider(screen.get_width() - 375, sliderOffset + (beanCounter * 100), 375, 87, bean, "red", beanCounter)
        beanCounter += 1

    sliderOffset = (screen.get_height() - (_NO_BEANS * 100)) / 2
    beanCounter = 0
    while not (beanCounter == _NO_BEANS):
        AmountSlider(0, sliderOffset + (beanCounter * 100), 375, 87, "NO", "blue", beanCounter)
        beanCounter += 1

    Button(screen.get_width() / 2 - 300, screen.get_height() / 4, 200, 100, 'BEAN', deal)
    Button(screen.get_width() / 2 + 100, screen.get_height() / 4, 200, 100, 'NO BEAN', no_deal)

    play_sound_effect('assets/ambience.mp3', -1)
    _GAME_STATE = 'BEAN'
    game_loop(ParticleEmitter(1, 0.1))

def game_loop(
        particles = ParticleEmitter(2, 0.05),
        particleEvent = p.USEREVENT + 1,
        background = Background()
):
    clock = p.time.Clock()
    p.time.set_timer(particleEvent, 30)

    gameState = _GAME_STATE
    while gameState == _GAME_STATE:
        for event in p.event.get():
            if event.type == p.QUIT:
                quit()
            if event.type == particleEvent:
                particles.spawn()

        background.process()
        particles.process()

        for object in _OBJECTS:
            object.process()

        if _GAME_STATE == 'BEAN':
            decision_music()
            wizard_rings()

        p.display.flip()

        clock.tick(60)

    _OBJECTS.clear()

def game_init():
    p.init()
    m.init()

    init_holding()

    if not _SKIP_INTRO:
        intro()

    init_bean()
    p.quit()

if __name__ == '__main__':
    game_init()
