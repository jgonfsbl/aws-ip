# -*- coding: utf-8 -*-
# pylint: disable=locally-disabled, multiple-statements, too-few-public-methods
# pylint: disable=fixme, line-too-long, invalid-name
# pylint: disable=W0703

"""
A microservice to capture, store and supervise AWS IPs
"""

__author__ = '@EA1HET'
__date__ = "2019-07-09"
__version__ = "1.0"

from environs import Env
from pymysql import connect, err
from requests import get


#
# 1. Load the environment variable
#
try:
    ENVIR = Env()
    ENVIR.read_env()
    DB_HOST = ENVIR('DB_HOST')
    DB_USER = ENVIR('DB_USER')
    DB_PASS = ENVIR('DB_PASS')
    DB_TABL = ENVIR('DB_TABL')
except Exception as e:
    print('Error: $s' % e)
    exit(code=1)


#
# 2. Variable definition
#
URL = 'https://ip-ranges.amazonaws.com/ip-ranges.json'
SQL = 'insert into `ip` (`aws-token`, `date-creation`, `ip-prefix`, `region`, `service`) ' \
      'values (%s, %s, %s, %s, %s)'


#
# 3. Obtain the JSON from AWS site
#
r = get(URL)
j = r.json()


#
# 4. Establish the database connection to MariaDB
#
conn = connect(DB_HOST, DB_USER, DB_PASS, DB_TABL)


#
# 5. Get a cursor from the database
#
try:
    print('Connection to database successful')
    with conn:
        cur = conn.cursor()

        for each in j['prefixes']:
            VAL = [j['syncToken'], j['createDate'],
                   each['ip_prefix'], each['region'], each['service']]
            res = cur.execute(SQL, VAL)
            conn.commit()

except err.DatabaseError as conerr:
    print('DB connection failed: %s' % conerr)
except KeyboardInterrupt:
    print('User stopped program')
except Exception as e:
    print('DB Error: %s' % e)
finally:
    conn.close()
    print('Task done')
