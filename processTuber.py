#!/bin/env python3

# —————————————————————————————————————————————————————————

import sys, re, signal, time

# ---------------------------------------------------------

from worker import Worker
from dlBox import myDowloadWidget
from smallListItem import SmallListItem
# ---------------------------------------------------------

from PyQt5.QtCore import    (
                            Qt,
                            pyqtSlot,
                            pyqtSignal,
                            QSize,
                            QUrl,
                            QTimer,
                            QEvent,
                            QSettings,
                            QPoint,
                            )
# ---------------------------------------------------------

#from PyQt5 import uic
# ---------------------------------------------------------

from PyQt5.QtGui import QTextCursor,QKeySequence, QIcon
# ---------------------------------------------------------

from PyQt5.QtWidgets import (
                            QApplication,
                            QAbstractItemView,
                            QAction,
                            QCheckBox,
                            QDesktopWidget,
                            QGridLayout,
                            QHBoxLayout,
                            QVBoxLayout,
                            QGroupBox,
                            QPushButton,
                            QPlainTextEdit,
                            QScrollArea,
                            QSizePolicy,
                            QSplitter,
                            QKeySequenceEdit,
                            QMenu,
                            QShortcut,
                            QLineEdit,
                            QListView,
                            QListWidget,
                            QListWidgetItem,
                            QLabel,
                            QWidget,
                            QComboBox,
                            )

# —————————————————————————————————————————————————————————
# BEGIN Setup Main GUI ————————————————————————————————————


class TestUI(QWidget):
    settings = QSettings("gui.ini", QSettings.IniFormat)
    getMetaSignal = pyqtSignal(str)
    pauseSignal = pyqtSignal()
    stopSignal = pyqtSignal()
    downloadSignal = pyqtSignal()
    def __init__(self):
        super().__init__()
        signal.signal(signal.SIGINT, signal.SIG_DFL)

        self.resize(480,256)
        self.setWindowIcon(QIcon("audio-waves.svg"))
        self.setWindowTitle("ProcessTuber")

        self.currentlyChecked = []

        self.numAddWidget = 1
        self.worker = Worker()
        self.setAcceptDrops(True)
        self.init_ui()
        self.init_components()
        self.init_keyboard_shortcuts()
        self.setStyleSheet(
        """
                    QToolTip{
                        border: 0px;
                        font-size: 13px;
                    }
        """
        )
        self.addedWidgets = []
        self.setMinimumWidth(260)
        self.setMinimumHeight(150)
        self.myMainSplitter.setSizes([int(self.width() / 2), int(self.width() / 2)])

    def init_ui(self):

        self.myWidgetList = listBox(self)
        #self.myWidgetList.installEventFilter(self)
        self.myWidgetList.setFocusPolicy(Qt.StrongFocus)
        self.myWidgetList.setMinimumWidth(130)
        self.myWidgetList.setStyleSheet(
        """

                QScrollBar:vertical {
                    width: 0px;
                    background-color: rgba(255,255,255,0);
                }

                QListWidget:item:selected {
                    background-color: transparent;
                }

                QListWidget:item:selected {
                    background-color: #0b1811;
                    opacity: 0.5;
                }

 
        """
        )


        self.myUrlList = listBox(self)
        self.myUrlList.setMinimumWidth(130)
        self.myUrlList.setStyleSheet(
        """

                QScrollBar:vertical {
                    width: 0px;
                    background-color: rgba(255,255,255,0);
                }
                QScrollBar::handle:vertical {
                    background-color: green;         /* #605F5F; */
                    min-height: 5px;
                }

                QListWidget:item:selected {
                    background-color: #0b1811;
                    opacity: 0.5;
                }

        """
        )

        #self.myUrlList.installEventFilter(self)
        self.result = QPlainTextEdit()

        self.myWarningLabel = QLabel("")
        self.myWarningLabel.setAlignment(Qt.AlignCenter)
        self.myWarningLabel.setMinimumHeight(40)
        self.myWarningLabel.setHidden(True)


        #self.createButtonBox()


        #self.myMainBox = QGroupBox()
        #myMainSubLayout = QGridLayout()
        #myMainSubLayout.addWidget(self.myWidgetList, 0,0)
        #myMainSubLayout.addWidget(self.myUrlListBox,  0,1)
        #myMainSubLayout.setColumnStretch(0, 4)
        #myMainSubLayout.setColumnStretch(1, 2)
        #self.myMainBox.setLayout(myMainSubLayout)

        self.myMainSplitter = QSplitter(self)
        self.myMainSplitter.addWidget(self.myWidgetList)
        self.myMainSplitter.addWidget(self.myUrlList)
        self.myMainSplitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.myMainSplitter.setStyleSheet(
        """
                QSplitter::handle {
                    width: 1px;
                    margin: 1px;
                    background: #0f1e16;
                }
                QSplitter::handle:hover {
                    background: #1c3929;
                }
                QSplitter::handle:pressed {
                    background: #3f7e5b;
                }

        """
        )
        self.mySettings = QPushButton("")

        self.myButtonPlay = QPushButton("")
        self.myButtonPause = QPushButton("")
        self.myButtonStop = QPushButton("")
        self.myButtonStop
        self.myLineEdit = MyLineEdit(self)
        self.myLineEdit.droppedUrlSignal.connect(self.addWidget)
        self.myLineEdit.setStyleSheet(
        """
                QLineEdit {
                    background-color: transparent;
                    padding: 5px;
                    margin: 1px;
                    border-color: #13271d;
                    border-width: 1px;
                    border-style: solid;
                    border-radius: 15px;
                }

                QLineEdit:focus {
                    background-color: transparent;
                    padding: 5px;
                    margin: 1px;
                    border-color: green;
                    border-width: 1px;
                    border-style: solid;
                    border-radius: 15px;
                }
        """
        )
        self.myIsCheckedButton = QCheckBox()
        self.myIsCheckedButton.setTristate(True)
        self.myIsCheckedButton.clicked.connect(self.onCheckedWidget)
        self.myIsCheckedButton.setToolTip("If checked, then the download controls\nonly apply to checked items — if threre are any\n\nIf there are none checked the buttons will  apply to all items")
        self.myIsCheckedButton.setCheckable(True)
        self.myIsCheckedButton.setMaximumWidth(15)
        self.myIsCheckedButton.setMaximumHeight(14)
        self.myIsCheckedButton.setStyleSheet(
        """
            QCheckBox::indicator {
                background: #2f2f46;
                margin: 1px;
                border-width: 1px;
                border-style: solid;
                border-radius: 6px;
            }
            QCheckBox::indicator:indeterminate {
                background: #0073ac;
                margin: 1px;
                border-width: 1px;
                border-style: solid;
                border-radius: 6px;
            }
            QCheckBox::indicator:checked {
                background: #4c996e;
                margin: 1px;
                border-width: 1px;
                border-style: solid;
                border-radius: 6px;
            }
        """
        )
        #self.myIsCheckedButton.setStyleSheet(
        #"""
                #QPushButton {
                    #background-color: transparent;
                    #padding: 5px;
                    #margin-left: 1px;
                    #border-color: #33674b;
                    #border-width: 1px;
                    #border-style: solid;
                    #border-radius: 7px;
                #}
                #QPushButton:checked {
                    #background-color: #4c996e;
                    #padding: 5px;
                    #margin-left: 1px;
                    #border-color: green;
                    #border-width: 1px;
                    #border-style: solid;
                    #border-radius: 7px;
                #}
        #"""
        #)
        self.myTopBox = QWidget(self)
        myTopBoxLayout = QHBoxLayout()
        myTopBoxLayout.addSpacing(8)
        myTopBoxLayout.addWidget(self.mySettings)
        myTopBoxLayout.addSpacing(10)
        myTopBoxLayout.addWidget(self.myLineEdit)
        myTopBoxLayout.addSpacing(10)
        myTopBoxLayout.addWidget(self.myButtonStop)
        myTopBoxLayout.addSpacing(5)
        myTopBoxLayout.addWidget(self.myButtonPause)
        myTopBoxLayout.addSpacing(5)
        myTopBoxLayout.addWidget(self.myButtonPlay)
        myTopBoxLayout.addSpacing(10)
        myTopBoxLayout.addWidget(self.myIsCheckedButton)
        myTopBoxLayout.setContentsMargins(0, 0, 9, 0)
        myTopBoxLayout.setSpacing(0)
        self.myTopBox.setLayout(myTopBoxLayout)
        self.myTopBox.setMaximumHeight(50)
        self.myTopBox.setStyleSheet(
        """
                QPushButton {
                        font-size: 18px;
                        border: 1 solid transparent;
                        background-color: transparent;
                }

        """
        )


        self.myMainLayout = QVBoxLayout(self)
        self.myMainLayout.addWidget(self.myTopBox)
        self.myMainLayout.addWidget(self.myWarningLabel)
        self.myMainLayout.addWidget(self.myMainSplitter)
        self.myMainLayout.setContentsMargins(0, 0, 0, 0)
        self.myMainLayout.setSpacing(0)
        self.myMainLayout.setAlignment(Qt.AlignTop)
        #self.setMinimumWidth(180)



    #def createButtonBox(self):

        #self.myUrlListBox = QWidget(self)
        #myLayout = QVBoxLayout()
        #myLayout.addWidget(self.myUrlList)
        #self.myUrlListBox.setLayout(myLayout)

# SHORTCUTS ----------------------------------------------------------

    def init_keyboard_shortcuts(self):
        #self.shortcutSpacePressed = QShortcut(QKeySequence("Space"), self)
        #self.shortcutSpacePressed.activated.connect(self.pauseSignalCheck)

        self.shortcutCtrlShiftUp = QShortcut(QKeySequence("Ctrl+Shift+Up"), self)
        self.shortcutCtrlShiftUp.activated.connect(self.moveCenter)

        self.shortcutShiftDelete = QShortcut(QKeySequence("Shift+Del"), self)
        self.shortcutShiftDelete.activated.connect(self.remove_from_list)

    # QUIT APP - - - - - - - - - - - - - - - - - - - - - - - - -

        self.shortcutQuit = QShortcut(QKeySequence("Ctrl+Q"), self)
        self.shortcutQuit.activated.connect(lambda: sys.exit())

        self.shortcutQuitX = QShortcut(QKeySequence("Ctrl+Shift+X"), self)
        self.shortcutQuitX.activated.connect(lambda: sys.exit())

    #  - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self.shortcutPaste = QShortcut(QKeySequence("Ctrl+V"), self)
        self.shortcutPaste.activated.connect(lambda: self.addWidget(QApplication.clipboard().text()))

        self.shortcutCtrlUp = QShortcut(QKeySequence("Ctrl+Up"), self)
        self.shortcutCtrlUp.activated.connect(self.moveRight)

    # MOVE AND RESIZE WINDOW - - - - - - - - - - - - - - - - - -

        self.shortcutCtrlDown = QShortcut(QKeySequence("Ctrl+Down"), self)
        self.shortcutCtrlDown.activated.connect(self.moveDown)

        self.shortcutResizeLeft = QShortcut(QKeySequence("Ctrl+Left"), self)
        self.shortcutResizeLeft.activated.connect(self.resizeLeft)

        self.shortcutResizeRight = QShortcut(QKeySequence("Ctrl+Right"), self)
        self.shortcutResizeRight.activated.connect(self.resizeRight)

    #  - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self.shortcutCtrlSpacePressed = QShortcut(QKeySequence("Ctrl+Space"), self)
        self.shortcutCtrlSpacePressed.activated.connect(lambda: self.setFocus())

        self.shortcutCtrlReturnPressed = QShortcut(QKeySequence("Ctrl+Return"), self)
        self.shortcutCtrlReturnPressed.activated.connect(self.downloadSignalCheck)

        self.shortcutCtrlShiftReturnPressed = QShortcut(QKeySequence("Ctrl+Shift+Return"), self)
        self.shortcutCtrlShiftReturnPressed.activated.connect(lambda: self.stopSignal.emit())

# --------------------------------------------------------------------

    def moveCenter(self):
        self.resize(480,256)
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

    def moveDown(self):
        qtRectangle = self.frameGeometry()
        print(qtRectangle)
        centerPoint = QDesktopWidget().availableGeometry().center()
        available_screen = QDesktopWidget().availableGeometry()
        print(centerPoint)
        print(available_screen)
        qtRectangle.moveTop(900)
        self.resize(1800,150)
        self.move(qtRectangle.topLeft())

    def moveRight(self):
        qtRectangle = self.frameGeometry()
        print(qtRectangle)
        centerPoint = QDesktopWidget().availableGeometry().center()
        available_screen = QDesktopWidget().availableGeometry()
        print(centerPoint)
        print(available_screen)
        self.resize(180,400)
        qtRectangle.moveLeft(1670)
        self.resize(180,957)
        self.move(qtRectangle.topLeft())

    @pyqtSlot()
    def resizeRight(self):
        if self.myMainSplitter.sizes()[0] == 0:
            self.myMainSplitter.setSizes([1,1])
        elif self.myMainSplitter.sizes()[0] > 0:
            print(self.myMainSplitter.sizes())
            self.myMainSplitter.setSizes([1,0])
            self.myWidgetList.setFocus()

    @pyqtSlot()
    def resizeLeft(self):
        if self.myMainSplitter.sizes()[1] == 0:
            self.myMainSplitter.setSizes([1,1])
        elif self.myMainSplitter.sizes()[1] > 0:
            self.myMainSplitter.setSizes([0,1])




    def init_components(self):
        self.myButtonPause.clicked.connect(self.pauseSignalCheck)
        self.myButtonStop.clicked.connect(self.stopSignalCheck)
        self.myButtonPlay.clicked.connect(self.downloadSignalCheck)
        #self.myButtonPause.clicked.connect(lambda: self.pauseSignal.emit())
        #self.myButtonStop.clicked.connect(lambda: self.stopSignal.emit())
        #self.myButtonPlay.clicked.connect(lambda: self.downloadSignal.emit())

        self.myWidgetList.clicked.connect(self.press_WidgetListItem)
        self.myWidgetList.clickedSignal.connect(self.deselectAll)
        self.myWidgetList.deleteSignal.connect(self.remove_from_list)
        self.myWidgetList.currentRowChanged.connect(self.syncRowsBig)

        self.myUrlList.currentRowChanged.connect(self.syncRowsSmall)
        self.myUrlList.clickedSignal.connect(self.deselectAll)
        self.myUrlList.deleteSignal.connect(self.remove_from_list)

        self.myLineEdit.returnPressed.connect(self.press_add)




# END Setup Main GUI ——————————————————————————————————————
# —————————————————————————————————————————————————————————

    @pyqtSlot(int)
    def syncRowsBig(self):
        ul = self.myUrlList
        wl = self.myWidgetList

        ul.setCurrentRow(wl.currentRow())

    @pyqtSlot(int)
    def syncRowsSmall(self):
        ul = self.myUrlList
        wl = self.myWidgetList

        wl.setCurrentRow(ul.currentRow())

# Main GUI funtions ———————————————————————————————————————
    @pyqtSlot()
    def pauseSignalCheck(self):
        checkFlag = False
        for x in range(self.myWidgetList.count()):
            my_item_widget = self.myWidgetList.itemWidget(self.myWidgetList.item(x))
            print(my_item_widget.isCheckedState)
            if my_item_widget.isCheckedState == True:
                my_item_widget.press_pause()
                checkFlag = True
            if checkFlag == False:
                self.pauseSignal.emit()

    @pyqtSlot()
    def downloadSignalCheck(self):
        time.sleep(.2)
        checkFlag = False
        for x in range(self.myWidgetList.count()):
            my_item_widget = self.myWidgetList.itemWidget(self.myWidgetList.item(x))
            if my_item_widget.isCheckedState == True:
                my_item_widget.press_download()
                checkFlag = True
        if checkFlag == False:
            self.downloadSignal.emit()

        #if self.myIsCheckedButton.isChecked():
            #for x in range(self.myWidgetList.count()):
                #my_item_widget = self.myWidgetList.itemWidget(self.myWidgetList.item(x))
                #if my_item_widget.isCheckedStateFunction():
                    #my_item_widget.press_download()
        #else:
            #self.downloadSignal.emit()

    @pyqtSlot()
    def stopSignalCheck(self):
        checkFlag = False
        for x in range(self.myWidgetList.count()):
            my_item_widget = self.myWidgetList.itemWidget(self.myWidgetList.item(x))
            print(my_item_widget.isCheckedState)
            if my_item_widget.isCheckedState == True:
                my_item_widget.press_stop()
                checkFlag = True
            if checkFlag == False:
                self.stopSignal.emit()

    def press_toggle_leftBox(self):
        print(self.myMainSplitter.sizes()[0])
        if self.myMainSplitter.sizes()[0] == 0:
            self.myMainSplitter.setSizes([1,1])
            #self.myWidgetList.setMaximumWidth(0)
        else:
            self.myMainSplitter.setSizes([1,0])

            #self.myWidgetList.setMaximumWidth(7680)


    def press_add(self):
        lst = []

        for x in range(self.myUrlList.count()):
            other_current = self.myUrlList.itemWidget(self.myUrlList.item(x))
            current = self.myWidgetList.itemWidget(self.myWidgetList.item(x))
            if self.myLineEdit.text().lower() in other_current._Title.itemText(0).lower():
                for x in range(self.myUrlList.count()):
                    self.myUrlList.item(x).setSelected(False)
                    self.myWidgetList.item(x).setSelected(False)

        for x in range(self.myUrlList.count()):
            other_current = self.myUrlList.itemWidget(self.myUrlList.item(x))
            current = self.myWidgetList.itemWidget(self.myWidgetList.item(x))
            if self.myLineEdit.text().lower() in other_current._Title.itemText(0).lower():
                lst.append(x)
                self.myWidgetList.setSelectionMode(QAbstractItemView.MultiSelection)
                self.myUrlList.setSelectionMode(QAbstractItemView.MultiSelection)
                self.myUrlList.item(x).setSelected(True)
                self.myWidgetList.item(x).setSelected(True)
                self.myUrlList.setSelectionMode(QAbstractItemView.SingleSelection)
                self.myWidgetList.setSelectionMode(QAbstractItemView.SingleSelection)

            if len(lst) == 1:
                self.myUrlList.setCurrentItem(self.myUrlList.item(lst[0]))
                self.myWidgetList.setCurrentItem(self.myWidgetList.item(lst[0]))

        myAnswer = self.myLineEdit.text()

        if self.validateUrlLineCheck(myAnswer):
            self.addWidget(myAnswer)
        self.myLineEdit.clear()



    @pyqtSlot()
    def press_UrlListItem(self):
        originalWidget = self.sender().parent()
        #originalWidget = self.sender()
        itemInListWidget = self.myUrlList.itemAt(originalWidget.pos())
        rowIndex = self.myUrlList.row(itemInListWidget)
        print(originalWidget,itemInListWidget,rowIndex)
        print("clicked me!")
        self.myWidgetList.setCurrentItem(self.myWidgetList.item(rowIndex))
        self.myUrlList.setCurrentItem(self.myUrlList.item(rowIndex))
        self.press_WidgetListItem()


    @pyqtSlot()
    def press_WidgetListItem(self):

        if self.myWidgetList.currentItem() != None:
            myCurrentItem = self.myWidgetList.currentItem()
            for x in range(self.myWidgetList.count()):
                if self.myWidgetList.item(x) == myCurrentItem:

                    self.myUrlList.item(x).setSelected(True)

    def hideUnhideMatchWarningLabel(self):
        self.myWarningLabel.setText("Url is already queued")
        self.myWarningLabel.setHidden(False)
        self.mytimer = QTimer()
        self.mytimer.timeout.connect(lambda: self.myWarningLabel.setHidden(True))
        self.mytimer.start(3500)

    def hideUnhideIllegalWarningLabel(self):
        self.myWarningLabel.setText("Not a valid URL")
        self.myWarningLabel.setHidden(False)
        self.mytimer = QTimer()
        self.mytimer.timeout.connect(lambda: self.myWarningLabel.setHidden(True))
        self.mytimer.start(3500)

    def deselectAll(self):
        for x in range(self.myUrlList.count()):
            self.myUrlList.item(x).setSelected(False)
            self.myWidgetList.item(x).setSelected(False)
            #self._keysequenceedit.setFocus()


# Other funtions ———————————————————————————————————————————



    @pyqtSlot(str)
    def updateUrlSmall(self, new_url):
        originalWidget = self.sender()
        parentOfOriginalWidget = self.sender().parent()
        itemInListWidget = self.myUrlList.itemAt(originalWidget.pos())

        rowIndex = self.myUrlList.row(itemInListWidget)

        my_small_widget = self.myUrlList.itemWidget(self.myUrlList.item(rowIndex))
        my_big_widget = self.myWidgetList.itemWidget(self.myWidgetList.item(rowIndex))


        my_small_widget.set_new_url(new_url)
        my_big_widget.urlValueChanged(new_url)

    @pyqtSlot(str)
    def updateFolderSmall(self, new_folder):
        originalWidget = self.sender()
        parentOfOriginalWidget = self.sender().parent()
        itemInListWidget = self.myUrlList.itemAt(originalWidget.pos())

        rowIndex = self.myUrlList.row(itemInListWidget)

        my_small_widget = self.myUrlList.itemWidget(self.myUrlList.item(rowIndex))
        my_big_widget = self.myWidgetList.itemWidget(self.myWidgetList.item(rowIndex))

        my_big_widget.folderLineEdit.setText(new_folder)
        my_big_widget.folderValueChanged(new_folder)

    @pyqtSlot(str)
    def updateOuttmplSmall(self, new_outtmpl):
        originalWidget = self.sender()
        parentOfOriginalWidget = self.sender().parent()
        itemInListWidget = self.myUrlList.itemAt(originalWidget.pos())

        rowIndex = self.myUrlList.row(itemInListWidget)

        my_small_widget = self.myUrlList.itemWidget(self.myUrlList.item(rowIndex))
        my_big_widget = self.myWidgetList.itemWidget(self.myWidgetList.item(rowIndex))

        my_big_widget.outtmplLineEdit.setText(new_outtmpl)
        my_big_widget.outtmplValueChanged(new_outtmpl)


    @pyqtSlot(str)
    def updateUrl(self, new_url):
        originalWidget = self.sender()
        itemInListWidget = self.myWidgetList.itemAt(originalWidget.pos())
        rowIndex = self.myWidgetList.row(itemInListWidget)
        my_small_widget = self.myUrlList.itemWidget(self.myUrlList.item(rowIndex))
        my_big_widget = self.myWidgetList.itemWidget(self.myWidgetList.item(rowIndex))
        if my_small_widget._Url != new_url:
            my_small_widget.set_new_url(new_url)
            my_big_widget.urlValueChanged(new_url)

    @pyqtSlot(int)
    def updateFormatSmall(self, new_format_index):
        originalWidget = self.sender()
        parentOfOriginalWidget = self.sender().parent()
        itemInListWidget = self.myUrlList.itemAt(originalWidget.pos())

        rowIndex = self.myUrlList.row(itemInListWidget)

        my_small_widget = self.myUrlList.itemWidget(self.myUrlList.item(rowIndex))
        my_big_widget = self.myWidgetList.itemWidget(self.myWidgetList.item(rowIndex))

        my_big_widget.formatSelect.setCurrentIndex(new_format_index)
        my_big_widget.formatSelectClone.setCurrentIndex(new_format_index)
        my_big_widget.updateTitle()
        my_big_widget.update_dl_gui_ToolTips()

    @pyqtSlot(int)
    def updateQualitySmall(self, new_quality):
        originalWidget = self.sender()
        parentOfOriginalWidget = self.sender().parent()
        itemInListWidget = self.myUrlList.itemAt(originalWidget.pos())

        rowIndex = self.myUrlList.row(itemInListWidget)

        my_small_widget = self.myUrlList.itemWidget(self.myUrlList.item(rowIndex))
        my_big_widget = self.myWidgetList.itemWidget(self.myWidgetList.item(rowIndex))

        my_big_widget.audioQualitySlider.setValue(new_quality)
        my_big_widget.updateTitle()
        my_big_widget.update_dl_gui_ToolTips()



    def onClickedWidgetText(self):
        #originalWidget = self.sender().parent()
        originalWidget = self.sender()
        itemInListWidget = self.myWidgetList.itemAt(originalWidget.pos())
        rowIndex = self.myWidgetList.row(itemInListWidget)
        #print(originalWidget,itemInListWidget,rowIndex)
        #print("clicked me!")
        self.myWidgetList.setCurrentItem(self.myWidgetList.item(rowIndex))
        self.press_WidgetListItem()




    def onCheckedWidget(self):
        if self.myIsCheckedButton.checkState() == 0:
            for x in range(self.myWidgetList.count()):
                my_item_widget = self.myWidgetList.itemWidget(self.myWidgetList.item(x))
                my_url_widget = self.myUrlList.itemWidget(self.myUrlList.item(x))

                my_item_widget.isCheckedState = False
                my_item_widget.dl_gui_IsCheckedStateButton.setChecked(False)

                my_url_widget.isCheckedState = False
                my_url_widget._CheckButton.setChecked(False)

        if self.myIsCheckedButton.checkState() == 1:
            if len(self.currentlyChecked) != 0:
                for index in self.currentlyChecked:

                    #my_item_widget = self.myWidgetList.itemWidget(self.myWidgetList.item(index))
                    #my_url_widget = self.myUrlList.itemWidget(self.myUrlList.item(index))

                    index.isCheckedState = True
                    try:
                        index._CheckButton.setChecked(True)
                    except:
                        pass
                    try:
                        index.dl_gui_IsCheckedStateButton.setChecked(True)
                    except:
                        pass
                    #my_item_widget.isCheckedState = True
                    #my_item_widget.dl_gui_IsCheckedStateButton.setChecked(True)

                    #my_url_widget.isCheckedState = True
                    #my_url_widget._CheckButton.setChecked(True)
            else:
                for x in range(self.myWidgetList.count()):
                    my_item_widget = self.myWidgetList.itemWidget(self.myWidgetList.item(x))
                    my_url_widget = self.myUrlList.itemWidget(self.myUrlList.item(x))

                    my_url_widget.isCheckedState = True
                    my_url_widget._CheckButton.setChecked(True)

                    my_item_widget.isCheckedState = True
                    my_item_widget.dl_gui_IsCheckedStateButton.setChecked(True)

                self.myIsCheckedButton.setCheckState(2)

        if self.myIsCheckedButton.checkState() == 2:

            if len(self.currentlyChecked) == 0:

                for x in range(self.myWidgetList.count()):
                    my_item_widget = self.myWidgetList.itemWidget(self.myWidgetList.item(x))
                    my_url_widget = self.myUrlList.itemWidget(self.myUrlList.item(x))

                    self.currentlyChecked.append(my_item_widget)
                    self.currentlyChecked.append(my_url_widget)

            for x in range(self.myWidgetList.count()):
                my_item_widget = self.myWidgetList.itemWidget(self.myWidgetList.item(x))
                my_url_widget = self.myUrlList.itemWidget(self.myUrlList.item(x))

                my_url_widget.isCheckedState = True
                my_url_widget._CheckButton.setChecked(True)

                my_item_widget.isCheckedState = True
                my_item_widget.dl_gui_IsCheckedStateButton.setChecked(True)


    @pyqtSlot()
    def onClickedCheckSmall(self):
        self.currentlyChecked.clear()
        checkFlag = False
        originalWidget = self.sender()
        itemInListWidget = self.myUrlList.itemAt(originalWidget.pos())
        rowIndex = self.myUrlList.row(itemInListWidget)

        my_item_widget = self.myUrlList.itemWidget(self.myUrlList.item(rowIndex))
        my_other_widget = self.myWidgetList.itemWidget(self.myWidgetList.item(rowIndex))

        my_other_widget.press_checked()

        for x in range(self.myWidgetList.count()):
            other_current = self.myWidgetList.itemWidget(self.myWidgetList.item(x))
            current = self.myUrlList.itemWidget(self.myUrlList.item(x))
            if other_current.isCheckedState == True:
                self.currentlyChecked.append(other_current)
                self.currentlyChecked.append(current)
                checkFlag = True

        if checkFlag == False:
            self.myIsCheckedButton.setCheckState(0)

        elif checkFlag == True:

            my_count = 0

            for x in range(self.myWidgetList.count()):

                other_current = self.myWidgetList.itemWidget(self.myWidgetList.item(x))
                current = self.myUrlList.itemWidget(self.myUrlList.item(x))

                if current.isCheckedState == True:
                    my_count = my_count + 1

            if my_count < self.myWidgetList.count():
                self.myIsCheckedButton.setCheckState(1)
            elif my_count == self.myWidgetList.count():
                self.myIsCheckedButton.setCheckState(2)



    @pyqtSlot()
    def onClickedCheckBig(self):
        self.currentlyChecked.clear()
        checkFlag = False
        originalWidget = self.sender()
        itemInListWidget = self.myWidgetList.itemAt(originalWidget.pos())
        rowIndex = self.myWidgetList.row(itemInListWidget)

        my_other_widget = self.myUrlList.itemWidget(self.myUrlList.item(rowIndex))
        my_item_widget = self.myWidgetList.itemWidget(self.myWidgetList.item(rowIndex))

        my_other_widget.press_checked()

        for x in range(self.myUrlList.count()):
            other_current = self.myUrlList.itemWidget(self.myUrlList.item(x))
            current = self.myWidgetList.itemWidget(self.myWidgetList.item(x))
            if other_current.isCheckedState == True:
                self.currentlyChecked.append(other_current)
                self.currentlyChecked.append(current)
                checkFlag = True

        if checkFlag == False:
            self.myIsCheckedButton.setCheckState(0)

        elif checkFlag == True:

            my_count = 0

            for x in range(self.myWidgetList.count()):

                current = self.myWidgetList.itemWidget(self.myWidgetList.item(x))
                other_current = self.myUrlList.itemWidget(self.myUrlList.item(x))

                if current.isCheckedState == True:
                    my_count = my_count + 1

            if my_count < self.myWidgetList.count():
                self.myIsCheckedButton.setCheckState(1)
            elif my_count == self.myWidgetList.count():
                self.myIsCheckedButton.setCheckState(2)


# ADD WIDGET -------------------------------------------------------
    #@pyqtSlot(int)
    #def handleWidgetProgressTotal(self, current_progress):
        #originalWidget = self.sender()
        #itemInListWidget = self.myWidgetList.itemAt(originalWidget.pos())
        #rowIndex = self.myWidgetList.row(itemInListWidget)
        #my_item_widget = self.myUrlList.itemWidget(self.myUrlList.item(rowIndex))
        #my_item_widget.progressTotal(current_progress)

    #@pyqtSlot(int)
    #def handleWidgetProgressValue(self, current_progress):
        #originalWidget = self.sender()
        #itemInListWidget = self.myWidgetList.itemAt(originalWidget.pos())

        #rowIndex = self.myWidgetList.row(itemInListWidget)

        #my_item_widget = self.myUrlList.itemWidget(self.myUrlList.item(rowIndex))
        #my_item_widget.progressValue(current_progress)

    @pyqtSlot(list)
    def handleWidgetInfo(self, current_info):
        originalWidget = self.sender()
        itemInListWidget = self.myWidgetList.itemAt(originalWidget.pos())
        rowIndex = self.myWidgetList.row(itemInListWidget)
        my_item_widget = self.myUrlList.itemWidget(self.myUrlList.item(rowIndex))
        my_item_widget.gotInfoSlot(current_info)

    @pyqtSlot(int)
    def handleChangeSmallSlider(self, current_quality):
        originalWidget = self.sender()
        itemInListWidget = self.myWidgetList.itemAt(originalWidget.pos())
        rowIndex = self.myWidgetList.row(itemInListWidget)
        my_item_widget = self.myUrlList.itemWidget(self.myUrlList.item(rowIndex))
        my_item_widget.audioQualitySlider.setValue(current_quality)

    @pyqtSlot(str)
    def validateUrlLineCheck(self, url):
        regex = re.compile(
                r'^(?:http|ftp)s?://' # http:// or https://
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
                r'localhost|' #localhost...
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
                r'(?::\d+)?' # optional port
                r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        if not re.match(regex, url):
            return False
        else:
            return True

    @pyqtSlot(str)
    def validateUrl(self, url):
        regex = re.compile(
                r'^(?:http|ftp)s?://' # http:// or https://
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
                r'localhost|' #localhost...
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
                r'(?::\d+)?' # optional port
                r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        if not re.match(regex, url):
            self.hideUnhideIllegalWarningLabel()
            return False
        else:
            return True

    @pyqtSlot(str)
    def checkMatchUrl(self,  url):
        checkFlag = False
        #   Check if url matches one in list
        for x in range(self.myUrlList.count()):
            my_item_widget = self.myUrlList.itemWidget(self.myUrlList.item(x))
            if my_item_widget._Url == url:
                self.hideUnhideMatchWarningLabel()
                self.myUrlList.item(x).setSelected(True)
                self.myWidgetList.setCurrentItem(self.myWidgetList.item(x))
                checkFlag = True

        if checkFlag == True:
            return True
        else:
            return False

    def addWidget(self, url):
        if self.validateUrl(url):
            if self.checkMatchUrl(url):
                pass
            else:
                self.widget_WidgetList = myDowloadWidget(self.numAddWidget, url)

                self.widget_WidgetListListItem = QListWidgetItem()
                #self.widget_WidgetListListItem.setSizeHint(self.widget_WidgetList.sizeHint())
                #self.widget_WidgetListListItem.setSizeHint(QSize(170, 140))
                height = self.height()
                try:
                    self.widget_WidgetListListItem.setSizeHint(QSize(100,height))
                except:
                    print("fail")
                #self.widget_WidgetListListItem.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
                #self.widget_WidgetListListItem.setSizeHint(QSize(100, 150))

                ### Set selecatibility using flags
                #self.widget_WidgetListListItem.setFlags(Qt.ItemIsSelectable)    # Selectable = False
                #self.widget_WidgetListListItem.setFlags(self.widget_WidgetListListItem.flags() & ~ Qt.ItemIsSelectable)    # Selectable = False
                #self.widget_WidgetListListItem.setFlags(self.widget_WidgetListListItem.flags() | Qt.ItemIsSelectable)      # Selectable = True


                self.widget_WidgetUrlList = SmallListItem(url)
                self.myUrlListItem = QListWidgetItem()
                self.myUrlListItem.setSizeHint(QSize(0,27))

                self.myWidgetList.insertItem(0, self.widget_WidgetListListItem)
                self.myWidgetList.setItemWidget(self.widget_WidgetListListItem, self.widget_WidgetList)
                self.myUrlList.insertItem(0, self.myUrlListItem)
                self.myUrlList.setItemWidget(self.myUrlListItem, self.widget_WidgetUrlList)

                #self.widget_WidgetList.dl_gui_TextLog.clickedSignal.connect(self.onClickedWidgetText)
                self.widget_WidgetList.clickedSignal.connect(self.onClickedWidgetText)
                self.widget_WidgetList.changeSmallSliderSignal.connect(self.handleChangeSmallSlider)
                #self.widget_WidgetList.progressValueSignal.connect(self.handleWidgetProgressValue)
                #self.widget_WidgetList.progressTotalSignal.connect(self.handleWidgetProgressTotal)
                self.widget_WidgetList.gotInfoSignal.connect(self.handleWidgetInfo)
                #self.widget_WidgetList.resizeSignal.connect(lambda: self.widget_WidgetListListItem.setSizeHint(QSize(200, 200)))
                self.widget_WidgetList.droppedUrlSignal.connect(self.addWidget)
                self.widget_WidgetList.clickedCheckSignal.connect(self.onClickedCheckBig)
                self.downloadSignal.connect(self.widget_WidgetList.press_download)
                self.pauseSignal.connect(self.widget_WidgetList.press_pause)
                self.stopSignal.connect(self.widget_WidgetList.press_stop)
                self.widget_WidgetList.updateUrlSignal.connect(self.updateUrl)

                self.widget_WidgetUrlList._Title.clickedSignal.connect(self.press_UrlListItem)
                self.widget_WidgetUrlList.urlUpdatedSignal.connect(self.updateUrlSmall)
                self.widget_WidgetUrlList.qualityUpdatedSignal.connect(self.updateQualitySmall)
                self.widget_WidgetUrlList.formatUpdatedSignal.connect(self.updateFormatSmall)
                self.widget_WidgetUrlList.folderUpdatedSignal.connect(self.updateFolderSmall)
                self.widget_WidgetUrlList.clickedCheckSignal.connect(self.onClickedCheckSmall)
                self.widget_WidgetUrlList.outtmplUpdatedSignal.connect(self.updateOuttmplSmall)

                other_current = self.myUrlList.itemWidget(self.myUrlList.item(0))
                current = self.myWidgetList.itemWidget(self.myWidgetList.item(0))

                other_current.my_twin = current
                current.my_twin = other_current



        #print(other_current.my_twin)
        #print(current.my_twin)

#   Get the widget inside QListWidgetItem
        #self.addedWidgets.append(self.myWidgetList.itemWidget(self.myWidgetList.item(x)))



#   --------------------------------------------------------------

    def resizeEvent(self, event):
        height = self.height()
        #width = self.width()

        if self.myWidgetList.count() > 0:
            for x in range(self.myWidgetList.count()):
                item = self.myWidgetList.item(x)
                item.setSizeHint(QSize(100, height))




    @pyqtSlot()
    def remove_from_list(self):
        remove_items = []
        for x in range(self.myUrlList.count()):
            if self.myUrlList.item(x).isSelected():
                remove_items.append(self.myUrlList.item(x))

        if len(remove_items) > 0:
            for i in remove_items:

                self.myWidgetList.takeItem(self.myUrlList.row(i))
                self.myUrlList.takeItem(self.myUrlList.row(i))

        else:
            try:
                myWidgetList_current_row = self.myWidgetList.currentRow()
                myUrlList_current_row = self.myUrlList.currentRow()

                try:
                    self.myWidgetList.takeItem(myWidgetList_current_row)
                    self.myUrlList.takeItem(myWidgetList_current_row)
                except:
                    print("fail takeitem 1")
                try:
                    self.myWidgetList.takeItem(myUrlList_current_row)
                    self.myUrlList.takeItem(myUrlList_current_row)
                except:
                    print("fail takeitem 2")
            except:
                print("fail!")


# Drag and Drop ———————————————————————————————————————————

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()

        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(Qt.CopyAction)
            event.accept()

        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(Qt.CopyAction)
            event.accept()

            for url in event.mimeData().urls():
                if url.isLocalFile():
                    pass
                else:
                    self.urlToText = str(url.toString())
                    self.addWidget(self.urlToText)

    def mousePressEvent(self, event):
        self._mouse_button = event.button()
        if self._mouse_button == 1:
            self.deselectAll()


    #def eventFilter(self, obj, event):
        #if obj is self.myUrlList and event.type() == QEvent.KeyPress:
            #if event.key() == Qt.Key_Shift:
                #if event.key() == Qt.Key_Delete:
                    #print("lol")
                    #return True
        #return super(TestUI, self).eventFilter(obj, event)



# —————————————————————————————————————————————————————————
# SUBCLASSES & OVERLOADS ——————————————————————————————————


#   LISTBOX BEGIN   ---------------------------------------

class listBox(QListWidget):
    clickedSignal = pyqtSignal()
    valueChanged = pyqtSignal(object)
    deleteSignal = pyqtSignal()
    def __init__(self, scrollWidget=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scrollWidget=scrollWidget

    def mousePressEvent(self, e):
        self._mose_button = e.button()
        if self._mose_button == 1:
            #print("mose 1")
            self.clickedSignal.emit()
        super(listBox, self).mousePressEvent(e)


    def mouseDoubleClickEvent(self, e):
        if e.button() == 1:
            print("mose 1: 2x!")


    #def printPing(self):
        #print("ping")


    #def wheelEvent(self, e):
        #if self.hasFocus():
            ##print(self.verticalScrollBar().value())
            ##print(self.verticalScrollBar().maximum())
            #my_direction = e.angleDelta().y() // 120
            #print(my_direction)
            #super(QListWidget, self).wheelEvent(e)


#   LISTBOX END     ---------------------------------------
class MyLineEdit(QLineEdit):
    clickedSignal = pyqtSignal()
    doubleclickedSignal = pyqtSignal()
    droppedUrlSignal = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.setDropAction(Qt.MoveAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()

            for url in event.mimeData().urls():
                # https://doc.qt.io/qt-5/qurl.html
                if url.isLocalFile():
                   pass
                else:
                    self.text = str(url.toString())
                    self.droppedUrlSignal.emit(self.text)

        else:
            event.ignore()

# —————————————————————————————————————————————————————————


if __name__ == "__main__":
    APP = QApplication(sys.argv)
    ex = TestUI()
    #APP.setStyle('Plastique')
    ex.show()
    sys.exit(APP.exec_())






#from PyQt5 import QtCore, QtGui, QtWidgets

#class KeySequenceEdit(QtWidgets.QKeySequenceEdit):
    #def keyPressEvent(self, event):
        #super(KeySequenceEdit, self).keyPressEvent(event)
        #seq_string = self.keySequence().toString(QtGui.QKeySequence.NativeText)
        #if seq_string:
            #last_seq = seq_string.split(",")[-1].strip()
            #le = self.findChild(QtWidgets.QLineEdit, "qt_keysequenceedit_lineedit")
            #self.setKeySequence(QtGui.QKeySequence(last_seq))
            #le.setText(last_seq)
            #self.editingFinished.emit()


#class Widget(QtWidgets.QWidget):
    #def __init__(self, parent=None):
        #super(Widget, self).__init__(parent)
        #self._keysequenceedit = KeySequenceEdit(editingFinished=self.on_editingFinished)
        #button = QtWidgets.QPushButton("clear", clicked=self._keysequenceedit.clear)
        #hlay = QtWidgets.QHBoxLayout(self)
        #hlay.addWidget(self._keysequenceedit)
        #hlay.addWidget(button)

    #@QtCore.pyqtSlot()
    #def on_editingFinished(self):
        #sequence = self._keysequenceedit.keySequence()
        #seq_string = sequence.toString(QtGui.QKeySequence.NativeText)
        #print("sequence: ", seq_string)

#if __name__ == '__main__':
    #import sys
    #app = QtWidgets.QApplication(sys.argv)
    #w = Widget()
    #w.show()
    #sys.exit(app.exec_())





#class CheckableList(QListWidget):
    #def __init__(self, parent = None):
        #super(CheckableList, self).__init__(parent)
        #self.parent = parent
        #self.pressed.connect(self.handleItemPressed)

    #def handleItemPressed(self, index):
        #item = self.currentItem()
        #if item.checkState() == Qt.Checked:
            #item.setCheckState(Qt.Unchecked)
        #else:
            #item.setCheckState(Qt.Checked)
        #self.on_selectedItems()

    #def checkedItems(self):
        #checkedItems = []
        #for x in range(self.count()):
            #item = self.item(x)
            #if item.checkState() == Qt.Checked:
                #checkedItems.append(item)
        #return checkedItems

    #def on_selectedItems(self):
        #selectedItems = self.checkedItems()
        #self.parent.lblSelectItem.setText("")
        #for item in selectedItems:
            #self.parent.lblSelectItem.setText("{} {} "
                       #"".format(self.parent.lblSelectItem.text(), item.text()))


#class ExampleWidget(QGroupBox):
    #def __init__(self, numAddWidget):
        #QGroupBox.__init__(self)
        #self.numAddWidget = numAddWidget
        #self.numAddItem   = 1
        #self.setTitle("Title {}".format(self.numAddWidget))
        #self.initSubject()
        #self.organize()

    #def initSubject(self):
        #self.lblName = QLabel("Label Title {}".format(self.numAddWidget), self)
        #self.lblSelectItem = QLabel(self)

        #self.teachersselect = CheckableList(self)
        #item = QListWidgetItem("-Select {}-".format(self.numAddItem))
        #item.setCheckState(Qt.Unchecked)

        #self.teachersselect.addItem(item)

        #self.addbtn = QPushButton("ComboBoxAddItem...", self)
        #self.addbtn.clicked.connect(self.addTeacher)

    #def organize(self):
        #grid = QVBoxLayout(self)
        #self.setLayout(grid)
        #grid.addWidget(self.lblName)
        #grid.addWidget(self.lblSelectItem)
        #grid.addWidget(self.teachersselect)
        #grid.addWidget(self.addbtn)

    #def addTeacher(self):
        #self.numAddItem += 1
        #item = QListWidgetItem("-Select {}-".format(self.numAddItem))
        #item.setCheckState(Qt.Unchecked)
        #self.teachersselect.addItem(item)
