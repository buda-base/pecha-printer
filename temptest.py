import tempfile
import os
import glob
import shutil

# create a temporary directory using the context manager
# with tempfile.TemporaryDirectory() as tmpdirname:

#     f = open(os.path.join(tmpdirname, "guru99.txt"), "w+")

#     print('created temporary directory', tmpdirname)

# directory and contents have been removed

def addfiles(dir):
    f = open(os.path.join(dir, "guru99.txt"), "w+")

def printfiles(dir):
    files = os.listdir(dir)
    for f in files:
        print(f)

def delfiles(dir):
    files = os.listdir(dir)
    for f in files:
        fpath = os.path.join(dir, f)
        os.remove(fpath)


with tempfile.TemporaryDirectory() as tmpdirname:
    print('created temporary directory', tmpdirname)

    addfiles(tmpdirname)
    printfiles(tmpdirname)
    delfiles(tmpdirname)

    print('emptied temporary directory', tmpdirname)






