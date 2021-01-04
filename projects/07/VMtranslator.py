#!/usr/bin/env python3
class VMTranslator():
    def __init__(self, vm, fname):
        self.vm = vm
        self.fname = fname
        self.stacktoD = ["@SP", "M=M-1", "A=M", "D=M"]
        self.stackpless = ["@SP", "M=M-1", "A=M"]
        self.toSP = ["@SP", "A=M"]
        self.SPplus = ["@SP", "M=M+1"]
        self.push = ["@SP", "A=M", "M=D"] + self.SPplus
        self.pop = ["@R13", "M=D"] + self.stacktoD + ["@R13", "A=M", "M=D"]
        self.arithmetic = {
            "add":  self.stacktoD + self.stackpless + ["M=D+M"] + self.SPplus,
            "sub":  self.stacktoD + self.stackpless + ["M=M-D"] + self.SPplus,
            "neg":  self.stackpless + ["M=-M"] + self.SPplus,
            "and":  self.stacktoD + self.stackpless + ["M=D&M"] + self.SPplus,
            "or":   self.stacktoD + self.stackpless + ["M=D|M"] + self.SPplus,
            "not":  self.stackpless + ["M=!M"] + self.SPplus,
        }
        self.segs = {
            "local":    "LCL",
            "argument": "ARG",
            "this":     "THIS",
            "that":     "THAT"
        }
        self.pointers = {
            "0":        "THIS",
            "1":        "THAT"
        }
        self.nocomment = self.clear()
        self.final = self.process()

    def _translator(self, linenumber, cmd):
        cmds = ["// " + cmd]

        if cmd in self.arithmetic:
            cmds = cmds + self.arithmetic[cmd]
        elif cmd in ["eq", "lt", "gt"]:
            comp = self._bool(cmd, linenumber)
            cmds = cmds + comp[cmd]
        elif "push" in cmd:
            cmds = cmds + self._push(cmd)
        elif "pop" in cmd:
            cmds = cmds + self._pop(cmd)
        else:
            print("syntax error" + cmd)
        return cmds

    def _bool(self, cmd, linenumber):
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
        return comp

    def _push(self, cmd):
        op, seg, i = cmd.split()  # cmd on format "push/pop segment index"
        if seg in self.segs:
            cmds = ["@"+self.segs[seg], "D=M",
                    "@"+i, "A=D+A", "D=M"] + self.push
        elif seg == "static":
            cmds = ["@"+self.fname+"."+i, "D=M"] + self.push
        elif seg == "temp":
            cmds = ["@"+i, "D=A", "@5", "A=D+A", "D=M"] + self.push
        elif seg == "pointer":
            cmds = ["@"+self.pointers[i], "D=M"] + self.push
        elif seg == "constant":
            cmds = ["@"+i, "D=A"] + self.push
        else:
            print("segmentation error", seg)
        return cmds

    def _pop(self, cmd):
        op, seg, i = cmd.split()  # cmd on format "push/pop segment index"
        if seg in self.segs:
            cmds = ["@"+self.segs[seg], "D=M", "@"+i, "D=D+A"] + self.pop
        elif seg == "static":
            cmds = self.stacktoD + ["@"+self.fname+"."+i, "M=D"]
        elif seg == "temp":
            cmds = ["@"+i, "D=A", "@5", "D=D+A"] + self.pop
        elif seg == "pointer":
            cmds = self.stacktoD + ["@"+self.pointers[i], "M=D"]
        else:
            print("segmentation error", seg)
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
                nocomment[i] = cmd.split("/")[0].strip()
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
    parser.add_argument("path", type=str, help="path to the .vm file",
                        nargs='+')
    args = parser.parse_args()
    paths = args.path

    for path in paths:
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
        print(outpath)

        for line in final:
            output.write(line+"\n")
        output.close()
