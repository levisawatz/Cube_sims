import random
import pygame
import numpy as np
import math
import time

from cubelib import gravity3d as g

CAMERAPOS0=[-5000,0,3000]
CAMERADIR02=np.array([.66,0,-.30],float)

SCREENDIST=700
DISPWIDTH=1200
DISPHIGHT=850
COSVIEWANGLE=SCREENDIST/math.sqrt((DISPWIDTH/2)**2+(DISPHIGHT/2)**2+SCREENDIST**2)

ROTATEVEL=.00005
CUBEROTMAX=.5
CAMVEL=300
SHOTVEL=500
SHOTSTEPS=8
MCP=(1050,700)
MCPR=50
SENSY=.001
SENSZ=.001
SENSMAX=1
black=(0,0,0)
white=(255,255,230)
grey=(100,100,100)
green =(0,255,0)
red = (255,0,50)
blue=(5,5,255)
yellow=(255,255,10)
orange=(255,160,5)
fcolor=[green,red,white,yellow,orange,blue]
#       -x     -y   +z  -z      +y     +x

    
vcsigns=np.array([[1,1,1],
                [-1,1,1],
                [-1,-1,1],
                [1,-1,1],
                [1,-1,-1],
                [-1,-1,-1],
                [-1,1,-1],
                [1,1,-1]])
face=np.array([[0,3,4,7],
        [0,1,6,7],
        [0,1,2,3],
        [4,5,6,7],
        [2,3,4,5],
        [1,2,5,6]],int)

def display(disp,cube,cam):
    ##verts=cube.vertcalc()
    disptime0=time.time()
        
    verts=np.zeros((8,3),float)
    for i in range(8):
        verts[i]=np.array(cube.center) + np.dot(cube.coords,vcsigns[i]*cube.slen/2)
    ##print(" test time, sec:")
    ##print(time.time()-disptime0)   
    order=facedist(verts,cam.camerapos)
    dotrc=res=d=0.0
    x=y=0
    toobig=0
    
    
    for i in range(3):
        v=np.zeros((4,2))
        
        for j in range(4):
            rayd=verts[face[order[3+i],j]]-cam.camerapos
            dotrc=np.dot(rayd,cam.direction[0])
            if dotrc<0.1: #toobig
                toobig=1
                # print("dotrc!!!!!!!!!")
                # print(i,j)
                break

            d=np.dot((cam.screencenter-cam.camerapos),cam.direction[0])/dotrc
            point=cam.camerapos+d*rayd
            v1=point-cam.screencenter
            
            v1m=np.linalg.norm(v1)
            if v1m>5000:
                toobig=1
                # print("TOOBIG")
                break
            v1/=v1m
            res=np.dot(cam.direction[2],v1)
            y=round(res*v1m)
            
            x=round(v1m*math.sin(math.acos(res)))
            if (np.dot(v1,cam.direction[1])<0):
                x=-x
            x+=DISPWIDTH//2
            y+=DISPHIGHT//2
            
            v[j]=[x,y]
        if not toobig:
            pygame.draw.polygon(disp,cube.color[order[i+3]], v )

            ##pygame.draw.polygon(disp,cube.color[order[i+3]], ((v[0,0],v[0,1]),(v[1,0],v[1,1]),(v[2,0],v[2,1]),(v[3,0],v[3,1])) )
def disp2(disp,fps,inframe):
    pygame.draw.circle(disp, (150,150,255), MCP, MCPR, width=0)
    pygame.draw.circle(disp, (0,0,0), (DISPWIDTH/2,DISPHIGHT/2), 2, width=0)
    ab1=f"FPS: {round(fps,3)}"
    ab2=f"In Frame: {inframe}"
    tilefont = pygame.font.Font('freesansbold.ttf', 30)
    text = tilefont.render(ab1, True, grey)
    text2 = tilefont.render(ab2, True, grey)

    textRect = text.get_rect()
    textRect.center = (150,40)
    disp.blit(text, textRect)
    textRect = text2.get_rect()
    textRect.center = (160,80)
    disp.blit(text2, textRect)
class Camera:
    camerapos=np.array(CAMERAPOS0,float)
    
    direction=np.array([[1,0,0],
                        [0,1,0],
                        [0,0,1]],float)
    screencenter=np.array(camerapos-SCREENDIST*direction[0])
    def __init__(self,pos):
        self.camerapos=np.array(pos,float)
        self.setdirection()
        self.screencenter=np.array(self.camerapos-SCREENDIST*self.direction[0])
    def setdirection(self):
        self.direction[0]=CAMERADIR02/np.linalg.norm(CAMERADIR02)
        self.direction[1]=np.cross(np.array([0,0,1],float),self.direction[0])
        self.direction[1]/=np.linalg.norm(self.direction[1])
        self.direction[2]=np.cross(self.direction[0],self.direction[1])

class Cube:
    worryindex=[]
    def __init__(self,center,slen,color_std_rand):
        '''
        center [v3]
        slen (int or [v3])
        colour: 'std' else rand
        '''
        self.center=np.array(center)
        try:
            a=int(slen)
            self.slen=np.array([a,a,a])
        except TypeError:
            self.slen=np.array(slen)
        
        self.radius=np.linalg.norm(self.slen)/2
        self.coords=np.array([[1,0,0],[0,1,0],[0,0,1]])
        self.vert=self.vertcalc()
        
        if color_std_rand=='std':
            self.color=np.copy(fcolor)
        
        else:
            self.color=[]
            for i in range(6):
                self.color.append(tuple(np.random.randint(0,255,3)))

        self.body=g.Body(0,self.center,np.average(slen),[0,0,1],[0,0,1],abs(self.slen[0]*self.slen[1]*self.slen[2])/10**7)
            
    def colorme(self,c):
        for i in range(6):
            self.color[i]=c
        print('coloured')

    def vertcalc(self):
        v=np.zeros((8,3),float)
        for i in range(8):
            v[i]=np.array(self.center) + np.dot(self.coords,vcsigns[i]*self.slen/2)
        return v


# rubix test
class Rbx:
    cubes=[]
    center=np.array([0,0,0],float)
    coords=np.array([[1,0,0],[0,1,0],[0,0,1]],float)
    rotateface='u'
    rotspeed=.05
    currentoffset=0.0
def rotrbx(rbx):
    if rbx.rotateface=='u':
        face=[]
        ang=rbx.rotspeed
        for i in rbx.cubes:
            if np.dot(i.center-rbx.center,rbx.coords[2])>12:
                #face.append([i,i.center-rbx.center])
                i.center=rbx.center+np.dot(zrot(ang),i.center-rbx.center)
                i.coords=np.dot(zrot(ang),i.coords)
    rbx.currentoffset+=abs(rbx.rotspeed)
    if rbx.currentoffset>math.pi/2:
        overshoot=rbx.currentoffset-math.pi/2
        ang=-overshoot*abs(ang)/ang
        for i in rbx.cubes:
            if np.dot(i.center-rbx.center,rbx.coords[2])>12:
                #face.append([i,i.center-rbx.center])
                i.center=rbx.center+np.dot(zrot(ang),i.center-rbx.center)
                i.coords=np.dot(zrot(ang),i.coords)
        rbx.rotateface=False
        rbx.currentoffset=0
        rbx.rotspeed=0
# def arrangeRubix():
#     cubes=[]
#     slen=200
#     for i in range(3):
#         for j in range(3):
#             for k in range(3):
#                 if not (1==i==j==k):
#                     cubes.append(Cube(1.1*slen*np.array([i-.5,j-.5,k-.5]),slen,'std'))
#                 else:
#                     print(f"real center: {1.1*slen*np.array([i-.5,j-.5,k-.5])}") 
#     return cubes
            
    


def facedist(verts,campos):
    dist=[0.0,0.0,0.0,0.0,0.0,0.0]
    ret=[0.0,0.0,0.0,0.0,0.0,0.0]
    for i in range(6):
        for j in range(2):
            dist[i]+= np.linalg.norm(verts[face[i,j*2]]-campos)
    for i in range(6):
        ind=dist.index(max(dist))
        dist[ind]=0
        ret[i]=ind
    return ret
def cubedist(cubes,campos):
    dist=[]
    ret=[]
    bigg=0
    ind=0
    for i in range(len(cubes)):
        
        dist.append(np.linalg.norm(cubes[i].center-campos))
    for i in range(len(cubes)):
        bigg=max(dist)
        ind=dist.index(bigg)
        dist[ind]=0
        ret.append(ind)
    return ret


def xrot(a):
    return np.array([[1,0,0],
                    [0, math.cos(a),-math.sin(a)],
                    [0,math.sin(a),math.cos(a)]],float)
def yrot(a):
    return np.array([[math.cos(a),0,math.sin(a)],
                    [0, 1,0],
                    [-math.sin(a),0,math.cos(a)]],float)
def zrot(a):
    return np.array([[math.cos(a),-math.sin(a),0],
                    [math.sin(a),math.cos(a),0],
                    [0,0,1]],float)
def rotatebyaxis(axis,t):
    a=axis[0]
    b=axis[1]
    c=axis[2]
    d=math.sqrt(b*b+c*c)
    rx=np.array([[1,0,0],
                [0,c/d,-b/d],
                [0,b/d,c/d]],float)
    ry=np.array([[d,0,-a],
                [0,1,0],
                [a,0,d]],float)
        
    T=np.dot(np.dot(np.linalg.inv(rx),np.linalg.inv(ry)),zrot(t))
    ret= np.dot(T,np.dot(ry,rx))
    return ret
        
def distpoint2line(a,b,dir):
    # point:A line: B + dir    
    return np.linalg.norm(np.cross(dir,b-a))
def resetstd(slen,num):
    prb=num/slen**3
    cubes=[]
    for i in range(slen) :
        for j in range(slen):
            for k in range(slen):
                if random.random()<prb:
                    cubes.append(Cube(3000*np.array([i-slen/2,j-slen/2,k-slen/2]),np.random.randint(500,1000,3),0))
    return cubes




                

# shooting
def worry(cubes,pos,vel):
    worry = []
    for i in range(len(cubes)):
        dist=distpoint2line(cubes[i].center,pos,vel/np.linalg.norm(vel))
        
        if dist<cubes[i].radius:
            worry.append(i)
    return worry

def explode(cube0):
    cubes=[]
    nmass=cube0.body.mass/8
    for i in range(2) :
        for j in range(2):
            for k in range(2):
                ncube=Cube(cube0.center+1.5*cube0.slen*np.array([i-.5,j-.5,k-.5]),cube0.slen/2,'std')
                ncube.body.mass=nmass
                ncube.color=np.copy(cube0.color)
                ncube.body.vel=np.copy(cube0.body.vel)+600*(ncube.center-cube0.center)/np.linalg.norm(ncube.center-cube0.center)
                ncube.body.rot=2*np.random.random(2)-np.array([1,1],float)
                cubes.append(ncube)
    return cubes


def main():
    pygame.init()
    disp=pygame.display.set_mode((DISPWIDTH,DISPHIGHT))
    pygame.display.set_caption('CUBES!!!')
    #pygame.mouse.set_visible(False)
    clock= pygame.time.Clock()
    cam=Camera(CAMERAPOS0)
    pmp=mousepos=(0,0)
    mousebutton=0
    begintime=time.time()
    framenum=0
    fps=1
    dist=dotrc=0
    senszz=SENSZ
    sensyy=SENSY
    
    cubes=[]
    shootcubes=[]
    rbx=Rbx()
    

    grav=False
    
    
    cubes=resetstd(6,40)
    
    rightc=upc=forc=leftrc=downrc=0
    while True:
        framenum+=1
        
        if mousebutton:
            pmp=np.array(mousepos)

        
        for event in pygame.event.get():
            
            ##print(event)
            if event.type==pygame.QUIT or (event.type==pygame.KEYDOWN and event.scancode==41):
                pygame.quit()
                quit()
            if event.type==pygame.KEYDOWN:
                print(event)
                lastkey=event.unicode
                if event.scancode==80:##left
                    rightc=-1
                elif event.scancode==79:##right
                    rightc=1
                if event.scancode==82:##up
                    upc=1
                elif event.scancode==81:##down
                    upc=-1
                if event.scancode==54:##back <
                    forc=-1
                elif event.scancode==55:##forward >
                    forc=1
                if event.unicode=='w':
                    downrc=-1
                elif event.unicode=='s':
                    downrc=1
                if event.unicode=='a':
                    leftrc=1
                elif event.unicode=='d':
                    leftrc=-1
                if event.unicode=='r':
                    grav=False
                    cubes=resetstd(7,32)

                if event.unicode=='1': #random
                    grav=False
                    cubes=resetstd(6,40)
                      
                if event.unicode=='2': # solar system
                    grav=True
                    cubes=[]
                    ncubes3=6
                    prbcubes=.11
                    for i in range(ncubes3) :
                        for j in range(ncubes3):
                            for k in range(ncubes3):
                                if not(i or k or j):
                                    newcube=Cube(3000*np.array([0,0,0]),2000,0)
                                    newcube.colorme(red)
                                    newcube.body.mass*=100
                                    cubes.append(newcube)
                                elif random.random()<prbcubes:
                                    newcube=Cube(5000*np.array([i-ncubes3/2,j-ncubes3/2,k-ncubes3/2]),np.random.randint(500,1000,3),0)
                                    newcubedir=np.cross(newcube.center,np.array([0,0,1],float))
                                    newcube.body.vel=newcubedir/np.linalg.norm(newcubedir)*8*10000/math.sqrt(np.linalg.norm(newcube.center))
                                    newcube.body.rot=[0,.24*(random.random()-.5)]
                                    cubes.append(newcube)

                if event.unicode=='3':
                    grav=False
                    cubes=resetstd(6,216)

                             
                
                if event.unicode=='g':
                    if grav:
                        grav=False
                    else:
                        grav=True

                                    
                if event.scancode==229:##shift 
                    shot=Cube(cam.camerapos+100*cam.direction[0],100,'std')
                    shot.vel=cam.direction[0]*SHOTVEL
                    shot.worryindex=worry(cubes,shot.center,shot.vel)
                    shot.colorme(red)
                    shootcubes.append(shot)
                    print(shot.vel,shot.center)



                
                if event.scancode==44:##space
                    if mousebutton:
                        mousebutton=0
                    else:
                        mousebutton=1
                        
            elif event.type==pygame.KEYUP:                

                if event.scancode==79 or event.scancode==80:##right
                    rightc=0
                if event.scancode==82 or event.scancode==81:##up
                    upc=0
                if event.scancode==54 or event.scancode==55:
                    forc=0
                if event.scancode==26 or event.scancode==22:
                    downrc=0 
                    sensyy=SENSY
                if event.scancode==4 or event.scancode==7:
                    leftrc=0
                    senszz=SENSZ
               ## if event.scancode==44:##back
                 ##   mousebutton=0
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pass##mousebutton=1
            elif event.type == pygame.MOUSEBUTTONUP:
                pass##mousebutton=0
            elif event.type==pygame.MOUSEMOTION: 
                mousepos=event.pos

        #cube rotation
        mpa=np.array(mousepos)
        if np.linalg.norm(mpa-np.array(MCP))<MCPR:
            for c in cubes:  
                c.coords=np.dot(yrot(ROTATEVEL*-(MCP[1]-mousepos[1])*abs(MCP[1]-mousepos[1])),c.coords)
                c.coords=np.dot(zrot(ROTATEVEL*-(MCP[0]-mousepos[0])*abs(MCP[0]-mousepos[0])),c.coords)
        else:
            for c in cubes:  
                c.coords=np.dot(yrot(c.body.rot[0]*CUBEROTMAX),c.coords)
                c.coords=np.dot(zrot(c.body.rot[1]*CUBEROTMAX),c.coords)
        
        #cam rotation
        if downrc or leftrc:
            rotsens=.2
            zzyyacc=.05
            if downrc:
                sensyy+=zzyyacc
                if sensyy>SENSMAX:
                    sensyy=SENSMAX
                
                cam.direction=np.dot(yrot(-sensyy*downrc*rotsens),cam.direction)
            if leftrc:
                senszz+=zzyyacc
                if senszz>SENSMAX:
                    senszz=SENSMAX
                cam.direction=np.dot(zrot(-senszz*leftrc*rotsens),cam.direction)
            cam.screencenter=np.array(cam.camerapos-SCREENDIST*cam.direction[0])
        elif mousebutton and (pmp[0]!=mpa[0] or pmp[1]!=mpa[1]) and np.linalg.norm(mpa-pmp)<80:
            cam.direction=np.dot(yrot(SENSZ*(mpa[1]-pmp[1])),cam.direction)
            cam.direction=np.dot(zrot(SENSZ*-(mpa[0]-pmp[0])),cam.direction)  
            cam.direction=np.dot(xrot(-math.asin(cam.direction[1,1])),cam.direction)
   
            cam.screencenter=np.array(cam.camerapos-SCREENDIST*cam.direction[0])
        
        ##cam motion
        if rightc:
            cam.camerapos-=rightc*CAMVEL*cam.direction[1]
            cam.screencenter=np.array(cam.camerapos-SCREENDIST*cam.direction[0])
        if upc:
            cam.camerapos[2]+=upc*CAMVEL
            cam.screencenter=np.array(cam.camerapos-SCREENDIST*cam.direction[0])
        if forc:
            cam.camerapos+=forc*cam.direction[0]*CAMVEL
            cam.screencenter=np.array(cam.camerapos-SCREENDIST*cam.direction[0])
            #cam.__init__(cam.camerapos)
        
        #move shots
        for s in shootcubes:
            s.center+=s.vel
            #print(s.worryindex)
            s.worryindex=worry(cubes,s.center,s.vel)
            for i in s.worryindex:
                if np.linalg.norm(cubes[i].center-s.center)<2*SHOTVEL+cubes[i].radius:
                    for qtrstp in range(SHOTSTEPS):
                        ctop=s.center-s.vel*qtrstp/SHOTSTEPS-cubes[i].center
                        pop=True
                        for j in range(3):
                            if abs(np.dot(ctop,cubes[i].coords[j]))>cubes[i].slen[j]/2:
                                pop=False
                                break
                        if pop:
                            if grav:
                                newcubes=explode(cubes[i])
                                cubes+=newcubes
                            
                            cubes.pop(i)
                            
                            for s in shootcubes:
                                s.worryindex=worry(cubes,s.center,s.vel)
                            break
                        
                    print("popped")
                    break

        try:
            if np.linalg.norm(shootcubes[0].center-cam.camerapos)>60000:
                shootcubes.pop(0)
        except IndexError:
            pass
        


        disp.fill((220,220,190))
        allcubes=np.copy(cubes)
        if grav:
            g.move([c.body for c in allcubes])
            for c in allcubes:
                c.center=c.body.pos
        allcubes=np.append(allcubes,shootcubes)
        activecubes=[]

        for c in allcubes:
            dist=np.linalg.norm(c.center-cam.camerapos)
            dotrc = np.dot(c.center-cam.camerapos,cam.direction[0])/dist
            if dotrc>COSVIEWANGLE:
                activecubes.append(c)

        cubeorder=cubedist(activecubes,cam.camerapos)
        disptime0=time.time()
        for i in cubeorder:
            display(disp,activecubes[i],cam)

        
            
        #disptime0=time.time()
        ##print("display time, sec:")
        ##print(time.time()-disptime0)
        if len(rbx.cubes)>0:
            if not rbx.rotateface:
                rbx.rotateface='u'
                rbx.rotspeed=-.05+.1*random.randint(0,1)

            rotrbx(rbx)

        now=time.time()       
        if now-begintime>.5:
            fps=framenum/(now-begintime)
            framenum=0
            begintime=now

        disp2(disp,fps,len(activecubes))
        pygame.display.update()
        
        clock.tick(20)




if __name__ == "__main__":
    main()