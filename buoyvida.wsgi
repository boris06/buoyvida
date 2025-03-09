#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from cgi import parse_qs
import sys
# import string
import os
import magic

__all__ = ["index", "scalar", "scalar2excel", "vector", "vector2excel", "trajectory_hodograph"]
_mbp_module_name = "mbp_buoy_vida"

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


def getVector(environ):
    from mbp_buoy_vida import vector
    request_script_path = environ["SCRIPT_NAME"]
    qs = parse_qs(environ['QUERY_STRING'])
    selectHeights = qs.get("selectHeights", [None])
    try:
        selectHeights = ",".join(selectHeights)
    except:
        pass
    rvBuf = vector.vector(
            selectHeights = selectHeights,
            startDateTime = qs.get("startDateTime", [None])[0],
            endDateTime = qs.get("endDateTime", [None])[0],
            scriptAbsPath = request_script_path
            )
    return rvBuf


def getVector2Excel(environ):
    from mbp_buoy_vida import vector2excel
    request_script_path = environ["SCRIPT_NAME"]
    qs = parse_qs(environ['QUERY_STRING'])
    selectHeights = qs.get("selectHeights", [None])
    try:
        selectHeights = ",".join(selectHeights)
    except:
        pass
    [filename, rvBuf] = vector2excel.vector2excel(
            selectHeights = selectHeights,
            startDateTime = qs.get("startDateTime", [None])[0],
            endDateTime = qs.get("endDateTime", [None])[0]
            )
    return [filename, rvBuf]


def getTrajectoryHodograph(environ):
    from mbp_buoy_vida import trajectory_hodograph
    import pathlib
    scriptUrl = environ["SCRIPT_NAME"]
    thisFileDirectoryPath = pathlib.Path(__file__).parent.resolve();
    mbpModuleDirectoryPath = "%s/%s" % (thisFileDirectoryPath, _mbp_module_name)
    qs = parse_qs(environ['QUERY_STRING'])

    formOp = trajectory_hodograph.FORM_OP_NONE
    if "getTrajectory" in qs.keys():
        formOp = trajectory_hodograph.FORM_OP_GET_TRAJECTORY
    elif "getHodograph" in qs.keys():
        formOp = trajectory_hodograph.FORM_OP_GET_HODOBRAPH

    rvBuf = trajectory_hodograph.trajectory_hodograph(
        scriptsRootDir = mbpModuleDirectoryPath,
        endDate = qs.get("endDate", [None])[0],
        endTime = qs.get("endTime", [None])[0],
        selectHeight = qs.get("selectHeight", [None])[0],
        selectDuration = qs.get("selectDuration", [None])[0],
        selectZoom = qs.get("selectZoom", [None])[0],
        selectBuoyPosition = qs.get("selectBuoyPosition", [None])[0],
        selectDateTime = qs.get("selectDateTime", [None])[0],
        selectMaxHeight = qs.get("selectMaxHeight", [None])[0],
        formOp = formOp,
        endDateHidden = qs.get("endDateHidden", [None])[0],
        endTimeHidden = qs.get("endTimeHidden", [None])[0],
        durationHidden = qs.get("durationHidden", [None])[0],
        scriptAbsUrl = scriptUrl
        )
    return rvBuf


def application(environ, start_response):
    status = "200 OK"
    # output = "Hello World!"

    request_action = environ["PATH_INFO"]
    response_headers = []
    if request_action == "/index":
        response_headers.append(("Content-type", "text/plain; charset=utf-8"))
        response_body = getIndex(environ)
    elif request_action == "/dbg":
        response_headers.append(("Content-type", "text/plain; charset=utf-8"))
        response_body = getDebug(environ)
    elif request_action == "/scalar":
        response_body = getScalar(environ)
        response_headers.append(("Content-type", "text/html; charset=utf-8"))
    elif request_action == "/scalar2excel":
        [filename, response_body] = getScalar2Excel(environ)
        response_headers.append(("Content-type", "application/octet-stream"))
        response_headers.append(("Content-Disposition", 'attachment; filename="%s"' % filename))
    elif request_action == "/vector":
        response_body = getVector(environ)
        response_headers.append(("Content-type", "text/html; charset=utf-8"))
    elif request_action == "/vector2excel":
        [filename, response_body] = getVector2Excel(environ)
        response_headers.append(("Content-type", "application/octet-stream"))
        response_headers.append(("Content-Disposition", 'attachment; filename="%s"' % filename))
    elif request_action == "/trajectory_hodograph":
        response_body = getTrajectoryHodograph(environ)
        response_headers.append(("Content-type", "text/html; charset=utf-8"))
    else:
        import pathlib
        reqPath = environ['PATH_INFO']
        reqPath = reqPath[1:] if reqPath.startswith('/') else reqPath
        thisDirPath = pathlib.Path(__file__).parent.resolve();
        fullReqPath = os.path.join(thisDirPath, reqPath[:])
        print(f"thisDirPath = '{thisDirPath}' / reqPath = '{reqPath}' / fullReqPath = '{fullReqPath}'")
        if reqPath == "/":
            reqPath = "/index.html"
        if  os.path.exists(fullReqPath) and os.path.isdir(fullReqPath):
            err_message = f"Directory listing is not allowed!"
            print(f"ERROR: {err_message} Request for {reqPath} denied, HTTP.404 is going to be returned.")
            status = "404 Not Found"
            response_body = b' '
            response_headers.append(("Content-type", "text/html"))
        elif os.path.exists(fullReqPath) and os.path.isfile(fullReqPath):
            mime_type = "text/plain"
            fileExtension = fullReqPath[fullReqPath.rfind('.'):]
            if fileExtension.lower() in ['.jpg', '.gif', '.ico', '.png', '.jpeg', '.html', '.htm', '.txt']:
                print(f"Returning file with extension '{fileExtension}' - fullReqPath='{fullReqPath}'")
                with open(fullReqPath, 'rb') as file:
                    response_body = file.read()
                if len(response_body) > 0:
                    mime_type = magic.from_buffer(response_body, mime=True)
                    print(f"mime_type = '{mime_type}'")
                else:
                    if reqPath.endswith(".html") or reqPath.endswith(".htm"):
                        mime_type = "text/html"
                    response_body = b'';
            else:
                print(f"Returning files with extension '{fileExtension}' is NOT allowed - fullReqPath='{fullReqPath}'")
                status = "404 Not Found"
                response_body = b' '
            response_headers.append(("Content-type", mime_type))
        else:
            print(f"!!! File NOT FOUND {fullReqPath} !!!")
            status = "404 Not Found"
            response_body = b' '
            response_headers.append(('Content-Type', 'text/plain'))
    start_response(status, response_headers)
    response_type = list(filter(lambda h : h[0].lower() == "content-type"  , response_headers))[0][1]
    is_response_text = response_type.startswith("text/")
    print(f"""
Request:
----
REQUEST_METHOD:  '{environ['REQUEST_METHOD']}'
PATH_INFO:  '{environ['PATH_INFO']}'
QUERY_STRING:  '{environ['QUERY_STRING'] if 'QUERY_STRING' in environ else ""}'
HTTP_REFERER:  '{environ['HTTP_REFERER'] if 'HTTP_REFERER' in environ else ""}'
HTTP_ACCEPT:  '{environ['HTTP_ACCEPT'] if 'HTTP_ACCEPT' in environ else ""}'
HTTP_USER_AGENT:  '{environ['HTTP_USER_AGENT'] if 'HTTP_USER_AGENT' in environ else ""}'
HTTP_ACCEPT_ENCODING:  '{environ['HTTP_ACCEPT_ENCODING'] if 'HTTP_ACCEPT_ENCODING' in environ else ""}'
HTTP_ACCEPT_LANGUAGE:  '{environ['HTTP_ACCEPT_LANGUAGE'] if 'HTTP_ACCEPT_LANGUAGE' in environ else ""}'
----

Response:""", end='')

    if is_response_text:
        print("----")
        print(f"{response_body if len(response_body) < 100 else f'{response_body[:96]} ...'}")
    else:
        print(f"---- type: {response_type} ----")
    print("----")

    return [response_body.encode("utf-8") if isinstance(response_body, str) else response_body]


# Python3 changes: START
from wsgiref.util import setup_testing_defaults

def simple_app(environ, start_response):
    setup_testing_defaults(environ)

    status = '200 OK'
    headers = [('Content-type', 'text/plain; charset=utf-8')]

    start_response(status, headers)

    ret = [("%s: %s\n" % (key, value)).encode("utf-8")
           for key, value in environ.items()]
    return ret
# Python3 changes: END

if __name__ == '__main__':
    if len(sys.argv) != 3 or sys.argv[1] != "--port":
        print(f"""
This is the WSGI configuration. The file usually isn't ran from
CLI, but still, for debug purposes, the CLI operation is supported
as well.


Usage:
  {sys.argv[0]} --port <TCP server port number>
""")
        sys.exit(-1)

    tcp_port = 0
    try:
        tcp_port = int(sys.argv[2])
    except:
        print("ERROR: Invalid port specified! Exiting ...")
        sys.exit(-2)

    print(f"Starting a web server on <localhost>:{tcp_port} ...")
    from wsgiref.simple_server import make_server
    with make_server('0.0.0.0', tcp_port, application) as httpd:
        httpd.serve_forever()
