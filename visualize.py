# Author: Mashiro
# Last update: 2022/11/07
# Description: module for visualizing

# load modules
import base64
from io import BytesIO

import matplotlib
matplotlib.use('svg')
import matplotlib.pyplot as plt
import pandas as pd

# define function for deciding unit
def decideUnit(x):
    
    if x == 'wind_direction_angle':
        return 'Degree'
    elif x == 'wind_speed':
        return 'm/s'
    elif x == 'TSR':
        return 'W/m^2'
    elif x == 'pressure':
        return 'hPa'
    elif x == 'PM10' or x == 'PM2_5':
        return 'µg/m^3'
    elif x == 'CO2':
        return 'ppm'
    elif x == 'rain_gauge':
        return 'mm'
    elif x == 'HUM':
        return '%RH'
    elif x == 'illumination':
        return 'Lux'
    elif x == 'wind_speed_level':
        return 'UnitLess'
    elif x == 'TEM':
        return 'Celsius_degree'
    elif x == 'rain_snow' or x == 'wind_direction_angle':
        return 'nounit'

# define function for drawing plot

def drawPlot(x, y, weatherVariable, smoothed = None):
    plt.rcParams["figure.subplot.bottom"] = 0.20
    # draw plot
    plt.plot(x, y)
    
    if smoothed is not None:
        plt.title('Sensor Data; {}'.format(weatherVariable)
                  + ' ('
                  + 'smoothed: '
                  + smoothed
                  +')')
    else:
        plt.title('Sensor Data; {}'.format(weatherVariable)+ ' (raw)')
    plt.xlabel('Date')
    plt.xticks(rotation = 45)
    plt.ylabel(weatherVariable + ' (' + decideUnit(weatherVariable) + ')')

    ofs = BytesIO()
    plt.savefig(ofs, format = 'png')
    data = ofs.getvalue()
    plt.clf() ; plt.close()
    
    base64Data = base64.b64encode(data).decode()
    
    return base64Data

def drawPlot2(x, y, weatherVariable, smoothed = None):
    fig, ax = plt.subplots()
    
    # draw plot
    ax.plot(x, y)
    
    if smoothed is not None:
        ax.set_title('Sensor Data; {}'.format(weatherVariable)
                  + ' ('
                  + 'smoothed: '
                  + smoothed
                  +')')
    else:
        ax.set_title('Sensor Data; {}'.format(weatherVariable)+ ' (raw)')
    ax.set_xlabel('Date')
    fig.autofmt_xdate(rotation = 45)
    ax.set_ylabel(weatherVariable + ' (' + decideUnit(weatherVariable) + ')')
    
    return fig

# define function for calculating smoothed average value

def calcSmoothedValue(df, unit):
    durationDict = {'2w': '2W', '1w': '1W',
                    '3d': '3D', '2d': '2D', '1d': '1D',
                    '12h': '12H', '6h': '6H', '3h': '3H', '2h': '2H', '1h': '1H',
                    '30m': '30T'}
    
    value = df.filter(items = ['value'])
    value = value.astype(float)
    value.index = pd.to_datetime(df['time_JST'])
    
    return value.resample(rule = durationDict[unit]).mean()