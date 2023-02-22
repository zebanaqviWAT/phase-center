# -*- coding: utf-8 -*-

################################################################################
## Phase Center App - using PySide6 for UI and PyAEDT
## Author : Zeba Naqvi
## Last tested with pyaedt version 0.5.7, pyqtgraph 0.12.4
##
## Qt User Interface Compiler version 6.3.0
##
##  if you choose a cut angle not available in infinite sphere, it will appear as it is in plot's legend and everywhere
##  but correct angle (smaller than that value) will be used in optimization setup creation. This can be corrected for
##  but not urgent.
################################################################################
import math
from random import seed
from random import randint
import sys, time, numpy as np
from pyaedt import Hfss
from PySide6.QtCore import (QCoreApplication, QRegularExpression, QDate, QDateTime, QLocale,
                            QMetaObject, QObject, QPoint, QRect,
                            QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QDoubleValidator, QRegularExpressionValidator, QColor, QConicalGradient,
                           QCursor,
                           QFont, QFontDatabase, QGradient, QIcon, QCloseEvent,
                           QImage, QKeySequence, QLinearGradient, QPainter,
                           QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QMainWindow, QCheckBox, QComboBox, QGroupBox,
                               QLabel, QMenu, QMenuBar, QLineEdit, QPushButton, QRadioButton,
                               QSizePolicy, QWidget, QMessageBox, QStatusBar)
from pyqtgraph import PlotWidget, plot
import pyqtgraph
import MyImages_rc


class UiPhaseCenter(QMainWindow):

    def setupUi(self, PhaseCenter):
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
        self.PC_CS_name = "PCCS"
        self.Inf_global = "Infinite_Sphere_Global"
        self.Inf_PC = "Infinite_Sphere_PC"
        self.Opti_name = "OptimizationSetup_PC"
        self.ffData = 0
        self.hfss = Hfss(specified_version="2022.1", new_desktop_session=False, non_graphical=False)
        self.cuts = {"Phi": {}, "Theta": {}}
        self.hfss.optimizations.delete(self.Opti_name)

        # print("Frequency ########## ",self.hfss.setups[0].props["Frequency"])
        if not self.hfss.setups[0].is_solved:
            dlg = QMessageBox()
            dlg.setWindowTitle("Error")
            dlg.setText("Setup not solved!")
            self.hfss.release_desktop(False, False)
            button = dlg.exec()
            if button == QMessageBox.Ok:
                QCoreApplication.instance().quit()
        # time.sleep()

        if not PhaseCenter.objectName():
            PhaseCenter.setObjectName(u"PhaseCenter")
        PhaseCenter.resize(820, 820)  # (731, 674)
        self.actionHow_to_Use = QAction(PhaseCenter)
        self.actionHow_to_Use.setObjectName(u"actionHow_to_Use")

        self.centralwidget = QWidget(PhaseCenter)
        self.centralwidget.setObjectName(u"centralwidget")

        self.groupBox_UserInput = QGroupBox(self.centralwidget)
        self.groupBox_UserInput.setObjectName(u"groupBox_UserInput")
        self.groupBox_UserInput.setGeometry(QRect(10, 50, 331, 581 + 32))

        self.groupBox_RCS = QGroupBox(self.groupBox_UserInput)
        self.groupBox_RCS.setObjectName(u"groupBox_RCS")
        self.groupBox_RCS.setGeometry(QRect(10, 50, 211, 141))

        self.lineEdit_EulerPsi = QLineEdit(self.groupBox_RCS)
        self.lineEdit_EulerPsi.setObjectName(u"lineEdit_EulerPsi")
        self.lineEdit_EulerPsi.setGeometry(QRect(100, 110, 36, 21))
        self.lineEdit_EulerPsi.setValidator(regValidator)
        self.lineEdit_EulerPsi.setEnabled(True)

        self.label_OriginY = QLabel(self.groupBox_RCS)
        self.label_OriginY.setObjectName(u"label_OriginY")
        self.label_OriginY.setGeometry(QRect(10, 80, 16, 16))

        self.lineEdit_OriginY = QLineEdit(self.groupBox_RCS)
        self.lineEdit_OriginY.setObjectName(u"lineEdit_OriginY")
        self.lineEdit_OriginY.setGeometry(QRect(30, 80, 31, 21))
        self.lineEdit_OriginY.setValidator(regValidator)
        self.lineEdit_OriginY.setEnabled(True)

        self.comboBox_Euler = QComboBox(self.groupBox_RCS)
        self.comboBox_Euler.addItem("")
        self.comboBox_Euler.addItem("")
        self.comboBox_Euler.setObjectName(u"comboBox_Euler")
        self.comboBox_Euler.setGeometry(QRect(150, 30, 51, 22))

        self.lineEdit_OriginX = QLineEdit(self.groupBox_RCS)
        self.lineEdit_OriginX.setObjectName(u"lineEdit_OriginX")
        self.lineEdit_OriginX.setGeometry(QRect(30, 50, 31, 21))
        self.lineEdit_OriginX.setValidator(regValidator)
        self.lineEdit_OriginX.setEnabled(True)

        self.label_EulerPsi = QLabel(self.groupBox_RCS)
        self.label_EulerPsi.setObjectName(u"label_EulerPsi")
        self.label_EulerPsi.setGeometry(QRect(70, 110, 31, 16))

        self.lineEdit_EulerPhi = QLineEdit(self.groupBox_RCS)
        self.lineEdit_EulerPhi.setObjectName(u"lineEdit_EulerPhi")
        self.lineEdit_EulerPhi.setGeometry(QRect(100, 50, 36, 21))
        self.lineEdit_EulerPhi.setValidator(regValidator)
        self.lineEdit_EulerPhi.setEnabled(True)

        self.label_EulerPhi = QLabel(self.groupBox_RCS)
        self.label_EulerPhi.setObjectName(u"label_EulerPhi")
        self.label_EulerPhi.setGeometry(QRect(70, 50, 31, 16))

        self.label_Euler = QLabel(self.groupBox_RCS)
        self.label_Euler.setObjectName(u"label_Euler")
        self.label_Euler.setGeometry(QRect(100, 30, 31, 16))

        self.lineEdit_EulerTheta = QLineEdit(self.groupBox_RCS)
        self.lineEdit_EulerTheta.setObjectName(u"lineEdit_EulerTheta")
        self.lineEdit_EulerTheta.setGeometry(QRect(100, 80, 36, 21))
        self.lineEdit_EulerTheta.setValidator(regValidator)
        self.lineEdit_EulerTheta.setEnabled(True)

        self.label_Origin = QLabel(self.groupBox_RCS)
        self.label_Origin.setObjectName(u"label_Origin")
        self.label_Origin.setGeometry(QRect(30, 30, 49, 16))

        self.lineEdit_OriginZ = QLineEdit(self.groupBox_RCS)
        self.lineEdit_OriginZ.setObjectName(u"lineEdit_OriginZ")
        self.lineEdit_OriginZ.setGeometry(QRect(30, 110, 31, 21))
        self.lineEdit_OriginZ.setValidator(regValidator)
        self.lineEdit_OriginZ.setEnabled(True)

        self.label_OriginX = QLabel(self.groupBox_RCS)
        self.label_OriginX.setObjectName(u"label_OriginX")
        self.label_OriginX.setGeometry(QRect(10, 50, 16, 16))

        self.label_OriginZ = QLabel(self.groupBox_RCS)
        self.label_OriginZ.setObjectName(u"label_OriginZ")
        self.label_OriginZ.setGeometry(QRect(10, 110, 16, 16))

        self.label_EulerTheta = QLabel(self.groupBox_RCS)
        self.label_EulerTheta.setObjectName(u"label_EulerTheta")
        self.label_EulerTheta.setGeometry(QRect(70, 80, 31, 16))

        self.pushButton_CreateRCS = QPushButton(self.groupBox_RCS)
        self.pushButton_CreateRCS.setObjectName(u"pushButton_CreateRCS")
        self.pushButton_CreateRCS.setGeometry(QRect(150, 60, 51, 31))
        self.pushButton_CreateRCS.clicked.connect(self.createRCS)
        self.pushButton_CreateRCS.setToolTip("Creates Phase Center Coordinate System")
        self.pushButton_CreateRCS.setEnabled(True)

        self.groupBox_Visualize = QGroupBox(self.groupBox_UserInput)
        self.groupBox_Visualize.setObjectName(u"groupBox_Visualize")
        self.groupBox_Visualize.setGeometry(QRect(230, 50, 91, 141))

        self.comboBox_ViewOrientation = QComboBox(self.groupBox_Visualize)
        self.comboBox_ViewOrientation.addItem("")
        self.comboBox_ViewOrientation.addItem("")
        self.comboBox_ViewOrientation.addItem("")
        self.comboBox_ViewOrientation.addItem("")
        self.comboBox_ViewOrientation.setObjectName(u"comboBox_ViewOrientation")
        self.comboBox_ViewOrientation.setGeometry(QRect(15, 80, 60, 22))
        self.comboBox_ViewOrientation.setToolTip("Orientation to visualize in")

        self.comboBox_referenceCS1 = QComboBox(self.groupBox_Visualize)
        self.comboBox_referenceCS1.addItem("")
        # self.comboBox_referenceCS1.addItem("")
        self.comboBox_referenceCS1.setObjectName(u"comboBox_referenceCS1")
        self.comboBox_referenceCS1.setGeometry(QRect(15, 50, 60, 22))
        self.comboBox_referenceCS1.setToolTip("Visualize wrt this coordinate system")

        self.checkBox_ShowPattern = QCheckBox(self.groupBox_Visualize)
        self.checkBox_ShowPattern.setObjectName(u"checkBox_ShowPattern")
        self.checkBox_ShowPattern.setGeometry(QRect(20, 30, 75, 20))
        self.checkBox_ShowPattern.setToolTip("tentative: Currently doesn't overlay 3D polar plot")
        self.checkBox_ShowPattern.setEnabled(False)

        self.pushButton_View = QPushButton(self.groupBox_Visualize)
        self.pushButton_View.setObjectName(u"pushButton_View")
        self.pushButton_View.setGeometry(QRect(15, 110, 60, 24))
        self.pushButton_View.clicked.connect(self.visualize)
        self.pushButton_View.setToolTip("Updates the image based on orientation chosen")
        self.pushButton_View.setEnabled(True)

        self.comboBox_unit = QComboBox(self.groupBox_UserInput)
        self.comboBox_unit.addItem("")
        self.comboBox_unit.addItem("")
        self.comboBox_unit.addItem("")
        self.comboBox_unit.addItem("")
        self.comboBox_unit.addItem("")
        self.comboBox_unit.setObjectName(u"comboBox_unit")
        self.comboBox_unit.setGeometry(QRect(60, 20, 56, 22))
        self.comboBox_unit.setToolTip("Unit for length assumed for user entries")

        self.label_unit = QLabel(self.groupBox_UserInput)
        self.label_unit.setObjectName(u"label_unit")
        self.label_unit.setGeometry(QRect(20, 20, 31, 16))

        self.groupBox_BeamCuts = QGroupBox(self.groupBox_UserInput)
        self.groupBox_BeamCuts.setObjectName(u"groupBox_BeamCuts")
        self.groupBox_BeamCuts.setGeometry(QRect(10, 200, 311, 220))

        self.label_Polarization = QLabel(self.groupBox_BeamCuts)
        self.label_Polarization.setObjectName(u"label_Polarization")
        self.label_Polarization.setGeometry(QRect(10, 20, 61, 16))

        self.comboBox_Polarization = QComboBox(self.groupBox_BeamCuts)
        self.comboBox_Polarization.addItem("")
        self.comboBox_Polarization.addItem("")
        self.comboBox_Polarization.addItem("")
        self.comboBox_Polarization.addItem("")
        self.comboBox_Polarization.setObjectName(u"comboBox_Polarization")
        self.comboBox_Polarization.setGeometry(QRect(10, 40, 61, 22))

        self.label_Frequency = QLabel(self.groupBox_BeamCuts)
        self.label_Frequency.setObjectName(u"label_Frequency")
        self.label_Frequency.setGeometry(QRect(200, 20, 61, 16))

        self.lineEdit_Frequency = QLineEdit(self.groupBox_BeamCuts)
        self.lineEdit_Frequency.setObjectName(u"lineEdit_Frequency")
        self.lineEdit_Frequency.setGeometry(QRect(200, 40, 61, 21))
        self.lineEdit_Frequency.setEnabled(False)
        self.lineEdit_Frequency.setToolTip("Solution Frequency (1st for multifrequency)")

        self.comboBox_referenceCS = QComboBox(self.groupBox_BeamCuts)
        self.comboBox_referenceCS.addItem("")
        # self.comboBox_referenceCS.addItem("")
        self.comboBox_referenceCS.setObjectName(u"comboBox_referenceCS")
        self.comboBox_referenceCS.setGeometry(QRect(110, 40, 61, 22))
        self.comboBox_referenceCS.setToolTip("Plot phase wrt this coordinate system")

        self.label_referenceCS = QLabel(self.groupBox_BeamCuts)
        self.label_referenceCS.setObjectName(u"label_referenceCS")
        self.label_referenceCS.setGeometry(QRect(110, 20, 61, 16))

        self.label_CutPlane = QLabel(self.groupBox_BeamCuts)
        self.label_CutPlane.setObjectName(u"label_CutPlane")
        self.label_CutPlane.setGeometry(QRect(10, 70, 51, 16))

        self.comboBox_CutPlane_ThetaOrPhi = QComboBox(self.groupBox_BeamCuts)
        self.comboBox_CutPlane_ThetaOrPhi.addItem("")
        self.comboBox_CutPlane_ThetaOrPhi.addItem("")
        self.comboBox_CutPlane_ThetaOrPhi.setObjectName(u"comboBox_CutPlane_ThetaOrPhi")
        self.comboBox_CutPlane_ThetaOrPhi.setGeometry(QRect(110, 70, 61, 22))
        self.comboBox_CutPlane_ThetaOrPhi.activated.connect(self.theta_or_phi_plane_chosen)

        self.lineEdit_CutPlane_AngleValue = QLineEdit(self.groupBox_BeamCuts)
        self.lineEdit_CutPlane_AngleValue.setObjectName(u"lineEdit_CutPlane_AngleValue")
        self.lineEdit_CutPlane_AngleValue.setGeometry(QRect(200, 70, 61, 21))
        self.lineEdit_CutPlane_AngleValue.setValidator(regValidator)
        self.lineEdit_CutPlane_AngleValue.editingFinished.connect(self.check_within_range)
        self.lineEdit_CutPlane_AngleValue.setEnabled(True)

        self.label_deg1 = QLabel(self.groupBox_BeamCuts)
        self.label_deg1.setObjectName(u"label_deg1")
        self.label_deg1.setGeometry(QRect(270, 70, 31, 16))

        self.label_equal = QLabel(self.groupBox_BeamCuts)
        self.label_equal.setObjectName(u"label_equal")
        self.label_equal.setGeometry(QRect(180, 70, 21, 16))

        self.label_SweepWhat = QLabel(self.groupBox_BeamCuts)
        self.label_SweepWhat.setObjectName(u"label_SweepWhat")
        self.label_SweepWhat.setGeometry(QRect(10, 100, 96, 16))

        self.lineEdit_sweep_ang_high = QLineEdit(self.groupBox_BeamCuts)
        self.lineEdit_sweep_ang_high.setObjectName(u"lineEdit_sweep_ang_high")
        self.lineEdit_sweep_ang_high.setGeometry(QRect(200, 100, 61, 21))
        self.lineEdit_sweep_ang_high.setValidator(regValidator)
        self.lineEdit_sweep_ang_high.editingFinished.connect(self.check_within_range)
        self.lineEdit_sweep_ang_high.setEnabled(True)

        self.lineEdit_sweep_ang_low = QLineEdit(self.groupBox_BeamCuts)
        self.lineEdit_sweep_ang_low.setObjectName(u"lineEdit_sweep_ang_low")
        self.lineEdit_sweep_ang_low.setGeometry(QRect(110, 100, 61, 21))
        self.lineEdit_sweep_ang_low.setValidator(regValidator)
        self.lineEdit_sweep_ang_low.editingFinished.connect(self.check_within_range)
        self.lineEdit_sweep_ang_low.setEnabled(True)

        self.label_deg2 = QLabel(self.groupBox_BeamCuts)
        self.label_deg2.setObjectName(u"label_deg2")
        self.label_deg2.setGeometry(QRect(270, 100, 31, 16))

        self.label_to = QLabel(self.groupBox_BeamCuts)
        self.label_to.setObjectName(u"label_to")
        self.label_to.setGeometry(QRect(180, 100, 16, 16))

        self.pushButton_AddCut = QPushButton(self.groupBox_BeamCuts)
        self.pushButton_AddCut.setObjectName(u"pushButton_AddCut")
        self.pushButton_AddCut.setGeometry(QRect(100, 130, 61, 24))
        self.pushButton_AddCut.clicked.connect(self.add_cut_to_list)
        self.pushButton_AddCut.setEnabled(True)

        self.comboBox_CutsAdded = QComboBox(self.groupBox_BeamCuts)
        self.comboBox_CutsAdded.setObjectName(u"comboBox_CutsAdded")
        self.comboBox_CutsAdded.setGeometry(QRect(10, 160, 291, 22))

        self.pushButton_DeleteCut = QPushButton(self.groupBox_BeamCuts)
        self.pushButton_DeleteCut.setObjectName(u"pushButton_DeleteCut")
        self.pushButton_DeleteCut.setGeometry(QRect(230, 190, 31, 24))
        self.pushButton_DeleteCut.clicked.connect(self.deleteCut)
        icon = QIcon()
        icon.addFile(u":/icons/delete.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton_DeleteCut.setIcon(icon)
        self.pushButton_DeleteCut.setEnabled(True)

        self.pushButton_PlotCut = QPushButton(self.groupBox_BeamCuts)
        self.pushButton_PlotCut.setObjectName(u"pushButton_PlotCut")
        self.pushButton_PlotCut.setGeometry(QRect(270, 190, 31, 24))
        self.pushButton_PlotCut.clicked.connect(self.plotCut)
        icon1 = QIcon()
        icon1.addFile(u":/icons/icons8-plot-50.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton_PlotCut.setIcon(icon1)
        self.pushButton_PlotCut.setIconSize(QSize(25, 25))
        self.pushButton_PlotCut.setEnabled(True)

        self.label_Initial_Guess = QLabel(self.groupBox_BeamCuts)
        self.label_Initial_Guess.setObjectName(u"label_Initial_Guess")
        self.label_Initial_Guess.setGeometry(QRect(10, 190, 291, 16))

        # self.label_21 = QLabel(self.groupBox_BeamCuts)
        # self.label_21.setObjectName(u"label_21")
        # self.label_21.setGeometry(QRect(10, 210, 61, 16))

        self.label_PC = QLabel(self.groupBox_BeamCuts)
        self.label_PC.setObjectName(u"label_PC")
        self.label_PC.setGeometry(QRect(50, 210, 200, 48))

        self.pushButton_Clear_Plot = QPushButton(self.centralwidget)
        self.pushButton_Clear_Plot.setObjectName(u"pushButton_Clear_Plot")
        self.pushButton_Clear_Plot.setGeometry(QRect(590, 330, 70, 24))
        self.pushButton_Clear_Plot.clicked.connect(self.clearPlots)
        self.pushButton_Clear_Plot.setEnabled(True)

        self.groupBox_optimization = QGroupBox(self.groupBox_UserInput)
        self.groupBox_optimization.setObjectName(u"groupBox_optimization")
        self.groupBox_optimization.setGeometry(QRect(10, 430, 311, 121))

        self.lineEdit_SearchZ2 = QLineEdit(self.groupBox_optimization)
        self.lineEdit_SearchZ2.setObjectName(u"lineEdit_SearchZ2")
        self.lineEdit_SearchZ2.setGeometry(QRect(130, 90, 41, 21))
        self.lineEdit_SearchZ2.setValidator(regValidator)
        # self.lineEdit_SearchZ2.editingFinished.connect(self.check_within_range)
        self.lineEdit_SearchZ2.setEnabled(True)

        self.lineEdit_SearchX1 = QLineEdit(self.groupBox_optimization)
        self.lineEdit_SearchX1.setObjectName(u"lineEdit_SearchX1")
        self.lineEdit_SearchX1.setGeometry(QRect(10, 60, 41, 21))
        self.lineEdit_SearchX1.setValidator(regValidator)
        self.lineEdit_SearchX1.setEnabled(True)

        self.lineEdit_SearchX2 = QLineEdit(self.groupBox_optimization)
        self.lineEdit_SearchX2.setObjectName(u"lineEdit_SearchX2")
        self.lineEdit_SearchX2.setGeometry(QRect(10, 90, 41, 21))
        self.lineEdit_SearchX2.setValidator(regValidator)
        # self.lineEdit_SearchX2.editingFinished.connect(self.check_within_range)
        self.lineEdit_SearchX2.setEnabled(True)

        self.lineEdit_SearchY2 = QLineEdit(self.groupBox_optimization)
        self.lineEdit_SearchY2.setObjectName(u"lineEdit_SearchY2")
        self.lineEdit_SearchY2.setGeometry(QRect(70, 90, 41, 21))
        self.lineEdit_SearchY2.setValidator(regValidator)
        # self.lineEdit_SearchY2.editingFinished.connect(self.check_within_range)
        self.lineEdit_SearchY2.setEnabled(True)

        self.lineEdit_SearchY1 = QLineEdit(self.groupBox_optimization)
        self.lineEdit_SearchY1.setObjectName(u"lineEdit_SearchY1")
        self.lineEdit_SearchY1.setGeometry(QRect(70, 60, 41, 21))
        self.lineEdit_SearchY1.setValidator(regValidator)
        self.lineEdit_SearchY1.setEnabled(True)

        self.lineEdit_SearchZ1 = QLineEdit(self.groupBox_optimization)
        self.lineEdit_SearchZ1.setObjectName(u"lineEdit_SearchZ1")
        self.lineEdit_SearchZ1.setGeometry(QRect(130, 60, 41, 21))
        self.lineEdit_SearchZ1.setValidator(regValidator)
        self.lineEdit_SearchZ1.setEnabled(True)

        self.pushButton_CreateOptimization = QPushButton(self.groupBox_optimization)
        self.pushButton_CreateOptimization.setObjectName(u"pushButton_CreateOptimization")
        self.pushButton_CreateOptimization.setGeometry(QRect(190, 60, 91, 51))
        self.pushButton_CreateOptimization.clicked.connect(self.createOptimization)
        self.pushButton_CreateOptimization.setEnabled(True)

        self.label_SearchRange = QLabel(self.groupBox_optimization)
        self.label_SearchRange.setObjectName(u"label_SearchRange")
        self.label_SearchRange.setGeometry(QRect(50, 20, 81, 16))

        self.label_SearchRangeX = QLabel(self.groupBox_optimization)
        self.label_SearchRangeX.setObjectName(u"label_SearchRangeX")
        self.label_SearchRangeX.setGeometry(QRect(20, 40, 16, 16))

        self.label_SearchRangeY = QLabel(self.groupBox_optimization)
        self.label_SearchRangeY.setObjectName(u"label_SearchRangeY")
        self.label_SearchRangeY.setGeometry(QRect(80, 40, 16, 16))

        self.label_SearchRangeZ = QLabel(self.groupBox_optimization)
        self.label_SearchRangeZ.setObjectName(u"label_SearchRangeZ")
        self.label_SearchRangeZ.setGeometry(QRect(140, 40, 16, 16))

        self.pushButton_Reset = QPushButton(self.groupBox_UserInput)
        self.pushButton_Reset.setObjectName(u"pushButton_Reset")
        self.pushButton_Reset.setGeometry(QRect(265, 20, 60, 24))
        self.pushButton_Reset.clicked.connect(self.reset)
        self.pushButton_Reset.setEnabled(True)

        self.pushButton_Exit = QPushButton(self.groupBox_UserInput)
        self.pushButton_Exit.setObjectName(u"pushButton_Exit")
        self.pushButton_Exit.setGeometry(QRect(200, 20, 60, 24))
        self.pushButton_Exit.clicked.connect(self.exitApp)
        self.pushButton_Exit.setEnabled(True)

        # self.label_sigma_of_plot = QLabel(self.centralwidget)
        # self.label_sigma_of_plot.setObjectName(u"label_sigma_of_plot")
        # self.label_sigma_of_plot.setGeometry(QRect(370, 330, 49, 31))

        self.label_status = QLabel(self.centralwidget)
        self.label_status.setObjectName(u"label_status")
        self.label_status.setGeometry(QRect(10, 640 + 32, 711, 16))

        self.reset()
        # self.save()

        # for x in self.hfss.field_setups:  # self.hfss.design_properties["RadField"]["FarFieldSetups"]:
        #     if x.name == self.Inf_global:
        #         x.delete()
        #         self.hfss.save_project()
        #         time.sleep(2)
        # #deleted Infinite_Sphere_Global to avoid name conflict
        if self.Inf_global not in [x.name for x in self.hfss.field_setups]:
            self.hfss.insert_infinite_sphere(definition='Theta-Phi', x_start=-180, x_stop=180, x_step=self.theta_step,
                                             y_start=-180, y_stop=180, y_step=self.phi_step, units='deg',
                                             custom_radiation_faces=None, custom_coordinate_system=None,
                                             use_slant_polarization=False, polarization_angle=45,
                                             name=self.Inf_global)
            # self.label_status.setText("Infinite Sphere Setup refernced to Global CS created")
        # for x in self.hfss.modeler.coordinate_systems:
        #     if self.PC_CS_name in x.name:
        #         x.delete()
        #         self.hfss.save_project()
        #         time.sleep(5)

        self.hfss.modeler.fit_all()
        self.hfss.modeler.set_working_coordinate_system('Global')
        self.hfss.post.export_model_picture(self.hfss.working_directory + "/test_img.jpg", show_grid=False,
                                            show_ruler=False, width=0, height=0, orientation="Isometric")
        self.pixmap = QPixmap(self.hfss.working_directory + "/test_img.jpg")
        self.label_Modeler = QLabel(self.centralwidget)
        self.label_Modeler.setPixmap(self.pixmap)
        self.label_Modeler.setScaledContents(True)
        self.label_Modeler.setObjectName(u"label_Modeler")
        self.label_Modeler.setGeometry(QRect(360, 50, 300, 250))

        self.plotwidget = PlotWidget(PhaseCenter)
        self.plotwidget.setObjectName(u"plotwidget")
        self.plotwidget.setGeometry(QRect(360, 380, 300, 250))
        self.plotwidget.setBackground(background='white')
        self.plotwidget.raise_()
        self.hfss.modeler.fit_all()
        self.hfss.post.export_model_picture(self.hfss.working_directory + "/test_img.jpg", show_grid=False,
                                            show_ruler=False, orientation="isometric")

        PhaseCenter.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(PhaseCenter)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 731, 22))

        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName(u"menuHelp")

        PhaseCenter.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(PhaseCenter)
        self.statusbar.setObjectName(u"statusbar")
        PhaseCenter.setStatusBar(self.statusbar)

        QWidget.setTabOrder(self.pushButton_Reset, self.comboBox_unit)
        QWidget.setTabOrder(self.comboBox_unit, self.lineEdit_OriginX)
        QWidget.setTabOrder(self.lineEdit_OriginX, self.lineEdit_OriginY)
        QWidget.setTabOrder(self.lineEdit_OriginY, self.lineEdit_OriginZ)
        QWidget.setTabOrder(self.lineEdit_OriginZ, self.comboBox_Euler)
        QWidget.setTabOrder(self.comboBox_Euler, self.lineEdit_EulerPhi)
        QWidget.setTabOrder(self.lineEdit_EulerPhi, self.lineEdit_EulerTheta)
        QWidget.setTabOrder(self.lineEdit_EulerTheta, self.lineEdit_EulerPsi)
        QWidget.setTabOrder(self.lineEdit_EulerPsi, self.pushButton_CreateRCS)
        QWidget.setTabOrder(self.pushButton_CreateRCS, self.checkBox_ShowPattern)
        QWidget.setTabOrder(self.checkBox_ShowPattern, self.comboBox_ViewOrientation)
        QWidget.setTabOrder(self.comboBox_ViewOrientation, self.pushButton_View)
        QWidget.setTabOrder(self.pushButton_View, self.comboBox_Polarization)
        QWidget.setTabOrder(self.comboBox_Polarization, self.comboBox_referenceCS)
        QWidget.setTabOrder(self.comboBox_referenceCS, self.lineEdit_Frequency)
        QWidget.setTabOrder(self.lineEdit_Frequency, self.comboBox_CutPlane_ThetaOrPhi)
        QWidget.setTabOrder(self.comboBox_CutPlane_ThetaOrPhi, self.lineEdit_CutPlane_AngleValue)
        QWidget.setTabOrder(self.lineEdit_CutPlane_AngleValue, self.lineEdit_sweep_ang_low)
        QWidget.setTabOrder(self.lineEdit_sweep_ang_low, self.lineEdit_sweep_ang_high)
        QWidget.setTabOrder(self.lineEdit_sweep_ang_high, self.pushButton_AddCut)
        QWidget.setTabOrder(self.pushButton_AddCut, self.comboBox_CutsAdded)
        QWidget.setTabOrder(self.comboBox_CutsAdded, self.pushButton_DeleteCut)
        QWidget.setTabOrder(self.pushButton_DeleteCut, self.pushButton_PlotCut)
        QWidget.setTabOrder(self.pushButton_PlotCut, self.pushButton_Clear_Plot)
        QWidget.setTabOrder(self.pushButton_Clear_Plot, self.lineEdit_SearchX1)
        QWidget.setTabOrder(self.lineEdit_SearchX1, self.lineEdit_SearchX2)
        QWidget.setTabOrder(self.lineEdit_SearchX2, self.lineEdit_SearchY1)
        QWidget.setTabOrder(self.lineEdit_SearchY1, self.lineEdit_SearchY2)
        QWidget.setTabOrder(self.lineEdit_SearchY2, self.lineEdit_SearchZ1)
        QWidget.setTabOrder(self.lineEdit_SearchZ1, self.lineEdit_SearchZ2)
        QWidget.setTabOrder(self.lineEdit_SearchZ2, self.pushButton_CreateOptimization)

        self.menubar.addAction(self.menuHelp.menuAction())
        self.menuHelp.addAction(self.actionHow_to_Use)

        self.retranslateUi(PhaseCenter)

        QMetaObject.connectSlotsByName(PhaseCenter)

    # setupUi

    def retranslateUi(self, PhaseCenter):
        PhaseCenter.setWindowTitle(QCoreApplication.translate("PhaseCenter", u"Phase Center App", None))
        self.actionHow_to_Use.setText(QCoreApplication.translate("PhaseCenter", u"How to Use", None))
        self.groupBox_UserInput.setTitle(QCoreApplication.translate("PhaseCenter", u"User Input", None))
        self.groupBox_RCS.setTitle(QCoreApplication.translate("PhaseCenter", u"Relative Coordinate System", None))
        self.label_OriginY.setText(QCoreApplication.translate("PhaseCenter", u"Y", None))
        self.comboBox_Euler.setItemText(0, QCoreApplication.translate("PhaseCenter", u"ZYZ", None))
        self.comboBox_Euler.setItemText(1, QCoreApplication.translate("PhaseCenter", u"ZXZ", None))

        self.lineEdit_OriginX.setText(QCoreApplication.translate("PhaseCenter", u"0", None))
        self.lineEdit_OriginY.setText(QCoreApplication.translate("PhaseCenter", u"0", None))
        self.lineEdit_OriginZ.setText(QCoreApplication.translate("PhaseCenter", u"0", None))
        self.lineEdit_EulerPhi.setText(QCoreApplication.translate("PhaseCenter", u"0", None))
        self.lineEdit_EulerTheta.setText(QCoreApplication.translate("PhaseCenter", u"0", None))
        self.lineEdit_EulerPsi.setText(QCoreApplication.translate("PhaseCenter", u"0", None))
        self.lineEdit_CutPlane_AngleValue.setText(QCoreApplication.translate("PhaseCenter", u"0", None))
        self.lineEdit_sweep_ang_low.setText(QCoreApplication.translate("PhaseCenter", u"-10", None))
        self.lineEdit_sweep_ang_high.setText(QCoreApplication.translate("PhaseCenter", u"10", None))

        self.label_EulerPsi.setText(QCoreApplication.translate("PhaseCenter", u"Psi", None))
        self.label_EulerPhi.setText(QCoreApplication.translate("PhaseCenter", u"Phi", None))
        self.label_Euler.setText(QCoreApplication.translate("PhaseCenter", u"Euler", None))
        self.label_Origin.setText(QCoreApplication.translate("PhaseCenter", u"Origin", None))
        self.label_OriginX.setText(QCoreApplication.translate("PhaseCenter", u"X", None))
        self.label_OriginZ.setText(QCoreApplication.translate("PhaseCenter", u"Z", None))
        self.label_EulerTheta.setText(QCoreApplication.translate("PhaseCenter", u"Theta", None))
        self.pushButton_CreateRCS.setText(QCoreApplication.translate("PhaseCenter", u"Create", None))

        self.pushButton_Exit.setText(QCoreApplication.translate("PhaseCenter", u"Exit", None))
        self.pushButton_Reset.setText(QCoreApplication.translate("PhaseCenter", u"Reset", None))

        self.groupBox_Visualize.setTitle(QCoreApplication.translate("PhaseCenter", u"Visualize", None))
        self.comboBox_ViewOrientation.setItemText(0, QCoreApplication.translate("PhaseCenter", u"XY", None))
        self.comboBox_ViewOrientation.setItemText(1, QCoreApplication.translate("PhaseCenter", u"YZ", None))
        self.comboBox_ViewOrientation.setItemText(2, QCoreApplication.translate("PhaseCenter", u"ZX", None))
        self.comboBox_ViewOrientation.setItemText(3, QCoreApplication.translate("PhaseCenter", u"Iso", None))

        self.comboBox_referenceCS1.setItemText(0, QCoreApplication.translate("PhaseCenter", u"Global", None))

        self.checkBox_ShowPattern.setText(QCoreApplication.translate("PhaseCenter", u"Pattern", None))
        self.pushButton_View.setText(QCoreApplication.translate("PhaseCenter", u"View", None))
        self.comboBox_unit.setItemText(0, QCoreApplication.translate("PhaseCenter", u"mm", None))
        self.comboBox_unit.setItemText(1, QCoreApplication.translate("PhaseCenter", u"cm", None))
        self.comboBox_unit.setItemText(2, QCoreApplication.translate("PhaseCenter", u"mil", None))
        self.comboBox_unit.setItemText(3, QCoreApplication.translate("PhaseCenter", u"meter", None))
        self.comboBox_unit.setItemText(4, QCoreApplication.translate("PhaseCenter", u"in", None))

        # if QT_CONFIG(tooltip)
        self.comboBox_unit.setToolTip("")

        # endif // QT_CONFIG(tooltip)
        # if QT_CONFIG(whatsthis)
        self.comboBox_unit.setWhatsThis("")

        # endif // QT_CONFIG(whatsthis)
        self.label_unit.setText(QCoreApplication.translate("PhaseCenter", u"Unit", None))
        self.groupBox_BeamCuts.setTitle(QCoreApplication.translate("PhaseCenter", u"Beam Cuts", None))
        self.label_Polarization.setText(QCoreApplication.translate("PhaseCenter", u"Polarization", None))
        self.comboBox_Polarization.setItemText(0, QCoreApplication.translate("PhaseCenter", u"X", None))
        self.comboBox_Polarization.setItemText(1, QCoreApplication.translate("PhaseCenter", u"Y", None))
        # self.comboBox_Polarization.setItemText(0, QCoreApplication.translate("PhaseCenter", u"Phi", None))
        # self.comboBox_Polarization.setItemText(1, QCoreApplication.translate("PhaseCenter", u"Theta", None))
        self.comboBox_Polarization.setItemText(2, QCoreApplication.translate("PhaseCenter", u"LHCP", None))
        self.comboBox_Polarization.setItemText(3, QCoreApplication.translate("PhaseCenter", u"RHCP", None))

        self.label_Frequency.setText(QCoreApplication.translate("PhaseCenter", u"Frequency", None))
        self.comboBox_referenceCS.setItemText(0, QCoreApplication.translate("PhaseCenter", u"Global", None))
        # self.comboBox_referenceCS.setItemText(1, QCoreApplication.translate("PhaseCenter", u"PCCS", None))

        self.label_referenceCS.setText(QCoreApplication.translate("PhaseCenter", u"Reference", None))
        self.label_CutPlane.setText(QCoreApplication.translate("PhaseCenter", u"Cut Plane", None))
        self.comboBox_CutPlane_ThetaOrPhi.setItemText(0, QCoreApplication.translate("PhaseCenter", u"Phi", None))
        self.comboBox_CutPlane_ThetaOrPhi.setItemText(1, QCoreApplication.translate("PhaseCenter", u"Theta", None))

        self.label_deg1.setText(QCoreApplication.translate("PhaseCenter", u"deg", None))
        self.label_equal.setText(QCoreApplication.translate("PhaseCenter", u"=", None))
        self.label_SweepWhat.setText(QCoreApplication.translate("PhaseCenter", u"Sweep Theta from", None))
        self.label_deg2.setText(QCoreApplication.translate("PhaseCenter", u"deg", None))
        self.label_to.setText(QCoreApplication.translate("PhaseCenter", u"to", None))
        self.pushButton_AddCut.setText(QCoreApplication.translate("PhaseCenter", u"Add Cut", None))
        # self.pushButton_DeleteCut.setText(QCoreApplication.translate("PhaseCenter", u"", None))
        # self.pushButton_PlotCut.setText(QCoreApplication.translate("PhaseCenter", u"PushButton", None))
        self.label_Initial_Guess.setText(QCoreApplication.translate("PhaseCenter", u"", None))
        # self.label_21.setText(QCoreApplication.translate("PhaseCenter", u"(x,y,z) = ", None))
        self.label_PC.setText(QCoreApplication.translate("PhaseCenter", u"", None))
        # self.label_sigma.setText(QCoreApplication.translate("PhaseCenter", u"\u03C3 =", None))
        # self.label_sigmaValue.setText(QCoreApplication.translate("PhaseCenter", u"NA", None))
        self.pushButton_Clear_Plot.setText(QCoreApplication.translate("PhaseCenter", u"Clear Plot", None))
        self.groupBox_optimization.setTitle(QCoreApplication.translate("PhaseCenter", u"Optimization", None))
        self.pushButton_CreateOptimization.setText(QCoreApplication.translate("PhaseCenter", u"Create\n"
                                                                                             " Optimization\n"
                                                                                             " Setup", None))
        self.label_SearchRange.setText(QCoreApplication.translate("PhaseCenter", u"Search Range", None))
        self.label_SearchRangeX.setText(QCoreApplication.translate("PhaseCenter", u"X", None))
        self.label_SearchRangeY.setText(QCoreApplication.translate("PhaseCenter", u"Y", None))
        self.label_SearchRangeZ.setText(QCoreApplication.translate("PhaseCenter", u"Z", None))
        self.pushButton_Reset.setText(QCoreApplication.translate("PhaseCenter", u"Reset", None))
        self.pushButton_Exit.setText(QCoreApplication.translate("PhaseCenter", u"Exit", None))
        # self.pushButton_Exit.setText(QCoreApplication.translate("PhaseCenter", u"Save", None))
        # self.label_sigma_of_plot.setText(QCoreApplication.translate("PhaseCenter", u"Sigma", None))
        self.label_status.setText(QCoreApplication.translate("PhaseCenter", u"Status:", None))
        # self.label_Modeler.setText(QCoreApplication.translate("PhaseCenter", u"TextLabel", None))
        self.menuHelp.setTitle(QCoreApplication.translate("PhaseCenter", u"Help", None))

    # retranslateUi

    def closeEvent(self, event: QCloseEvent) -> None:
        # self.reset()
        # self.hfss.save_project()
        # print('saving............')
        # time.sleep(3)
        self.hfss.release_desktop(False, False)

        event.accept(self)

    def getFrequency(self, str_freq_w_unit):
        freq_val = float(str_freq_w_unit[:-3])
        # read freq unit from the UI (assumed to be of length=3)
        freq_unit = str_freq_w_unit[-3:]
        # get multiplier i.e 4.5GHz becomes 4.5*1e9
        f = self.getFreqMultiplier(freq_unit)
        freq = freq_val * f
        return freq

    def setFrequency(self):
        if self.hfss.setups[0].props["SolveType"] == "MultiFrequency":
            myFreq = self.hfss.setups[0].props["MultipleAdaptiveFreqsSetup"]["AdaptAt"][0]["Frequency"]
        elif self.hfss.setups[0].props["SolveType"] == "Broadband":
            myFreq = self.hfss.setups[0].props["MultipleAdaptiveFreqsSetup"]["Low"]
        else:
            myFreq = self.hfss.setups[0].props["Frequency"]
        self.lineEdit_Frequency.setText(myFreq)

    def populateSearch(self):
        unit = self.comboBox_unit.currentText()

        originX = self.lineEdit_OriginX.text()
        originY = self.lineEdit_OriginY.text()
        originZ = self.lineEdit_OriginZ.text()

        self.lineEdit_SearchX1.setText(str(float(originX) - 1))
        self.lineEdit_SearchX2.setText(str(float(originX) + 1))

        self.lineEdit_SearchY1.setText(str(float(originY) - 1))
        self.lineEdit_SearchY2.setText(str(float(originY) + 1))

        self.lineEdit_SearchZ1.setText(str(float(originZ) - 1))
        self.lineEdit_SearchZ2.setText(str(float(originZ) + 1))

    def createPostProcessingVar(self, originX, originY, originZ, unit):
        self.hfss["post_PhaseCenter_X"] = originX + unit
        self.hfss["post_PhaseCenter_Y"] = originY + unit
        self.hfss["post_PhaseCenter_Z"] = originZ + unit

    def createRCS(self):
        Inf_setup_list = [x for x in self.hfss.field_setups if self.Inf_PC in x.name]
        if Inf_setup_list:
            [x.delete() for x in Inf_setup_list]
        CS_list = [x for x in self.hfss.modeler.coordinate_systems if self.PC_CS_name in x.name]
        if CS_list:
            [x.delete() for x in CS_list]

        self.hfss.save_project()
        # time.sleep(2)

        if self.comboBox_referenceCS.count() == 1:
            name = self.PC_CS_name
            self.comboBox_referenceCS.addItem(name)
            self.comboBox_referenceCS1.addItem(name)
        self.label_status.setText("Creating Relative Coordinate System for phase center calculation")
        self.hfss.save_project()

        unit = self.comboBox_unit.currentText()
        mode = self.comboBox_Euler.currentText().lower()

        euler_phi = self.lineEdit_EulerPhi.text()
        euler_theta = self.lineEdit_EulerTheta.text()
        euler_psi = self.lineEdit_EulerPsi.text()

        originX = self.lineEdit_OriginX.text()
        originY = self.lineEdit_OriginY.text()
        originZ = self.lineEdit_OriginZ.text()
        origin = [originX + unit, originY + unit, originZ + unit]
        self.populateSearch()
        self.setFrequency()

        self.hfss.modeler.create_coordinate_system(name=self.PC_CS_name, origin=origin, \
                                                   reference_cs='Global', mode=mode, \
                                                   phi=euler_phi, theta=euler_theta, \
                                                   psi=euler_psi)
        self.label_status.setText("Created Relative Coordinate System")
        # As soon as relative CS created, update the image to show the new CS

        [x.delete() for x in self.hfss.field_setups if x.name == self.Inf_PC]
        self.hfss.insert_infinite_sphere(definition='Theta-Phi', x_start=-180, x_stop=180, x_step=self.theta_step,
                                         y_start=0, y_stop=180, y_step=self.phi_step, units='deg',
                                         custom_radiation_faces=None, custom_coordinate_system=self.PC_CS_name,
                                         use_slant_polarization=False, polarization_angle=45,
                                         name=self.Inf_PC)
        self.createPostProcessingVar("0", "0", "0", unit)
        origin = ["post_PhaseCenter_X", "post_PhaseCenter_Y", "post_PhaseCenter_Z"]
        self.hfss.modeler.create_coordinate_system(name=self.PC_CS_name + "optim",
                                                   origin=origin, \
                                                   reference_cs=self.PC_CS_name)
        self.hfss.insert_infinite_sphere(definition='Theta-Phi', x_start=-180, x_stop=180, x_step=self.theta_step,
                                         y_start=0, y_stop=180, y_step=self.phi_step, units='deg',
                                         custom_radiation_faces=None,
                                         custom_coordinate_system=self.PC_CS_name + "optim",
                                         use_slant_polarization=False, polarization_angle=45,
                                         name=self.Inf_PC + "optim")
        self.hfss.post.export_model_picture(self.hfss.working_directory + "/test_img2.jpg", show_grid=False,
                                            show_ruler=False, orientation="Isometric")
        self.pixmap = QPixmap(self.hfss.working_directory + "/test_img2.jpg")
        # self.label_img = QLabel(Form)
        self.label_Modeler.setPixmap(self.pixmap)
        self.label_Modeler.setScaledContents(True)

        self.label_status.setText("Infinite Sphere Setup referenced to Phase Center CS created")

    def visualize(self):
        hfss = self.hfss
        if self.comboBox_referenceCS1.currentText() == "Global":
            cs = "Global"
        elif self.comboBox_referenceCS1.currentText() == "PCCS":
            cs = self.PC_CS_name
        elif "PCCS" in self.comboBox_referenceCS1.currentText():
            cs = self.comboBox_referenceCS1.currentText()

        self.hfss.modeler.set_working_coordinate_system(cs)

        if self.comboBox_ViewOrientation.currentText() == "XY":
            orientation = "top"
        elif self.comboBox_ViewOrientation.currentText() == "ZX":
            orientation = "Right"
        elif self.comboBox_ViewOrientation.currentText() == "YZ":
            orientation = "Front"
        else:
            orientation = "Isometric"

        hfss.post.export_model_picture(self.hfss.working_directory + "/test_img.jpg", show_grid=False,
                                       show_ruler=False, orientation=orientation)
        self.pixmap = QPixmap(self.hfss.working_directory + "/test_img.jpg")
        # self.label_img = QLabel(Form)
        self.label_Modeler.setPixmap(self.pixmap)
        self.label_Modeler.setScaledContents(True)

        setupName = hfss.existing_analysis_setups[0]
        setup_sweep_name = setupName + " : LastAdaptive"
        ## show pattern
        if self.checkBox_ShowPattern.isChecked():
            variations = {}
            variations["Freq"] = [self.lineEdit_Frequency.text()]
            variations["Theta"] = ["All"]
            variations["Phi"] = ["All"]

            ffData = hfss.post.get_solution_data(expressions="GainTotal", setup_sweep_name=setup_sweep_name,
                                                 report_category="Far Fields", \
                                                 context=self.Inf_global, variations=variations)
            hfss.post.create_3d_plot(ffData)

    def deleteCut(self):
        if self.comboBox_CutsAdded.currentText() == "":
            return
        c = self.comboBox_CutsAdded.currentText().split()
        phiOrtheta = c[2]
        cutangle = c[4][:-1]
        if c[12] == 'Global':
            self.label_status.setText("No worries. Global cuts won't be used in optimization")
        else:
            del self.cuts[phiOrtheta][cutangle]
        self.comboBox_CutsAdded.removeItem(self.comboBox_CutsAdded.currentIndex())

    def plotCut(self, n):
        unit = self.comboBox_unit.currentText()
        if self.comboBox_CutsAdded.currentText() == '' or self.lineEdit_Frequency.text() == '':
            return
        # for item in self.plotwidget.listDataItems():
        #     self.plotwidget.removeItem(item)
        hfss = self.hfss
        setupName = hfss.existing_analysis_setups[0]  # pick only the first analysis setup
        setup_sweep_name = setupName + " : LastAdaptive"
        variations = {}
        variations["Freq"] = [self.lineEdit_Frequency.text()]
        variations["Theta"] = ["All"]
        variations["Phi"] = ["All"]
        cut_description = self.comboBox_CutsAdded.currentText()  # 1st key to get theta or phi cut
        cut_at, cut_angle, sweep_from, sweep_to, polarization, relCS = self.getCutInfo(cut_description)
        if relCS == "Global":
            context = self.Inf_global
        elif relCS == "PCCS":
            context = self.Inf_PC
        # if self.comboBox_referenceCS.currentText()=="Global":
        #     context=self.Inf_global
        # else:
        #     context=self.Inf_PC

        self.label_status.setText("Plotting...........")

        ffData = hfss.post.get_solution_data(expressions="cang_deg(rE" + polarization + ")",
                                             setup_sweep_name=setup_sweep_name, report_category="Far Fields", \
                                             context=context, variations=variations)
        ffData_freq_array = ffData.intrinsics["Freq"]
        ffData_theta_array = ffData.intrinsics["Theta"]
        ffData_phi_array = ffData.intrinsics["Phi"]

        if cut_at == "Phi":
            primary_sweep_variable = "Theta"
            angle_array = ffData_theta_array
        else:
            primary_sweep_variable = "Phi"
            angle_array = ffData_phi_array

        p = float(cut_angle[:-4])
        A = self.get_array(sweep_from, sweep_to, angle_array)
        if cut_at == "Phi":
            min_val, min_pos = self.find_min_val_pos(ffData_phi_array, p)
            families_dict = {"Freq": self.lineEdit_Frequency.text(), "Theta": A, "Phi": str(min_val) + "deg"}
        else:
            min_val, min_pos = self.find_min_val_pos(ffData_theta_array, p)
            families_dict = {"Freq": self.lineEdit_Frequency.text(), "Theta": str(min_val) + "deg", "Phi": A}
        report_category = "Far Fields"
        plot_type = "Rectangular Plot"
        plot_name = "rE"
        # polarization = self.comboBox_Polarization.currentText()
        cut_data = hfss.post.get_solution_data(expressions="rE" + polarization, \
                                               setup_sweep_name=setup_sweep_name,
                                               primary_sweep_variable=primary_sweep_variable, \
                                               report_category="Far Fields", context=context,
                                               variations=families_dict)
        # self.label_sigma_of_plot.setText("Sigma = "+str(numpy.std(cut_data.data_phase(radians=False))))
        # self.label_sigma_of_plot.adjustSize()
        # called only in auto mode

        ## Plotting begins
        self.plotwidget.addLegend(offset=(30, 10))
        ## Pencolor will cycle through the LINECOLORS. On repeat the line thickness w will be reduced to 1. Hopefully no\
        # one will keep adding more. If cycled through thrid time, you can't distinguish but it will any way be \
        # indistinguishable due to too many curves
        mkPenColor = self.LINECOLORS[self.numCurves % len(self.LINECOLORS)]
        if self.numCurves >= len(self.LINECOLORS):
            w = 1
        else:
            w = 3
        ## Legend uses greek symbol for cut plane phi/theta, and polarization phi, theta, rhcp, lhcp
        if cut_at == "Phi":
            cutplane = "\u03C6"
        else:
            cutplane = "\u03B8"
        if polarization == "Theta":
            pol = "\u0398"
        elif polarization == "Phi":
            pol = "\u03A6"
        elif polarization == "LHCP":
            pol = "\u21BB"
        elif polarization == "RHCP":
            pol = "\u21BA"
        elif polarization == "X":
            pol = "X"
        elif polarization == "Y":
            pol = "Y"
        self.plotwidget.plot(cut_data.primary_sweep_values, cut_data.data_phase(radians=False),
                             pen=pyqtgraph.mkPen(mkPenColor, width=w), \
                             name=cutplane + "=" + str(cut_angle)[:-1] + " | " + pol,
                             label={'left': "Y", "bottom": "X"})
        self.numCurves += 1
        self.label_status.setText("Plot Created.")
        self.hfss.save_project()

    def convertMeterToUnit(self, n, unit):
        '''unit assumed mil, mm, cm, meter, in\
        n is in meters'''
        if unit == "mil":
            f = 1 / (25.4 * 1e-6)
        elif unit == "mm":
            f = 1000
        elif unit == "cm":
            f = 100
        elif unit == "meter":
            f = 1
        elif unit == "in":
            f = 1 / 0.0254
        else:
            pass
        return n * f

    def getFreqMultiplier(self, freq_unit):
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

    def getCutInfo(self, cut_description):
        c = cut_description.split()
        # print(c)
        cut_at = c[2]  # phi or theta
        cut_angle = c[4]  # value of cut angle
        sweep_from = c[8]
        sweep_to = c[10]
        polarization = c[11]
        relCS = c[12]
        return cut_at, cut_angle, sweep_from, sweep_to, polarization, relCS

    def clearPlots(self):
        for item in self.plotwidget.listDataItems():
            self.plotwidget.removeItem(item)
        self.numCurves = 0
        self.label_status.setText("Plots cleared.")

    def reset(self):
        # for item in self.plotwidget.listDataItems():
        #     self.plotwidget.removeItem(item)
        self.lineEdit_OriginX.setText("0")
        self.lineEdit_OriginY.setText("0")
        self.lineEdit_OriginZ.setText("0")
        self.lineEdit_sweep_ang_high.setText("10")
        self.lineEdit_sweep_ang_low.setText("-10")
        self.lineEdit_EulerPhi.setText("0")
        self.lineEdit_EulerTheta.setText("0")
        self.lineEdit_EulerPsi.setText("0")
        self.lineEdit_CutPlane_AngleValue.setText("0")
        self.lineEdit_SearchX1.setText("")
        self.lineEdit_SearchX2.setText("")
        self.lineEdit_SearchY1.setText("")
        self.lineEdit_SearchY2.setText("")
        self.lineEdit_SearchZ1.setText("")
        self.lineEdit_SearchZ2.setText("")
        Inf_setup_list = [x for x in self.hfss.field_setups if self.Inf_PC in x.name or self.Inf_global in x.name]
        if Inf_setup_list:
            [x.delete() for x in Inf_setup_list]
            print("Deleted field setups from last run")
        self.hfss._project_dictionary = None
        self.hfss.save_project()
        CS_list = [x for x in self.hfss.modeler.coordinate_systems if self.PC_CS_name in x.name]

        if CS_list:
            [l.delete() for l in CS_list]
            print("Deleted coordinate systems from last run")

        self.hfss.save_project()
        # [x.delete() for x in self.hfss.modeler.coordinate_systems if self.PC_CS_name in x.name]

    def exitApp(self):
        self.hfss.save_project()
        self.hfss.release_desktop(False, False)
        QCoreApplication.instance().quit()  # close the app after use.

    def theta_or_phi_plane_chosen(self):
        if self.comboBox_CutPlane_ThetaOrPhi.currentText() == "Theta":
            self.label_SweepWhat.setText("Sweep Phi from")
        else:
            self.label_SweepWhat.setText("Sweep Theta from")

    def check_within_range(self):
        s = self.sender()
        val = s.text()
        if s in [self.lineEdit_CutPlane_AngleValue, self.lineEdit_sweep_ang_high, self.lineEdit_sweep_ang_low]:
            # if self.comboBox_cutPlane.currentText() =="Theta":
            #     l = -180
            #     u = 180
            # else:
            #     l = 0
            #     u = 180
            l = -180;
            u = 180
            if float(val) > u or float(val) < l:
                dlg = QMessageBox()
                dlg.setWindowTitle("Error")
                dlg.setText("Out of range!")
                button = dlg.exec()
                if button == QMessageBox.Ok:
                    s.setText('')
            return

    def add_cut_to_list(self):
        sweep_angle = self.comboBox_CutPlane_ThetaOrPhi.currentText()
        polarization = self.comboBox_Polarization.currentText()
        relCS = self.comboBox_referenceCS.currentText()
        if not self.lineEdit_sweep_ang_low.text() or not self.lineEdit_sweep_ang_high.text() or not self.lineEdit_CutPlane_AngleValue.text():
            dlg = QMessageBox()
            dlg.setWindowTitle("Error")
            dlg.setText("No value given!")
            button = dlg.exec()
            # if button == QMessageBox.Ok:
            #    self.lineEdit_sweep_ang_high.setText('')
            return
        # print("Low = ", self.lineEdit_sweep_ang_low.text())
        low = float(self.lineEdit_sweep_ang_low.text())
        high = float(self.lineEdit_sweep_ang_high.text())

        if (low >= high):
            dlg = QMessageBox()
            dlg.setWindowTitle("Error")
            dlg.setText("Lower limit >= upper!")
            button = dlg.exec()
            if button == QMessageBox.Ok:
                self.lineEdit_sweep_ang_low.setText('')
                self.lineEdit_sweep_ang_high.setText('')
                return
        if (high - low) < 4:
            dlg = QMessageBox()
            dlg.setWindowTitle("Error")
            dlg.setText("Sweep over range >= 4 deg.")
            button = dlg.exec()
            if button == QMessageBox.Ok:
                self.lineEdit_sweep_ang_low.setText('')
                self.lineEdit_sweep_ang_high.setText('')
                return
        # if relCS == "PCCS":
        #     self.cuts[self.comboBox_CutPlane_ThetaOrPhi.currentText()][self.lineEdit_CutPlane_AngleValue.text() + "deg"] = [
        #     self.lineEdit_sweep_ang_low.text() + "deg", self.lineEdit_sweep_ang_high.text() + "deg", polarization, relCS ]

        if relCS != "Global":
            self.cuts[self.comboBox_CutPlane_ThetaOrPhi.currentText()][
                self.lineEdit_CutPlane_AngleValue.text() + "deg"] = [
                self.lineEdit_sweep_ang_low.text() + "deg", self.lineEdit_sweep_ang_high.text() + "deg", polarization,
                relCS]

        # #print(self.cuts)
        # self.comboBox_CutsAdded.addItem(
        #     "Cut at " + sweep_angle + " = " + self.lineEdit_CutPlane_AngleValue.text() + "deg, " + \
        #     self.label_SweepWhat.text() + " " + self.lineEdit_sweep_ang_low.text() + "deg to " + \
        #     self.lineEdit_sweep_ang_high.text() + "deg "+polarization)
        # add logic to show only right value available in infinite sphere for the cut angle. self.lineEdit_CutPlane_AngleValue.text()
        this_cut = "Cut at " + sweep_angle + " = " + self.lineEdit_CutPlane_AngleValue.text() + "deg, " + \
                   self.label_SweepWhat.text() + " " + self.lineEdit_sweep_ang_low.text() + "deg to " + \
                   self.lineEdit_sweep_ang_high.text() + "deg " + polarization + " " + relCS
        if this_cut not in [self.comboBox_CutsAdded.itemText(i) for i in range(self.comboBox_CutsAdded.count())]:
            # print("unique cut")
            self.comboBox_CutsAdded.insertItem(0, this_cut)
        self.comboBox_CutsAdded.setCurrentText(this_cut)
        # self.hfss.save_project()

    def createOptimization(self):

        # if PC was suggested, read which value was accepted.
        # Create post processing variables.
        # Assign origin for the Corresponding CS [post_PhaseX,Y,Z] with same values
        # use this CS as context in optimization goals.
        self.label_status.setText("Adding optimization goals.........")
        if self.comboBox_CutsAdded.currentText() == "":
            self.label_status.setText("Add some beam cuts to optimize on!")
            return
        l = [self.comboBox_CutsAdded.itemText(i) for i in range(self.comboBox_CutsAdded.count()) if
             self.comboBox_CutsAdded.itemText(i)[-6:] != 'Global']
        if l == []:
            self.label_status.setText("Add cuts wrt phase center coordinate system")
            dlg = QMessageBox()
            dlg.setWindowTitle("Error")
            dlg.setText("All cuts are wrt Global CS. Add some cut(s) wrt phase center coordinate system !")
            button = dlg.exec()
            if button == QMessageBox.Ok:
                return
        x1 = float(self.lineEdit_SearchX1.text())
        x2 = float(self.lineEdit_SearchX2.text())
        y1 = float(self.lineEdit_SearchY1.text())
        y2 = float(self.lineEdit_SearchY2.text())
        z1 = float(self.lineEdit_SearchZ1.text())
        z2 = float(self.lineEdit_SearchZ2.text())
        if x1 > x2 or y1 > y2 or z1 > z2:
            self.label_status.setText("Low>High!")
            dlg = QMessageBox()
            dlg.setWindowTitle("Error")
            dlg.setText("Low > High!")
            button = dlg.exec()
            if button == QMessageBox.Ok:
                return

        self.pushButton_CreateOptimization.blockSignals(True)
        self.label_status.setText("Creating Optimization Setup........")
        # print("Creating Optimization Setup")

        cuts = self.cuts
        hfss = self.hfss

        polarization = self.comboBox_Polarization.currentText()
        variations = {}
        variations["Freq"] = [self.lineEdit_Frequency.text()]
        variations["Theta"] = ["All"]
        variations["Phi"] = ["All"]

        context = self.Inf_PC + "optim"

        setup_sweep_name = hfss.existing_analysis_setups[0] + " : LastAdaptive"
        try:
            ffData = hfss.post.get_solution_data(expressions="cang_deg(rE" + polarization + ")",
                                                 setup_sweep_name=setup_sweep_name, report_category="Far Fields", \
                                                 context=context, variations=variations)
        except:
            print("Far Field Data not available")
        goals_list = self.get_goals(ffData.intrinsics["Freq"], ffData.intrinsics["Theta"], ffData.intrinsics["Phi"],
                                    context)  # returns ["Name:Goals",[],[],[],[]...]
        unit = self.comboBox_unit.currentText()

        min_x = float(self.lineEdit_SearchX1.text())
        max_x = float(self.lineEdit_SearchX2.text())
        min_y = float(self.lineEdit_SearchY1.text())
        max_y = float(self.lineEdit_SearchY2.text())
        min_z = float(self.lineEdit_SearchZ1.text())
        max_z = float(self.lineEdit_SearchZ2.text())

        hfss.activate_variable_optimization(variable_name="post_PhaseCenter_X", min_val=str(min_x) + unit,
                                            max_val=str(max_x) + unit)
        hfss.activate_variable_optimization(variable_name="post_PhaseCenter_Y", min_val=str(min_y) + unit,
                                            max_val=str(max_y) + unit)
        hfss.activate_variable_optimization(variable_name="post_PhaseCenter_Z", min_val=str(min_z) + unit,
                                            max_val=str(max_z) + unit)

        oModule = self.hfss.odesign.GetModule("Optimetrics")
        oModule.InsertSetup("OptiOptimization",
                            [
                                "NAME:OptimizationSetup_PC",
                                "IsEnabled:=", True,
                                [
                                    "NAME:ProdOptiSetupDataV2",
                                    "SaveFields:="	, True,
                                    "CopyMesh:="		, True,
                                    "SolveWithCopiedMeshOnly:=", True
                                ],
                                [
                                    "NAME:StartingPoint",
                                    "post_PhaseCenter_X:="		, self.lineEdit_OriginX.text( ) +unit,
                                    "post_PhaseCenter_Y:="		, self.lineEdit_OriginY.text( ) +unit,
                                    "post_PhaseCenter_Z:="		, self.lineEdit_OriginZ.text( ) +unit
                                ],
                                "Optimizer:="		, "kDX ASO",
                                [
                                    "NAME:AnalysisStopOptions",
                                    "StopForNumIteration:="	, True,
                                    "StopForElapsTime:="	, False,
                                    "StopForSlowImprovement:=", False,
                                    "StopForGrdTolerance:="	, False,
                                    "MaxNumIteration:="	, 100,
                                    "MaxSolTimeInSec:="	, 3600,
                                    "RelGradientTolerance:=", 0,
                                    "MinNumIteration:="	, 10
                                ],
                                "CostFuncNormType:="	, "L2",
                                "PriorPSetup:="		, "",
                                "PreSolvePSetup:="	, True,
                                [
                                    "NAME:Variables",
                                    "post_PhaseCenter_X:=", ["i:=", True ,"int:=", False, "Min:=", min_x, "Max:=", max_x, "MinStep:=",
                                     "0.1" + unit, "MaxStep:=", "1" + unit, "MinFocus:=", "-2" + unit, "MaxFocus:=",
                                     "15" + unit, "UseManufacturableValues:=", "false", "Level:=", "[5: 15] mm"],
                                    "post_PhaseCenter_Y:=",
                                    ["i:=", True, "int:=", False, "Min:=", min_y, "Max:=", max_y, "MinStep:=",
                                     "0.1" + unit, "MaxStep:=", "1" + unit, "MinFocus:=", "-2" + unit, "MaxFocus:=",
                                     "15" + unit, "UseManufacturableValues:=", "false", "Level:=", "[5: 15] mm"],
                                    "post_PhaseCenter_Z:=",
                                    ["i:=", True, "int:=", False, "Min:=", min_z, "Max:=", max_z, "MinStep:=",
                                     "0.02" + unit, "MaxStep:=", "0.2" + unit, "MinFocus:=", "-2" + unit, "MaxFocus:=",
                                     "1" + unit, "UseManufacturableValues:=", "false", "Level:=", "[-1: 1] mm"]
                                ],
                                [
                                    "NAME:LCS"
                                ],

                                goals_list
                                ,
                                "Acceptable_Cost:=", 0,
                                "Noise:="	, 0.0001,
                                "UpdateDesign:="	, False,
                                "UpdateIteration:="	, 5,
                                "KeepReportAxis:="	, True,
                                "UpdateDesignWhenDone:=", True,
                                [
                                    "NAME:DXOptimizerOptionData",
                                    "InitSamples:="		, 12,
                                    "MaxEvaluations:="	, 48,
                                    "ConvergenceTolerance:=", 0.001,
                                    "RandomSeed:="		, 0,
                                    "MaxCydes:="		, 10,
                                    "ScreenSamples:="	, 300,
                                    "StartingPoints:="	, 9,
                                    "MaxDomainReductions:="	, 20,
                                    "PercentDomainReductions:=", 0.1,
                                    "RetainedDomainPerIteration:=", 40
                                ]
                            ])
        self.hfss.save_project()
        self.label_status.setText("Done")
        self.hfss.release_desktop(False ,False)
        time.sleep(2)
        QCoreApplication.instance().quit()  # close the app after use.

    def get_goals(self, f, t, ph, context):
        self.label_status.setText("Getting goals...")
        cuts = self.cuts
        hfss = self.hfss
        setup_sweep_name = hfss.existing_analysis_setups[0] + " : LastAdaptive"
        # polarization = self.buttonGroup.checkedButton().text()
        G = ["NAME:Goals"]
        for k in cuts.keys():  # theta cuts or Phi cuts - only 2 iterations
            if k == "Phi":
                primary_sweep_variable = "Theta"
                angle_array = t
            else:
                primary_sweep_variable = "Phi"
                angle_array = ph
            for c in cuts[k].keys():  # value of cut angle whether theta or phi
                polarization = cuts[k][c][2]
                p = float(c[:-3])
                A = self.get_array(cuts[k][c][0], cuts[k][c][1], angle_array)
                start = A[0]
                stop = A[-1]
                DiscreteValues = ','.join(A)
                if k == "Phi":
                    cut_variable = "Phi"
                    min_val, min_pos = self.find_min_val_pos(ph, p)
                    cut_value = str(min_val) + "deg"
                else:
                    cut_variable = "Theta"
                    min_val, min_pos = self.find_min_val_pos(t, p)
                    cut_value = str(min_val) + "deg"
                Gi = ["NAME:Goal", "ReportType:=", "Far Fields", "Solution:=", setup_sweep_name
                    , ["NAME:SimValueContext", "Context:=", context],
                      "Calculation:=", "pk2pk(cang_deg(rE" + polarization + "))",
                      "Name:="	, "pk2pk(cang_deg(rE" +polarization + "))",
                      [
                          "NAME:Ranges",
                          "Range:="	, [	"Var:=", primary_sweep_variable ,"Type:=", "rd", "Start:=", start, "Stop:=", stop
                          , "DiscreteValues:=", DiscreteValues],
                          "Range:="	, [	"Var:=", cut_variable,	"Type:=", "d" ,"DiscreteValues:=", cut_value],
                          "Range:="	, [ "Var:=", "Freq" ,"Type:=", "d", "DiscreteValues:=", str(f[0]) + "GHz"]
                      ],
                      "Condition:="	, "<=" ,["NAME:GoalValue" ,"GoalValueType:="	,"Independent" ,"Format:=", "Real/Img " ,"bG:="
                       ,["v:=", "[0.005;]"]],
                      "Weight:="		, "[1;]"
                      ]
                G.append(Gi)
        return G

    def get_array(self ,start :str, stop :str , arry :list):
        start = float(start[:-3])
        stop = float(stop[:-3])
        array = [str(x ) +"deg" for x in arry if x>= start and x <= stop ]
        return array

    def find_min_val_pos(self, array, number):
        m = [abs(x - number) for x in array]
        min_pos = m.index(min(m))
        min_val = array[min_pos]
        return min_val, min_pos

if __name__ == "__main__":
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = UiPhaseCenter()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())
