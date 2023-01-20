import random
from pprint import pprint
import pygame
import numpy as np
import math
import time
import sys
import twophase.solver as sv


#from RT_lib import *


CAMERAPOS0=[0,-5000,3000]
CAMERADIR02=np.array([0,0.66,-.30],float)
RBXROTSPD=.8
SCREENDIST=700
DISPWIDTH=1200
DISPHIGHT=850
COSVIEWANGLE=SCREENDIST/math.sqrt((DISPWIDTH/2)**2+(DISPHIGHT/2)**2+SCREENDIST**2)

ROTATEVEL=.00005
CUBEROTMAX=.5
CAMVEL=300
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

face=np.array([[0,3,4,7],
        [0,1,6,7],
        [0,1,2,3],
        [4,5,6,7],
        [2,3,4,5],
        [1,2,5,6]],int)

    

def colored(s:str,color):
    return(f"\033[48;5;{color}m{s.ljust(2,' ')}\033[0;0;0m")

    
class Brain:
    
    def __init__(self) -> None:
        if False:
            #                 0   1   2
            #                 3   U   5 -white
            #                 6   7   8
            #                           /-- orange
            # 9   10  11      18  19  20      27  28  29      36  37  38
            # 12  L   14      21  F   23      30  R   32      39  B   41
            # 15  16  17      24  25  26      33  34  35      42  43  44

            #                 45  46  47
            #                 48  D   50 -yellow
            #                 51  52  53

            pass
            

        self.u=np.arange(0,9,1,int).reshape((3,3))
        self.u=np.array([[0,1,2],\
                        [3,4,5],\
                        [6,7,8]],int)
        self.l=np.arange(9,18,1,int).reshape((3,3))
        self.f=np.arange(18,27,1,int).reshape((3,3))
        self.r=np.arange(27,36,1,int).reshape((3,3))
        self.b=np.arange(36,45,1,int).reshape((3,3))
        self.d=np.arange(45,54,1,int).reshape((3,3))
        keys="u l f r b d".split()
        
        self.cubelist=[self.u,self.l,self.f,self.r,self.b,self.d]
        """[self.u, self.l, self.f, self.r, self.b, self.d]"""
        self.cube=dict(zip(keys,self.cubelist))

    def rotarry(self,face,cw=1):
        new=self.cube[face]
        face=np.copy(new)
        a=[2,2,2,1,0,0,0,1]
        b=[0,1,2,2,2,1,0,0]
        c=[0,0,0,1,2,2,2,1]
        for n in range(8):
            i=a[n]
            j=a[n-2]
            k=a[n-4]
            
            if cw:new[j,k]=face[i,j]
            else:new[j,i]=face[k,j]

    def bturn(self,cw):
        temp=np.copy(np.flip(self.u[0]))
        self.u[0]=self.r[:,2]
        self.r[:,2]=np.flip(self.d[2])
        self.d[2]=self.l[:,0]
        self.l[:,0]=temp
    def uturn(self,cw):
        if cw:
            temp=np.copy(self.l[0])
            self.l[0]=self.f[0]
            self.f[0]=self.r[0]
            self.r[0]=self.b[0]
            self.b[0]=temp
        else:
            pass            
    def rturn(self,cw):
        if cw:
            temp=np.copy(self.u[:,2])
            self.u[:,2]=self.f[:,2]
            self.f[:,2]=self.d[:,2]
            self.d[:,2]=np.copy(np.flip(self.b[:,0]))
            self.b[:,0]=np.copy(np.flip(temp))
    def fturn(self,cw):
        if cw:
            temp=np.copy(self.u[2])
            self.u[2]=np.flip(self.l[:,2])
            self.l[:,2]=self.d[0]
            self.d[0]=np.flip(self.r[:,0])
            self.r[:,0]=temp
    def dturn(self,cw):
        temp=np.copy(self.l[2])
        self.l[2]=self.b[2]
        self.b[2]=self.r[2]
        self.r[2]=self.f[2]
        self.f[2]=temp
    def lturn(self,cw):
        temp=np.copy(self.d[:,0])
        self.d[:,0]=self.f[:,0]
        self.f[:,0]=self.u[:,0]
        self.u[:,0]=np.copy(np.flip(self.b[:,2]))
        self.b[:,2]=np.copy(np.flip(temp))

    def rotface(self,face, cw=1):
        copy=np.copy(np.rot90(self.cube[face],1+2*(cw)))
        for i in range(3):
                self.cube[face][i]=np.copy(copy[i])
        
        if face=="u": self.uturn(cw)
        if face=="r": self.rturn(cw)
        if face=="f": self.fturn(cw)
        if face=="d": self.dturn(cw)
        if face=="l": self.lturn(cw)
        if face=="b": self.bturn(cw)

        self.show()
    def show(self):
        colors=[231,27,214,70,9,227]
        text=[]
        for face in self.cubelist:
            for row in face:
                for t in row:
                    text.append(colored(str(t),colors[t//9]))
        order=list(range(9))
        for j in range(3): order+=[9+i//3*9+i%3+3*j for i in range(12)]
        order+=list(range(45,54))
        for i in range(54):
            if not i%3 and (i<9 or i>44): sys.stdout.write('\n         ')
            sys.stdout.write(f' {text[order[i]]}')
            if i in [8,20,32,53]: sys.stdout.write('\n')
        
        return

class Camera:
    def __init__(self,pos=CAMERAPOS0, direction=np.array([[1,0,0],[0,1,0],[0,0,1]],float)):
        self.camerapos=np.array(pos,float)
        self.direction=direction
        self.setdirection()
        self.screencenter=np.array(self.camerapos-SCREENDIST*self.direction[0])
        self.senszz,self.sensyy=SENSZ,SENSY
        self.rotsens,self.zzyyacc=.2,.05
        self.rightc=self.upc=self.forc=self.leftrc=self.downrc=0

    def setdirection(self):
        self.direction[0]=CAMERADIR02/np.linalg.norm(CAMERADIR02)
        self.direction[1]=np.cross(np.array([0,0,1],float),self.direction[0])
        self.direction[1]/=np.linalg.norm(self.direction[1])
        self.direction[2]=np.cross(self.direction[0],self.direction[1]) 

    def events(self,event):
        if event.type==pygame.KEYDOWN:
            #print(event)
            lastkey=event.unicode
            if event.scancode==80:self.rightc=1##left
            elif event.scancode==79:self.rightc=-1##right
            if event.scancode==82:self.upc=-1##up
            elif event.scancode==81:self.upc=1##down
            if event.scancode==54:self.forc=-1##back <
            elif event.scancode==55:self.forc=1##forward >
                
        if event.type==pygame.KEYUP:
            #print(event)
            if event.scancode==80:self.rightc=0##left
            elif event.scancode==79:self.rightc=0
            if event.scancode==82 or event.scancode==81:##up
                self.upc=0
            if event.scancode==54 or event.scancode==55:
                self.forc=0
            if event.scancode==26 or event.scancode==22:
                self.downrc=0 
                self.sensyy=SENSY
            if event.scancode==4 or event.scancode==7:
                self.leftrc=0
                self.senszz=SENSZ

    def execute(self):
        distance=np.linalg.norm(self.camerapos)
        camvel=CAMVEL*distance/3000
        if self.leftrc: self.rotatez()
        if self.downrc: self.rotatey()
        if self.forc:
            self.camerapos+=self.forc*self.direction[0]*camvel
            distance=np.linalg.norm(self.camerapos)
        if self.rightc or self.upc:
            if self.rightc:
                self.camerapos-=self.rightc*camvel*self.direction[1]
                #self.direction=np.dot(self.direction,zrot(-self.rightc*math.atan(CAMVEL/distance)))
            if self.upc:
                self.camerapos+=self.upc*camvel *self.direction[2]
                #self.direction=np.dot(self.direction,yrot(-self.upc*math.atan(CAMVEL/distance)))
            self.camerapos*=distance/np.linalg.norm(self.camerapos)
            self.direction[0]=-self.camerapos/distance
            self.direction[2]=np.cross(self.direction[0],self.direction[1])
            self.direction[2]/=np.linalg.norm(self.direction[2])
            self.direction[1]=np.cross(self.direction[2],self.direction[0])
        self.screencenter=np.array(self.camerapos-SCREENDIST*self.direction[0])
                        
    def rotatey(self): 
        self.sensyy+=self.zzyyacc
        if self.sensyy>SENSMAX:
            self.sensyy=SENSMAX
        self.direction=np.dot(yrot(-self.sensyy*self.downrc*self.rotsens),self.direction)
    def rotatez(self): 
        self.senszz+=self.zzyyacc
        if self.senszz>SENSMAX:
            self.senszz=SENSMAX
        self.direction=np.dot(zrot(-self.senszz*self.leftrc*self.rotsens),self.direction)

    
    def faceinfo(self,cubes:'list[Cube]',mousepos):
        infolist=[]
        for cube in cubes:
            polygoncount=0
            disptime0=time.time()
            verts=np.zeros((8,3),float)
            for i in range(8):
                verts[i]=np.array(cube.center) + np.dot(cube.coords,Cube.vcsigns[i]*cube.slen/2)
            order=facedist(verts,self.camerapos)
            dotrc=res=d=0.0
            x=y=0
            toobig=0
            for i in range(3):
                v=np.zeros((4,2))
                if not any(cube.color[order[i+3]]):## 
                    continue
                for j in range(4):
                    rayd=verts[face[order[3+i],j]]-self.camerapos
                    dotrc=np.dot(rayd,self.direction[0])
                    if dotrc<0.1: #toobig
                        toobig=1
                        #print("dotrc!!!!!!!!!")
                        #print(i,j)
                        break

                    d=np.dot((self.screencenter-self.camerapos),self.direction[0])/dotrc
                    point=self.camerapos+d*rayd
                    v1=point-self.screencenter
                    
                    v1m=np.linalg.norm(v1)
                    if v1m>5000:
                        toobig=1
                        #print("TOOBIG")
                        break
                    v1/=v1m
                    res=np.dot(self.direction[2],v1)
                    y=round(res*v1m)
                    
                    x=round(v1m*math.sin(math.acos(res)))
                    if (np.dot(v1,self.direction[1])<0):
                        x=-x
                    x+=DISPWIDTH//2
                    y+=DISPHIGHT//2
                    v[j]=[x,y]  
                
                if not toobig:
                    polygon_middle=np.array([0,0],int)
                    for xy in v:
                        polygon_middle+=np.array(xy,int)
                    polygon_middle//=4
                    infolist.append(FaceInfo(cube,order[i+3],distance2d(polygon_middle,mousepos)))
                    #pygame.draw.polygon(disp,cube.color[order[i+3]], v )
                    polygoncount+=1
        infolist.sort()
        infolist[0].show()


class Cube:
    vcsigns=np.array([[1,1,1],
                [-1,1,1],
                [-1,-1,1],
                [1,-1,1],
                [1,-1,-1],
                [-1,-1,-1],
                [-1,1,-1],
                [1,1,-1]])
    def __init__(self,center,slen,color_std_rand,id=0):
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
        self.id=id
        self.radius=np.linalg.norm(self.slen)/2
        self.coords=np.array([[1,0,0],[0,1,0],[0,0,1]],float)
        self.vert=self.vertcalc()
        
        if color_std_rand=='std':
            self.color=np.copy(fcolor)
        
        else:
            self.color=[]
            for i in range(6):
                self.color.append(tuple(np.random.randint(0,255,3)))

        #self.body=g.Body(0,self.center,np.average(slen),[0,0,1],[0,0,1],abs(self.slen[0]*self.slen[1]*self.slen[2])/10**7)
            
    def colorme(self,c):
        for i in range(6):
            self.color[i]=tuple(c)
        #print('coloured')
   

    def vertcalc(self):
        v=np.zeros((8,3),float)
        for i in range(8):
            v[i]=np.array(self.center) + np.dot(self.coords,Cube.vcsigns[i]*self.slen/2)
        return v

class MoveParams:
    def __init__(self,letter) -> None:
        if   letter =='r':self.innit(0,1)
        elif letter =='l':self.innit(0,-1,1)
        elif letter =='u':self.innit(2,1)
        elif letter =='d':self.innit(2,-1,1)
        elif letter =='f':self.innit(1,-1,1)
        elif letter =='b':self.innit(1,1)
        else: print("bad init of move params")
    def innit(self,axis,oppface,direction=-1) -> None:
        self.axis=axis
        self.oppface=oppface
        self.direction=direction

class Rbx:
    def __init__(self) -> None:
        
        self.cubetiles=Brain()
        self.cubes:'list[Cube]'=[]
        self.center=np.array([0,0,0],float)
        self.coords=np.array([[1,0,0],[0,1,0],[0,0,1]],float)


        # self.rotateface='u'
        self.lastmove='u'
        self.queue=''
        self.shuffling=False
        self.midrotation=False



        self.rotspeed=RBXROTSPD
        self.colors=[white,blue,orange,green,red,yellow]
        self.currentoffset=0.0
        self.raxis=0
        self.oppface=1 ##1,-1
        self.stopping=False
        self.rotatebool=0
        self.moves={'r':MoveParams('r'),
                    'l':MoveParams('l'),
                    'u':MoveParams('u'),
                    'd':MoveParams('d'),
                    'f':MoveParams('f'),
                    'b':MoveParams('b')
                        }

    def colorme(self):
        for cube in self.cubes: cube.colorme((0,0,0))
        for i in range(9): self.cubes[i].color[2]=self.colors[self.cubetiles.u[i//3,i%3]//9]
        for j in range(3):
            for i in range(3):
                self.cubes[  i*3 +9*j].color[5]=tuple(self.colors[self.cubetiles.l[j,i%3]//9])
                self.cubes[6+i   +9*j].color[4]=tuple(self.colors[self.cubetiles.f[j,i%3]//9])
                self.cubes[8-i*3 +9*j].color[0]=tuple(self.colors[self.cubetiles.r[j,i%3]//9])
                self.cubes[2-i   +9*j].color[1]=tuple(self.colors[self.cubetiles.b[j,i%3]//9])
        for i in range(9): self.cubes[18+i].color[3]=self.colors[self.cubetiles.d[2-i//3,i%3]//9]

    def arrangecubes(self):
            self.center=0
            self.cubes=arrangeRubix(self.center)
            self.currentoffset=0
    def rotrbx(self,u='u'):
        self.midrotation=True
        u=self.queue[0]

        axis,oppface=(self.moves[u].axis,self.moves[u].oppface)
        ang=RBXROTSPD*self.moves[u].direction
        for i in self.cubes:
            if oppface*np.dot(i.center-self.center,self.coords[axis])>self.cubes[0].slen[0]/2:
                i.center=self.center+np.dot(rotatebyaxis(self.coords[axis],ang),i.center-self.center)
                i.coords=np.dot(rotatebyaxis(self.coords[axis],ang),i.coords)
                
        self.currentoffset+=abs(ang)
        if self.currentoffset>math.pi/2:
            self.midrotation=False
            self.queue=self.queue[1:]
            self.currentoffset=0
            self.arrangecubes()
            self.colorme()



    def randomrotate(self):
        choices="rufldb"
        newface=random.choice(choices)
        self.queue=newface
        if self.stopping:
            self.rotatebool=0
            return False
        
          
        return True
    
    
    def events(self,key):
        if key=='0':
            self.arrangecubes()
            self.cubetiles.__init__()
        if key=='h':
                self.shuffling= not self.shuffling
                self.stopping=not self.stopping
        if key in "rufldb": self.queue+=key   
        if key=='s':
            self.initsolve()
    def initsolve(self):
        faceletter="ULFRBD"
        currentstate=""
        for face in [  self.cubetiles.u,
                    self.cubetiles.r,
                    self.cubetiles.f,
                    self.cubetiles.d,
                    self.cubetiles.l,
                    self.cubetiles.b,]:
            for row in face:
                currentstate+=''.join([faceletter[s//9] for s in row])
        #print(currentstate)
        solvequeue=sv.solve(currentstate)
        #print("solvequeue",solvequeue)
        queue=""
        for i in solvequeue.split():
            if len(i)==2:
                queue+=i[0]*int(i[1])
        self.queue=queue.lower()
        
        print("self.queue",self.queue)
    def managerotation(self):
        if self.midrotation:
            self.rotrbx()
            #print("midrotation")
        else: 
            self.colorme()
            if len(self.queue)>0:
                self.rotrbx()
                self.cubetiles.rotface(self.queue[0])
                #print("uhh here")
            elif self.shuffling:
                self.randomrotate()
                self.rotrbx()
                self.cubetiles.rotface(self.queue[0])
                print("shuffling")


def display(disp,cube:Cube ,cam:Camera):
    polygoncount=0
    ##verts=cube.vertcalc()
    disptime0=time.time()
    
    #locate the coords of the vertecies of each side of the cube
    verts=np.zeros((8,3),float)
    for i in range(8):
        verts[i]=np.array(cube.center) + np.dot(cube.coords,Cube.vcsigns[i]*cube.slen/2)
    
    #make the closet side get drawn last
    order=facedist(verts,cam.camerapos)

    toobig=0

    dotrc=res=d=0.0
    x=y=0

    #draw the closest 3 faces
    for i in range(3):
        
        if not any(cube.color[order[i+3]]):## 
            continue
        v=np.zeros((4,2))

        # translate 3D vertex coords into 2D display coords
        for j in range(4):

            # vector from cam to vertex
            rayd=verts[face[order[3+i],j]]-cam.camerapos

            dotrc=np.dot(rayd,cam.direction[0])
            # =|rayd|cos(@)

            if dotrc<0.1: #toobig    
                toobig=1
                print(f"dotrc!!!!!!!!!\ni,j= {i},{j}")
                break

            
            d=np.dot((cam.screencenter-cam.camerapos),cam.direction[0])/dotrc
            point=cam.camerapos+d*rayd
            v1=point-cam.screencenter
            v1m=np.linalg.norm(v1)

            if v1m>5000:
                toobig=1
                print("TOOBIG")
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
            polygoncount+=1
    return polygoncount
def disp2(disp,fps,inframe,polygons):
    pygame.draw.circle(disp, (150,150,255), MCP, MCPR, width=0)
    pygame.draw.circle(disp, (0,0,0), (DISPWIDTH/2,DISPHIGHT/2), 2, width=0)
    ab1=f"FPS: {round(fps,3)}"
    ab2=f"In Frame: {inframe}"
    ab3=f"Polygon count: {polygons}"
    tilefont = pygame.font.Font('freesansbold.ttf', 30)
    text = tilefont.render(ab1, True, grey)
    text2 = tilefont.render(ab2, True, grey)
    text3 = tilefont.render(ab3, True, grey)
    textRect = text.get_rect()
    textRect.center = (150,40)
    disp.blit(text, textRect)
    textRect = text2.get_rect()
    textRect.center = (160,80)
    disp.blit(text2, textRect)
    textRect = text3.get_rect()
    textRect.center = (160,120)
    disp.blit(text3, textRect)

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
def cubedist(cubes:'list[Cube]',campos):
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
    if d==0:
        ##print(f'axis: {axis}')# a,b,c = 1,0,0
        rx=np.array([[1,0,0],
                    [0,1,0],
                    [0,0,1]],float)
    else:
        rx=np.array([[1,0,0],
                    [0,c/d,-b/d],
                    [0,b/d,c/d]],float)
    ry=np.array([[d,0,-a],
                [0,1,0],
                [a,0,d]],float)
        
    T=np.dot(np.dot(np.linalg.inv(rx),np.linalg.inv(ry)),zrot(t))
    ret= np.dot(T,np.dot(ry,rx))
    return ret

def distance2d(a,b):
    delx=b[0]-a[0]
    dely=b[1]-a[1]
    d=math.sqrt(delx**2+dely**2)
    return d
        
def distpoint2line(a,b,dir):
    # point:A line: B + dir    
    return np.linalg.norm(np.cross(dir,b-a))
def resetstd(slen,num)->'list[Cube]':
    prb=num/slen**3
    cubes=[]
    for i in range(slen) :
        for j in range(slen):
            for k in range(slen):
                if random.random()<prb:
                    cubes.append(Cube(3000*np.array([i-slen/2,j-slen/2,k-slen/2]),np.random.randint(500,1000,3),0))
    return cubes

def arrangeRubix(center):
    cubes=[]
    slen=200
    center=np.array(center)
    id=-1
    for k in range(2,-1,-1):
        for j in range(2,-1,-1):
            for i in range(3):
                id+=1
                if 1 or not (1==i==j==k):
                    newcube=Cube(1.1*slen*np.array([i-1,j-1,k-1])+center,slen,'std',id)
                    
                    if i<2:
                        newcube.color[0]=black
                    if i>0:
                        newcube.color[5]=black
                    if j<2:
                        newcube.color[1]=black
                    if j>0:
                        newcube.color[4]=black
                    if k<2:
                        newcube.color[2]=black
                    if k>0:
                        newcube.color[3]=black


                    cubes.append(newcube)
                

    return cubes

def multrbx(slen)->'list[Rbx]':
    rbxs:'list[Rbx]'=[]
    for i in range(slen) :
        for j in range(slen):
                k=0
                newrbx=Rbx()
                newrbx.center=2000*np.array([i-(slen-1)/2,j-(slen-1)/2,k-(slen-1)/2])
                newrbx.cubes=arrangeRubix(newrbx.center)
                newrbx.rotspeed+=RBXROTSPD/2*(random.random()-.5)
                rbxs.append(newrbx)
    return rbxs
                
def getcolorname(rgb):
    if list(rgb)==list(white):return "white"
    if list(rgb)==list(green):return "green"
    if list(rgb)==list(red):return "red"
    if list(rgb)==list(blue):return "blue"
    if list(rgb)==list(yellow):return "yellow"
    if list(rgb)==list(orange):return "orange"
    return rgb
class FaceInfo:
    def __init__(self,cube,face, distance) -> None:
        self.distance=distance
        self.cube:Cube=cube
        self.face=face

    def __eq__(self, __o: object) -> bool:
        return self.distance==__o.distance
    def __lt__(self, __o: object) -> bool:
        return self.distance<__o.distance
    def show(self):
        print("\n---------------")
        print(f"   -Cube id:  {self.cube.id}    location: {self.cube.center}")

        print(f"   -Face num: {self.face}")
        color=getcolorname(self.cube.color[self.face])
        print(f"   -color:    {color}")

       
def main():
    pygame.init()
    disp=pygame.display.set_mode((DISPWIDTH,DISPHIGHT))
    pygame.display.set_caption('RBX CUBES!!!')
    #pygame.mouse.set_visible(False)
    clock= pygame.time.Clock()
    cam=Camera(CAMERAPOS0)
    cam.camerapos=np.array([  658.76455063, -1449.24573266,   670.57717643])
    cam.direction=np.array([[-3.81358905e-01,  8.38968588e-01, -3.88197236e-01],\
                            [-9.10362575e-01, -4.13811529e-01,  2.77555756e-17],\
                            [-1.60640492e-01,  3.53400235e-01,  9.21576316e-01]])
    # pmp=mousepos=(0,0)
    mousebutton=0

    begintime=time.time()
    framenum=0
    fps=1

    dist=dotrc=0
    rbx=Rbx()
    menu=0

    rbx=multrbx(1)[0]
    rbx.colorme()
    while True:
        framenum+=1
        
        # if mousebutton:
        #     pmp=np.array(mousepos)


        # Manage user keyboard/mouse inputs
        for event in pygame.event.get():
            if event.type==pygame.QUIT or (event.type==pygame.KEYDOWN and event.scancode==41):
                pygame.quit()
                quit()
            if event.type==pygame.MOUSEMOTION: 
                mousepos=event.pos
                continue
            cam.events(event)
            
            if event.type==pygame.KEYDOWN:
                rbx.events(event.unicode)
                if event.unicode=='m':
                    menu= not menu
                if event.unicode=='f':
                    cam.faceinfo(rbx.cubes, mousepos)
                    
                if event.unicode=='c':
                    print(cam.camerapos)
                    pprint(cam.direction)
                
                if event.scancode==44:##space
                    mousebutton = not mousebutton

        
        cam.execute()

        # cube rotation
        rbx.managerotation()
                
        # cube display
        allcubes=np.copy(rbx.cubes)
        activecubes=[]

        # create list of cubes to render
        for c in allcubes:
            dist=np.linalg.norm(c.center-cam.camerapos)
            dotrc = np.dot(c.center-cam.camerapos,cam.direction[0])/dist
            if dotrc>COSVIEWANGLE:
                activecubes.append(c)
        cubeorder=cubedist(activecubes,cam.camerapos)
    
        polygoncount=0

        # display cubes
        disp.fill((220,220,190))
        for i in cubeorder:
            polygoncount+=display(disp,activecubes[i],cam)
        now=time.time()       
        if now-begintime>.5:
            fps=framenum/(now-begintime)
            framenum=0
            begintime=now

        # display menu
        if menu:
            disp2(disp,fps,len(activecubes),polygoncount)
        pygame.display.update()
        
        clock.tick(20)

if __name__ == "__main__":
    main()

