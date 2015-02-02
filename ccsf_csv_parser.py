#!/usr/bin/env python

"""
    Program to convert City College of San Francisco class roster to CSV format with only pertinent data.
    Copyright (C) 2015 Alycia Kaplan

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

import csv
import sys
import re

def main():
	filein = raw_input('Enter the file name : ')
	#filenames = get_file_names()
	#for filename in filenames:
	parse_input_file_to_csv(filein)

def parse_input_file_to_csv(filein=None):
	"""parse_input_file_to_csv takes a file name (of a class roster file)
	and converts that file to CSV. If the filename is, for instance, example.txt,
	then the output CSV file will be named example.csv
	"""
	Data, Header, fileout = parse_raw_input(filename=filein)
	fileout = fileout.split(".txt")[0] + ".csv"
	write_csv(Data=Data, Header=Header, filename=fileout)
	print "Successfully wrote %s" % fileout

def write_csv(Data=None, Header=None, filename=None):
	"""write_csv forces data into an acceptable format for the csv library's write functions
	"""
	with open(filename, 'wb') as f:
		writer = csv.DictWriter(f, fieldnames=Header)
		writer.writeheader()
		sample = Data["ID"]
		for i in range(len(sample)):
			tmp = dict()
			for k in Data.keys():
				tmp[k] = Data[k][i]
			writer.writerow(tmp)


def parse_raw_input(filename=None):
	"""parse_raw_input parses the file based on a known/desired ordering scheme in the Header.
	Function gets course information and iterates over respective "user blocks"
	until the associated users are exhausted, and reiterates until fin.
	RE is used as necessary as a means of extraction (or to simplify extraction) of certain data. 
	"""
	Header = ["CRN", "TERM", "SUBJ", "CRSE", "SEC", "Title", "CREDITS", "Seq.", "Student Name", "PHONE NUMBER", "E-MAIL",
		"ID", "Levl", "Majr", "Cl", "Hrs", "MGrd", "FGrd", "Stat", "Date"] #orders the csv output
	Data = dict(zip(Header, [[] for i in range(len(Header))])) #creates the dictionary of dreams
	read_next_line = False
	in_user_block = False
	is_first_user = False
	ukey_matcher = re.compile("^[0-9]{2}   [A-Z]")
	email_matcher = re.compile("[\w.-]+@([\w.-]+)")
	with open(filename, "r") as f:
		for line in f:
			line = line.strip()
			#Reuse the keys and fields lists for every ukey/ufield list below until a new key/field list in file
			if line.find("CRN")>-1 and line.find("CRSE")>-1:
				read_next_line = True
				keys = line.split(" ")
				keys = [s for s in keys if s]
				keys = keys[0:-2] #removes Cl Level(s)
				keys.append("Title")
				continue
			if read_next_line:
				fields = line.split(" ")
				fields = [s for s in fields if s] #list comprehension to remove empty list elements
				fields = fields[0:-1] #removes Cl Level(s) entry
				title = fields[5:-1]
				for i in range(len(title)):
					fields.pop(5)
				fields.append(' '.join(title))
				assert len(keys)==len(fields), "Keys and fields unequal."
				for i, key in enumerate(keys):
					Data[key].append(fields[i]) #fills the dictionary
				read_next_line = False
				continue
			if line.find("Seq.")>-1 and line.find("MGrd")>-1:
				is_first_user = True
				ukeys = line.split(" ")
				ukeys = [s for s in ukeys if s]
				ukeys = ukeys[0:-2] #removes Last Attend entry
				student_name = ukeys[1:3] #combines Student Name fields
				ukeys.pop(1)
				ukeys[1] = ' '.join(student_name)
				continue
			if ukey_matcher.match(line):
				in_user_block, have_phone, have_email = True, False, False
				if not is_first_user:
					for i, key in enumerate(keys):
						Data[key].append(fields[i]) #fills the dictionary
				ufields = line.split(" ")
				ufields = [s for s in ufields if s]
				student_name = ufields[1:-9] #combines Student Name entries
				for i in range(len(student_name)-1):
					ufields.pop(1)
				ufields[1] = ' '.join(student_name)
				assert len(ukeys)==len(ufields), "User keys and user fields unequal. key: %s, field: %s" % (len(ukeys), len(ufields))
				for i, ukey in enumerate(ukeys):
					Data[ukey].append(ufields[i]) #fills the dictionary
				email = "No valid e-mail" #creates a default field for e-mail per user
				Data["E-MAIL"].append(email)
				continue
			if in_user_block and not have_phone:
				have_phone = True
				phone = line.strip()
				Data["PHONE NUMBER"].append(phone) #adds phone number to the dictionary
				continue
			if in_user_block and not have_email and email_matcher.search(line):
				have_email = True
				email = line.strip() #if finds e-mail within a user block, rewrites over default empty field
				Data["E-MAIL"][-1] = email #adds e-mail to the dictionary
				is_first_user = False
				continue
	return Data, Header, filename

if __name__ == '__main__':
	main()
