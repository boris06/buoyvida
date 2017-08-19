# -*- coding: UTF-8 -*- 

from datetime import datetime, timedelta
import MySQLdb as mdb
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import date2num
from matplotlib.dates import DateFormatter, HourLocator, DayLocator
import cStringIO
import base64

from mbp_buoy_vida import config

def get_buoy_currents(dbConfig, period_list,cells):
    con = mdb.connect(dbConfig.host, dbConfig.username, dbConfig.password, dbConfig.db)
    con.ping(True)    
    with con:
        cur = con.cursor()
        uarr = []
        varr = []
        for cell in (cells):
            con.ping(True)    
            cur = con.cursor()
            cur.execute("SELECT profile.datestart, profile.dateend, awac_currents.current_E, awac_currents.current_N, awac_currents.cell_no "
                        "FROM awac_currents RIGHT JOIN profile ON awac_currents.pid = profile.pid "
                        "WHERE profile.dateend>='%s' AND profile.dateend<='%s' AND awac_currents.cell_no=%s" % (period_list[0],period_list[-1],cell))
            date_start = []
            date_end = []
            current_E = np.zeros(cur.rowcount)
            current_N = np.zeros(cur.rowcount)
            for i in range(cur.rowcount):            
                row = cur.fetchone()
                date_start.append(row[0])
                date_end.append(row[1])
                current_E[i] = float(row[2])
                current_N[i] = float(row[3])
            ind = [i for i, item in enumerate(period_list) if item in set(date_end)]
            current_E_new = np.zeros(len(period_list))
            current_N_new = np.zeros(len(period_list))
            current_E_new[:] = np.NAN
            current_N_new[:] = np.NAN
            current_E_new[ind] = current_E
            current_N_new[ind] = current_N

            uarr.append(current_E_new)
            varr.append(current_N_new)

    con.close()

    return(uarr,varr)

def get_buoy_data(dbConfig, fields,tables,period_list):
    con = mdb.connect(dbConfig.host, dbConfig.username, dbConfig.password, dbConfig.db)
    con.ping(True)    
    with con:
        cur = con.cursor()
        fields = ', '.join(fields)
        strSQL = "SELECT profile.datestart, profile.dateend, " + fields + ' FROM profile '
        strLeftJoin = ''
        for i in range(len(tables)):
                strLeftJoin = strLeftJoin + 'LEFT JOIN %s ON profile.pid = %s.pid ' % (tables[i],tables[i])
        strSQL = strSQL + strLeftJoin
        strSQL = strSQL + "WHERE profile.dateend>='%s' AND profile.dateend<='%s' AND profile.period_length='30'" % (period_list[0],period_list[-1])
        cur.execute(strSQL)
        date_start = []
        date_end = []
        nseries = len(fields.split(', '))
        series = np.zeros((cur.rowcount,nseries))
        series[:] = np.NAN
        for i in range(cur.rowcount):
            row = cur.fetchone()
            date_start.append(row[0])
            date_end.append(row[1])
            for j in range(nseries):
                series[i,j] = row[2+j]
    con.close()
    ind = [i for i, item in enumerate(period_list) if item in set(date_end)]
    series_new = np.zeros((len(period_list),nseries))
    series_new[:] = np.NAN
    series_new[ind] = series
    
    return (nseries,series_new)

def make_period_list(startDateTime,endDateTime):
    tm_s = datetime.strptime(startDateTime, "%Y-%m-%dT%H:%M:%S")
    tm_s = tm_s - timedelta(minutes=tm_s.minute % 30,
                            seconds=tm_s.second,
                            microseconds=tm_s.microsecond)
    tm_e = datetime.strptime(endDateTime, "%Y-%m-%dT%H:%M:%S") 
    tm_e = tm_e - timedelta(minutes=tm_e.minute % 30,
                            seconds=tm_e.second,
                            microseconds=tm_e.microsecond)
    periods = (tm_e-tm_s).total_seconds()/60./30.
    period_list = [tm_s+timedelta(minutes=x*30.) for x in range(0, int(periods)+1)]
    return period_list

def make_vector_plot(period_list,uvec,vvec,C,desc,ref,keytext,ylabel,yrot,keyxpos,keyypos,scale):

    X,Y = np.meshgrid(date2num(period_list),[float(i) for i in range(len(desc))])

    all_missing = False
    if (len(desc)==1):
        fig_height = 3.5*len(desc)
        fig, ax = plt.subplots(figsize=(11, fig_height))
    else:
        fig_height = 1.5*len(desc)
        fig, ax = plt.subplots(figsize=(11, fig_height))
	all_missing = False
    if np.isnan(uvec).all() or np.isnan(vvec).all():
        all_missing = True

    if all_missing:
        ax.set_xlim([date2num(period_list)[0], date2num(period_list)[-1]])
        if (len(desc) == 1):
            ax.set_ylim([-(1.0), 1.0])
        else:
            ax.set_ylim([-(1.0), float(len(desc))])
        plt.text(np.mean(date2num(period_list)), np.mean(range(len(desc))),
                "Missing data!", fontsize=24, va='center', ha='center', color='red')
    else:
        q = ax.quiver(X, Y, uvec, vvec, color=C,
                      angles='uv', width=0.002, headwidth=5,scale=scale,
                      headlength=5, headaxislength=5 )

        if (len(desc) == 1):
            pass
        else:
            ax.set_ylim([-(1.0), float(len(desc))])

        qw = plt.quiverkey(q, keyxpos, keyypos, ref,
                          keytext % ref,color=C,
                          labelpos='W', coordinates='axes', fontproperties={'size':14})
	plt.ylabel(ylabel, fontsize=11)
    plt.yticks(np.arange(len(desc)), desc, rotation=yrot)

    #ax.get_yaxis().set_visible(False)
    ax.xaxis_date()    
    
    _ = plt.xticks(rotation=0)

    date_format = "%Y-%m-%d %H:%M"
    a = period_list[0]
    b = period_list[-1]
    delta = b - a
    days = delta.days + 1
    if days > 4:
        if days > 8:
            days = 12
        else:
            days = 6

    plt.gca().xaxis.set_major_locator( DayLocator())
    plt.gca().xaxis.set_minor_locator( HourLocator(byhour=range(0, 24, days)))
    plt.gca().xaxis.set_major_formatter( DateFormatter('%d/%m/%y') )
    plt.gca().xaxis.set_minor_formatter( DateFormatter('%H') )

    plt.gca().xaxis.grid(b=True, which=u'both')
    plt.gca().yaxis.grid(b=True, which=u'both')

    plt.tick_params(axis='both', which='major', labelsize=11, pad=15)
    plt.tick_params(axis='both', which='minor', labelsize=10)

    #write to file object
    f = cStringIO.StringIO()
    plt.savefig(f, dpi=120, format='png')
    f.seek(0)

    img = f.read()

    encoded = base64.b64encode(img)    
    
    error = False

    #plt.show()    
    
    return encoded

def make_scalar_plot(period_list,series,fieldDesc,yLab,axis,colorStyle,fieldFactor):

    nseries = series.shape[1]

    ylabelColor = [cs[0] for cs in colorStyle]
    linewidth=2
    
    fig, ax1 = plt.subplots()
    t = date2num(period_list)
    isax2 = False
    for i in range(nseries):
        if fieldFactor[i] != 1.0:
            series[:, i] *= fieldFactor[i]
        if (axis[i] == 'left'):
            ax1.plot(t, series[:, i], colorStyle[i], linewidth=2, label=fieldDesc[i])
        else:
            isax2 = True

    # Make the y-axis label and tick labels match the line color.
    ax1.set_ylabel(yLab[0], color=ylabelColor[0])
    for tl in ax1.get_yticklabels():
        tl.set_color(ylabelColor[0])

    if isax2 == True:  
        ax2 = ax1.twinx()
        for i in range(nseries):
            if (axis[i] == 'right'):
                ax2.plot(t,series[:,i],colorStyle[i],linewidth=2,label=fieldDesc[i])
                ilab2 = i
            else:
                pass
        ax2.set_ylabel(yLab[ilab2], color=ylabelColor[-1])
        for tl in ax2.get_yticklabels():
            tl.set_color(ylabelColor[-1])
            
    ax1.set_xlabel('')

    ax1.xaxis_date()    

    _ = plt.xticks(rotation=0)

    date_format = "%Y-%m-%d %H:%M"
    a = period_list[0]
    b = period_list[-1]
    delta = b - a
    days = delta.days + 1
    if days > 4:
        if days > 8:
            days = 12
        else:
            days = 6

    plt.gca().xaxis.set_major_locator( DayLocator())
    plt.gca().xaxis.set_minor_locator( HourLocator(byhour=range(0, 24, days)))
    plt.gca().xaxis.set_major_formatter( DateFormatter('%d/%m/%y') )
    plt.gca().xaxis.set_minor_formatter( DateFormatter('%H') )

    plt.gca().xaxis.grid(b=True, which=u'both')
    plt.gca().yaxis.grid(b=True, which=u'both',color=ylabelColor[1],linewidth=1)
    ax1.xaxis.grid(b=True, which=u'both',linewidth=1)
    ax1.yaxis.grid(b=True, which=u'both',color=ylabelColor[0],linewidth=1)

    plt.tick_params(axis='both', which='major', labelsize=11)
    plt.tick_params(axis='both', which='minor', labelsize=10)

    for tick in ax1.xaxis.get_major_ticks():
        tick.label.set_fontsize(11)
        tick.set_pad(15.)    
    for tick in ax1.xaxis.get_minor_ticks():
        tick.label.set_fontsize(10) 
    
    for tick in ax1.yaxis.get_major_ticks():
        tick.label.set_fontsize(11)
    for tick in ax1.yaxis.get_minor_ticks():
        tick.label.set_fontsize(10) 
    

    box1 = ax1.get_position()
    ax1.set_position([box1.x0, box1.y0 + box1.height * 0.15,
                 box1.width, box1.height * 0.85])
    ax1.legend(loc='lower left', bbox_to_anchor=(0.0, -0.30), prop={'size':10},
               handlelength=3,numpoints=4)
    if (isax2 == True):
        box2 = ax2.get_position()
        ax2.set_position([box2.x0, box2.y0 + box2.height * 0.15,
                 box2.width, box2.height * 0.85])
        ax2.legend(loc='lower right',
                   bbox_to_anchor=(1.013, -0.30),
                   prop={'size':10},
                   handlelength=3,numpoints=4)

    f = cStringIO.StringIO()
    plt.savefig(f, dpi=120, format='png')
    f.seek(0)
    img = f.read()
    encoded = base64.b64encode(img)    

    #plt.show()

    return encoded
