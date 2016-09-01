# -*- coding: UTF-8 -*- 

##buoySelFields ={'Wind Speed and Gusts': ['wind.vmspd', 'wind.maxspd'],
##                'Air Temperature and Humidity': ['air.tempmean','air.humidmean'],
##                'Sea Temperature and Salinity': ['sea_water.meantemp','awac_sensors.temperature',
##                                                 'sea_water.meansalin'],
##                'Waves': ['awac_waves.wave_height','awac_waves.wave_height_max','awac_waves.mean_period'],
##                'D.O., Chl-a and Sea Temperature': ['sea_water.chlorophile','sea_water.meantemp'],
##                'Air and Sea Temperatures': ['air.tempmean','sea_water.meantemp','awac_sensors.temperature'],
##                'Compass and Wind': [],
##                'PAR, D.O. and Chl-a': []}

buoySelDesc = ['Wind Speed and Gusts',
               'Air Temperature and Humidity',
               'Sea Temperature and Salinity',
               'Waves',
               'D.O., Chl-a and Sea Temperature',
               'Air and Sea Temperatures',
               'Compass and Wind',
               'PAR, D.O. and Chl-a']

buoyDelDBFields = [['wind.vmspd', 'wind.maxspd'],
                   ['air.tempmean','air.humidmean'],
                   ['sea_water.meantemp','awac_sensors.temperature','sea_water.meansalin'],
                   ['awac_waves.wave_height','awac_waves.wave_height_max','awac_waves.mean_period'],
                   ['oxygen4835.concentrationmean','sea_water.chlorophile','sea_water.meantemp'],
                   ['air.tempmean','sea_water.meantemp','awac_sensors.temperature'],
                   ['compass.dirmean','compass.rollmean','compass.pitchmean','wind.vmspd','wind.maxspd',],
                   ['par.par','oxygen4835.concentrationmean','sea_water.chlorophile']]

buoySelFields = dict(zip(buoySelDesc, buoyDelDBFields))

buoyAxis = [['left','left'],
            ['left','right'],
            ['left','left','right'],
            ['left','left','right'],
            ['left','left','right'],
            ['left','left','left'],
            ['left','left','left','right','right'],
            ['left','right','right']]

buoySelAxis = dict(zip(buoySelDesc, buoyAxis))

buoyColorStyle = [['b-','r-'],
                  ['r-','b-'],
                  ['r-','r--','g-'],
                  ['b-','r-','g-'],
                  ['b-','g-','r-'],
                  ['r-','r--','r.'],
                  ['g-','g--','g.','b-','r-'],
                  ['r-x','b-x','g-x']]

buoySelColorStyle = dict(zip(buoySelDesc, buoyColorStyle))

buoyDBFields = ['wind.vmspd',
                'wind.maxspd',
                'air.tempmean',
                'air.humidmean',
                'sea_water.meantemp',
                'awac_sensors.temperature',
                'sea_water.meansalin',
                'awac_waves.wave_height',
                'awac_waves.wave_height_max',
                'awac_waves.mean_period',
                'sea_water.chlorophile',
                'compass.dirmean',
                'compass.rollmean',
                'compass.pitchmean',
                'oxygen4835.concentrationmean',
                'par.par']

buoyFieldsDesc = ['Mean Wind Speed',
                  'Gust Wind Speed',
                  'Air Temperature',
                  'Air Humidity',
                  'Sea Temperature (3m)',
                  'Sea Temperature (bottom)',
                  'Sea Salinity (3m)',
                  'Waves mean height',
                  'Waves max. eight',
                  'Waves mean period',
                  'Chl-a (3m)',
                  'Heading',
                  'Roll',
                  'Pitch',
                  'Dissolved Oxygen',
                  'PAR']

fieldDict = dict(zip(buoyDBFields, buoyFieldsDesc))

buoyFieldsUnit = ['m/s',
                  'm/s',
                  '$^0$C',
                  '%',
                  '$^0$C',
                  '$^0$C',
                  '',
                  'm',
                  'm',
                  's',
                  '$\mu$g/l',
                  '$^0$',
                  '$^0$',
                  '$^0$',
                  'mmol',
                  '$\mu$mol/sm']

buoyYAxisLabel = ['Speed',
                  'Speed',
                  'Temperature',
                  'Humidity',
                  'Temperature',
                  'Temperature',
                  'Salinity',
                  'Height',
                  'Height',
                  'Period',
                  'Concentration',
                  'Degrees',
                  'Degrees',
                  'Degrees',
                  'Concentration',
                  'PAR']

yLabDict = dict(zip(buoyDBFields, buoyYAxisLabel))    
yLabUnit = dict(zip(buoyDBFields, buoyFieldsUnit))    

def get_buoyparam(selectPlot):

    fields = buoySelFields[selectPlot]
    tables = [(lambda i: fields[i].split('.')[0])(i) for i in range(len(fields))]
    tables = list(set(tables))

    fieldDesc = [fieldDict[x] for x in fields]

    yLab = [yLabDict[x] + ' [' + yLabUnit[x] + ']' for x in fields]
    yLab = [w.replace(' []', '') for w in yLab]

    axis = buoySelAxis[selectPlot]

    colorStyle = buoySelColorStyle[selectPlot]    
       
    return (fields,tables,fieldDesc,yLab,axis,colorStyle)

#(fields,tables,ylabel) = get_buoyparam('Sea Temperature and Salinity')
