import requests
import os
import datetime
import json
import click
from difflib import get_close_matches
from prettytable import PrettyTable
baseUrl="https://aerodatabox.p.rapidapi.com"
rapidHost="aerodatabox.p.rapidapi.com"
KEY=os.environ.get("AERO_KEY")
   

def get_airport(identity):
    #open json file
    file=open("airports.json", encoding="utf-8")
    airports=json.load(file)
    # If identity is a IATA Code    
    if len(identity)==3:
        identity=identity.upper()
        for value,key in airports.items():
            if key["iata"]==identity:
                return [[key["icao"],key["iata"],key["name"],key["city"],key["state"],key["country"]]]

    # If identity is a ICAO Code
    elif len(identity)==4:
        identity=identity.upper()
        key=airports[identity]
        return [[key["icao"],key["iata"],key["name"],key["city"],key["state"],key["country"]]]
    # If identity is airport name    
    else:
        identity=identity.title()
        all_names=[]    # Store all airport names to use in difflib in case if it's misspelled
        for value,key in airports.items():
            all_names.append(key["name"])
            if key["name"]==identity:
                return [[key["icao"],key["iata"],key["name"],key["city"],key["state"],key["country"]]]
        #If airport name is misspelled find matches from all_names using difflib's get_close_matches
        matches=get_close_matches(identity, all_names)
        if matches:    
            click.echo("Did you mean?.....")
            for x in matches:
                click.echo(x)
            click.echo(f"Using the best match: {matches[0]}")
            if click.confirm('Do you want to continue?', default=True):
                return get_airport(matches[0])
            else:
                return None
        else:
            click.echo(f"Couldn't find any match for {identity}!!!")
            return None

def get_response(icao,begin,end):
    url=baseUrl+f"/flights/airports/icao/{icao}/{begin}/{end}"
    query={"withLeg":"true","withCancelled":"true","withCodeshared":"true","withCargo":"true","withPrivate":"true"}
    headers={'x-rapidapi-key':KEY,'x-rapidapi-host': rapidHost}
    response=requests.get(url,params=query,headers=headers)
    if response:
        return response.json()
    else:
        print(f"Connection Error! {response.status_code}")
def get_flights(flag,identity,begin,end):
    response=get_response(identity,begin,end)
    key="arrivals" if flag==True else "departures"
    key2="arrival" if flag==False else "departure"
    key3="arrival" if flag==True else "departure"
    table=[]
    for row in response[key]:
        flight=row["number"]
        airline=row["airline"]["name"]
        status=row["status"]
        time_utc=row[key3].get("scheduledTimeUtc","-")
        time_local=row[key3].get("scheduledTimeLocal","-")
        terminal=row[key3].get("terminal","-")
        airport=row[key2]["airport"]["name"]
        icao=row[key2]["airport"].get("icao","-")
        iata=row[key2]["airport"].get("iata","-")
        table.append([flight,airline,status,time_utc,time_local,terminal,airport,icao,iata])
    return table

#Helper function to print the table
def print_table(data,header):
    x=PrettyTable()
    x.field_names=header
    x.add_rows(data)
    click.echo(x)

#Helper function to change the time format
def getTime(begin,end):
    if begin==None:
        begin=datetime.datetime.utcnow()
    else:
        if len(begin.split())==2:
            begin=datetime.datetime.strptime(begin,"%d/%m/%Y %H:%M")
        else:
            begin=datetime.datetime.strptime(begin,"%d/%m/%Y")
    end=datetime.timedelta(hours=end)+begin
    begin=begin.strftime("%Y-%m-%dT%H:%M")
    end=end.strftime("%Y-%m-%dT%H:%M")
    return begin,end

def get_filter(flights, icao,iata):
    new_table=[]
    icao=icao.upper() if icao!=None else "NaN"
    iata=iata.upper() if iata!=None else "NaN" 
    for row in flights:
        if row[-1]==iata or row[-2]==icao:
            new_table.append(row)
    return new_table

# Filter the flights according to airline
def get_airlines(flights, airline):
    new_table=[]
    if airline:
        for row in flights:
            if row[1]==airline:
                new_table.append(row)

    return new_table

# Get the flight status using flight number and date
def get_flight_status(flight,begin):
    if begin==None:
        begin=datetime.datetime.utcnow()
    else:
        begin=datetime.datetime.strptime(begin,"%d/%m/%Y")
    begin=begin.strftime("%Y-%m-%d")
    headers = {
    'x-rapidapi-key': KEY,
    'x-rapidapi-host': rapidHost
    }
    url=f"https://aerodatabox.p.rapidapi.com/flights/number/{flight}/{begin}"
    response=requests.get(url,headers=headers).json()
    data=[]
    for flight in response:
        airline=flight["airline"].get("name")
        arrival_airport=flight["arrival"].get("airport").get("name")
        arrival_time=flight["arrival"].get("scheduledTimeUtc")
        arrival_time_local=flight["arrival"].get("scheduledTimeLocal")
        depart_airport=flight["departure"].get("airport").get("name")
        depart_time=flight["departure"].get("scheduledTimeUtc")
        depart_time_local=flight["departure"].get("scheduledTimeLocal")
        status=flight["status"]
        number=flight["number"]
        data.append([number,status,airline,arrival_airport,arrival_time,arrival_time_local,depart_airport,depart_time,depart_time_local])
    return data

# Search airport information using input string
def find_airport(string):
    url = "https://aerodatabox.p.rapidapi.com/airports/search/term"
    querystring = {"q":string,"limit":"10"}
    headers = {
    'x-rapidapi-key': KEY,
    'x-rapidapi-host': rapidHost
    }
    response=requests.get(url,headers=headers,params=querystring)
    response=response.json()
    data=[]
    
    if response:
            
        for airport in response["items"]:
            icao=airport.get("icao","-")
            iata=airport.get("iata","-")
            name=airport.get("name","-")
            city=airport.get("municipalityName","-")
            country=airport.get("countryCode","-")
            data.append([icao,iata,name,city,country])

    return data






