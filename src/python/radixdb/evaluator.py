import json
import pickle
import io
from types import MethodType
from datetime import datetime
from datetime import date
import time
import decimal
from uuid import UUID

import radixdb.lang as lang
import base64

import matplotlib
matplotlib.use('webagg')
import matplotlib.pyplot as plt
import pandas as pd

plt.gcf().set_size_inches(0.5, 0.5)

def records_to_df(records):
    data = {}
    for r in records:
        for k in r.keys():
            if data.get(k, -1) == -1:
                data[k] = []
            data[k].append(r[k])
    return pd.DataFrame(data)

def _save_plot():
    buf = io.BytesIO()
    plt.savefig(buf, format='jpg')
    buf.seek(0)
    return "data:image/jpg;base64," + base64.b64encode(buf.getbuffer().tobytes()).decode("utf-8", "ignore")

def radixdb_eval(code, plot_encoding=True):
    output = []
    try:
        from radixdb.radixbot import exec_query
        print("code:", code)
        statmts = lang.parse(code)
        sql = statmts[0]
        print("sql:", sql)
        ret = exec_query(sql)
        df = records_to_df(ret)
        output.append(df)
        for s in statmts[1:]:
            print("s:", s)
            if s.startswith("_df"):
                eval(s, {"_df": df})
            else:
                exec(open("./models/"+s+".py").read(), {"_df": df})
            output.append(_save_plot())
    except Exception as e:
        output = []
        output.append(pd.DataFrame({'error':[str(e)]}))
    return output
