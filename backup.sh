#!/bin/bash

echo $(date)
# tar chokes on spaces and colons.
name=$(date | sed 's/\ /_/g' | sed 's/:/_/g')
cd /data/dbbackup
pg_dumpall > pg_$name.sql && tar -czf pg_$name.tar.gz pg_$name.sql && rm -r pg_$name.sql
echo "removing old files..."
find /data/dbbackup/ -mtime +2 -exec echo {} \;
find /data/dbbackup/ -mtime +2 -exec rm -r {} \;
echo $(date)
