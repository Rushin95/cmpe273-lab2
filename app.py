import datetime
import logging
import requests
from spyne.application import Application
from spyne.decorator import srpc
from spyne.protocol.http import HttpRpc
from spyne.protocol.json import JsonDocument
from spyne.server.wsgi import WsgiApplication
from spyne.service import ServiceBase


class Crime(ServiceBase):
    @srpc(float, float, float, _returns=unicode)
    def checkcrime(lat, lon, radius):

        # resp_json = requests.get("https://api.spotcrime.com/crimes.json", params={"lat":lat, "lon":lon,"radius":radius,"key":"."})
        # resp_json = requests.get("https://api.spotcrime.com/crimes.json", params={"lat":37.334164,"lon": -121.884301, "radius": 0.02, "key":"."})
        # print resp_json

        url = "https://api.spotcrime.com/crimes.json"
        payload = {'lat': lat, 'lon': lon, 'radius': radius, 'key': '.'}
        # GET with params in URL
        r = requests.get(url, params=payload)
        data = r.json()

#count of crimes

        #yield len(data["crimes"])
        #yield data

#for fetching street names
        dict = {}
        for n in range(len(data["crimes"])):
            address = data["crimes"][n]["address"]
            streetnames=address.split("&")

            for streetname in streetnames:
                newstreetname = ""
                templist = streetname.split(" ")
                for temp in templist:
                    if temp.isnumeric() or temp == "BLOCK" or temp == "OF":
                        continue
                    else:
                        newstreetname = newstreetname + " " + temp

                newstreetname =newstreetname.lstrip()
                if not dict.has_key(newstreetname):
                    dict[newstreetname] = 1
                else:
                    dict[newstreetname] = dict[newstreetname] + 1
        sorted_dict=sorted(dict.items(), key=lambda x: (-x[1], x[0]))
        top3_streets = []
        count = 0;
        for k,v in sorted_dict:
           if (count > 2):
               break
           top3_streets.append(k)
           count = count + 1
        # yield top3_streets



#FOR THE COUNT OF CRIME TYPES
        crimetypes = {}
        for n in range(len(data["crimes"])):
            typename = data["crimes"][n]["type"]
            if not crimetypes.has_key(typename):
                crimetypes[typename] = 1
            else:
                crimetypes[typename] += 1
        #yield crimetypes


#FOR COUNTING CRIMES ACCORDING TO TIME PERIOD

        t1 = 0
        t2 = 0
        t3 = 0
        t4 = 0
        t5 = 0
        t6 = 0
        t7 = 0
        t8 = 0

        d1 = datetime.datetime.strptime("12:00 AM", "%I:%M %p").time()
        d2 = datetime.datetime.strptime("03:00 AM", "%I:%M %p").time()# 3 am
        d3 = datetime.datetime.strptime("06:00 AM", "%I:%M %p").time()# 6 am
        d4 = datetime.datetime.strptime("09:00 AM", "%I:%M %p").time()# 9 am
        d5 = datetime.datetime.strptime("12:00 PM", "%I:%M %p").time()# 12 pm
        d6 = datetime.datetime.strptime("03:00 PM", "%I:%M %p").time()# 3 pm
        d7 = datetime.datetime.strptime("06:00 PM", "%I:%M %p").time()# 6 pm
        d8 = datetime.datetime.strptime("09:00 PM", "%I:%M %p").time()# 9 pm

        for n in range(len(data["crimes"])):
            date_str = data["crimes"][n]["date"]
            d = datetime.datetime.strptime(date_str, "%m/%d/%y %I:%M %p").time()
            if d1 < d <= d2:
                t1 += 1
            elif d2 < d <= d3:
                t2 += 1
            elif d3 < d <= d4:
                t3 += 1
            elif d4 < d <= d5:
                t4 += 1
            elif d5 < d <= d6:
                t5 += 1
            elif d6 < d <= d7:
                t6 += 1
            elif d7 < d <= d8:
                t7 += 1
            elif d8 < d or d == d1:
                t8 += 1

        result={
        "total_crime" : len(data["crimes"]),
        "the_most_dangerous_streets" : top3_streets,
        "crime_type_count" : crimetypes,
        "event_time_count" :{
            "12:01am-3am" : t1,
            "3:01am-6am" : t2,
            "6:01am-9am" : t3,
            "9:01am-12noon" : t4,
            "12:01pm-3pm" : t5,
            "3:01pm-6pm" : t6,
            "6:01pm-9pm" : t7,
            "9:01pm-12midnight" : t8
                            }
                }

        return result

if __name__ == '__main__':
    # Python daemon boilerplate
    from wsgiref.simple_server import make_server

    logging.basicConfig(level=logging.DEBUG)

    application = Application([Crime], 'spyne.model.Crime',
                              in_protocol=HttpRpc(validator='soft'),
                              out_protocol=JsonDocument(ignore_wrappers=True),
                              )

    wsgi_application = WsgiApplication(application)

    server = make_server('127.0.0.1', 5000, wsgi_application)

    logging.info("listening to http://127.0.0.1:5000")
    logging.info("wsdl is at: http://localhost:5000/?wsdl")

server.serve_forever()
