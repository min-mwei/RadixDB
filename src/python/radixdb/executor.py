import asyncio
import asyncpg
import json
import pandas as pd

def _records_to_df(records):
    data = {}
    for r in records:
        for k in r.keys():
            if data.get(k, -1) == -1:
                data[k] = []
            data[k].append(r[k])
    return pd.DataFrame(data)

async def _run(pool, query, *args):
    async with pool.acquire() as connection:
        await connection.set_builtin_type_codec('hstore', codec_name='pg_contrib.hstore')
        return await connection.fetchval(query)

async def _run_ddl(connString, query):
    con = await asyncpg.connect(connString)
    result = await con.execute(query)
    print(result)
    await con.close()

async def _exec_ddl(pool, query, *args):
    async with pool.acquire() as conn:
        return await conn.execute(query)

async def _exec_dml(pool, query, *args):
    async with pool.acquire() as conn:
        await conn.set_builtin_type_codec('hstore', codec_name='pg_contrib.hstore')
        await conn.set_type_codec(
            'numeric', encoder=str, decoder=float,
            schema='pg_catalog', format='text'
        )
        return await conn.fetch(query)

async def _exec_query(query, connString, *args):
    conn = await asyncpg.connect(connString)
    ret = await conn.fetch(query)
    await conn.close()
    return ret

async def _insert_bytes(pool, name, data):
    async with pool.acquire() as conn:
        return await conn.execute('''
        INSERT INTO contents(name, data) VALUES($1, $2)
    ''', name, data)

async def _copy_records(connString, tbl, tuples, columns):
    con = await asyncpg.connect(connString)
    ret = await con.copy_records_to_table(tbl, records=tuples, columns=list(columns))
    await con.close()
    return ret

_df_pg_types = {
    'float64': 'double precision',
    'float32': 'float',
    'datetime64[ns]': 'timestamp without time zone',
    'datetime64[h]': 'timestamp without time zone',
    'datetime64[M]': 'date',
    'string': 'text',
    'int': 'int',
    'object': 'text',
    'int64': 'bigint',
    }

def df_create(df, tbl, connString):
    tuples = []
    for name, t in zip(df.columns, df.dtypes):
        tuples.append(name + '\t' + _df_pg_types[str(t)])
    sql = "create table " + tbl + "(" + ",".join(tuples) + ")"
    return asyncio.get_event_loop().run_until_complete(_run_ddl(connString, sql))

def df_copy(df, tbl, connString):
    tuples = [tuple(x) for x in df.values]
    return asyncio.get_event_loop().run_until_complete(_copy_records(connString, tbl, tuples, list(df.columns)))

def df_query(query, connString):
    return _records_to_df(asyncio.get_event_loop().run_until_complete(_exec_query(query, connString)))
    #return asyncio.get_event_loop().run_until_complete(_exec_query(query, connString))

def do_insert_value(loop, pool, name, data):
     return loop.run_until_complete(_insert_bytes(pool, name, data))

def run_sql(connString, query):
     return asyncio.get_event_loop().run_until_complete(_run_ddl(connString, query))

def run_query(loop, pool, query):
    r = loop.run_until_complete(_run(pool, query))
    return r

def exec_query(loop, pool, query):
    r = loop.run_until_complete(_exec_dml(pool, query))
    return r

def exec_ddl(loop, query, pool=None):
    r = loop.run_until_complete(_exec_ddl(pool, query))
    return r

def run_job(loop, connString, source_code):
    ret = loop.run_until_complete(_run(connString, 'select radixdb_exec($${0}$$)'.format(source_code)))
    return json.loads(ret[0]['radixdb_exec'])['radixdb_data']

async def run_sql_at_background(conn, sql):
    ret = await conn.fetch('select radixdb_exec_sql_background($${0}$$)'.format(sql))
    return json.loads(ret[0]['radixdb_exec_sql_background'])

async def get_background_result(conn, handle):
    ret = await conn.fetch('SELECT * FROM pg_background_result({}) as (result jsonb);'.format(handle['pg_background_launch']))
    return ret[0]
