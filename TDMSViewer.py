# -*- coding: utf-8 -*-
"""
Created on Tue Aug 31 10:50:53 2021

@author: HCI7RT
"""
from PyQt5.QtWidgets import (QMainWindow, QTableView, QApplication, QAction,
                             QHeaderView, QListWidget, QFileDialog, QMenu,
                             QFrame, QHBoxLayout, QVBoxLayout, QAbstractItemView,
                             QListWidgetItem)
from PyQt5 import QtCore, QtGui

import sys, os
import nptdms
import pandas as pd

#os.chdir(r"\\bosch.com\dfsrb\DfsDE\LOC\Rt\BST\40_bst_lab\06_products\\")
class pandasModel(QtCore.QAbstractTableModel):
    def __init__(self, data, parent=None):
        QtCore.QAbstractItemModel.__init__(self, parent)
        self._data = data

        self.colors = dict()

    def rowCount(self, parent=None):
        return self._data.index.size

    def columnCount(self, parent=None):
        return self._data.columns.size

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])
            if role == QtCore.Qt.EditRole:
                return str(self._data.iloc[index.row(), index.column()])
            if role == QtCore.Qt.BackgroundRole:
                color = self.colors.get((index.row(), index.column()))
                if color is not None:
                    return color
        return None

    def headerData(self, rowcol, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self._data.columns[rowcol]
        if orientation == QtCore.Qt.Vertical and role == QtCore.Qt.DisplayRole:
            return self._data.index[rowcol]
        return None

    def flags(self, index):
        flags = super(self.__class__, self).flags(index)
        flags |= QtCore.Qt.ItemIsEditable
        flags |= QtCore.Qt.ItemIsSelectable
        flags |= QtCore.Qt.ItemIsEnabled
        flags |= QtCore.Qt.ItemIsDragEnabled
        flags |= QtCore.Qt.ItemIsDropEnabled
        return flags

    def sort(self, Ncol, order):
        """Sort table by given column number.
        """
        try:
            self.layoutAboutToBeChanged.emit()
            self._data = self._data.sort_values(
                self._data.columns[Ncol], ascending=not order
            )
            self.layoutChanged.emit()
        except Exception as e:
            print(e)

    def change_color(self, row, column, color):
        ix = self.index(row, column)
        self.colors[(row, column)] = color
        self.dataChanged.emit(ix, ix, (QtCore.Qt.BackgroundRole,))

class TDMSViewer(QMainWindow):
    def __init__(self, parent = None):
        super(TDMSViewer, self).__init__(parent)
        self.setWindowTitle('TDMS-Viewer')
        self.Main()
        self.Menu()
        self.TriggerList = []
        self.Search_in_TDMS_cols = ['Index_Messgroesse', 'Index_Messblock',
       'MessblockSchritt', 'MesspunktSchritt', 'Samples', 
       'Status', 'Info', 'Warn', 'Drehrate',
       'DrehrateIst', 'Einbaulage', 'MGFLoop', 'Position', 'PositionIst',
       'Spannung', 'SpannungIst', 'Temperatur', 'TemperaturIst']
        self.Integer_Cols = ['MessblockSchritt', 'MesspunktSchritt', 'Samples', 
       'Status', 'Info', 'Warn', 'Drehrate',
       'DrehrateIst', 'Einbaulage', 'MGFLoop', 'Position', 'PositionIst',
       'Spannung', 'SpannungIst', 'Temperatur', 'TemperaturIst']
        self.Search = {}
        for col in self.Search_in_TDMS_cols:
            self.Search[col] = []

    def MainBackground(self, image):
        '''
        

        Parameters
        ----------
        window : TYPE
            DESCRIPTION.
        image : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        '''
        try:
            Map = QtGui.QImage(image)
            Map = Map.scaled(QtCore.QSize(self.width(), self.height()), QtCore.Qt.IgnoreAspectRatio)
            palette = QtGui.QPalette()
            palette.setBrush(QtGui.QPalette.Window, QtGui.QBrush(Map))
            self.setPalette(palette)     
        except:
            None
            
    def Menu(self):
        MenuBar = self.menuBar()
        Action = QAction('&Open', self)
        Action.triggered.connect(self.OpenDataSet)  
        MenuBar.addAction(Action)
        Action = QAction('&Add', self)
        Action.triggered.connect(self.AddDataSet)  
        MenuBar.addAction(Action)
        self.setStyleSheet("""
        QMenuBar {
            background-color: rgb(200,200,200);
            color: rgb(0,0,0);
            }	""")
        
    def NewContextMenu(self):
        if self.sender().selectionModel().selectedColumns():
            Col = self.sender().selectionModel().selectedColumns()[0].column()
            Name = self.actualData.columns[Col]
    
            if Name in self.Search_in_TDMS_cols:
                Menu = QMenu()
                SubA = Menu.addMenu('All')
                SubV = Menu.addMenu('Visible')
                if Name not in self.Integer_Cols:
                    Actual = self.Data[Name].unique().tolist()
                    VisibleActual = self.actualData[Name].unique().tolist()
                    First = [i[0].upper() for i in Actual]
                    VisibleFirst = [i[0].upper() for i in VisibleActual]                
                    SubMenus = [i for i in set(First)]
                    SubMenus.sort()
                    VisibleSubMenus = [i for i in set(VisibleFirst)]
                    VisibleSubMenus.sort()
                    for i in SubMenus:
                        NewSub = SubA.addMenu(i)
                        k = [Idx for Idx in range(len(First)) if First[Idx] == i]
                        for Idx in k:
                            Action = QAction(str(Actual[Idx]), NewSub)
                            Action.triggered.connect(self.ActionTrigger)
                            setattr(Action, 'column', Name)
                            NewSub.addAction(Action)
                            Action.setCheckable(True)
                            if self.Search[Name]:
                                if Actual[Idx] in self.Search[Name]:
                                    Action.setChecked(True)
                    for i in VisibleSubMenus:
                        NewSub = SubV.addMenu(i)
                        k = [Idx for Idx in range(len(VisibleFirst)) if VisibleFirst[Idx] == i]
                        for Idx in k:
                            Action = QAction(str(VisibleActual[Idx]), NewSub)
                            Action.triggered.connect(self.ActionTrigger)
                            setattr(Action, 'column', Name)
                            NewSub.addAction(Action)
                            Action.setCheckable(True)
                            if self.Search[Name]:
                                if VisibleActual[Idx] in self.Search[Name]:
                                    Action.setChecked(True)
                                    
                else:
                    Actual = self.Data[Name].unique().tolist()
                    VisibleActual = self.actualData[Name].unique().tolist()
                    SubMenus = [i for i in set(Actual)]
                    SubMenus.sort()
                    VisibleSubMenus = [i for i in set(VisibleActual)]
                    VisibleSubMenus.sort()
                    for i in SubMenus:
                        k = [Idx for Idx in range(len(Actual)) if Actual[Idx] == i]
                        for Idx in k:
                            Action = QAction(str(Actual[Idx]), SubA)
                            Action.triggered.connect(self.ActionTrigger)
                            setattr(Action, 'column', Name)
                            SubA.addAction(Action)
                            Action.setCheckable(True)
                            if self.Search[Name]:
                                if Actual[Idx] in self.Search[Name]:
                                    Action.setChecked(True)
    
                    for i in VisibleSubMenus:
                        k = [Idx for Idx in range(len(VisibleActual)) if VisibleActual[Idx] == i]
                        for Idx in k:
                            Action = QAction(str(VisibleActual[Idx]), SubV)
                            Action.triggered.connect(self.ActionTrigger)
                            setattr(Action, 'column', Name)
                            SubV.addAction(Action)
                            Action.setCheckable(True)
                            if self.Search[Name]:
                                if VisibleActual[Idx] in self.Search[Name]:
                                    Action.setChecked(True)
                    
                Menu.exec_(QtGui.QCursor.pos())
        
    def ContextMenu(self):
        '''
        Define context menu for QTableView.
        The menu can be opened by clicking the right mouse button on a table row
        to give the option to edit or delete this data row.

        '''
        Menu = QMenu()
        Col = self.sender().selectionModel().selectedColumns()[0].column()
        Name = self.actualData.columns[Col]
        SubN = Menu.addMenu('Not Visible')
        SubM = Menu.addMenu('Selection')
        SubO = Menu.addMenu('others')
        SubL = {}
        SubNL = {}
        SubNO = SubN.addMenu('others')

        if Name in self.Search_in_TDMS_cols:
            Actual = self.actualData[Name].unique().tolist()
            ActuaZ = [i[0] for i in Actual if isinstance(i,str)]
            ActuaL = pd.unique(ActuaZ).tolist()
            Entrys = self.Data[Name].unique().tolist()
            EntryZ = [i[0] for i in Entrys if isinstance(i,str)]
            EntryL = pd.unique(EntryZ).tolist()
            ABC = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
            for Letter in ABC:
                if Letter in EntryL:
                    SubL[Letter] = Menu.addMenu(Letter)
            for Letter in ABC:
                if Letter in ActuaL:
                    SubNL[Letter] = SubN.addMenu(Letter)
            for k in Entrys:
                if k in Actual:
                    if k in self.Search[Name]:
                        Action = QAction(str(k), SubM)
                        SubM.addAction(Action)
                    else:
                        if not isinstance(k, int):
                            for Letter in EntryL:
                                if k[0].upper() == Letter:
                                    Action = QAction(str(k), SubL[Letter])
                                    Action.triggered.connect(self.ActionTrigger)
                                    SubL[Letter].addAction(Action)
                        else:
                            Action = QAction(str(k), SubO)
                            SubO.addAction(Action)
                                
                            
                    setattr(Action, 'column', Name)
                    Action.setCheckable(True)
                    Action.triggered.connect(self.ActionTrigger)
                    if self.Search[Name]:
                        if k in self.Search[Name]:
                            Action.setChecked(True)
                else:
                    if not isinstance(k, int):
                        for Letter in EntryL:
                            if k[0].upper() == Letter:
                                try:
                                    Action = QAction(str(k), SubNL[Letter])
                                    SubNL[Letter].addAction(Action)
                                    setattr(Action, 'column', Name)
                                    Action.setCheckable(True)
                                    Action.triggered.connect(self.ActionTrigger)
                                    if self.Search[Name]:
                                        if k in self.Search[Name]:
                                            Action.setChecked(True)
                                except:
                                    print(Letter + 'not in dict')
                    else:
                        Action = QAction(str(k), SubNO)
                        SubNO.addAction(Action)
                        setattr(Action, 'column', Name)
                        Action.setCheckable(True)
                        Action.triggered.connect(self.ActionTrigger)
                        if self.Search[Name]:
                            if k in self.Search[Name]:
                                Action.setChecked(True)          
        Menu.exec_(QtGui.QCursor.pos())
        
    def ActionTrigger(self):
        Value = self.sender().text()
        try:
            Value = int(Value)
        except:
            None
        Column = getattr(self.sender(), 'column')
        if self.Search[Column]:
            New = self.Search[Column]
        else:
            New = []
        if self.sender().isChecked():
            New.append(Value)
        else:
            New.remove(Value)
            if not New:
                New = []
        self.Search[Column] = New
        self.actualData = self.Data
        self.Filter()
            
    def GetAllTrueIndex(self):
        Idx = []
        for i in self.TriggerList:
            for k in self.actualData.columns:
                Idx.append(self.actualData[self.actualData[k].astype(str) == i].index.values.astype(int))

    def Main(self):
        Main = QFrame()
        Lay = QHBoxLayout()
        View = QListWidget()
        View.setFixedWidth(300)
        View.itemClicked.connect(self.Open)
        Lay.addWidget(View)
        Frame = QFrame()
        Lay1 = QVBoxLayout()
        View = QTableView()
        View.setToolTip('Header')
        View.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        View.horizontalHeader().hide()
        View.setFixedHeight(275)
        Lay1.addWidget(View)
        View = QTableView()
        View.setToolTip('Measurement Data')
        View.setSelectionBehavior(QAbstractItemView.SelectColumns)
        View.setSelectionMode(QAbstractItemView.SingleSelection)
        View.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        View.verticalHeader().hide()
        View.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        View.customContextMenuRequested.connect(self.NewContextMenu)
        View.setModel(pandasModel(pd.DataFrame()))
        View.setSortingEnabled(True)
        Lay1.addWidget(View)
        Frame.setLayout(Lay1)
        Lay.addWidget(Frame)
        Main.setLayout(Lay)
        
        self.setCentralWidget(Main)
        
    def _fileOpened(self, modelIndex):
        path = self.sender().model().filePath(modelIndex)
        print(path)
        
    def OpenDataSet(self):
        Win = QFileDialog()
        Win.setFileMode(QFileDialog.Directory)
        Win.setDirectory(r"\\bosch.com\dfsrb\DfsDE\LOC\Rt\BST\40_bst_lab\06_products\\")
        
        if Win.exec_():
            self.ResetFrames()
            path = Win.selectedFiles()[0]
            View = self.findChildren(QListWidget)[0]
            setattr(View, 'path', path)
            View.clear()
            for k in os.listdir(path):
                if '.tdms' == k[-5:]:
                    item = QListWidgetItem(k)
                    item.setToolTip(path)
                    View.addItem(item)
                    
    def AddDataSet(self):
        Win = QFileDialog()
        Win.setFileMode(QFileDialog.Directory)
        Win.setDirectory(r"\\bosch.com\dfsrb\DfsDE\LOC\Rt\BST\40_bst_lab\06_products\\")
        
        if Win.exec_():
            path = Win.selectedFiles()[0]
            View = self.findChildren(QListWidget)[0]
            setattr(View, 'path', path)
            for k in os.listdir(path):
                if '.tdms' == k[-5:]:
                    item = QListWidgetItem(k)
                    item.setToolTip(path)
                    View.addItem(item)
    
    def Filter(self):
        for i in self.Search_in_TDMS_cols:
            if self.Search[i]:
                l = self.Search[i]
                self.actualData = self.actualData[self.actualData[i].isin(l)]
                
        for i in self.findChildren(QTableView):
            if i.toolTip() == 'Measurement Data':
                i.setModel(pandasModel(self.actualData))
            
    def Open(self):
        path = getattr(self.sender(), 'path')
        path = self.sender().selectedItems()[0].toolTip()
        file = self.sender().currentItem().text()
        Header, self.Data = self.TDMS_to_DataFrame(path + '/' + file)
        self.actualData = self.Data
        for i in self.findChildren(QTableView):
            if i.toolTip() == 'Header':
                i.setModel(pandasModel(Header))
        self.Filter()
        
    def ResetFrames(self):
        self.TriggerList = []
        self.Search_in_TDMS_cols = ['Index_Messgroesse', 'Index_Messblock',
       'MessblockSchritt', 'MesspunktSchritt', 'Samples', 
       'Status', 'Info', 'Warn', 'Drehrate',
       'DrehrateIst', 'Einbaulage', 'MGFLoop', 'Position', 'PositionIst',
       'Spannung', 'SpannungIst', 'Temperatur', 'TemperaturIst']
        self.Integer_Cols = ['MessblockSchritt', 'MesspunktSchritt', 'Samples', 
       'Status', 'Info', 'Warn', 'Drehrate',
       'DrehrateIst', 'Einbaulage', 'MGFLoop', 'Position', 'PositionIst',
       'Spannung', 'SpannungIst', 'Temperatur', 'TemperaturIst']
        self.Search = {}
        for col in self.Search_in_TDMS_cols:
            self.Search[col] = []
                
    def TDMS_to_DataFrame(self, path):
        File = nptdms.TdmsFile.read(path)
        
        MgIdx = File['Messgroessen']['Index'][:]
        MgMg = File['Messgroessen']['Messgroesse'][:]
        MgE = File['Messgroessen']['Einheit'][:]
        dicMg = dict(zip(MgIdx, MgMg + '(' + MgE + ')'))
        
        MbIdx = File['Messblock']['Index'][:]
        MbMb = File['Messblock']['Messblock'][:]
        dicMb = dict(zip(MbIdx, MbMb))
        
        DataIdxMg = File['Messungen']['Index_Messgroesse'][:]
        DataNameMg = [dicMg[i] for i in DataIdxMg]
        
        DataIdxMb = File['Messungen']['Index_Messblock'][:]
        DataNameMb = [dicMb[i] for i in DataIdxMb]
        
        Data = File['Messungen'].as_dataframe()
        Data['Index_Messblock'] = DataNameMb
        Data['Index_Messgroesse'] = DataNameMg
        Data = Data.drop(labels='Index', axis = 1)
        
        F = open(path,'rb')
        lines=[]
        for i in range(5): #len(open(path,'rb').readlines())):
            lines.append(F.readline())
        
        Head = ''
        for i in lines:
            Head = Head + i.decode('cp1252', 'ignore')
        Head = Head.split('Messgroessen')[0]
        for i in ['\x00', '\x01', '\x03', '\x04', '\x05', '\x06', '\x07', '\x08', 
                  '\x0b', '\x0c', '\x0f', 
                  '\x10', '\x12', '\x14', '\x15', '\x17', '\x18', '\x19',
                  ' \n', ' \r', ' \t']:
            Head = Head.replace(i, '}')
        Head = Head.replace('\n', '}')
        Head = Head.replace('\t', '}')
        H = []
        for i in Head.split('}'):
            if i != '' and i != ' ':
                H.append(i)
                
        Extract  = ['DateTime', 'Profil', 'Sensor Nr', 'Typ', 'LMEx Frame Version', 'LMEx Applikation Version', 'Messplatz', 'SNR', 'USNR']
        Value = []
        for i in Extract:
            try:
                Idx = H.index(i)
                Value.append(H[Idx+1])
            except:
                Value.append('NaN')
            
        dic = dict(zip(Extract, Value))
        df = pd.DataFrame.from_dict(dic, orient='index')
                
        return df, Data


app = QApplication(sys.argv)
app.setStyle('Fusion')
ex = TDMSViewer()
ex.showMaximized()
sys.exit(app.exec_())   
