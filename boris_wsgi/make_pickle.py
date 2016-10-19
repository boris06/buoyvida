import matplotlib
matplotlib.use('Agg')         # Force matplotlib to not use any Xwindows backend.
import matplotlib.pyplot as plt 
import numpy as np
from mpl_toolkits.basemap import Basemap
import pickle

F_lat_min = 45.47
F_lat_max = 45.63
F_lon_min = 13.43
F_lon_max = 13.67

fig = plt.figure()
m = Basemap(llcrnrlon=F_lon_min, llcrnrlat=F_lat_min, urcrnrlon=F_lon_max, urcrnrlat=F_lat_max,
            rsphere=(6378137.00, 6356752.3142),
            resolution='f', projection='merc')
# draw coastlines, country boundaries, fill continents.
m.drawcoastlines(linewidth=0.25)
m.drawcountries(linewidth=0.25)
m.fillcontinents(color='beige', lake_color='aqua')
# draw the edge of the map projection region (the projection limb)
m.drawmapboundary(fill_color='aqua')
# draw lat/lon grid lines every five degrees.
m.drawmeridians(np.arange(13, 14, 0.1), labels=[0, 0, 1, 0]) 
m.drawparallels(np.arange(45.4, 45.6, 0.1), labels=[1, 0, 0, 0]) 
pickle.dump(m, open('buoy.trajectory.pickle', 'wb'), -1)  # pickle it
plt.show()
