#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import cStringIO
import cgi
import cgitb
import base64
from datetime import datetime, timedelta
import MySQLdb as mdb
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import date2num
from matplotlib.dates import DateFormatter, HourLocator, DayLocator
import sys

from buoydef import *
from buoyvida import *
    
cgitb.enable()

form = cgi.FieldStorage()

if "selectPlot" not in form or "startDateTime" not in form or "endDateTime" not in form:
    selectPlot = "Wind Speed and Gusts"
    endDateTime = datetime.today().strftime('%Y-%m-%dT%H:%M:%S')
    startDateTime = (datetime.today() - timedelta(days=2)).strftime('%Y-%m-%dT%H:%M:%S')
else:
    selectPlot = form["selectPlot"].value
    startDateTime = form["startDateTime"].value
    endDateTime = form["endDateTime"].value

start_date = startDateTime.replace('T', ' ')
end_date = endDateTime.replace('T', ' ')

if (start_date < end_date):
    
    # make period list
    period_list = make_period_list(startDateTime,endDateTime)

    if (len(period_list) <= 7*24*2):        
    
        # get buoy database parameters
        (fields,tables,fieldDesc,yLab,axis,colorStyle) = get_buoyparam(selectPlot)
            
        # get buoy scalar data
        (nseries,series) = get_buoy_data(fields,tables,period_list)

        # plot scalar data
        encoded = make_scalar_plot(period_list,series,fieldDesc,yLab,axis,colorStyle)        
    
        error = False

    else:

        errmsg = 'Period length must be shorter than 7 days!'
        error = True
            
else:    

    errmsg = 'Start date and time must be before end date and time!'
    error = True
    
print "<!DOCTYPE html>"
print "<html>"
print
print '<head>'
print '<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">'
print '<title>Buoy scalar multi-plot</title>'
print '<style>'
print 'h2 {'
print '    text-align: center;'
print '}'
print '</style>'
print '</head>'
print
print '<body>'
print
print '<form action="buoy_scalar.py">'
print '<h2>Data from the oceanographic buoy Vida</h2>'
print '<h2 style="color:blue">%s</h2>' % selectPlot
print '<hr>'
print '<label for="selectPlot">Select plot:</label>'
print '<select name="selectPlot" id="selectPlot">'
for i in range(len(buoySelDesc)):
    if (buoySelDesc[i] == selectPlot):
        print '  <option selected="selected">%s</option>' % buoySelDesc[i]
    else:
        print '  <option>%s</option>' % buoySelDesc[i]
print '</select>'
print '&nbsp;'
print '&nbsp;'
print '<label for="startDateTime">Start date and time:</label>'
print '<input type="datetime-local" name="startDateTime" value=%s>' % startDateTime
print '&nbsp;'
print '&nbsp;'
print '<label for="endDateTime">End date and time:</label>'
print '<input type="datetime-local" name="endDateTime" value=%s>' % endDateTime
print '&nbsp;'
print '&nbsp;'
print '<input type="submit" value="Go!" />'
print '&nbsp;'
print '&nbsp;'
print '</form>'
print '<form method="post" action="scalar2excel.py" style="display:inline;">'
print '<input type="hidden" name="selectPlot" value="%s">' % selectPlot
print '<input type="hidden" name="startDateTime" value="%s">' % startDateTime
print '<input type="hidden" name="endDateTime" value="%s">' % endDateTime
print '<button type="submit">Download to Excel!</button>'
print '</form>'
print '&nbsp;'
print '&nbsp;'
print '<form style="display:inline;">'
print '<button onclick="myFunction()">Print this page</button>'
print
print '<script>'
print 'function myFunction() {'
print '    window.print();'
print '}'
print '</script>'

if (error):
    print '<h2 style="color:red">%s</h2>' % errmsg
else:
    print '<hr>'
    print '<div align="center"><img src=\"data:image/png;base64,' + encoded + "\" /></div>"
    print '<hr>'
    print '<br>'
    print '<table border="1" style="width:50%" align="center">'
    print '  <tr>'
    print '    <th>Date and time</th>'
    for i in range(nseries):
        print '    <th>%s</th>' % fieldDesc[i]		
    print '  </tr>'
    for i in range(len(period_list)):
        print '<tr>'
        print '<td>%s</td>' % period_list[i].strftime('%Y-%m-%d %H:%M')
        for j in range(nseries):
            print '<td align="right">%9.2f</td>' % series[i,j]
        print '</tr>'
    print '</table>'
print '</body>'
print '</html>'
