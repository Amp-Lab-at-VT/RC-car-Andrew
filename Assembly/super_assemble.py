#SUPER ASSEMBLY SYNTAX TABLE
#"Super Assembly Word"      "Parameter Type/Format"     "Composition"
#$  const                   Integer                     rcon_I0,sh2u,sh2u,rcon_I1,sh2u,sh2u
#$  clear                   none                        rcon_0,sh2u,sh2u,rcon_0,sh2u,sh2u,rcon_0,sh2u,sh2u,rcon_0,sh2u,sh2u,rcon_0,sh2u,sh2u,rcon_0,sh2u,sh2u,rcon_0,sh2u,sh2u,rcon_0,sh2u,sh2u
#$  ramcon                  Address,Integer             rcon_A1,sh2u,sh2u,rcon_A2,sh2u,sh2u,rcon_A3,sh2u,sh2u,sh2u,sh2u,sh2u,sh2u,sh2u,sh2u,rcon_I0,sh2u,sh2u,rcon_I1,sh2u,sh2u,wram_A0


#A note about super instructions:
#
#capitalized letters denote type. A is address, I is integer - these are used during parsing to ensure data ends up where its supposed to go.


lut = {}
with open ("super_assemble.py","r") as myself:
    for line in myself:
        if line[:2]=="#$":
            line = line.replace("\n","")
            line = line.replace("#$","")
            line = line.split(" ")
            lut_arr = []
            for token in line:
                if len(token)!=0:
                    lut_arr.append(token)
            lut[lut_arr[0]] = {lut_arr[1]:lut_arr[2]}

to_assemble = input("super assembly source: ")
rom,inserter,line_counter = {},0,0
with open(to_assemble+".txt","r")as source:
    for line in source:
        line = line.replace("\n","")
        preline = line
        line = line.split("#")[0]
        line = line.split(" ")
        if line[0] in lut:
            rom[inserter] = "# "+preline
            inserter = inserter + 1
            super_assembly_command = line[0]
            for parameter_type in lut[line[0]]:
                instructions = lut[line[0]][parameter_type].split(",")
                print(super_assembly_command,parameter_type,instructions)
                for instruction in instructions:
                    instruction = instruction.replace("_"," ")
                    p_types = parameter_type.split(",")
                    for p_type in p_types:
                        print(p_type[0],instruction)
                        if (p_type[0] in instruction) and (p_type[0].isupper()):
                            print("IN "+str(line))
                            index = int(instruction[len(instruction)-1])
                            if len(line) > 2:
                                if p_type[0] == "A":
                                    value = str(line[1][3-index])
                                elif p_type[0] == "I":
                                    value = str(line[2][1-index])
                            elif len(line) == 2:
                                value = str(line[1][1-index])
                            instruction = instruction[0:len(instruction)-3]+" "+str(int(value,16))
                            print("new instruction: "+instruction)
                            break
                    rom[inserter] = instruction
                    inserter = inserter + 1
                    line_counter = line_counter + 1

#print(rom)

with open("p1.txt","w") as fp:
    for line in rom:
        fp.write(rom[line]+"\n")