# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'blanka_gui.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING! All changes made in this file will be lost!

from run_blanka3 import *
from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("BLANKA GUI")
        MainWindow.resize(620, 420)
        MainWindow.setMinimumSize(QtCore.QSize(620, 420))
        MainWindow.setMaximumSize(QtCore.QSize(620, 420))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.sample_label = QtWidgets.QLabel(self.centralwidget)
        self.sample_label.setGeometry(QtCore.QRect(10, 10, 81, 16))
        self.sample_label.setObjectName("sample_label")
        self.sample_text = QtWidgets.QLineEdit(self.centralwidget)
        self.sample_text.setGeometry(QtCore.QRect(10, 30, 411, 20))
        self.sample_text.setObjectName("sample_text")
        self.sample_file_browser = QtWidgets.QPushButton(self.centralwidget)
        self.sample_file_browser.setGeometry(QtCore.QRect(440, 30, 31, 23))
        self.sample_file_browser.setObjectName("sample_file_browser")
        self.num_samples = QtWidgets.QCheckBox(self.centralwidget)
        self.num_samples.setGeometry(QtCore.QRect(490, 30, 121, 21))
        self.num_samples.setObjectName("num_samples")
        self.blank_text = QtWidgets.QLineEdit(self.centralwidget)
        self.blank_text.setGeometry(QtCore.QRect(10, 90, 411, 20))
        self.blank_text.setObjectName("control_text")
        self.blank_label = QtWidgets.QLabel(self.centralwidget)
        self.blank_label.setGeometry(QtCore.QRect(10, 70, 81, 16))
        self.blank_label.setObjectName("control_label")
        self.blank_file_browser = QtWidgets.QPushButton(self.centralwidget)
        self.blank_file_browser.setGeometry(QtCore.QRect(440, 90, 31, 23))
        self.blank_file_browser.setObjectName("control_file_browser")
        self.num_blanks = QtWidgets.QCheckBox(self.centralwidget)
        self.num_blanks.setGeometry(QtCore.QRect(490, 90, 121, 21))
        self.num_blanks.setObjectName("num_controls")
        self.output_label = QtWidgets.QLabel(self.centralwidget)
        self.output_label.setGeometry(QtCore.QRect(10, 130, 141, 16))
        self.output_label.setObjectName("output_label")
        self.output_text = QtWidgets.QLineEdit(self.centralwidget)
        self.output_text.setGeometry(QtCore.QRect(10, 150, 411, 20))
        self.output_text.setObjectName("output_text")
        self.output_file_browser = QtWidgets.QPushButton(self.centralwidget)
        self.output_file_browser.setGeometry(QtCore.QRect(440, 150, 31, 23))
        self.output_file_browser.setObjectName("output_file_browser")
        self.experiment_label = QtWidgets.QLabel(self.centralwidget)
        self.experiment_label.setGeometry(QtCore.QRect(10, 190, 71, 21))
        self.experiment_label.setObjectName("instrument_label")
        self.experiment_choice = QtWidgets.QComboBox(self.centralwidget)
        self.experiment_choice.setGeometry(QtCore.QRect(90, 190, 161, 22))
        self.experiment_choice.setObjectName("instrument_choice")
        self.experiment_choice.addItem("")
        self.experiment_choice.addItem("")
        self.snr_label = QtWidgets.QLabel(self.centralwidget)
        self.snr_label.setGeometry(QtCore.QRect(10, 230, 111, 21))
        self.snr_label.setObjectName("snr_label")
        self.snr_text = QtWidgets.QLineEdit(self.centralwidget)
        self.snr_text.setGeometry(QtCore.QRect(120, 230, 51, 20))
        self.snr_text.setText("")
        self.snr_text.setObjectName("snr_text")
        self.snr_unit = QtWidgets.QLabel(self.centralwidget)
        self.snr_unit.setGeometry(QtCore.QRect(180, 230, 21, 21))
        self.snr_unit.setObjectName("snr_unit")
        self.rt_label = QtWidgets.QLabel(self.centralwidget)
        self.rt_label.setGeometry(QtCore.QRect(10, 270, 151, 21))
        self.rt_label.setObjectName("rt_label")
        self.rt_unit = QtWidgets.QLabel(self.centralwidget)
        self.rt_unit.setGeometry(QtCore.QRect(230, 270, 21, 21))
        self.rt_unit.setObjectName("rt_unit")
        self.rt_text = QtWidgets.QLineEdit(self.centralwidget)
        self.rt_text.setGeometry(QtCore.QRect(170, 270, 51, 20))
        self.rt_text.setText("")
        self.rt_text.setObjectName("rt_text")
        self.mz_label = QtWidgets.QLabel(self.centralwidget)
        self.mz_label.setGeometry(QtCore.QRect(10, 310, 151, 21))
        self.mz_label.setObjectName("precursor_mz_label")
        self.mz_text = QtWidgets.QLineEdit(self.centralwidget)
        self.mz_text.setGeometry(QtCore.QRect(110, 310, 51, 20))
        self.mz_text.setText("")
        self.mz_text.setObjectName("precursor_mz_text")
        self.mz_unit = QtWidgets.QLabel(self.centralwidget)
        self.mz_unit.setGeometry(QtCore.QRect(175, 310, 21, 21))
        self.mz_unit.setObjectName("precursor_mz_unit")
        self.verbose = QtWidgets.QCheckBox(self.centralwidget)
        self.verbose.setGeometry(QtCore.QRect(370, 310, 121, 21))
        self.verbose.setObjectName("verbose")
        self.advanced_options_label = QtWidgets.QLabel(self.centralwidget)
        self.advanced_options_label.setGeometry(QtCore.QRect(10, 350, 91, 16))
        self.advanced_options_label.setObjectName("advanced_options_label")
        self.cpu_text = QtWidgets.QLineEdit(self.centralwidget)
        self.cpu_text.setGeometry(QtCore.QRect(170, 370, 51, 20))
        self.cpu_text.setText("")
        self.cpu_text.setObjectName("cpu_text")
        self.cpu_label = QtWidgets.QLabel(self.centralwidget)
        self.cpu_label.setGeometry(QtCore.QRect(10, 370, 161, 21))
        self.cpu_label.setObjectName("cpu_label")
        self.start = QtWidgets.QPushButton(self.centralwidget)
        self.start.setGeometry(QtCore.QRect(520, 370, 75, 23))
        self.start.setObjectName("start")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        MainWindow.setWindowIcon(QtGui.QIcon('media/blanka.png'))

        self.arguments = {}
        self.set_default_args()

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # Connect buttons to functions
        self.sample_file_browser.clicked.connect(self.get_sample_path)
        self.blank_file_browser.clicked.connect(self.get_blank_path)
        self.output_file_browser.clicked.connect(self.get_output_path)
        self.start.clicked.connect(self.run_blanka_gui)

    def get_sample_path(self):
        if self.num_samples.isChecked():
            sample_directory = QtWidgets.QFileDialog.getExistingDirectory(None, 'Select Directory', 'C:\\')
            sample_directory = str(sample_directory).replace('/', '\\')
            self.sample_text.setText(sample_directory)
        else:
            sample_filepath = QtWidgets.QFileDialog.getOpenFileName(None, 'Open File', 'C:\\')
            sample_filepath = str(sample_filepath).replace('/', '\\')
            self.sample_text.setText(sample_filepath)

    def get_blank_path(self):
        if self.num_blanks.isChecked():
            blank_directory = QtWidgets.QFileDialog.getExistingDirectory(None, 'Select Directory', 'C:\\')
            blank_directory = str(blank_directory).replace('/', '\\')
            self.blank_text.setText(blank_directory)
        else:
            blank_filepath = QtWidgets.QFileDialog.getOpenFileName(None, 'Open File', 'C:\\')
            blank_filepath = str(blank_filepath).replace('/', '\\')
            self.blank_text.setText(blank_filepath)

    def get_output_path(self):
        output_directory = QtWidgets.QFileDialog.getExistingDirectory(None, 'Select Directory', 'C:\\')
        output_directory = str(output_directory).replace('/', '\\')
        self.output_text.setText(output_directory)

    def set_default_args(self):
        self.arguments['output'] = ''
        self.arguments['snr'] = 4
        self.arguments['rt_tol'] = 6
        self.arguments['precursor_mz_tol'] = 0.2
        self.arguments['cpu'] = cpu_count() - 1
        self.arguments['verbose'] = False

    def get_args_gui(self):
        self.arguments['sample'] = str(self.sample_text.text())
        self.arguments['blank'] = str(self.blank_text.text())
        self.arguments['output'] = str(self.output_text.text())
        if self.experiment_choice.currentText() == 'LC-MS/MS':
            self.arguments['experiment'] = 'lcms'
        elif self.experiment_choice.currentText() == 'MALDI Dried Droplet':
            self.arguments['experiment'] = 'dd'
        self.arguments['snr'] = int(self.snr_text.text())
        self.arguments['rt_tol'] = float(self.rt_text.text())
        self.arguments['precursor_mz_tol'] = float(self.mz_text.text())
        self.arguments['fragment_mz_tol'] = float(self.mz_text.text())
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
        if not os.path.exists(self.arguments['blank']):
            error_text += '* Sample path does not exist.\n\n'
        if self.arguments['cpu'] >= cpu_count():
            error_text += '* Number of threads specified exceeds number of available threads. Your computer has ' +\
                str(cpu_count() - 1) + ' usable threads.\n\n'
        if error_text != '':
            error_text += 'Re-run after fixing parameters...'
            error_box = QtWidgets.QMessageBox()
            error_box.setText(error_text)
            error_box.setWindowTitle('Error')
            error_box.setWindowIcon(QtGui.QIcon('media/blanka.png'))
            error_box.exec()
            return False
        return True

    # BLANKA has completed running popup
    def finished_dialogue_box(self):
        finish_box = QtWidgets.QMessageBox()
        finish_box.setText('BLANKA successfully finished!')
        finish_box.setWindowtitle('BLANKA GUI')
        finish_box.setWindowIcon(QtGui.QIcon('media/blanka.png'))
        finish_box.exec_()

    def run_blanka_gui(self):
        self.get_args_gui()
        if not self.args_check_gui():
            return None
        # Runs BLANKA by generating a command line command and creating a subprocess
        if getattr(sys, 'frozen', False):
            blanka_cmd = 'python ' + os.path.dirname(sys.executable) + '\\run_blanka3.py '
        elif __file__:
            blanka_cmd = 'python ' + os.path.dirname(__file__) + '\\run_blanka3.py'
        for key, value in self.arguments.iteritems():
            if key == 'verbose':
                if value:
                    blanka_cmd += '--' + str(key) + ' ' + str(value) + ' '
        print(blanka_cmd)
        if platform.system() == 'Windows':
            if self.arguments['verbose']:
                subprocess.call(blanka_cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                subprocess.call(blanka_cmd)
        else:
            if self.arguments['verbose']:
                subprocess.call(blanka_cmd, creationflags=subprocess.CREATE_NEW_CONSOLE, shell=True)
            else:
                subprocess.call(blanka_cmd, shell=True)
        self.finished_dialogue_box()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "BLANKA GUI"))
        self.sample_label.setText(_translate("MainWindow", "Sample"))
        self.sample_file_browser.setText(_translate("MainWindow", "..."))
        self.num_samples.setText(_translate("MainWindow", "Multiple Sample Files"))
        self.blank_label.setText(_translate("MainWindow", "Blank"))
        self.blank_file_browser.setText(_translate("MainWindow", "..."))
        self.num_blanks.setText(_translate("MainWindow", "Multiple Blank Files"))
        self.output_label.setText(_translate("MainWindow", "Output Directory (Optional)"))
        self.output_file_browser.setText(_translate("MainWindow", "..."))
        self.experiment_label.setText(_translate("MainWindow", "Experiment"))
        self.experiment_choice.setItemText(0, _translate("MainWindow", "LC-MS/MS"))
        self.experiment_choice.setItemText(1, _translate("MainWindow", "MALDI Dried Droplet"))
        self.snr_label.setText(_translate("MainWindow", "Signal to Noise Ratio:"))
        self.snr_unit.setText(_translate("MainWindow", ": 1"))
        self.rt_label.setText(_translate("MainWindow", "Retention Time Tolerance: +/-"))
        self.rt_unit.setText(_translate("MainWindow", "sec"))
        self.mz_label.setText(_translate("MainWindow", "m/z Tolerance: +/-"))
        self.mz_unit.setText(_translate("MainWindow", "Da"))
        self.verbose.setText(_translate("MainWindow", "Verbose"))
        self.advanced_options_label.setText(_translate("MainWindow", "Advanced Options"))
        self.cpu_label.setText(_translate("MainWindow", "Number of CPU Threads to Use:"))
        self.start.setText(_translate("MainWindow", "Run"))


def main():
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    main()
