# -*- coding: utf-8 -*-
"""
/***************************************************************************
 sitnThemes
                                 A QGIS plugin
 Load QGIS projects witth themes likes in online geoportal
                              -------------------
        begin                : 2017-04-13
        git sha              : $Format:%H$
        copyright            : (C) 2017 by om/sitn
        email                : olivier.monod@ne.ch
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, Qt
from PyQt4.QtCore import SIGNAL, QObject, QSize, QRect
from PyQt4.QtGui import QAction, QIcon, QMessageBox
from PyQt4.QtGui import QPushButton, QIcon, QPixmap, QListWidgetItem
# Initialize Qt resources from file resources.py
import resources

# Import the code for the DockWidget
from sitnTheme_dockwidget import sitnThemesDockWidget
import os.path
from themesConfig import themes as themesList
print themesList

class sitnThemes:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface

        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'sitnThemes_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&sitnThemes')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'sitnThemes')
        self.toolbar.setObjectName(u'sitnThemes')

        #print "** INITIALIZING sitnThemes"

        self.pluginIsActive = False
        self.dockwidget = None


    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('sitnThemes', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action


    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/sitnThemes/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u''),
            callback=self.run,
            parent=self.iface.mainWindow())
            

    #--------------------------------------------------------------------------

    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""

        #print "** CLOSING sitnThemes"

        # disconnects
        self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)

        # remove this statement if dockwidget is to remain
        # for reuse if plugin is reopened
        # Commented next statement since it causes QGIS crashe
        # when closing the docked window:
        # self.dockwidget = None

        self.pluginIsActive = False


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""

        #print "** UNLOAD sitnThemes"

        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&sitnThemes'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    #--------------------------------------------------------------------------

    def run(self):
        """Run method that loads and starts the plugin"""

        if not self.pluginIsActive:
            self.pluginIsActive = True

            #print "** STARTING sitnThemes"

            # dockwidget may not exist if:
            #    first run of plugin
            #    removed on close (see self.onClosePlugin method)
            if self.dockwidget == None:
                # Create the dockwidget (after translation) and keep reference
                self.dockwidget = sitnThemesDockWidget()
                QObject.connect(self.dockwidget.listThemes,SIGNAL("itemClicked(QListWidgetItem *)"), self.openSitnTheme) 



            # connect to provide cleanup on closing of dockwidget
            self.dockwidget.closingPlugin.connect(self.onClosePlugin)

            # show the dockwidget
            # TODO: fix to allow choice of dock location
            self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dockwidget)
            self.dockwidget.show()
            self.fillThemes()

    def openSitnTheme(self, item):
        """
        Load the default SelvansGeo QGIS Project
        """
        print item.project_path
        warningTxt = unicode('Ceci annulera les modifications non sauvegardée du projet QGIS ouvert actuellement', 'utf-8')
        reply = QMessageBox.question(self.dockwidget ,'Avertissement!', warningTxt, QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)
        if reply == QMessageBox.Ok:
            self.iface.addProject(item.project_path)
            self.iface.actionOpenProject()
            
    def fillThemes(self):
        """
        Fill the themes list
        """
        # print themes
        themes = themesList
        self.dockwidget.listThemes.clear()
        for theme in themes:

            itm = QThemeItem(theme[1], "");
            itm.setSizeHint(QSize(114,64))
            itm.setToolTip(theme[0])
            itm.setProjectPath(theme[2])
            icon = QIcon()
            pixmap = QPixmap(110, 60)
            path = ":/plugins/sitnThemes/themes/" + theme[1]
            print path
            pixmap.load(path)
            icon.addPixmap(pixmap, QIcon.Normal, QIcon.On)
            itm.setIcon(icon);
            itm.setIcon(icon);
            self.dockwidget.listThemes.addItem(itm)
            
"""
    Subclass the QListWidgetItem in order to add a project_path property
"""        
class QThemeItem(QListWidgetItem):

    def __init__(self, project_path, text):
        self.project_path = project_path
        super(QThemeItem, self).__init__()
        if text != None:
            self.setText(text)

    def setProjectPath(self, project_path):
        self.project_path = project_path