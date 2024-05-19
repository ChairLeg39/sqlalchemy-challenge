# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

# Create an engine for the hawaii.sqlite database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()

# Reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

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
def homepage():
    """List all available api routes."""
    return(
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():

    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Calculate the date one year ago from the last data point in the database
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    previous_year_date = dt.datetime.strptime(most_recent_date, "%Y-%m-%d") - dt.timedelta(days=365)
    
    # Perform a query to retrieve the data and precipitation scores
    results = session.query(Measurement.date, Measurement.prcp).\
                filter(Measurement.date >= previous_year_date).\
                filter(Measurement.date <= most_recent_date).\
                order_by(Measurement.date).all()
    
    # Close the session
    session.close()
    
    # Convert the query results to a dictionary using date as the key and prcp as the value
    prcp_dict = {date: prcp for date, prcp in results}
    
    # Return the JSON representation of the dictionary
    return jsonify(prcp_dict)

@app.route("/api/v1.0/stations")
def stations():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Perform a query to return all the stations in the database
    stations = session.query(Station.station).all()
    
    # Close the session
    session.close()
    
    # Convert list of tuples into normal list
    stations_list = list(np.ravel(stations))
    
    # Return the JSON representation of the list
    return jsonify(stations_list)
    
@app.route("/api/v1.0/tobs")
def tobs():

    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Find the most active station
    most_active_station = session.query(Measurement.station, func.count(Measurement.station)).\
                            group_by(Measurement.station).\
                            order_by(func.count(Measurement.station).desc()).first()[0]
                            
    # Calculate the date one year ago from the last data point in the database
    most_recent_date = session.query(func.max(Measurement.date)).\
                            filter(Measurement.station == most_active_station).scalar()
    previous_year_date = dt.datetime.strptime(most_recent_date, "%Y-%m-%d") - dt.timedelta(days=365)
    
    # Perform a query for the last year of temperature observations for this station
    results = session.query(Measurement.date, Measurement.tobs).\
                             filter(Measurement.station == most_active_station).\
                             filter(Measurement.date >= previous_year_date).\
                             order_by(Measurement.date).all()
                             
    # Close the session
    session.close()
    
    # Create a list of dictionaries, using date and tobs as the keys
    tobs_list = [{"date": date, "tobs": tobs} for date, tobs in results]
    
    # Return the JSON representation of the list
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def temp_stats_from_start(start):

    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Perform a query to find the temperature statistics starting with the start date
    results = session.query(func.min(Measurement.tobs),
                    func.avg(Measurement.tobs),
                    func.max(Measurement.tobs)).\
                    filter(Measurement.date >= start).all()
                    
    # Close the session
    session.close()
    
    # Create a dictionary to hold the results
    temp_stats = {
        "Start Date": start,
        "Min Temp": results[0][0],
        "Avg Temp": round(results[0][1], 1),
        "Max Temp": results[0][2]
    }

    # Return the JSON representation of the dictionary
    return jsonify(temp_stats)

@app.route("/api/v1.0/<start>/<end>")
def temp_stats_from_range(start, end):
    
    # Create our session (link) from Python to the DB
    session = Session(engine)


if __name__ == '__main__':
    app.run(debug=True)
