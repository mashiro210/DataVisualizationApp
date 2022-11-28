# Author: Mashiro
# Last update: 2022/10/12
# Description: module for getting data from InfluxDB cloud

# load molues
from datetime import datetime
from dateutil.tz import gettz

import pandas as pd
import influxdb_client

# define functions for converting timezone

def convertTimeZoneFromUTC(timestampUTC, timeZone = 'Asia/Tokyo'):
    convertedDatetime = timestampUTC.astimezone(gettz(timeZone))
    convertedTimestamp = datetime.strftime(convertedDatetime, '%Y-%m-%d %H:%M')

    return convertedTimestamp

def convertTimeZoneToUTC(timestamp):
    convertedDatetime = timestamp.astimezone(gettz('UTC'))
    convertedTimestamp = datetime.strftime(convertedDatetime, '%Y-%m-%d %H:%M')

    return convertedTimestamp

# define function for generating params

def generateParams(startDate, startHour, startMin, stopDate, stopHour, stopMin,
                   token = "t8fA0ToMKRTTj4qgcSpHzaknTARp8l9lONCFQiysVxzRwMsIaLrnHV_rTgUO3S4kz0nAq6fsSKH4SElOZN559w==",
                   org = "mashiro.jst.midori@gmail.com",
                   url = "https://europe-west1-1.gcp.cloud2.influxdata.com",
                   bucket = "kumamoto_weather_station"):
    
    '''all args require str'''
    
    start = startDate + 'T' + startHour + ':' + startMin + ':00Z'
    start = datetime.strptime(start, '%Y-%m-%dT%H:%M:%SZ')
    start = datetime.strptime(convertTimeZoneToUTC(start), '%Y-%m-%d %H:%M')
    stop = stopDate + 'T' + stopHour + ':' + stopMin + ':00Z'
    stop = datetime.strptime(stop, '%Y-%m-%dT%H:%M:%SZ')
    stop = datetime.strptime(convertTimeZoneToUTC(stop), '%Y-%m-%d %H:%M')
    
    params = dict(token = token,
                  org = org,
                  url = url,
                  bucket = bucket,
                  start = start,
                  stop = stop)
    
    return params

# define function for getting data from cloud

def getData(params):
    
    # API setting
    client = influxdb_client.InfluxDBClient(url = params['url'],
                                            org = params['org'],
                                            token = params['token'])
    
    queryAPI = client.query_api()
    
    # query setting at InfluxDB side
    query = '''
            from(bucket: _bucket)
                |> range(start: _start, stop: _stop)
                |> filter(fn: (r) => r["_measurement"] == "sensor_data")
            '''
    
    # get data from InfluxDB Cloud via API
    tables = queryAPI.query(query = query, org = params['org'],
                            params = {'_bucket': params['bucket'],
                                    '_start': params['start'],
                                    '_stop': params['stop']})

    # convert data to Pandas dataframe
    df = pd.read_json(tables.to_json())

    # extract target columns and convert timezone UTC to JST
    dfNow = df.filter(items = ['_time', '_field', '_value'], axis = 'columns')
    dfNow.columns = ['time_UTC', 'weatherVariable', 'value']
    dfNow['time_JST'] = dfNow['time_UTC'].map(convertTimeZoneFromUTC) # add new column on dataframe
    
    return dfNow