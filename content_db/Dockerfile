FROM postgres:10.6

COPY *.sql /home/

#COPY ./database.sql /docker-entrypoint-initdb.d
COPY ./setup.sh /docker-entrypoint-initdb.d

