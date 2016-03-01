import array
import binascii
from random import randint

class Chip8:
    def __init__(self, name):
        self.rom = open(name, "rb")
        self.memory = [0x0]*4096
        self.stack = [None]*16
        self.sp = 0
        self.v = [0]*16
        self.i = 0
        self.pc = 0x200
        self.delayTimer = None
        self.soundTimer = None
        self.key = [0]*16
        # via http://www.multigesture.net/articles/how-to-write-an-emulator-chip-8-interpreter
        self.fontSet = [0xF0, 0x90, 0x90, 0x90, 0xF0,  # 0
                        0x20, 0x60, 0x20, 0x20, 0x70,  # 1
                        0xF0, 0x10, 0xF0, 0x80, 0xF0,  # 2
                        0xF0, 0x10, 0xF0, 0x10, 0xF0,  # 3
                        0x90, 0x90, 0xF0, 0x10, 0x10,  # 4
                        0xF0, 0x80, 0xF0, 0x10, 0xF0,  # 5
                        0xF0, 0x80, 0xF0, 0x90, 0xF0,  # 6
                        0xF0, 0x10, 0x20, 0x40, 0x40,  # 7
                        0xF0, 0x90, 0xF0, 0x90, 0xF0,  # 8
                        0xF0, 0x90, 0xF0, 0x10, 0xF0,  # 9
                        0xF0, 0x90, 0xF0, 0x90, 0x90,  # A
                        0xE0, 0x90, 0xE0, 0x90, 0xE0,  # B
                        0xF0, 0x80, 0x80, 0x80, 0xF0,  # C
                        0xE0, 0x90, 0x90, 0x90, 0xE0,  # D
                        0xF0, 0x80, 0xF0, 0x80, 0xF0,  # E
                        0xF0, 0x80, 0xF0, 0x80, 0x80]  # F
        # store fontset in memory
        for index, byte in enumerate(self.fontSet):
            self.memory[index] = byte

        # store game in memory, starting at position 512
        memoryPointer = 512
        while True:
            byte = self.rom.read(1)
            if not byte:
                break
            self.memory[memoryPointer] = binascii.b2a_hex(byte).upper()
            memoryPointer += 1

    def emulateCycle(self):
        # CHIP-8 opcodes are two bytes long, big-endian
        opcodeFirstByte = str(self.memory[self.pc])
        opcodeLastByte = str(self.memory[self.pc+1])
        opcode = opcodeFirstByte + opcodeLastByte
        print opcode
        pcIncrementBy = 2  # amount to increase pc by after cycle. 2 bytes by default

        if opcode == "00E0":  # clear screen
            pass
        elif opcode == "00EE":  # return from subroutine
            self.sp -= 1
            self.pc = self.stack[self.sp]

        # 1NNN - Jumps to address NNN
        elif opcode[0] == "1":
            self.pc = int(opcode[1:],16)
            pcIncrementBy = 0

        # 2NNN - Calls subroutine at NNN
        elif opcode[0] == "2":
            self.stack[self.sp] = self.pc
            self.sp += 1
            self.pc = int(opcode[1:], 16)
            pcIncrementBy = 0

        # 3XNN - Skips the next instruction if V[X] == NN
        elif opcode[0] == "3":
            if self.v[int(opcode[1], 16)] == opcodeLastByte:
                pcIncrementBy = 4  # jump ahead 4 bytes instead of the usual 2

        # 4XNN - Skips the next instruction if V[X] != NN
        elif opcode[0] == "4":
            if self.v[int(opcode[1], 16)] != opcodeLastByte:
                pcIncrementBy = 4  # jump ahead 4 bytes instead of the usual 2

        # 5XY0 - Skips the next instruction if V[X] == V[Y]
        elif opcode[0] == "5":
            if self.v[int(opcode[1], 16)] == self.v[int(opcode[2],16)]:
                pcIncrementBy = 4  # jump ahead 4 bytes instead of the usual 2

        # 6XNN - Sets V[X] to NN
        elif opcode[0] == "6":
            self.v[int(opcode[1], 16)] = opcodeLastByte

        # 7XNN - Adds NN to V[X]
        elif opcode[0] == "7":
            vx = int(self.v[int(opcode[1], 16)], 16)
            nn = int(opcodeLastByte, 16)
            sum = hex(vx + nn)[2:]
            self.v[int(opcode[1], 16)] = sum

        # 8XY0 - Sets V[X] = V[Y]
        elif opcode[0] == "8" and opcode[3] == "0":
            self.v[int(opcode[1], 16)] = self.v[int(opcode[2], 16)]

        # 8XY1 - Sets V[X] = V[X] | V[Y]
        elif opcode[0] == "8" and opcode[3] == "1":
            self.v[int(opcode[1], 16)] = hex(int(self.v[int(opcode[1], 16)], 16) | int(self.v[int(opcode[2], 16)], 16))[2:]

        # 8XY2 - Sets V[X] = V[X] & V[Y]
        elif opcode[0] == "8" and opcode[3] == "2":
            self.v[int(opcode[1], 16)] = hex(int(self.v[int(opcode[1], 16)], 16) & int(self.v[int(opcode[2], 16)], 16))[2:]

        # 8XY3 - Sets V[X] = V[X] ^ V[Y]
        elif opcode[0] == "8" and opcode[3] == "3":
            self.v[int(opcode[1], 16)] = hex(int(self.v[int(opcode[1], 16)], 16) ^ int(self.v[int(opcode[2], 16)], 16))[2:]

        # 8XY4 - Sets V[X] += V[Y]. If V[X] + V[Y] > 255, then V[0xF] is set to 1, else set to 0
        elif opcode[0] == "8" and opcode[3] == "4":
            intVX = int(self.v[int(opcode[1], 16)], 16)
            intVY = int(self.v[int(opcode[2], 16)], 16)
            if intVX + intVY > 255:
                self.v[0xf] = 1
            else:
                self.v[0xf] = 0
            self.v[int(opcode[1],16)] = hex(intVX + intVY)[2:]

        # 8XY5 - Sets V[X]-= V[Y]. If V[X] - V[Y] < 0, then VF is set to 0, else set to 1
        elif opcode[0] == "8" and opcode[3] == "5":
            intVX = int(self.v[int(opcode[1], 16)], 16)
            intVY = int(self.v[int(opcode[2], 16)], 16)
            if intVX - intVY < 0:
                self.v[0xf] = 0
            else:
                self.v[0xf] = 1
            self.v[int(opcode[1], 16)] = hex(intVX - intVY)[2:]

        # 8XY6 - Shifts VX right by one. VF is set to the value of the least significant bit of VX before the shift.
        elif opcode[0] == "8" and opcode[3] == "6":
            intVX = int(self.v[int(opcode[1], 16)], 16)
            binVX = bin(intVX)
            self.v[int(opcode[1], 16)] = intVX >> 1
            self.v[0xf] = binVX[-1]


        # 8XY7 - Sets VX to VY minus VX. VF is set to 0 when there's a borrow, and 1 when there isn't.
        elif opcode[0] == "8" and opcode[3] == "7":
            intVX = int(self.v[int(opcode[1], 16)], 16)
            intVY = int(self.v[int(opcode[2], 16)], 16)
            if intVY - intVX < 0:
                self.v[0xf] = 0
            else:
                self.v[0xf] = 1
            self.v[int(opcode[1], 16)] = hex(intVY - intVX)[2:]

        # 8XYE - Shifts VX left by one. VF is set to the value of the most significant bit of VX before the shift
        elif opcode[0] == "8" and opcode[3] == "E":
            intVX = int(self.v[int(opcode[1], 16)], 16)
            binVX = format(intVX, '#010b')
            self.v[int(opcode[1], 16)] = intVX << 1
            self.v[0xf] = binVX[2]

        # 9XY0 - Skips the next instruction if VX doesn't equal VY.
        elif opcodeFirstByte[0] == "9":
            if self.v[int(opcode[1], 16)] != self.v[int(opcode[2], 16)]:
                pcIncrementBy = 4 # jump ahead 4 bytes instead of the usual 2


        # ANNN - Sets I to the address NNN
        elif opcodeFirstByte[0] == "A":
            self.i = opcode[1:]

        # CXNN - Sets V[X] to the result of a bitwise and operation on a random number and NN.
        elif opcodeFirstByte[0] == "C":
            self.v[int(opcode[1], 16)] = hex(int(opcode[2:], 16) & randint(0,255))[2:]


        # DXYN - Sprites stored in memory at location in index register (I), 8bits wide.
        #        Wraps around the screen. If when drawn, it clears a pixel,
        #        then register V[F] is set to 1. Otherwise it is zero.
        #        All drawing is XOR drawing (i.e. it toggles the screen pixels).
        #        Sprites are drawn starting at position V[X], V[Y].
        #        N is the number of 8bit rows that need to be drawn.
        #        If N is greater than 1, second line continues at position V[X], V[Y+1], and so on.
        elif opcodeFirstByte[0] == "D":
            pass

        # EX9E - Skips the next instruction if the key stored in VX is pressed.
        elif opcodeFirstByte[0] == "E" and opcodeLastByte == "9E":
            pass

        # EXA1 - Skips the next instruction if the key stored in VX isn't pressed.
        elif opcodeFirstByte[0] == "E" and opcodeLastByte == "A1":
            pass

        # FX07 - Sets VX to the value of the delay timer.
        elif opcodeFirstByte[0] == "F" and opcodeLastByte == "07":
            self.v[int(opcode[1], 16)] = self.delayTimer

        # FX0A - A key press is awaited, and then stored in VX.
        elif opcodeFirstByte[0] == "F" and opcodeLastByte == "0A":
            pass

        # FX15 - Sets the delay timer to VX.
        elif opcodeFirstByte[0] == "F" and opcodeLastByte == "15":
            self.delayTimer = self.v[int(opcode[1], 16)]

        # FX18 - Sets the sound timer to VX.
        elif opcodeFirstByte[0] == "F" and opcodeLastByte == "18":
            self.soundTimer = self.v[int(opcode[1], 16)]

        # FX1E- Adds VX to I.
        elif opcodeFirstByte[0] == "F" and opcodeLastByte == "1E":
            intVX = int(self.v[int(opcode[1], 16)], 16)
            intI = int(self.i, 16)
            self.i = hex(intI + intVX)[2:]

        # FX29- Sets I to the location of the sprite for the character in VX.
        #       Characters 0-F (in hexadecimal) are represented by a 4x5 font.
        elif opcodeFirstByte[0] == "F" and opcodeLastByte == "29":
            pass

        # FX33- Stores the Binary-coded decimal representation of VX,
        #       with the most significant of three digits at the address in I,
        #       the middle digit at I plus 1, and the least significant digit at I plus 2.
        #       (In other words, take the decimal representation of VX,
        #       place the hundreds digit in memory at location in I,
        #       the tens digit at location I+1, and the ones digit at location I+2.)
        elif opcodeFirstByte[0] == "F" and opcodeLastByte == "33":
            intVX = format(int(self.v[int(opcode[1], 16)], 16), '03') # padded with zeroes if <100 or <10
            self.memory[int(self.i, 16)] = intVX[0]
            self.memory[int(self.i, 16)+1] = intVX[1]
            self.memory[int(self.i, 16)+2] = intVX[2]

        # FX55- Stores V0 to VX (including VX) in memory starting at address I.
        elif opcodeFirstByte[0] == "F" and opcodeLastByte == "55":
            x = int(opcode[1], 16)
            for vIterator in range(0, x+1):
                self.memory[int(self.i, 16)+vIterator] = self.v[vIterator]

        # FX65- Fills V0 to VX (including VX) with values from memory starting at address I.
        elif opcodeFirstByte[0] == "F" and opcodeLastByte == "65":
            x = int(opcode[1], 16)
            for vIterator in range(0, x+1):
                self.v[vIterator] = self.memory[int(self.i, 16)+vIterator]

        self.pc += pcIncrementBy

    def getDrawFlag(self):
        return False
