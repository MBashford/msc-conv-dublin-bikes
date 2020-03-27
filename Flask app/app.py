'''
Created on 16 Feb 2020

@author: Ruth Holmes
'''

from flask import Flask, render_template, g, jsonify, request
from sqlalchemy import create_engine
from configparser import ConfigParser

# read DataBase info from the config file
config = ConfigParser()
config.read("config.ini")
options = config["DataBase"]

app = Flask(__name__)

engine = create_engine("mysql://" + options["user"] + ":" + options["passwd"] + "@"
                       + options["host"] + "/" + options["database"])
engine.connect()
 
# @app.route("/test")
# def dub_bikes():
#     l1 = engine.execute('select name from static_data')  #
#     return render_template('home.html', l1=l1)  # pulls home.html template from templates folder
#  
@app.route("/index")
def index_page():
    # request co-ordinates, name, number & dynamic bikes/weather data from DataBase for each bike station
    statinfo = engine.execute("""
        select s.number, s.address, b.status, b.available_bike_stands, b.available_bikes, 
            w.weather_main, w.weather_icon, w.main_temp, w.main_feels_like, w.rain_1h,
            s.lat, s.lng 
        from static_data s, bikes_current b, weather_current w, bike_weather_assoc a
        where s.number = b.number and b.number = a.bike_station_id and a.weather_station = w.name
        order by s.address asc
        """)
    return render_template('index.html', title='Map', statinfo=statinfo)


@app.route("/index/route")
def index_page_route():
    statinfo = engine.execute('select number, address, lat, lng from static_data')
    coords = {"dest":[float(request.args.get('tolat')),float(request.args.get('tolong'))],
            "origin":[float(request.args.get('fromlat')), float(request.args.get('fromlong'))]}
    return render_template('routeindex.html', title='Map', statinfo=statinfo, coordinates=coords)


@app.route("/info")
def info_page():
    stat_addr = engine.execute('select number, address from static_data')
    return render_template('info.html', stat_addr = stat_addr, stat_info="none")  # pulls home.html template from templates folder


@app.route("/info/<stat_id>")
def info_page_refined(stat_id):
    stat_info = engine.execute('select * from static_data where number = {}'.format(stat_id))
    stat_addr = engine.execute('select number, address from static_data')
    return render_template('info.html', stat_addr = stat_addr,  stat_info = stat_info)  # pulls home.html template from templates folder


@app.route("/")
def bikemap():
    statinfo = engine.execute('select number, address, lat, lng from static_data')
    return render_template('map.html', title='Map', statinfo=statinfo)


@app.route("/route")
def routemap():
    statinfo = engine.execute('select number, address, lat, lng from static_data')
    return render_template('route.html', title='Route', statinfo=statinfo)


@app.route("/get_weather_dublin")
def get_weather_dublin():
    """Allows client side to get up-to-date weather Info for dublin"""
    dublin_weather = engine.execute("""
        select w.main_temp, w.main_feels_like, w.weather_main, w.weather_icon
        from weather_current w
        where w.name = "Dublin"
        """)

    for row in dublin_weather:
        response = jsonify(dict(row))
        response.headers.add('Access-Control-Allow-Origin', '*')

    return response


# allows us to run directly with python i.e. don't have to set env variables each time
if __name__ == '__main__':
    app.run(debug=True)
