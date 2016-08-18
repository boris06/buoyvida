#!/usr/bin/env python 
# -*- coding: UTF-8 -*- 

from buoydef import *
from buoyvida import *
import cgi
import cgitb
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cmx

cgitb.enable(logdir="")
form = cgi.FieldStorage()

all_heights = ['%d' % height for height in range(2,23)]
def_heights = ['2', '5', '10', '15', '20']
if "startDateTime" not in form or "endDateTime" not in form or "selectHeights" not in form:
    endDateTime = datetime.today().strftime('%Y-%m-%dT%H:%M:%S')
    startDateTime = (datetime.today() - timedelta(days=2)).strftime('%Y-%m-%dT%H:%M:%S')
    heights = def_heights
else:
    startDateTime = form["startDateTime"].value
    endDateTime = form["endDateTime"].value
    heights = []
    try:
        for i in range(len(form["selectHeights"])):
            heights.append(form["selectHeights"][i].value)
    except:
        heights.append(form["selectHeights"].value)
        
start_date = startDateTime.replace('T', ' ')
end_date = endDateTime.replace('T', ' ')
cells = map(str, (np.asarray(map(int, heights)) - 2)) 

if (start_date < end_date):
    
    # make period list
    period_list = make_period_list(startDateTime,endDateTime)

    if (len(period_list) <= 7*24*2):            
    
        # get wind and waves data
        fields=['wind.vmspd', 'wind.vmdir', 'awac_waves.wave_height', 'awac_waves.mean_direction']
        tables=['wind', 'awac_waves']
        # table
        fieldDesc = [fieldDict[x] for x in fields]

        (nseries,series)=get_buoy_data(fields,tables,period_list)
        uwind = series[:,0] * np.cos((270. - series[:,1])*np.pi/180.)
        vwind = series[:,0] * np.sin((270. - series[:,1])*np.pi/180.)
        uwaves = series[:,2] * np.cos((270. - series[:,3])*np.pi/180.)
        vwaves = series[:,2] * np.sin((270. - series[:,3])*np.pi/180.)

        # get sea currents data
        (current_E,current_N) = get_buoy_currents(period_list,cells)    

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
        currents_encoded = make_vector_plot(period_list,uvec,vvec,colorVal,desc,30,keytext,'Sea currents at height [m]','horizontal',0.55,0.96,None)

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
print '<title>Buoy vector multi-plot</title>'
print '<style>'
print 'h2 {'
print '    text-align: center;'
print '}'
print '</style>'
print '</head>'
print
print '<body>'    
print '<form name="main" id="main" action="buoy_vector.py">'
print '<h2>Wind, waves and sea currents from the oceanographic buoy Vida</h2>'
print '<hr>'
print '<label for="startDateTime">Start date and time:</label>'
print '<input type="datetime-local" name="startDateTime" value=%s>' % startDateTime
print '&nbsp;'
print '&nbsp;'
print '<label for="endDateTime">End date and time:</label>'
print '<input type="datetime-local" name="endDateTime" value=%s>' % endDateTime
print '&nbsp;'
print '&nbsp;'
all_heights_m = ['%s m' % height for height in all_heights]
print '<label for="selectHeights">Select heights:</label>'
print '<select multiple name="selectHeights" id="selectHeights" size="3" title="Hold down the Ctrl (windows) / Command (Mac) button to select multiple options.">'
for i in range(len(all_heights)):
    if (all_heights[i] in heights):
        print '   <option value="%s" selected="selected">%s</option>' % (all_heights[i],all_heights_m[i])
    else:
        print '   <option value="%s">%s</option>' % (all_heights[i],all_heights_m[i])
print '</select>'
print '&nbsp;'
print '&nbsp;'
print '<input type="submit" value="Go!" />'
print '</form>'
print '&nbsp;'
print '&nbsp;'
print '<form method="post" action="vector2excel.py" style="display:inline;">'
print '<input type="hidden" name="startDateTime" value="%s">' % startDateTime
print '<input type="hidden" name="endDateTime" value="%s">' % endDateTime
print '<input type="hidden" name="cells" value="%s">' % cells
print '<input type="hidden" name="heights" value="%s">' % heights
print '<button type="submit">Download to Excel!</button>'
print '</form>'
print '&nbsp;'
print '&nbsp;'
print '<form style="display:inline;">'
print '<button onclick="myPrint()">Print this page</button>'
print
print '<script>'
print 'function myPrint() {'
print '    window.print();'
print '}'
print '</script>'
print '</form>'
print '&nbsp;'
print '&nbsp;'
print '<form style="display:inline;">'
print '<button onclick="resetHeights()">Reset heights</button>'
print '<script>'
print 'function resetHeights() {'
print '  var el = document.getElementById("selectHeights");'
print '  for (var i = 0; i < el.length; i++) {'
print '     document.getElementById("selectHeights")[i].selected = false;'
print '  }'
print '  var value = ["2", "5", "10", "15", "20"];'
print '  for (var j = 0; j < value.length; j++) {'
print '     for (var i = 0; i < el.length; i++) {'
print '        if (el[i].value == value[j]) {'
print '           document.getElementById("selectHeights")[i].selected = true;'
print '        }'
print '     }'
print '  }'
print '}'
print '</script>'
print '</form>'
print

if (error):
    print '<h2 style="color:red">%s</h2>' % errmsg
else:
    print '<hr>'
    print '<div align="center"><img src=\"data:image/png;base64,' + wind_encoded + "\" /></div>"
    print '<div align="center"><img src=\"data:image/png;base64,' + waves_encoded + "\" /></div>"
    print '<div align="center"><img src=\"data:image/png;base64,' + currents_encoded + "\" /></div>"
    print '<hr>'
    print '<br>'
    print '<table border="1" style="width:90%" align="center">'
    print '  <tr>'
    print '    <th>Date and time</th>'
    for i in range(nseries):
        print '    <th>%s</th>' % fieldDesc[i]
    for i in range(len(fieldDescCurr)):
        print '    <th>%s</th>' % fieldDescCurr[i]
    print '  </tr>'
    for i in range(len(period_list)):
        print '<tr>'
        print '<td>%s</td>' % period_list[i].strftime('%Y-%m-%d %H:%M')
        for j in range(nseries):
            print '<td align="right">%9.2f</td>' % series[i,j]
        for j in range(len(desc)):
            print '<td align="right">%9.2f</td>' % uvec[j,i]
            print '<td align="right">%9.2f</td>' % vvec[j,i]            
        print '</tr>'            
    print '</table>'
print '</body>'
print '</html>'
