import gtk
import cairo
import array
import math
import logging
import time

from threading import Thread
from sensor_area import SensorArea
from sensor import Sensor
from config import Config
from clustering.kmeans import KMeans
from clustering.fcmeans import FCMeans
import map_handler
import image_handler


class Controller:

    def __init__(self, gui=False):
        self.gui = gui
        if self.gui:
            self.init_gtk_variables()

        # log_filename = time.strftime("%d-%m-%Y_%H:%M:%S") + '.log'
        # logging.basicConfig(filename=self.cfg.appRootDir + "/" + log_filename, level=logging.INFO)
        # logging.info(time.asctime(time.localtime(time.time())))

    def init_gtk_variables(self):
        """
        GUI elements and main module initialization

        :param
            da         - drawing area to draw map, grids, clusters, and sensors
            sa         - Sensor Area instance (sensor deployment methods)
            background - map (satellite image)
            cfg        - Config instance for global parameters

            colors     - for drawing clusters' numbers and priorities
            pi2        - for drawing sensors

            gui.glade  - glade file for GUI
            selectedGrid (int) - selected grid on GUI
        """
        self.init_params()

        gtk.gdk.threads_init()

        self.colors = [[0.9, 0.0, 0.0], [0.0, 0.9, 0.0], [0.0, 0.0, 0.9],
                       [0.75, 0.0, 0.75], [0.0, 0.75, 0.75], [0.75, 0.75, 0.0]]
        self.pi2 = 2 * math.pi

        # load glade file
        builder = gtk.Builder()
        builder.add_from_file(self.cfg.appRootDir + "/gui.glade")

        # connect signals
        builder.connect_signals(self)
        window = builder.get_object("window1")
        window.connect("destroy", gtk.main_quit)

        # get objects
        self.fileImportImage = builder.get_object("fileImportImage")
        self.txtLocationSearch = builder.get_object("txtLocationSearch")
        self.txtZoomLevel = builder.get_object("txtZoomLevel")
        self.txtRadius = builder.get_object("txtRadius")
        self.txtClusterCount = builder.get_object("txtClusterCount")
        self.txtPriority = builder.get_object("txtPriority")
        self.lblPriority = builder.get_object("lblPriority")
        self.txtSensorCount = builder.get_object("txtSensorCount")
        self.txtSaveImage = builder.get_object("txtSaveImage")
        self.observeDeploymentCheck = builder.get_object("observeDeploymentCheck")

        self.reset_text_entries()

        self.da = builder.get_object("drawingArea")
        self.da.set_events(gtk.gdk.EXPOSURE_MASK
                           | gtk.gdk.LEAVE_NOTIFY_MASK
                           | gtk.gdk.BUTTON_PRESS_MASK
                           | gtk.gdk.POINTER_MOTION_MASK
                           | gtk.gdk.POINTER_MOTION_HINT_MASK)

        # set size and show window
        window.set_size_request(self.cfg.width + 260, self.cfg.height + 20)
        window.show_all()
        self.drawable = self.da.window
        gtk.main()

    def init_params(self, width=640, height=480, radius=33):
        self.cfg = Config(width=width, height=height, radius=radius)
        self.sa = SensorArea(self.cfg)
        self.background = None
        self.selectedGrid = -1

    def reset_text_entries(self):
        self.txtRadius.set_text(str(self.cfg.radius))
        self.txtClusterCount.set_text(str(self.cfg.clusterCnt))
        self.txtSensorCount.set_text(str(self.cfg.sensorCnt))
        self.txtSaveImage.set_text(time.strftime("%d-%m-%Y_%H:%M:%S"))

    def toggle_observe(self, widget):
        """
        Adding itself as the observer of the deployment
        it is attachable-detachable during the run of the deployment
        """
        if widget.get_active():
            self.sa.attach(self)
        else:
            self.sa.detach(self)

    def clear_all_area(self, widget):
        """
        clear all sensor area with new Sensor Area instance
        """

        self.init_params(self.cfg.width, self.cfg.height, self.cfg.radius)
        self.reset_text_entries()

        self.draw_again()

    def clear_deployment(self, widget):
        """
        removing sensors from sensor area
        """
        self.sa.clear_deployment()

        self.draw_again()

    # MAP AND IMAGE FUNCTIONS
    def search_location(self, loc="", zoom=15):
        """
        search location on google map with name, coordinates etc.

        :param
            location (string)   - name of location, coordinates etc.
            zoom (int)          - zoom ratio for google map
            imgSize (int tuple) - map size

        :return
            saved and loaded map image from google map
        """

        try:
            if self.gui:
                loc = self.txtLocationSearch.get_text()
                zoom = int(self.txtZoomLevel.get_text())

            imgSize = (self.cfg.width, self.cfg.height + self.cfg.gMapCrop)

            googleMap = map_handler.get_google_map(imgDir=self.cfg.imgDir, center=loc, zoom=zoom, imgSize=imgSize)
            self.load_image(googleMap, self.cfg.gMapCrop)

        except ValueError as e:
            print "ValueError:", e

    def import_image(self, widget):
        """
        import map manually
        """
        imgDir = self.fileImportImage.get_filename()
        self.load_image(imgDir, self.cfg.gMapCrop)

    def load_image(self, imgDir, crop=0):
        """
        loading map which searched on google map or import manual for Drawing Area and Sensor Area object

        :param
            imgDir (string) - saved image location
            crop (int)      - cut google logo from map

        :return
            imageFile - loaded image file for Sensor Area object
            imgd      - loaded image for Drawing Area
        """

        imageFile, imgd = image_handler.load_image(imgDir, self.cfg.width, self.cfg.height, crop)

        if imageFile and imgd:
            self.sa.import_satellite_image(imageFile)

            a = array.array('B', imgd)
            self.background = cairo.ImageSurface.create_for_data(a, cairo.FORMAT_ARGB32, self.cfg.width, self.cfg.height)

            self.draw_again()

    def save_image(self, imageName):
        imgDir = self.cfg.appRootDir + "/images/" + imageName + ".png"
        drawable = self.drawable

        pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, 0, 8, *drawable.get_size())
        pixbuf = pixbuf.get_from_drawable(drawable, drawable.get_colormap(), 0, 0, 0, 0, *drawable.get_size())
        pixbuf.save(imgDir, 'png')

    def toggle_save_image(self, widget):
        """
        save image to file
        """

        imageName = self.txtSaveImage.get_text()

        self.save_image(imageName)

    # SENSOR FUNCTIONS
    def set_radius(self, widget):
        """
        set sensor radius

        :param
            radius (int) - new radius length for each sensor

        :return
            new Config object and Sensor Area instances
            selectedGrid - reset to -1
        """
        try:
            radius = int(self.txtRadius.get_text())

            if radius > 0:
                self.cfg.radius = radius
                self.clear_all_area(widget)

                self.selectedGrid = -1
                self.draw_again()

        except ValueError as e:
            print "ValueError:", e

    def set_priority(self, clusterNum=0, priority=0.0):
        """
        set priority to selected grid and to other grids which in the same cluster with selected grid

        :param
            selectedGrid (int) - selected grid on GUI
            priority (float)   - set priority value for selected grid
            sizeRatio (float)  - ratio of grid's area, priority value will reduce with this value

        :return
            set priority value for all grids which in the same cluster with selected grid
        """

        if not self.gui or (self.selectedGrid >= 0 and self.cfg.clusterCnt > 0):
            try:
                if self.gui:
                    priority = float(self.txtPriority.get_text())
                    clusterNum = self.sa.grids[self.selectedGrid].clusterNum

                if priority >= 0:
                    self.cfg.clusterPriorities[clusterNum] = priority

                    for grid in self.sa.grids:
                        if grid.clusterNum == clusterNum:
                            grid.priority = priority * grid.sizeRatio

                else:
                    raise ValueError("Invalid range for priority value")

            except ValueError as e:
                print "ValueError:", e

        elif self.selectedGrid < 0:
            print "Please select grid!"
        else:
            print "No cluster!"

        self.draw_again()

    # CLUSTERING FUNCTIONS
    def clustering(self, clusterCnt):
        """
        find clusters for grids

        :param
            clusterCnt (int)  - total cluster count
            input data (list) - grids' color average and standard deviation values
            clusterPriorities (float list) - initialize cluster priorities list

        :return
            cluster number for each grid
        """

        if (clusterCnt > 0) and (len(self.sa.grids) > clusterCnt):
            self.cfg.clusterCnt = clusterCnt
            self.cfg.clusterPriorities = [0 for i in range(clusterCnt)]

            inp = [grid.colorAvg + grid.colorStdDev for grid in self.sa.grids]
            clusters = self.cfg.clusteringMethod.cluster(inp, clusterCnt)

            for i, grid in enumerate(self.sa.grids):
                grid.clusterNum = clusters[i]

            return clusters

        else:
            raise ValueError("Invalid range for cluster count value")

    def clustering_get_cnt(self, clusterCnt):
        try:
            if self.gui:
                clusterCnt = int(self.txtClusterCount.get_text())

            self.clustering(clusterCnt)

        except ValueError as e:
            print "ValueError:", e

    def run_kmeans(self, clusterCnt=3):
        """
        clustering with K-Means algorithm
        """
        self.cfg.clusteringMethod = KMeans()
        self.clustering_get_cnt(clusterCnt)

        self.draw_again()

    def run_fcmeans(self, clusterCnt=3):
        """
        clustering with Fuzzy C-Means algorithm
        """

        self.cfg.clusteringMethod = FCMeans()
        self.clustering_get_cnt(clusterCnt)

        self.draw_again()

    # DEPLOYMENT FUNCTIONS
    def deployment(self, deploymentMethods, sensorCnt):
        """
        call priority queue deployment and optimization

        :param
            deploymentMethods (function list) - to call deployment methods (pq, random, and simulated annealing)
        """

        try:
            if self.gui:
                sensorCnt = int(self.txtSensorCount.get_text())

            if sensorCnt > 0:
                self.cfg.sensorCnt = sensorCnt

                for deploymentMethod in deploymentMethods:
                    startTime = time.time()
                    deploymentMethod()
                    print "({totalTime} sec.)".format(totalTime=round(time.time() - startTime, 2))

            else:
                raise ValueError("Invalid range for sensor count value")

        except ValueError as e:
            print "ValueError:", e

        self.draw_again()

    def deploy_random(self, sensorCnt=75):
        """
        call random deployment method
        """

        deploymentMethods = [self.sa.random_deployment]
        self.deployment(deploymentMethods, sensorCnt)

    def deploy_simulated_annealing(self, sensorCnt=75):
        """
        call simulated annealing optimization method with priority queue deployment
        """

        # deploymentMethods = [self.sa.pq_deployment], self.sa.simulated_annealing]
        deploymentMethods = [self.sa.genetic_algorithms] # , self.sa.simulated_annealing]
        self.deployment(deploymentMethods, sensorCnt)

    def start_deployment(self, deploymentMethods, sensorCnt):
        Thread(target=self.deployment, args=(deploymentMethods, sensorCnt)).start()
        # TODO: in exit this thread must be cleaned if it is running still

    # MOUSE EVENT FUNCTIONS
    def button_press_event(self, *args):
        """
        mouse events handler

        :param
            left mouse button - grid selecting
            right mouse button - grid deselecting
            middle mouse button - sensor adding
        """

        event = args[1]

        column = int(math.ceil(float(event.x) / self.cfg.gridEdge))
        row = int(math.ceil(float(event.y) / self.cfg.gridEdge))

        gridNumber = self.cfg.columnCnt * (row - 1) + column - 1

        # select grid (left mouse button)
        if event.button == 1:
            self.selectedGrid = gridNumber
            priority = self.sa.grids[self.selectedGrid].priority

            if priority != 0:
                self.txtPriority.set_text(str(priority))
            else:
                self.txtPriority.set_text('')

        # deselect grid (right mouse button)
        elif event.button == 3 and self.selectedGrid == gridNumber:
            self.selectedGrid = 0
            self.txtPriority.set_text('')

        # TODO: sensor id start from 0 or what?
        # add sensor (middle mouse button)
        elif event.button == 2:
            if self.sa.pixels and self.cfg.clusterCnt > 0:
                sensor = Sensor(self.cfg.sensorCnt, event.x, event.y)
                sensor.priority, c = self.sa.cover_and_priority(sensor.xPos, sensor.yPos, sensor.sensorId)

                self.sa.sensors.append(sensor)
                self.cfg.sensorCnt += 1

        self.draw_again()

    def key_press_event(self, *args):
        event = args[1]
        key = gtk.gdk.keyval_name(event.keyval)
        print key

    def do_expose_event(self, widget, event):
        self.cr = self.da.window.cairo_create()
        self.cr.rectangle(event.area.x, event.area.y, event.area.width, event.area.height)
        self.cr.clip()
        self.draw(self.sa.sensors)

    def draw_again(self):
        """
        method to trigger redraw of the screen
        """
        if self.gui:
            self.da.queue_draw()

    def update(self, subject, message):
        """
        method which is triggered by subject
        it is used for observing the subject (sensor_area)
        """

        if message:
            logging.info(message)
        self.draw_again()

    def draw(self, sensors):
        """
        drawing map, grids, clusters, and sensors to sensor area
        """

        width = self.cfg.width
        height = self.cfg.height
        radius = self.cfg.radius
        gridEdge = self.cfg.gridEdge

        cr = self.cr

        def draw_background():
            if self.background:
                cr.set_source_surface(self.background, 0, 0)
                cr.paint_with_alpha(1.0)  # transparent paint

        def draw_grids():
            cr.set_source_rgb(0.0, 0.0, 0.0)
            cr.set_line_width(0.3)

            for i in range(gridEdge, height, gridEdge):
                cr.move_to(0, i)
                cr.line_to(width, i)
                cr.stroke()

            for i in range(gridEdge, width, gridEdge):
                cr.move_to(i, 0)
                cr.line_to(i, height)
                cr.stroke()

        def draw_clusters():
            cr.save()

            for g in self.sa.grids:
                if len(self.cfg.clusterPriorities) > 0:
                    color = self.colors[g.clusterNum]
                    cr.set_source_rgb(color[0], color[1], color[2])

                    cr.select_font_face("Georgia", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)

                    cr.set_font_size(radius)
                    cnXBearing, cnYBearing, cnWidth, cnHeight = cr.text_extents(str(g.clusterNum))[:4]
                    cr.move_to(g.xPos - cnWidth/2 - cnXBearing, g.yPos - cnHeight/2 - cnYBearing)

                    cr.show_text(str(g.clusterNum))
                    cr.stroke()

                    cr.set_font_size(radius/1.8)
                    pvXBearing, pvYBearing, pvWidth, pvHeight = cr.text_extents(str(round(g.priority, 2)))[:4]
                    cr.move_to(g.xPos - pvWidth/2 - pvXBearing, g.yPos - cnHeight/2 - (pvHeight * 1.5) - pvYBearing)

                    cr.show_text(str(round(g.priority, 2)))
                    cr.stroke()

            cr.restore()

        def draw_selected_grid():
            if self.selectedGrid > 0:
                cr.set_source_rgb(1.0, 0.0, 0.0)
                cr.set_line_width(2.0)

                xPos = self.sa.grids[self.selectedGrid].xPos
                yPos = self.sa.grids[self.selectedGrid].yPos

                cr.rectangle(xPos - radius,  yPos - radius, gridEdge, gridEdge)
                cr.stroke()

                self.lblPriority.set_text('Priority (' + str(self.selectedGrid) + '):')
            else:
                self.lblPriority.set_text('Priority ():')

        def draw_sensors():
            cr.set_source_rgb(1.0, 1.0, 1.0)
            cr.set_line_width(1.4)

            for s in sensors:
                cr.arc(s.xPos, s.yPos, radius, 0, self.pi2)
                cr.stroke()

                cr.set_font_size(radius / 2.5)
                cnXBearing, cnYBearing, cnWidth, cnHeight = cr.text_extents(str(s.sensorId))[:4]
                cr.move_to(s.xPos - cnWidth/2 - cnXBearing, s.yPos - cnHeight/2 - cnYBearing)

                cr.show_text(str(s.sensorId))
                cr.stroke()

                cr.set_font_size(radius / 2.5)
                pvXBearing, pvYBearing, pvWidth, pvHeight = cr.text_extents(str(round(s.priority, 2)))[:4]
                cr.move_to(s.xPos - pvWidth/2 - pvXBearing, s.yPos + cnHeight/2 + pvHeight/2 - pvYBearing)

                cr.show_text(str(round(s.priority, 2)))
                cr.stroke()

        draw_background()
        draw_grids()
        draw_clusters()
        draw_selected_grid()
        draw_sensors()

    def on_window1_destroy(self, widget):
        self.exit(widget)

    def exit(self, widget):
        print "quit"
        gtk.main_quit()


if __name__ == "__main__":
    controller = Controller(gui=True)
