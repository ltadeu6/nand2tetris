#!/usr/bin/env python3
class Assembler():
    def __init__(self, asm):
        self.varaddr = 16
        self.asm = asm
        self.symbols = {
            "R0":       0,
            "R1":       1,
            "R2":       2,
            "R3":       3,
            "R4":       4,
            "R5":       5,
            "R6":       6,
            "R7":       7,
            "R8":       8,
            "R9":       9,
            "R10":      10,
            "R11":      11,
            "R12":      12,
            "R13":      13,
            "R14":      14,
            "R15":      15,
            "SCREEN":   16384,
            "KBD":      24576,
            "SP":       0,
            "LCL":      1,
            "ARG":      2,
            "THIS":     3,
            "THAT":     4
        }
        self.jumpT = {
            "":      "000",
            "JGT":   "001",
            "JEQ":   "010",
            "JGE":   "011",
            "JLT":   "100",
            "JNE":   "101",
            "JLE":   "110",
            "JMP":   "111",
        }
        self.compT = {
            "0":    "101010",
            "1":    "111111",
            "-1":   "111010",
            "D":    "001100",
            "A":    "110000",
            "!D":   "001101",
            "!A":   "110001",
            "-D":   "001111",
            "-A":   "110011",
            "D+1":  "011111",
            "A+1":  "110111",
            "D-1":  "001110",
            "A-1":  "110010",
            "D+A":  "000010",
            "D-A":  "010011",
            "A-D":  "000111",
            "D&A":  "000000",
            "D|A":  "010101",
        }
        self.nocomment = self.clear()
        self.final = self.process()

    def cparser(self, cmd):
        dest = ""
        jump = ""

        if "=" in cmd:  # has dest
            dest, cmd = cmd.split("=")
        if ";" in cmd:  # has jump
            cmd, jump = cmd.split(";")

        a = "1" if ("M" in cmd) else "0"
        if int(a):  # intruction with M
            cmd = cmd.replace("M", "A")

        d1 = "1" if ("A" in dest) else "0"
        d2 = "1" if ("D" in dest) else "0"
        d3 = "1" if ("M" in dest) else "0"

        head = "111"
        dest = d1+d2+d3

        return head, a, cmd, dest, jump

    def acommand(self, cmd):
        symbols = self.symbols
        varaddr = self.varaddr

        if cmd[1:].isdigit():  # a-command with numbers
            n = int(cmd[1:])
        elif cmd[1:] in symbols:  # a-command with a known name
            n = symbols[cmd[1:]]
        else:  # a-command with a unknown name
            self.symbols[cmd[1:]] = varaddr
            n = varaddr
            self.varaddr += 1

        a = bin(n)
        a = str(a)
        a = a[2:]
        return a.zfill(16)

    def ccommand(self, cmd):

        head, a, cmd, dest, jump = self.cparser(cmd)

        cmd = self.compT[cmd]
        jump = self.jumpT[jump]

        return head + a + cmd + dest + jump

    def clear(self):
        asm = self.asm
        npcmd = 0
        nocomment = list()
        for i, cmd in enumerate(asm):
            # remove white space and line brakers
            asm[i] = cmd.replace(" ", "").replace("\n", "")
        for i, cmd in enumerate(asm):
            if (cmd and not cmd[0] == "/"):  # remove line without commands
                nocomment.append(cmd)
        for i, cmd in enumerate(nocomment):
            if "/" in cmd:
                # remove comments in lines with commands
                nocomment[i] = cmd.split("/")[0]
            if cmd[0] == "(":
                # remove pseudo commands and store the line value in the table
                pcmd = cmd.replace("(", "").replace(")", "")
                self.symbols[pcmd] = i - npcmd
                npcmd += 1
        return nocomment

    def process(self):
        commands = self.nocomment
        final = list()
        for i, cmd in enumerate(commands):
            if cmd[0] == "@":  # a-instruction
                final.append(self.acommand(cmd))
            elif cmd[0] == "(":  # pseudo-instruction
                pass
            else:  # c-instruction
                final.append(self.ccommand(cmd))
        return final


if __name__ == "__main__":
    # parse arguments
    import argparse
    parser = argparse.ArgumentParser(
        description="Assembler for the hack computer")
    parser.add_argument("path", type=str, help="path to the .asm file")
    args = parser.parse_args()
    path = args.path

    # Read file
    inputf = open(path, "r")
    asm = inputf.readlines()
    inputf.close()

    # assemble file
    assembler = Assembler(asm)
    final = assembler.final

    # output file
    outpath = path[:-3] + "hack"
    output = open(outpath, "w")

    for line in final:
        output.write(line+"\n")
    output.close()
