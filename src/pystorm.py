# -*- coding: utf-8 -*-

import usb
from time import sleep

try:
    # Python2
    import Tkinter as tk
    print "Imported TKinter (Python2)"
except ImportError:
    # Python3
    import tkinter as tk

def find_device():
    busses = usb.busses()
    for bus in busses:
        for dev in bus.devices:
            if dev.idVendor == 0x2123 and dev.idProduct == 0x1010:
                return dev

class ControlMode:
    BASIC = 1
    MULTICOMMAND = 2
    
class Commands:
    DOWN    = 0x01
    UP      = 0x02
    LEFT    = 0x04
    RIGHT   = 0x08
    SHOOT   = 0x10
    STOP    = 0x20

class Missile(object):
    CONTROL_UPDATE_DELAY = 20; #milliseconds
    
    _dev = None
    handle = None
    controlMode = ControlMode.MULTICOMMAND
    moving = False
    controlCode = 0x0

    def __init__(self):
        self._dev = find_device()
        self.handle = self.init_usb_connection()

    def init_usb_connection(self):
        handle = self._dev.open()
        #try:
        #    handle.detachKernelDriver(0) # Should this be iface.interfaceNumber?
        #except usb.USBError:
        #    print "Already detached"
        return handle
    
    #Main control update loop
    def update(self):
        #print("UPDATE!")
        
        if self.controlCode != 0:
            if ~self.moving:
                self.moving = True
            self.send_message(self.controlCode)
        else:
            if self.moving:
                self.stop()
                self.moving = False
        
        root.after(Missile.CONTROL_UPDATE_DELAY, self.update) #prep to update self again in a bit
    
    def send_message(self, message):
        msg_buffer = [0x02] + [message] + [0] * 6
        print msg_buffer
        print self.handle.controlMsg(usb.TYPE_CLASS | usb.RECIP_INTERFACE | usb.ENDPOINT_OUT, usb.REQ_SET_CONFIGURATION, msg_buffer, usb.DT_CONFIG, 0)

    def stop(self):
        self.send_message(Commands.STOP)

    def move(self, direction, s = 0):
        self.send_message(direction)
        s = max(s, 0.01) # minimum pause to see some movement
        sleep(s)
        self.stop()

    def up(self, s = 0):
        # experience shows that full up<->down is around 0.76s
        self.move(Commands.UP, s)

    def down(self, s = 0):
        # experience shows that full up<->down is around 0.76s
        self.move(Commands.DOWN, s)

    def left(self, s = 0):
        # experience shows that full left<->right is around 5s
        # experience shows something like 90° ~ 1.7s
        self.move(Commands.LEFT, s)

    def right(self, s = 0):
        # experience shows that full left<->right is around 5s
        # experience shows something like 90° ~ 1.7s
        self.move(Commands.RIGHT, s)

    def shoot(self):
        self.send_message(Commands.SHOOT)

missile = Missile()

#Handles keyboard key-down events
def onKeyDown(event):
    """shows key or tk code for the key"""
    if event.keysym == 'Escape':
        root.destroy()

    #Missile controls (single-command version)
    if missile.controlMode == ControlMode.BASIC:
        if event.keysym == 'Up':
            missile.up()
        if event.keysym == 'Down':
            missile.down()
        if event.keysym == 'Left':
            missile.left()
        if event.keysym == 'Right':
            missile.right()
        if event.keysym == 'space':
            missile.shoot()
        
    #Missile controls (multiple simultaneous commands version)
    if missile.controlMode == ControlMode.MULTICOMMAND:
        dirMsg = 0x0
        if event.keysym == 'Up':
            dirMsg += Commands.UP
        if event.keysym == 'Down':
            dirMsg += Commands.DOWN
        if event.keysym == 'Left':
            dirMsg += Commands.LEFT
        if event.keysym == 'Right':
            dirMsg += Commands.RIGHT
        if event.keysym == 'space':
            missile.shoot()
            
        if dirMsg != 0:
            missile.controlCode = missile.controlCode | dirMsg
            #missile.move(missile.controlCode)

#Handles keyboard key-up events
def onKeyUp(event):
        
    #Missile controls (multiple simultaneous commands version)
    if missile.controlMode == ControlMode.MULTICOMMAND:
        dirMsg = 0x0
        if event.keysym == 'Up':
            dirMsg += Commands.UP
        if event.keysym == 'Down':
            dirMsg += Commands.DOWN
        if event.keysym == 'Left':
            dirMsg += Commands.LEFT
        if event.keysym == 'Right':
            dirMsg += Commands.RIGHT
        if event.keysym == 'space':
            missile.shoot()
            
        #Remove active movement command for each released key
        if dirMsg != 0:
            missile.controlCode = missile.controlCode ^ dirMsg

  
root = tk.Tk()
print( "Press a key (Escape key to exit):" )
root.bind_all('<Key>', onKeyDown)
root.bind_all('<KeyRelease>', onKeyUp)
# don't show the tk window
#root.withdraw()
missile.root = root
root.after(Missile.CONTROL_UPDATE_DELAY, missile.update)
root.mainloop()
print "Goodbye!"
