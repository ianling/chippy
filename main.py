"""
main


"""
from chip8 import Chip8
import pygame
from sys import argv, exit
from os.path import isfile


def main():
    # get rom path
    rom = argv[1]
    print rom
    if not isfile(rom):
        exit()

    # CHIP-8 native graphics are 64x32
    pygame.init()
    pygame.display.set_caption('chippy')
    clock = pygame.time.Clock()
    chip8 = Chip8(pygame.display.set_mode((512, 256)), rom)

    while True:
        if chip8.getDrawFlag():
            clock.tick(60)  # CHIP-8 native refresh rate is 60Hz
            pygame.display.update()
            # check if the user tried to close the window
            event = pygame.event.poll()
            if event.type == pygame.QUIT:
                exit()
            pygame.event.clear()  # we don't use pygame events
            chip8.setDrawFlag(False)

        chip8.emulateCycle()


main()
