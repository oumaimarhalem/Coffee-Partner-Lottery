import pandas as pd
import csv
import random
import copy
import os
import time
import sys
import colorama

# printing text with a typing effect
def slow_print(text, delay=0.05):    
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

# path to the CSV files with participant data
participants_csv = "Coffee Partner Lottery participants.csv"

# count the number of participants
participants_data = pd.read_csv(participants_csv)
num_participants = len(participants_data)

# header names in the CSV file (name and e-mail of participants)
header_name = "Your name:"
header_email = "Your e-mail:"

# path to TXT file that stores the pairings of this round
new_pairs_txt = "Coffee Partner Lottery new pairs.txt"

# path to CSV file that stores the pairings of this round
new_pairs_csv = "Coffee Partner Lottery new pairs.csv"

# path to CSV file that stores all pairings (to avoid repetition)
all_pairs_csv = "Coffee Partner Lottery all pairs.csv"

# ask user for group size
while True:
    try:
        slow_print("Welcome to Brew Buddies! Let's espresso ourselves and make some frothy new friendships.")
        group_size = int(input("Please enter the desired group size (2 to 5): ")) 
        
        # check if the desired group size is valid
        if 2 <= group_size <= 5:
            
            # check if there are enough participants for the chosen group size
            if num_participants < group_size * 2:
                print(f"Not enough participants. Please choose a smaller group size (up to {num_participants // 2}).")
            
            else:
                break
        else:
            print("Please enter a number between 2 and 5.")
    
    except ValueError:
        print("Invalid input. Please enter a number between 2 and 5.")
        
# init set of old pairs
opairs = set()

DELIMITER=','

# load all previous pairings (to avoid redundancies)
if os.path.exists(all_pairs_csv):
    with open(all_pairs_csv, "r") as file:
        csvreader = csv.reader(file, delimiter=DELIMITER)
        for row in csvreader:
            group = []
            for i in range(0,len(row)):
                group.append(row[i])                        
            opairs.add(tuple(group))

# load participant's data
formdata = pd.read_csv(participants_csv, sep=DELIMITER)

# create duplicate-free list of participants
participants = list(set(formdata[header_email]))

# running set of participants
nparticipants = copy.deepcopy(participants)

# Boolean flag to check if new pairing has been found
new_groups_found = False

# try creating new pairing until successful
while not new_groups_found:   # to do: add a maximum number of tries

    # create a list to store the groups in
    groups = []
    
    # randomly shuffle the list of participants
    random.shuffle(nparticipants)
    
    # distribute the participants into groups
    while len(nparticipants) > 0:
        # if remaining participants are fewer than the desired group size
        # create the final group with whatever participants are remaining
        if len(nparticipants) < group_size:
            groups.append(nparticipants)
            break
        else:
            # otherwise, create a group of the desired group size
            group = nparticipants[:group_size]
            groups.append(group)
            nparticipants = nparticipants[group_size:]

    # check if any new pairings within groups are already in old pairs
    ngroups = set()    
    redundant_pair_found = False
    
    for group in groups:
        # sort the group alphabetically
        group.sort()
        # check every possible pair in the group
        for i in range(len(group)):
            for j in range(i+1, len(group)):
                pair = tuple(sorted([group[i], group[j]]))
                if pair in opairs:
                    redundant_pair_found = True
                    break
            if redundant_pair_found:
                break
        if redundant_pair_found:
            break
        # if no redundant pairs are found, add the group to ngroups
        ngroups.add(tuple(group))
    
    # if no redundant pairs are found, the new groups are good, else reset
    if not redundant_pair_found:
        new_groups_found = True
    else: 
        ngroups = set()
        nparticipants = copy.deepcopy(participants)

# assemble output for printout
output_string = ""

output_string += "------------------------\n"
output_string += "Today's coffee partners:\n"
output_string += "------------------------\n"

for pair in npairs:
    pair = list(pair)
    output_string += "* "
    for i in range(0,len(pair)):
        name_email_pair = f"{formdata[formdata[header_email] == pair[i]].iloc[0][header_name]} ({pair[i]})"
        if i < len(pair)-1:
            output_string += name_email_pair + ", "
        else:
            output_string += name_email_pair + "\n"
    
# write output to console
print(output_string)

# write output into text file for later use
with open(new_pairs_txt, "wb") as file:
    file.write(output_string.encode("utf8"))

# write new pairs into CSV file (for e.g. use in MailMerge)
with open(new_pairs_csv, "w") as file:
    header = ["name1", "email1", "name2", "email2", "name3", "email3"]
    file.write(DELIMITER.join(header) + "\n")
    for pair in npairs:
        pair = list(pair)
        for i in range(0,len(pair)):
            name_email_pair = f"{formdata[formdata[header_email] == pair[i]].iloc[0][header_name]}{DELIMITER} {pair[i]}"
            if i < len(pair)-1:
                file.write(name_email_pair + DELIMITER + " ")
            else:
                file.write(name_email_pair + "\n")
                
# append pairs to history file
if os.path.exists(all_pairs_csv):
    mode = "a"
else:
    mode = "w"

with open(all_pairs_csv, mode) as file:
    for pair in npairs:
        pair = list(pair)
        for i in range(0,len(pair)):
            if i < len(pair)-1:
                file.write(pair[i] + DELIMITER)
            else:
                file.write(pair[i] + "\n")


             
# print finishing message
print()
print("Job done.")
