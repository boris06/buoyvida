#!/usr/bin/env python

import pickle
from math import cos, pi
from dateutil.parser import parse as date_parse

import matplotlib

matplotlib.use('Agg')  # Force matplotlib to not use any Xwindows backend.

FORM_OP_NONE = 0
FORM_OP_GET_HODOBRAPH = 1
FORM_OP_GET_TRAJECTORY = 2

__DBG = False
if __DBG == True:
    import cgitb

    cgitb.enable()  # Enable detailed and formated exception stacktrace logging

from .buoyvida import *

# from mbp_buoy_vida import config as DbConfig
from mbp_buoy_vida import config as DbConfig
dbConfig = DbConfig.DbConfig()

__all__ = ['trajectory_hodograph']


def make_traj_hodo_plot(scriptsRootDir, curr_traj_e, curr_traj_n, zoom, buoy_position, curr_hodo_e, curr_hodo_n, max_cell,
                        period_list):
    plt.figure(figsize=(14, 6))

    # trajectory generation from the starting position at buoy, according to website:
    # http://gis.stackexchange.com/questions/2951/algorithm-for-offsetting-a-latitude-longitude-by-some-amount-of-meters

    # Position of buoy Vida, decimal degrees
    lat_buoy = 45.548800
    lon_buoy = 13.550525

    # Earth's radius, sphere
    r = 6378137

    lat1 = lat_buoy
    lon1 = lon_buoy
    lat = np.zeros(len(curr_traj_e))
    lon = np.zeros(len(curr_traj_e))
    for icurr in range(len(curr_traj_e)):
        lat[icurr] = lat1
        lon[icurr] = lon1
        # if any of currents velocities are missing then stop generating trajectory
        if curr_traj_e[icurr] == np.NAN or curr_traj_n[icurr] == np.NAN:
            break
        else:
            # simplified procedure for small areas -
            # see http://gis.stackexchange.com/questions/2951/algorithm-for-offsetting-a-latitude-longitude-by-some-amount-of-meters
            # offsets in meters
            dn = curr_traj_n[icurr] / 100 * 1800
            de = curr_traj_e[icurr] / 100 * 1800
            # Coordinate offsets in radians
            dlat = dn / r
            dlon = de / (r * cos(pi * lat1 / 180))
            # OffsetPosition, decimal degrees
            lat1 += dlat * 180 / pi
            lon1 += dlon * 180 / pi

    # if trajectory doesn't start at buoy position then
    # it must be shifted - assuming the homogenoues velocity
    # in this part of the Gulf of Trieste
    if buoy_position == 'at the middle of trajectory':
        lat_shift = lat[0] - lat[len(curr_traj_e) / 2]
        lon_shift = lon[0] - lon[len(curr_traj_e) / 2]
        lat += lat_shift
        lon += lon_shift
    if buoy_position == 'at the end of trajectory':
        lat_shift = lat[0] - lat[-1]
        lon_shift = lon[0] - lon[-1]
        lat += lat_shift
        lon += lon_shift

    # prepare the trajectory plot (left)
    ax1 = plt.subplot(1, 2, 1)

    # the basemap of the part of the Gulf of Trieste was previously saved to pickle
    tmpFileName = "%s/%s" % (scriptsRootDir, "buoy.trajectory.pickle")
    m2 = pickle.load(open(tmpFileName, 'rb'))  # load here the above pickle
    # m2 = pickle.load(open(tmpFileName, 'rb'), encoding='latin1')
    # m2 = pickle.load(open(tmpFileName, 'rb'), encoding='iso-8859-1')

    m2.ax = ax1
    # draw coastlines, country boundaries, fill continents.
    m2.drawcoastlines(linewidth=0.25)
    m2.drawcountries(linewidth=0.25)
    m2.fillcontinents(color='peru', lake_color='lightcyan')
    # draw the edge of the map projection region
    m2.drawmapboundary(fill_color='lightcyan')
    # zoom > 1 was applied
    if zoom > 1:
        lon_diff = (m2.lonmax - m2.lonmin) * (zoom - 1) / 2 / zoom
        lat_diff = (m2.latmax - m2.latmin) * (zoom - 1) / 2 / zoom
        m2.latmin += lat_diff
        m2.lonmin += lon_diff
        m2.latmax -= lat_diff
        m2.lonmax -= lon_diff
        lonmin_new, latmin_new = m2(m2.lonmin, m2.latmin)
        lonmax_new, latmax_new = m2(m2.lonmax, m2.latmax)
        ax1.set_xlim(lonmin_new, lonmax_new)
        ax1.set_ylim(latmin_new, latmax_new)
    meridians = np.arange(13, 14, 1 / 60.)
    m2.drawmeridians(meridians, labels=[0, 0, 0, 0])
    parallels = np.arange(45, 46, 1 / 60.)
    m2.drawparallels(parallels, labels=[0, 0, 0, 0])
    # here we use the method annotate for drawing labels instead of basemap drawmeridians and drawparallels, see:
    # http://stackoverflow.com/questions/25790755/how-to-label-parallels-meridian-on-orthographic-projection-using-matplotlib-base
    degree_sign = u'\N{DEGREE SIGN}'
    for im in np.arange(len(meridians)):
        lon_deg = np.floor(meridians[im])
        lon_min = np.round((meridians[im] - lon_deg) * 60)
        lon_txt = '%d%s%d\'' % (lon_deg, degree_sign, lon_min)
        if np.remainder(lon_min, 2) == 0 or zoom > 1:
            plt.annotate(lon_txt, xy=m2(meridians[im], m2.latmax), xycoords='data', va='bottom', ha='center',
                         fontsize=10)
    for ip in np.arange(len(parallels)):
        lat_deg = np.floor(parallels[ip])
        lat_min = np.round((parallels[ip] - lat_deg) * 60)
        lat_txt = '%d%s%d\'' % (lat_deg, degree_sign, lat_min) + ' |'
        plt.annotate(lat_txt, xy=m2(m2.lonmin, parallels[ip]), xycoords='data', va='center', ha='right', fontsize=10)

    # we remove the land points on the trajectory
    x, y = m2(lon, lat)
    x1 = []
    y1 = []
    for icurr in range(len(x)):
        # if the point is on land, stop immediately
        if not m2.is_land(x[icurr], y[icurr]):
            x1.append(x[icurr])
            y1.append(y[icurr])
        else:
            break
    x = np.asarray(x1)
    y = np.asarray(y1)

    # trajectory plot in red
    m2.plot(x, y, color='red', linewidth=2)
    # draw hourly labels inside map boundaries with the date at the beginning of trajectory and midnight
    for icurr in range(len(x)):
        if m2.lonmin < lon[icurr] < m2.lonmax and m2.latmin < lat[icurr] < m2.latmax:
            if period_list[icurr].hour == 0 and period_list[icurr].minute == 0 or icurr == 0:
                s1 = period_list[icurr].strftime('%d/%m/%y %H:%M')
            elif period_list[icurr].minute == 0:
                s1 = period_list[icurr].strftime('%H:%M')
            else:
                s1 = ''
            plt.text(x[icurr], y[icurr], s1, ha='center', va='center', fontsize=8)

    # prepare the hodograph plot (right)
    ax2 = plt.subplot(1, 2, 2, projection='polar')

    if not (np.isnan(np.sum(curr_hodo_e)) and np.isnan(np.sum(curr_hodo_n))):

        r = np.sqrt(curr_hodo_e * curr_hodo_e + curr_hodo_n * curr_hodo_n)
        r = r[range(max_cell)]
        theta = np.arctan2(curr_hodo_n, curr_hodo_e)
        theta = theta[range(max_cell)]

        # plot "real" hodograph in white (it will be invisible)
        # this ensures the proper axis limits for radius (r)
        ax2.plot(theta, r, color='white', zorder=0)

        # plot arrows
        # small displacement of the label from the end of vector (e.g. 1.5 cm)
        dr = 1.5
        # the length of arrow head
        rmax = np.amax(r)
        head_length = rmax * 0.1
        for icurr in range(len(r)):
            # plot arrow
            plt.arrow(theta[icurr], 0, 0, r[icurr], alpha=1, head_width=0.05, head_length=head_length,
                      length_includes_head=True,
                      edgecolor='red', facecolor='red', lw=1, zorder=1)
            # draw height labels
            ax2.text(theta[icurr], r[icurr] + dr, '%d m' % (icurr + 2), fontsize=8, ha='center', va='center', zorder=2)
        # current velocity labels along r axis are blue
        ax2.tick_params(axis='y', colors='blue')
        # drawing the label 'cm/s'
        rlim = ax2.get_ylim()
        ax2.text(22.5 * pi / 180, rlim[1] * 1.1, 'cm/s', va='center', color='blue')

    else:
        # current velocity is nan
        ax2.text(0, 0, "Missing data!", fontsize=24, va='center', ha='center', color='red')

    ax2.grid(True)

    plt.tight_layout()

    # write to file object and encode
    f = io.BytesIO()
    plt.savefig(f, dpi=120, format='png')
    f.seek(0)

    img = f.read()

    encoded = base64.b64encode(img).decode()

    return encoded


def trajectory_hodograph(scriptsRootDir, endDate=None, endTime=None, selectHeight=None, selectDuration=None, selectZoom=None,
                         selectBuoyPosition=None, selectDateTime=None, selectMaxHeight=None, formOp=None,
                         endDateHidden=None, endTimeHidden=None, durationHidden=None, scriptAbsUrl='/'):
    global dbConfig

    all_heights = ['%d' % height for height in range(2, 23)]
    all_durations = ['%d' % duration for duration in [6, 12, 24]]
    all_cells = list(map(str, (np.asarray(list(map(int, all_heights))) - 2)))
    all_options = ["at the start of trajectory", "at the middle of trajectory", "at the end of trajectory"]

    # check if user has entered the parameters for trajectory, otherwise set the default ones
    if endDate is None or endTime is None or selectDuration is None or selectHeight is None \
       or selectZoom is None or selectBuoyPosition is None:
        endDate = datetime.today().strftime('%Y-%m-%d')
        endTime = datetime.today().strftime('%H:%M')
        selectHeight = "22 m"
        selectDuration = "6 hours"
        selectZoom = "1"
        selectBuoyPosition = all_options[0]
    endDateTime = endDate + "T" + endTime + ":00"

    duration = int(selectDuration.split(" ")[0])
    startDateTime = (date_parse(endDateTime) - timedelta(hours=duration)).strftime(
        '%Y-%m-%dT%H:%M:%S')
    start_date = startDateTime.replace('T', ' ')
    end_date = endDateTime.replace('T', ' ')
    selectCell = int(selectHeight.split(" ")[0]) - 2

    # make the list of valid dates and times from the start to the end of trajectory every 30 minutes
    period_list = make_period_list(startDateTime, endDateTime)

    # check if user has entered the parameters for hodograph, otherwise set the default ones
    if selectDateTime is None or selectMaxHeight is None:
        selectDateTime = period_list[-1].strftime('%d.%m.%Y %H:%M')
        selectMaxHeight = '22 m'
        indDateTime = len(period_list) - 1
    else:
        # if user pressed the button "getHodograph" or changed the slider "selectZoom" or changed "selectBuoyPosition"
        if formOp == FORM_OP_GET_HODOBRAPH \
           or ( endDate == endDateHidden and \
                endTime == endTimeHidden and \
                selectDuration == durationHidden \
              ):
            indDateTime = [item.strftime('%d.%m.%Y %H:%M') for item in period_list].index(selectDateTime)
        else:
            selectDateTime = period_list[-1].strftime('%d.%m.%Y %H:%M')
            selectMaxHeight = '22 m'
            indDateTime = len(period_list) - 1

    (current_E, current_N) = get_buoy_currents(dbConfig, period_list, all_cells)

    curr_traj_E = current_E[selectCell]
    curr_traj_N = current_N[selectCell]

    curr_hodo_E = np.asarray(current_E).transpose()[indDateTime]
    curr_hodo_N = np.asarray(current_N).transpose()[indDateTime]

    # if the most recent currents are not yet available, we take the second last ones
    # this happens if the user requests the data immediately after times hh:00 or hh:30
    if not (np.isnan(np.sum(curr_hodo_E)) and np.isnan(np.sum(curr_hodo_N))):
        pass
    else:
        if indDateTime == (len(period_list) - 1):
            indDateTime -= 1
            curr_hodo_E = np.asarray(current_E).transpose()[indDateTime]
            curr_hodo_N = np.asarray(current_N).transpose()[indDateTime]
            selectDateTime = period_list[indDateTime].strftime('%d.%m.%Y %H:%M')

    maxCell = ['%s m' % height for height in all_heights].index(selectMaxHeight) + 1

    # make the joint trajectory and hodograph plot
    traj_hodo_encoded = make_traj_hodo_plot(scriptsRootDir, curr_traj_E, curr_traj_N, int(selectZoom), selectBuoyPosition, curr_hodo_E,
                                            curr_hodo_N, maxCell, period_list)

    # beginning of the construction of html page
    rvBuf = ""
    rvBuf += "<!DOCTYPE html>"
    rvBuf += '<html>'

    # head
    rvBuf += """
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<title>Buoy trajectory and hodograph</title>
<link href="//fonts.googleapis.com/css?family=Open+Sans:300,300italic,400,400italic,600,600italic,700,700italic,800,800italic" rel="stylesheet" type="text/css">
<style>
  body {
    font-family: "Open Sans";
  }
  h2 {
    text-align: center;
  }
  table tbody {
    font-size: 0.7em;
  }
</style>
</head>
"""

    # body
    rvBuf += '<body>'

    # form
    rvBuf += '<form  name="main" id="main" action="%s/trajectory_hodograph">' % (scriptAbsUrl)

    # two IOC UNESCO logos, title, NIB MBP logo
    rvBuf += '<table>'
    rvBuf += '<tr>'
    tmpFileName = "%s/%s" % (scriptsRootDir, "natcom_slovenia_si.png")
    with open(tmpFileName, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    rvBuf1 = '<div align="left"><img style="height:140px;" src=\"data:image/png;base64,' + encoded_string + "\" /></div>"
    tmpFileName = "%s/%s" % (scriptsRootDir, "ioc_si_national_committee_slovenia_si.png")
    with open(tmpFileName, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    rvBuf2 = '<div align="left"><img style="height:140px;" src=\"data:image/png;base64,' + encoded_string + "\" /></div>"
    rvBuf += '<th>' + rvBuf1 + '</th>'
    rvBuf += '<th>' + rvBuf2 + '</th>'
    rvBuf += '<th>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</th>'
    rvBuf += '<th>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</th>'
    rvBuf += '<th>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</th>'
    rvBuf += '<th><h1>Buoy trajectory and hodograph</h1></th>'
    rvBuf += '<th>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</th>'
    rvBuf += '<th>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</th>'
    rvBuf += '<th>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</th>'
    tmpFileName = "%s/%s" % (scriptsRootDir, "logo_MBP_Pantone_slo.png")
    with open(tmpFileName, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    rvBuf3 = '<div align="left"><img style="height:75px;" src=\"data:image/png;base64,' + encoded_string + "\" /></div>"
    rvBuf += '<th>' + rvBuf3 + '</th>'
    rvBuf += '</tr>'
    rvBuf += '</table>'
    rvBuf += '<table>'

    # titles "Trajectory", "Hodograph"
    rvBuf += '<tr>'
    rvBuf += '<th>Trajectory</th>'
    rvBuf += '<th></th>'
    rvBuf += '<th></th>'
    rvBuf += '<th></th>'
    rvBuf += '<th></th>'
    rvBuf += '<th>Hodograph</th>'
    rvBuf += '</tr>'
    rvBuf += '<tr>'

    # trajectory end date
    rvBuf += '<td align="center">'
    rvBuf += '<label for="endDate">End date: </label>'
    rvBuf += '<input type="date" name="endDate" id="endDate" title="Enter the trajectory end date" value=%s>' % \
             period_list[
                 -1].strftime('%Y-%m-%d')
    rvBuf += '&nbsp;'
    rvBuf += '&nbsp;'

    # trajectory end time
    rvBuf += '<label for="endTime">End time: </label>'
    rvBuf += '<input type="time" name="endTime" id="endTime" title="Enter the trajectory end time" value=%s step="1800">' % \
             period_list[-1].strftime('%H:%M')
    rvBuf += '&nbsp;'
    rvBuf += '&nbsp;'

    # select trajectory duration
    all_durations_m = ['%s hours' % duration for duration in all_durations]
    rvBuf += '<label for="selectDuration">Duration: </label>'
    rvBuf += '<select name="selectDuration" id="selectDuration"  title="Select the trajectory duration">'
    for i in range(len(all_durations_m)):
        if all_durations_m[i] == selectDuration:
            rvBuf += '  <option selected="selected">%s</option>' % all_durations_m[i]
        else:
            rvBuf += '  <option>%s</option>' % all_durations_m[i]
    rvBuf += '</select>'
    rvBuf += '&nbsp;'
    rvBuf += '&nbsp;'

    # select trajectory height
    all_heights_m = ['%s m' % height for height in all_heights]
    rvBuf += '<label for="selectHeight">Height: </label>'
    rvBuf += '<select name="selectHeight" id="selectHeight" title="Select the trajectory height" >'
    for i in range(len(all_heights_m)):
        if all_heights_m[i] == selectHeight:
            rvBuf += '  <option value="%s" selected="selected">%s</option>' % (all_heights_m[i], all_heights_m[i])
        else:
            rvBuf += '   <option value="%s">%s</option>' % (all_heights_m[i], all_heights_m[i])
    rvBuf += '</select>'
    rvBuf += '&nbsp;'
    rvBuf += '&nbsp;'

    # get trajectory button (submit)
    rvBuf += '<input type="submit"  name="getTrajectory" id="getTrajectory"   title="Calculates and shows the trajectory" value="Get trajectory" />'
    rvBuf += '</td>'
    rvBuf += '<td>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</td>'
    rvBuf += '<td>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</td>'
    rvBuf += '<td>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</td>'
    rvBuf += '<td>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</td>'

    # select hodograph date and time
    rvBuf += '<td align="center">'
    all_times_m = [item.strftime('%d.%m.%Y %H:%M') for item in period_list]
    rvBuf += '<label for="selectDateTime">Date and time: </label>'
    rvBuf += '<select name="selectDateTime" id="selectDateTime"   title="Select the hodograph date and time">'
    for i in range(len(all_times_m)):
        if all_times_m[i] == selectDateTime:
            rvBuf += '  <option selected="selected">%s</option>' % all_times_m[i]
        else:
            rvBuf += '  <option>%s</option>' % all_times_m[i]
    rvBuf += '</select>'
    rvBuf += '&nbsp;'
    rvBuf += '&nbsp;'

    # select hodograph max. height
    rvBuf += '<label for="selectMaxHeight">Max. height: </label>'
    rvBuf += '<select name="selectMaxHeight" id="selectMaxHeight"   title="Select the hodograph maximum height" >'
    for i in range(len(all_heights_m)):
        if all_heights_m[i] == selectMaxHeight:
            rvBuf += '  <option value="%s" selected="selected">%s</option>' % (all_heights_m[i], all_heights_m[i])
        else:
            rvBuf += '   <option value="%s">%s</option>' % (all_heights_m[i], all_heights_m[i])
    rvBuf += '</select>'
    rvBuf += '&nbsp;'
    rvBuf += '&nbsp;'

    # get hodograph button (submit)
    rvBuf += '<input type="submit" name="getHodograph" id="getHodograph" title="Shows the hodograph" value="Get hodograph" />'
    rvBuf += '&nbsp;'
    rvBuf += '&nbsp;'
    rvBuf += '&nbsp;'
    rvBuf += '&nbsp;'

    # print button
    rvBuf += '<button onclick="myPrint()">Print this page</button>'
    rvBuf += '</td>'
    rvBuf += '</tr>'
    rvBuf += '<tr>'
    rvBuf += '<td>'

    # select zoom slider
    rvBuf += '<label for="selectZoom">Zoom: </label>'
    rvBuf += '<input name="selectZoom" id="selectZoom" type="range" min="1" max="5" step="1" title="Slide to zoom area (1-5x)" value=%s onchange="clickButton()"/>' % selectZoom
    rvBuf += '&nbsp;'
    rvBuf += '&nbsp;'

    # select buoy position
    rvBuf += '<label for="selectBuoyPosition">Buoy position: </label>'
    rvBuf += '<select name="selectBuoyPosition" id="selectBuoyPosition" title="Choose the buoy position within the trajectory" onchange="clickButton()">'
    for i in range(len(all_options)):
        if all_options[i] == selectBuoyPosition:
            rvBuf += '  <option value="%s" selected="selected">%s</option>' % (all_options[i], all_options[i])
        else:
            rvBuf += '  <option value="%s">%s</option>' % (all_options[i], all_options[i])
    rvBuf += '</select>'
    rvBuf += '</td>'
    rvBuf += '</tr>'
    rvBuf += '</table>'

    # hidden fields for trajectory end date, end time and duration
    # they are used to control whether user has changed the above visible fields with the same names
    # if changed then a new trajectory is calculated and presented, otherwise the zoom, buoy position or
    # buoy hodograph controls were changed or pressed
    rvBuf += '<input type="hidden" name="endDateHidden" id="endDateHidden" value="%s">' % endDate
    rvBuf += '<input type="hidden" name="endTimeHidden" id="endTimeHidden" value="%s">' % endTime
    rvBuf += '<input type="hidden" name="durationHidden" id="durationHidden" value="%s">' % selectDuration
    rvBuf += '</form>'
    rvBuf += '<hr>'

    # showing the trajectory and hodograph plot
    rvBuf += '<div align="center"><img src=\"data:image/png;base64,' + traj_hodo_encoded + "\" /></div>"
    rvBuf += '<br>'
    rvBuf += '<div style="margin-left:100px">'

    # presenting the text below the plot
    rvBuf += '<table>'
    rvBuf += '<tr>'
    rvBuf += '<td>'
    rvBuf += '<h4 lang="sl">Hodograf horizontalnega potovanja namišljenega delca iz lege boje Vide od %s do %s.</h4>' \
             % (period_list[0].strftime('%d.%m.%Y %H:%M'), period_list[-1].strftime('%d.%m.%Y %H:%M'))
    rvBuf += '</td>'
    rvBuf += '<td>'
    rvBuf += '<div style="width:200px"></div>'
    rvBuf += '</td>'
    rvBuf += '<td>'
    rvBuf += '<h4 lang="sl">Vertikalna porazdelitev tokov na boji Vidi po vodnem stolpcu ob %s. Vektorjem hitrosti toka, katerih jakosti (cm/s) so določene s polmeri krožnic, so pripisane višine (m) nad dnom.</h4>' \
             % selectDateTime
    rvBuf += '</td>'
    rvBuf += '</tr>'
    rvBuf += '<tr>'
    rvBuf += '<td>'
    rvBuf += '<h4 lang="en">The hodograph of the horizontal travel of an imaginary particle from the position of buoy Vida from %s to %s.</h4>' \
             % (period_list[0].strftime('%m/%d/%Y %H:%M'), period_list[-1].strftime('%m/%d/%Y %H:%M'))
    rvBuf += '</td>'
    rvBuf += '<td>'
    rvBuf += '<div style="width:200px"></div>'
    rvBuf += '</td>'
    rvBuf += '<td>'
    rvBuf += '<h4 lang="en">The vertical distribution of currents on the buoy Vida along the water column at %s. The current velocity vectors for which the magnitudes (cm/s) are determined by the radii of circles are attributed with the height (m) above the bottom.</h4>' \
             % (date_parse(selectDateTime).strftime('%m/%d/%Y %H:%M'))
    rvBuf += '</td>'
    rvBuf += '</tr>'
    rvBuf += '</table>'
    rvBuf += '<br>'
    rvBuf += '<p lang="sl">Aplikacijo razvil B. Petelin, namestil D. Deželjin.</p>'
    rvBuf += '<p lang="en">Application developed by B. Petelin, installed by D. Deželjin</p>'
    rvBuf += '</div>'

    # script for calling the print function after print button was pressed
    rvBuf += '<script>'
    rvBuf += 'function myPrint() {'
    rvBuf += '    window.print();'
    rvBuf += '}'
    rvBuf += '</script>'

    # script for firing the getTrajectory button after changing selectZoom or selectBuoyPosition
    rvBuf += '<script>'
    rvBuf += 'function clickButton() {'
    rvBuf += '    document.getElementById("getTrajectory").click();'
    rvBuf += '}'
    rvBuf += '</script>'
    rvBuf += '</body>'
    rvBuf += '</html>'

    # finally create the whole html
    return rvBuf
