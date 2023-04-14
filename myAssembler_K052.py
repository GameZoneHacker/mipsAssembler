import re #re (regular expression) module for matching operations
import numpy as np #numpy module for array operations
import pyparsing # pyparsing module for parsing operations
import time #time module to get current time
import sys #used to take arguments while executing via command prompt
import os #used to delete a file in this program

def read_file(): #reads the input file & removes all comments
    finput = open(sys.argv[1]+".asm","r")
    finput = finput.read()
    foutput = open(sys.argv[1]+"_nocom.asm","w") 
    comment = pyparsing.pythonStyleComment().suppress() #used to remove all comments from the file
    newtext = comment.transformString(finput) 
    foutput.write(newtext) # creates a new file without comments
    foutput.close()

def sanitize(): #ignores all undesired special characters (except $) & stores only alphanumerics in a list
    with open(sys.argv[1]+"_nocom.asm","r") as file:            
            res = [re.split(r'[`!@#%^&*()_+\=\[\]{};\':"\\|,.<>\/?~(\n)\1{}]| ',line) for line in file.readlines() if line.strip('\n')] 
    os.remove(sys.argv[1]+"_nocom.asm") # deletes the newly created file              
    for i in res:
        while '' in i:
            i.remove('') # removes empty elements from all sublists of res
    return res

def R_TYPE(f, j, opCode): #to convert R-Type instructions into hexcode
    f_bin="000000"+str(np.array(f)[1])+str(np.array(f)[2])+str(np.array(f)[0])+"00000"+str(opCode[j][1]) #generates binary equivalent of instruction
    f_hex=hex(int(f_bin,2))#generates hex equivalent of instruction
    new_hex=is_8bits(str(f_hex)) #adds leading zeros if the hex has less than 8 bits
    return new_hex

def S_TYPE(f, j, opCode): #to convert R-Type shift instructions into hexcode
    shamt = int(np.array(f)[2])
    shamt = is_5bits(str(bin(shamt%(1<<4))).replace("0b","")) # calculates 5 bit binary of shamt(positive or negative): it performs modulus of 'shamt' and 16 (1<<4)
    f_bin = "00000000000"+str(np.array(f)[1])+str(np.array(f)[0])+shamt+str(opCode[j][1]) #generates binary equivalent of instruction
    f_hex=hex(int(f_bin,2)) #generates hex equivalent of instruction
    new_hex=is_8bits(str(f_hex)) #adds leading zeros if the hex has less than 8 bits
    return new_hex

def I_TYPE(f, j, opCode): #to convert I-Type instructions into hexcode
    for i in f: #accesing args
        if len(i)<5 or i[0:2]=="0x": #checks for immediate or offset values in the args 
                imm_d=int(i) 
                if f.index(i) == 1:
                    rs = 2 # if the index of imm value is 1 then index of rs is set to 2
                else:
                    rs = 1 # if the index of imm value is 2 then index of rs is set to 1
    imm_d = is_16bits(str(bin(imm_d%(1<<4))).replace("0b","")) # calculates 16 bit binary of imm or offset(positive or negative): it performs modulus of 'imm' and 16 (1<<4)
    f_bin=str(opCode[j][1])+str(np.array(f)[rs])+str(np.array(f)[0])+str(imm_d) #generates binary equivalent of instruction
    f_hex=hex(int(f_bin,2)) #generates hex equivalent of instruction
    new_hex = is_8bits(f_hex) #adds leading zeros if the hex has less than 8 bits
    return new_hex

def is_8bits(n): #check if the input has 8 bits or not, if not then adds the remaining leading zeros
    if len(n[2:])<8:
        return "0x"+"0"*(8-len(n[2:]))+n[2:]
    return n

def is_5bits(n): #check if the input has 5 bits or not, if not then adds the remaining leading zeros
    if len(n)<5:
        return "0"*(5-len(n))+n

def is_16bits(n): #check if the input has 16 bits or not, if not then adds the remaining leading zeros
    if len(n)<16:
        return "0"*(16-len(n))+n

def main(): #main()
    # dictionary for all R & I type instructions 
    opCode = {"add" : ["R","100000"] , "addi" :["I","001000"] , "addiu" :["I","001001"] , "addu" :["R","100001"] , 
              "and" :["R","100100"], "andi" :["I","001100"], "lb" : ["I","100000"], "lbu" : ["I","100100"], "lhu" : ["I","100101"], 
              "ll" : ["I","110000"], "lui" : ["I","001111"], "lw" : ["I","100011"], "nor" : ["R","100111"], "or" : ["R","100101"], 
              "ori" : ["I","001101"], "slt" : "101010", "slti" : ["I","001010"], "sltiu" : ["I","001011"], "sltu" : ["R","101011"], 
              "sll" : ["S","000000"], "srl" : ["S","000010"], "sb" : ["I","101000"] , "sc" : ["I","111000"], "sh" : ["I","101001"], 
              "sw" : ["I","101011"], "sub" : ["R","100010"], "subu" : ["R","100011"]}

     # dictionary for all registers 
    reg = {"$zero" : "00000", "$at" : "00001", "$v0" : "00010", "$v1" : "00011", "$a0" : "00100", "$a1" : "00101", "$a2" : "00110", 
           "$a3" : "00111", "$t0" : "01000", "$t1" : "01001", "$t2" : "01010", "$t3" : "01011","$t4" : "01100","$t5" : "01101",
           "$t6" : "01110","$t7" : "01111","$s0" : "10000","$s1" : "10001","$s2" : "10010", "$s3" : "10011", "$s4" : "10100",
           "$s5" : "10101","$s6" : "10110","$s7" : "10111","$t8" : "11000", "$t9" : "11001","$k0" : "11010","$k1" : "11011", 
           "$gp" : "11100", "$sp" : "11101", "$fp" : "11110", "$ra" : "11111"}

    args = [] #list of arguments with their binary values, binary values not included for immediate or offset (only decimal)
    read_file() 
    res = sanitize() # list includes every line of the file as a sublist (after santizing)
    timestr = time.strftime("%Y%m%d-%H%M%S") 

    out  = open(timestr+"test.txt","a") # creates a new text file (output) everytime the program is executed (so that the previous outputs dont get overwritted)

    for i in res: #accesing each instructions (each sublist)
        for j in i: # loop for accessing registers & constants from the list
            if j in reg.keys(): # check if its a register
                args.append(reg[j]) # if true, append it to args list
            elif j.isdigit() or j[0:2]=="0x" or j<"0": #check if the arg is a decimal or hexadecimal value (immediate or offset)
                 args.append(j)  # if true, append it to args list
        if len(args) == 0: # if the above loop doesn't result in an empty list, generate an error
            out.write("Error! Can't read line..\n")            
        for j in i: #loop for performing instructions on the args
            if j in opCode.keys(): 
                if opCode[j][0] == "R": #checks if the format of the instruction is 'R' from opCode dictionary
                    new_hex = R_TYPE(args,j,opCode)  #calculates hex equivalent of the instruction
                    out.write(new_hex) #writes the hexcode of the instruction to the output file
                    out.write("\n")
                elif opCode[j][0] == "S":#checks if the format of the instruction is 'S' from opCode dictionary
                    new_hex=S_TYPE(args, j, opCode) #calculates hex equivalent of the instruction
                    out.write(new_hex) #writes the hexcode of the instruction to the output file
                    out.write("\n")
                else: #I-type
                    new_hex = I_TYPE(args, j, opCode) #calculates hex equivalent of the instruction
                    out.write(new_hex)#writes the hexcode of the instruction to the output file
                    out.write("\n")
        args.clear()  #clears the argument list for the next instruction
    out.close()

main()