#!/bin/sh
while IFS= read -r line
do
  ssh-keygen -q -t rsa -b 4096 -N '' -C "$line@example.com" -f "/keys/$line"
done < "/all_users"
