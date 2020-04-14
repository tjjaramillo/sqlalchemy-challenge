# Import dependencies
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# Set database

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
base = automap_base()
base.prepare(engine, reflect=True)

measurement = base.classes.measurement
station = base.classes.station

# Set Flask

app = Flask(__name__)

#Set routes

@app.route("/")
def home():
    return (
        f"Available Routes:<br/>"
        f"Precipitation: /api/v1.0/precipitation<br/>"
        f"List of Stations: /api/v1.0/stations<br/>"
        f"Temperature for one year: /api/v1.0/tobs<br/>"
        f"Minimum, maximum and average temperatures from start date(yyyy-mm-dd): /api/v1.0/yyyy-mm-dd<br/>"
        f"Minimum, maximum, and average temperatures from start date to end date(yyyy-mm-dd): /api/v1.0/yyy-mm-dd"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    select = [measurement.date,measurement.prcp]
    queryresult = session.query(*select).all()
    session.close()

    precipitation = []
    for date, prcp in queryresult:
        prcp_dict = {}
        prcp_dict["Date"] = date
        prcp_dict["Precipitation"] = prcp
        precipitation.append(prcp_dict)

    return jsonify(precipitation)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    select = [Station.station,Station.name,Station.latitude,Station.longitude,Station.elevation]
    queryresult = session.query(*select).all()
    session.close()

    stations = []
    for station,name,lat,lon,elevation in queryresult:
        station_dict = {}
        station_dict["Station"] = station
        station_dict["Name"] = name
        station_dict["Latitude"] = lat
        station_dict["Longitude"] = lon
        station_dict["Elevation"] = elevation
        stations.append(station_dict)

    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    lateststr = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    latestdate = dt.datetime.strptime(lateststr, '%Y-%m-%d')
    querydate = dt.date(latestdate.year -1, latestdate.month, latestdate.day)
    sel = [Measurement.date,Measurement.tobs]
    query_result = session.query(*sel).filter(Measurement.date >= querydate).all()
    session.close()

    tobsall = []
    for date, tobs in query_result:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Tobs"] = tobs
        tobsall.append(tobs_dict)

    return jsonify(tobsall)

@app.route("/api/v1.0/<start>")
def start_date(start):
    session = Session(engine)
    query_result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    session.close()

    tobsall = []
    for min,avg,max in query_result:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        tobsall.append(tobs_dict)

    return jsonify(tobsall)

@app.route("/api/v1.0/<start>/<stop>")
def start_stop_date(start,stop):
    session = Session(engine)
    queryresult = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= stop).all()
    session.close()

    tobsall = []
    for min,avg,max in queryresult:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        tobsall.append(tobs_dict)

    return jsonify(tobsall)

if __name__ == '__main__':
    app.run(debug=True)


