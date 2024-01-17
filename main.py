import pygame
from pygame import draw, font, transform, Color, gfxdraw, Vector2, Vector3
from random import uniform, randint
import math
from threading import Thread
import time

from typing import overload, Union, Generic, Any, Callable

WIDTH, HEIGHT = 500, 500

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Partickl')

transform.set_smoothscale_backend('SSE')

class Particle:
    
    pos: Vector2
    tgt: Vector2
    
    clr: Vector3
    clrtgt: Vector3
    
    def __init__(self,pos:Vector2,tgt:Vector2=Vector2(0,0),clr:Vector3=Vector3(255,255,255),clrtgt:Vector3=Vector3(0,0,0)):
        self.pos = pos
        self.tgt = tgt
        self.clr = clr
        self.clrtgt = clrtgt
        
    def copy(self) -> 'Particle':
        return Particle(self.pos.copy(),self.tgt.copy())

    def draw(self,surf:pygame.Surface):
        #draw.circle(surf,Color(255,255,255,255),self.pos,1)
        draw.rect(surf,(self.clr.x,self.clr.y,self.clr.z,255),(self.pos.x+WIDTH/2,self.pos.y+HEIGHT/2,1,1))
        
    def update(self,dt:float,particles:list['Particle']):
        #self.pos += (self.tgt-self.pos)/.1*dt
        #self.clr += (self.clrtgt-self.clr)/.1*dt
        self.pos += (self.tgt-self.pos)/50
        self.clr += (self.clrtgt-self.clr)/50
        if (self.pos-self.tgt).length() < 1:
            self.pos = self.tgt.copy()

running = True
particles:list[Particle] = [Particle(Vector2(uniform(-WIDTH/2,+WIDTH/2),uniform(-HEIGHT/2,+HEIGHT/2)),clr=Vector3(uniform(0,255),uniform(0,255),uniform(0,255))) for _ in range(250000//5)]

def refresh_targets(poses:list[Vector2],unref:bool=True):
    if unref: poses = [*poses]
    for p in particles:
        if len(poses) == 0:
            theta = uniform(0,math.pi*2)
            rad = ((WIDTH/2)**2+(HEIGHT/2)**2)**.5
            p.tgt = Vector2(math.cos(theta)*rad,math.sin(theta)*rad)
        else:
            t = poses.pop(randint(0,len(poses)-1))
            p.tgt,p.clrtgt = t

refresh_targets([ (Vector2(x,y),Vector3(255,255,255)) for x in range(-10,10) for y in range(-10,10) ])

def update_thread_fn():
    global particles, running, pause
    t = time.time()
    while running:
        pt = [p.copy() for p in particles]
        for p in particles:
            p.update(time.time()-t,pt)
        t = time.time()
        
def refresh_thread_fn(img:pygame.Surface):
    global imgposes
    rec = lambda v: v**.5
    sz = min(WIDTH,HEIGHT)
    if img.get_width() > img.get_height():
        img = transform.scale(img,(sz,(sz/img.get_width())*img.get_height()))
    else:
        img = transform.scale(img,((sz/img.get_height())*img.get_width(),sz))
    tgt = []
    w,h = img.get_size()
    for x in range(w):
        for y in range(h):
            clr = img.get_at((x,y))
            if randint(0,256) < rec((clr.grayscale().r*(clr.a/255))/255)*255:
                tgt.append((Vector2(x-w/2,y-h/2),Vector3(clr.r,clr.g,clr.b)))
    imgposes = tgt
    refresh_targets(imgposes,False)

imgposes = []

try:        

    frame = 0

    update_thread = Thread(target=update_thread_fn)
    update_thread.start()

    while running:
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.DROPFILE:
                img = pygame.image.load(event.file)
                refresh_thread = Thread(target=refresh_thread_fn,args=(img,))
                refresh_thread.start()
        
        scr = pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)
        
        for p in particles:
            p.draw(scr)
            
        if pygame.mouse.get_pressed()[0]:
            for _ in range(10):
                tgt: Vector2 = None
                clrtgt: Vector2 = None
                if len(imgposes) == 0:
                    theta = uniform(0,math.pi*2)
                    rad = ((WIDTH/2)**2+(HEIGHT/2)**2)**.5
                    tgt = Vector2(math.cos(theta)*rad,math.sin(theta)*rad)
                    clrtgt = Vector3(uniform(0,255),uniform(0,255),uniform(0,255))
                else:
                    t = imgposes.pop(randint(0,len(imgposes)-1))
                    tgt,clrtgt = t
                particles.append(Particle(Vector2(pygame.mouse.get_pos())-Vector2(WIDTH/2,HEIGHT/2),tgt,Vector3(uniform(0,255),uniform(0,255),uniform(0,255)),clrtgt))
                
        if pygame.mouse.get_pressed()[2]:
            for _ in range(50):
                if len(particles): particles.pop(randint(0,len(particles)-1))
            
        screen.fill(Color(0,0,0))
        screen.blit(scr,(0,0))

        pygame.display.flip()
        
        frame += 1
        
except BaseException as e:
    
    print(e.argqres)
    
finally:
    
    running = False
    pygame.quit()