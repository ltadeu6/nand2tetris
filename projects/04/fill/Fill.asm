// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.

(START)
  @SCREEN
  D = A
  @i
  M = D //Start i = SCR(0)
  @8191
  D = D + A
  @R1
  M = D // R1 = SCR + 8191

  @KBD
  D=M
  @BLACK
  D;JNE // Go to black if KBD != 0
  @WHITE
  0;JMP // Else go to white

(BLACK) // key beeing pressed
  @i
  A = M
  M = -1 // RAM[i] = -1
  @i
  M = M + 1 // i = i + 1

  D = M
  @R1
  D = M - D
  @BLACK
  D;JGE // repeat if (R1 > i)

  @START
  0;JMP

(WHITE) // No key
  @i
  A = M
  M = 0 // RAM[i] = 0
  @i
  M = M + 1 // i = i + 1

  D = M
  @R1
  D = M - D
  @WHITE
  D;JGE // repeat if (R1 > i)

  @START
  0;JMP
