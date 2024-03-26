import pyMeow as pm
import math


proc = pm.open_process("WolfSP.exe")

class Modules:
    base = pm.get_module(proc,"WolfSP.exe")["base"]
    qagamex86 = pm.get_module(proc,"qagamex86.dll")["base"]

class Addresses:
    entity_list = Modules.qagamex86+0x53EB80
    camera_direction = Modules.base+0x5D16F4

class Offsets:
    ent_size = 0x588
    health_offset = 0x3D8
    pos = 0x18
    is_valid = 0x9E0

class Entity:
    def __init__(self,base):
        self.base = base
        self.h = base+Offsets.health_offset
        self.pos = base+Offsets.pos
        self.xbase = hex(base)
    def health(self):
        return pm.r_int(proc,self.h)
    def position(self):
        return pm.r_floats(proc,self.pos,3)
    def teleport(self,pos):
        pm.w_floats(proc,self.pos,pos)
    
def direction():
    return pm.r_floats(proc,Addresses.camera_direction,3)

def  entities():
    ply = Entity(Addresses.entity_list)
    return ply

def norm(vec):
    m = math.sqrt(sum([vec[i]**2 for i in range(3)]))
    return [i/m for i in vec]

def wts(ply,worldpos):
    width,height = pm.get_screen_width(),pm.get_screen_height()
    x_fov = math.radians(90) 
    y_fov = x_fov/width * height
    cam_pos = ply.position()
    cam_look = direction()
    camToObj = [worldpos[i]-cam_pos[i] for i in range(3)]
    distToObj = math.sqrt(sum([camToObj[i]**2 for i in range(3)]))
    camToObj = [i/distToObj for i in camToObj]
    camYaw = math.atan2(cam_look[1],cam_look[0])
    objYaw = math.atan2(camToObj[1],camToObj[0])
    relYaw = camYaw-objYaw
    if (relYaw > math.pi):
        relYaw -= 2*math.pi
    if (relYaw<-math.pi):
        relYaw += 2*math.pi
    objPitch = math.asin(camToObj[2])
    camPitch = math.asin(cam_look[2])
    relPitch = camPitch-objPitch
    x = relYaw/(0.5*x_fov)
    y = relPitch/(0.5*y_fov)
    x = (x+1)/2
    y = (y+1)/2
    return x*width,y*height,distToObj

ents = [Entity(Addresses.entity_list+Offsets.ent_size*i) for i in range(1,1000) if pm.r_int(proc,Addresses.entity_list+Offsets.ent_size*i+Offsets.is_valid)!=0]
ply = Entity(Addresses.entity_list)

class Colors:
    cyan = pm.get_color("cyan")
    red = pm.get_color("red")



pm.overlay_init(target="Wolfenstein", fps=144, trackTarget=True)
while pm.overlay_loop():
    alive_enemies = [i for i in ents if i.health()>0]       
    pm.begin_drawing()
    for i in alive_enemies:
        pos = i.position()
        x,y,dist = wts(ply,pos)
        width = 15000/dist
        height = 35000/dist
        x-=width/2
        
        pm.draw_text("health: "+str(i.health()),x,y,20/dist,Colors.cyan)
        pm.draw_line(x,y,x+width,y,Colors.red)
        pm.draw_line(x,y,x,y+height,Colors.red)
        pm.draw_line(x+width,y,x+width,y+height,Colors.red)
        pm.draw_line(x,y+height,x+width,y+height,Colors.red)

    pm.end_drawing()