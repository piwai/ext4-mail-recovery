#!/bin/env python3

import email

import os
import sys

DUP_DIR = "duplicates"

if len(sys.argv) < 2:
    print("Usage: filter.py email_dir")
    sys.exit(1)

mail_dir = sys.argv[1]

message_ids = {}

if not os.path.exists(DUP_DIR):
    os.mkdir(DUP_DIR)

for filename in os.listdir(mail_dir):
    filepath = os.path.join(mail_dir, filename)
    dest_path = os.path.join(DUP_DIR, filename)
    with open(filepath, 'rb') as fp:
        msg = email.message_from_binary_file(fp)
        msg_id = msg["Message-Id"]
        if msg_id in message_ids.keys():
            print("Duplicate: {name1} -> {name2}".format(name1=filename, name2=message_ids[msg_id]))
            os.rename(filepath, dest_path)
        else:
            message_ids[msg_id] = filepath

