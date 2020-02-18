# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'blanka_gui.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from run_blanka import *
from subprocess import call, CREATE_NEW_CONSOLE, PIPE, STDOUT, Popen
from PyQt4 import QtCore, QtGui
import sys

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("BLANKA GUI"))
        MainWindow.resize(621, 551)
        MainWindow.setMinimumSize(QtCore.QSize(621, 551))
        MainWindow.setMaximumSize(QtCore.QSize(621, 551))
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.sample_label = QtGui.QLabel(self.centralwidget)
        self.sample_label.setGeometry(QtCore.QRect(10, 10, 81, 16))
        self.sample_label.setObjectName(_fromUtf8("sample_label"))
        self.sample_text = QtGui.QLineEdit(self.centralwidget)
        self.sample_text.setGeometry(QtCore.QRect(10, 30, 411, 20))
        self.sample_text.setObjectName(_fromUtf8("sample_text"))
        self.sample_file_browser = QtGui.QPushButton(self.centralwidget)
        self.sample_file_browser.setGeometry(QtCore.QRect(440, 30, 31, 23))
        self.sample_file_browser.setObjectName(_fromUtf8("sample_file_browser"))
        self.num_samples = QtGui.QCheckBox(self.centralwidget)
        self.num_samples.setGeometry(QtCore.QRect(490, 30, 121, 21))
        self.num_samples.setObjectName(_fromUtf8("num_samples"))
        self.control_text = QtGui.QLineEdit(self.centralwidget)
        self.control_text.setGeometry(QtCore.QRect(10, 90, 411, 20))
        self.control_text.setObjectName(_fromUtf8("control_text"))
        self.control_label = QtGui.QLabel(self.centralwidget)
        self.control_label.setGeometry(QtCore.QRect(10, 70, 81, 16))
        self.control_label.setObjectName(_fromUtf8("control_label"))
        self.control_file_browser = QtGui.QPushButton(self.centralwidget)
        self.control_file_browser.setGeometry(QtCore.QRect(440, 90, 31, 23))
        self.control_file_browser.setObjectName(_fromUtf8("control_file_browser"))
        self.num_controls = QtGui.QCheckBox(self.centralwidget)
        self.num_controls.setGeometry(QtCore.QRect(490, 90, 121, 21))
        self.num_controls.setObjectName(_fromUtf8("num_controls"))
        self.output_label = QtGui.QLabel(self.centralwidget)
        self.output_label.setGeometry(QtCore.QRect(10, 130, 141, 16))
        self.output_label.setObjectName(_fromUtf8("output_label"))
        self.output_text = QtGui.QLineEdit(self.centralwidget)
        self.output_text.setGeometry(QtCore.QRect(10, 150, 411, 20))
        self.output_text.setObjectName(_fromUtf8("output_text"))
        self.output_file_browser = QtGui.QPushButton(self.centralwidget)
        self.output_file_browser.setGeometry(QtCore.QRect(440, 150, 31, 23))
        self.output_file_browser.setObjectName(_fromUtf8("output_file_browser"))
        self.instrument_label = QtGui.QLabel(self.centralwidget)
        self.instrument_label.setGeometry(QtCore.QRect(10, 190, 71, 21))
        self.instrument_label.setObjectName(_fromUtf8("instrument_label"))
        self.instrument_choice = QtGui.QComboBox(self.centralwidget)
        self.instrument_choice.setGeometry(QtCore.QRect(90, 190, 161, 22))
        self.instrument_choice.setObjectName(_fromUtf8("instrument_choice"))
        self.instrument_choice.addItem(_fromUtf8(""))
        self.instrument_choice.addItem(_fromUtf8(""))
        self.instrument_choice.addItem(_fromUtf8(""))
        self.ms1_threshold_label = QtGui.QLabel(self.centralwidget)
        self.ms1_threshold_label.setGeometry(QtCore.QRect(10, 230, 251, 21))
        self.ms1_threshold_label.setObjectName(_fromUtf8("ms1_threshold_label"))
        self.ms1_threshold_text = QtGui.QLineEdit(self.centralwidget)
        self.ms1_threshold_text.setGeometry(QtCore.QRect(260, 230, 51, 21))
        self.ms1_threshold_text.setObjectName(_fromUtf8("ms1_threshold_text"))
        self.ms2_threshold_text = QtGui.QLineEdit(self.centralwidget)
        self.ms2_threshold_text.setGeometry(QtCore.QRect(260, 270, 51, 20))
        self.ms2_threshold_text.setText(_fromUtf8(""))
        self.ms2_threshold_text.setObjectName(_fromUtf8("ms2_threshold_text"))
        self.ms2_threshold_label = QtGui.QLabel(self.centralwidget)
        self.ms2_threshold_label.setGeometry(QtCore.QRect(10, 270, 251, 21))
        self.ms2_threshold_label.setObjectName(_fromUtf8("ms2_threshold_label"))
        self.snr_label = QtGui.QLabel(self.centralwidget)
        self.snr_label.setGeometry(QtCore.QRect(10, 310, 111, 21))
        self.snr_label.setObjectName(_fromUtf8("snr_label"))
        self.snr_text = QtGui.QLineEdit(self.centralwidget)
        self.snr_text.setGeometry(QtCore.QRect(120, 310, 51, 20))
        self.snr_text.setText(_fromUtf8(""))
        self.snr_text.setObjectName(_fromUtf8("snr_text"))
        self.snr_unit = QtGui.QLabel(self.centralwidget)
        self.snr_unit.setGeometry(QtCore.QRect(180, 310, 21, 21))
        self.snr_unit.setObjectName(_fromUtf8("snr_unit"))
        self.rt_label = QtGui.QLabel(self.centralwidget)
        self.rt_label.setGeometry(QtCore.QRect(10, 350, 151, 21))
        self.rt_label.setObjectName(_fromUtf8("rt_label"))
        self.rt_unit = QtGui.QLabel(self.centralwidget)
        self.rt_unit.setGeometry(QtCore.QRect(230, 350, 21, 21))
        self.rt_unit.setObjectName(_fromUtf8("rt_unit"))
        self.rt_text = QtGui.QLineEdit(self.centralwidget)
        self.rt_text.setGeometry(QtCore.QRect(170, 350, 51, 20))
        self.rt_text.setText(_fromUtf8(""))
        self.rt_text.setObjectName(_fromUtf8("rt_text"))
        self.precursor_mz_label = QtGui.QLabel(self.centralwidget)
        self.precursor_mz_label.setGeometry(QtCore.QRect(10, 390, 151, 21))
        self.precursor_mz_label.setObjectName(_fromUtf8("precursor_mz_label"))
        self.precursor_mz_text = QtGui.QLineEdit(self.centralwidget)
        self.precursor_mz_text.setGeometry(QtCore.QRect(160, 390, 51, 20))
        self.precursor_mz_text.setText(_fromUtf8(""))
        self.precursor_mz_text.setObjectName(_fromUtf8("precursor_mz_text"))
        self.precursor_mz_unit = QtGui.QLabel(self.centralwidget)
        self.precursor_mz_unit.setGeometry(QtCore.QRect(220, 390, 21, 21))
        self.precursor_mz_unit.setObjectName(_fromUtf8("precursor_mz_unit"))
        self.peak_mz_label = QtGui.QLabel(self.centralwidget)
        self.peak_mz_label.setGeometry(QtCore.QRect(10, 430, 121, 21))
        self.peak_mz_label.setObjectName(_fromUtf8("peak_mz_label"))
        self.peak_mz_unit = QtGui.QLabel(self.centralwidget)
        self.peak_mz_unit.setGeometry(QtCore.QRect(200, 430, 21, 21))
        self.peak_mz_unit.setObjectName(_fromUtf8("peak_mz_unit"))
        self.peak_mz_text = QtGui.QLineEdit(self.centralwidget)
        self.peak_mz_text.setGeometry(QtCore.QRect(140, 430, 51, 20))
        self.peak_mz_text.setText(_fromUtf8(""))
        self.peak_mz_text.setObjectName(_fromUtf8("peak_mz_text"))
        self.noise_removal_only = QtGui.QCheckBox(self.centralwidget)
        self.noise_removal_only.setGeometry(QtCore.QRect(370, 310, 121, 21))
        self.noise_removal_only.setObjectName(_fromUtf8("noise_removal_only"))
        self.blank_removal_only = QtGui.QCheckBox(self.centralwidget)
        self.blank_removal_only.setGeometry(QtCore.QRect(370, 350, 121, 21))
        self.blank_removal_only.setObjectName(_fromUtf8("blank_removal_only"))
        self.verbose = QtGui.QCheckBox(self.centralwidget)
        self.verbose.setGeometry(QtCore.QRect(370, 390, 121, 21))
        self.verbose.setObjectName(_fromUtf8("verbose"))
        self.advanced_options_label = QtGui.QLabel(self.centralwidget)
        self.advanced_options_label.setGeometry(QtCore.QRect(10, 470, 91, 16))
        self.advanced_options_label.setObjectName(_fromUtf8("advanced_options_label"))
        self.cpu_text = QtGui.QLineEdit(self.centralwidget)
        self.cpu_text.setGeometry(QtCore.QRect(170, 490, 51, 20))
        self.cpu_text.setText(_fromUtf8(""))
        self.cpu_text.setObjectName(_fromUtf8("cpu_text"))
        self.cpu_label = QtGui.QLabel(self.centralwidget)
        self.cpu_label.setGeometry(QtCore.QRect(10, 490, 161, 21))
        self.cpu_label.setObjectName(_fromUtf8("cpu_label"))
        self.start = QtGui.QPushButton(self.centralwidget)
        self.start.setGeometry(QtCore.QRect(520, 490, 75, 23))
        self.start.setObjectName(_fromUtf8("start"))
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        MainWindow.setWindowIcon(QtGui.QIcon('blanka.png'))

        self.arguments = {}
        self.set_default_args()

        self.retranslateUi(MainWindow)

        QtCore.QObject.connect(self.sample_file_browser, QtCore.SIGNAL('clicked()'), self.get_sample_path)
        QtCore.QObject.connect(self.control_file_browser, QtCore.SIGNAL('clicked()'), self.get_control_path)
        QtCore.QObject.connect(self.output_file_browser, QtCore.SIGNAL('clicked()'), self.get_output_path)
        QtCore.QObject.connect(self.start, QtCore.SIGNAL('clicked()'), self.run_blanka_gui)

    def get_sample_path(self):
        if self.num_samples.isChecked():
            self.sample_text.setText(str(QtGui.QFileDialog.getExistingDirectory(None, 'Select Directory',
                                                                                'C:\\')).replace('/', '\\'))
        else:
            self.sample_text.setText(str(QtGui.QFileDialog.getOpenFileName(None, 'Open File',
                                                                           'C:\\')).replace('/', '\\'))

    def get_control_path(self):
        if self.num_controls.isChecked():
            self.control_text.setText(str(QtGui.QFileDialog.getExistingDirectory(None, 'Select Directory',
                                                                                 'C:\\')).replace('/', '\\'))
        else:
            self.control_text.setText(str(QtGui.QFileDialog.getOpenFileName(None, 'Open File',
                                                                            'C:\\')).replace('/', '\\'))

    def get_output_path(self):
        self.output_text.setText(str(QtGui.QFileDialog.getExistingDirectory(None, 'Select Directory',
                                                                            'C:\\')).replace('/', '\\'))

    def set_default_args(self):
        self.arguments['output'] = ''
        self.arguments['ms1_threshold'] = 0.5
        self.arguments['ms2_threshold'] = 0.2
        self.arguments['signal_noise_ratio'] = 4
        self.arguments['retention_time_tolerance'] = 0.1
        self.arguments['precursor_mz_tolerance'] = 0.02
        self.arguments['peak_mz_tolerance'] = 0.02
        self.arguments['noise_removal_only'] = False
        self.arguments['blank_removal_only'] = False
        self.arguments['cpu'] = cpu_count() - 1
        self.arguments['verbose'] = False

    def get_args_gui(self):
        self.arguments['sample'] = str(self.sample_text.text())
        self.arguments['control'] = str(self.control_text.text())
        self.arguments['output'] = str(self.output_text.text())
        if self.instrument_choice.currentText() == 'LC-MS or LC-MS/MS (LCQ)':
            self.arguments['instrument'] = 'lcq'
        elif self.instrument_choice.currentText() == 'LC-MS or LC-MS/MS (qTOF)':
            self.arguments['instrument'] = 'qtof'
        elif self.instrument_choice.currentText() == 'MALDI Dried Droplet':
            self.arguments['instrument'] = 'dd'
        self.arguments['ms1_threshold'] = float(self.ms1_threshold_text.text())
        self.arguments['ms2_threshold'] = float(self.ms2_threshold_text.text())
        self.arguments['signal_noise_ratio'] = int(self.snr_text.text())
        self.arguments['retention_time_tolerance'] = float(self.rt_text.text())
        self.arguments['precursor_mz_tolerance'] = float(self.precursor_mz_text.text())
        self.arguments['peak_mz_tolerance'] = float(self.peak_mz_text.text())
        if self.noise_removal_only.isChecked():
            self.arguments['noise_removal_only'] = True
        else:
            self.arguments['noise_removal_only'] = False
        if self.blank_removal_only.isChecked():
            self.arguments['blank_removal_only'] = True
        else:
            self.arguments['blank_removal_only'] = False
        if self.cpu_text.text() != '':
            self.arguments['cpu'] = int(self.cpu_text.text())
        if self.verbose.isChecked():
            self.arguments['verbose'] = True
        else:
            self.arguments['verbose'] = False

    def args_check_gui(self):
        error_text = ''
        if not os.path.exists(self.arguments['sample']):
            error_text += '* Sample path does not exist.\n\n'
        if not os.path.exists(self.arguments['control']):
            error_text += '* Control path does not exist.\n\n'
        if self.arguments['ms1_threshold'] > 1:
            error_text += '* MS1 Threshold must be less than or equal to 1.\n\n'
        if self.arguments['ms2_threshold'] > 1:
            error_text += '* MS2 Threshold must be less than or equal to 1.\n\n'
        if self.arguments['cpu'] >= cpu_count():
            error_text += '* Number of threads specified exceeds number of available threads. Your computer has ' \
                          + str(cpu_count() - 1) + ' usable threads.\n\n'
        if self.arguments['noise_removal_only'] and self.arguments['blank_removal_only']:
            error_text += '* --noise_removal_only and --blank_removal_only both cannot be selected at once.\n\n'
        if error_text != '':
            error_text += 'Re-run after fixing parameters...'
            error_box = QtGui.QMessageBox()
            error_box.setText(error_text)
            error_box.setWindowTitle('Error')
            error_box.setWindowIcon(QtGui.QIcon('blanka.png'))
            error_box.exec_()
            return False
        return True

    def run_blanka_gui(self):
        self.get_args_gui()
        if not self.args_check_gui():
            return None
        # runs BLANKA by generating a command line command and creating a subprocess
        blanka_cmd = 'python ' + os.path.dirname(__file__) + '/run_blanka.py '
        for key, value in self.arguments.iteritems():
            if key == 'noise_removal_only' or key == 'blank_removal_only' or key == 'verbose':
                if value:
                    blanka_cmd += '--' + str(key) + ' ' + str(value) + ' '
            elif value != '':
                blanka_cmd += '--' + str(key) + ' ' + str(value) + ' '
        print blanka_cmd
        if platform.system() == 'Windows':
            if self.arguments['verbose']:
                subprocess.call(blanka_cmd, creationflags=CREATE_NEW_CONSOLE)
            else:
                subprocess.call(blanka_cmd)
        else:
            if self.arguments['verbose']:
                subprocess.call(blanka_cmd, creationflags=CREATE_NEW_CONSOLE, shell=True)
            else:
                subprocess.call(blanka_cmd, shell=True)

        # BLANKA has completed running popup
        finish_box = QtGui.QMessageBox()
        finish_box.setText('BLANKA successfully finished!')
        finish_box.setWindowTitle('BLANKA GUI')
        finish_box.setWindowIcon(QtGui.QIcon('blanka.png'))
        finish_box.exec_()

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "BLANKA GUI", None))
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.sample_label.setText(_translate("MainWindow", "Sample", None))
        self.sample_file_browser.setText(_translate("MainWindow", "...", None))
        self.num_samples.setText(_translate("MainWindow", "Multiple Sample Files", None))
        self.control_label.setText(_translate("MainWindow", "Control", None))
        self.control_file_browser.setText(_translate("MainWindow", "...", None))
        self.num_controls.setText(_translate("MainWindow", "Multiple Control Files", None))
        self.output_label.setText(_translate("MainWindow", "Output Directory (Optional)", None))
        self.output_file_browser.setText(_translate("MainWindow", "...", None))
        self.instrument_label.setText(_translate("MainWindow", "Experiment", None))
        self.instrument_choice.setItemText(0, _translate("MainWindow", "LC-MS or LC-MS/MS (LCQ)", None))
        self.instrument_choice.setItemText(1, _translate("MainWindow", "LC-MS or LC-MS/MS (qTOF)", None))
        self.instrument_choice.setItemText(2, _translate("MainWindow", "MALDI Dried Droplet", None))
        self.ms1_threshold_label.setText(_translate("MainWindow", "Blank Removal Relative Intensity Threshold (MS1):", None))
        self.ms2_threshold_label.setText(_translate("MainWindow", "Blank Removal Relative Intensity Threshold (MS2):", None))
        self.snr_label.setText(_translate("MainWindow", "Signal to Noise Ratio:", None))
        self.snr_unit.setText(_translate("MainWindow", ": 1", None))
        self.rt_label.setText(_translate("MainWindow", "Retention Time Tolerance: +/-", None))
        self.rt_unit.setText(_translate("MainWindow", "sec", None))
        self.precursor_mz_label.setText(_translate("MainWindow", "Precursor m/z Tolerance: +/-", None))
        self.precursor_mz_unit.setText(_translate("MainWindow", "Da", None))
        self.peak_mz_label.setText(_translate("MainWindow", "Peak m/z Tolerance: +/-", None))
        self.peak_mz_unit.setText(_translate("MainWindow", "Da", None))
        self.noise_removal_only.setText(_translate("MainWindow", "Noise Removal Only", None))
        self.blank_removal_only.setText(_translate("MainWindow", "Blank Removal Only", None))
        self.verbose.setText(_translate("MainWindow", "Verbose", None))
        self.advanced_options_label.setText(_translate("MainWindow", "Advanced Options", None))
        self.cpu_label.setText(_translate("MainWindow", "Number of CPU Threads to Use:", None))
        self.start.setText(_translate("MainWindow", "Run", None))


def main():
    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()