
from Syncer import *

#===============================================================================
#= INITIALIZATION
#=

# First we ask if the current execution role. Server or client?
SERVER_ROLE = int(input("Run as server? (0=no, 1=yes): "))

# Servers must be initialized with a port number.
if SERVER_ROLE:
    syncer = Syncer(port=27445)

# Clients doesn't need to be initialized with a port number as it may be
# selected at runtime.
else:
    syncer = Syncer()
    # and then we connect to the server right on.
    server_addr = ("127.0.0.1", 27445)
    syncer.connect("hello-im-connecting", server_addr)

#===============================================================================
#= DEFINING OBJECT-OVER-NETWORK CLASSES
#=

import struct

@UID_register_class
class Circle(object):

    # Let's define a Circle class. Circles are simple objects with only three
    # fields: position (x, y), speed (x, y) and color (from 0 to 255).
    
    def __init__(self, **kargs):
        self.pos = kargs.get("pos", [0.0,0.0])
        self.spd = kargs.get("spd", [0.0,0.0])
        self.color = kargs.get("color", 0)

        
    # get_data() method returns a string representing the local state of the
    # object.

    def get_data(self):
        return struct.pack("!4fi", self.pos[0], self.pos[1], self.spd[0], self.spd[1], self.color)

    
    # set_data(data, offset, conn) method updates the local state of the object
    # with a substring contained in the given string. The parameters also
    # specifies where the substring starts and references the sender's
    # connection. The method must know by itself how interpret the substring and
    # how long it is, returning where it ends.
    
    def set_data(self, data, offset, conn):
        self.pos[0], self.pos[1], self.spd[0], self.spd[1], self.color = struct.unpack_from("!4fi", data, offset)
        return offset + struct.calcsize("!4fi")

    
    # is_feed_to(conn) method returns if this object should send updates to the
    # given connection. In the example only the server sends feed.
    
    def is_feed_to(self, conn):
        return 1 if SERVER_ROLE else 0
    
    # is_feed_accepted(conn) method returns if this object should receive a
    # update from the given connection. In the example only the client receives
    # feed, and it must come from the server.
    
    @staticmethod
    def is_feed_accepted(self, conn):
        if SERVER_ROLE: return 0
        return conn["addr"] == server_addr
    
    # Nothing is ever erased in this example
    
    def is_remove_to(self, conn):
        return 0
        
    def is_remove_accepted(self, conn):
        return 0
    


import pygame

import random
import sys
import time

screen = pygame.display.set_mode((640, 480))


while 1:
 
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
 
    screen.fill((0, 0, 0))
 
    if SERVER_ROLE:

        if pygame.mouse.get_pressed()[0]:
            instance = Circle(
                pos=list(pygame.mouse.get_pos()),
                spd=list((random.random()*2, random.random()*2)),
                color=255,
            )
            UID_register(instance)

        for circle in Circle.INSTANCES.itervalues():
            if circle.color == 255:
                circle.color = 0
                syncer.feed(circle)

    else:
        
        if not len(syncer.connections): exit()
 
    for circle in Circle.INSTANCES.itervalues():
        circle.color += 1
        circle.color = min(255, circle.color)
        circle.pos[0] += circle.spd[0]
        circle.pos[1] += circle.spd[1]
        if circle.pos[0] < 0:   circle.spd[0] =  abs(circle.spd[0])
        if circle.pos[1] < 0:   circle.spd[1] =  abs(circle.spd[1])
        if circle.pos[0] > 640: circle.spd[0] = -abs(circle.spd[0])
        if circle.pos[1] > 480: circle.spd[1] = -abs(circle.spd[1])
        pygame.draw.circle(screen, (255 - circle.color, 0, circle.color), (int(circle.pos[0]), int(circle.pos[1])), 20)
        
    syncer.process()
 
    time.sleep(0.02)
    pygame.display.flip()
    
    
    
    
    
    
