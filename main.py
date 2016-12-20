"""
main


"""
from chip8 import Chip8
import pygame
from sys import argv, exit
from os.path import isfile

def updateScreen():
    pass

def main():
    # get rom path
    rom = argv[1]
    print rom
    if not isfile(rom):
        exit()

    # initialize graphics
    # see https://github.com/metulburr/pong/blob/master/data/control.py
    # graphics = 64x32
    pygame.init()
    pygame.display.set_caption('chippy')
    clock = pygame.time.Clock()
    chip8 = Chip8(pygame.display.set_mode((512, 256)), rom)

    # main loop
    while True:
        # if we're updating the screen, make sure the screen only updates at 60FPS max
        if chip8.getDrawFlag():
            clock.tick(60)
            pygame.display.update()
            # check if the player has tried to close the window
            event = pygame.event.poll()
            if event.type == pygame.QUIT:
                exit()
            pygame.event.clear() # we don't use pygame events
            chip8.setDrawFlag(False)
            chip8.emulateCycle()
        else:
            # still run other opcodes, even if we aren't drawing anything
            chip8.emulateCycle()

main()
