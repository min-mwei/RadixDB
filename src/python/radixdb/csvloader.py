import csv
import asyncpg
import os
import pathlib
import asyncio

def build_fileds(row):
    result = ""
    for i in range(len(row)):
        result += '"' + row[i] + '"'
        result += " text"
        if i < len(row) - 1 :
            result += ','
    #print("result:", result)
    return result

async def create_table(tbl, fields):
    conn = await asyncpg.connect('postgresql://postgres@localhost/radixdb')
    await conn.execute('''
        drop table if exists {0};
        CREATE TABLE {1} (
            {2}
        )
    '''.format(tbl, tbl, fields))
    await conn.close()

async def create_schema(schema):
    conn = await asyncpg.connect('postgresql://postgres@localhost/radixdb')
    await conn.execute('''create schema if not exists {0};'''.format(schema))
    await conn.close()

async def insert(tbl, data, schema_name):
    conn = await asyncpg.connect('postgresql://postgres@localhost/radixdb')
    result = await conn.copy_records_to_table(tbl, records = data, schema_name = schema_name)
    await conn.close()

def internal_load(table_name, file_name, encoding, schema_name = None, override=True, batch_size=1000):
    with open(file_name, newline='', encoding = encoding) as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        row_count = 0
        batch = 0
        records = []
        for row in reader:
            if row_count == 0:
                if schema_name:
                    tbl_name = schema_name +  "." + table_name
                    asyncio.get_event_loop().run_until_complete(create_schema(schema_name))
                else:
                    tbl_name = table_name
                if override:
                    asyncio.get_event_loop().run_until_complete(create_table(tbl_name, build_fileds(row)))
            if batch < batch_size:
                batch += 1
                if row_count > 0:
                    records.append(tuple(row))
            else:
                asyncio.get_event_loop().run_until_complete(insert(table_name, records, schema_name))
                records = []
                batch = 0
            row_count += 1
        if batch > 0:
            asyncio.get_event_loop().run_until_complete(insert(table_name, records, schema_name))
    return True

def load_csv(table_name, file_name, schema_name = None, override=True, batch_size=1000):
    for encoding in ["utf-8","ISO-8859-1"]:
        try:
            if internal_load(table_name, file_name, encoding, schema_name, batch_size):
                return
        except ValueError as e:
            print("data parse error", str(e))
