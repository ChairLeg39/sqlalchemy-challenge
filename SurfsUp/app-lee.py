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
    import datetime as dt
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
    
    # Convert the query results to a dictionary using date as they key and prcp as the value
    prcp_dict = {date: prcp for date, prcp in results}
    
    # Close the session
    session.close()
    
    # Return the JSON representation of the dictionary
    return jsonify(prcp_dict)





if __name__ == '__main__':
    app.run(debug=True)
