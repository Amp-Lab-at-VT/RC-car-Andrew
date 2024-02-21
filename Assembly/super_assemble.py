#SUPER ASSEMBLY SYNTAX TABLE
#"Super Assembly Word"      "Parameter Type/Format"     "Composition"
#$  thing1                      thing2                      thing3



with open ("super_assemble.py","r") as myself:
    for line in myself:
        if "#$" in line:
            line = line.replace("\n","")
            line = line.replace("#$","")
            line = line.split(" ")
            print(line)

to_assemble = input("super assembly source: ")
with open(to_assemble+".txt","r")as source:
    for line in source:
        line = line.replace("\n","")
        line = line.split("#")[0]
        line = line.split(" ")
        #for token in line: