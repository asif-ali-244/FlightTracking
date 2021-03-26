import requests
import json
import click
import datetime
import csv
import sys
from helper import get_airport, get_flights, getTime, print_table, get_filter,get_flight_status,get_airlines,find_airport

@click.group(invoke_without_command=True)
@click.pass_context
@click.option("-a","-dest","--arrivals", default=None, help="Destination Airport")
@click.option("-d","-src","--departures",default=None, help="Source Airport")
@click.option("-b","--date",default=None,help="Date")
@click.option("-t","--delta",default=12, type=int,help="Time Window in hours")
@click.option("--airline",default=None,help="Airline Name")
def cli(ctx,arrivals,departures,date,delta,airline):
    """
        Retrieve flights for a certain airport or between two airports which arrived/departed on the mentioned date
        within a given time interval.
    """
    if ctx.invoked_subcommand is None:
        date_from,date_to=getTime(date,delta)
        src=get_airport(departures) if departures!=None else None
        dest=get_airport(arrivals) if arrivals!=None else None
        header3=["From Time","To Time"]
        print_table([[date_from,date_to]],header3)
        header2=["ICAO","IATA","Name of Airport","City","State","Country"]
        if src!=None and dest==None:
            flights=get_flights(False,src[0][0],date_from,date_to)
            print_table(src,header2)
            click.echo(f"\nListing all departure flights from airport {src[0][2]}")
        elif src==None and dest!=None:
            flights=get_flights(True,dest[0][0],date_from,date_to)
            print_table(dest,header2)
            click.echo(f"\nListing all arrival flights to airport {dest[0][2]}")
        elif src!=None and dest!=None:
            flights=get_flights(False,src[0][0],date_from,date_to)
            flights=get_filter(flights,dest[0][0],dest[0][1])
            print_table(src,header2)
            print_table(dest,header2)
            click.echo(f"\nListing all flights from airport {src[0][2]} to airport {dest[0][2]}")
        else:
            click.echo("At least one arrival or departure airport required")
            sys.exit("Aborting!!!")
        if airline:
            flights=get_airlines(flights,airline)
            click.echo(f"via airline {airline}")
        
        header=["Flight Number","Airline","Status","Scheduled Time(UTC)","Scheduled Time(Local)","Terminal","Airport","ICAO","IATA"]
        print_table(flights,header)
        
        

@cli.command('flight')
@click.argument("flight_number")
@click.option("--date",default=None, help="Date of flight in %d/%m/%Y")
def flight_cli(flight_number,date):
    """
        Get Flight Status by using flight number and optional argument date
    """
    flight_stats=get_flight_status(flight_number,date)
    header=["Flight Number","Status","Airline","Arrival Airport","Arrival Time(UTC)","Arrival Time(Local)","Departure Airport","Departure Time(UTC)","Departure Time(Local)"]
    print_table(flight_stats,header)
    

@cli.command('search')
@click.argument("string")
def search_airports(string):
    """
        Search airport information using name, ICAO, or IATA by string input
    """
    data=find_airport(string)
    header=["ICAO","IATA","Name","City","Country Code"]
    print_table(data,header)

