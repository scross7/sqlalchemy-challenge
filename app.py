import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt
from datetime import datetime
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station


app = Flask(__name__)


@app.route("/")
def home():
    """List of all available api routes."""

    return (
        f"Available Routes:<br/>"
        f"<br/>"
        f" This will return a list of precipitation data<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"<br/>"
        f" This will return a list of stations<br/>"
        f"/api/v1.0/stations<br/>"
        f"<br/>"
        f" This will return a list of temperature data<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br/>"
        f" This will accept start date and start/end date in the format '%Y-%m-%d'<br/>"
        f" and return the minimum, average, and maximum temperatures for that range of dates<br/>"
        f"/api/v1.0/start and /api/v1.0/start/end<br/>"

    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Dictionary using 'date' as key and 'preciptation' as value."""

    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp).all()
    session.close()

    date_prcp = []
    for date, prcp in results:
        date_prcp_dict = {}
        date_prcp_dict["date"] = date
        date_prcp_dict["prcp"] = prcp
        date_prcp.append(date_prcp_dict)

    return jsonify(date_prcp)


@app.route("/api/v1.0/stations")
def stations():
    
    """JSON List of all stations."""

    session = Session(engine)
    results = session.query(Station.name.distinct())
    session.close()

    station = []
    for name in results:
        station_dict = {}
        station_dict["name"] = name
        station.append(station_dict)

    return jsonify(station)


@app.route("/api/v1.0/tobs")
def tobs():
    
    """JSON List of Temperature Observations from the previous year."""

    session = Session(engine)

    # Calculate the date 1 year ago from the last data point in the database ('2017-08-23')
    d = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    d = dt.datetime.strptime(d, '%Y-%m-%d')

    # datetime.datetime(2016, 8, 23, 0, 0)
    d_yr = d - dt.timedelta(days=366)

    # Perform a query to retrieve the data and precipitation scores
    # Save the query results as a Pandas DataFrame and set the index to the date column
    # Sort the dataframe by date
    columns = [Measurement.date, Measurement.tobs]
    results = session.query(*columns).filter(Measurement.date >= d_yr)

    session.close()
    
    date_tobs = []
    for date, tobs in results:
        date_tobs_dict = {}
        date_tobs_dict["date"] = date
        date_tobs_dict["tobs"] = tobs
        date_tobs.append(date_tobs_dict)

    return jsonify(date_tobs)


@app.route("/api/v1.0/<start1>")
def calc_temps1(start1):

    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start1).all()
    session.close()
    
    tobs_desc = []
    for min, avg, max in results:
        tobs_desc_dict = {}
        tobs_desc_dict["Min"] = min
        tobs_desc_dict["Avg"] = avg
        tobs_desc_dict["Max"] = max
        tobs_desc.append(tobs_desc_dict)

    return jsonify(tobs_desc)

@app.route("/api/v1.0/<start>/<end>")
def calc_temps(start, end):

    """TMIN, TAVG, and TMAX from start to end date.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns JSON List:
        TMIN, TAVE, and TMAX
    """

    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()
    
    tobs_desc = []
    for min, avg, max in results:
        tobs_desc_dict = {}
        tobs_desc_dict["Min"] = min
        tobs_desc_dict["Avg"] = avg
        tobs_desc_dict["Max"] = max
        tobs_desc.append(tobs_desc_dict)

    return jsonify(tobs_desc)


if __name__ == "__main__":
    app.run(debug=True)
