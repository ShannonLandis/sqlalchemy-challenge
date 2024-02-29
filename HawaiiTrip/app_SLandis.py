# Import the dependencies.
import numpy as np
import datetime as dt
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify



#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Station = Base.classes.station
Measurements = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0" 
    )


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all stations"""
    # Query all Stations
    results = session.query(Station.name).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)


@app.route("/api/v1.0/precipitation")
def precip():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return precipitation for last 12 months with date as key and prcp as value"""
    # Get Start Date
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    # get the date and precip
    results = session.query(Measurements.date, Measurements.prcp ).\
                  filter(Measurements.date > query_date).group_by(Measurements.date).order_by(Measurements.date).all()

    session.close()

    # Convert list of tuples into normal list
    #precip_bydate = list(np.ravel(results))
    precip_bydate = []
    for date, pcrp in results:
        precip_dict = {}
        precip_dict["date"] = date
        precip_dict["pcrp"] = pcrp
        precip_bydate.append(precip_dict)

    return jsonify(precip_bydate)


   
    
    

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all tobs for Station with most records - last 12 months"""
    # Get Start Date
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurements.date, Measurements.tobs).\
                  filter(Measurements.date >= query_date).filter(Measurements.station == 'USC00519281').\
                    all()

    session.close()

    # Convert list of tuples into normal list
    station_tobs = list(np.ravel(results))

    return jsonify(station_tobs)




@app.route("/api/v1.0/<startdate>")
def startdate(startdate):
    
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    result = session.query(Measurements.date,\
                           func.min(Measurements.tobs),\
                           func.max(Measurements.tobs),\
                           func.avg(Measurements.tobs)).\
                            group_by(Measurements.date).all()
    
    session.close()
    
    
    temps_bydate = []
    for date, minTemp, maxTemp, avgTemp in result:
        temp_dict = {}
        temp_dict["date"] = date
        temp_dict["minTemp"] = minTemp
        temp_dict["maxTemp"] = maxTemp
        temp_dict["avgTemp"] = avgTemp
        temps_bydate.append(temp_dict)    
    
    
    for i in range(len(temps_bydate)):
        
        if temps_bydate[i]['date'] == startdate:

            return jsonify(temps_bydate[i])

    return jsonify({"error": f"Date {startdate} not found."}), 404






@app.route("/api/v1.0/<startdate>/<enddate>")
def startenddate(startdate, enddate):
    
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    result = session.query(Measurements.date,\
                           func.min(Measurements.tobs),\
                           func.max(Measurements.tobs),\
                           func.avg(Measurements.tobs)).\
                            group_by(Measurements.date).all()
    
    session.close()
    
    
    temps_bydate = []
    for date, minTemp, maxTemp, avgTemp in result:
        temp_dict = {}
        temp_dict["date"] = date
        temp_dict["minTemp"] = minTemp
        temp_dict["maxTemp"] = maxTemp
        temp_dict["avgTemp"] = avgTemp
        temps_bydate.append(temp_dict)    
    
    result_dates = []
    for i in range(len(temps_bydate)):
        
        if temps_bydate[i]['date']>= startdate and temps_bydate[i]['date'] <= enddate:
            
            result_dates.append(temps_bydate[i]) 
        
        
    if len(result_dates)>0:
        return jsonify(result_dates)

    return jsonify({"error": f"Date {startdate} not found."}), 404


                              
                                        
                                        

if __name__ == "__main__":
    app.run(debug=True)

    





