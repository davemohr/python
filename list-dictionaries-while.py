#!/usr/bin/env python3.6

#dictionary
user1 = { 'admin': True, 'active':True, 'name':'John' }
user2 = { 'admin': True, 'active':False, 'name':'Paul' }
user3 = { 'admin': False, 'active':True, 'name':'George' }
user4 = { 'admin': True, 'active':False, 'name':'Ringo' }

#list
band_members_list = [user1, user2, user3, user4]
i = 0
while i < len(band_members_list):
	if (band_members_list[i]['active'] == True and band_members_list[i]['admin'] == True):
		prefix = "ACTIVE - (ADMIN) "
		print (f"{prefix} {band_members_list[i]['name']}")
	elif (band_members_list[i]['admin'] == True):
		prefix = "(ADMIN) "
		print (f"{prefix} {band_members_list[i]['name']}")
	elif (band_members_list[i]['active'] == True):
		prefix = "ACTIVE - "
		print (f"{prefix} {band_members_list[i]['name']}")
	i += 1
