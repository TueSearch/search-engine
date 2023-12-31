FROM percona/percona-server:8.0.33-25

COPY docker/my.cnf /etc/mysql/my.cnf

COPY docker/mysql.cnf /etc/mysql/conf.d/mysql.cnf

COPY docker/.myrocks.conf $HOME/tuesearch_myrocks.conf

CMD ["mysqld"]