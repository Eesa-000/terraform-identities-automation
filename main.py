import re  # this module is used to search for the specific string of the users inside the .tf files
import os  # this module is solely used to create a new directory right now

# Added input for easier debugging purposes

firstname = ""
lastname = ""
engineering = ""
team = ""
employmenttype = ""
office = ""
groups = []


def resetinputs():
    '''resets all the inputs back to blank so the inputs()
    function can handle a new set of inputs by the user'''
    global firstname
    global lastname
    global team
    global engineering
    global office
    global employmenttype
    global groups
    firstname = ""
    lastname = ""
    engineering = ""
    team = ""
    employmenttype = ""
    office = ""
    groups.clear
    inputs()


def inputs():
    '''This handles all the user inputs and assigns them to their respective variables, 
    it also validates the user inputs'''
    global firstname
    global lastname
    global team
    global engineering
    global office
    global employmenttype
    global groups

    while firstname == "":  # This validates the user entry isn't blank, should develop on this so it can refuse if numbers are added etc
        firstname = input("Please enter first name: ")
        firstname = firstname.lower()
        if firstname == "":
            print("Invalid input, please try again: ")

    while lastname == "":
        lastname = input("Please enter last name: ")
        lastname = lastname.lower()
        if lastname == "":
            print("Invalid input, please try again: ")

    while team == "":
        team = input("Please enter a team: ")
        team = team.lower()
        if team == "":
            print("Invalid input, please try again: ")

    # ensures only a y/n entry, specifies engineering to a "true" or "false" string
    while engineering not in ("y", "Y", "n", "N"):
        engineering = input("Are they an engineer? (y/n): ")
        if engineering not in ("y", "Y", "n", "N"):
            print("Invalid input, please try again: ")
        elif engineering in ("Y", "y"):
            engineering = "true"
            break
        elif engineering in ("N", "n"):
            engineering = "false"
            break

    # For now just have fte and intern, may add more later such as external users etc
    while office not in ("cambridge", "london", "bristol", "edinburgh", "croydon"):
        office = input("Please enter an office (london/bristol/cambridge/edinburgh/croydon): ")
        office = office.lower()
        if office not in ("cambridge", "london", "bristol", "edinburgh", "croydon"):
            print("Invalid input, please try again: ")

    # For now just have fte and intern, may add more later such as external users etc
    while employmenttype not in ("fte", "intern", "contractor"):
        employmenttype = input("Please enter an employment type (fte/intern/contractor): ")
        employmenttype = employmenttype.lower()
        if employmenttype not in ("fte", "intern", "contractor"):
            print("Invalid input, please try again: ")

    userinp = ""
    while userinp != "#":  # keeps adding users to groups until a "#" character is input, may want to import a list of groups from FreeIPA and validate against that
        userinp = input("Please type a group to add the user to (type '#' when you are done): ")
        userinp = userinp.lower()
        # if userinp in ("")
        # use the above line to validate against FreeIPA list
        if userinp == "#":
            break
        # should add validation so no duplicate entries are added
        if userinp not in ("#", ""):
            groups.append(userinp)
    firstname = firstname.lower()
    lastname = lastname.lower()
    createlist()


def createlist():
    '''This collates a list of all the current users for the file and adds on our newly
    specified one, it then orders the list alphabetically'''
    if employmenttype == "fte" or employmenttype == "contractor":
        print("fiveaidone ######")  # DEBUG ##################################
        fileo = "identities/fiveai.tf"
    elif employmenttype == "intern":
        # DEBUG ##################################
        print("interns done ###########")
        fileo = "identities/interns.tf"
    # this opens the file specified, in this case the terraform file that uses interns/fiveai staff
    tffile = open(fileo, mode="r+")
    contents = tffile.read()  # reads the contents of the file
    # this finds all the 'name' strings
    matches = re.findall(r"module \"(.+?)\" {", contents)
    print(matches)
    sortedmatches = sorted(matches)
    try:  # this is because if you attempt to remove 'aws groups' from the intern list, it throws an error
        sortedmatches.remove("aws_groups")
    except ValueError:
        pass
    fullname = str(firstname+"_"+lastname).lower()
    if fullname in matches:
        alreadyexists(fullname)
        
    sortedmatches.append(fullname)
    sortedmatches.sort()
    index = sortedmatches.index(fullname)
    print(sortedmatches)
    print("  first_name      = "+firstname+"\n  last_name       = "+lastname+"\n  team            = "+team+"\n  employment_type = "+employmenttype+"\n  engineering     = "+engineering+"\n  office          = "+office+"\n  groups          = "+str(groups).replace("'", '"'))
    confirm = ""  # above confirms user entry, below makes sure they want to continue with the entry

    while confirm not in ("y", "Y", "n", "N"):  # ensures only a y/n entry
        confirm = input("\nIs the above information correct? (y/n): ")
        if confirm not in ("y", "Y", "n", "N"):
            print("Invalid input, please try again: ")
        elif confirm in ("Y", "y"):
            apply(index, sortedmatches, fileo)
        elif confirm in ("N", "n"):
            resetinputs()


# using a different module for fte, interns, external etc, probably should change this
def apply(index, sortedmatches, fileo):
    '''Corralates the name before the name we want to add 
    and decides which line number to input the string into'''
    lookup = sortedmatches[index-1]  # sets the pointer to the previous entry
    print(fileo)
    if index < 1:  # if lookup is less than 1, there are no previous entries and we need to set it to the first entry
        if fileo == "identities/fiveai.tf":
            num = 57  # IF ANY LINES INSERTED/REMOVED ABOVE, CHANGE THIS!!!!
        elif fileo == "identities/interns.tf":
            num = 0  # same applies ^^

    else:
        if fileo == "identities/fiveai.tf":
            with open(fileo) as myFile:
                lines_after_55 = myFile.readlines()[55:]
                # looks for the line where the previous entry is, CHANGE IF LINES ABOVE USERS CHANGE!!!
                for num, line in enumerate(lines_after_55, 1):
                    if lookup in line:
                        num = num+57  # 55 is how many lines from where we read, 2 is how many lines after the space is, this is where we add the new entry
                        break

        elif fileo == "identities/interns.tf":
            print("interns.tf")
            with open(fileo) as myFile:
                internfile = myFile.readlines()
                # looks for the line where the previous entry is, CHANGE IF LINES ABOVE USERS CHANGE!!!
                for num, line in enumerate(internfile, 1):
                    if lookup in line:
                        num = int(num)
                        print(num)
                        break

    with open(fileo, 'r') as file:
        lines = file.readlines()  # creates an array of lines

    if fileo == "identities/fiveai.tf":
        if len(lines) > int(num):  # uses the 'num' variable to see where to insert the new data
            # this directly edits the fiveai.tf file
            lines.insert(num, "\nmodule \""+firstname+"_"+lastname+"\" {\n  source = \"fiveai/"+firstname+"."+lastname+"\"\n}\n")
        else:
            lines.append("\nmodule \""+firstname+"_"+lastname+"\" {\n  source = \"fiveai/"+firstname+"."+lastname+"\"\n}\n")
        try:
            os.mkdir("identities/fiveai/"+firstname+"."+lastname)
        except FileExistsError:
            print("File already exists!")
        maintfcreate = open("identities/fiveai/"+firstname+"."+lastname+"/main.tf", "w+")
        maintfcreate.write("module \"freeipa_user\" { \n  source = \"../../../onprem/modules/freeipa_user\"\n  first_name      = \""+firstname+"\"\n  last_name       = \""+lastname+"\"\n  team            = \""+team+"\"\n  employment_type = \""+employmenttype+"\"\n  engineering     = \""+engineering+"\"\n  office          = \""+office+"\"\n  groups          = "+str(groups).replace("'", '"')+"\n}\n")

    elif fileo == "identities/interns.tf":
        print(len(lines))  # DEBUG ##################################
        print(num) # DEBUG ##################################
        if num == 0:  # if the person precedes all current people, this just adds a line to the top so there is room for another 'module' to be added
            print("WARNING ################")
            i = len(lines)
            lines.append("}")
            while i > 0:
                lines[i] = lines[i-1]
                i = i - 1
            # this directly edits the interns.tf file
            lines[0] = "module \""+firstname+"_"+lastname + \
                "\" {\n  source = \"interns/" + \
                firstname+"."+lastname+"\"\n}\n"+"\n"

        elif len(lines) > int(num):  # uses the 'num' variable to see where to insert the new data
            print("111111111111111111111111111111111")  # DEBUG ##################################
            # this directly edits the interns.tf file
            lines.insert(num, "\nmodule \""+firstname+"_"+lastname+"\" {\n  source = \"interns/"+firstname+"."+lastname+"\"\n}\n")
        else:
            print("2222222222222222222222222222222222222222222222")  # DEBUG ##################################
            lines.append("\nmodule \""+firstname+"_"+lastname+"\" {\n  source = \"interns/"+firstname+"."+lastname+"\"\n}\n")
        try:
            # creates the new user directory
            os.mkdir("identities/interns/"+firstname+"."+lastname)
        except FileExistsError:
            print("File already exists!")
        maintfcreate = open("identities/interns/"+firstname+"."+lastname+"/main.tf", "w+")
        maintfcreate.write("module \"freeipa_user\" { \n  source = \"../../../onprem/modules/freeipa_user\"\n  first_name      = \""+firstname+"\"\n  last_name       = \""+lastname+"\"\n  team            = \"" +team+"\"\n  employment_type = \""+employmenttype+"\"\n  engineering     = \""+engineering+"\"\n  office          = \""+office+"\"\n  groups          = "+str(groups).replace("'", '"')+"\n}\n")
    print("number =", num) 
    writefiles(lines, fileo)


def writefiles(lines, fileo):
    '''this writes the the specified file
    made this function as I was boiling the issue down to the .writelines function
    '''
    fileopen = open(fileo, 'w')
    print(lines) # DEBUG ##################################
    print(fileo) #From what I can see, the print(lines) function returns the desired output, so why doesn't .writelines(lines) actually perform as expected for interns.tf?
    print(fileopen) # DEBUG ##################################
    fileopen.writelines(lines)
    fileopen.close
    print("Added "+firstname+" "+lastname+" as "+employmenttype+" in "+team+".")
    start()


def alreadyexists(fullname):
    '''throws an error and breaks program 
    if user already exists in file, 
    one point of failure covered'''
    print("User already exists! Please manually add")
    start()


def start():
    '''start of program, just confirms that the user would
    like to perform the function of this program, could potentially
    expand further on to include what function the user want's to perform'''
    addinguser = ""
    while addinguser not in ("Y", "y", "N", "n "):
        addinguser = input("Would you like to add a user? (y/n): ")
        if addinguser in ("y", "Y"):
            resetinputs()
        elif addinguser in ("n", "N"):
            exit()


start()


#print(firstname, lastname, team, employmenttype, groups)
#print("module \"freeipa_user\" { \n  source = \"../../../onprem/modules/freeipa_user\"\n  first_name      = "+firstname+"\n  last_name       = "+lastname+"\n  team            = "+team+"\n  employment_type = "+employmenttype+"\n  engineering     = "+engineering+"\n  office          = "+office+"\n  groups          = "+str(groups)+"\n}")
#print("\nmodule \""+firstname+"_"+lastname+"\" {\n  source = \"fiveai/."+firstname+"_"+lastname+"\" \n}\n")
