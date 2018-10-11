#!/usr/bin/env python3.6

#file_object  = open(“filename”, “mode”)

#read in an existing file
#my_file = open('file.txt', 'r' ) #r is for read-only. there is also a for append or w for write.
#print(my_file.read()) #this prints it out to the console

#write a file
print("Creating testfile.txt (opening it in write mode)...")
file = open("testfile.txt","w+") 
 
file.write("Hello World, ") 
file.write("this is a new text file.") 
file.write("\nAnd this is another line.\n") 
file.close() 
print("Wrote three lines to it, then closed it.")

import time
time.sleep(2) #make sure the file closed before trying to read it

print("Now copying testfile.txt as testfile2.txt")
#now let's copy testfile.txt contents into a new testfile2.txt file
from shutil import copyfile
#copyfile(src, dst)
copyfile('testfile.txt', 'testfile2.txt')

print("Now authoring new testfile3.txt in write mode, reading testfile2.txt into it, and closing both")
#here's another way to copy by creating a new empty file and reading file contents in
f3 = open('testfile3.txt', 'w')
source_file = open("testfile.txt","r")
f3.write(source_file.read())
source_file.close()
f3.close()

#now let's append a new line to an existing file
print("Now opening testfile3.txt in append mode and writing a new line to the end of it")
time.sleep(3)
f3 = open('testfile3.txt', 'a') #open it in append mode
with f3:
	f3.write('new line added')
f3.close()
