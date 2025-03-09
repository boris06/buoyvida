#!/usr/bin/env python3

import matplotlib
matplotlib.use('Agg')         # Force matplotlib to not use any Xwindows backend.

__DBG = False
if __DBG == True:
    import cgitb
    cgitb.enable()            # Enable detailed and formated exception stacktrace logging

from .buoydef import *
from .buoyvida import *
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cmx
# import string

from mbp_buoy_vida import config as DbConfig
dbConfig = DbConfig.DbConfig()

__all__ = ['vector']


def vector(selectHeights=None, startDateTime=None, endDateTime=None, scriptAbsPath='/'):
    global dbConfig
    all_heights = ['%d' % height for height in range(2,23)]
    def_heights = ['2', '5', '10', '15', '20']
    if selectHeights is None  or  startDateTime is None  or  endDateTime is None:
        endDateTime = datetime.today().strftime('%Y-%m-%dT%H:%M:%S')
        startDateTime = (datetime.today() - timedelta(days=2)).strftime('%Y-%m-%dT%H:%M:%S')
        heights = def_heights
    else:
        try:
            heights = selectHeights.split(',')
        except:
            heights = selectHeights

    start_date = startDateTime.replace('T', ' ')
    end_date = endDateTime.replace('T', ' ')
    cells = list(map(str, (np.asarray(list(map(int, heights))) - 2)))

    if (start_date < end_date):

        # make period list
        period_list = make_period_list(startDateTime, endDateTime)

        if (len(period_list) <= 7*24*2):

            # get wind and waves data
            fields=['wind.vmspd', 'wind.vmdir', 'awac_waves.wave_height', 'awac_waves.mean_direction']
            tables=['wind', 'awac_waves']
            # table
            # for x in fields:
            #     fieldDict[x]
            # ??? fieldDesc = [fieldDict[x] for x in fields]
            # Damir
            # fieldDesc = string.join(fields)
            # Boris
            fieldDesc = [fieldDict[x] for x in fields]

            (nseries,series)=get_buoy_data(dbConfig, fields, tables, period_list)
            uwind = series[:,0] * np.cos((270. - series[:,1])*np.pi/180.)
            vwind = series[:,0] * np.sin((270. - series[:,1])*np.pi/180.)
            uwaves = series[:,2] * np.cos((270. - series[:,3])*np.pi/180.)
            vwaves = series[:,2] * np.sin((270. - series[:,3])*np.pi/180.)

            # get sea currents data
            (current_E,current_N) = get_buoy_currents(dbConfig, period_list,cells)

            # plot wind vectors
            C = ['r']
            desc = ['Wind']
            keytext = "Wind Speed %s m/s"
            wind_encoded = make_vector_plot(period_list,uwind,vwind,C,desc,6,keytext,'','vertical',0.5,0.9,None)

            # plot waves vectors
            C = ['b']
            desc = ['Sea waves']
            keytext = "Waves height %s m"
            waves_encoded = make_vector_plot(period_list,uwaves,vwaves,C,desc,0.5,keytext,'','vertical',0.5,0.9,None)

            # plot buoy currents
            uvec = np.vstack(current_E[0])
            uvec = uvec.T
            for i in range(1,len(current_E)):
                uvec = np.vstack((uvec,current_E[i].T))
            vvec = np.vstack(current_N[0])
            vvec = vvec.T
            for i in range(1,len(current_N)):
                vvec = np.vstack((vvec,current_N[i].T))
            desc = ['%s' % height for height in heights]
            fieldDescCurr = ['Curr%s (%s m)' % (direction,height) for height in heights for direction in ['E','N']]
            values = range(len(uvec))
            jet = cm = plt.get_cmap('jet')
            cNorm  = colors.Normalize(vmin=0, vmax=values[-1])
            scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=jet)
            colorVal = []
            for idx in range(len(uvec)):
                for j in range(len(period_list)):
                    colorVal.append(scalarMap.to_rgba(values[idx]))
            keytext = "Sea Current Speed %s cm/s"
            currents_encoded = make_vector_plot(period_list,uvec,vvec,colorVal,desc,30,keytext,'Sea currents at height [m] above sea bottom','horizontal',0.55,0.96,None)

            error = False

        else:

            errmsg = 'Period length must be shorter than 7 days!'
            error = True

    else:

        errmsg = 'Start date and time must be before end date and time!'
        error = True

    rvBuf = ""
    rvBuf += "<!DOCTYPE html>"
    rvBuf += "<html>"

    rvBuf += """
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<title>Buoy vector multi-plot</title>
<link href="//fonts.googleapis.com/css?family=Open+Sans:300,300italic,400,400italic,600,600italic,700,700italic,800,800italic" rel="stylesheet" type="text/css">
<style>
  body {
    font-family: "Open Sans";
  }
  h2 {
    text-align: center;
  }
  table {
    border-collapse: collapse;
    border: 1px solid black;
  }
  table tbody {
    font-size: 0.7em;
  }
  tbody tr:nth-child(odd) {
    background-color: lightgray;bl
  }
</style>
</head>
"""

    rvBuf += '<body>'
    rvBuf += '<form method="get" name="main" id="main" action="%s/vector">' % (scriptAbsPath)
    rvBuf += '<h2>Wind, waves and sea currents from the oceanographic buoy Vida</h2>'
    rvBuf += '<hr>'
    rvBuf += '<label for="startDateTime">Start date and time:</label>'
    rvBuf += '<input type="datetime-local" name="startDateTime" value=%s>' % startDateTime
    rvBuf += '&nbsp;'
    rvBuf += '&nbsp;'
    rvBuf += '<label for="endDateTime">End date and time:</label>'
    rvBuf += '<input type="datetime-local" name="endDateTime" value=%s>' % endDateTime
    rvBuf += '&nbsp;'
    rvBuf += '&nbsp;'
    all_heights_m = ['%s m' % height for height in all_heights]
    rvBuf += '<label for="selectHeights">Select heights:</label>'
    rvBuf += '<select multiple name="selectHeights" id="selectHeights" size="3" title="Hold down the Ctrl (windows) / Command (Mac) button to select multiple options.">'
    for i in range(len(all_heights)):
        if (all_heights[i] in heights):
            rvBuf += '   <option value="%s" selected="selected">%s</option>' % (all_heights[i],all_heights_m[i])
        else:
            rvBuf += '   <option value="%s">%s</option>' % (all_heights[i],all_heights_m[i])
    rvBuf += '</select>'
    rvBuf += '&nbsp;'
    rvBuf += '&nbsp;'
    rvBuf += '<input type="submit" value="Go!" />'
    rvBuf += '</form>'
    rvBuf += '&nbsp;'
    rvBuf += '&nbsp;'
    rvBuf += '<form method="get" action="%s/vector2excel" style="display:inline;">' % (scriptAbsPath)
    rvBuf += '<input type="hidden" name="startDateTime" value="%s">' % startDateTime
    rvBuf += '<input type="hidden" name="endDateTime" value="%s">' % endDateTime
    rvBuf += '<input type="hidden" name="selectHeights" value="%s">' % ",".join(heights)
    rvBuf += '<button type="submit">Download to Excel!</button>'
    rvBuf += '</form>'
    rvBuf += '&nbsp;'
    rvBuf += '&nbsp;'
    rvBuf += '<form style="display:inline;">'
    rvBuf += '<button onclick="myPrint()">Print this page</button>'
    print
    rvBuf += '<script>'
    rvBuf += 'function myPrint() {'
    rvBuf += '    window.print();'
    rvBuf += '}'
    rvBuf += '</script>'
    rvBuf += '</form>'
    rvBuf += '&nbsp;'
    rvBuf += '&nbsp;'
    rvBuf += '<form style="display:inline;">'
    rvBuf += '<button onclick="resetHeights()">Reset heights</button>'
    rvBuf += '<script>'
    rvBuf += 'function resetHeights() {'
    rvBuf += '  var el = document.getElementById("selectHeights");'
    rvBuf += '  for (var i = 0; i < el.length; i++) {'
    rvBuf += '     document.getElementById("selectHeights")[i].selected = false;'
    rvBuf += '  }'
    rvBuf += '  var value = ["2", "5", "10", "15", "20"];'
    rvBuf += '  for (var j = 0; j < value.length; j++) {'
    rvBuf += '     for (var i = 0; i < el.length; i++) {'
    rvBuf += '        if (el[i].value == value[j]) {'
    rvBuf += '           document.getElementById("selectHeights")[i].selected = true;'
    rvBuf += '        }'
    rvBuf += '     }'
    rvBuf += '  }'
    rvBuf += '}'
    rvBuf += '</script>'
    rvBuf += '</form>'
    print

    if (error):
        rvBuf += '<h2 style="color:red">%s</h2>' % errmsg
    else:
        rvBuf += '<hr>'
        rvBuf += '<div align="center"><img src=\"data:image/png;base64,' + wind_encoded + "\" /></div>"
        rvBuf += '<div align="center"><img src=\"data:image/png;base64,' + waves_encoded + "\" /></div>"
        rvBuf += '<div align="center"><img src=\"data:image/png;base64,' + currents_encoded + "\" /></div>"
        rvBuf += '<hr>'
        rvBuf += '<br>'
        rvBuf += '<table border="1" style="width:90%" align="center">'
        rvBuf += '  <tr>'
        rvBuf += '    <th>Date and time</th>'
        for i in range(nseries):
            rvBuf += '    <th>%s</th>' % fieldDesc[i]
        for i in range(len(fieldDescCurr)):
            rvBuf += '    <th>%s</th>' % fieldDescCurr[i]
        rvBuf += '  </tr>'
        for i in range(len(period_list)):
            rvBuf += '<tr>'
            rvBuf += '<td>%s</td>' % period_list[i].strftime('%Y-%m-%d %H:%M')
            for j in range(nseries):
                rvBuf += '<td align="right">%9.2f</td>' % series[i,j]
            for j in range(len(desc)):
                rvBuf += '<td align="right">%9.2f</td>' % uvec[j,i]
                rvBuf += '<td align="right">%9.2f</td>' % vvec[j,i]
            rvBuf += '</tr>'
        rvBuf += '</table>'
    rvBuf += '</body>'
    rvBuf += '</html>'
    return rvBuf
