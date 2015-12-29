"""
main


"""
from chip8 import Chip8

def updateScreen():
    pass

def main():
    #initialize graphics, audio
    #see https://github.com/metulburr/pong/blob/master/data/control.py
    #graphics = 64x32

    chip8 = Chip8('/home/ianl/chip8/roms/PONG')

    while True:
        chip8.emulateCycle()
        if chip8.getDrawFlag:
            updateScreen()
        #set key press flags...

main()