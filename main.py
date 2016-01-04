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
    display = pygame.display.set_mode((512, 256))
    pygame.display.set_caption('chippy')
    clock = pygame.time.Clock()

    chip8 = Chip8('M:/BACKUPS/Coding/Python/roms/PONG')

    while True:
        chip8.emulateCycle()
        pygame.display.update()
        clock.tick(60)
        #if chip8.getDrawFlag:
        #    updateScreen()
        #set key press flags...

main()
