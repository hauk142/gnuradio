# Copyright 2014-2020 Free Software Foundation, Inc.
# This file is part of GNU Radio
#
# GNU Radio Companion is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# GNU Radio Companion is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA

from __future__ import absolute_import, print_function

# Standard modules
import logging

import xml.etree.ElementTree as ET

from ast import literal_eval

# Third-party modules
import six

from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import Qt

class GeneralTab(QtWidgets.QWidget):
    def __init__(self, parent, block, *args, **kwargs):
        super(QtWidgets.QWidget, self).__init__(*args, **kwargs)
        layout = QtWidgets.QGridLayout()

        i = 0
        for key, item in block.params.items():
            if item.hide not in ('all','part'):
                layout.addWidget(QtWidgets.QLabel(key), i, 0)
                if item.dtype == 'enum':
                    combobox = QtWidgets.QComboBox()
                    for key, val in item.options.items():
                        combobox.addItem(val)
                    layout.addWidget(combobox, i, 1)
                else:
                    layout.addWidget(QtWidgets.QLineEdit(item.value), i, 1)
                i += 1
        self.setLayout(layout)

class AdvancedTab(QtWidgets.QWidget):
    def __init__(self, block, *args, **kwargs):
        super(QtWidgets.QWidget, self).__init__(*args, **kwargs)
        layout = QtWidgets.QGridLayout()
        layout.addWidget(QtWidgets.QLabel("Comment"), 0, 0)
        layout.addWidget(QtWidgets.QTextEdit(), 0, 1)
        self.setLayout(layout)

class DocumentationTab(QtWidgets.QWidget):
    def __init__(self, block, *args, **kwargs):
        super(QtWidgets.QWidget, self).__init__(*args, **kwargs)
        layout = QtWidgets.QGridLayout()
        layout.addWidget(QtWidgets.QLabel("Documentation"), 0, 0)
        layout.addWidget(QtWidgets.QTextEdit(), 0, 1)
        self.setLayout(layout)

class ParamDialog(QtWidgets.QDialog):
    def __init__(self, block, *args, **kwargs):
        super(ParamDialog, self).__init__()
        self.resize(600, 500)
        self.tabs = QtWidgets.QTabWidget()
        
        top_layout = QtWidgets.QVBoxLayout()

        self.tabs.addTab(GeneralTab(self, block), "General")
        self.tabs.addTab(AdvancedTab(block), "Advanced")
        self.tabs.addTab(DocumentationTab(block), "Documentation")
        
        self.setWindowTitle("ja")
        self.setWindowModality(Qt.ApplicationModal)
        self.buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok
                             | QtWidgets.QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        top_layout.addWidget(self.tabs, 6)
        top_layout.addWidget(QtWidgets.QTextEdit(), 2)
        top_layout.addWidget(self.buttonBox)
        self.setLayout(top_layout)
        self.exec_()