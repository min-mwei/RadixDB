def parse(sql):
    source = sql.split(';')
    #sql =  rewrite_sql(sql)
    statmts = []
    for s in source:
        c = s.strip().replace('\xa0', ' ')
        if c.startswith("plot"):
            c = '_df.' + c
        if len(c) > 0:
            statmts.append(c)
    return statmts
