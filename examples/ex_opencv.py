#
# Opencv example using geotiler
#
"""
Create an object containing a geotiler object and convert the resulting
image to an opencv image in order to show it.
Also contains functions to plot points on the resulting map
Zooming is also possible with the mousewheel and + and - keys

Requirements:

- geotiler
- opencv
- numpy (also required by opencv)
"""

import geotiler
import cv2
import numpy as np


RED = (0, 0, 255)
BLUE = (255, 0, 0)
GREEN = (0, 255, 0)


class MapObject:
    def __init__(self, center: tuple=(0.0, 51.47879),
                 zoom: int=15, size: tuple=(1900, 1000)):
        """
            MapObject constructor
            Creates a open cv compatible map image of requested size,
            zoom level and coordinates.
            After creating the object the map can be displayed using
            cv2.imShow('window name',MapObject.img) and cv2.waitKey(10)
            Keyword arguments:
                center (Optional[tuple]) -- center coordinates of the map tuple
                (lon,lat) (default 0.0,51.47879) (Greenwich)
                zoom (Optional[int]) -- zoom level of the map, int between
                3 and 19 (default 15)
                size (Optional[int]) -- resolution of the resulting image
                (default (1900,1000)) (good for full HD monitor)
        """
        self.mm = geotiler.Map(center=center, zoom=zoom, size=size)
        self.mapmarkers = []
        self.updatemap()

    def updatemap(self):
        """
            Download new maptiles and redraw everyting on the map
        """
        self.pilImage = geotiler.render_map(self.mm)
        self.drawMap()

    def drawMap(self):
        """
            Draw the map again, to redownload the maptiles use updatemap()
            If you want to draw things on the map, call your function from here
        """
        self.img = cv2.cvtColor(np.array(self.pilImage)[:, :, :3],
                                cv2.COLOR_RGB2BGR)
        self.plotPoint(self.mapmarkers)

    def zoomIn(self):
        """
            Zoom in, this functions downloads a new map
        """
        if self.mm.zoom < 19:
            self.mm.zoom += 1
        self.updatemap()

    def zoomOut(self):
        """
            Zoom out, this function dowmloads a new map
        """
        if self.mm.zoom > 3:
            self.mm.zoom -= 1
        self.updatemap()

    def plotPoint(self, markers):
        """
            Draws a circle at all the points in the list self.mapmarkers[]
        """
        for lon, lat in markers:
            x, y = self.mm.rev_geocode((lon, lat))
            cv2.circle(self.img, center=(int(x), int(y)), radius=5,
                       color=RED, thickness=-1)

    def mouse_callback(self, event, x, y, flag=0, param=None):
        """
            mouse_callback function for use with the cv2.setMouseCallback()
            Left-clicking in the windows will add a point to self.mapmarkers[]
            Richt-clicking will remove a point from self.mapmarkers[]
            Scrolling will zoom in or outat the location the mouse is pointing
        """
        if event == cv2.EVENT_MOUSEWHEEL:
            if flag > 0:  # Scroll up
                self.mm.center = self.mm.geocode((x, y))
                self.zoomIn()
            elif flag < 0:    # Scroll down
                self.mm.center = self.mm.geocode((x, y))
                self.zoomOut()
        elif event == cv2.EVENT_LBUTTONUP:
            self.mapmarkers.append(self.mm.geocode((x, y)))
            self.drawMap()
        elif event == cv2.EVENT_RBUTTONUP:
            if len(self.mapmarkers) > 0:
                del self.mapmarkers[-1]
                self.drawMap()
            else:
                print('Nothing to delete')


# Create the map object and call it "kaart"(dutch for map)
kaart = MapObject()
# Create a window called window and have it adjust in size automatically
cv2.namedWindow('window', cv2.WINDOW_AUTOSIZE)
# Create the mousecallback in the window called "window"
cv2.setMouseCallback('window', kaart.mouse_callback)


while 1:
    # Show the image in "window"
    cv2.imshow('window', kaart.img)
    # OpenCV doesn't show anything untill the waitKey function is called
    key = cv2.waitKey(20)
    # when Esc is pressed: close all opencv windows and break
    if (key == 27):
        cv2.destroyAllWindows()
        break
    elif key == 43:  # "+" key
        kaart.zoomIn()
    elif key == 45:   # "-" key
        kaart.zoomOut()
