ROM_HEADER = "v2.0 raw\n"
program = {} #list of binary literal strings
rom_pointer = 0
rom = {}
ROM_ADDRESS_BITS = 15
routine_names_and_locations = {"test":14}
lut_dict = {}
to_compile = str(input("compile: (do not include file extension)"))
line_counter = 1
poopies = ['',' ',""," ","\n"," \n"]
failed = False
variables = {}


#initialize rom structure (the * character means that it is unmodified data.)
for i in range(2**ROM_ADDRESS_BITS):
    rom[i]="*00"

#load in program to be compiled.
with open(to_compile+".txt","r") as fp:
    for line in fp:
        line = line.replace("\n","")
        line = line.replace("\t","")
        line = line.split("#")[0]
        line = line.split(" ")
        
        #print(str(line_counter) + " " + str(len(line[0]))+ " " + str(line))
        if len(line[0]) != 0:
            program[line_counter] = line
        line_counter = line_counter + 1

#interpret text RTL through LUT into binary literal
with open("lut_convert.txt","r") as fp:
    for line in fp:
        if "#" not in line:
            line = line.split(" ")
            lut_dict[line[0]] = line[1].replace("\n","")

#reset and wipe
with open("rom.txt","w")as fp:
    fp.write(ROM_HEADER)

#parse reserved keywords
def parse_reserved(program_line):
    if(program_line[0] == "every"):
        spacer = int(program_line[1])
        command = program_line[2]
        for i in range(int((2**ROM_ADDRESS_BITS)/int(spacer))):
            if i != 0:
                rom[(i*spacer)+1]=lut_dict[command]
    elif(program_line[0] == "routine"):
        print("creating a new routine called "+str(program_line[1])+" referencing rom location "+str(rom_pointer))
        routine_names_and_locations[program_line[1]]=rom_pointer
    
    #The loadpointer reserved keyword will create a series of instructions which populates a specified
    #location in ram with the pointer value.
    # elif(program_line[0] == "pointer"):
    #     pointer_name = program_line[1]
    #     if pointer_name in routine_names_and_locations:  #if the pointer exists
    #         #Load the pointer:
    #         print("reference to pointer "+pointer_name+" at "+str(routine_names_and_locations[pointer_name])+" found.")
    #         routine_pointer = routine_names_and_locations[program_line[1]]
    #         hex_pointer_array = ["0","0","0","0"]
    #         pointer_index = 3
    #         HEX_POINTER = str(hex(routine_pointer))[2:]
    #         for character in HEX_POINTER:
    #             hex_pointer_array[pointer_index] = character
    #             pointer_index = pointer_index - 1
    #         #TODO!
    #         #build_load_stem_for_4b_array(hex_pointer_array,routine_pointer)
    #         #print("created following instructions to load pointer at "+str(rom_pointer)+"\n")
    #     else:
    #         print("reference to unknown pointer "+program_line[1])
    #         exit()
                
#?     
def build_load_stem_for_4b_array(hex_pointer_array,routine_pointer):
    #todo: make sure rom has vacancy for entire constant build.
    to_add_to_pointer = 0
    rom[rom_pointer] = "D"+str(hex_pointer_array[3])
    rom[rom_pointer+1] = "00"
    rom[rom_pointer+2] = "00"
    if(routine_pointer > 15):
        rom[rom_pointer+3] = "D"+str(hex_pointer_array[2])
        rom[rom_pointer+4] = "00"
        rom[rom_pointer+5] = "00"
        rom[rom_pointer+6] = "B0"
        if(routine_pointer > 255):
            rom[rom_pointer+7] = "D"+str(hex_pointer_array[1])
            rom[rom_pointer+8] = "00"
            rom[rom_pointer+9] = "00"
            if(routine_pointer > 4095):
                rom[rom_pointer+10] = "D"+str(hex_pointer_array[0])
                rom[rom_pointer+11] = "00"
                rom[rom_pointer+12] = "00"
                rom[rom_pointer+13] = "B1"
                to_add_to_pointer = 15
            else:
                rom[rom_pointer+10] = "00"
                rom[rom_pointer+11] = "00"
                rom[rom_pointer+12] = "B1"
                to_add_to_pointer = 14
    else:
        rom[rom_pointer+3] = "00"
        rom[rom_pointer+4] = "00"
        rom[rom_pointer+5] = "B0"
        to_add_to_pointer = 6
    return to_add_to_pointer

#
for line in program:
    if program[line][0] not in poopies:
        print("--------------------------------------------------------------------------------")
        print("parsing: "+str(program[line])+"\n")
        to_write = ""
        for command_name_or_data in program[line]:
            if command_name_or_data not in poopies:
                if command_name_or_data in lut_dict:
                    if(lut_dict[command_name_or_data] == "RESERVED"):
                        to_add_to_pointer = parse_reserved(program[line])
                        break
                    else:
                        to_write = to_write + lut_dict[command_name_or_data]    
                #elif command_name_or_data in 
                else:
                    failed = True
                    print("unknown token @ "+str(line)+" : "+str(command_name_or_data))
        print(to_write)

        #TODO further develop overlapping checking
        if rom[rom_pointer] == "*00":
            #print("no util exists yetat this location.")
            rom[rom_pointer] = to_write
            rom_pointer = rom_pointer + 1
        elif rom[rom_pointer] != "A0":
            
            a = 1
        else:
            print("error! overwriting util.")

#write rom structure into text file
with open("rom.txt","a")as fp:
    for line in rom:
        fp.write(rom[line].replace("*","")+"\n")
if not failed:
    print("compiled successfully\n")

