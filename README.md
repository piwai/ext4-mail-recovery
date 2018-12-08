Mail recovery Tutorial
======================

This repository describes my (desperate) attempt to try to recover deleted emails, in the hope that it can help somebody else.

Note: Don't use this if you're using Microsoft Outlook or another mail agent which uses a global binary file per folder (.pst for Outlook). There are dedicated tools for that.

Here we will try to recover text files on a linux server with an ext4 partition. The files were emails stored in an IMAP folder, and have been deleted by mistake.
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

To encode the header in Hex format used by foremost, use the code below:

```
$ python3 -q
>>> header = "Received:"
>>> print(''.join(str(hex(ord(c))) for c in header).replace('0x','\\x'))
\x52\x65\x63\x65\x69\x76\x65\x64\x3a
```

Then put this result into a foremost.conf file, like this:
```
$ echo "txt n 1000 \x52\x65\x63\x65\x69\x76\x65\x64\x3a" > foremost.conf
```
You may also use the foremost.conf from this repository.

Step 2: Run foremost to get the potential location of files
===========================================================

Now that we have set our custom config to locate emails, we can run foremost to tell us at which offset it saw the signature.
On Debian-based systems, foremost can be installed with:

```
$ sudo apt-get install foremost
```
If it's not available for your distribution, you may need to compile it from source.

Once installed, use the following command to run it:

```
$ foremost -w -c ./foremost.conf -i disk.img
```
 * -w is "dry-run" mode, it means don't try to extact the data, just locate the header.
 * -c tells to use the config in the current folder
 * -i means use "disk.img" as the raw image extracted by "dd" to look for deleted mails.

Depending on the image size, this might take several hours to complete.
When it's done, you should get a file named "audit.txt" in a "output" folder.
There is a "audit.txt.sample" in the repo so you can see what it looks like. It's a sample,
in my case the full file was nearly 45MB with almost 900k matches.

Step 3: Extract file chunks based on audit.txt file
===================================================

