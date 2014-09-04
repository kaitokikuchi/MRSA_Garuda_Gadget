#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
GUI for PPi calculation script
"""
from __future__ import print_function
import sys
import csv
import os
import glob
from PyQt4 import QtGui, QtCore
from rpy2.robjects import r
import garuda.garudaclientbackend as Garuda
from garuda.garudaclientbackend import GarudaClientBackend, Gadget

 #default working directory
directory = '/Users/kaito/Dropbox/Data_Mining/MRSA_PIN/MRSA-scripts/Data'


#Class for emmiting logs to screen
class EmittingStream(QtCore.QObject):

    textWritten = QtCore.pyqtSignal(str)

    def write(self, text):
        self.textWritten.emit(str(text))


#GUI
class GadgetFrame(QtGui.QMainWindow):

    def __init__(self, gadget_name, gadget_id):
        super(GadgetFrame, self).__init__()

        #Garuda related inits
        self.gadget_name = gadget_name
        self.gadget_id = gadget_id
        self.init_backend()

        #PyQt Inits
        self.initUI()
        self.create_widgets()

        #declare global lists and dicts
        self.pnamelist = []
        self.drugtotal = []
        self.essentialtotal = []
        self.modulename = []
        self.targetdict = {}
        self.essentialdict = {}

    def init_backend(self):
        try:
            self.backend = GarudaClientBackend(self.gadget_name,
                                               self.gadget_id)
            self.backend.add_lisenter(self.property_changed)
            self.backend.display_log = self.show_log
            self.backend.initialize()
            self.backend.register_gadget()
        except Exception, what:
            #- print what
            pass

    def OnNotificationTest(self, event):
        current_target_index = self.compatible_gadgets.GetSelection()
        if current_target_index >= 0:
            target_name = self.compatible_gadgets.GetString(current_target_index)
            target_id = self.compatible_gadgets.GetClientData(current_target_index)
        else:
            pass
        self.backend.send_notification_to_core(Gadget(self.gadget_name, self.gadget_id, None),
                                                   "602",
                                                   "None")
        pass

    def set_file_types(self, extension):
        self.file_type.Clear()
        if extension == "xml":
            items = ["xml", "celldesigner", "phml",
                     "cellml", "sbml", "sedml"]
            for item in items:
                self.file_type.Append(item)
            self.file_type.SetValue("xml")
        elif extension == "txt":
            items = ["kegg", "ensemble", "genelist"]
            for item in items:
                self.file_type.Append(item)
            self.file_type.SetValue("kegg")
        elif extension == "csv":
            items = ["csv", "kegg", "ensemble", "genelist"]
            for item in items:
                self.file_type.Append(item)
            self.file_type.SetValue("csv")
        elif extension == "phml":
            self.file_type.Append("phml")
            self.file_type.SetValue("phml")
        else:
            return

    def property_changed(self, message_id, error_code, param):
        """
        handle message_id event.
        """
        if message_id == Garuda.ID_ACTIVATE_GADGET_RESPONSE:
            if error_code == "200":
                #- print 'Activate Gadget: 200-success.'
                pass
            else:
                error_message = 'Activate Gadget Error: %s' % error_code
                #- print error_message
                self.MessageBox(error_message, 'Activate Error')
        elif message_id == Garuda.ID_REGISTER_GADGET_RESPONSE:
            if error_code == "200":
                #- print 'Register Gadget: 200-success'
                pass
            else:
                error_message = 'Register Gadget Error: %s' % error_code
                #- print error_message
                self.MessageBox(error_message, 'Register Error')
        elif message_id == Garuda.ID_GET_COMPATIBLE_GADGET_LIST_RESPONSE:
            if error_code == '200':
                self.compatible_gadgets.Clear()
                gadgets = self.backend.get_compatible_gadget_list()

                # Print Log
                #- print '*' * 50
                for gadget in gadgets:
                    #- print '\n        '.join(str(gadget).split("\n"))
                    pass
                #- print '*' * 50
                # End Print Log

                for gadget in gadgets:
                    self.compatible_gadgets.Append(gadget.gadget_name,
                                                   gadget.gadget_id)

            else:
                error_message = 'GetCompatibleGadgets Error: %s' % error_code
                #- print error_message
                self.MessageBox(error_message, 'GetCompatibleGadget Error')

        elif message_id == Garuda.ID_CONNECTION_NOT_INITIALIZED:
            if error_code:
                self.MessageBox("Connection not Initialized!", "Connection Error")
            else:
                pass

        elif message_id == Garuda.ID_CONNECTION_TERMINATED:
            self.MessageBox("Socket Connection Terminated!", "Terminated")
            if isinstance(param, dict):
                message = param.get("message", None)
                if message == 'RemoteHostClosedError':
                    self.Close()

        elif message_id == Garuda.ID_CONNECTION_NOT_INITIALIZED:
            self.MessageBox("connection not initalized!", "IID_CONNECTION_NOT_INITIALIZED")

        elif message_id == Garuda.ID_JSON_PARSE_ERROR:
            self.MessageBox("Json parse error!", "ID_JSON_PARSE_ERROR")

        elif message_id == Garuda.ID_JSON_DUMPS_ERROR:
            self.MessageBox("Json dumps error!", "ID_JSON_DUMPS_ERROR")

        elif message_id == Garuda.ID_SEND_DATA_GADGET_RESPONSE:
            if error_code == "200":
                pass
            else:
                error_message = 'Send data gadget Error: %s' % error
                self.MessageBox(error_message, 'SendDataGadget Error')
        elif message_id == Garuda.ID_LOAD_DATA_REQUEST:
            if not isinstance(param, dict):
                return
            gadget = param.get("gadget", None)
            file_path = param.get("data", "")
            file_name = os.path.basename(file_path)
            self.file_list.Append(file_name, file_path)
            try:
                _file = open(file_path, 'r')
                content = _file.read()
                self.file_content.SetValue(content)
                _file.close()
                self.file_info.SetSelection(1)
                # Modify Func..................
                self.backend.response_load_data(gadget.gadget_name, gadget.gadget_id, "200")
            except Exception, what:
                #- print what
                pass
        elif message_id == Garuda.ID_LOAD_GADGET_REQUEST:
            self.MessageBox("load gadget", "ID_LOAD_GADGET_REQUEST")

            # param is a gadget
            if isinstance(param, dict):
                gadget = param.get("gadget", None)
                path = param.get("path", None)

                if gadget and path:
                    self.backend.response_load_gadget(gadget.gadget_name, gadget.gadget_id, "200")
            else:
                #- print "get args error."
                pass
        elif message_id == Garuda.ID_SEND_NOTIFICATION_TO_GADGET_REQUEST:
            if error_code == "602":
                # self.Show()
                if isinstance(param, dict):
                    gadget = param.get("gadget", None)
                    if gadget:
                        self.backend.response_send_notification_to_gadget(gadget.gadget_name, gadget.gadget_id, "200")
                    pass
            elif error_code == "603":
                if isinstance(param, dict):
                    message = param.get("Message", "None")
                    gadget = param.get("gadget", None)
                    if gadget:
                        self.backend.response_send_notification_to_gadget(gadget.gadget_name, gadget.gadget_id, "200")
                    self.MessageBox("Send Notification to Gadget",
                                    "ErrorCode:%s\r\nMessage:%s" % (error_code, message))
                else:
                    self.MessageBox("Send Notification to Gadget",
                                    "ErrorCode:%s\r\nMessage:%s" % (error_code, "None"))
            elif error_code == "604":

                if isinstance(param, dict):
                    message = param.get("Message", "None")
                    gadget = param.get("gadget", None)
                    if gadget:
                        self.backend.response_send_notification_to_gadget(gadget.gadget_name, gadget.gadget_id, "200")
                    self.MessageBox("Send Notification to Gadget",
                                    "ErrorCode:%s\r\nMessage:%s" % (error_code, message))
            else:
                self.MessageBox("Send Notification to Gadget",
                                "ErrorCode:%s\r\nMessage:%s" % (error_code, "None"))

        elif message_id == Garuda.ID_SEND_NOTIFICATION_TO_CORE_RESPONSE:
            pass
        else:
            #- print "Error:UnKnow MessageID."
            pass

    def __del__(self):
    # Restore sys.stdout
        sys.stdout = sys.__stdout__

    def create_widgets(self):
        #Widgets
        self.ppi_label = QtGui.QLabel("PPi Matrix File:")
        self.ppi_edit = QtGui.QLineEdit()
        self.ppi_button = QtGui.QPushButton("Search")

        self.drug_label = QtGui.QLabel("Drug Target File:")
        self.drug_edit = QtGui.QLineEdit()
        self.drug_button = QtGui.QPushButton("Search")

        self.ess_label = QtGui.QLabel("Essential Protein File:")
        self.ess_edit = QtGui.QLineEdit()
        self.ess_button = QtGui.QPushButton("Search")

        self.module_data = QtGui.QTextEdit()
        self.module_button = QtGui.QPushButton("Analyze!")

        #grid layout
        grid = QtGui.QGridLayout()
        grid.setSpacing(5)

        grid.addWidget(self.ppi_label, 1, 1)
        grid.addWidget(self.ppi_edit, 1, 2)
        grid.addWidget(self.ppi_button, 1, 3)

        grid.addWidget(self.drug_label, 2, 1)
        grid.addWidget(self.drug_edit, 2, 2)
        grid.addWidget(self.drug_button, 2, 3)

        grid.addWidget(self.ess_label, 3, 1)
        grid.addWidget(self.ess_edit, 3, 2)
        grid.addWidget(self.ess_button, 3, 3)

        grid.addWidget(self.module_button, 4, 1)
        grid.addWidget(self.module_data, 4, 2, 2, 5)

        #Create central widget, add layout and set
        central_widget = QtGui.QWidget()
        central_widget.setLayout(grid)
        self.setCentralWidget(central_widget)

        #connect signal
        QtCore.QObject.connect(self.ppi_button, QtCore.SIGNAL("clicked()"), self.OpenPPiFile)
        QtCore.QObject.connect(self.drug_button, QtCore.SIGNAL("clicked()"), self.OpenDrugFile)
        QtCore.QObject.connect(self.ess_button, QtCore.SIGNAL("clicked()"), self.OpenEssFile)
        QtCore.QObject.connect(self.module_button, QtCore.SIGNAL("clicked()"), self.DataProcess)

    def initUI(self):
        self.setGeometry(300, 300, 500, 200)
        self.setWindowTitle('PPi Analyzer')
        self.show()

    #Define function to calculate hypergeometric scores
    def hypergeotest(self, a, b, c):
        nontarget = len(self.pnamelist) - b
        hypergeo = {}
        r.assign('totalwhite', b)
        r.assign('totalblack', nontarget)
        for x in self.modulename:
            r.assign('drawnwhite', a[x])
            r.assign('drawnballs', c[x])
            p = r('phyper(drawnwhite, totalwhite, totalblack, drawnballs, lower.tail = FALSE, log.p = FALSE)')
            hypergeo[x] = p[0]
        return hypergeo

    #Instance to read in PPi matrix
    def OpenPPiFile(self):
        self.module_data.append("Opening PPi File...")
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file', directory)
        baitref = []
        preyref = []
        self.ppi_edit.setText(fname)
        f = open(fname, 'r')
        self.module_data.append("Populating Protein List...")
        with f:
            reader = csv.reader(f, delimiter=',')
            next(reader, None)
            for row in reader:
                a = row[0]
                baitref.append(a)
                b = row[2]
                preyref.append(b)

        self.pnamelist.extend(x for x in baitref if x not in self.pnamelist)
        self.pnamelist.extend(x for x in preyref if x not in self.pnamelist)
        self.module_data.append("Please Open Drug Target List File")

    #Instance to read in Drug Targets
    def OpenDrugFile(self):
        self.module_data.append("Opening Drug Target List File...")
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file', directory)
        druglist = []
        self.drug_edit.setText(fname)
        f = open(fname, 'r')
        with f:
            reader = csv.reader(f, delimiter=',')
            for row in reader:
                reader1 = row[3]
                druglist.append(reader1)

        #Delete header entry
        druglist.pop(0)

        #Create a dictionary
        for x in self.pnamelist:
            if x in druglist:
                self.targetdict[x] = 1
            else:
                self.targetdict[x] = 0
        self.drugtotal = sum(x == 1 for x in self.targetdict.values())
        self.module_data.append("Please Open Essential Protein List File")

    #Instance to read in Essential Proteins
    def OpenEssFile(self):
        self.module_data.append("Opening Essential Protein List File...")
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file', directory)
        essential = []
        self.ess_edit.setText(fname)
        f = open(fname, 'r')
        with f:
            reader = csv.reader(f, delimiter=',')
            for row in reader:
                reader1 = row[0]
                essential.append(reader1)

        for x in self.pnamelist:
            if x in essential:
                self.essentialdict[x] = 1
            else:
                self.essentialdict[x] = 0

        self.essentialtotal = sum(x == 1 for x in self.essentialdict.values())
        #print(self.essentialtotal)
        self.module_data.append("Press Analyze!")

    def DataProcess(self):
        self.module_data.append("Starting PPi Analysis...")
        filelist = []
        for files in glob.iglob('/Users/kaito/Dropbox/Data_Mining/MRSA_PIN/ClusteredResults/*.txt'):
            filelist.append(files)

        for x in filelist:
            (path, longname) = os.path.split(x)
            (filename, extension) = os.path.splitext(longname)

            protein = []
            module = []
            with open(x, 'r') as f:
                reader = csv.reader(f, delimiter='\t')
                for row in reader:
                    reader1 = row[0]
                    protein.append(reader1)
                    reader2 = row[1]
                    module.append(reader2)
            moddict = {}
            for i in range(len(protein)):
                moddict[protein[i]] = module[i]
            with open('/Users/kaito/Desktop/Core_V_0.2/gadgets/220e77c0-316c-11e4-8c21-0800200c9a66/Results/%sdata.txt' % filename, 'w') as fff:
                writer = csv.writer(fff, delimiter='\t')
                writer.writerow(('Protein', 'Module',  'Drug Target?', 'Essential?'))
                for x in protein:
                    writer.writerow((x, moddict[x], self.targetdict[x], self.essentialdict[x]))

            moduletarget = {}
            for k, v in moddict.items():
                moduletarget[v] = 0.0

            for k, v in moddict.items():
                if self.targetdict[k] == 1:
                    moduletarget[v] = moduletarget[v] + 1.0

            moduleess = {}
            for k, v in moddict.items():
                moduleess[v] = 0.0

            for k, v in moddict.items():
                if self.essentialdict[k] == 1:
                    moduleess[v] = moduleess[v] + 1.0

            #print(moduleess)

            self.modulename = []
            self.modulename.extend(x for x in moddict.values() if x not in self.modulename)
            self.modulename.sort()
            #print(self.modulename)

            moduletotal = {}

            for x in self.modulename:
                moduletotal[x] = sum(y == x for y in moddict.values())
            #print(moduletotal)
            #Calculate hypergeometric test p value for drug targets and essential genes
            moddrughypergeo = self.hypergeotest(moduletarget, self.drugtotal, moduletotal)
            modesshypergeo = self.hypergeotest(moduleess, self.essentialtotal, moduletotal)

            with open('/Users/kaito/Desktop/Core_V_0.2/gadgets/220e77c0-316c-11e4-8c21-0800200c9a66/Results/%smodules.txt' % filename, 'w') as fff:
                writer = csv.writer(fff, delimiter='\t')
                writer.writerow(('Module', 'Membership', 'Drug Targets', 'Essential Genes', 'Drug Fraction', 'Essential Fraction', 'Hypergeometric Score of Module Target','Hypergeometric Score of Module Essential'))
                for x in self.modulename:
                    writer.writerow((x, moduletotal[x], moduletarget[x], moduleess[x], round(moduletarget[x]/self.drugtotal, 3), round(moduleess[x]/self.essentialtotal, 3), moddrughypergeo[x], modesshypergeo[x]))

        self.module_data.append("Completed Analysis! Stats are stored at gadgets/220e77c0-316c-11e4-8c21-0800200c9a66/Results")


def main():
    app = QtGui.QApplication(sys.argv)
    ex = GadgetFrame("PPiAnalyzer", "220e77c0-316c-11e4-8c21-0800200c9a66")
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
