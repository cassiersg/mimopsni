#! /bin/sh

git ls-tree -r master --name-only | xargs sed -i -E -e "s/(G|g)a(ë|e)tan/FirstName/" -e "s/(C|c)assiers/LastName/"
git ls-tree -r master --name-only | zip -@ tool.zip

