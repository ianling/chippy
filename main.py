"""
main


"""
from chip8 import Chip8
import pygame

def updateScreen():
    pass

def main():
    #initialize graphics, audio
    #see https://github.com/metulburr/pong/blob/master/data/control.py
    #graphics = 64x32
    pygame.init()
#    display = pygame.display.set_mode((512, 256))
    pygame.display.set_caption('chippy')
    clock = pygame.time.Clock()

#    chip8 = Chip8('M:/BACKUPS/Coding/Python/roms/PONG')
    chip8 = Chip8(pygame.display.set_mode((512, 256)), 'C:/Users/Ian Ling/Documents/bk/chip8/roms/PONG2')

    while True:
        # if we're updating the screen, make sure the screen only updates at 60FPS max
        if chip8.getDrawFlag():
            clock.tick(60)
            pygame.display.update()
            pygame.event.clear() # we don't use pygame events
            chip8.setDrawFlag(False)
            chip8.emulateCycle()
        else:  # if we're not updating the screen, run other opcodes as quickly as possible
            chip8.emulateCycle()
        #set key press flags...

main()
