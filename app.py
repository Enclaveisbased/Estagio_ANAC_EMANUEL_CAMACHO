from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
import requests
from geopy.distance import geodesic
import Simmpy
import numpy as np
import sys
import os
import scipy.constants as sc
import matplotlib.pyplot as plt
import Unitconversions as cf
import Glidecharpy
import Ballisticpy
import requests
from geopy.distance import geodesic
from geopy.point import Point
import webbrowser

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # For session management

# Dummy data
file_path = 'DATASHEET.xlsx'
fixed_wing_df = pd.read_excel(file_path, sheet_name='fixed', header=None, names=['Name', 'Cruise speed', 'Max speed', 'Endurance', 'Ceiling', 'MTOM', 'Aspect Ratio', 'Wing Area', 'Cd0', 'Oswald Coefficient'])
quadcopter_df = pd.read_excel(file_path, sheet_name='quad', header=None, names=['Name', 'Ceiling', 'Max Wind Resistance', 'MTOM', 'Cd0', 'Max speed', 'Side area'])


@app.route('/')
def index():
    return render_template('index.html',
                           fixed_wing_list=fixed_wing_df['Name'].tolist(),
                           quadcopter_list=quadcopter_df['Name'].tolist(),
                           errors={})



@app.route('/run_analysis', methods=['POST'])
def run_analysis():
    errors = {}
    
    # Retrieve and validate form data
    aircraft_type = request.form.get('aircraft_type')
    aircraft_name = request.form.get('aircraft_name')
    icao_code = request.form.get('icao_code')
    box = request.form.get('box')
    initial_latitude = request.form.get('initial_latitude')
    initial_longitude = request.form.get('initial_longitude')
    heading = request.form.get('heading')
    speed = request.form.get('speed')
    
    # Validate ICAO code
    if icao_code and len(icao_code) != 4:
        errors['icao_code'] = "ICAO Code must be exactly 4 letters."
    
    # Validate bounding box
    if box:
        box_parts = box.split(',')
        if len(box_parts) != 4:
            errors['box'] = "Bounding box must have exactly four values: lat1, lon1, lat2, lon2."
        else:
            try:
                lat1, lon1, lat2, lon2 = map(float, box_parts)
                if not (-90 <= lat1 <= 90) or not (-90 <= lat2 <= 90):
                    errors['box'] = "Latitude values must be between -90 and 90 degrees."
                if not (-180 <= lon1 <= 180) or not (-180 <= lon2 <= 180):
                    errors['box'] = "Longitude values must be between -180 and 180 degrees."
            except ValueError:
                errors['box'] = "Bounding box values must be valid numbers."
    
    # Validate latitude and longitude
    if initial_latitude:
        try:
            initial_latitude = float(initial_latitude)
            if not (-90 <= initial_latitude <= 90):
                errors['initial_latitude'] = "Latitude must be between -90 and 90 degrees."
        except ValueError:
            errors['initial_latitude'] = "Initial Latitude must be a valid number."
    
    if initial_longitude:
        try:
            initial_longitude = float(initial_longitude)
            if not (-180 <= initial_longitude <= 180):
                errors['initial_longitude'] = "Longitude must be between -180 and 180 degrees."
        except ValueError:
            errors['initial_longitude'] = "Initial Longitude must be a valid number."
    
    # Validate heading
    if heading:
        try:
            heading = float(heading)
            if not (0 <= heading <= 360):
                errors['heading'] = "Heading must be between 0 and 360 degrees."
        except ValueError:
            errors['heading'] = "Heading must be a valid number."
    
    # Validate speed
    if speed:
        try:
            speed = float(speed)
            # Fetch max speed from the dataframe
            if aircraft_type == 'fixed_wing':
                max_speed = fixed_wing_df.query("Name == @aircraft_name")['Max speed'].values
            else:
                max_speed = quadcopter_df.query("Name == @aircraft_name")['Max speed'].values
            
            if max_speed.size > 0 and speed > max_speed[0]:
                errors['speed'] = f"Speed must be less than or equal to the maximum speed of {max_speed[0]}."
        except ValueError:
            errors['speed'] = "Speed must be a valid number."

    if errors:
        # If there are errors, re-render the form with error messages
        return render_template('index.html', 
                               aircraft_type=aircraft_type, aircraft_name=aircraft_name,
                               icao_code=icao_code, box=box, initial_latitude=initial_latitude,
                               initial_longitude=initial_longitude, heading=heading, speed=speed,
                               errors=errors, fixed_wing_list=fixed_wing_df['Name'].tolist(),
                               quadcopter_list=quadcopter_df['Name'].tolist())
    
 ### METAR AQUISITION

    # Parse and format the bounding box for API request
    if box:
        box_parts = list(map(float, box.split(',')))
        box_formatted = ",".join(map(str, box_parts))
    else:
        box_formatted = ""

    # METAR Acquisition
    try:
        METARres = requests.get(f"https://aviationweather.gov/api/data/metar?ids={icao_code}&format=geojson&bbox={box_formatted}")
        METARres.raise_for_status()
        METAR = METARres.json()
        
        TSL = METAR["features"][1]["properties"]["temp"]
        PSL = METAR["features"][1]["properties"]["altim"]
        windspd = METAR["features"][1]["properties"]["wspd"]
        windhdg = METAR["features"][1]["properties"]["wdir"]
    except Exception as e:
        flash(f"An error occurred while fetching METAR data: {e}", category='error')
        return redirect(url_for('index'))



    ### SPECIFIC AIRCRAFT DATA RETRIEVAL
    if aircraft_type == 'fixed_wing':
        aircraft_df = fixed_wing_df
    elif aircraft_type == 'quadcopter':
        aircraft_df = quadcopter_df
    else:
        flash("Invalid aircraft type selected.", category='error')
        return redirect(url_for('index'))

    aircraft_data = aircraft_df[aircraft_df['Name'] == aircraft_name]
    if aircraft_data.empty:
        flash("Selected aircraft not found in the database.", category='error')
        return redirect(url_for('index'))

    aircraft_properties = aircraft_data.iloc[0]

    if aircraft_type == 'fixed_wing':
        MTOM = aircraft_properties['MTOM']
        AR = aircraft_properties['Aspect Ratio']
        WA = aircraft_properties['Wing Area']
        Cd0 = aircraft_properties['Cd0']
        oswald = aircraft_properties['Oswald Coefficient']
        ceiling = aircraft_properties['Ceiling']
        simresults = Simmpy.fix(TSL, PSL, initial_latitude, initial_longitude, heading, windspd, windhdg, ceiling, MTOM, AR, WA, Cd0, oswald, 0)
    elif aircraft_type == 'quadcopter':
        MTOM = aircraft_properties['MTOM']
        A = aircraft_properties['Side area']
        Cd0 = aircraft_properties['Cd0']
        ceiling = aircraft_properties['Ceiling']
        simresults = Simmpy.quad(PSL, TSL, heading, initial_latitude, initial_longitude, windhdg, windspd, 0, speed, ceiling, MTOM, Cd0, A)

    ###### RESULTS SHOWING ###################################################################################

    final_latitude = simresults[0]
    final_longitude = simresults[1]  
    
    
    










    #######################FINAL##############################

    flash("Analysis completed successfully!", category='success')
    
    return render_template('results.html', simresults=simresults)

      
    
 

    

if __name__ == '__main__':
    app.run(debug=True)
