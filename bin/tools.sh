#!/bin/bash
brew install cmake node npm redis hiredis unixodbc
export SLUGIFY_USES_TEXT_UNIDECODE=yes
pip3 install monthdelta asyncpg py-postgresql sqlalchemy sklearn psycopg2-binary fastai tensorflow keras pandas statsmodels networkx pystan apache-airflow apache-airflow[postgres]
npm install -g node-gyp
#apt-get install libhiredis-dev
