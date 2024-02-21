################    INSTRUCTION TABLE   ################

#                       SHIFTS:
                    
#"literal"      "abbrev"    "argument"      "description"
#$  0           sh2a        ram_addr_cond       bus twice if alu cout or result eq_zero
#$  1           sh2c        ram_addr_cond       bus twice if alu cout
#$  2           sh2z        ram_addr_cond       bus twice if alu result eq_zero
#$  3           sh2u        none                bus twice unconditionally
#$  4           sh1a        ram_addr_cond       bus once if alu cout or result eq_zero
#$  5           sh1c        ram_addr_cond       bus once if alu cout
#$  6           sh1z        ram_addr_cond       bus once if alu result eq_zero
#$  7           sh1u        none                bus once unconditionally

#                       WRITES:

#"literal"      "abbrev"    "argument"      "description"
#$  8           r+r2        ram_addr_lsh        ram(addr) + r2 to r7
#$  9           r&r2        ram_addr_lsh        ram(addr) NAND r2 to r7
#$  a           wpcl        ram_addr_lsh        ram(addr) to PC lower, write PC lower byte to PC upper
#$  b           wram        ram_addr_lsh        r4,r3 to ram(addr)
#$  c           rpcu        none                PC upper to r4,r3
#$  d           rcon        constant            constant from rom to r5
#$  e           rext        none                external to r1,r0
#$  f           wext        select_peri         r1,r0 to external


#create look up table of instructions.
ROM_HEADER = "v2.0 raw\n"
lut = {}
with open("assembler2.py","r") as myself:
    for line in myself:
        if line[:2]=="#$":
            line = line.replace("\n","")
            line = line.replace("#$","")
            line = line.split(" ")
            lut_arr = []
            for token in line:
                if len(token)!=0:
                    lut_arr.append(token)
            lut[lut_arr[1]] = lut_arr[0]

#reset rom
with open("rom.txt","w")as fp:
    fp.write(ROM_HEADER)

#load and tokenize program to be compiled.
line_counter,program,to_compile = 1,{},str(input("compile: (do not include file extension)"))
with open(to_compile+".txt","r") as fp:
    for line in fp:
        line = line.replace("\n","")
        line = line.replace("\t","")
        line = line.split("#")[0]
        line = line.split(" ")
        if len(line[0]) != 0:   #filter out the empties
            if len(line) == 1:  #preprocess the instructions without attributes
                line.append("0")
            program[line_counter] = line
        line_counter = line_counter + 1
    #print("Length of program to assemble: " +str(len(program)))

#parse instruction tokens.
rom = {}
instruction_pointer = 0
for instruction in program:
    if program[instruction][0] in lut:
        to_write = ""
        for token in program[instruction]:
            to_write = to_write + lut[token]
        rom[instruction_pointer] = to_write
        instruction_pointer = instruction_pointer + 1
with open("sim0.txt","w")as fp:
    fp.write("##########0##########\n")
    for instruction in rom:
        fp.write("rom "+str(instruction)+" "+str(hex(int(rom[instruction],16))[2:])+"\n")
    fp.write("pc 0 00\n")
    fp.write("pc 1 00\n")

#processor simulator helper methods
def ram(processor_state,instruction):       #RETURN TYPE INT
    r7 = reg(processor_state,"7")*4096
    r6 = reg(processor_state,"6")*256
    r5 = reg(processor_state,"5")*16
    lsb = int(instruction[1],16)
    address = (r7 + r6 + r5 + lsb)%32768
    if str(address) in processor_state["ram"]:
        return int(processor_state["ram"][str(address)],16)
    else:
        return 0
def reg(processor_state,select_register):   #RETURN TYPE INT
    if str(select_register) in processor_state["reg"]:
        return int(processor_state["reg"][str(select_register)],16)
    else:
        return 0
def pc(processor_state):                    #RETURN TYPE STR
    if "1" in processor_state["pc"]:    
        return processor_state["pc"]["1"]
    else:
        return "00"
def shift(processor_state,shift_amount):
    while shift_amount > 0:
        r7 = reg(processor_state,"7")
        r6 = reg(processor_state,"6")
        r5 = reg(processor_state,"5")
        r4 = reg(processor_state,"4")
        r3 = reg(processor_state,"3")
        r2 = reg(processor_state,"2")
        r1 = reg(processor_state,"1")
        r0 = reg(processor_state,"0")
    
        processor_state["reg"]["7"] = str(hex(((int(str(r0%2),2)*8) + int(str(r7//2),16)))[2:])
        processor_state["reg"]["6"] = str(hex(((int(str(r7%2),2)*8) + int(str(r6//2),16)))[2:])
        processor_state["reg"]["5"] = str(hex(((int(str(r6%2),2)*8) + int(str(r5//2),16)))[2:])
        processor_state["reg"]["4"] = str(hex(((int(str(r5%2),2)*8) + int(str(r4//2),16)))[2:])
        processor_state["reg"]["3"] = str(hex(((int(str(r4%2),2)*8) + int(str(r3//2),16)))[2:])
        processor_state["reg"]["2"] = str(hex(((int(str(r3%2),2)*8) + int(str(r2//2),16)))[2:])
        processor_state["reg"]["1"] = str(hex(((int(str(r2%2),2)*8) + int(str(r1//2),16)))[2:])
        processor_state["reg"]["0"] = str(hex(((int(str(r1%2),2)*8) + int(str(r0//2),16)))[2:])

        shift_amount = shift_amount - 1

    return processor_state
def nand(operandA,operandB):                #RETURN TYPE INT
    operandA,operandB = str(bin(operandA)[2:]),str(bin(operandB)[2:])
    for i in range(4-len(operandA)):
        operandA = "0"+operandA
    for i in range(4-len(operandB)):
        operandB = "0"+operandB
    output = ""
    for i in range(len(operandA)):
        characterA,characterB = operandA[i],operandB[i]
        if (characterA == "1") and (characterB == "1"):
            output = output + "0"
        else:
            output = output + "1"
    return int(output,2)

#simulate a single instruction
def simulate_instruction(processor_name,instruction,index):
    #load processor state from processor file and verify instruction validity
    processor_state,line_counter = {"rom":{},"ram":{},"pc":{},"reg":{}},0
    index_found = False
    try:
        with open(str(processor_name)+str(index)+".txt","r") as processor:
            for line in processor:
                line = line.replace("\n","")
                line_counter = line_counter + 1
                if not index_found:
                    if "##########" in line:
                        if line.split("##########")[1]==str(index):
                            index_found = True
                else:
                    if "##########" in line:
                        index_found = False
                    else:
                        line = line.split("#")[0]
                        if(len(line)>0):
                            line = line.split(" ")
                            if line[1] not in processor_state[line[0]]:
                                processor_state[line[0]][line[1]]=line[2]
                            else:
                                print("Simulation error at line "+str(line_counter)+": REDEFINE "+line[0].upper()+" VALUE AT ADDRESS "+str(line[1]))
            if len(processor_state["rom"]) == 0:
                return None
    except:
        return None
    
    #GENERAL PURPOSE FLAGS
    ram_str = str(hex(ram(processor_state,instruction)%16)[2:])+str(hex(ram(processor_state,instruction)//16)[2:])
    operandA = ram(processor_state,instruction)%16
    operandB = reg(processor_state,"2")
    operation8 = operandA + operandB
    operation9 = nand(operandA,operandB)
    cout_flag = (operandA + operandB) > 15
    zero_flag = operandB == 0
    
    #perform action based upon instruction
    match instruction[0]:
        case "0":   #shift 2 if zero or shift 2 if cout
            if cout_flag or zero_flag:
                processor_state = shift(processor_state,2)
        case "1":   #shift 2 if cout
            if cout_flag:
                processor_state = shift(processor_state,2)
        case "2":   #shift 2 if zero
            if zero_flag:
                processor_state = shift(processor_state,2)
        case "3":   #shift 2
            processor_state = shift(processor_state,2)
        case "4":   #shift 1 if zero or shift 1 if cout
            if cout_flag or zero_flag:
                processor_state = shift(processor_state,1)
        case "5":   #shift 1 if cout
            if cout_flag:
                processor_state = shift(processor_state,1)
        case "6":   #shift 1 if zero
            if zero_flag:
                processor_state = shift(processor_state,1)
        case "7":   #shift 1
            processor_state = shift(processor_state,1)
        case "8":   #r(addr) + r2
            processor_state["reg"]["r7"] = str(operation8//16)
            processor_state["reg"]["r6"] = str(operation8%16)
        case "9":   #r(addr) NAND r2
            processor_state["reg"]["r7"] = str(operation9//16)
            processor_state["reg"]["r6"] = str(operation9%16)
        case "a":   #ram(addr) to PC lower, write PC lower byte to PC upper
            if "0" in processor_state["pc"]:
                processor_state["pc"]["1"] = processor_state["pc"]["0"]
            else:   
                processor_state["pc"]["1"] = "00"
            processor_state["pc"]["0"] = ram_str
        case "b":   #r4,r3 to ram(addr)
            r7 = reg(processor_state,"7")*4096
            r6 = reg(processor_state,"6")*256
            r5 = reg(processor_state,"5")*16
            r4 = reg(processor_state,"4")*16
            r3 = reg(processor_state,"3")
            lsb = int(instruction[1],16)
            address = (r7 + r6 + r5 + lsb)%32768
            write_byte = str(hex(r4+r3)[2:])
            processor_state["ram"][str(address)] = write_byte
        case "c":   #PC upper to r4,r3
            processor_state["reg"]["4"] = pc(processor_state)[0]
            processor_state["reg"]["3"] = pc(processor_state)[1]
        case "d":   #constant from rom to r5
            processor_state["reg"]["5"] = instruction[1]
    
    #writeback to next state file.
    next_program_counter = int(processor_state["pc"]["1"],16)*16 + int(processor_state["pc"]["0"],16)+1
    with open(str(processor_name)+str(index+1)+".txt","w") as fp:
        fp.write("##########"+str(index+1)+"##########"+instruction+"\n")
        for data_type in processor_state:
            if (data_type != "pc") or (instruction[0] == "a"):
                for location in processor_state[data_type]:
                    fp.write(data_type+" "+location+" "+processor_state[data_type][location]+"\n")
            else:
                #print(str(hex(next_program_counter%16))[2:])
                lower = str(hex(next_program_counter%256))[2:]
                for i in range(2-len(lower)):
                    lower = "0"+lower
                upper = str(hex(next_program_counter//256))[2:]
                for i in range(2-len(upper)):
                    upper = "0"+upper

                fp.write("pc 0 "+lower+"\n")
                fp.write("pc 1 "+upper)
            fp.write("\n")  
    
    if str(next_program_counter) in processor_state["rom"]:
        return processor_state["rom"][str(next_program_counter)],None
    else:
        return None,str(processor_state["pc"]["1"]+processor_state["pc"]["0"])

#run the assembled program on a simulated processor
processor_state = {}    
max_depth = 100
iteration = 0    
next_instruction = rom[0],None       
while iteration < max_depth: #each instruction is an int



    next_instruction = simulate_instruction("sim",next_instruction[0],iteration)
        
    if next_instruction[0] == None:
        print("Simulator reached unwritten location in ROM: "+str(next_instruction[1])+"\n")
        iteration = max_depth
    
    iteration = iteration + 1






################    ASSEMBLABLES   ################
#$  0   0
#$  1   1
#$  2   2
#$  3   3
#$  4   4
#$  5   5
#$  6   6
#$  7   7
#$  8   8
#$  9   9
#$  a   10
#$  b   11
#$  c   12
#$  d   13
#$  e   14
#$  f   15
