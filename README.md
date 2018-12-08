Mail recovery Tutorial
======================

This repository describes my (desperate) attempt to try to recover deleted emails on my personnal server.
The emails were text files in an IMAP folder.
Details are here: https://serverfault.com/questions/942480/recovering-deleted-plain-text-emails-files-from-raw-disk-image

I will assume that you've already did what I did first:

 * Dump the whole server partition using "dd" and transfer it elsewhere
 * Try recovery tools on the dd image (ext4undelete, ext4magic)
 * Find that the tools don't see anything to restore.

I will also assume that you have basic Python knowledge to make the scripts and snippets work.


Step 0: Do a proper backup
==========================

If you're reading this, chances are that, just like me, you didn't have a working backup of your data. So, stop reading this, and do a backup of your other data. Now.


You're back? OK, let's continue.


Step 1: Configure foremost to locate emails
===========================================

Foremost (http://foremost.sourceforge.net/) is a data recovery tool.
Its purpose is to recover binary data like pictures, videos, compressed archives which were deleted from a hard drive... Theses files generally have a specific signature in their header, and they also include their own size in their metadata, so they are easier to restore. In my case, the mails were just plain text, with SMTP headers, body and base64 attachments.

So we will use foremost only to locate where the emails are on the partition, and we will delegate the extraction to a custom Python script, which will be able to extract just the correct amount of data.

To do this, you will need to define a specific signature with a SMTP header encoded in hex, so that foremost can look for this in the partition and tell you at which offset it saw the signature. The header is "Received:", which is a fairly common header that each MTA adds to the email when routing it.

To encode it, use the code below:

```
$ python3 -q
>>> header = "Received:"
>>> print(''.join(str(hex(ord(c))) for c in header).replace('0x','\\x'))
\x52\x65\x63\x65\x69\x76\x65\x64\x3a
```

Then put this result into foremost.conf file, like this:
```
txt n 1000 \x52\x65\x63\x65\x69\x76\x65\x64\x3a
```
