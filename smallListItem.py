#!/bin/env python3

# —————————————————————————————————————————————————————————

import sys,re, subprocess
# ---------------------------------------------------------

from worker import Worker
from dlBox import myDowloadWidget
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
                            )
# ---------------------------------------------------------

#from PyQt5 import uic
# ---------------------------------------------------------

from PyQt5.QtGui import QTextCursor,QKeySequence
# ---------------------------------------------------------

from PyQt5.QtWidgets import (
                            QApplication,
                            QGridLayout,
                            QHBoxLayout,
                            QLineEdit,
                            QVBoxLayout,
                            QPushButton,
                            QProgressBar,
                            QScrollArea,
                            QSizePolicy,
                            QKeySequenceEdit,
                            QShortcut,
                            QSlider,
                            QListView,
                            QLabel,
                            QWidget,
                            QComboBox,
                            )

# —————————————————————————————————————————————————————————
# BEGIN Setup Main GUI ————————————————————————————————————


class SmallListItem(QWidget):
    gotNameSignal = pyqtSignal(str)
    downloadSignal = pyqtSignal()
    qualityUpdatedSignal = pyqtSignal(int)
    formatUpdatedSignal = pyqtSignal(int)
    clickedCheckSignal = pyqtSignal()
    urlUpdatedSignal = pyqtSignal(str)
    folderUpdatedSignal = pyqtSignal(str)
    outtmplUpdatedSignal = pyqtSignal(str)
    def __init__(self, url, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._Url = url
        self.isCheckedState = False
        self._TitleList = []
        self.my_twin = None
        #self._Path = path
        #print(self.my_twin)


        #self._Title = QLabel(self)
        #self._Title.setText("  "+url+"  ")
        self._Progress = MyProgress(self)
        self._Progress.doubleClickSignal.connect(self.openFolder)
        self._Progress.setHidden(True)
        self._Progress.setTextVisible(True)
        self._Progress.setStyleSheet(
        """
            QProgressBar {
                color: #ffffff;
                text-align: left center;
                background-color: rgba(255, 255, 255, 0); /* set transparent */
                opacity: .9;
            }

            QProgressBar:chunk {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 2,
                                stop: 0 #003a67, stop: 1 #002434);

            }
        """
        )

        self._Title = MyQComboBox(self)
        self._Title.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        self._Title.addItem(self._Url)
        self._Title.setStyleSheet(
        """

            QComboBox {
                border: 0;
                background-color: transparent;
                padding-left: 1px;
                margin: 1px;
            }

            QComboBox QAbstractItemView {
                selection-background-color: #222222;
                background-color: transparent;
            }

            QComboBox::drop-down {
                image: url("none");
                subcontrol-origin: padding;
                subcontrol-position: left top;
            }

        """
        )

        self._UrlEdit = QLineEdit(self)
        self._UrlEdit.setHidden(True)

        self._FolderEdit = QLineEdit(self)
        self._FolderEdit.setHidden(True)

        self._OuttmplEdit = QLineEdit(self)
        self._OuttmplEdit.setHidden(True)

        self._CheckButton = QPushButton()
        self._CheckButton.setToolTip("Click to set as checked")
        self._CheckButton.setCheckable(True)
        self._CheckButton.setStyleSheet(
        """
                QPushButton {
                    background-color: transparent;
                    padding: 3px;
                    margin-left: 5px;
                    margin-right: 9px;
                    max-width: 4px;
                    max-height: 4px;
                    border-color: #33674b;
                    border-width: 1px;
                    border-style: solid;
                    border-radius: 6px;
                }
                QPushButton:checked {
                    background-color: #4c996e;
                    padding: 3px;
                    max-width: 4px;
                    max-height: 4px;
                    border-color: transparent;
                    border-width: 1px;
                    border-style: solid;
                    border-radius: 6px;
                }
        """
        )
        self.formatSelect = MyQFormatBox(self)
        self.formatSelect.addItem("mp3"                 , "mp3")
        self.formatSelect.addItem("m4a"                 , "m4a")
        self.formatSelect.addItem("aac"                 , "aac")
        self.formatSelect.addItem("alac"                , "alac")
        self.formatSelect.addItem("opus"                , "opus")
        self.formatSelect.addItem("ogg"                 , "vorbis")
        self.formatSelect.addItem("flac"                , "flac")
        self.formatSelect.addItem("wav"                 , "wav")
        self.formatSelect.setStyleSheet(
        """

            QComboBox {
                border: 0;
                padding-left: 0px;
                background-color: transparent;
                margin: 0px;
            }

        """
        )
        self.formatSelect.setHidden(True)
        self.formatSelect.activated.connect(self.handleFormatChange)

        self.audioQualitySlider = MyQSlider()
        self.audioQualitySlider.setMinimum(0)
        self.audioQualitySlider.setMaximum(9)
        self.audioQualitySlider.setOrientation(Qt.Horizontal)
        self.audioQualitySlider.setValue(9)
        #self.audioQualitySlider.setHidden(True)
        self.audioQualitySlider.setStyleSheet(
        """
                QSlider::groove:horizontal {
                    border: 0px;
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #000000, stop:1 #00aa7f);
                    height: 3px;
                    border-radius: 2px;
                }
                QSlider::sub-page:horizontal {
                    background: transparent;
                    border: 0px;
                    height: 3px;
                    border-radius: 2px;
                }

                QSlider::add-page:horizontal {
                    background: transparent;
                    border: 0;
                    height: 3px;
                    border-radius: 2px;
                }


                QSlider::handle:horizontal {
                    background: #4c996e;
                    border: 1px transparent;
                    width: 14px;
                    margin-top: -3px;
                    margin-bottom: -3px;
                }

        """
        )
        self.sliderLabel = QLabel()
        self.sliderLabel.setText(self.invertValue(self.audioQualitySlider.value()))
        self.sliderBox = QWidget(self)
        sliderLay = QHBoxLayout()
        sliderLay.addWidget(self.sliderLabel)
        sliderLay.addWidget(self.audioQualitySlider)
        self.sliderBox.setLayout(sliderLay)
        self.sliderBox.setHidden(True)

        self.playControls = QWidget(self)

        self.playButton = QPushButton("")
        self.stopButton = QPushButton("")
        self.pauseButton = QPushButton("")
        self.pauseButton.setHidden(True)


        playControlsLay = QHBoxLayout()
        playControlsLay.addSpacing(5)
        playControlsLay.addWidget(self.stopButton)
        playControlsLay.addSpacing(2)

        playControlsLay.addWidget(self.playButton)
        playControlsLay.addWidget(self.pauseButton)
        playControlsLay.addSpacing(2)
        playControlsLay.setContentsMargins(0, 0, 0, 0)
        playControlsLay.setSpacing(0)

        self.playControls.setLayout(playControlsLay)
        self.playControls.setMaximumWidth(40)
        self.playControls.setStyleSheet(
        """
                QPushButton {
                    background-color: transparent;
                    max-width: 10px;
                    max-height: 10px;

                }
        """
        )



        dl_list_mainLayout = QHBoxLayout(self)
        dl_list_mainLayout.addWidget(self._Title)
        dl_list_mainLayout.addWidget(self._UrlEdit)
        dl_list_mainLayout.addWidget(self._FolderEdit)
        dl_list_mainLayout.addWidget(self._OuttmplEdit)
        dl_list_mainLayout.addWidget(self.formatSelect)
        dl_list_mainLayout.addWidget(self.sliderBox)
        dl_list_mainLayout.addWidget(self._Progress)
        dl_list_mainLayout.addWidget(self.playControls)
        dl_list_mainLayout.addWidget(self._CheckButton)
        dl_list_mainLayout.setContentsMargins(0, 0, 0, 0)
        dl_list_mainLayout.setSpacing(0)

        self.setLayout(dl_list_mainLayout)
        self.setMinimumWidth(10)



        self._Title.editableFormatSignal.connect(self.makeFormatEditableSlot)
        self._Title.editableQualitySignal.connect(self.makeQualityEditableSlot)
        self._Title.editableUrlSignal.connect(self.makeUrlEditableSlot)
        self._Title.editableFolderSignal.connect(self.makeFolderEditableSlot)
        self._Title.editableOuttmplSignal.connect(self.makeOuttmplEditableSlot)
        self._Title.activated.connect(self.TitleActivated)
        self.audioQualitySlider.sliderReleased.connect(self.finishedQualitySelect)
        self.audioQualitySlider.valueChanged.connect(self.updateSliderLabel)
        self.audioQualitySlider.finishedEditSignal.connect(self.finishedQualitySelect)
        self.formatSelect.activated.connect(self.finishedFormatSelect)
        self.formatSelect.finishedEditSignal.connect(self.finishedFormatSelect)
        self._UrlEdit.returnPressed.connect(self.finishedEditSlot)
        self._FolderEdit.returnPressed.connect(self.finishedEditSlot)
        self._OuttmplEdit.returnPressed.connect(self.finishedEditSlot)
        self._Progress.valueChanged.connect(self.handleValueChangedProgress)
        self._CheckButton.clicked.connect(self.press_checked)
        self._CheckButton.clicked.connect(lambda: self.clickedCheckSignal.emit())
        self.playButton.clicked.connect(self.press_download)
        self.pauseButton.clicked.connect(self.press_pause)
        self.stopButton.clicked.connect(self.press_stop)




    @pyqtSlot()
    def resetGUI(self):

        self.playButton.setHidden(False)
        self.pauseButton.setHidden(True)
        self.formatSelect.setHidden(True)
        self.sliderBox.setHidden(True)

        self._UrlEdit.setHidden(True)
        self._FolderEdit.setHidden(True)
        self._OuttmplEdit.setHidden(True)
        self._Progress.setHidden(True)
        self._Progress.reset()
        self._Title.setHidden(False)
        self._Title.setCurrentIndex(0)

    @pyqtSlot()
    def press_download(self):
        if self.my_twin.paused == 1:
            self.my_twin.press_pause()
        elif self.my_twin.paused == 0:
            self.my_twin.press_download()
        self.playButton.setHidden(True)
        self.pauseButton.setHidden(False)

    @pyqtSlot()
    def press_pause(self):
        self.my_twin.press_pause()

        self.playButton.setHidden(False)
        self.pauseButton.setHidden(True)

    @pyqtSlot()
    def press_stop(self):
        self.my_twin.press_stop()
        self.playButton.setHidden(False)
        self.pauseButton.setHidden(True)

    @pyqtSlot()
    def press_checked(self):
        if self.isCheckedState == False:
            self.isCheckedState = True
            self._CheckButton.setChecked(True)
        else:
            self.isCheckedState = False
            self._CheckButton.setChecked(False)


    @pyqtSlot(int)
    def TitleActivated(self, index):
        if self._Title.itemData(index) == "name":
            pass
        elif self._Title.itemData(index) == "url":
            self.makeUrlEditableSlot()
        elif self._Title.itemData(index) == "folder":
            self.makeFolderEditableSlot()
        elif self._Title.itemData(index) == "outtmpl":
            self.makeOuttmplEditableSlot()
        elif self._Title.itemData(index) == "format":
            self.makeFormatEditableSlot()
        elif self._Title.itemData(index) == "quality":
            self.makeQualityEditableSlot()


    @pyqtSlot()
    def openFolder(self):
        #print(self._FolderEdit.text())
        for x in range(self._Title.count()):
            if self._Title.itemData(x) == "folder":
                try:
                    subprocess.Popen(['dolphin', self._Title.itemText(x)])
                except:
                    print("couldn't open filebrowser")
    @pyqtSlot()
    def makeUrlEditableSlot(self):
        self._Title.setHidden(True)
        self._FolderEdit.setHidden(True)
        self._OuttmplEdit.setHidden(True)
        self.formatSelect.setHidden(True)
        self.sliderBox.setHidden(True)

        self._UrlEdit.setHidden(False)
        self._UrlEdit.setFocus(True)
        self._UrlEdit.setText(self._Title.currentText())

    @pyqtSlot()
    def makeFolderEditableSlot(self):
        self._Title.setHidden(True)
        self._UrlEdit.setHidden(True)
        self._OuttmplEdit.setHidden(True)
        self.formatSelect.setHidden(True)
        self.sliderBox.setHidden(True)

        self._FolderEdit.setHidden(False)
        self._FolderEdit.setFocus(True)
        self._FolderEdit.setText(self._Title.currentText())

    @pyqtSlot()
    def makeOuttmplEditableSlot(self):
        self._Title.setHidden(True)
        self._UrlEdit.setHidden(True)
        self._FolderEdit.setHidden(True)
        self.formatSelect.setHidden(True)
        self.sliderBox.setHidden(True)


        self._OuttmplEdit.setHidden(False)
        self._OuttmplEdit.setFocus(True)
        self._OuttmplEdit.setText(self._Title.currentText())

    @pyqtSlot()
    def makeFormatEditableSlot(self):
        self._Title.setHidden(True)
        self._UrlEdit.setHidden(True)
        self._FolderEdit.setHidden(True)
        self._OuttmplEdit.setHidden(True)
        self.sliderBox.setHidden(True)

        self.formatSelect.setHidden(False)
        self.formatSelect.setFocus(True)
        self.formatSelect.showPopup()

    @pyqtSlot()
    def makeQualityEditableSlot(self):
        self._Title.setHidden(True)
        self._UrlEdit.setHidden(True)
        self._FolderEdit.setHidden(True)
        self._OuttmplEdit.setHidden(True)
        self.formatSelect.setHidden(True)

        self.sliderBox.setHidden(False)
        self.audioQualitySlider.setFocus(True)

    @pyqtSlot(int)
    def updateSliderLabel(self, new_value):
        self.sliderLabel.setText(self.invertValue(new_value))

    @pyqtSlot(int)
    def handleSliderChange(self, new_value):
        self.qualityUpdatedSignal.emit(new_value)

    @pyqtSlot()
    def handleFormatChange(self):
        current_index = self.formatSelect.currentIndex()
        self.formatUpdatedSignal.emit(current_index)

    @pyqtSlot()
    def finishedFormatSelect(self):
        self._UrlEdit.setHidden(True)
        self._FolderEdit.setHidden(True)
        self.formatSelect.setHidden(True)
        self._OuttmplEdit.setHidden(True)
        self.sliderBox.setHidden(True)

        self._Title.setHidden(False)
        self._Title.setCurrentIndex(0)

    @pyqtSlot()
    def finishedQualitySelect(self):
        self._UrlEdit.setHidden(True)
        self._FolderEdit.setHidden(True)
        self.formatSelect.setHidden(True)
        self._OuttmplEdit.setHidden(True)
        self.sliderBox.setHidden(True)
        self.handleSliderChange(self.audioQualitySlider.value())

        self._Title.setHidden(False)


    @pyqtSlot()
    def finishedEditSlot(self):
#  CONSIDER AND CHANGE COMBOBOX VALUES ------------------------------

        for x in range(self._Title.count()):
            if self._Title.itemData(x) == "url" and not self._UrlEdit.isHidden():
                if self.validateUrl(self._UrlEdit.text()):
                    self.urlUpdatedSignal.emit(self._UrlEdit.text())
                    self._Title.setItemText(x, self._UrlEdit.text())

            elif self._Title.itemData(x) == "folder" and not self._FolderEdit.isHidden():
                self._Title.setItemText(x, self._FolderEdit.text())
                self.folderUpdatedSignal.emit(self._FolderEdit.text())

            elif self._Title.itemData(x) == "outtmpl" and not self._OuttmplEdit.isHidden():
                if self._OuttmplEdit.text() != '':
                    self._Title.setItemText(x, self._OuttmplEdit.text())
                    self.outtmplUpdatedSignal.emit(self._OuttmplEdit.text())


        self._Title.setHidden(False)
        self._UrlEdit.setHidden(True)
        self._FolderEdit.setHidden(True)
        self._OuttmplEdit.setHidden(True)
        self.sliderBox.setHidden(True)

# -------------------------------------------------------------------

    def validateUrl(self, url):

        regex = re.compile(
                r'^(?:http|ftp)s?://' # http:// or https://
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
                r'localhost|' #localhost...
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
                r'(?::\d+)?' # optional port
                r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        if not re.match(regex, url):
            print(url)
            print("nope")
            return False
        else:
            return True


    @pyqtSlot(int)
    def handleValueChangedProgress(self, value):
        #pass
        if value == self._Progress.maximum():
            self.playButton.setHidden(False)
            self.pauseButton.setHidden(True)
            self._Progress.setFormat("  ✔  "+self._Title.itemText(0))
            self._Progress.setStyleSheet(
            """
                QProgressBar {
                    color: #ffffff;
                    text-align: left center;
                    background-color: rgba(255, 255, 255, 0); /* set transparent */
                }

                QProgressBar:chunk {
                    background: #3a7000;
                }
            """
            )

    @pyqtSlot(str)
    def set_new_url(self, url):
        self._Url = url
        self._Progress.setFormat("      "+self._Title.itemText(0)+"    ")
        self._Progress.setToolTip(url)
        #self._Title.clear()
        #self._Title.insertItem(1, url)
        self.updateToolTip()

    @pyqtSlot(str)
    def gotNameSlot(self, myName):
        self._Title.insertItem(0, myName,         "name")
        self._Title.setCurrentIndex(0)


    @pyqtSlot(int)
    def invertValue(self,value):
        value = self.audioQualitySlider.value()
        lst = [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
        index = [x for x in range(len(lst)) if lst[x] == value]
        return str(index[0])

    @pyqtSlot(list)
    def gotInfoSlot(self, info):
        self.playButton.setHidden(False)
        self.pauseButton.setHidden(True)
        self._Title.clear()
        mystr = ""
        print("len info: "+str(len(info)))
        for i in info:
            print(i)
        if len(info) == 5:
            self._Title.insertItem(0, info[0], "url" )
            self._Title.insertItem(1, info[1], "folder" )
            self._Title.insertItem(2, info[2], "outtmpl" )
            self._Title.insertItem(3, info[3], "format" )
            self._Title.insertItem(4, info[4], "quality" )

            mystr = info[0]+"\n"+info[1]+"\n"+info[2]+"\n"+info[3]+"\n"+info[4]

        elif len(info) == 6:
            self._Title.insertItem(0, info[0], "name")
            self._Title.insertItem(1, info[1], "url")
            self._Title.insertItem(2, info[2], "folder")
            self._Title.insertItem(3, info[3], "outtmpl")
            self._Title.insertItem(4, info[4], "format")
            self._Title.insertItem(5, info[5], "quality" )
            mystr = info[0]+"\n"+info[1]+"\n"+info[2]+"\n"+info[3]+"\n"+info[4]+"\n"+info[5]


        self._Title.setToolTip(mystr)

    @pyqtSlot(int)
    def progressTotal(self, recieved_progressTotal):
        self.playButton.setHidden(True)
        self.pauseButton.setHidden(False)
        self._Title.setHidden(True)
        self._Progress.setHidden(False)
        self._Progress.setMaximum(recieved_progressTotal)
        self._Progress.setFormat("  "+self._Title.itemText(0)+"  ")
        self._Progress.setStyleSheet(
        """
            QProgressBar {
                color: #ffffff;
                text-align: left center;
                background-color: rgba(255, 255, 255, 0); /* set transparent */
            }

            QProgressBar:chunk {
                background-color: #005841;
                opacity: .9;
            }
        """
        )


    @pyqtSlot(int)
    def progressValue(self, recieved_progressTotal):
        self._Title.setHidden(True)
        self._Progress.setHidden(False)
        self._Progress.setValue(recieved_progressTotal)



    def updateToolTip(self):
        if len(self._TitleList) == 0:
            self._Progress.setToolTip(self._Url)
# —————————————————————————————————————————————————————————

# SUBCLASSES AND OVERLOADS ————————————————————————————————

class MyProgress(QProgressBar):
    doubleClickSignal = pyqtSignal()
    def __init__(self, scrollWidget=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def mousePressEvent(self, e):
        super(MyProgress, self).mousePressEvent(e)
        e.ignore()

    def mouseDoubleClickEvent(self, e):
        if e.button() == 1:
            self.doubleClickSignal.emit()


# ----------------------------------------------

class MyQFormatBox(QComboBox):
    clickedSignal = pyqtSignal()
    finishedEditSignal = pyqtSignal()
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def keyPressEvent(self, e):
        key = e.key()
        if key == Qt.Key_Return:
            self.finishedEditSignal.emit()
        elif key == Qt.Key_Escape:
            self.finishedEditSignal.emit()
        super(MyQFormatBox, self).keyPressEvent(e)
        e.accept()

# ----------------------------------------------




# ------------------------------------------

class MyQSlider(QSlider):
    clickedSignal = pyqtSignal()
    finishedEditSignal = pyqtSignal()
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Return:
            self.finishedEditSignal.emit()
        elif key == Qt.Key_Escape:
            self.finishedEditSignal.emit()
        event.accept()

# ------------------------------------------

class MyQComboBox(QComboBox):
    clickedSignal = pyqtSignal()
    editableUrlSignal = pyqtSignal()
    editableFolderSignal = pyqtSignal()
    editableOuttmplSignal = pyqtSignal()
    editableFormatSignal = pyqtSignal()
    editableQualitySignal = pyqtSignal()
    editNameSignal = pyqtSignal()
    finishedEditSignal = pyqtSignal()
    def __init__(self, scrollWidget=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #print(self)
        self.scrollWidget=scrollWidget
        self.editableFlag = False
        self.setFocusPolicy(Qt.StrongFocus)


    def mousePressEvent(self, e):
        #self.getSizesSignal.emit()

        if e.button() == 1:
            self.editableFlag = False
            self.setEditable(False)
            super(MyQComboBox, self).mousePressEvent(e)

        if e.button() == 2:
           super(MyQComboBox, self).showPopup()
           super(MyQComboBox, self).mousePressEvent(e)

        else:
            #self.showPopup()
            #self.clickedSignal.emit()

            super().mousePressEvent(e)
        e.accept()


    def mouseDoubleClickEvent(self, e):
        #self.getSizesSignal.emit()

        if e.button() == 1:

            super(MyQComboBox, self).showPopup()

        e.accept()



    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Down:
            event.ignore()
        if key == Qt.Key_Up:
            event.ignore()


    def showPopup(self):
        self.clickedSignal.emit()

    def wheelEvent(self, *args, **kwargs):
        if self.hasFocus():
            #return QComboBox.wheelEvent(self, *args, **kwargs)
            pass
        else:
            pass
            #return self.scrollWidget.wheelEvent(*args, **kwargs)




    #def focusOutEvent(self, e):
        #if e.button() != 2:
            #self.editableFlag = False
            #self.setEditable(False)
        #super(MyQComboBox, self).focusOutEvent(e)


