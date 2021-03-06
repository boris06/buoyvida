#!/usr/bin/python
# -*- coding: UTF-8 -*- 

from cgi import parse_qs
import sys
import string

__all__ = ["index", "scalar", "scalar2excel", "vector", "vector2excel", "trajectory_hodograph"]

def getIndex(environ):
    rvBuf = "Available functions:\n"
    rvBuf += " -> " + "\n -> ".join(__all__)
    return rvBuf


def getDebug(environ):
    rvBuf = [
        "%s: %s" % (key, value) for key, value in sorted(environ.items())
    ]
    return "\n".join(rvBuf)


def getScalar(environ):
    from mbp_buoy_vida import scalar
    request_script_path = environ["SCRIPT_NAME"]
    qs = parse_qs(environ['QUERY_STRING'])
    rvBuf = scalar.scalar(
            selectPlot = qs.get("selectPlot", [None])[0],
            startDateTime = qs.get("startDateTime", [None])[0],
            endDateTime = qs.get("endDateTime", [None])[0],
            scriptAbsPath = request_script_path
            )
    return rvBuf


def getScalar2Excel(environ):
    from mbp_buoy_vida import scalar2excel
    request_script_path = environ["SCRIPT_NAME"]
    qs = parse_qs(environ['QUERY_STRING'])
    [filename, rvBuf] = scalar2excel.scalar2excel(
            selectPlot = qs.get("selectPlot", [None])[0],
            startDateTime = qs.get("startDateTime", [None])[0],
            endDateTime = qs.get("endDateTime", [None])[0]
            )
    return [filename, rvBuf]

def getTrajectoryHodograph(environ):
    from mbp_buoy_vida import trajectory_hodograph
    request_script_path = environ["SCRIPT_NAME"]
    qs = parse_qs(environ['QUERY_STRING'])
    rvBuf = trajectory_hodograph.trajectory_hodograph(
        endDate=qs.get("endDate", [None])[0],
        endTime=qs.get("endTime", [None])[0],
        selectHeight=qs.get("selectHeight", [None])[0],
        selectDuration=qs.get("selectDuration", [None])[0],
        selectZoom=qs.get("selectZoom", [None])[0],
        selectBuoyPosition=qs.get("selectBuoyPosition", [None])[0],
        selectDateTime=qs.get("selectDateTime", [None])[0],
        selectMaxHeight=qs.get("selectMaxHeight", [None])[0],
        getHodograph=qs.get("selectMaxHeight", [None])[0],
        endDateHidden=qs.get("endDateHidden", [None])[0],
        endTimeHidden=qs.get("endTimeHidden", [None])[0],
        durationHidden=qs.get("durationHidden", [None])[0]
        )
    return rvBuf

def getVector(environ):
    from mbp_buoy_vida import vector
    request_script_path = environ["SCRIPT_NAME"]
    qs = parse_qs(environ['QUERY_STRING'])
    rvBuf = vector.vector(
            selectHeights = string.join(qs.get("selectHeights", [None]), ","),
            startDateTime = qs.get("startDateTime", [None])[0],
            endDateTime = qs.get("endDateTime", [None])[0],
            scriptAbsPath = request_script_path
            )
    return rvBuf

def getVector2Excel(environ):
    from mbp_buoy_vida import vector2excel
    request_script_path = environ["SCRIPT_NAME"]
    qs = parse_qs(environ['QUERY_STRING'])
    [filename, rvBuf] = vector2excel.vector2excel(
            selectHeights = string.join(qs.get("selectHeights", [None]), ","),
            startDateTime = qs.get("startDateTime", [None])[0],
            endDateTime = qs.get("endDateTime", [None])[0]
            )
    return [filename, rvBuf]


def application(environ, start_response):
    status = "200 OK"
    output = "Hello World!"

    request_action = environ["PATH_INFO"]
    response_headers = []
    if request_action == "/index":
        response_headers.append(("Content-type", "text/plain"))
        response_body = getIndex(environ)
    elif request_action == "/dbg":
        response_headers.append(("Content-type", "text/plain"))
        response_body = getDebug(environ)
    elif request_action == "/scalar":
        response_body = getScalar(environ)
        response_headers.append(("Content-type", "text/html"))
    elif request_action == "/scalar2excel":
        [filename, response_body] = getScalar2Excel(environ)
        response_headers.append(("Content-type", "application/octet-stream"))
        response_headers.append(("Content-Disposition", 'attachment; filename="%s"' % filename))
    elif request_action == "/trajectory_hodograph":
        response_body = getTrajectoryHodograph(environ)
        response_headers.append(("Content-type", "text/html"))
    elif request_action == "/vector":
        response_body = getVector(environ)
        response_headers.append(("Content-type", "text/html"))
    elif request_action == "/vector2excel":
        [filename, response_body] = getVector2Excel(environ)
        response_headers.append(("Content-type", "application/octet-stream"))
        response_headers.append(("Content-Disposition", 'attachment; filename="%s"' % filename))
    else:
        response_headers.append(("Content-type", "text/plain"))
        response_body = "n/a"

    response_headers.append(
        ("Content-Length", str(len(response_body)))
        )
    start_response(status, response_headers)

    return [response_body]



if __name__ == '__main__':
    if len(sys.argv) != 3 or sys.argv[1] != "--port":
        print """
This is the WSGI configuration. The file usually isn't ran from
CLI, but still, for debug purposes, the CLI operation is supported
as well.


Usage:
  %s --port <TCP server port number>
""" % sys.argv[0]
        sys.exit(-1)

    tcp_port = 0
    try:
        tcp_port = int(sys.argv[2])
    except:
        print "ERROR: Invalid port specified! Exiting ..."
        sys.exit(-2)

    print "Starting a web server on <localhost>:%d ..." % (tcp_port)
    from wsgiref.simple_server import make_server
    httpd = make_server('localhost', tcp_port, application)
    httpd.serve_forever()
