###Title: Dynamic overview of selected data from the oceanographic buoy.

####Author: Boris Petelin, National Institute of Biology, Marine Biology Station Piran, Slovenia

####Date: December, 2015

####Description

The following files should be placed into subdirectory *cgi-bin* of the directory where cgi-bin server is running.

#####List of files:
* readme.md ... this file
* cgi-bin/buoydef.py ... Python definitions required for the access to mySQL database and plotting graphs 
* cgi-bin/buoyvida.py ... Python code accessing the mySQL database and plotting graphs 
* cgi-bin/buoy_scalar.py ... buoy data scalar plot
* cgi-bin/buoy_vector.py ...  buoy data vector plot
* cgi-bin/scalar2excel.py ... routine for saving the vector data to MS Excel
* cgi-bin/vector2excel.py ... routine for saving the scalar data to MS Excel

####Prerequisites

The following prerequisites must be installed on the server:

* **Python** 2.7 or higher (https://www.python.org/).
* **Matplotlib** - python 2D plotting library (http://matplotlib.org/).
* **Python cgi** - support module for Common Gateway Interface (CGI) scripts (https://docs.python.org/2/library/cgi.html).
* **Python cgi server** - see relevant webpages, for example, http://httpd.apache.org/docs/2.2/howto/cgi.html.
* **Python openpyxl** - Python library to read/write Excel 2010 xlsx/xlsm/xltx/xltm files (https://pypi.python.org/pypi/openpyxl).
* **Python MySQLdb** - Python interface to MySQL (https://pypi.python.org/pypi/MySQL-python/)

####Running the webpage

* on the web server: http://website_running_python_cgi//cgi-bin/buoy_scalar.py  
http://localhost:8000/cgi-bin/buoy_vector.py

* on the localhost: http://localhost:8000/cgi-bin/buoy_scalar.py  
http://localhost:8000/cgi-bin/buoy_vector.py
