#!/bin/env python3

import email

import os
import sys

EMAIL_DIR = "emails"

if len(sys.argv) < 3:
    print("Usage: filter.py <chunk_dir> <recipent_address>")
    sys.exit(1)

chunk_dir = sys.argv[1]
recipient = sys.argv[2]

if not os.path.exists(EMAIL_DIR):
    os.mkdir(EMAIL_DIR)

for filename in os.listdir(chunk_dir):
    filepath = os.path.join(chunk_dir, filename)
    dest_path = os.path.join(EMAIL_DIR, filename)
    with open(filepath, 'rb') as fp:
        msg = email.message_from_binary_file(fp)
    if (msg['To'] and recipient in msg['To']) or\
       (msg['Delivered-To'] and recipient in msg['Delivered-To']):
        print("File: {fname}".format(fname=filename))
        print("From:", msg['From'])
        print("To:", msg['To'])
        print("Subject:", msg['Subject'])
        print("Spam:", msg['X-Spam-Status'])
        os.rename(filepath, dest_path)
    else:
        print("skip {fname} (to {to})".format(fname=filename, to=msg['To']))




