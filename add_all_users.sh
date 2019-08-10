#!/bin/sh
while IFS= read -r line
do
  /git/add_git_user.sh $line "`cat /keygen/${line}.pub`"
done < "/all_users"
