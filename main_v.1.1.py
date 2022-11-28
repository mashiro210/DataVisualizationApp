# Author: Mashiro
# Last update: 2022/11/28
# Description: application for visualizing data collected by IoT sensors

# load modules
import datetime
import time

import flet
from flet import (dropdown, Page, Dropdown,
                  ElevatedButton, Row, Image,
                  Text, UserControl, icons,
                  FilePickerResultEvent, Column, FilePicker)

# load my modules
import getDataFromInfluxDBCloud
import visualize

# drop down menues
class ddMenu(UserControl):
    def build(self):
    
        today = datetime.date.today()
        self.dateList = [dropdown.Option(str(today))]

        for i in range(1, 30):
            date = str(today - datetime.timedelta(days = i))
            self.dateList.append(dropdown.Option(date))

    
        weatherVariables = ['wind_direction', 'wind_speed', 'TSR',
                            'rain_snow', 'pressure', 'PM10', 'PM2_5',
                            'wind_direction_angle', 'CO2', 'rain_gauge',
                            'HUM', 'illumination', 'wind_speed_level', 'TEM']
        
        self.ddStartDate = Dropdown(label = 'Start Date',
                                    options = list(reversed(self.dateList)),
                                    width = 300)
        
        self.ddStartHour = Dropdown(label = 'Hour',
                                    options = [dropdown.Option(j) for j in
                                               ['0' + str(i) if len(str(i)) == 1
                                                else str(i) for i in range(0, 24)]])
        
        self.ddStartMin = Dropdown(label = 'Min',
                                   options = [dropdown.Option(j) for j in
                                              ['0' + str(i) if len(str(i)) == 1
                                               else str(i) for i in range(0, 60)]])
        
        self.ddEndDate = Dropdown(label = 'End Date', options = self.dateList)
        
        self.ddEndHour = Dropdown(label = 'Hour',
                                  options = [dropdown.Option(j) for j in
                                             ['0' + str(i) if len(str(i)) == 1
                                              else str(i) for i in range(0, 24)]])
        
        self.ddEndMin = Dropdown(label = 'Min',
                                 options = [dropdown.Option(j) for j in
                                            ['0' + str(i) if len(str(i)) == 1
                                             else str(i) for i in range(0, 60)]])
        
        self.ddWeatherVariables = Dropdown(label = 'Weather Variables',
                                           options = [dropdown.Option(i) for i in weatherVariables])
        
        self.ddVisualize = Dropdown(label = 'Select format',
                                    options = [dropdown.Option('Raw Data'),
                                               dropdown.Option('Figure')])
        
        duration = ['2w', '1w',
                    '3d', '2d', '1d',
                    '12h', '6h', '3h', '2h', '1h',
                    '30m']
        
        self.ddSmooth = Dropdown(label = 'option',
                                 options = [dropdown.Option(i) for i in duration])
        
        return Column([Row(controls = [self.ddStartDate, self.ddStartHour, self.ddStartMin]),
                       Row(controls = [self.ddEndDate, self.ddEndHour, self.ddEndMin]),
                       Row(controls = [self.ddWeatherVariables, self.ddVisualize, self.ddSmooth])])


def main(page: Page):
    
    formatHist = []
    userRequestedParam = ddMenu()


    def saveFileResult(e: FilePickerResultEvent):
        saveFilePath.value = e.path if e.path else 'File saving was cancelled!'
        saveFilePath.update()

    
    def execute(e):

        # check blanks are filled
        if isinstance(userRequestedParam.ddVisualize.value, str):
            if userRequestedParam.ddVisualize.value == 'Raw Data':
                filled = (isinstance(userRequestedParam.ddStartDate.value, str)
                          and isinstance(userRequestedParam.ddStartHour.value, str)
                          and isinstance(userRequestedParam.ddStartMin.value, str)
                          and isinstance(userRequestedParam.ddEndDate.value, str)
                          and isinstance(userRequestedParam.ddEndHour.value, str)
                          and isinstance(userRequestedParam.ddEndMin.value, str))

            elif userRequestedParam.ddVisualize.value == 'Figure':
                filled = (isinstance(userRequestedParam.ddStartDate.value, str)
                          and isinstance(userRequestedParam.ddStartHour.value, str)
                          and isinstance(userRequestedParam.ddStartMin.value, str)
                          and isinstance(userRequestedParam.ddEndDate.value, str)
                          and isinstance(userRequestedParam.ddEndHour.value, str)
                          and isinstance(userRequestedParam.ddEndMin.value, str)
                          and isinstance(userRequestedParam.ddWeatherVariables.value, str))

        else:
            filled = False
        
        # after filled check
        if filled:
            status.value = 'Getting data from cloud server' ; status.update()
            
            requestParamForInflux = getDataFromInfluxDBCloud.generateParams(startDate = userRequestedParam.ddStartDate.value,
                                                                            startHour = userRequestedParam.ddStartHour.value,
                                                                            startMin = userRequestedParam.ddStartMin.value,
                                                                            stopDate = userRequestedParam.ddEndDate.value,
                                                                            stopHour = userRequestedParam.ddEndHour.value,
                                                                            stopMin = userRequestedParam.ddEndMin.value)
            # check how many times execute botton clicked
            if execBotton.data > 1:
                if lastRequestParamForInflux == requestParamForInflux:
                    sensorData = getDataFromInfluxDBCloud.getData(lastRequestParamForInflux)
                else:
                    sensorData = getDataFromInfluxDBCloud.getData(requestParamForInflux)

            else:
                sensorData = getDataFromInfluxDBCloud.getData(requestParamForInflux)
                lastRequestParamForInflux = requestParamForInflux
            
            if userRequestedParam.ddVisualize.value == 'Raw Data':
                formatHist.append('R')
                status.value = 'Click Save file botton and Enter file name' ; status.update()
                
                while saveFilePath.value is None:
                    time.sleep(0.25)
                
                if saveFilePath.value[-4:] != '.csv':
                    saveFilePath.value = saveFilePath.value + '.csv'
                
                sensorData.to_csv(saveFilePath.value, index = False)
                
                status.value = 'File saving was successfully done!' ; status.update()
                saveFilePath.value = '' ; saveFilePath.update()

            elif userRequestedParam.ddVisualize.value == 'Figure':
                formatHist.append('F')
                status.value = 'Now visualizing' ; status.update()
                selectedVariable = userRequestedParam.ddWeatherVariables.value
                sensorDataTemp = sensorData.query('weatherVariable == @selectedVariable')
                if isinstance(userRequestedParam.ddSmooth.value, str):
                    sensorDataTemp = visualize.calcSmoothedValue(df = sensorDataTemp,
                                                                 unit = userRequestedParam.ddSmooth.value)
                    plotData = visualize.drawPlot(x = sensorDataTemp.index, y = sensorDataTemp['value'],
                                                  weatherVariable =  userRequestedParam.ddWeatherVariables.value,
                                                  smoothed = userRequestedParam.ddSmooth.value)
                
                else:
                    plotData = visualize.drawPlot(x = sensorDataTemp['time_JST'], y = sensorDataTemp['value'],
                                                  weatherVariable =  userRequestedParam.ddWeatherVariables.value)
                
                if formatHist.count('F') == 1:
                    status.value = 'Done!' ; status.update()
                    plot = Image(src_base64 = plotData)
                    page.add(plot)
                else:
                    status.value = 'Done!' ; status.update()
                    page.controls[-1].src_base64 = plotData
                    page.update()
                
            else:
                pass
            
        else:
            status.value = 'Error: fill all blanks!'
        
        status.update()
        
    status = Text(size = 20, color = 'red', text_align = 'center')
    execBotton = ElevatedButton(text = 'Execute', on_click = execute, data = 0)
    saveFilePath = Text()
    saveFileDialog = FilePicker(on_result = saveFileResult)
    fileSaveBotton = ElevatedButton(text = 'Save file', icon = icons.SAVE,
                                    on_click = lambda _: saveFileDialog.save_file(),
                                    disabled = page.web)
    
    page.scroll = 'auto'
    
    page.add(userRequestedParam,
             Row(controls = [execBotton, fileSaveBotton, status]),
             Row(controls = [saveFileDialog, saveFilePath]))


flet.app(target = main)
