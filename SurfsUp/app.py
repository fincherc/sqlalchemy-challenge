# Import the dependencies.
from flask import Flask, jsonify
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


#################################################
# Function Setup
#################################################

def latest_date_db():
    recent_date = Session.query(func.max(Measurement.date)).one()
    most_recent_date = recent_date[0]

    # Calculate the date one year from the last date in data set.
    most_recent_date = dt.datetime.strptime(most_recent_date, '%Y-%m-%d')
    one_year_ago_date = most_recent_date - dt.timedelta(days=365)

    return one_year_ago_date

#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Declare a Base using `automap_base()`
Base = automap_base()

# Use the Base class to reflect the database tables
Base.prepare(autoload_with=engine)


# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session
Session = Session(engine)


#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    return (
        f"Welcome to the Climate App API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start><end>"
    )

# Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value.
# Return the JSON representation of your dictionary.

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value."""
    
    one_year_ago_date = latest_date_db()

    # Perform a query to retrieve the data and precipitation scores
    precipitation_date_data = Session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago_date).order_by(Measurement.date).all()
    
    precipitation_date_dict = dict(precipitation_date_data)
    
    return jsonify(precipitation_date_dict)

# Return a JSON list of stations from the dataset.

@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""

    stations = [result[0] for result in Session.query(Measurement.station).distinct()]
    
    return jsonify(stations)

# Query the dates and temperature observations of the most-active station for the previous year of data.
# Return a JSON list of temperature observations for the previous year.

@app.route("/api/v1.0/tobs")
def tobs():
    """Query the dates and temperature observations of the most-active station for the previous year of data."""
    
    #Retrieve active stations
    result_active_station = Session.query(Measurement.station, func.count(Measurement.station).label('count')).\
        group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    
    most_active_station = result_active_station[0][0]

    one_year_ago_date = latest_date_db()

    #Get the tobs
    tobs_station = [result[0] for result in Session.query(Measurement.tobs).\
        filter(Measurement.date >= one_year_ago_date).\
        filter(Measurement.station == most_active_station)]

    return jsonify(tobs_station)

# Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start range.
# For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.

@app.route("/api/v1.0/<start>")
def start(start):
    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start range."""
    
    result = Session.query(func.min(Measurement.tobs).label('TMIN'),
                           func.avg(Measurement.tobs).label('TAVG'),
                           func.max(Measurement.tobs).label('TMAX')) \
                    .filter(Measurement.date >= start) \
                    .all()
    
    tobs_start_data = [result[0][0], result[0][1], result[0][2]]
    
    return jsonify(tobs_start_data)

# Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start-end range.
# For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.

@app.route("/api/v1.0/<start>/<end>")
def start_and_end(start, end):

    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start-end range."""

    result = Session.query(func.min(Measurement.tobs).label('TMIN'),
                           func.avg(Measurement.tobs).label('TAVG'),
                           func.max(Measurement.tobs).label('TMAX')) \
                    .filter(Measurement.date >= start) \
                    .filter(Measurement.date <= end) \
                    .all()
    
    tobs_start_data = [result[0][0], result[0][1], result[0][2]]
    
    return jsonify(tobs_start_data)

if __name__ == "__main__":
    app.run(debug=True)
