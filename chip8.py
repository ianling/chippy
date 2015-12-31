import array
import binascii


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
        pcIncrementBy = 2 # amount to increase pc by after cycle. 2 bytes by default

        if opcode == "00E0": # clear screen
            pass
        elif opcode == "00EE": # return from subroutine
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
            self.pc = opcode[1:]
            pcIncrementBy = 0

        # 3XNN - Skips the next instruction if V[X] == NN
        elif opcode[0] == "3":
            if self.v[int(opcode[1],16)] == opcodeLastByte:
                pcIncrementBy = 4 # jump ahead 4 bytes instead of the usual 2

        # 4XNN - Skips the next instruction if V[X] != NN
        elif opcode[0] == "4":
            if self.v[int(opcode[1],16)] != opcodeLastByte:
                pcIncrementBy = 4 # jump ahead 4 bytes instead of the usual 2

        # 5XY0 - Skips the next instruction if V[X] == V[Y]
        elif opcode[0] == "5":
            if self.v[int(opcode[1],16)] == self.v[int(opcode[2],16)]:
                pcIncrementBy = 4 # jump ahead 4 bytes instead of the usual 2

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
            self.v[int(opcode[1],16)] = self.v[int(opcode[2],16)]

        # 8XY1 - Sets V[X] = V[X] | V[Y]
        elif opcode[0] == "8" and opcode[3] == "1":
            self.v[int(opcode[1],16)] = hex(int(self.v[int(opcode[1],16)],16) | int(self.v[int(opcode[2],16)], 16))[2:]

        # 8XY2 - Sets V[X] = V[X] & V[Y]
        elif opcode[0] == "8" and opcode[3] == "2":
            self.v[int(opcode[1],16)] = hex(int(self.v[int(opcode[1],16)],16) & int(self.v[int(opcode[2],16)], 16))[2:]

        # 8XY3 - Sets V[X] = V[X] ^ V[Y]
        elif opcode[0] == "8" and opcode[3] == "3":
            self.v[int(opcode[1],16)] = hex(int(self.v[int(opcode[1],16)],16) ^ int(self.v[int(opcode[2],16)], 16))[2:]

        # 8XY4 - Sets V[X] += V[Y]. If V[X] + V[Y] > 255, then V[0xF] is set to 1, else set to 0
        elif opcode[0] == "8" and opcode[3] == "4":
            intVX = int(self.v[int(opcode[1],16)], 16)
            intVY = int(self.v[int(opcode[2],16)], 16)
            if intVX + intVY > 255:
                self.v[0xf] = 1
            else:
                self.v[0xf] = 0
            self.v[int(opcode[1],16)] = hex(intVX + intVY)[2:]

        # 8XY5 - Sets V[X]-= V[Y]. If V[X] - V[Y] < 0, then VF is set to 0, else set to 1
        elif opcode[0] == "8" and opcode[3] == "5":
            intVX = int(self.v[int(opcode[1],16)], 16)
            intVY = int(self.v[int(opcode[2],16)], 16)
            if intVX - intVY < 0:
                self.v[0xf] = 0
            else:
                self.v[0xf] = 1
            self.v[int(opcode[1],16)] = hex(intVX - intVY)[2:]

        # 8XY6 - Shifts VX right by one. VF is set to the value of the least significant bit of VX before the shift.


        # 8XY7 - Sets VX to VY minus VX. VF is set to 0 when there's a borrow, and 1 when there isn't.


        # 8XYE - Shifts VX left by one. VF is set to the value of the most significant bit of VX before the shift



        # ANNN - Sets I to the address NNN
        elif opcodeFirstByte[0] == "A":
            self.i = opcode[1:]

        # DXYN - Sprites stored in memory at location in index register (I), 8bits wide.
        #        Wraps around the screen. If when drawn, it clears a pixel,
        #        then register V[F] is set to 1. Otherwise it is zero.
        #        All drawing is XOR drawing (i.e. it toggles the screen pixels).
        #        Sprites are drawn starting at position V[X], V[Y].
        #        N is the number of 8bit rows that need to be drawn.
        #        If N is greater than 1, second line continues at position V[X], V[Y+1], and so on.
        elif opcodeFirstByte[0] == "D":
            pass

        self.pc += pcIncrementBy

    def getDrawFlag(self):
        return False
