#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import matplotlib
matplotlib.use('Agg')         # Force matplotlib to not use any Xwindows backend.

__DBG = False
if __DBG == True:
    import cgitb
    cgitb.enable()            # Enable detailed and formated exception stacktrace logging

from datetime import datetime, timedelta

from .buoydef import *
from .buoyvida import *

from mbp_buoy_vida import config as DbConfig
dbConfig = DbConfig.DbConfig()

__all__ = ['scalar']

def scalar(selectPlot=None, startDateTime=None, endDateTime=None, scriptAbsPath='/'):
    global dbConfig

    # cgitb.enable()

    rvBuf = ""

    if selectPlot is None  or  startDateTime is None  or  endDateTime is None:
        selectPlot = "Wind Speed and Gusts"
        endDateTime = datetime.today().strftime('%Y-%m-%dT%H:%M:%S')
        startDateTime = (datetime.today() - timedelta(days=2)).strftime('%Y-%m-%dT%H:%M:%S')

    start_date = startDateTime.replace('T', ' ')
    end_date = endDateTime.replace('T', ' ')

    if (start_date < end_date):

        # make period list
        period_list = make_period_list(startDateTime,endDateTime)

        if (len(period_list) <= 7*24*2):

            # get buoy database parameters
            (fields,tables,fieldDesc,yLab,axis,colorStyle,fieldFactor, whereCond) = get_buoyparam(selectPlot)

            # get buoy scalar data
            (nseries,series) = get_buoy_data(dbConfig, fields,tables,period_list, whereCond)

            # plot scalar data
            encoded = make_scalar_plot(period_list,series,fieldDesc,yLab,axis,colorStyle,fieldFactor)

            error = False

        else:

            errmsg = 'Period length must be shorter than 7 days!'
            error = True

    else:

        errmsg = 'Start date and time must be before end date and time!'
        error = True

    rvBuf += "<!DOCTYPE html>"
    rvBuf += "<html>"

    rvBuf += """
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<title>Buoy scalar multi-plot</title>
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
    rvBuf += '<form method="get" action="%s/scalar">' % (scriptAbsPath)
    rvBuf += '<h2>Data from the oceanographic buoy Vida</h2>'
    rvBuf += '<h2 style="color:blue">%s</h2>' % selectPlot
    rvBuf += '<hr>'
    rvBuf += '<label for="selectPlot">Select plot:</label>'
    rvBuf += '<select name="selectPlot" id="selectPlot">'
    for i in range(len(buoySelDesc)):
        if (buoySelDesc[i] == selectPlot):
            rvBuf += '  <option selected="selected">%s</option>' % buoySelDesc[i]
        else:
            rvBuf += '  <option>%s</option>' % buoySelDesc[i]
    rvBuf += '</select>'
    rvBuf += '&nbsp;'
    rvBuf += '&nbsp;'
    rvBuf += '<label for="startDateTime">Start date and time:</label>'
    rvBuf += '<input type="datetime-local" name="startDateTime" value=%s>' % startDateTime
    rvBuf += '&nbsp;'
    rvBuf += '&nbsp;'
    rvBuf += '<label for="endDateTime">End date and time:</label>'
    rvBuf += '<input type="datetime-local" name="endDateTime" value=%s>' % endDateTime
    rvBuf += '&nbsp;'
    rvBuf += '&nbsp;'
    rvBuf += '<input type="submit" value="Go!" />'
    rvBuf += '&nbsp;'
    rvBuf += '&nbsp;'
    rvBuf += '</form>'
    rvBuf += '<form method="get" action="%s/scalar2excel" style="display:inline;">' % (scriptAbsPath)
    rvBuf += '<input type="hidden" name="selectPlot" value="%s">' % selectPlot
    rvBuf += '<input type="hidden" name="startDateTime" value="%s">' % startDateTime
    rvBuf += '<input type="hidden" name="endDateTime" value="%s">' % endDateTime
    rvBuf += '<button type="submit">Download to Excel!</button>'
    rvBuf += '</form>'
    rvBuf += '&nbsp;'
    rvBuf += '&nbsp;'
    rvBuf += '<form style="display:inline;">'
    rvBuf += '<button onclick="myFunction()">Print this page</button>'
    print
    rvBuf += '<script>'
    rvBuf += 'function myFunction() {'
    rvBuf += '    window.print();'
    rvBuf += '}'
    rvBuf += '</script>'

    if (error):
        rvBuf += '<h2 style="color:red">%s</h2>' % errmsg
    else:
        rvBuf += '<hr>'
        rvBuf += '<div align="center"><img src=\"data:image/png;base64,' + encoded + "\" /></div>"
        rvBuf += '<hr>'
        rvBuf += '<br>'
        rvBuf += '<table border="1" style="width:50%" align="center">'
        rvBuf += '<thead>'
        rvBuf += '  <tr>'
        rvBuf += '    <th>Date and time</th>'
        for i in range(nseries):
            rvBuf += '    <th>%s</th>' % fieldDesc[i]
        rvBuf += '  </tr>'
        rvBuf += '</thead>'
        rvBuf += '<tbody>'
        for i in range(len(period_list)):
            rvBuf += '<tr>'
            rvBuf += '<td>%s</td>' % period_list[i].strftime('%Y-%m-%d %H:%M')
            for j in range(nseries):
                rvBuf += '<td align="right">%9.2f</td>' % series[i,j]
            rvBuf += '</tr>'
        rvBuf += '</tbody>'
        rvBuf += '</table>'
    rvBuf += '</body>'
    rvBuf += '</html>'

    return rvBuf
