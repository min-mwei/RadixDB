import os
from pathlib import Path
import radixdb
import subprocess
import os, signal, time

def check_kill_process(pstring):
    for line in os.popen("ps ax | grep " + pstring + " | grep -v grep"):
        fields = line.split()
        pid = fields[0]
        os.kill(int(pid), signal.SIGKILL)

def get_stored_procedure():
    return str(Path(os.path.join(radixdb.__path__[0], "sql/setup.sql")))

def setup_localdb():
    args = ['pg_ctl', '-D', 'radixdb', 'stop']
    subprocess.run(args)

    args = ['pg_ctl', '-D', 'radixdbw1', 'stop']
    subprocess.run(args)

    args = ['pg_ctl', '-D', 'radixdbw2', 'stop']
    subprocess.run(args)

    time.sleep(1)
    check_kill_process('postgres')
    
    time.sleep(1)
    args = ['rm', '-rf', os.path.abspath('radixdb')]
    subprocess.run(args)
    args = ['rm', '-rf', os.path.abspath('radixdbw1')]
    subprocess.run(args)
    args = ['rm', '-rf', os.path.abspath('radixdbw2')]
    subprocess.run(args)

    args = ['initdb', '-D', 'radixdb', '-U' 'postgres']
    subprocess.run(args)
    
    args = ['pg_ctl', '-D', 'radixdb', '-l', 'logfile', 'start']
    subprocess.run(args)

    args = ['psql', '-X', '-U', 'postgres', '-c', 'create database radixdb']
    subprocess.run(args)

    args = ['pg_ctl', '-D', 'radixdb', '-l', 'logfile', 'stop']
    subprocess.run(args)

    args = ['initdb', '-D', 'radixdbw1', '-U' 'postgres']
    subprocess.run(args)
    args = ['pg_ctl', '-D', 'radixdbw1', '-l', 'logfile-w1', 'start']
    subprocess.run(args)
    args = ['psql', '-X', '-U', 'postgres', '-c', 'create database radixdb']
    subprocess.run(args)
    args = ['pg_ctl', '-D', 'radixdbw1', '-l', 'logfile-w1', 'stop']
    subprocess.run(args)

    args = ['initdb', '-D', 'radixdbw2', '-U' 'postgres']
    subprocess.run(args)
    args = ['pg_ctl', '-D', 'radixdbw2', '-l', 'logfile-w2', 'start']
    subprocess.run(args)
    args = ['psql', '-X', '-U', 'postgres', '-c', 'create database radixdb']
    subprocess.run(args)
    args = ['pg_ctl', '-D', 'radixdbw2', '-l', 'logfile-w2', 'stop']
    subprocess.run(args)

    with open('./radixdb/postgresql.conf','a')  as f:
        f.write('\n' + "shared_preload_libraries = 'citus,pg_cron,hll,topn,pg_stat_statements'")
        f.write('\n' + "cron.database_name = 'radixdb'")
        f.write('\n' + "pg_trgm.similarity_threshold = 0.1")
        f.write('\n' + "pg_trgm.word_similarity_threshold = 0.1")
        f.write('\n' + "pg_trgm.strict_word_similarity_threshold = 0.2")

    with open('./radixdbw1/postgresql.conf','a')  as f:
        f.write('\n' + "port = 5433")
        f.write('\n' + "shared_preload_libraries = 'citus,hll,topn,pg_stat_statements'")
        f.write('\n' + "pg_trgm.similarity_threshold = 0.1")
        f.write('\n' + "pg_trgm.word_similarity_threshold = 0.1")
        f.write('\n' + "pg_trgm.strict_word_similarity_threshold = 0.2")

    with open('./radixdbw2/postgresql.conf','a')  as f:
        f.write('\n' + "port = 5434")
        f.write('\n' + "shared_preload_libraries = 'citus,hll,topn,pg_stat_statements'")
        f.write('\n' + "pg_trgm.similarity_threshold = 0.1")
        f.write('\n' + "pg_trgm.word_similarity_threshold = 0.1")
        f.write('\n' + "pg_trgm.strict_word_similarity_threshold = 0.2")

    args = ['pg_ctl', '-D', 'radixdb', '-l', 'logfile', 'start']
    subprocess.run(args)

    args = ['psql', '-X', '-U', 'postgres', '-d', 'radixdb', '-c', 'create extension citus;create extension pg_cron; create extension pg_background; create extension plpython3u;create extension hll;create extension hstore;create extension topn;create extension kmeans;CREATE EXTENSION http;create extension btree_gist;create extension btree_gin;CREATE EXTENSION pg_trgm;;CREATE EXTENSION ltree;CREATE EXTENSION cube;CREATE EXTENSION intarray;create extension pg_stat_statements;create extension istore;']
    subprocess.run(args)

    args = ['pg_ctl', '-D', 'radixdbw1', '-l', 'logfile-w1', 'start']
    subprocess.run(args)
    args = ['psql', '-X', '-U', 'postgres', '-p', '5433', '-d', 'radixdb', '-c', 'create extension citus;create extension plpython3u; create extension pg_background;create extension hll;create extension topn;create extension hstore;create extension btree_gist;create extension btree_gin;CREATE EXTENSION intarray;CREATE EXTENSION pg_trgm;CREATE EXTENSION ltree;CREATE EXTENSION cube;create extension pg_stat_statements;create extension istore;']
    subprocess.run(args)

    args = ['pg_ctl', '-D', 'radixdbw2', '-l', 'logfile-w2', 'start']
    subprocess.run(args)
    args = ['psql', '-X', '-U', 'postgres', '-p', '5434', '-d', 'radixdb', '-c', 'create extension citus;create extension plpython3u;create extension pg_background; create extension hll;create extension hstore;create extension topn;create extension btree_gist;create extension btree_gin;CREATE EXTENSION intarray;CREATE EXTENSION pg_trgm;CREATE EXTENSION ltree;CREATE EXTENSION cube;create extension pg_stat_statements;create extension istore;']
    subprocess.run(args)

    args = ['psql', '-X', '-U', 'postgres', '-p', '5432', '-d', 'radixdb', '-c', "SELECT * from master_add_node('localhost', 5433);"]
    subprocess.run(args)

    args = ['psql', '-X', '-U', 'postgres', '-p', '5432', '-d', 'radixdb', '-c', "SELECT * from master_add_node('localhost', 5434);"]
    subprocess.run(args)

    args = ['psql', '-X', '-U', 'postgres', '-p', '5432', '-d', 'radixdb', '-f', get_stored_procedure()]
    subprocess.run(args)


def setup_localdb_nested():
    args = ['pg_ctl', '-D', 'radixdb', 'stop']
    subprocess.run(args)

    args = ['pg_ctl', '-D', 'radixdbw1', 'stop']
    subprocess.run(args)

    args = ['pg_ctl', '-D', 'radixdbw2', 'stop']
    subprocess.run(args)

    args = ['pg_ctl', '-D', 'radixdbw1-1', 'stop']
    subprocess.run(args)

    args = ['pg_ctl', '-D', 'radixdbw1-2', 'stop']
    subprocess.run(args)

    time.sleep(1)
    check_kill_process('postgres')

    time.sleep(1)
    args = ['rm', '-rf', os.path.abspath('radixdb')]
    subprocess.run(args)
    args = ['rm', '-rf', os.path.abspath('radixdbw1')]
    subprocess.run(args)
    args = ['rm', '-rf', os.path.abspath('radixdbw2')]
    subprocess.run(args)

    args = ['rm', '-rf', os.path.abspath('radixdbw1-1')]
    subprocess.run(args)
    args = ['rm', '-rf', os.path.abspath('radixdbw1-2')]
    subprocess.run(args)

    args = ['initdb', '-D', 'radixdb', '-U' 'postgres']
    subprocess.run(args)
    args = ['pg_ctl', '-D', 'radixdb', '-l', 'logfile', 'start']
    subprocess.run(args)
    args = ['psql', '-X', '-U', 'postgres', '-c', 'create database radixdb']
    subprocess.run(args)
    args = ['pg_ctl', '-D', 'radixdb', '-l', 'logfile', 'stop']
    subprocess.run(args)

    args = ['initdb', '-D', 'radixdbw1', '-U' 'postgres']
    subprocess.run(args)
    args = ['pg_ctl', '-D', 'radixdbw1', '-l', 'logfile-w1', 'start']
    subprocess.run(args)
    args = ['psql', '-X', '-U', 'postgres', '-c', 'create database radixdb']
    subprocess.run(args)
    args = ['pg_ctl', '-D', 'radixdbw1', '-l', 'logfile-w1', 'stop']
    subprocess.run(args)

    args = ['initdb', '-D', 'radixdbw2', '-U' 'postgres']
    subprocess.run(args)
    args = ['pg_ctl', '-D', 'radixdbw2', '-l', 'logfile-w2', 'start']
    subprocess.run(args)
    args = ['psql', '-X', '-U', 'postgres', '-c', 'create database radixdb']
    subprocess.run(args)
    args = ['pg_ctl', '-D', 'radixdbw2', '-l', 'logfile-w2', 'stop']
    subprocess.run(args)

    args = ['initdb', '-D', 'radixdbw1-1', '-U' 'postgres']
    subprocess.run(args)
    args = ['pg_ctl', '-D', 'radixdbw1-1', '-l', 'logfile-w1-1', 'start']
    subprocess.run(args)
    args = ['psql', '-X', '-U', 'postgres', '-c', 'create database radixdb']
    subprocess.run(args)
    args = ['pg_ctl', '-D', 'radixdbw1-1', '-l', 'logfile-w1-1', 'stop']
    subprocess.run(args)

    args = ['initdb', '-D', 'radixdbw1-2', '-U' 'postgres']
    subprocess.run(args)
    args = ['pg_ctl', '-D', 'radixdbw1-2', '-l', 'logfile-w1-2', 'start']
    subprocess.run(args)
    args = ['psql', '-X', '-U', 'postgres', '-c', 'create database radixdb']
    subprocess.run(args)
    args = ['pg_ctl', '-D', 'radixdbw1-2', '-l', 'logfile-w1-2', 'stop']
    subprocess.run(args)

    with open('./radixdb/postgresql.conf','a')  as f:
        f.write('\n' + "shared_preload_libraries = 'citus,pg_cron,hll,topn,pg_stat_statements'")
        f.write('\n' + "cron.database_name = 'radixdb'")

    with open('./radixdbw1/postgresql.conf','a')  as f:
        f.write('\n' + "port = 5433")
        f.write('\n' + "shared_preload_libraries = 'citus,hll,topn,pg_stat_statements'")

    with open('./radixdbw2/postgresql.conf','a')  as f:
        f.write('\n' + "port = 5434")
        f.write('\n' + "shared_preload_libraries = 'citus,hll,topn,pg_stat_statements'")

    with open('./radixdbw1-1/postgresql.conf','a')  as f:
        f.write('\n' + "port = 5435")
        f.write('\n' + "shared_preload_libraries = 'citus,hll,topn,pg_stat_statements'")

    with open('./radixdbw1-2/postgresql.conf','a')  as f:
        f.write('\n' + "port = 5436")
        f.write('\n' + "shared_preload_libraries = 'citus,hll,topn,pg_stat_statements'")

    args = ['pg_ctl', '-D', 'radixdb', '-l', 'logfile', 'start']
    subprocess.run(args)
    args = ['psql', '-X', '-U', 'postgres', '-d', 'radixdb', '-c', 'create extension citus;create extension pg_cron; create extension pg_background;create extension plpython3u;create extension hll;create extension hstore;create extension topn;create extension kmeans;CREATE EXTENSION http;create extension btree_gist;create extension btree_gin;CREATE EXTENSION pg_trgm;;CREATE EXTENSION ltree;CREATE EXTENSION cube;CREATE EXTENSION intarray;create extension pg_stat_statements;create extension istore;']
    subprocess.run(args)

    args = ['pg_ctl', '-D', 'radixdbw1', '-l', 'logfile-w1', 'start']
    subprocess.run(args)
    args = ['psql', '-X', '-U', 'postgres', '-p', '5433', '-d', 'radixdb', '-c', 'create database radixdb']
    subprocess.run(args)
    args = ['psql', '-X', '-U', 'postgres', '-p', '5433', '-d', 'radixdb', '-c', 'create extension citus;create extension pg_background;create extension plpython3u;create extension hll;create extension topn;create extension hstore;create extension btree_gist;create extension btree_gin;CREATE EXTENSION intarray;CREATE EXTENSION pg_trgm;CREATE EXTENSION ltree;CREATE EXTENSION cube;create extension pg_stat_statements;create extension istore;']
    subprocess.run(args)

    args = ['pg_ctl', '-D', 'radixdbw2', '-l', 'logfile-w2', 'start']
    subprocess.run(args)
    args = ['psql', '-X', '-U', 'postgres', '-p', '5434', '-d', 'radixdb', '-c', 'create extension citus;create extension pg_background;create extension plpython3u;create extension hll;create extension topn;create extension hstore;create extension btree_gist;create extension btree_gin;CREATE EXTENSION intarray;CREATE EXTENSION pg_trgm;CREATE EXTENSION ltree;CREATE EXTENSION cube;create extension pg_stat_statements;create extension istore;']
    subprocess.run(args)

    args = ['psql', '-X', '-U', 'postgres', '-p', '5432', '-d', 'radixdb', '-c', "SELECT * from master_add_node('localhost', 5433);"]
    subprocess.run(args)
    args = ['psql', '-X', '-U', 'postgres', '-p', '5432', '-d', 'radixdb', '-c', "SELECT * from master_add_node('localhost', 5434);"]
    subprocess.run(args)
    args = ['psql', '-X', '-U', 'postgres', '-p', '5432', '-d', 'radixdb', '-f', "src/sql/init.sql"]
    subprocess.run(args)

    args = ['pg_ctl', '-D', 'radixdbw1-1', '-l', 'logfile-w1-1', 'start']
    subprocess.run(args)
    args = ['psql', '-X', '-U', 'postgres', '-p', '5435', '-d', 'radixdb', '-c', 'create extension citus;create extension pg_background;create extension plpython3u;create extension hll;create extension topn;create extension hstore;create extension btree_gist;create extension btree_gin;CREATE EXTENSION intarray;CREATE EXTENSION pg_trgm;CREATE EXTENSION ltree;CREATE EXTENSION cube;create extension pg_stat_statements;create extension istore;']
    subprocess.run(args)

    args = ['pg_ctl', '-D', 'radixdbw1-2', '-l', 'logfile-w1-2', 'start']
    subprocess.run(args)
    args = ['psql', '-X', '-U', 'postgres', '-p', '5436', '-d', 'radixdb', '-c', 'create extension citus;create extension pg_background;create extension plpython3u;create extension hll;create extension topn;create extension hstore;create extension btree_gist;create extension btree_gin;CREATE EXTENSION intarray;CREATE EXTENSION pg_trgm;CREATE EXTENSION ltree;CREATE EXTENSION cube;create extension pg_stat_statements;create extension istore;']
    subprocess.run(args)

    args = ['psql', '-X', '-U', 'postgres', '-p', '5433', '-d', 'radixdb', '-c', "SELECT * from master_add_node('localhost', 5435);"]
    subprocess.run(args)
    args = ['psql', '-X', '-U', 'postgres', '-p', '5433', '-d', 'radixdb', '-c', "SELECT * from master_add_node('localhost', 5436);"]
    subprocess.run(args)
    args = ['psql', '-X', '-U', 'postgres', '-p', '5433', '-d', 'radixdb', '-f', get_stored_procedure()]
    subprocess.run(args)
