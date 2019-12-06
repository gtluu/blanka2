from subprocess import call, CREATE_NEW_CONSOLE, PIPE, STDOUT, Popen
from PyQt4 import QtGui, QtCore
import datetime
from run_blanka import *

class BlankaGUI(QtGui.QWidget):
    def __init__(self, parent=None):
        super(BlankaGUI, self).__init__(parent)
        self.arguments = {}
        self.sample_label = QtGui.QLabel('Sample', self)
        self.num_samples = QtGui.QCheckBox('Multiple Sample Files', self)
        self.sample_text = QtGui.QLineEdit(self)
        self.sample_file_browser = QtGui.QPushButton('...', self)
        self.control_label = QtGui.QLabel('Control', self)
        self.num_controls = QtGui.QCheckBox('Multiple Control Files', self)
        self.control_text = QtGui.QLineEdit(self)
        self.control_file_browser = QtGui.QPushButton('...', self)
        self.output_label = QtGui.QLabel('Output Directory (Optional)', self)
        self.output_text = QtGui.QLineEdit(self)
        self.output_file_browser = QtGui.QPushButton('...', self)
        self.instrument_label = QtGui.QLabel('Experiment', self)
        self.instrument_choice = QtGui.QComboBox(self)
        self.threshold_label = QtGui.QLabel('Blank Removal Relative Intensity Threshold (MS1): ', self)
        self.threshold_text = QtGui.QLineEdit(self)
        self.threshold_label2 = QtGui.QLabel('Blank Removal Relative Intensity Threshold (MS2): ', self)
        self.threshold_text2 = QtGui.QLineEdit(self)
        self.snr_label = QtGui.QLabel('Signal to Noise Ratio: ', self)
        self.snr_text = QtGui.QLineEdit(self)
        self.snr_unit = QtGui.QLabel(': 1', self)
        self.rt_label = QtGui.QLabel('Retention Time Tolerance: ', self)
        self.rt_text = QtGui.QLineEdit(self)
        self.rt_unit = QtGui.QLabel('sec', self)
        self.precursor_mz_label = QtGui.QLabel('Precursor m/z Tolerance: ', self)
        self.precursor_mz_text = QtGui.QLineEdit(self)
        self.precursor_mz_unit = QtGui.QLabel('Da', self)
        self.peak_mz_label = QtGui.QLabel('Peak m/z Tolerance: ', self)
        self.peak_mz_text = QtGui.QLineEdit(self)
        self.peak_mz_unit = QtGui.QLabel('Da', self)
        self.plus_minus = QtGui.QLabel('+/-', self)
        self.plus_minus2 = QtGui.QLabel('+/-', self)
        self.plus_minus3 = QtGui.QLabel('+/-', self)
        self.noise_removal_only = QtGui.QCheckBox('Noise Removal Only', self)
        self.blank_removal_only = QtGui.QCheckBox('Blank Removal Only', self)
        self.advanced = QtGui.QLabel('Advanced Options', self)
        self.cpu_label = QtGui.QLabel('Number of CPU Threads to Use: ', self)
        self.cpu_text = QtGui.QLineEdit(self)
        self.start = QtGui.QPushButton('Run', self)
        self.verbose = QtGui.QCheckBox('Verbose', self)
        self.init_gui()

    def init_gui(self):
        self.set_default_args()

        self.instrument_choice.addItem('LC-MS or LC-MS/MS (LCQ)', self)
        self.instrument_choice.addItem('LC-MS or LC-MS/MS (qTOF)', self)
        self.instrument_choice.addItem('MALDI Dried Droplet', self)

        self.threshold_text.setText(str(self.arguments['ms1_threshold']))
        self.threshold_text2.setText(str(self.arguments['ms2_threshold']))
        self.snr_text.setText(str(self.arguments['signal_noise_ratio']))
        self.rt_text.setText(str(self.arguments['retention_time_tolerance']))
        self.precursor_mz_text.setText(str(self.arguments['precursor_mz_tolerance']))
        self.peak_mz_text.setText(str(self.arguments['peak_mz_tolerance']))
        self.cpu_text.setText(str(self.arguments['cpu']))

        self.set_layout()
        self.setGeometry(200, 100, 625, 475)
        self.setWindowTitle('BLANKA GUI')
        self.setWindowIcon(QtGui.QIcon('blanka.png'))
        self.show()

        QtCore.QObject.connect(self.sample_file_browser, QtCore.SIGNAL('clicked()'), self.get_sample_path)
        QtCore.QObject.connect(self.control_file_browser, QtCore.SIGNAL('clicked()'), self.get_control_path)
        QtCore.QObject.connect(self.output_file_browser, QtCore.SIGNAL('clicked()'), self.get_output_path)
        QtCore.QObject.connect(self.start, QtCore.SIGNAL('clicked()'), self.run_blanka_gui)

    def set_layout(self):
        # fix positioning now that maldi dd template removed
        self.sample_label.move(20, 20)
        self.num_samples.move(490, 40)
        self.sample_text.move(20, 40)
        self.sample_text.setFixedWidth(400)
        self.sample_file_browser.move(440, 38)
        self.sample_file_browser.setFixedWidth(30)
        self.control_label.move(20, 70)
        self.num_controls.move(490, 90)
        self.control_text.move(20, 90)
        self.control_text.setFixedWidth(400)
        self.control_file_browser.move(440, 88)
        self.control_file_browser.setFixedWidth(30)
        self.output_label.move(20, 120)
        self.output_text.move(20, 140)
        self.output_text.setFixedWidth(400)
        self.output_file_browser.move(440, 138)
        self.output_file_browser.setFixedWidth(30)
        self.instrument_label.move(20, 180)
        self.instrument_choice.move(100, 178)
        self.threshold_label.move(20, 220)
        self.threshold_text.move(270, 218)
        self.threshold_label2.move(20, 250)
        self.threshold_text2.move(270, 248)
        self.snr_label.move(20, 280)
        self.snr_text.move(130, 278)
        self.snr_text.setFixedWidth(30)
        self.snr_unit.move(165, 280)
        self.rt_label.move(20, 310)
        self.plus_minus.move(150, 310)
        self.rt_text.move(173, 308)
        self.rt_text.setFixedWidth(50)
        self.rt_unit.move(232, 310)
        self.precursor_mz_label.move(20, 340)
        self.plus_minus2.move(145, 340)
        self.precursor_mz_text.move(168, 338)
        self.precursor_mz_text.setFixedWidth(50)
        self.precursor_mz_unit.move(227, 340)
        self.peak_mz_label.move(20, 370)
        self.plus_minus3.move(122, 370)
        self.peak_mz_text.move(145, 368)
        self.peak_mz_text.setFixedWidth(50)
        self.peak_mz_unit.move(204, 370)
        self.noise_removal_only.move(300, 280)
        self.blank_removal_only.move(300, 310)
        self.verbose.move(300, 340)
        self.advanced.move(20, 410)
        self.cpu_label.move(20, 430)
        self.cpu_text.move(180, 428)
        self.cpu_text.setFixedWidth(30)
        self.start.move(500, 430)

    def get_sample_path(self):
        if self.num_samples.isChecked():
            self.sample_text.setText(str(QtGui.QFileDialog.getExistingDirectory(self, 'Select Directory',
                                                                                'C:\\')).replace('/', '\\'))
        else:
            self.sample_text.setText(str(QtGui.QFileDialog.getOpenFileName(self, 'Open File',
                                                                           'C:\\')).replace('/', '\\'))

    def get_control_path(self):
        if self.num_controls.isChecked():
            self.control_text.setText(str(QtGui.QFileDialog.getExistingDirectory(self, 'Select Directory',
                                                                                 'C:\\')).replace('/', '\\'))
        else:
            self.control_text.setText(str(QtGui.QFileDialog.getOpenFileName(self, 'Open File',
                                                                            'C:\\')).replace('/', '\\'))

    def get_output_path(self):
        self.output_text.setText(str(QtGui.QFileDialog.getExistingDirectory(self, 'Select Directory',
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
        self.arguments['ms1_threshold'] = float(self.threshold_text.text())
        self.arguments['ms2_threshold'] = float(self.threshold_text2.text())
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
            error_text += '* File is not Excel file. Please load appropriate spreadsheet.\n\n'
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

    def log(self, blanka_shell):
        month_dict = {'1': 'JAN', '2': 'FEB', '3': 'MAR', '4': 'APR', '5': 'MAY', '6': 'JUN',
                      '7': 'JUL', '8': 'AUG', '9': 'SEP', '10': 'OCT', '11': 'NOV', '12': 'DEC'}
        today = datetime.datetime.today()
        with open(self.arguments['output'] + '\\blanka_log_' + str(today.year) + \
                  month_dict[str(today.month)] + str(today.day) + '_' + str(today.hour) + str(today.minute) + \
                  str(today.second) + '.txt', 'w') as logfile:
            output = ''
            while True:
                terminal = blanka_shell.stdout.readline()
                output += terminal
                if terminal == '' and blanka_shell.poll() is not None:
                    break
                if terminal:
                    if self.arguments['verbose'] == True:
                        log_box.setText(output)
                    # instead of print, create verbose window here
            logfile.write(output)

    def run_blanka_gui(self):
        self.get_args_gui()
        if not self.args_check_gui():
            return None
        # runs BLANKA by generating a command line command and creating a subprocess
        blanka_cmd = 'python ' + os.path.dirname(__file__) + '/run_blanka_v3.py '
        for key, value in self.arguments.iteritems():
            if key == 'noise_removal_only' or key == 'blank_removal_only':
                if value:
                    blanka_cmd += '--' + str(key) + ' ' + str(value) + ' '
            elif value != '':
                blanka_cmd += '--' + str(key) + ' ' + str(value) + ' '
        if self.arguments['verbose'] == True:
            if self.arguments['output'] == '':
                self.arguments['output'] = os.path.split(self.arguments['sample'])[0]
            month_dict = {'1': 'JAN', '2': 'FEB', '3': 'MAR', '4': 'APR', '5': 'MAY', '6': 'JUN',
                          '7': 'JUL', '8': 'AUG', '9': 'SEP', '10': 'OCT', '11': 'NOV', '12': 'DEC'}
            today = datetime.datetime.today()
            blanka_cmd += '|& tee ' + self.arguments['output'] + '\\blanka_log_' + str(today.year) + \
                          month_dict[str(today.month)] + str(today.day) + '_' + str(today.hour) + str(today.minute) + \
                          str(today.second) + '.txt'
            blanka_cmd = 'powershell.exe -command "' + blanka_cmd + '"'
            blanka_cmd = blanka_cmd.replace('\b', '\\b')
        print blanka_cmd
        if platform.system() == 'Windows':
            subprocess.call(blanka_cmd, creationflags=CREATE_NEW_CONSOLE)
        else:
            subprocess.call(blanka_cmd, creationflags=CREATE_NEW_CONSOLE, shell=True)

        # BLANKA has completed running popup
        finish_box = QtGui.QMessageBox()
        finish_box.setText('BLANKA successfully finished!')
        finish_box.setWindowTitle('BLANKA GUI')
        finish_box.setWindowIcon(QtGui.QIcon('blanka.png'))
        finish_box.exec_()

def main():
    app = QtGui.QApplication(sys.argv)
    blanka_gui = BlankaGUI()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
