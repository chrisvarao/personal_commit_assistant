#!/bin/sh
while IFS= read -r line
do
  /git/del_git_user.sh $line
done < "/all_users"
