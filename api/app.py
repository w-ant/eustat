from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import pandas as pd

pd.options.mode.chained_assignment = None
import simplejson as json

app = Flask(__name__)
CORS(app)


@app.route("/")
def home():
    return "<h1>Eurostat</h1>"


@app.route("/countries")
def list_of_countries():
    db = sqlite3.connect("eurostat.db")
    cursor = db.cursor()
    query = "SELECT ccode,country FROM countries"
    result = dict(cursor.execute(query).fetchall())
    db.close()
    return jsonify(result)


@app.route("/data/<country_code>/<trade_type>", methods=["GET", "OPTIONS"])
def country(country_code, trade_type):

    db = sqlite3.connect("eurostat.db")

    # sql_query = 'SELECT PERIOD, SUM(VALUE_EUR) total FROM data  WHERE DECLARANT_ISO=? and TRADE_TYPE=? and PERIOD NOT LIKE "%52" GROUP BY PERIOD ORDER BY PERIOD'
    sql_query = "SELECT PERIOD, SUM(VALUE_IN_EUROS) total FROM trade  WHERE DECLARANT_ISO=? and TRADE_TYPE=? GROUP BY PERIOD "
    cc = country_code.upper()
    tt = trade_type.upper()
    df = pd.read_sql_query(sql_query, db, params=[cc, tt])
    db.close()
    print(df.head())
    months = df[df.PERIOD % 100 != 52]
    # years = df[df.PERIOD % 100 == 52]
    months["MA12"] = months.total.rolling(12).mean()
    months["MOM"] = months.total.pct_change() * 100
    months["YOY"] = months.total.pct_change(periods=12) * 100
    # years.drop(columns=["total"], inplace=True)
    # years.rename(index=str, columns={"PERIOD": "year"}, inplace=True)

    # years = years.round(2).to_dict(orient="list")
    months = months.round(2).to_dict(orient="list")

    retJson = json.dumps({**months}, ignore_nan=True)

    return retJson


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
