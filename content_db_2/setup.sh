#!/bin/bash 

sleep 5

echo $POSTGRES_USER
echo $POSTGRES_DB

if [[ $INIT_DB -eq 1 ]]
then
    echo "Setting up schema..."
    psql -U $POSTGRES_USER -d $POSTGRES_DB -f /home/schema.sql
fi

sleep 1

if [[ $INIT_DATA -eq 1 ]]
then
    echo "Inserting data..."
    psql -U $POSTGRES_USER -d $POSTGRES_DB -f /home/data.sql
fi
