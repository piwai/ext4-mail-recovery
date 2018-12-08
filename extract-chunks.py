#!/bin/env python3

import os
import sys

HEADER_THRESHOLD = 5000  # 2 matches within 5k of data are likely the same mail
CHUNK_MAX_SIZE = 50 * 1000 * 1000  # Conservative limit of 50 MB per chunk
CHUNK_DIR = "chunks"

if len(sys.argv) < 3:
    print("Usage: extract-chunks.py <audit_file.txt> <raw_image.bin>")
    sys.exit(1)

audit_file = sys.argv[1]
raw_image = sys.argv[2]

if not os.path.exists(CHUNK_DIR):
    os.mkdir(CHUNK_DIR)

with open(audit_file) as fa:
    with open(raw_image, errors='ignore') as fr:
        # Skip foremost headers
        line = fa.readline()
        while not line.startswith("Num"):
            line = fa.readline()
            continue
        # Skip the empty line before offset list
        line = fa.readline()

        # Start processing
        line = fa.readline()
        index_start = 0
        chunk_start = int(line.split()[-1])
        while len(line):
            index, _, _, _, offset = line.split()
            index, offset = int(index.rstrip(':')), int(offset)

            if (offset - chunk_start) < HEADER_THRESHOLD:
                # Probably the same set of mail headers, keep going
                print("Merge #{index} (size {size})".format(index=index, size=offset-chunk_start))
            else:
                # Ok, we got a chunk of reasonable size, extract it in a file
                # Limit chunk size to avoid avoid dumping GBs of useless data
                # if the next offset is very far away in the file
                chunk_end = offset - 1
                chunk_size = min(chunk_end - chunk_start, CHUNK_MAX_SIZE)

                print("Chunk from index #{i}->#{j} ({start} -> {end}), size={s}".format(i=index_start, j=index, start=chunk_start, end=chunk_end, s=(chunk_end - chunk_start)))
                fr.seek(chunk_start)
                chunk = fr.read(chunk_size)
                chunk_name = "{folder}/{start}-{end}.txt".format(folder=CHUNK_DIR, start=chunk_start, end=chunk_end)
                with open(chunk_name, 'a') as fc:
                    fc.write(chunk)
                    fc.close()
                # Reset values for the next chunk
                chunk_start = offset
                index_start = index
            line = fa.readline()
            if line.startswith('Finish'):
                # We've reached the end of the audit file
                break
