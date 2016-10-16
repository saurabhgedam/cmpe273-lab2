import requests
import json
from urllib import urlopen
from datetime import datetime
import operator
from spyne import ServiceBase, Float,Unicode, rpc, Application
from spyne.protocol.http import HttpRpc
from spyne.protocol.json import JsonDocument
from spyne.server.wsgi import WsgiApplication
import logging
logging.basicConfig(level=logging.DEBUG)

class CrimeService(ServiceBase):
  @rpc(Float, Float, Float, _returns=Unicode)
  def checkcrime(self, latitude, longitude, radius):
    #response = requests.get('https://api.spotcrime.com/crimes.json?lat=37.334164&lon=-121.884301&radius=0.02&key=.')

    url = 'https://api.spotcrime.com/crimes.json?lat=37.334164&lon=-121.884301&radius=0.02&key=.'

    abc= urlopen(url)
    xyz = json.loads(abc.read().decode('utf-8'))
    total_crime=0
    Assault=0
    Arrest=0
    Burglary=0
    Robbery=0
    Theft=0
    Other=0

    crime_time_dict = {}
    crime_address_dict = {}
    crime_type_dict = {}
    time_list=["12:01am-3am" ,"3:01am-6am","6:01am-9am", "9:01am-12noon","12:01pm-3pm","3:01pm-6pm","6:01pm-9pm", "9:01pm-12midnight"]


    for each in xyz['crimes']:
        total_crime=total_crime+1
        crime_type = each['type']
        if crime_type not in crime_type_dict:
            crime_type_dict[crime_type] = 1
        else:
            crime_type_dict[crime_type] = crime_type_dict[crime_type] + 1
        crime_address = each['address']
        if crime_address not in crime_address_dict:
            crime_address_dict[crime_address] = 1
        else:
            crime_address_dict[crime_address] = crime_address_dict[crime_address] + 1
        crime_time = datetime.strptime(each["date"], '%m/%d/%y %I:%M %p').hour
        if (crime_time > 0 and crime_time <= 3):
            event_time = 0
        elif crime_time >3 and crime_time <=6 : 
            event_time = 1
        elif crime_time >6 and crime_time <=9 : 
            event_time = 2
        elif crime_time >9 and crime_time <=12 : 
            event_time = 3
        elif crime_time >12 and crime_time <=15 :
            event_time = 4
        elif crime_time >15 and crime_time <=18 :
            event_time = 5
        elif crime_time >18 and crime_time <=21 :
            event_time = 6
        else:
            event_time =7
        if time_list[event_time] not in crime_time_dict:
            crime_time_dict[time_list[event_time]] = 1
        else:
            crime_time_dict[time_list[event_time]] = crime_time_dict[time_list[event_time]] + 1

    sorted_map = sorted(crime_address_dict.items(), key=operator.itemgetter(1),reverse=True)
    #print(crime_time_dict)
    #print(crime_type_dict)
    #print(crime_address_dict)
    #print(total_crime)
    #print(sorted_map)

    response = {
        "total_crime": total_crime,
        "the_most_dangerous_streets" : get_most_dangerous_streets(sorted_map),
        "crime_type_count" : crime_type_dict,
        "event_time_count" : crime_time_dict
        }
    return response

application = Application([CrimeService],
tns='spyne.examples.crime',
in_protocol=HttpRpc(validator='soft'),
out_protocol=JsonDocument()
)

def get_most_dangerous_streets(sorted_map):
    return_arr =[sorted_map[0][0], sorted_map[1][0], sorted_map[2][0]]

    return return_arr


if __name__ == '__main__':
    # You can use any Wsgi server. Here, we chose
    # Python's built-in wsgi server but you're not
    # supposed to use it in production.
    from wsgiref.simple_server import make_server
    wsgi_app = WsgiApplication(application)
    server = make_server('0.0.0.0', 8000, wsgi_app)
    server.serve_forever()