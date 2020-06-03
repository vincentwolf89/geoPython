import os
dirName = r'C:\Users\vince\Desktop\Cucina del Lupo'
file = r'C:\Users\vince\Desktop\output.txt'

def getListOfFiles(dirName):
    # create a list of file and sub directories
    # names in the given directory
    listOfFile = os.listdir(dirName)
    allFiles = list()
    # Iterate over all the entries
    for entry in listOfFile:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        # If entry is a directory then get the list of files in this directory
        if os.path.isdir(fullPath):
            allFiles = allFiles + getListOfFiles(fullPath)
        else:
            allFiles.append(fullPath)

    return allFiles

# Get the list of all files in directory tree at given path
listOfFiles = getListOfFiles(dirName)

# Print the files
for elem in listOfFiles:
    print(elem)

print ("****************")

# Print the files
with open(file, 'w') as f:
    for item in listOfFiles:
        f.write("%s\n" % item)

f.close()