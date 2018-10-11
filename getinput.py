#!/usr/bin/env python3.6
import os 
#import time #this imports the entire package, which is inefficient

from time import localtime, strftime #this is more efficient, we import only the parts of the standard library we will use

#now = time.localtime() #this is how you call it when you import time
now = localtime() #but since we imported the localtime part already, we can just call it this way now

print(f"\n{__file__} started at {strftime('%X', now)}") #the print(f... thing only works in python 3


path_found = os.getenv("PATH")
print(f"The system PATH is {path_found}")


def gather_info():
	cluster_name = str(input("\nName for the cluster? ").strip())
	while True:
		try:
			num_masters = int(input("\nNumber of master nodes? "))
			break
		except ValueError:
			print("Error: Invalid number")
	
	while True:
		try:
			size_masters = str(input("\nPlease specify the  master nodes instance size \n[1] t2.large\n[2] t2.xlarge  \nRespond with the number corresponding to the option you want [1/2] ").strip())
			if size_masters == "1":
				size_masters = "t2.large"
				break
			elif size_masters == "2":
				size_masters = "t2.xlarge"
				break
			else:
				print("Error: you must enter 1 or 2 as the response.")
		except ValueError:
			print("Error.")


	num_workers = int(input("\nNumber of worker nodes? "))
	
	while True:
		try:
			size_workers = str(input("\nPlease specify the worker nodes instance size \n[1] t2.large\n[2] t2.xlarge  \nRespond with the number corresponding to the option you want [1/2] ").strip())
			if size_workers == "1":
				size_workers = "t2.large"
				break
			elif size_workers == "2":
				size_workers = "t2.xlarge"
				break
			else:
				print("Error: you must enter 1 or 2 as the response.")
		except ValueError:
			print("Error.")
	
	
	return (cluster_name, num_masters, size_masters, num_workers, size_workers)

while True:
	cluster_name, num_masters, size_masters, num_workers, size_workers = gather_info()
	break

print()
print("--------------------------------------------")
print(f"Your cluster will be named {cluster_name}.")
print(f"It will have {num_masters} masters of size {size_masters}.")
print(f"It will have {num_workers} worker nodes of size {size_workers}.")
now = localtime()
print(f"\n{__file__} finished at {strftime('%X', now)}")
print("--------------------------------------------")
