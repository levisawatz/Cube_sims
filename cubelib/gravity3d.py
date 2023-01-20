import random
from numpy.core.arrayprint import format_float_scientific
import pygame
import numpy as np
import math
BIG_G=1000000
class Body:
    
    name=0
    pos=np.array([0,0,0],float)
    radius=0
    vel=np.array([0,0,0],float)
    direction=np.array([0,0,0],float)
    mass=0
    force=np.array([0,0,0],float)
    acceleration=np.array([0,0,0],float)

    rot=np.array([0,0],float)
    def __init__(self,name,pos,radius,vel,direction,mass):
        self.name=name
        self.pos=np.array(pos,float)
        self.radius=radius
        self.vel=np.array(vel,float)
        self.direction=np.array(direction,float)
        self.mass=mass
        return
    
    

        
def move(bodies):
    #set vel
    
    
    for b1 in bodies:
        forces=np.array([0,0,0],float)
        for b2 in bodies:
            delta=b2.pos-b1.pos
            
            d=np.linalg.norm(delta)         
            if d>5:
                force=np.array([1,1,1],float) 
                if d<(b1.radius+b2.radius):
                    collide(b1,b2,delta)
                    #smush(b1,b2)
                    delta=b2.pos-b1.pos
                    d=np.linalg.norm(delta)
                    b1.rot=2*np.random.random(2)-np.array([1,1],float)
                    b2.rot=2*np.random.random(2)-np.array([1,1],float)
                   
                netforce=BIG_G*b1.mass*b2.mass/(d**2)
                force*=netforce*delta/d
                forces+=force
                
        b1.force=forces
        b1.acceleration=b1.force/b1.mass
        

        b1.vel+=b1.acceleration
    for b1 in bodies:
        b1.pos+=b1.vel
        
       # print('name:',b1.name,'vel:',mag(b1.vel))

def smush(b1,b2):
    vel=(b1.vel+b2.vel)/2
    b1.vel=np.copy(vel)
    b2.vel=np.copy(vel)
def collide(b1,b2,n):
    n/=np.linalg.norm(n)
    c=np.dot(n,b1.vel-b2.vel)
    
    b1.vel-=b2.mass*c/(b1.mass+b2.mass)*2*n
    b2.vel+=b1.mass*c/(b1.mass+b2.mass)*2*n
    b1.pos+=b1.vel
    b2.pos+=b2.vel
    return

def mag(x): 
    return math.sqrt(sum(i**2 for i in x))


def centerOfMass(bodies):
    netmass=0
    weightedPos=np.array([0.0,0.0])
    for i in bodies:
        weightedPos+=i.pos*i.mass
        netmass+=i.mass
    com=weightedPos/netmass
    return com


def draw(disp,bodies,bodyset,newbody,mousepos,fb,fn):
    white=(255,255,230)
    green =(0,255,0)
    red = (255,0,50)
    darkred=(115,10,50)
    bodynumber=0
    for i in bodies:
        if fb and bodynumber==fn:
            pygame.draw.circle(disp, darkred, i.pos, i.radius, width=0)
        else:
            pygame.draw.circle(disp, red, i.pos, i.radius, width=0)
        bodynumber+=1
    if bodyset>0:
        #pygame.draw.circle(disp, darkred, newbody.pos, newbody.radius, width=0)
        if bodyset==3:
            pygame.draw.line(disp, (0,0,0), newbody.pos,mousepos, width=7)

    pygame.display.update()



def distance(a,b):
    delx=b[0]-a[0]
    dely=b[1]-a[1]
    
    d=math.sqrt(delx**2+dely**2)
    return d
def follow(bodies,b1):
    shift=[800,600]-b1
    for i in bodies:
        i.pos+=shift
    return
    
def Velreset(bodies,b1):
    
    for i in bodies:
        i.vel-=b1
    return
 
def main():
    pygame.init()
    disp=pygame.display.set_mode((1600,1200))
    pygame.display.set_caption('gravity sim')
    clock= pygame.time.Clock()
    
    
    #bodyList=BodyList()
    mousepressed=False
    mousepos=(0,0)
    bodyList=[]
    nbindex=-1
    setvelconstant=.1

    bodyset=True
    followbool=False
    COMstep=0
    COMrecord=[0,0]
    orbit=False
    velreset=False
    vailidInp=['0','1','2','3','4','5','6','7','8','9']
    follownumber=-1
    setstep=0
    
    
    while True:
        for event in pygame.event.get():
            
            print(event)
            if event.type==pygame.QUIT or (event.type==pygame.KEYDOWN and event.scancode==41):
                pygame.quit()
                quit()
            if event.type==pygame.KEYDOWN:
                print(event)
                if event.scancode<=82 and event.scancode>=79:
                    print(event.scancode)
                if event.unicode=='p':  #play bool
                    
                    if play:
                        play=False
                        print('paused')
                    else:
                        print('play')
                        play=True
                if event.unicode=='n':  #new body
                    
                    if bodyset:
                        bodyset=False
                        setstep=0
                        bodyList.pop(nbindex)
                        nbindex-=1
                        print('creation cancelled')
                    else:
                        bodyset=True
                        print('create body')
                if event.unicode=='f':  #followbool
                    if followbool:
                        followbool=False
                        print('follow mode off')
                    else:
                        followbool=True
                        print('press number to follow body')
                if event.unicode=='o':  #orbit
                    if orbit!=0:
                        orbit=0
                        print('orbit cancelled')
                    else:
                        orbit=1
                        if not followbool:
                            followbool=True
                            follownumber=0
                if event.unicode=='v': #vel reset
                    velreset=True
                
                if event.unicode=='m': # center of mass
                    follow(bodyList,centerOfMass(bodyList))
                    COMstep=1
                
                if event.scancode==42: #delete recent
                    bodyList.pop(nbindex)
                    nbindex-=1
    
                if followbool:
                    if vailidInp.count(event.unicode)==1 and int(event.unicode)<len(bodyList):
                        follownumber=int(event.unicode)
                        print(follownumber)
                    
                   
            if event.type==pygame.MOUSEMOTION:
                    mousepos=event.pos
            if event.type==pygame.MOUSEBUTTONDOWN:
                mousepressed=True
            if event.type==pygame.MOUSEBUTTONUP:
                mousepressed=False
        if COMstep:
            COMstep+=1
            if COMstep==2:
                COMrecord[0]=np.copy(centerOfMass(bodyList))
            elif COMstep==3:
                COMrecord[1]=centerOfMass(bodyList)
                Velreset(bodyList,COMrecord[1]-COMrecord[0])
                COMstep==0
            


        if bodyset or (len(bodyList)==0): #bodyset fx
                bodyset=True
            
                if setstep==0:
                    play=False
                    nbindex+=1
                    bodyList.append(Body(nbindex,[100,100],20,[0,0],[0,0],10))
                    setstep=1
                if setstep==1:    
                    bodyList[nbindex].pos[0]=mousepos[0]
                    bodyList[nbindex].pos[1]=mousepos[1]
                    #print(bodyList[nbindex].pos)
                    if mousepressed:
                        setstep=2
                        mousepressed=False
                elif setstep==2:
                    bodyList[nbindex].radius=distance(bodyList[nbindex].pos,mousepos)
                    if mousepressed:
                        bodyList[nbindex].mass=bodyList[nbindex].radius**3
                        setstep=3
                        mousepressed=False
                elif setstep==3 and orbit !=0:
                    if orbit==1:
                        perp= bodyList[follownumber].pos-bodyList[nbindex].pos
                        tangent=np.array([-perp[1],perp[0]])/mag(perp)
                        orbitvel=15*math.sqrt(bodyList[follownumber].mass*BIG_G/mag(perp))

                        orbit=2
                    if orbit==2:
                        if np.dot(tangent,np.array(mousepos)-bodyList[nbindex].pos)<0:
                            tangent*=-1
                        if mousepressed:
                            bodyList[nbindex].vel=orbitvel*tangent
                            if followbool and follownumber!=-1:
                                bodyList[nbindex].vel+=bodyList[follownumber].vel
                            mousepressed=False
                            bodyset=False
                            setstep=0
                            play=True
                            orbit=0
                    mousepos=bodyList[nbindex].pos+tangent*orbitvel/setvelconstant

                    

                elif setstep==3:

                    bodyList[nbindex].direction=[bodyList[nbindex].pos,mousepos]
                    #pygame.draw.line(disp, (0,0,0), bodyList[nbindex].pos,mousepos, width=7)
                    if mousepressed:
                        bodyList[nbindex].vel=setvelconstant*(np.array(mousepos)-np.array(bodyList[nbindex].pos))
                        if followbool and follownumber!=-1:
                            bodyList[nbindex].vel+=bodyList[follownumber].vel
                        mousepressed=False
                        bodyset=False
                        setstep=0
                        play=True
        
 
       
        if followbool and follownumber!=-1:
            follow(bodyList,bodyList[follownumber].pos)
            if velreset:
                Velreset(bodyList,bodyList[follownumber].vel)
                followbool=False
                velreset=False

        if play:
            move(bodyList) 
             
        disp.fill((125,125,125))
        
        
        draw(disp,bodyList,setstep,bodyList[nbindex],mousepos,followbool,follownumber)
        
        
        clock.tick(60)
if __name__ == "__main__":

    main()