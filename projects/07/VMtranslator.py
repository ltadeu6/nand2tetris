#!/usr/bin/env python3
class VMTranslator():
    def __init__(self, vm, fname):
        self.vm = vm
        self.fname = fname
        self.stacktoD = ["@SP", "M=M-1", "A=M", "D=M"]
        self.stackpless = ["@SP", "M=M-1", "A=M"]
        self.toSP = ["@SP", "A=M"]
        self.SPplus = ["@SP", "M=M+1"]
        self.arithmetic = {
            "add":  self.stacktoD + self.stackpless + ["M=D+M"] + self.SPplus,
            "sub":  self.stacktoD + self.stackpless + ["M=M-D"] + self.SPplus,
            "neg":  self.stackpless + ["M=-M"] + self.SPplus,
            "and":  self.stacktoD + self.stackpless + ["M=D&M"] + self.SPplus,
            "or":   self.stacktoD + self.stackpless + ["M=D|M"] + self.SPplus,
            "not":  self.stackpless + ["M=!M"] + self.SPplus,
        }
        self.nocomment = self.clear()
        self.final = self.process()

    def _translator(self, linenumber, cmd):
        cmds = ["// " + cmd]

        if cmd in self.arithmetic:
            cmds = cmds + self.stacktoD + self.arithmetic[cmd]

        elif "push" in cmd or "pop" in cmd:
            cmds = cmds + self._pushpop(cmd)

        elif cmd in comp:
            i = str(linenumber)
            true = ["D=M-D", "@TRUE_"+i]
            boolean = ["@FALSE_"+i, "0;JMP", "(TRUE_"+i+")", "D=-1",
                       "@CONTINUE_"+i, "0;JMP", "(FALSE_"+i+")",
                       "D=0", "(CONTINUE_"+i+")"]
            comp = {
                "eq":   self.stacktoD + self.stackpless + true + ["D;JEQ"] +
                boolean + self.toSP + ["M=D"] + self.SPplus,
                "gt":   self.stacktoD + self.stackpless + true + ["D;JGT"] +
                boolean + self.toSP + ["M=D"] + self.SPplus,
                "lt":   self.stacktoD + self.stackpless + true + ["D;JLT"] +
                boolean + self.toSP + ["M=D"] + self.SPplus,
            }
            cmds = cmds + self.stacktoD + comp[cmd]

        else:
            print("syntax error" + cmd)

        return cmds

    def _pushpop(self, cmd):
        push = ["@SP", "A=M", "M=D"] + self.SPplus
        pop = ["@R13", "M=D"] + self.stacktoD + ["@R13", "A=M", "M=D"]
        ssegs = {
            "local":    "LCL",
            "argument": "ARG",
            "this":     "THIS",
            "that":     "THAT"
        }
        pointers = {
            "0":        "THIS",
            "1":        "THAT"
        }
        op, seg, i = cmd.split()  # cmd on format "push/pop segment index"
        if op == "push":  # D<-data, SP++, *SP<-D
            if seg in ssegs:
                cmds = ["@"+ssegs[seg], "D=M", "@"+i, "A=D+A", "D=M"] + push
            elif seg == "static":
                cmds = ["@"+self.fname+"."+i, "D=M"] + push
            elif seg == "temp":
                cmds = ["@"+i, "D=A", "@5", "A=D+A", "D=M"] + push
            elif seg == "pointer":
                cmds = ["@"+pointers[i], "D=M"] + push
            elif seg == "constant":
                cmds = ["@"+i, "D=A"] + push
            else:
                print("segmentation error", seg)

        elif op == "pop":  # D<-addr, R13<-D, *R13<-*SP, SP--
            if seg in ssegs:
                cmds = ["@"+ssegs[seg], "D=M", "@"+i, "D=D+A"] + pop
            elif seg == "static":
                cmds = self.stacktoD + ["@"+self.fname+"."+i, "M=D"]
            elif seg == "temp":
                cmds = ["@"+i, "D=A", "@5", "D=D+A"] + pop
            elif seg == "pointer":
                cmds = self.stacktoD + ["@"+pointers[i], "M=D"]
            else:
                print("segmentation error", seg)
        else:
            print("operation error", op)

        return cmds

    def clear(self):
        vm = self.vm
        npcmd = 0
        nocomment = list()
        for i, cmd in enumerate(vm):
            # remove white space and line brakers
            vm[i] = cmd.replace("\n", "")
        for i, cmd in enumerate(vm):
            if (cmd and not cmd[0] == "/"):  # remove lines without commands
                nocomment.append(cmd)
        for i, cmd in enumerate(nocomment):
            if "/" in cmd:
                # remove comments in lines with commands
                nocomment[i] = cmd.split("/")[0]
        return nocomment

    def process(self):
        vmcmd = self.nocomment
        asmcmd = list()
        for i, cmd in enumerate(vmcmd):
            asmcmd = asmcmd + self._translator(i, cmd)
        return asmcmd


if __name__ == "__main__":
    # parse arguments
    import argparse
    parser = argparse.ArgumentParser(
        description="VM translator for the hack computer")
    parser.add_argument("path", type=str, help="path to the .vm file")
    args = parser.parse_args()
    path = args.path

    # Read file
    inputf = open(path, "r")
    vm = inputf.readlines()
    inputf.close()

    # assemble file
    fname = path.split("/")[-1][:-3]
    translator = VMTranslator(vm, fname)
    final = translator.final

    # output file
    outpath = path[:-2] + "asm"
    output = open(outpath, "w")

    for line in final:
        output.write(line+"\n")
    output.close()
