import pandas as pd
import csv
import random
import copy
#import os2
import time
import sys
import colorama
import requests
from googleapiclient import discovery
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import client, file, tools
import json

from google.oauth2.credentials import Credentials

from email.mime.text import MIMEText
import base64


def get_conversation_starter():
    url = "https://official-joke-api.appspot.com/random_joke"
    response = requests.get(url)
    joke = response.json()
    return f"{joke['setup']} {joke['punchline']}"


def save_message_to_file(group, message, filename="coffee_groups_messages.txt"):
    with open(filename, "a") as file:
        file.write(f"Group: {', '.join(group)}\n")
        file.write(f"Message: {message}\n\n")
    


# printing text with a typing effect
def slow_print(text, delay=0.05):    
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()




slow_print("If you want to fill out the sign up forms, please do at:")
slow_print("https://docs.google.com/forms/d/e/1FAIpQLSfCiLAIa-3Ssd_ewvwe0FpeLdz75fYGwhlwtJH3ydAnesk2cQ/viewform")

"""
All code for google forms is from google developers pages. I did not wrote it.
"""


SCOPES = [
    "https://www.googleapis.com/auth/forms.responses.readonly",
    "https://www.googleapis.com/auth/gmail.send"  # For sending emails
    ]

DISCOVERY_DOC = "https://forms.googleapis.com/$discovery/rest?version=v1"

store = file.Storage("token.json")
creds = None
if not creds or creds.invalid:
  flow = client.flow_from_clientsecrets("creden.json", SCOPES)
  creds = tools.run_flow(flow, store)

service = discovery.build(
    "forms",
    "v1",
    http=creds.authorize(Http()),
    discoveryServiceUrl=DISCOVERY_DOC,
    static_discovery=False,
    )


# Using Gmail API
def send_email_via_gmail(group, message, subject="Coffee Group Notification"):
    service = build("gmail", "v1", credentials=creds)

    sender_email = "Brewbuddies3@gmail.com"
    
    # Converting a list of names to a list of mailboxes
    recipient_emails = [emails[name] for name in group if name in emails]

    if not recipient_emails:
        print("⚠️ No valid emails found for the given group.")
        return
    
    # email content
    mime_message = MIMEText(message, "plain", "utf-8")
    mime_message["to"] = ", ".join(recipient_emails)
    mime_message["subject"] = subject
    mime_message["from"] = sender_email

    try:
        raw_message = mime_message.as_string()
        raw_message_base64 = base64.urlsafe_b64encode(raw_message.encode("utf-8")).decode("utf-8")
        message_body = {"raw": raw_message_base64}
        message = service.users().messages().send(userId="me", body=message_body).execute()
        print(f"✅ Successfully emailed to: {', '.join(group)}")
    except Exception as e:
        print(f"⚠️ Error: {e}")



# Prints the responses of your specified form:
form_id = "1eVElX0Ci_jFXhPhmety9IeySqea_B63JYceqm62MN70"
result = service.forms().responses().list(formId=form_id).execute()
#print(result)

AnswerData = []

for response in result["responses"]:
    answers = response["answers"]
    
    Name = next(iter(answers.get("4d9aecd4", {}).get("textAnswers", {}).get("answers", [{}])), {}).get("value", "")
    Email = next(iter(answers.get("72137182", {}).get("textAnswers", {}).get("answers", [{}])), {}).get("value", "")
    print(Name,Email)
    if Name and Email:  # Ensure both name and email exist
        AnswerData.append({"name": Name, "email": Email})

# Print extracted names and emails as JSON
#print(AnswerData)

num_participants=len(AnswerData)
#print(num_participants)
# ask user for group size
while True:
    try:
        slow_print(colorama.Fore.GREEN + "Welcome to Brew Buddies! Let's espresso ourselves and make some frothy new friendships." + colorama.Fore.RESET)
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


'''
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
'''


# create duplicate-free list of participants

participants=[]
emails={}
for i in range(len(AnswerData)):
    participants.append((AnswerData[i]['name']))
    emails.update({(AnswerData[i]['name']):(AnswerData[i]['email'])})

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
slow_print(colorama.Fore.YELLOW + "The groups have been generated! \n")
slow_print(colorama.Fore.YELLOW + "Who will you roast and toast with today? \n")

slow_print(colorama.Fore.CYAN +"------------------------\n")
slow_print(colorama.Fore.CYAN +"Today's Brew Buddies:\n")
slow_print(colorama.Fore.CYAN + "------------------------\n")

for i, group in enumerate(ngroups, start=1):
    message = ""
    message += f"Group {i}:"
      
    for participant in group:
        name = participant
        email = emails[name]
        conversation_starter = get_conversation_starter()
        2
        message += f"     {name:<25}: | {email}\n"
    
    message += f"\nConversation Starter:\n {conversation_starter}"
    message += "" # blank line for spacing between groups
    
    save_message_to_file(group, message, "coffee_groups_messages.txt")
    send_email_via_gmail(group, message)  # Send emails automatically
    slow_print(colorama.Fore.CYAN + message)
    
slow_print(colorama.Fore.CYAN + "Enjoy your coffee and great conversations! You're on the perfect blend for connection \n")
    


             
# print finishing message
print()
print("Job done.")
