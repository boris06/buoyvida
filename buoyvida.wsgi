#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from cgi import parse_qs
import sys
import string
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
        selectHeights = string.join(selectHeights, ",")
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
        selectHeights = string.join(selectHeights, ",")
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
    request_script_url = environ["SCRIPT_NAME"]
    scriptsRootDir = "%s/%s" % (environ["CONTEXT_DOCUMENT_ROOT"], _mbp_module_name)
    qs = parse_qs(environ['QUERY_STRING'])

    formOp = trajectory_hodograph.FORM_OP_NONE
    if qs.has_key("getTrajectory"):
        formOp = trajectory_hodograph.FORM_OP_GET_TRAJECTORY
    elif qs.has_key("getHodograph"):
        formOp = trajectory_hodograph.FORM_OP_GET_HODOBRAPH

    rvBuf = trajectory_hodograph.trajectory_hodograph(
        scriptsRootDir = scriptsRootDir,
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
        scriptAbsUrl = request_script_url
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
        req_path = environ['PATH_INFO']
        if os.path.exists(f"./{req_path}") and os.path.isdir(f"./{req_path}"):
            err_message = f"Directory listing is not allowed!"
            print(f"ERROR: {err_message} Request for {req_path} denied, HTTP.404 is going to be returned.")
            status = "404 Not Found"
            response_body = err_message
        elif os.path.exists(f"./{req_path}") and os.path.isfile(f"./{req_path}"):
            with open(f"./{req_path}", 'rb') as file:
                response_body = file.read()
            if len(response_body) > 0:
                mime_type = magic.from_buffer(response_body, mime=True)
            else:
                if req_path.endswith(".html") or req_path.endswith(".htm"):
                    mime_type = "text/html"
                else:
                    mime_type = "text/plain"
                response_body = '';
            response_headers.append(("Content-type", mime_type))
        else:
            print(f"!!! NOT FOUND {req_path} !!!")
            status = "404 Not Found"
            response_body = "Not Found"
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

Response:
""")

    if is_response_text:
        print("----")
        print(f"{response_body}")
    else:
        print(f"---- type: {response_type} ----")
    print("----")

    return [response_body.encode("utf-8") if is_response_text else response_body]


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
    with make_server('localhost', tcp_port, application) as httpd:
        httpd.serve_forever()
