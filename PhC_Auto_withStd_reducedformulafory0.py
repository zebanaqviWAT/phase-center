# -*- coding: utf-8 -*-

################################################################################
# Phase Center App - using PySide6 for UI and pyaedt
# Author : Zeba Naqvi
# Last tested with pyaedt version 0.5.7, pyqtgraph 0.12.4
#
# Qt User Interface Compiler version 6.3.0
#
################################################################################
import math
import os

from scipy.spatial.transform import Rotation
import sys, time, numpy as np
from pyaedt import Hfss
from PySide6.QtCore import (Qt, QCoreApplication, QRegularExpression, QMetaObject, QRect)
from PySide6.QtGui import (QAction, QRegularExpressionValidator, QIcon, QCloseEvent, QPixmap)
from PySide6.QtWidgets import (QApplication, QMainWindow, QCheckBox, QComboBox, QGroupBox, QLabel, QMenu, QMenuBar, \
                               QLineEdit, QPushButton, QWidget, QMessageBox, QStatusBar)
from pyqtgraph import PlotWidget
import pyqtgraph


class UiPhaseCenter1(QMainWindow):

    def setup_ui(self, phase_center):

        comboBoxHeight = 22
        comboBoxWidth = 56
        # origin_width = 31
        self.setWindowIcon(QIcon('antenna-icon-614x460.png'))

        self.theta_step = 1
        self.thetascale = 1  # if thetascale =1, it will use 1st point before and after 0. If thetascale=2,
        # 2nd point before and after 0 : these 3 points are used by phase center calculation algorithm
        self.phi_step = 1
        self.LINECOLORS = ['r', 'g', 'b', 'c', 'm', 'y', 'k']
        self.numCurves = 0
        self.plotRange = 10  # the phase vs theta plot in the plot widget ranges from - to + plotRange
        pattern = '[-]*[0-9]+[.]?[0-9]*'
        reg = QRegularExpression(pattern)
        regValidator = QRegularExpressionValidator(reg)
        self.PC_CS_name = "Z_At_max_rETot"
        self.PC_CS_name_auto = self.PC_CS_name
        self.Inf_global = "3D"
        self.Inf_PC = "InfSphere"
        self.Inf_PC_auto = self.Inf_PC
        self.ffData = 0
        self.hfss = Hfss(specified_version="2023.1", new_desktop_session=False,
                         non_graphical=False)  # ,projectname="D:\\phase-center\\Patch_Radome_Scan60.aedt")
        self.cuts = {"Phi": {}, "Theta": {}}
        # print("Frequency ########## ",self.hfss.setups[0].props["Frequency"])
        if not self.hfss.setups[0].is_solved:
            self.reset()
            dlg = QMessageBox()
            dlg.setWindowTitle("Error")
            dlg.setText("Setup not solved!")
            self.hfss.release_desktop(False, False)
            button = dlg.exec()
            if button == QMessageBox.Ok:
                sys.exit()

        # time.sleep()

        if not phase_center.objectName():
            phase_center.setObjectName(u"PhaseCenter")
        phase_center.resize(650, 700)  # (731, 674)
        self.actionHow_to_Use = QAction(phase_center)
        self.actionHow_to_Use.setObjectName(u"actionHow_to_Use")

        self.centralwidget = QWidget(phase_center)
        self.centralwidget.setObjectName(u"centralwidget")

        self.groupBox_UserInput = QGroupBox(self.centralwidget)
        self.groupBox_UserInput.setObjectName(u"groupBox_UserInput")
        self.groupBox_UserInput.setGeometry(QRect(10, 20, 150, 170))

        self.label_Polarization = QLabel(self.groupBox_UserInput)
        self.label_Polarization.setObjectName(u"label_Polarization")
        self.label_Polarization.setGeometry(QRect(10, 20, 61, 16))

        self.comboBox_Polarization = QComboBox(self.groupBox_UserInput)
        self.comboBox_Polarization.addItem("")
        self.comboBox_Polarization.addItem("")
        self.comboBox_Polarization.addItem("")
        self.comboBox_Polarization.addItem("")
        self.comboBox_Polarization.setObjectName(u"comboBox_Polarization")
        self.comboBox_Polarization.setGeometry(QRect(85, 20, comboBoxWidth, comboBoxHeight))

        self.label_pcv = QLabel(self.groupBox_UserInput)
        self.label_pcv.setObjectName(u"label_pcv")
        self.label_pcv.setGeometry(QRect(10, 10 + 20 + comboBoxHeight+1, 75, 16))

        self.comboBox_pcv = QComboBox(self.groupBox_UserInput)
        self.comboBox_pcv.addItem("")
        self.comboBox_pcv.addItem("")
        self.comboBox_pcv.setObjectName(u"comboBox_pcv")
        self.comboBox_pcv.setGeometry(QRect(85, 10 + 20 + comboBoxHeight, comboBoxWidth, comboBoxHeight))
        self.comboBox_pcv.setToolTip("Turn on for phase center variation plot vs frequency")

        self.label_unit = QLabel(self.groupBox_UserInput)
        self.label_unit.setObjectName(u"label_unit")
        self.label_unit.setGeometry(QRect(10, 20+2*(10+comboBoxHeight)+2, 75, 16))

        self.comboBox_unit = QComboBox(self.groupBox_UserInput)
        self.comboBox_unit.addItem("")
        self.comboBox_unit.addItem("")
        self.comboBox_unit.addItem("")
        self.comboBox_unit.addItem("")
        self.comboBox_unit.addItem("")
        self.comboBox_unit.setObjectName(u"comboBox_unit")
        self.comboBox_unit.setGeometry(
            QRect(85, 20+2*(10+comboBoxHeight), comboBoxWidth, comboBoxHeight))
        self.comboBox_unit.setToolTip("Unit for length assumed for user entries")

        self.pushButton_CreateRCS = QPushButton(self.groupBox_UserInput)
        self.pushButton_CreateRCS.setObjectName(u"pushButton_CreateRCS")
        self.pushButton_CreateRCS.setGeometry(QRect(40, 20+3*(10+comboBoxHeight)+10, comboBoxWidth + 10, 31))
        self.pushButton_CreateRCS.clicked.connect(self.createRCS)
        self.pushButton_CreateRCS.setToolTip("Click to calculate Phase Center")
        self.pushButton_CreateRCS.setEnabled(True)
        self.pushButton_CreateRCS.setStyleSheet('background-color :  green')

        self.groupBox_Visualize = QGroupBox(self.centralwidget)
        self.groupBox_Visualize.setObjectName(u"groupBox_Visualize")
        self.groupBox_Visualize.setGeometry(QRect(210, 20, 91 + 25, 131))
        self.checkBox_ShowPattern = QCheckBox(self.groupBox_Visualize)

        self.checkBox_ShowPattern.setObjectName(u"checkBox_ShowPattern")
        self.checkBox_ShowPattern.setGeometry(QRect(20, 20, 75, 20))
        self.checkBox_ShowPattern.setToolTip("tentative: Currently doesn't overlay 3D polar plot")
        self.checkBox_ShowPattern.setEnabled(True)

        self.comboBox_referenceCS1 = QComboBox(self.groupBox_Visualize)
        self.comboBox_referenceCS1.addItem("")
        # self.comboBox_referenceCS1.addItem("")
        self.comboBox_referenceCS1.setObjectName(u"comboBox_referenceCS1")
        self.comboBox_referenceCS1.setGeometry(QRect(15, 40, 60 + 30, comboBoxHeight))
        self.comboBox_referenceCS1.setToolTip("Visualize wrt to this Coordinate System")

        self.comboBox_ViewOrientation = QComboBox(self.groupBox_Visualize)
        self.comboBox_ViewOrientation.addItem("")
        self.comboBox_ViewOrientation.addItem("")
        self.comboBox_ViewOrientation.addItem("")
        self.comboBox_ViewOrientation.setObjectName(u"comboBox_ViewOrientation")
        self.comboBox_ViewOrientation.setGeometry(QRect(15, 70, 60 + 30, comboBoxHeight))
        self.comboBox_ViewOrientation.setToolTip("Orientation to visualize in")

        self.pushButton_View = QPushButton(self.groupBox_Visualize)
        self.pushButton_View.setObjectName(u"pushButton_View")
        self.pushButton_View.setGeometry(QRect(30, 100, 60, 24))
        self.pushButton_View.clicked.connect(self.visualize)
        self.pushButton_View.setToolTip("Updates the image based on orientation chosen")
        self.pushButton_View.setEnabled(True)

        # self.label_Initial_Guess = QLabel(self.groupBox_UserInput)
        # self.label_Initial_Guess.setObjectName(u"label_Initial_Guess")
        # self.label_Initial_Guess.setGeometry(QRect(10, 190, 291, 16))

        self.label_PC = QLabel(self.groupBox_UserInput)
        self.label_PC.setObjectName(u"label_PC")
        self.label_PC.setGeometry(QRect(50, 210, 200, 48))

        self.pushButton_Reset = QPushButton(self.centralwidget)
        self.pushButton_Reset.setObjectName(u"pushButton_Reset")
        self.pushButton_Reset.setGeometry(QRect(360, 20, 60, 24))
        self.pushButton_Reset.clicked.connect(self.reset)
        self.pushButton_Reset.setEnabled(True)
        self.pushButton_Reset.setToolTip("Resets the project by deleting far field setups and coordinate systems")

        self.pushButton_Exit = QPushButton(self.centralwidget)
        self.pushButton_Exit.setObjectName(u"pushButton_Exit")
        self.pushButton_Exit.setGeometry(QRect(425, 20, 60, 24))
        self.pushButton_Exit.clicked.connect(self.exit_app)
        self.pushButton_Exit.setEnabled(True)
        self.pushButton_Exit.setToolTip("Exits the app.")

        self.hfss.modeler.fit_all()
        self.hfss.modeler.set_working_coordinate_system('Global')

        self.hfss.post.export_model_picture(self.hfss.working_directory + "/model_iso.jpg", show_grid=False,
                                            show_ruler=False, width=0, height=0, orientation="Isometric")
        self.pixmap = QPixmap(self.hfss.working_directory + "/model_iso.jpg")
        self.label_Modeler0 = QLabel(self.centralwidget)
        self.label_Modeler0.setPixmap(self.pixmap)
        self.label_Modeler0.setScaledContents(True)
        self.label_Modeler0.setObjectName(u"label_Modeler0")
        self.label_Modeler0.setGeometry(QRect(360, 50, int(300 * (2 / 3)), 167))

        self.hfss.post.export_model_picture(self.hfss.working_directory + "/model_X.jpg", show_grid=False,
                                            show_ruler=False, width=0, height=0, orientation="front")
        self.pixmap = QPixmap(self.hfss.working_directory + "/model_X.jpg")
        self.label_Modeler1 = QLabel(self.centralwidget)
        self.label_Modeler1.setPixmap(self.pixmap)
        self.label_Modeler1.setScaledContents(True)
        self.label_Modeler1.setObjectName(u"label_Modeler1")
        self.label_Modeler1.setGeometry(QRect(360, 50 + 167 + 25, int(300 * (2 / 3)), 167))

        self.hfss.post.export_model_picture(self.hfss.working_directory + "/model_Z.jpg", show_grid=False,
                                            show_ruler=False, width=0, height=0, orientation="top")
        self.pixmap = QPixmap(self.hfss.working_directory + "/model_Z.jpg")
        self.label_Modeler2 = QLabel(self.centralwidget)
        self.label_Modeler2.setPixmap(self.pixmap)
        self.label_Modeler2.setScaledContents(True)
        self.label_Modeler2.setObjectName(u"label_Modeler2")
        self.label_Modeler2.setGeometry(QRect(360, 50 + 167 * 2 + 25 * 2, int(300 * (2 / 3)), 167))

        self.label_forModeler0 = QLabel(self.centralwidget)
        self.label_forModeler0.setObjectName(u"label_forModeler0")
        self.label_forModeler0.setGeometry(QRect(360, 50 + 167 + 5, 31 * 6, 16))

        self.label_forModeler1 = QLabel(self.centralwidget)
        self.label_forModeler1.setObjectName(u"label_forModeler1")
        self.label_forModeler1.setGeometry(QRect(360, 50 + (167 + 5) * 2 + 16 + 5, 31 * 6, 16))

        self.label_forModeler2 = QLabel(self.centralwidget)
        self.label_forModeler2.setObjectName(u"label_forModeler2")
        self.label_forModeler2.setGeometry(QRect(360, 50 + (167 + 5) * 3 + 32 + 5, 31 * 6, 16))

        self.label_Frequency = QLabel(self.centralwidget)
        self.label_Frequency.setObjectName(u"label_Frequency")
        self.label_Frequency.setGeometry(QRect(210, 150, 61, 16))

        self.lineEdit_Frequency = QLineEdit(self.centralwidget)
        self.lineEdit_Frequency.setObjectName(u"lineEdit_Frequency")
        self.lineEdit_Frequency.setGeometry(QRect(210, 170, 61, 21))
        self.lineEdit_Frequency.setEnabled(False)
        self.lineEdit_Frequency.setToolTip("Frequency for which it's calculating PhC")

        self.label_PhC = QLabel(self.centralwidget)
        self.label_PhC.setObjectName(u"label_PhC")
        self.label_PhC.setGeometry(QRect(120, 255, 130, 36))
        self.label_PhC.setAlignment(Qt.AlignCenter)

        self.comboBox_PhC = QComboBox(self.centralwidget)
        self.comboBox_PhC.setObjectName(u"comboBox_PhC")
        self.comboBox_PhC.setGeometry(QRect(20, 290, comboBoxWidth * 5+30, comboBoxHeight))
        self.comboBox_PhC.setToolTip("Phase Center Value (X,Y,Z) for a given frequency. Sigma is std of phase in degrees for plot range.")

        self.label_PlotTitle = QLabel(self.centralwidget)
        self.label_PlotTitle.setObjectName(u"label_PlotTitle")
        self.label_PlotTitle.setGeometry(QRect(120, 320, 130, 36))
        self.label_PlotTitle.setAlignment(Qt.AlignCenter)

        self.plotwidget = PlotWidget(phase_center)
        self.plotwidget.setObjectName(u"plotwidget")
        self.plotwidget.setGeometry(QRect(10, 380, 330, 250))
        self.plotwidget.setBackground(background='white')
        self.plotwidget.raise_()
        self.hfss.modeler.fit_all()
        # self.hfss.post.export_model_picture(self.hfss.working_directory + "/test_img.jpg", show_grid=False,
        #                                     show_ruler=False, orientation="isometric")

        phase_center.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(phase_center)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 731, 22))

        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName(u"menuHelp")

        phase_center.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(phase_center)
        self.statusbar.setObjectName(u"statusbar")
        phase_center.setStatusBar(self.statusbar)
        # self.reset()
        QWidget.setTabOrder(self.pushButton_Reset, self.comboBox_unit)
        QWidget.setTabOrder(self.comboBox_unit, self.pushButton_CreateRCS)
        QWidget.setTabOrder(self.pushButton_CreateRCS, self.checkBox_ShowPattern)
        QWidget.setTabOrder(self.checkBox_ShowPattern, self.comboBox_ViewOrientation)
        QWidget.setTabOrder(self.comboBox_ViewOrientation, self.pushButton_View)
        QWidget.setTabOrder(self.pushButton_View, self.comboBox_Polarization)
        QWidget.setTabOrder(self.comboBox_Polarization, self.comboBox_referenceCS1)
        QWidget.setTabOrder(self.comboBox_referenceCS1, self.lineEdit_Frequency)
        # QWidget.setTabOrder(self.lineEdit_Frequency, self.pushButton_Clear_Plot)

        self.menubar.addAction(self.menuHelp.menuAction())
        self.menuHelp.addAction(self.actionHow_to_Use)

        self.retranslate_ui(phase_center)

        QMetaObject.connectSlotsByName(phase_center)

    # setup_ui

    def retranslate_ui(self, phase_center):
        phase_center.setWindowTitle(QCoreApplication.translate("phase_center", u"Phase Center App", None))
        self.actionHow_to_Use.setText(QCoreApplication.translate("phase_center", u"How to Use", None))
        self.groupBox_UserInput.setTitle(QCoreApplication.translate("phase_center", u"User Input", None))

        # self.label_OriginY.setText(QCoreApplication.translate("phase_center", u"Y", None))
        #
        # self.lineEdit_OriginX.setText(QCoreApplication.translate("phase_center", u"0",None))
        # self.lineEdit_OriginY.setText(QCoreApplication.translate("phase_center", u"0", None))
        # self.lineEdit_OriginZ.setText(QCoreApplication.translate("phase_center", u"0", None))
        # self.label_Origin.setText(QCoreApplication.translate("phase_center", u"Origin", None))
        # self.label_OriginX.setText(QCoreApplication.translate("phase_center", u"X", None))
        # self.label_OriginZ.setText(QCoreApplication.translate("phase_center", u"Z", None))
        self.pushButton_CreateRCS.setText(QCoreApplication.translate("phase_center", u"Calculate", None))
        self.pushButton_Exit.setText(QCoreApplication.translate("phase_center", u"Exit", None))
        self.pushButton_Reset.setText(QCoreApplication.translate("phase_center", u"Reset", None))

        self.groupBox_Visualize.setTitle(QCoreApplication.translate("phase_center", u"Visualize", None))
        self.comboBox_ViewOrientation.setItemText(0, QCoreApplication.translate("phase_center", u"Isometric", None))
        self.comboBox_ViewOrientation.setItemText(1, QCoreApplication.translate("phase_center", u"+Y", None))
        self.comboBox_ViewOrientation.setItemText(2, QCoreApplication.translate("phase_center", u"-Y", None))

        self.comboBox_referenceCS1.setItemText(0, QCoreApplication.translate("phase_center", u"Global", None))

        self.checkBox_ShowPattern.setText(QCoreApplication.translate("phase_center", u"Pattern", None))
        self.pushButton_View.setText(QCoreApplication.translate("phase_center", u"View", None))
        self.comboBox_unit.setItemText(0, QCoreApplication.translate("phase_center", u"mm", None))
        self.comboBox_unit.setItemText(1, QCoreApplication.translate("phase_center", u"cm", None))
        self.comboBox_unit.setItemText(2, QCoreApplication.translate("phase_center", u"mil", None))
        self.comboBox_unit.setItemText(3, QCoreApplication.translate("phase_center", u"meter", None))
        self.comboBox_unit.setItemText(4, QCoreApplication.translate("phase_center", u"in", None))
        self.comboBox_pcv.setItemText(0, QCoreApplication.translate("phase_center", u"No", None))
        self.comboBox_pcv.setItemText(1, QCoreApplication.translate("phase_center", u"Yes", None))
        self.comboBox_unit.setToolTip("")
        self.comboBox_pcv.setToolTip(
            "If yes, calculates phase center variation wrt frequency, else wrt solution frequency.")
        self.comboBox_unit.setWhatsThis("")
        self.comboBox_pcv.setWhatsThis("")
        self.label_unit.setText(QCoreApplication.translate("phase_center", u"Unit [Length]", None))
        self.label_Polarization.setText(QCoreApplication.translate("phase_center", u"Polarization", None))
        self.label_pcv.setText(QCoreApplication.translate("phase_center", u"PhC Variation", None))
        self.comboBox_Polarization.setItemText(0, QCoreApplication.translate("phase_center", u"X", None))
        self.comboBox_Polarization.setItemText(1, QCoreApplication.translate("phase_center", u"Y", None))
        self.comboBox_Polarization.setItemText(2, QCoreApplication.translate("phase_center", u"LHCP", None))
        self.comboBox_Polarization.setItemText(3, QCoreApplication.translate("phase_center", u"RHCP", None))
        self.label_Frequency.setText(QCoreApplication.translate("phase_center", u"Frequency", None))
        self.label_PhC.setText(QCoreApplication.translate("phase_center", u"Phase Center Location\n[wrt Global]", None))
        # self.label_Initial_Guess.setText(QCoreApplication.translate("phase_center", u"", None))
        # self.label_PC.setText(QCoreApplication.translate("phase_center", u"", None))
        self.label_forModeler0.setText(QCoreApplication.translate("phase_center", u"Global Isometric View", None))
        self.label_forModeler1.setText(QCoreApplication.translate("phase_center", u"Global Front View", None))
        self.label_forModeler2.setText(QCoreApplication.translate("phase_center", u"Global Top View", None))
        self.label_PlotTitle.setText(QCoreApplication.translate("phase_center", u"", None))
        self.pushButton_Reset.setText(QCoreApplication.translate("phase_center", u"Reset", None))
        self.pushButton_Exit.setText(QCoreApplication.translate("phase_center", u"Exit", None))
        self.menuHelp.setTitle(QCoreApplication.translate("phase_center", u"Help", None))

    def closeEvent(self, event: QCloseEvent) -> None:
        self.hfss.release_desktop(False, False)
        event.accept()

    def get_frequency(self, str_freq_w_unit):
        freq_val = float(str_freq_w_unit[:-3])
        # read freq unit from the UI (assumed to be of length=3)
        freq_unit = str_freq_w_unit[-3:]
        # get multiplier i.e 4.5GHz becomes 4.5*1e9
        f = self.get_freq_multiplier(freq_unit)
        freq = freq_val * f
        return freq

    def set_frequency(self):
        if self.hfss.setups[0].props["SolveType"] == "MultiFrequency":
            myFreq = self.hfss.setups[0].props["MultipleAdaptiveFreqsSetup"]["AdaptAt"][0]["Frequency"]
        elif self.hfss.setups[0].props["SolveType"] == "Broadband":
            myFreq = self.hfss.setups[0].props["MultipleAdaptiveFreqsSetup"]["Low"]
        else:
            myFreq = self.hfss.setups[0].props["Frequency"]
        self.lineEdit_Frequency.setText(myFreq)

    def auto_create_rel_cs(self, setup):
        # This function creates relative coordinate system with Z pointing along max of rE_component (rEX or rEY etc. based on user input).
        # Antenna(array) is assumed to be created in the X,Y plane of the global coordinate system.
        # It's radiation (based on edit sources entries) ...write
        # Since polarization along X or Y, we want one coordinate system to have its X to lie in global XZ plane, and Y to lie in global YZ plane.

        # read user input from the UI
        unit = self.comboBox_unit.currentText()
        originX = '0'
        originY = '0'
        originZ = '0'
        origin = [originX + unit, originY + unit, originZ + unit]
        # create a CS with origin at where user specified. This is the Phase center location guessed by the user.
        # This CS goes from theta -180 to +180, phi 0-180 to cover entire sphere.
        # We will later export the far field values (compute antenna parameters) with respect to this CS.
        # That table in the txt exported will contain the AtMax(Theta,Phi) i.e. where the max rE occurs for given polarization.
        # if requency has a decimal point, can't use it to name coord systems/inf sphere. replace it with _ if decimal present
        current_freq = self.lineEdit_Frequency.text()
        if "." in current_freq:
            xx0 = current_freq.split(".")
            xx = xx0[0] + "_" + xx0[1]
        else:
            xx = current_freq

        # cs_auto_name = self.PC_CS_name_auto + "_" + xx
        Inf_PC_auto_name = self.Inf_PC_auto + "_" + xx
        pccs_auto_name = self.PC_CS_name_auto + "_" + xx
        relative2pccs_auto_name = "Z_At_max_rEcomp" + "_" + xx

        polarization = self.comboBox_Polarization.currentText()
        # These will be appended to the name of the coordinate systems based on whether X or Y pol is requested
        name_XZ = "_xz"
        name_YZ = "_yz"
        # name = cs_auto_name
        # self.comboBox_ViewOrientation.setCurrentText("YZ")
        # read frequency from the UI since it's already there, remove GHz/MHz etc (assumed not to be Hz) from it and convert to float

        # pick first analysis setup's last adaptive
        # setup = self.hfss.existing_analysis_setups[0]+": LastAdaptive"
        # sphere = self.Inf_global
        # below code finds the At(Theta,Phi) entry for rE_comp in Compute Antenna Parameters. This helps orient the \
        # coordinate system's Z axis along that direction.
        # rE_comp = 'rE'+polarization # for finding where is max of the asked polarization
        oMod = self.hfss.odesign.GetModule("RadField")
        #start_time_export = time.time()
        cwd = os.getcwd()
        oMod.ExportParametersToFile(
            [
                "ExportFileName:=", cwd + "\\exportparams.txt",
                "SetupName:=", self.Inf_global,
                "IntrinsicVariationKey:=", "Freq=" + current_freq,  # "Freq=\'4.5GHz\'",
                "DesignVariationKey:=", "",  # "Phi_Scan=\'0deg\' Theta_Scan=\'0deg\' v=\'0.123\'",
                "SolutionName:=", setup,
                "Quantity:="	, ""
            ]
            )
        #stop_time_export = time.time()
        #print("Exporting antenna parameters file took ", str("{:.2f}".format(stop_time_export - start_time_export)), " seconds")
        with open('exportparams.txt') as f:
            row_data_at_rETotal = [line.split()[4] for line in f.readlines() if line != '\n' and line.split()[0] == "Total" and len(line.split()) >= 5]
            b = list(row_data_at_rETotal[0])
        for i,x in enumerate(b):
            if not x.isdigit() and x != '-' and x != '.':
                b[i] = ' '
        # below two are float values of theta and phi at which the max rE field occurs
        theta_at_max_rETotal = float("".join(b).split()[0])# ['4  ','-80']
        phi_at_max_rETotal  = float("".join(b).split()[1])
        # check if the antenna is radiating in the upper hemisphere
        if abs(theta_at_max_rETotal) > 90:
            self.reset()
            dlg = QMessageBox()
            dlg.setWindowTitle("Error")
            dlg.setText("Max E field should be above global XY plane. Re-orient the antenna and try again.")
            self.hfss.release_desktop(False, False)
            button = dlg.exec()
            if button == QMessageBox.Ok:
                sys.exit()
                #QCoreApplication.instance().quit()
        # when we say X polarized, we mean with respect to global cs in which the geometry was drawn along x/y directions
        # so if polarization is X, the new CS with Z aligned along max of radiation should have its X' in XZ plane of global cs
        if polarization == 'X':
            context = Inf_PC_auto_name + name_XZ
            pccsname = pccs_auto_name + name_XZ
            bb = (phi_at_max_rETotal) * math.pi / 180
            cc = (theta_at_max_rETotal) * math.pi / 180
            dd = -(math.atan(math.tan(bb) * math.cos(cc))) * 180 / math.pi  # (math.acos(math.cos(bb)*math.cos(cc)))*180/math.pi
            # CS will have X in global XZ plane
            mode = 2# 'zyz'
            # Let's rotate the cs about Z so that X',Z and the beam vector are in 1 plane.
            euler_phi = (phi_at_max_rETotal)
            # now rotate about Y' so that Z' || beam vector
            euler_theta = (theta_at_max_rETotal)
            # now rotate about Z' so that X' X Z lie in one plane
            euler_psi = (dd)
        elif polarization == 'Y':
            context = Inf_PC_auto_name + name_YZ
            pccsname = pccs_auto_name + name_YZ
            # CS This will have Y aligned with global Y
            bb = (phi_at_max_rETotal - 90) * math.pi / 180
            cc = (theta_at_max_rETotal) * math.pi / 180
            dd = -(math.atan(math.tan(bb) * math.cos(cc))) * 180 / math.pi  # (math.acos(math.cos(bb)*math.cos(cc)))*180/math.pi
            mode = 1# 'zxz'
            euler_phi = (phi_at_max_rETotal - 90)
            euler_theta = (-theta_at_max_rETotal)
            euler_psi = (dd)
        else:
            mode = 2
            context = Inf_PC_auto_name+"_cp"
            pccsname = pccs_auto_name+"_cp"
            euler_phi = phi_at_max_rETotal
            euler_theta = theta_at_max_rETotal
            euler_psi = 0
        cs0 = self.hfss.modeler.create_coordinate_system(name=pccsname, origin=origin, reference_cs='Global')
        cs0.change_cs_mode(mode)
        cs0.props["Phi"] = euler_phi
        cs0.props["Theta"] = euler_theta
        cs0.props["Psi"] = euler_psi
        ZYZ_pccs = [euler_phi, euler_theta, euler_psi] # c  uld ZYZ, ZXZ. naming not ideal
        self.hfss.insert_infinite_sphere(definition='Theta-Phi', x_start=-10,
                                         x_stop=10, x_step=0.5,
                                         y_start=0, y_stop=180, y_step=1, units='deg',
                                         custom_radiation_faces=None, custom_coordinate_system=pccsname,
                                         use_slant_polarization=False, polarization_angle=45,
                                         name=Inf_PC_auto_name)

        # reduce the extend of theta start and stop to take less time as we are max rEComp should be in neighborhood of maxrETotal
        # Inf_setup_list = [x for x in self.hfss.field_setups if Inf_PC_auto_name == x.name]
        # if Inf_setup_list:
        #     Inf_setup_list[0].props["CoordSystem"] = pccsname
        #     Inf_setup_list[0].props["ThetaStart"] = "-30deg"
        #     Inf_setup_list[0].props["ThetaStop"] = "30deg"
        #     Inf_setup_list[0].props["ThetaStep"] = "0.5deg"

        # Now export antenna parameters file wrt rotated CS.

        oMod.ExportParametersToFile(
            [
                "ExportFileName:=", cwd+"\\exportparams2.txt",
                "SetupName:=", Inf_PC_auto_name,
                "IntrinsicVariationKey:=", "Freq=" + current_freq,  # "Freq=\'4.5GHz\'",
                "DesignVariationKey:=", "",  # "Phi_Scan=\'0deg\' Theta_Scan=\'0deg\' v=\'0.123\'",
                "SolutionName:=", setup,
                "Quantity:="	, ""
            ]
        )
        with open('exportparams2.txt') as f:
            row_data_at_rEcomp = [line.split()[3] for line in f.readlines() if line != '\n' and line.split()[0] == polarization]
        b=list(row_data_at_rEcomp[0])
        for i, x in enumerate(b):
            if not x.isdigit() and x != '-' and x != '.':
                b[i] = ' '
        # below two are float values of theta and phi at which the max rE field occurs
        theta_at_max_rEcomp = float("".join(b).split()[0]) # ['  0','-80']
        phi_at_max_rEcomp = float("".join(b).split()[1])

        if polarization == 'X':
            bb = (phi_at_max_rEcomp) * math.pi / 180
            cc = (theta_at_max_rEcomp) * math.pi / 180
            dd = -(math.atan(math.tan(bb) * math.cos(cc))) * 180 / math.pi  # (math.acos(math.cos(bb)*math.cos(cc)))*180/math.pi
            euler_phi = (phi_at_max_rEcomp)
            euler_theta = (theta_at_max_rEcomp)
            euler_psi = (dd)
        elif polarization == 'Y':
            bb = (phi_at_max_rEcomp - 90) * math.pi / 180
            cc = (theta_at_max_rEcomp) * math.pi / 180
            dd = -(math.atan(math.tan(bb) * math.cos(cc))) * 180 / math.pi  # (math.acos(math.cos(bb)*math.cos(cc)))*180/math.pi
            euler_phi = (phi_at_max_rEcomp - 90)
            euler_theta = (-theta_at_max_rEcomp)
            euler_psi = (dd)
        else:
            # bb = (phi_at_max_rETotal) * math.pi / 180
            # cc = (theta_at_max_rETotal) * math.pi / 180
            # dd = 0
            euler_phi = phi_at_max_rEcomp
            euler_theta = theta_at_max_rEcomp
            euler_psi = 0

        cs1 = self.hfss.modeler.create_coordinate_system(name=relative2pccs_auto_name, reference_cs=pccsname)
        cs1.change_cs_mode(mode)
        cs1.props["Phi"] = euler_phi
        cs1.props["Theta"] = euler_theta
        cs1.props["Psi"] = euler_psi
        ZYZ_rel = [euler_phi, euler_theta, euler_psi]  # [euler_psi,euler_theta,euler_phi]
        # Now the Z' axis of the CS is along max of rEcomp and X,Y are oriented correctly.
        # the infinite sphere below contains only 3 points along theta with 0 at the center. And has 2 phi cut planes - 0 and 90.
        self.hfss.insert_infinite_sphere(definition='Theta-Phi', x_start=-self.thetascale*self.theta_step,
                                         x_stop=self.thetascale*self.theta_step, x_step=self.thetascale*self.theta_step,
                                         y_start=0, y_stop=90, y_step=90, units='deg',
                                         custom_radiation_faces=None, custom_coordinate_system=relative2pccs_auto_name,
                                         use_slant_polarization=False, polarization_angle=45,
                                         name=context)

        variations = {}
        variations["Freq"] = [current_freq]
        variations["Theta"] = [str(-self.thetascale * self.theta_step) + 'deg', '0deg', str(
                               self.thetascale * self.theta_step) + 'deg']

        variations["Phi"] = ['0deg']  # ,  str(phi1 + self.phi_step) + 'deg']

        # implement logic to read ffdata for phi,theta = 90/90+deltaPhi,-+deltaTheta
        ## end ##
        # need to read theta array somehow. using ffdata for that
        ff_data1 = self.hfss.post.get_solution_data(expressions="rE" + polarization,
                                                    setup_sweep_name=setup, primary_sweep_variable="Theta",
                                                    report_category="Far Fields", context=context, 
                                                    variations=variations)
        del variations["Phi"]
        variations["Phi"] = ['90deg']
        ff_data2 = self.hfss.post.get_solution_data(expressions="rE" + polarization,
                                                    setup_sweep_name=setup, primary_sweep_variable="Theta", 
                                                    report_category="Far Fields",
                                                    context=context, variations=variations)

        freq_unit = ff_data1.units_sweeps["Freq"]
        factor = self.get_freq_multiplier(freq_unit)
        k0 = 2 * math.pi * ff_data1.intrinsics["Freq"][0] * factor / 299792458
        x0, y0, z0 = self.calculatePC2(k0, ff_data1, ff_data2)

        x0 = self.convert_meter_to_unit(x0, unit)
        y0 = self.convert_meter_to_unit(y0, unit)
        z0 = self.convert_meter_to_unit(z0, unit)
        self.hfss.modeler.create_coordinate_system(name="PhC_" + current_freq,
                                                   origin=[str(x0) + unit, str(y0) + unit, str(z0) + unit],
                                                   reference_cs=relative2pccs_auto_name)
        self.comboBox_referenceCS1.addItem("PhC_" + current_freq)

        PhC_wrt_rel = [[x0], [y0], [z0]]
        if mode == 1:
            euler_mode = "ZXZ"  # intrinsic
        elif mode == 2:
            euler_mode = "ZYZ"
        r = Rotation.from_euler(euler_mode, ZYZ_rel, degrees=True).as_matrix()
        V1 = np.matmul(r, PhC_wrt_rel)
        r = Rotation.from_euler(euler_mode, ZYZ_pccs, degrees=True).as_matrix()
        V2 = np.matmul(r, V1)
        initial_guess = np.array([[float(originX)], [float(originY)], [float(originZ)]])
        PhC_wrt_global = np.add(V2, initial_guess)
        # if PCV = No, then plot 2cuts.
        # insert infinite sphere for plotting in the App. We want to see how phase looks across 0,90 cuts using
        # global CS and predicted CS (PCCS)
        # find standard deviation of the phase at
        if polarization == 'X':
            qq = 90
        elif polarization == 'Y':
            qq = 0
        else:
            qq = 0
        self.hfss.insert_infinite_sphere(definition='Theta-Phi', x_start=-1 * self.plotRange, x_stop=self.plotRange,
                                         x_step=self.theta_step,
                                         y_start=qq, y_stop=qq, y_step=0, units='deg',
                                         custom_radiation_faces=None, custom_coordinate_system="PhC_" + current_freq,
                                         use_slant_polarization=False, polarization_angle=45,
                                         name=context + "plot")
        variations = {}
        variations["Freq"] = [current_freq]
        variations["Theta"] = ["All"]
        variations["Phi"] = ["All"]
        # for global theta range
        # theta_array_global = list(np.arange(-180, 180, self.theta_step))
        # theta_array = [str(x) + "deg" for x in theta_array_global if x >= -1 * self.plotRange and x <= self.plotRange]
        cut_data_phi0 = self.hfss.post.get_solution_data(expressions="rE" + polarization,
                                                         setup_sweep_name=setup,
                                                         primary_sweep_variable="Theta",
                                                         report_category="Far Fields", context=context + "plot",
                                                         variations=variations)
        sigma = np.std(cut_data_phi0.data_phase(radians=False))
        if self.comboBox_pcv.currentText() == "Yes":
            return PhC_wrt_global, sigma


        mk_pen_color = self.LINECOLORS[self.numCurves % len(self.LINECOLORS)]
        self.plotwidget.addLegend(offset=(30, 10))
        # if polarization == "Theta":
        #     pol = "\u0398"
        # elif polarization == "Phi":
        #     pol = "\u03A6"
        # elif polarization == "LHCP":
        #     pol = "\u21BB"
        # elif polarization == "RHCP":
        #     pol = "\u21BA"
        # elif polarization == 'X':
        #     pol = 'X'
        # elif polarization == 'Y':
        #     pol = 'Y'

        ## Legend uses greek symbol for cut plane phi/theta, and polarization phi, theta, rhcp, lhcp
        w = 3
        cutplane = "\u03C6"
        self.plotwidget.plot(cut_data_phi0.primary_sweep_values, cut_data_phi0.data_phase(radians=False),
                             pen=pyqtgraph.mkPen(mk_pen_color, width=w),
                             name=cutplane + "=" + str(qq) + "deg" + " | " + "PhC_" + current_freq + " | \u03C3=" + str(
                                 "{:.2f}".format(sigma)))
        self.numCurves += 1
        return PhC_wrt_global

    def createRCS(self):
        # clear up any previous Coordinate Systems, far field setups
        self.reset()
        self.hfss.save_project()

        self.hfss.insert_infinite_sphere(definition='Theta-Phi', x_start=-180, x_stop=180, x_step=self.theta_step,
                                         y_start=0, y_stop=180, y_step=self.phi_step, units='deg',
                                         custom_radiation_faces=None, custom_coordinate_system=None,
                                         use_slant_polarization=False, polarization_angle=45,
                                         name=self.Inf_global)


        # if phase center variation is requested, loop through frequency points
        if self.comboBox_pcv.currentText() == "Yes":
            start_time = time.time()
            if self.hfss.setups[0].sweeps == [] or (not self.hfss.setups[0].sweeps[0].is_solved) or \
                    (self.hfss.setups[0].sweeps[0].props['Type'] != 'Discrete') or \
                    (not self.hfss.setups[0].sweeps[0].props['SaveFields']):
                self.reset()
                dlg = QMessageBox()
                dlg.setWindowTitle("Error")
                dlg.setText("For PCV, a discrete sweep should be solved and fields saved.")
                self.hfss.release_desktop(False, False)
                button = dlg.exec()
                if button == QMessageBox.Ok:
                    sys.exit()

            self.label_PlotTitle.setText("Phase Center Variation\nvs Freq")
            sweep_name = self.hfss.setups[0].sweeps[0].name  # debug
            setup = self.hfss.existing_analysis_setups[0] + ": " + sweep_name
            f00 = self.hfss.setups[0].sweeps[0].props["RangeStart"]
            f11 = self.hfss.setups[0].sweeps[0].props["RangeEnd"]
            # self.hfss.setups[0].sweeps[0].props['RangeStep']
            f_unit = f00[-3:]
            m = self.get_freq_multiplier(f_unit)
            f0 = self.get_frequency(f00) / m
            f1 = self.get_frequency(f11) / m

            if self.hfss.setups[0].sweeps[0].props['RangeType'] == 'LinearCount':
                n = self.hfss.setups[0].sweeps[0].props["RangeCount"]
            elif self.hfss.setups[0].sweeps[0].props['RangeType'] == 'LinearStep':
                str_rangestep = self.hfss.setups[0].sweeps[0].props['RangeStep']
                step = str_rangestep[:-3]  # assuming same freq unit for step as start and end freqs
                step_unit = str_rangestep[-3:]
                n = math.floor((f1 - f0) * m / self.get_frequency(str_rangestep)) + 1

            PhC_vs_freq = np.zeros([3, n])
            c = -1
            for f in np.linspace(f0, f1, n):
                c += 1
                self.lineEdit_Frequency.setText(str(f) + f_unit)
                # check if ScanFrequency variable is present. If yes, set it to the current freq.
                if "ScanFrequency" in self.hfss.variable_manager.design_variable_names:
                    self.hfss["ScanFrequency"] = str(f*m) + "Hz"

                aa, sigma = self.auto_create_rel_cs(setup)
                answer = "Freq= " + str("{:.2f}".format(f)) + f_unit + " | x=" + str(
                    "{:.2f}".format(aa[0][0])) + " | y=" + str("{:.2f}".format(aa[1][0])) + " | z=" + str(
                    "{:.2f}".format(aa[2][0])) + " | \u03C3=" + str("{:.2f}".format(sigma))
                self.comboBox_PhC.addItem(answer)
                PhC_vs_freq[:, [c]] = aa

            self.plotwidget.addLegend(offset=(30, 10))
            #polarization = self.comboBox_Polarization.currentText()
            # if polarization == "LHCP":
            #     pol = "\u21BB"
            # elif polarization == "RHCP":
            #     pol = "\u21BA"
            # elif polarization == 'X':
            #     pol = 'X'
            # elif polarization == 'Y':
            #     pol = 'Y'

            ## Legend uses greek symbol for cut plane phi/theta, and polarization phi, theta, rhcp, lhcp
            w = 3
            # cutplane = "\u03C6"
            for i in list(range(3)):
                coord = ["X", "Y", "Z"]
                mk_pen_color = self.LINECOLORS[self.numCurves % len(self.LINECOLORS)]
                self.plotwidget.plot(list(np.linspace(f0, f1, n)), list(PhC_vs_freq[i, :]),
                                     pen=pyqtgraph.mkPen(mk_pen_color, width=w),
                                     name=coord[i])
                self.numCurves += 1
            stop_time = time.time()
            print("Took ", str("{:.2f}".format(stop_time - start_time)), " seconds")
        else:
            self.label_PlotTitle.setText("Phase vs Theta")
            setup = self.hfss.existing_analysis_setups[0] + ": LastAdaptive"
            self.set_frequency()
            # current_freq[:-3]
            aa = self.auto_create_rel_cs(setup)
            answer = "Freq=" + self.lineEdit_Frequency.text() + " | x=" + str(
                "{:.2f}".format(aa[0][0])) + " | y=" + str("{:.2f}".format(aa[1][0])) + " | z=" + str(
                "{:.2f}".format(aa[2][0]))
            self.comboBox_PhC.addItem(answer)
        return

    def visualize(self):
        hfss = self.hfss
        # if self.comboBox_referenceCS1.currentText() == "Global":
        #     cs = "Global"
        # elif "PhC_" in self.comboBox_referenceCS1.currentText():
        #     cs = self.comboBox_referenceCS1.currentText()
        cs = self.comboBox_referenceCS1.currentText()
        self.hfss.modeler.set_working_coordinate_system(cs)

        if self.comboBox_ViewOrientation.currentText() == "-Y":
            orientation = "right"
        elif self.comboBox_ViewOrientation.currentText() == "+Y":
            orientation = "left"
        elif self.comboBox_ViewOrientation.currentText() == "Isometric":
            orientation = "isometric"

        # pick frequency in result combobox. will make 3d polar plot visible for that frequency
        # pick right context - 3D. make its cs=phc selected
        # pick reComp to plot

        if self.comboBox_pcv.currentText() == "Yes":
            sweep_name = self.hfss.setups[0].sweeps[0].name  # debug
            setup = self.hfss.existing_analysis_setups[0] + " : " + sweep_name
            freq = self.comboBox_referenceCS1.currentText()[4:]
            if "ScanFrequency" in self.hfss.variable_manager.design_variable_names:
                self.hfss["ScanFrequency"] = freq
        else:
            setup = self.hfss.existing_analysis_setups[0] + " : LastAdaptive"
            freq = self.lineEdit_Frequency.text()

        if self.checkBox_ShowPattern.isChecked():

            # let the inf sphere wrt global cs be wrt the phc so we can plot the radiation pattern wrt that
            Inf_setup_list = [x for x in self.hfss.field_setups if self.Inf_global == x.name]
            if Inf_setup_list and self.comboBox_referenceCS1.currentText() != "Global":
                Inf_setup_list[0].props["CoordSystem"] = "PhC_" + freq
                Inf_setup_list[0].props["UseLocalCS"] = True
            oModule = hfss.odesign.GetModule('ReportSetup')
            # if rEcomp exists, delete it.
            if "rEcomp" in hfss.post.all_report_names:
                hfss.post.delete_report("rEcomp")
            oModule.CreateReport("rEcomp", "Far Fields", "3D Polar Plot", setup,
                                 ["Context:=", self.Inf_global],
                                 ["Phi:=", ["All"], "Theta:=", ["All"], "Freq:=", [freq]],
                                 ["Phi Component:=", "Phi", "Theta Component:=", "Theta", "Mag Component:=",
                                  ["mag(rE" + self.comboBox_Polarization.currentText() + ")"]])
            # variations = hfss.available_variations.nominal_w_values_dict
            # variations["Theta"] = ["All"]
            # variations["Phi"] = ["All"]
            # variations["Freq"] = [freq]
            # plot_report = hfss.post.create_report(expressions="mag(rE" + self.comboBox_Polarization.currentText() + ")",
            #                                       setup_sweep_name=setup, domain="Sweep", variations=variations,
            #                                       primary_sweep_variable="Phi",
            #                                       secondary_sweep_variable="Theta",
            #                                       report_category="Far Fields",
            #                                       plot_type="3D Polar Plot",
            #                                       context=self.Inf_global,
            #                                       plotname="rEcomp")

            oModule = hfss.odesign.GetModule("FieldsReporter")
            oModule.ShowRadiatedPlotOverlay("rEcomp", 0.4, 1)


        hfss.post.export_model_picture(self.hfss.working_directory + "/model_chosenOrientation.jpg", show_grid=False,
                                            show_ruler=False, orientation=orientation)
        self.pixmap = QPixmap(self.hfss.working_directory + "/model_chosenOrientation.jpg")
        # self.label_img = QLabel(Form)
        self.label_Modeler0.setPixmap(self.pixmap)
        self.label_Modeler0.setScaledContents(True)

        self.label_forModeler0.setText( cs + " - Chosen View")

        hfss.post.export_model_picture(self.hfss.working_directory + "/model_front.jpg", show_grid=False,
                                       show_ruler=False, orientation="front")
        self.pixmap = QPixmap(self.hfss.working_directory + "/model_front.jpg")
        # self.label_img = QLabel(Form)
        self.label_Modeler1.setPixmap(self.pixmap)
        self.label_Modeler1.setScaledContents(True)
        self.label_forModeler1.setText( cs + " - Front View")

        hfss.post.export_model_picture(self.hfss.working_directory + "/model_top.jpg", show_grid=False,
                                       show_ruler=False, orientation="top")
        self.pixmap = QPixmap(self.hfss.working_directory + "/model_top.jpg")
        # self.label_img = QLabel(Form)
        self.label_Modeler2.setPixmap(self.pixmap)
        self.label_Modeler2.setScaledContents(True)
        self.label_forModeler2.setText( cs + " - Top View")

        # setupName = hfss.existing_analysis_setups[0]
        # setup_sweep_name = setupName + " : LastAdaptive"
        ## show pattern
        # if self.checkBox_ShowPattern.isChecked():
        #
        #     variations = {}
        #     variations["Freq"] = [self.lineEdit_Frequency.text()]
        #     variations["Theta"] = ["All"]
        #     variations["Phi"] = ["All"]
        #
        #     ffData = hfss.post.get_solution_data(expressions="GainTotal", setup_sweep_name = setup_sweep_name, report_category="Far Fields",\
        #                                               context=self.Inf_global, variations=variations)
        #     hfss.post.create_3d_plot(ffData)

    def calculatePC2(self, k0, ff_data1, ff_data2):
        '''
        Solves system of 4 linear equations using numpy linear algebra methods.
        we need phase of the field in 4 directions close to z axis (why close to z axis?)
        '''
        theta1 = ff_data1.intrinsics["Theta"][ 0 ]*math.pi/180
        theta2 = ff_data1.intrinsics["Theta"][ 1 ]*math.pi/180
        theta3 = ff_data1.intrinsics["Theta"][ 2 ]*math.pi/180

        # phase1_atphi_90 = ff_data2.data_phase()[0] if ff_data2.data_phase()[0]>=0 else math.pi+ff_data2.data_phase()[0]
        # phase2_atphi_90 = ff_data2.data_phase()[1] if ff_data2.data_phase()[1]>=0 else math.pi+ff_data2.data_phase()[1]
        # phase3_atphi_90 = ff_data2.data_phase()[2] if ff_data2.data_phase()[2]>=0 else math.pi+ff_data2.data_phase()[2]

        expression = ff_data2.active_expression
        phase1_at_phi_90 = [math.atan2(k, i) for i, k in zip(ff_data2.data_real(expression), ff_data2.data_imag(expression))][0]
        phase2_at_phi_90 = [math.atan2(k, i) for i, k in zip(ff_data2.data_real(expression), ff_data2.data_imag(expression))][1]
        phase3_at_phi_90 = [math.atan2(k, i) for i, k in zip(ff_data2.data_real(expression), ff_data2.data_imag(expression))][2]
        # diagnostics
        #[print("phase negative!") if ff_data2.data_phase()[i] < 0 else print("positive") for i in [0, 1, 2]]
        #[print("phase negative!") if ff_data1.data_phase()[i] < 0 else print("positive") for i in [0, 1, 2]]

        stheta12 = math.sin(theta1)-math.sin(theta2)
        stheta13 = math.sin(theta1) - math.sin(theta3)
        ctheta12 = math.cos(theta1) - math.cos(theta2)
        ctheta13 = math.cos(theta1) - math.cos(theta3)

        phase12 = phase1_at_phi_90 - phase2_at_phi_90
        phase13 = phase1_at_phi_90 - phase3_at_phi_90

        y0 = (phase12*ctheta13-phase13*ctheta12)/( k0*(stheta12*ctheta13-stheta13 * ctheta12))

        # now calculate x0 and z0
        s31 = math.sin(theta3) - math.sin(theta1)
        s21 = math.sin(theta2) - math.sin(theta1)
        c21 = math.cos(theta2) - math.cos(theta1)
        c31 = math.cos(theta3) - math.cos(theta1)

        # phase1 = ff_data1.data_phase()[0] if ff_data1.data_phase()[0]>=0 else math.pi+ff_data1.data_phase()[0]
        # phase2 = ff_data1.data_phase()[1] if ff_data1.data_phase()[1]>=0 else math.pi+ff_data1.data_phase()[1]
        # phase3 = ff_data1.data_phase()[2] if ff_data1.data_phase()[2]>=0 else math.pi+ff_data1.data_phase()[2]
        expression = ff_data1.active_expression
        phase1 = [math.atan2(k, i) for i, k in zip(ff_data1.data_real(expression), ff_data1.data_imag(expression))][0]
        phase2 = [math.atan2(k, i) for i, k in zip(ff_data1.data_real(expression), ff_data1.data_imag(expression))][1]
        phase3 = [math.atan2(k, i) for i, k in zip(ff_data1.data_real(expression), ff_data1.data_imag(expression))][2]

        A1 = (math.cos(theta3) - math.cos(theta1)) / (math.cos(theta2) - math.cos(theta1))
        x0 = (phase3 + A1 * phase1 - A1 * phase2 - phase1) / (k0 * (s31 - A1 * s21))
        z0 = (phase2 - phase1 - k0 * s21 * x0) / (k0 * c21)

        return x0, y0, z0

    def convert_meter_to_unit(self, n, unit):
        '''unit assumed mil, mm, cm, meter, in\
        n is in meters'''
        if unit == "mil":
            f = 1/(25.4 * 1e-6)
        elif unit == "mm":
            f = 1000
        elif unit == "cm":
            f = 100
        elif unit == "meter":
            f = 1
        elif unit == "in":
            f = 1/0.0254
        else:
            pass
        return n * f

    def get_freq_multiplier(self, freq_unit):
        if freq_unit == "GHz":
            factor = 1e9
        elif freq_unit == "MHz":
            factor = 1e6
        elif freq_unit == "THz":
            factor = 1e12
        elif freq_unit == "KHz":
            factor = 1e3
        else:
            factor = 1
        return factor

    def reset(self):
        # clear messages.
        # for item in self.plotwidget.listDataItems():
        #     self.plotwidget.removeItem(item)

        #Inf_setup_list = [x for x in self.hfss.field_setups if self.Inf_PC in x.name or self.Inf_global in x.name]
        #if Inf_setup_list:
        #    [x.delete() for x in self.hfss.field_setups if self.Inf_PC in x.name]#Inf_setup_list]
        #    print("Deleted field setups from last run")

        infsphere_list = [x for x in self.hfss.field_setups]
        if infsphere_list:
            [x.delete() for x in infsphere_list]

        cs_list = [x for x in self.hfss.modeler.coordinate_systems]
        if cs_list:
            [x.delete() for x in cs_list]
            print("Deleted coordinate systems from last run")

        #self.hfss._project_dictionary = None
        self.hfss.save_project()
        #CS_list = [x for x in self.hfss.modeler.coordinate_systems if self.PC_CS_name in x.name]


        #self.hfss.save_project()
        # [x.delete() for x in self.hfss.modeler.coordinate_systems if self.PC_CS_name in x.name]
        # reset UI
        # remove all entries from phc result combobox
        # for some reason it is not removing all items. So I will try clear()
        if self.comboBox_PhC.count() != 0:
            # [self.comboBox_PhC.removeItem(i) for i in list(range(self.comboBox_PhC.count()))]
            self.comboBox_PhC.clear()
        # remove all entries from visualize/reference cs1 except global
        if self.comboBox_referenceCS1.currentText() != '':
            # [self.comboBox_referenceCS1.removeItem(i) for i in list(range(self.comboBox_referenceCS1.count())) if 'Global' != self.comboBox_referenceCS1.itemText(i)]
            self.comboBox_referenceCS1.clear()
            self.comboBox_referenceCS1.addItem('Global')
        # clear the plot
        for item in self.plotwidget.listDataItems():
            self.plotwidget.removeItem(item)
            # clear frequency
        self.lineEdit_Frequency.setText('')
        self.numCurves = 0

        self.hfss.odesktop.ClearMessages("", "", 3)
        # if exportantennaparams files exist, delete them
        try:
            os.remove(".\\exportparams.txt")
        except OSError:
            pass

        try:
            os.remove(".\\exportparams2.txt")
        except OSError:
            pass
        self.hfss.save_project()

    def exit_app(self):
        self.hfss.save_project()
        self.hfss.odesktop.ClearMessages("", "", 3)
        self.hfss.release_desktop(False, False)
        sys.exit()

    def get_array(self, start: str, stop: str, array: list):
        start = float(start[:-3])
        stop = float(stop[:-3])
        array = [str(x) + "deg" for x in array if x >= start and x <= stop]
        return array


if __name__ == "__main__":
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = UiPhaseCenter1()
    ui.setup_ui(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())
