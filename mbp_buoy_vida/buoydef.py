buoySelDesc = ['Wind Speed and Gusts',
               'Air Temperature and Humidity',
               'Sea Temperature and Salinity',
               'Waves',
               'Dissolved Oxygen and Temperature at Sea Bottom',
               'Air and Sea Temperatures',
               'Compass and Wind',
               'PAR and Dissolved Oxygen']

buoyDelDBFields = [['wind.vmspd', 'wind.maxspd'],
                   ['air.tempmean', 'air.humidmean'],
                   ['sea_water.meantemp', 'awac_sensors.temperature', 'sea_water.meansalin'],
                   ['awac_waves.wave_height', 'awac_waves.wave_height_max', 'awac_waves.mean_period'],
                   ['oxygen.concentrationmean', 'awac_sensors.temperature'],
                   ['air.tempmean', 'sea_water.meantemp', 'awac_sensors.temperature'],
                   ['compass.yaw', 'compass.roll', 'compass.pitch', 'wind.vmspd', 'wind.maxspd', ],
                   ['par.par', 'oxygen.concentrationmean']]

buoyDBWhereConds= [ "",
                   "",
                   "",
                   "",
                   "((device_id=1) OR (device_id IS NULL))",
                   "",
                   "",
                   "((device_id=1) OR (device_id IS NULL))"]

buoySelFields = dict(zip(buoySelDesc, buoyDelDBFields))

buoyAxis = [['left', 'left'],
            ['left', 'right'],
            ['left', 'left', 'right'],
            ['left', 'left', 'right'],
            ['left', 'right'],
            ['left', 'left', 'left'],
            ['left', 'left', 'left', 'right', 'right'],
            ['left', 'right']]

buoySelAxis = dict(zip(buoySelDesc, buoyAxis))

buoyColorStyle = [['b-', 'r-'],
                  ['r-', 'b-'],
                  ['r-', 'r--', 'g-'],
                  ['b-', 'r-', 'g-'],
                  ['b-', 'r-'],
                  ['r-', 'r--', 'r.'],
                  ['g-', 'g--', 'g.', 'b-', 'r-'],
                  ['r-x', 'b-x']]

buoySelColorStyle = dict(zip(buoySelDesc, buoyColorStyle))

buoyDBFields = ['wind.vmspd',
                'wind.vmdir',
                'wind.maxspd',
                'air.tempmean',
                'air.humidmean',
                'sea_water.meantemp',
                'awac_sensors.temperature',
                'sea_water.meansalin',
                'awac_waves.wave_height',
                'awac_waves.wave_height_max',
                'awac_waves.mean_period',
                'awac_waves.mean_direction',
                'sea_water.chlorophile',
                'compass.yaw',
                'compass.roll',
                'compass.pitch',
                'oxygen.concentrationmean',
                'par.par']

buoyFieldsDesc = ['Mean Wind Speed',
                  'Mean Wind Direction',
                  'Gust Wind Speed',
                  'Air Temperature',
                  'Air Humidity',
                  'Sea Temperature (3m)',
                  'Sea Temperature (bottom)',
                  'Sea Salinity (3m)',
                  'Waves mean height',
                  'Waves max height',
                  'Waves mean period',
                  'Waves mean direction',
                  'Chl-a (3m)',
                  'Yaw',
                  'Roll',
                  'Pitch',
                  'Dissolved Oxygen',
                  'PAR']

fieldDict = dict(zip(buoyDBFields, buoyFieldsDesc))
whereDict = dict(zip(buoySelDesc, buoyDBWhereConds))

buoyFieldsUnit = ['m/s',
                  '$^0$',
                  'm/s',
                  '$^0$C',
                  '%',
                  '$^0$C',
                  '$^0$C',
                  '',
                  'm',
                  'm',
                  's',
                  '',
                  '$\mu$g/l',
                  '$^0$',
                  '$^0$',
                  '$^0$',
                  'ml/l',
                  '$\mu$mol/sm']

buoyFieldsFactors = [1.0,
                     1.0,
                     1.0,
                     1.0,
                     1.0,
                     1.0,
                     1.0,
                     1.0,
                     1.0,
                     1.0,
                     1.0,
                     1.0,
                     1.0,
                     1.0,
                     1.0,
                     1.0,
                     22.3914,
                     1.0]

factorDict = dict(zip(buoyDBFields, buoyFieldsFactors))

buoyYAxisLabel = ['Speed',
                  'Direction',
                  'Speed',
                  'Temperature',
                  'Humidity',
                  'Temperature',
                  'Temperature',
                  'Salinity',
                  'Height',
                  'Height',
                  'Period',
                  'Direction',
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
    whereCond = whereDict[selectPlot]
    tables = [(lambda i: fields[i].split('.')[0])(i) for i in range(len(fields))]
    tables = list(set(tables))

    fieldDesc = [fieldDict[x] for x in fields]

    yLab = [yLabDict[x] + ' [' + yLabUnit[x] + ']' for x in fields]
    yLab = [w.replace(' []', '') for w in yLab]

    axis = buoySelAxis[selectPlot]

    colorStyle = buoySelColorStyle[selectPlot]

    fieldFactor = [factorDict[x] for x in fields]

    return (fields,tables,fieldDesc,yLab,axis,colorStyle,fieldFactor, whereCond)
