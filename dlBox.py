#!/bin/env python3
# ———————————————————————————————————————————

import os, sys, signal, re, time

# -------------------------------------------
from PyQt5.QtGui import     (
                            QTextCursor,
                            QIcon,
                            QFont,
                            QKeySequence,
                            )
# -------------------------------------------
from PyQt5.QtCore import    (
                            Qt,
                            QDir,
                            QUrl,
                            QEvent,
                            pyqtSlot,
                            pyqtSignal,
                            QTimer,
                            )
# -------------------------------------------
from PyQt5.QtWidgets import (
                            QVBoxLayout,
                            QHBoxLayout,
                            QGridLayout,
                            QGroupBox,
                            QButtonGroup,
                            QWidget,
                            QPushButton,
                            QPlainTextEdit,
                            QLabel,
                            QLineEdit,
                            QListWidget,
                            QScrollArea,
                            QShortcut,
                            QSizePolicy,
                            QComboBox,
                            QFrame,
                            QFileDialog,
                            QScrollArea,
                            QScrollBar,
                            QSlider,
                            QStyle,
                            QToolBar,
                            QMenuBar,
                            QCheckBox,
                            QMessageBox,
                            QProgressBar,
                            )
# -------------------------------------------
from worker import          (
                            Worker
                            )
# -------------------------------------------
from workerMeta import      (
                            WorkerMeta
                            )

# ———————————————————————————————————————————


#                            ⌫ 🗒 🗊 🖈 📦 

class myDowloadWidget(QWidget):
    resizeSignal = pyqtSignal()
    clickedSignal = pyqtSignal()
    clickedCheckSignal = pyqtSignal()
    gotNameSignal = pyqtSignal(str)
    gotInfoSignal = pyqtSignal(list)
    updatePathSignal = pyqtSignal(str)
    updateOuttmplSignal = pyqtSignal(str)
    updateUrlSignal = pyqtSignal(str)
    droppedUrlSignal = pyqtSignal(str)
    progressTotalSignal = pyqtSignal(int)
    progressValueSignal = pyqtSignal(int)
    changeSmallSliderSignal = pyqtSignal(int)
    def __init__(self, numAddWidget, url):
        QGroupBox.__init__(self)
        self.init_download_options()
        self.setAcceptDrops(True)
        self.worker = Worker()
        self.workerMeta = WorkerMeta()
        self.url = url
        self.my_twin = None
        #self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Preferred)
        #print(self.my_twin)
        self.mytimer = QTimer()
        self.init_raised_variables()
        self.myTitle = "{}".format(self.url)
        self.setStyleSheet(
        """
                    QToolTip{
                        border: 0px;
                        font-size: 13px;
                    }
        """
        )

        #self.setStyleSheet(
        #"""
            #QFileDialog {
                #background-color: #585858;
            #}
        #"""
        #)

################# CHECK IF ARGUMENT URL IS VALID URL #####################
        regex = re.compile(
                r'^(?:http|ftp)s?://' # http:// or https://
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
                r'localhost|' #localhost...
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
                r'(?::\d+)?' # optional port
                r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        if re.match(regex, url):
            self.getMeta()
###########################################################################

        self.numAddWidget = numAddWidget
        self.titleStorage = []
        self.path = None
        self.paused = 0
        self.init_dl_gui()
        self.organize()
        self.init_connections()
        self.setDefaultParentFolder()

# RAISED VARIABLES - USED AS BUFFERS
    @pyqtSlot()
    def init_raised_variables(self):
        self.isCheckedState = False
        self.myCheckMenuFlag = False
        self.currentUrlBuffer = False



# SETUP DOWNLOAD OPTIONS --------------

    def init_download_options(self):
        self.my_outtmpl = None
        self.default_outtmpl = '%(uploader)s/%(playlist)s/%(title)s [%(id)s].%(ext)s'
        self.meta_outtmpl = '%(title)s'


# -------------------------------------

#   SETUP GUI COMPONENTS ————————————————————————

    def init_dl_gui(self):

        self.dl_gui_TextLog = MyTextEdit()
        self.dl_gui_TextLog.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.dl_gui_TextLog.setStyleSheet(
        """
            QPlainTextEdit {
                padding: 1px;
                background-color: transparent;
            }
            QScrollBar:vertical {
                width: 2px;
                background-color: rgba(255,255,255,0);
            }
             QScrollBar::handle:vertical {
                background-color: green;         /* #605F5F; */
                min-height: 5px;
                border-radius: 4px;
            }

        """
        )

        self.dl_gui_TotalProgress = QProgressBar(self)
        self.dl_gui_TotalProgress.setAlignment(Qt.AlignCenter)
        self.dl_gui_TotalProgress.setTextVisible(False)
        self.dl_gui_TotalProgress.setStyleSheet(
        """
            QProgressBar {
            max-height: 2px;
            background-color: rgba(255, 255, 255, 0); /* set transparent */
            opacity: .4;


            }

            QProgressBar:chunk {
            background: #005841;
            opacity: 1000;
            }
        """
        )


        self.dl_gui_Title = MyQComboBox(self)
        self.dl_gui_Title.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.dl_gui_Title.setStyleSheet(
        """

            QComboBox {
                border: 0;
                padding-left: 1px;
                background-color: transparent;
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

        self.dl_gui_Title.addItem(self.url)
        #self.dl_gui_Title.setSizePolicy(
                        #QSizePolicy.Preferred,
                        #QSizePolicy.Expanding
        #)
        ##self.dl_gui_Title = QLabel(self.url)


        self.dl_gui_ToolButton = QPushButton("")
        self.dl_gui_ToolButton.setCheckable(True)
        self.dl_gui_ToolButton.setToolTip("Show/Hide settings")
        self.dl_gui_ToolButton.setStyleSheet(
        """
                    QToolTip{
                        border: 0;
                        font-size: 13px;
                    }
                    QPushButton {
                        font-size: 14px;
                        min-width: 15px;
                        max-height: 23px;
                        border-style: solid;
                        border-color: transparent;
                        background-color: transparent;
                    }
                    QPushButton:checked {
                        border-top-width: 1px;
                        border-style: groove;
                        border-color: #55aa7f;
                    }

        """
        )

        self.dl_gui_ToolBar = QWidget(self)
        #self.dl_gui_ToolBar = QToolBar(self)

        self.dl_gui_ToolBarGroup = QButtonGroup(self)
        #self.dl_gui_ToolBar.addAction(self.dl_gui_ParentFolderEdit)
        #self.dl_gui_ToolBar.setHidden(True)


        # BUTTONS IN TEXTLOG AND CONTROLS-FRAME
        self.dl_gui_ButtonDownload = QPushButton("")
        self.dl_gui_ButtonDownload.setToolTip("Start download")
        #self.dl_gui_ButtonDownload.setSizePolicy(
                        #QSizePolicy.Preferred,
                        #QSizePolicy.Expanding
        #)

        self.dl_gui_ButtonStop = QPushButton("")
        self.dl_gui_ButtonStop.setHidden(True)
        self.dl_gui_ButtonStop.setToolTip("Stop download")
        self.dl_gui_ButtonStop.setSizePolicy(
                        QSizePolicy.Preferred,
                        QSizePolicy.Expanding
        )

        self.dl_gui_ButtonPause = QPushButton("")
        self.dl_gui_ButtonPause.setHidden(True)
        self.dl_gui_ButtonPause.setToolTip("Pause download")
        self.dl_gui_ButtonPause.setSizePolicy(
                        QSizePolicy.Preferred,
                        QSizePolicy.Expanding
        )

        self.dl_gui_ButtonClearSelf = QPushButton("")
        self.dl_gui_ButtonClearSelf.setToolTip("Clear log and clean up ui")
        self.dl_gui_ButtonClearSelf.setHidden(True)
        self.dl_gui_ButtonClearSelf.setSizePolicy(
                        QSizePolicy.Preferred,
                        QSizePolicy.Expanding
        )

# BEGIN BUILD BOXES AND LAYOUTS -------------------------------

# DOWNLOAD INFO AND CONTROLS ---


# FOLDER + URL + OUTTMPL BUTTONS ----------------

        # BUTTONS IN (hidden) CHOICE MENU
        self.folderButtonToolbar = QPushButton("") # FOLDER BUTTON
        self.folderButtonToolbar.setCheckable(True)

        self.settingsButtonTool = QPushButton("") #URLS BUTTON
        self.settingsButtonTool.setCheckable(True)

# ------------------------------------------------

# ---
        #   BUILD (hidden) TOOLBAR BUTTONSBOX/CHOICE MENU
        toolBarLayout = QHBoxLayout()
        self.dl_gui_ToolBarGroup.addButton(self.folderButtonToolbar)
        #self.dl_gui_ToolBarGroup.addButton(self.settingsButtonTool)
        self.dl_gui_ToolBarGroup.addButton(self.settingsButtonTool)    #   ADD BUTTONS TO THE QBUTTONGROUP
        #toolBarLayout.addWidget(self.settingsButtonTool)                  #   AND THE (hidden) CHOICE MENU LAYOUT
        toolBarLayout.addWidget(self.settingsButtonTool)
        toolBarLayout.addWidget(self.folderButtonToolbar)
        toolBarLayout.setSpacing(10)
        toolBarLayout.setAlignment(Qt.AlignCenter)
        toolBarLayout.setContentsMargins(0, 0, 10, 0 )
        toolBarLayout.setAlignment(Qt.AlignTop)
        self.dl_gui_ToolBar.setLayout(toolBarLayout)
        self.dl_gui_ToolBar.setHidden(True)
        self.dl_gui_ToolBar.setStyleSheet(
        """

                    QPushButton {
                        font-size: 14px;
                        min-width: 15px;
                        max-height: 23px;
                        border: 0;
                        background-color: transparent;
                    }
                    QPushButton:checked {
                        background-color: transparent;
                        border-top-width: 1px;
                        border-style: groove;
                        border-color: #55aa7f;
                    }


        """
        )
        self.dl_gui_IsCheckedStateButton = QPushButton()
        self.dl_gui_IsCheckedStateButton.setToolTip("Click to set as checked")
        self.dl_gui_IsCheckedStateButton.setCheckable(True)
        self.dl_gui_IsCheckedStateButton.setStyleSheet(
        """
                QPushButton {
                    background-color: transparent;
                    padding: 3px;
                    margin-top: 4px;
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
        # BUILD TOPBAR: TITLE + TOOLBAR (starts hidden) + TOOLBUTTON


        self.urlEditClone = MyLineEditTitle(self)
        self.urlEditClone.setHidden(True)
        self.folderEditClone = MyLineEditTitle(self)
        self.folderEditClone.setHidden(True)
        self.outtmplEditClone = MyLineEditTitle(self)
        self.outtmplEditClone.setHidden(True)

        self.qualityEditClone = MySlider(self)
        self.qualityEditClone.setHidden(True)
        self.qualityEditClone.setHidden(True)

        self.qualityEditClone.setMinimum(0)
        self.qualityEditClone.setMaximum(9)
        self.qualityEditClone.setOrientation(Qt.Horizontal)
        self.qualityEditClone.setValue(0)

        self.titleBox = QWidget(self)
        titleLay = QVBoxLayout()
        titleLay.addWidget(self.qualityEditClone)
        titleLay.addWidget(self.urlEditClone)
        titleLay.addWidget(self.folderEditClone)
        titleLay.addWidget(self.outtmplEditClone)
        titleLay.setAlignment(Qt.AlignTop)
        titleLay.setContentsMargins(0, 0, 0, 0 )
        titleLay.setSpacing(0)
        self.titleBox.setLayout(titleLay)
        self.titleBox.setStyleSheet(
        """
                QSlider::groove:horizontal {
                    border: 0px;
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #000000, stop:1 #008b66);
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
                QPushButton {
                    font-size: 15px;
                    border: 0;
                    background-color: transparent;
                }

                QLineEdit {
                    border: 0 transparent;
                    background: transparent;
                    color: white;
                }

                QLineEdit:active {
                    background: transparent;
                    color: white;
                }
        """
        )

        self.titleToolBox = QWidget(self)
        titleToolBoxLayout = QHBoxLayout()
        titleToolBoxLayout.addWidget(self.dl_gui_Title)
        titleToolBoxLayout.addWidget(self.titleBox)
        titleToolBoxLayout.addWidget(self.dl_gui_ToolBar)
        titleToolBoxLayout.addWidget(self.dl_gui_ToolButton, alignment=Qt.AlignTop)
        titleToolBoxLayout.addWidget(self.dl_gui_IsCheckedStateButton, alignment=Qt.AlignTop)
        titleToolBoxLayout.setContentsMargins(0, 2, 3, 0 )
        titleToolBoxLayout.setAlignment(Qt.AlignRight)
        #titleToolBoxLayout.setColumnStretch(0,4)
        #titleToolBoxLayout.setColumnStretch(1,4)
        self.titleToolBox.setLayout(titleToolBoxLayout)
# ---

# BUILD FOLDER CHOICE SUBMENU ---
        self.folderSelectButton = QPushButton("") # Select Folder Button
        self.folderSelectButton.setMinimumWidth(20)
        self.folderSelectButton.setToolTip("Click to find a folder")
        self.folderSelectButton.setStyleSheet(
        """
                QPushButton {
                    font-size: 15px;
                    border: 0;
                    background-color: transparent;
                }

        """
        )

        self.folderSelectButton.clicked.connect(self.press_parentfolder)
        self.folderSelectButton.clicked.connect(lambda: self.clickedSignal.emit())
        self.folderLineEdit = MyLineEdit(self)
        self.folderLineEdit.setStyleSheet(
        """
                QLineEdit {
                    border: 0 transparent;
                    background-color: transparent;
                    color: white;
                }

        """
        )
        self.folderLineEdit.textChanged.connect(self.folderValueChanged)




# FOLDER ADDED LABEL
        self.droppedFolderLabel = QLabel(self.folderLineEdit.text())
        self.droppedFolderLabel.setHidden(True)
        self.droppedFolderLabel.setHidden(True)


# BUILD OUTTMPL CHOICE SUBMENU ---

        self.outtmplLineEdit = MyLineEdit(self)
        self.outtmplLineEdit.setText(self.default_outtmpl)
        self.outtmplLineEdit.textChanged.connect(self.outtmplValueChanged)
        #self.outtmplLineEdit.hasFocus.connect(lambda: self.clickedSignal.emit())

        self.outtmplLineEdit.setToolTip(self.outtmplLineEdit.text())
        self.outtmplLineEdit.setStyleSheet(
        """
                QLineEdit {
                    border: 0 transparent;
                    background-color: transparent;
                    color: white;
                }

        """
        )

        self.outtmplHelpButton = QPushButton("?")
        self.outtmplHelpButton.setMinimumWidth(20)
        self.outtmplHelpButton.setToolTip("What the hell is this?\nClick here for instructions")
        self.outtmplHelpButton.setStyleSheet(
        """
                QPushButton {
                    font-size: 15px;
                    font: bold;
                    border: 0px;
                    background-color: transparent;
                }

        """
        )
        self.outtmplHelpButton.clicked.connect(self.showHelp)
        self.outtmplHelpButton.clicked.connect(lambda: self.clickedSignal.emit())

        self.outtmplSelectButton = QPushButton("Set outtmpl")
        self.outtmplSelectButton.setToolTip("Make sure you're sure...\nhttps://github.com/yt-dlp/yt-dlp#output-template")
        self.outtmplSelectButton.clicked.connect(lambda: self.setOuttmpl(self.outtmplLineEdit.text()))
        self.outtmplSelectButton.setHidden(True)
        self.outtmplSelectButton.setStyleSheet(
        """
            QToolTip{
                border: 0px;
                font-size: 15px;
            }
        """
        )

        self.settingsMenu = MyFolderFrame(self)

        self.saveAsLabel = QPushButton("Save as:")
        self.saveAsLabel.setStyleSheet("""
                QPushButton {
                    padding-right: 5px;
                    border: 0;
                    background-color: transparent;
                }
        """)
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

        self.audioQualitySlider = QSlider()
        self.audioQualitySlider.setMinimum(0)
        self.audioQualitySlider.setMaximum(9)
        self.audioQualitySlider.setOrientation(Qt.Horizontal)
        self.audioQualitySlider.setValue(9)
        self.audioQualitySlider.setStyleSheet(
        """
                QSlider::groove:horizontal {
                    border: 0px;
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #000000, stop:1 #008b66);
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

        self.sliderLabel = QLabel("Audio quality: "+self.labelInvertvalue())

        self.checkGroup = QWidget(self)

        #self.checkOverwrite = QCheckBox("")
        self.checkOverwrite = QCheckBox()
        #self.checkOverwriteFlag = 0
        self.checkOverwrite.setTristate(True)

        self.checkOverwrite.setToolTip("Do not overwrite any files - setting does not affect metadata")
        self.checkOverwrite.clicked.connect(self.checkOverwriteClicked)
        self.checkOverwrite.clicked.connect(self.update_dl_gui_ToolTips)
        self.checkOverwrite.setStyleSheet(
        """
            QCheckBox::indicator {
                background: #4c996e;
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
                background: #c60003;
                margin: 1px;
                border-width: 1px;
                border-style: solid;
                border-radius: 6px;
            }
        """
        )

        #self.checkThumbnails = QCheckBox("")
        self.checkThumbnails = QCheckBox()
        #self.checkThumbnailsFlag = 0
        self.checkThumbnails.clicked.connect(self.checkThumbnailsClicked)
        self.checkThumbnails.clicked.connect(self.update_dl_gui_ToolTips)
        self.checkThumbnails.setToolTip("Embed thumbnails, do not write image-file\n\nNote:\nogg and wav will write an image-file since they don't support embedding")
        self.checkThumbnails.setTristate(True)
        self.checkThumbnails.setStyleSheet(
        """
            QCheckBox::indicator {
                background: #4c996e;
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
                background: #2f2f46;
                margin: 1px;
                border-width: 1px;
                border-style: solid;
                border-radius: 6px;
            }
        """
        )

        #self.checkMetaEmbed = QCheckBox("")
        self.checkMetaEmbed = QCheckBox()
        #self.checkMetaEmbedFlag = 0
        self.checkMetaEmbed.clicked.connect(self.checkEmbedMetaClicked)
        self.checkMetaEmbed.clicked.connect(self.update_dl_gui_ToolTips)
        self.checkMetaEmbed.setToolTip("Embed metadata and overwrite metadata for existing files")
        self.checkMetaEmbed.setTristate(True)
        self.checkMetaEmbed.setStyleSheet(
        """
            QCheckBox::indicator {
                background: #4c996e;
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
                background: #2f2f46;
                margin: 1px;
                border-width: 1px;
                border-style: solid;
                border-radius: 6px;
            }
        """
        )

        self.checkOverwriteClone = QCheckBox()
        #self.checkOverwriteFlag = 0
        self.checkOverwriteClone.setTristate(True)
        self.checkOverwriteClone.setToolTip("Do not overwrite any files - setting does not affect metadata")
        self.checkOverwriteClone.clicked.connect(lambda:self.checkOverwrite.setCheckState(self.checkOverwriteClone.checkState()))
        self.checkOverwriteClone.clicked.connect(self.checkOverwriteClicked)
        self.checkOverwriteClone.clicked.connect(self.update_dl_gui_ToolTips)
        self.checkOverwriteClone.setStyleSheet(
        """
            QCheckBox::indicator {
                background: #4c996e;
                margin: 1px;
                min-height: 10px;
                min-width: 10px;
                border-color: #4c996e;
                border-width: 1px;
                border-style: solid;
                border-radius: 6px;
            }
            QCheckBox::indicator:indeterminate {
                background: #0073ac;
                margin: 1px;
                min-height: 10px;
                min-width: 10px;
                border-color: #0073ac;
                border-width: 1px;
                border-style: solid;
                border-radius: 6px;
            }
            QCheckBox::indicator:checked {
                background: #c50407;
                margin: 1px;
                min-height: 10px;
                min-width: 10px;
                border-color: #c50407;
                border-width: 1px;
                border-style: solid;
                border-radius: 6px;
            }
        """
        )


        #self.checkThumbnails = QCheckBox("")
        self.checkThumbnailsClone = QCheckBox()
        self.checkThumbnailsClone.clicked.connect(lambda:self.checkThumbnails.setCheckState(self.checkThumbnailsClone.checkState()))
        self.checkThumbnailsClone.clicked.connect(self.checkThumbnailsClicked)
        self.checkThumbnailsClone.clicked.connect(self.update_dl_gui_ToolTips)
        self.checkThumbnailsClone.setToolTip("Embed thumbnails, do not write image-file\n\nNote:\nogg and wav will write an image-file since they don't support embedding")
        self.checkThumbnailsClone.setTristate(True)
        self.checkThumbnailsClone.setStyleSheet(
        """
            QCheckBox::indicator {
                background: #4c996e;
                margin: 1px;
                min-height: 10px;
                min-width: 10px;
                border-color: #4c996e;
                border-width: 1px;
                border-style: solid;
                border-radius: 6px;
            }
            QCheckBox::indicator:indeterminate {
                background: #0073ac;
                margin: 1px;
                min-height: 10px;
                min-width: 10px;
                border-color: #0073ac;
                border-width: 1px;
                border-style: solid;
                border-radius: 6px;
            }
            QCheckBox::indicator:checked {
                background: transparent;
                margin: 1px;
                min-height: 10px;
                min-width: 10px;
                border-color: #4c996e;
                border-width: 1px;
                border-style: solid;
                border-radius: 6px;
            }
        """
        )

        #self.checkMetaEmbed = QCheckBox("")
        self.checkMetaEmbedClone = QCheckBox()
        self.checkMetaEmbedClone.clicked.connect(lambda:self.checkMetaEmbed.setCheckState(self.checkMetaEmbedClone.checkState()))
        self.checkMetaEmbedClone.clicked.connect(self.checkEmbedMetaClicked)
        self.checkMetaEmbedClone.clicked.connect(self.update_dl_gui_ToolTips)
        self.checkMetaEmbedClone.setToolTip("Embed metadata and overwrite metadata for existing files")

        self.checkMetaEmbedClone.setTristate(True)
        self.checkMetaEmbedClone.setStyleSheet(
        """
            QCheckBox::indicator {
                background: #4c996e;
                margin: 1px;
                min-height: 10px;
                min-width: 10px;
                border-color: #4c996e;
                border-width: 1px;
                border-style: solid;
                border-radius: 6px;
            }
            QCheckBox::indicator:indeterminate {
                background: #0073ac;
                margin: 1px;
                min-height: 10px;
                min-width: 10px;
                border-color: #0073ac;
                border-width: 1px;
                border-style: solid;
                border-radius: 6px;
            }
            QCheckBox::indicator:checked {
                background: transparent;
                margin: 1px;
                min-height: 10px;
                min-width: 10px;
                border-color: #4c996e;
                border-width: 1px;
                border-style: solid;
                border-radius: 6px;
            }
        """
        )


        checkGroupLayout = QHBoxLayout()
        checkGroupLayout.addWidget(self.checkOverwrite)
        checkGroupLayout.addWidget(self.checkThumbnails)
        checkGroupLayout.addWidget(self.checkMetaEmbed)
        checkGroupLayout.setAlignment(Qt.AlignCenter)
        self.checkGroup.setLayout(checkGroupLayout)

        self.checkGroupClone = QWidget(self)
        checkGroupCloneLayout = QHBoxLayout()
        checkGroupCloneLayout.addWidget(self.checkOverwriteClone)
        checkGroupCloneLayout.addWidget(self.checkThumbnailsClone)
        checkGroupCloneLayout.addWidget(self.checkMetaEmbedClone)
        checkGroupCloneLayout.setAlignment(Qt.AlignCenter)
        checkGroupCloneLayout.setContentsMargins(0,0,0,0)
        checkGroupCloneLayout.setSpacing(0)
        checkGroupCloneLayout.setAlignment(Qt.AlignCenter)
        self.checkGroupClone.setLayout(checkGroupCloneLayout)



  #BUILD BUTTONSGROUP/CONTROLS-BOX
        self.buttonsGroup = QWidget(self)

        self.formatSelectClone = MyQFormatBox(self)

        subLay = QVBoxLayout()
        subLay.addWidget(self.formatSelectClone, alignment=Qt.AlignTop)
        subLay.addWidget(self.checkGroupClone,alignment=Qt.AlignTop)
        subLay.addSpacing(5)
        subLay.addWidget(self.dl_gui_ButtonDownload, alignment=Qt.AlignTop)
        subLay.addWidget(self.dl_gui_ButtonStop, alignment=Qt.AlignTop)
        subLay.addWidget(self.dl_gui_ButtonPause, alignment=Qt.AlignTop)
        subLay.addWidget(self.dl_gui_ButtonClearSelf, alignment=Qt.AlignTop)
        subLay.addStretch()
        subLay.setContentsMargins(0, 2, 0 ,0 )
        #subLay.setContentsMargins(-1, 0, -1, -1)
        self.buttonsGroup.setLayout(subLay)
        self.buttonsGroup.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.buttonsGroup.setStyleSheet(
        """
                QPushButton:pressed {
                    color: #33674b;
                }
                QPushButton {
                        font-size: 30px;
                        min-width: 50px;
                        border: 0;
                        background-color: transparent;
                }
                QComboBox {
                    border: 0;
                    padding-left: 1px;
                    background-color: transparent;
                    margin: 1px;
                }

        """
        )

        #   BUILD LOG AND CONTROLS BOX
        self.logAndButtonsBox = QWidget()

        logAndButtonsBoxLayout = QHBoxLayout()
        logAndButtonsBoxLayout.addWidget(self.dl_gui_TextLog, alignment=Qt.AlignTop)
        logAndButtonsBoxLayout.addWidget(self.buttonsGroup)
        #logAndButtonsBoxLayout.setSpacing(0)
        logAndButtonsBoxLayout.setContentsMargins(0, 0, 0, 5)
        self.logAndButtonsBox.setLayout(logAndButtonsBoxLayout)
        #self.logAndButtonsBox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
# ---



        self.saveBox = QWidget()
        saveBoxLayout = QGridLayout()
        saveBoxLayout.addWidget(self.checkGroup, 0,0, alignment=Qt.AlignLeft)
        saveBoxLayout.addWidget(self.saveAsLabel, 0,1, alignment=Qt.AlignRight)
        saveBoxLayout.addWidget(self.formatSelect, 0,2 ,alignment=Qt.AlignRight)
        saveBoxLayout.setContentsMargins(0, 0, 0, 0 )
        saveBoxLayout.setColumnStretch(0,2)
        saveBoxLayout.setSpacing(0)
        self.saveBox.setLayout(saveBoxLayout)

        self.qualityBox = QWidget()
        qualityLayout =  QHBoxLayout()
        qualityLayout.addWidget(self.sliderLabel)
        qualityLayout.addWidget(self.audioQualitySlider)
        qualityLayout.setContentsMargins(5, 0, 0, 0 )
        self.qualityBox.setLayout(qualityLayout)

        settingsMenuLayout = QVBoxLayout()
        #settingsMenuLayout.addWidget(self.checkGroup, alignment=Qt.AlignRight)
        settingsMenuLayout.addWidget(self.qualityBox)
        settingsMenuLayout.addWidget(self.saveBox)

        settingsMenuLayout.setContentsMargins(0, 10, 0, 0 )
        settingsMenuLayout.setSpacing(0)
        self.settingsMenu.setLayout(settingsMenuLayout)
        self.settingsMenu.setHidden(True)

        self.outtmplBox = QWidget()
        outtmplLayout = QHBoxLayout()
        outtmplLayout.addWidget(self.outtmplLineEdit)
        outtmplLayout.addWidget(self.outtmplHelpButton)
        outtmplLayout.setContentsMargins(0, 0, 0, 0 )
        outtmplLayout.setSpacing(10)
        self.outtmplBox.setLayout(outtmplLayout)

        self.folderBox = QWidget(self)

        self.folderMenu = MyFolderFrame(self)
        folderMenuLayout = QHBoxLayout()
        folderMenuLayout.addWidget(self.folderLineEdit)
        folderMenuLayout.addWidget(self.folderSelectButton)
        folderMenuLayout.setContentsMargins(0, 0, 0, 0 )
        folderMenuLayout.setSpacing(10)
        self.folderBox.setLayout(folderMenuLayout)

        self.urlLineEdit = MyLineEdit(self)
        self.urlLineEdit.setStyleSheet(
        """

            QLineEdit {
                border: 0 transparent;
                background-color: transparent;
                color: white;

            }

        """
        )
        self.urlLineEdit.setText(self.url)
        self.urlLineEdit.setToolTip(self.urlLineEdit.text())
        folderMenuMAINLayout = QVBoxLayout()
        folderMenuMAINLayout.addWidget(self.urlLineEdit)
        folderMenuMAINLayout.addWidget(self.folderBox)
        folderMenuMAINLayout.addWidget(self.outtmplBox)
        folderMenuMAINLayout.setContentsMargins(5, 10, 5, 0 )
        folderMenuMAINLayout.setSpacing(0)


        self.folderMenu.setLayout(folderMenuMAINLayout)
        self.folderMenu.setHidden(True)
# ---

# ---

# BUILD PROGRESS BOX ---

# ---
        #self.droppedFolderLabel = QLabel(self.folderLineEdit.text())
        self.droppedFolderLabel.setMaximumHeight(0)

        for x in range(self.formatSelect.count()):
            self.formatSelectClone.addItem(self.formatSelect.itemText(x))

# END ---------------------------------


# SETUP AND ORGANIZE MAIN LAYOUT ---------------------------------
    def organize(self):


        lay = QVBoxLayout(self)

        lay.addWidget(self.titleToolBox, alignment=Qt.AlignTop)
        lay.addWidget(self.droppedFolderLabel, alignment=Qt.AlignCenter)
        lay.addWidget(self.dl_gui_TotalProgress, alignment=Qt.AlignTop)
        lay.addWidget(self.logAndButtonsBox)
        lay.addWidget(self.folderMenu)
        lay.addWidget(self.settingsMenu)
        lay.setSpacing(0)
        lay.setAlignment(Qt.AlignTop)
        lay.setContentsMargins(2, 2, 2 ,2 )

        #self.logAndButtonsBox.setMinimumWidth(10)
        #self.dl_gui_TextLog.setMaximumHeight(100)
        ##self.dl_gui_Title.setMinimumWidth(0)
        self.buttonsGroup.setMaximumWidth(50)

        self.setLayout(lay)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        self.update_dl_gui_ToolTips()

    # SIGNAL CONNECTIONS
    def init_connections(self):
        self.worker.outSignal.connect(self.logging)
        self.worker.outSignal.connect(self.handle_total_progress)
        self.worker.finishedSignal.connect(self.downloadFinished)
        self.workerMeta.outSignal.connect(self.addMetaName)
        self.workerMeta.noTitleSignal.connect(self.addNoName)

        self.folderButtonToolbar.clicked.connect(self.showFolderMenu)
        self.folderButtonToolbar.clicked.connect(lambda: self.clickedSignal.emit())
        self.settingsButtonTool.clicked.connect(self.showsettingsMenu)
        self.settingsButtonTool.clicked.connect(lambda: self.clickedSignal.emit())

        self.saveAsLabel.clicked.connect(lambda: self.formatSelect.showPopup())
        self.audioQualitySlider.valueChanged.connect(lambda: self.sliderLabel.setText("Audio quality: "+self.labelInvertvalue()))
        #self.audioQualitySlider.valueChanged.connect(self.changeSmallSlider)
        self.audioQualitySlider.valueChanged.connect(self.changeSmallSlider)
        self.audioQualitySlider.valueChanged.connect(self.update_dl_gui_ToolTips)
        self.audioQualitySlider.valueChanged.connect(self.updateTitle)

        self.formatSelectClone.activated.connect(lambda: self.formatSelect.setCurrentIndex(self.formatSelectClone.currentIndex()))
        self.formatSelect.activated.connect(lambda: self.formatSelectClone.setCurrentIndex(self.formatSelect.currentIndex()))
        self.formatSelectClone.activated.connect(self.update_dl_gui_ToolTips)
        self.formatSelectClone.activated.connect(self.updateTitle)


        self.urlEditClone.textChanged.connect(lambda: self.urlLineEdit.setText(self.urlEditClone.text()))
        self.urlEditClone.returnPressed.connect(self.finishedSelectLine)
        self.urlEditClone.lostFocus.connect(lambda: self.urlEditClone.setHidden(True))
        self.urlEditClone.lostFocus.connect(lambda: self.dl_gui_Title.setHidden(False))
        self.urlEditClone.lostFocus.connect(lambda: self.dl_gui_Title.setCurrentIndex(0))

        self.folderEditClone.textChanged.connect(lambda: self.folderLineEdit.setText(self.folderEditClone.text()))
        self.folderEditClone.returnPressed.connect(self.finishedSelectLine)
        self.folderEditClone.lostFocus.connect(lambda: self.folderEditClone.setHidden(True))
        self.folderEditClone.lostFocus.connect(lambda: self.dl_gui_Title.setHidden(False))
        self.folderEditClone.lostFocus.connect(lambda: self.dl_gui_Title.setCurrentIndex(0))

        self.outtmplEditClone.textChanged.connect(lambda: self.outtmplLineEdit.setText(self.outtmplEditClone.text()))
        self.outtmplEditClone.returnPressed.connect(self.finishedSelectLine)
        self.outtmplEditClone.lostFocus.connect(lambda: self.outtmplEditClone.setHidden(True))
        self.outtmplEditClone.lostFocus.connect(lambda: self.dl_gui_Title.setHidden(False))
        self.outtmplEditClone.lostFocus.connect(lambda: self.dl_gui_Title.setCurrentIndex(0))

        self.qualityEditClone.valueChanged.connect(lambda: self.audioQualitySlider.setValue(self.qualityEditClone.value()))
        self.qualityEditClone.sliderReleased.connect(self.finishedSelectQuality)
        self.qualityEditClone.lostFocus.connect(lambda: self.qualityEditClone.setHidden(True))
        self.qualityEditClone.lostFocus.connect(lambda: self.dl_gui_Title.setHidden(False))
        self.qualityEditClone.lostFocus.connect(lambda: self.dl_gui_Title.setCurrentIndex(0))

        self.dl_gui_ButtonDownload.pressed.connect(self.press_download)
        self.dl_gui_ButtonDownload.clicked.connect(lambda: self.clickedSignal.emit())
        self.dl_gui_ButtonStop.pressed.connect(self.press_stop)
        self.dl_gui_ButtonStop.clicked.connect(lambda: self.clickedSignal.emit())
        self.dl_gui_ButtonPause.pressed.connect(self.press_pause)
        self.dl_gui_ButtonPause.clicked.connect(lambda: self.clickedSignal.emit())
        self.dl_gui_ButtonClearSelf.pressed.connect(self.press_clear)
        self.dl_gui_ButtonClearSelf.clicked.connect(lambda: self.clickedSignal.emit())

        self.dl_gui_IsCheckedStateButton.clicked.connect(self.press_checked)
        self.dl_gui_IsCheckedStateButton.clicked.connect(lambda: self.clickedCheckSignal.emit())

        self.dl_gui_ToolButton.pressed.connect(self.showToolbar)
        self.dl_gui_ToolButton.clicked.connect(lambda: self.clickedSignal.emit())
        self.dl_gui_ToolButton.pressed.connect(lambda: self.folderLineEdit.home(False))
        self.dl_gui_ToolButton.pressed.connect(lambda: self.urlLineEdit.home(False))
        self.dl_gui_ToolButton.pressed.connect(lambda: self.outtmplLineEdit.home(False))

        self.dl_gui_TextLog.doubleclickedSignal.connect(self.press_textEdit)
        self.dl_gui_TextLog.clickedSignal.connect(lambda: self.clickedSignal.emit())
        self.dl_gui_Title.activated.connect(self.activated)
        self.dl_gui_Title.clickedSignal.connect(lambda: self.clickedSignal.emit())
        #self.dl_gui_TextLog.clickedSignal.connect(self.printPing)

# ———————————————————————————————————————————————



    def wheelEvent(self, event):
        event.accept()


    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Down:
            event.ignore()
        if key == Qt.Key_Up:
            event.ignore()

    def resizeEvent(self, e):
        self.dl_gui_TextLog.setMinimumHeight(self.buttonsGroup.height()-self.formatSelectClone.height())
        self.dl_gui_TextLog.setMaximumHeight(self.buttonsGroup.height()-self.formatSelectClone.height())
        #self.dl_gui_TextLog.setMinimumWidth(self.width() - (self.buttonsGroup.width() +12))


    def finishedSelectQuality(self):
        self.qualityEditClone.setHidden(True)
        self.dl_gui_Title.setHidden(False)
        self.updateTitle()
        self.update_dl_gui_ToolTips()
        self.dl_gui_Title.setCurrentIndex(0)

    def finishedSelectLine(self):
        x = self.dl_gui_Title.currentIndex()

        if self.dl_gui_Title.itemData(x) == "url":
            self.urlEditClone.setHidden(True)
        elif self.dl_gui_Title.itemData(x) == "folder":
            self.folderEditClone.setHidden(True)
        elif self.dl_gui_Title.itemData(x) == "outtmpl":
            self.outtmplEditClone.setHidden(True)

        self.dl_gui_Title.setHidden(False)
        self.dl_gui_Title.setCurrentIndex(0)
        self.updateTitle()
        self.update_dl_gui_ToolTips()

    @pyqtSlot(int)
    def changeSmallSlider(self, new_value):
        self.changeSmallSliderSignal.emit(new_value)

    @pyqtSlot()
    def checkOverwriteClicked(self):
        checkButton = self.checkOverwrite
        checkButtonClone = self.checkOverwriteClone

        if checkButton.checkState() == 0:
            checkButton.setToolTip("Do not overwrite any files - setting does not affect metadata")
            checkButtonClone.setToolTip("Do not overwrite any files - setting does not affect metadata")
            #print(checkButton.checkState())


        elif checkButton.checkState() == 1:
            checkButton.setToolTip("Do not overwrite the video but overwrite related files\metadata\n( yt-dlp default )\n\n( might be an issue with certain codecs )")
            checkButtonClone.setToolTip("Do not overwrite the video but overwrite related files\metadata\n( yt-dlp default )\n\n( might be an issue with certain codecs )")
            #print(checkButton.checkState())


        elif checkButton.checkState() == 2:
            checkButton.setToolTip("Overwrite all video and metadata files\nThis option will overwrite partial downloads")
            checkButtonClone.setToolTip("Overwrite all video and metadata files\nThis option will overwrite partial downloads")
            #print(checkButton.checkState())


    @pyqtSlot()
    def checkThumbnailsClicked(self):
        checkButton = self.checkThumbnails
        checkButtonClone = self.checkThumbnailsClone

        if checkButton.checkState() == 0:
            checkButton.setToolTip("Embed thumbnails, do not write image-file\n\nNote:\nogg and wav will write an image-file since they don't support embedding")
            checkButtonClone.setToolTip("Embed thumbnails, do not write image-file\n\nNote:\nogg and wav will write an image-file since they don't support embedding")
            #print(checkButton.checkState())

        elif checkButton.checkState() == 1:
            checkButton.setToolTip("Write thumbnail(s), but don't embed")
            checkButtonClone.setToolTip("Write thumbnail(s), but don't embed")
            #print(checkButton.checkState())

        elif checkButton.checkState() == 2:
            checkButton.setToolTip("Do not write or embed thumbnails")
            checkButtonClone.setToolTip("Do not write or embed thumbnails")
            #print(checkButton.checkState())


    @pyqtSlot()
    def checkEmbedMetaClicked(self):
        checkButton = self.checkMetaEmbed
        checkButtonClone = self.checkMetaEmbedClone

        if checkButton.checkState() == 0:
            checkButton.setToolTip("Embed metadata and overwrite for existing files")
            checkButtonClone.setToolTip("Embed metadata and overwrite for existing files")
            #print(checkButton.checkState())

        elif checkButton.checkState() == 1:
            checkButton.setToolTip("Embed metadata to files — do not overwrite for existing files")
            checkButtonClone.setToolTip("Embed metadata to files — do not overwrite for existing files")
            #print(checkButton.checkState())

        elif checkButton.checkState() == 2:
            checkButton.setToolTip("Do not embed or overwrite metadata")
            checkButtonClone.setToolTip("Do not embed or overwrite metadata")
            #print(checkButton.checkState())



    @pyqtSlot(int)
    def invertValueDownload(self,value):
        value = self.audioQualitySlider.value()
        lst = [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
        index = [x for x in range(len(lst)) if lst[x] == value]
        return str(index[0])

    @pyqtSlot(int)
    def labelInvertvalue(self):
        value = self.audioQualitySlider.value()
        lst = [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
        index = [x for x in range(len(lst)) if lst[x] == value]
        return str(index[0])

    @pyqtSlot()
    def press_checked(self):
        if self.isCheckedState == False:
            print("checked it is")
            self.isCheckedState = True
            self.dl_gui_IsCheckedStateButton.setChecked(True)
        else:
            self.dl_gui_IsCheckedStateButton.setChecked(False)
            self.isCheckedState = False

    @pyqtSlot(str)
    def testUrl(self, url):
        regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        if re.match(regex, url):
            return True
        else:
            return False



    @pyqtSlot(str)
    def outtmplValueChanged(self, outtmplCurrentValue):
        self.updateTitle()
        self.update_dl_gui_ToolTips()

    @pyqtSlot(str)
    def folderValueChanged(self, folderLineCurrentValue):

        self.updateTitle()
        self.update_dl_gui_ToolTips()

    @pyqtSlot(str)
    def urlValueChanged(self, url_string):
        urlEditValue = url_string
        if self.testUrl(urlEditValue):
            self.urlLineEdit.setText(urlEditValue)
            self.url = urlEditValue
            self.myTitle = "{}".format(self.url)
            self.getMeta()
            self.updateUrlSignal.emit(self.url)
            self.updateTitle()
            self.update_dl_gui_ToolTips()

        else:
            print("pop")


    @pyqtSlot(str)
    def setOuttmpl(self, template):
        if template != self.my_outtmpl:
            self.my_outtmpl = template

    def showsettingsMenu(self):
        self.folderButtonToolbar.setChecked(False)
        self.settingsButtonTool.setChecked(True)

        self.logAndButtonsBox.setHidden(True)
        self.folderMenu.setHidden(True)

        self.settingsMenu.setHidden(False)

    def showFolderMenu(self):
        self.folderButtonToolbar.setChecked(True)
        self.settingsButtonTool.setChecked(False)

        self.logAndButtonsBox.setHidden(True)
        self.settingsMenu.setHidden(True)

        self.folderMenu.setHidden(False)

# BEGIN CLICK MENU BUTTON FUNCTIONS ------------------------------------

    def showToolbar(self):
        #self.resizeSignal.emit()
        # Set / reset list of current info for other view

        #print("ToolButton check state::"+str(myCheckState))

    # BEGIN hiding - - - - - - - - - - - - - - - - - - - - - - - - - - -

        #   HIDE MENUS (yes I'm sure)
        self.urlEditClone.setHidden(True)
        self.outtmplEditClone.setHidden(True)
        self.folderEditClone.setHidden(True)
        self.qualityEditClone.setHidden(True)
        self.dl_gui_Title.setHidden(False)


        if self.myCheckMenuFlag:

            self.myCheckMenuFlag = False

            self.settingsMenu.setHidden(True)
            self.folderMenu.setHidden(True)
            self.dl_gui_ToolBar.setHidden(True)

            self.dl_gui_Title.setHidden(False)
            self.logAndButtonsBox.setHidden(False)
            self.dl_gui_TotalProgress.setHidden(False)

        #---
            if self.urlLineEdit.text() != '':
                if self.url != self.urlLineEdit.text():
                    self.urlValueChanged(self.urlLineEdit.text())

            else:
                self.urlLineEdit.setText(self.url)
        #--------
        #---
            if self.folderLineEdit.text() != '':
                pass
            else:
                self.folderLineEdit.setText(self.my_DefaultPath)
        #--------
        #---
            if self.outtmplLineEdit.text() != '':
                pass
            else:
                self.outtmplLineEdit.setText(self.default_outtmpl)
        #-------



        #   SHOW MENUS (yes I'm sure)

        else:
            #self.urlBuffer = self.urlLineEdit.text()
            self.myCheckMenuFlag = True

            self.dl_gui_Title.setHidden(True)
            self.dl_gui_TotalProgress.setHidden(True)

            self.folderButtonToolbar.setChecked(True)

            self.dl_gui_ToolBar.setHidden(False)

            self.showFolderMenu()

    # END hiding  - - - - - - - - - - - - - - - - - - - - - - - - - - -

    # SAFETYCHECK FOLDERLINEEDIT  - - - - - - - - - - - - - - - - - - -

        length_of_foldertext = len(self.folderLineEdit.text())

        if self.folderLineEdit.text()[0] != "/":
            self.folderLineEdit.setText("/"+self.folderLineEdit)

        if self.folderLineEdit.text()[-1] == "/":
            self.folderLineEdit.setText(self.folderLineEdit.text()[0:length_of_foldertext-1])

    #   - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.updateTitle()


        #infoList.append(self.folderLineEdit.text())
        #infoList.append(self.outtmplLineEdit.text())
        #infoList.append(self.urlLineEdit.text())

        self.update_dl_gui_ToolTips()

# END CLICK MENU FUNCTIONS -----------------------------------------
    def updateTitle(self):
        infoList = []

        url_line = self.urlLineEdit.text()
        folder = self.folderLineEdit.text()
        outtmpl = self.outtmplLineEdit.text()
        my_format = self.formatSelect.itemText(self.formatSelect.currentIndex())
        my_quality = self.invertValueDownload(self.audioQualitySlider.value())

        for x in range(self.dl_gui_Title.count()):
            if self.dl_gui_Title.itemData(x) == "url":
                self.dl_gui_Title.setItemText(x, url_line)
            elif self.dl_gui_Title.itemData(x) == "folder":
                self.dl_gui_Title.setItemText(x, folder)
            elif self.dl_gui_Title.itemData(x) == "outtmpl":
                self.dl_gui_Title.setItemText(x, outtmpl)
            elif self.dl_gui_Title.itemData(x) == "format":
                self.dl_gui_Title.setItemText(x, my_format)
            elif self.dl_gui_Title.itemData(x) == "quality":
                self.dl_gui_Title.setItemText(x, "Audio quality: "+my_quality)

        for x in range(self.dl_gui_Title.count()):
            infoList.append(self.dl_gui_Title.itemText(x))

        self.gotInfoSignal.emit(infoList)        # EMIT LIST WITH FOLDER AND OUTPUT FOR FLAT-WIDGET LIST




    def showDragAndDropFolder(self):
        self.updateTitle()


        self.droppedFolderLabel.setHidden(False)
        self.droppedFolderLabel.setMaximumHeight(30)
        self.droppedFolderLabel.setText("New folder:    "+os.path.basename(self.folderLineEdit.text()))
        self.mytimer.start(3000)
        self.mytimer.timeout.connect(self.droppedFolderLabelHide)




    @pyqtSlot()
    def droppedFolderLabelHide(self):
        self.droppedFolderLabel.setHidden(True)
        self.droppedFolderLabel.setMaximumHeight(0)



    @pyqtSlot()
    def update_dl_gui_ToolTips(self):

        infoList = []

        name = self.dl_gui_Title.itemText(0)
        url = self.urlLineEdit.text()
        folder = self.folderLineEdit.text()
        outtmpl = self.outtmplLineEdit.text()
        current_format = self.formatSelect.itemText(self.formatSelect.currentIndex())
        current_quality = self.invertValueDownload(self.audioQualitySlider.value())

        if name == url:
            name = False

        elif name == folder:
            name = False

        elif name == outtmpl:
            name = False

        if name != False:
            mystr = name+"\n"+url+"\n"+folder+"\n"+outtmpl+"\n"+current_format+"\n"+"Audio Quality: "+current_quality
        else:
            mystr = url+"\n"+folder+"\n"+outtmpl+"\n"+current_format+"\n"+"Audio Quality: "+current_quality

        self.dl_gui_Title.setToolTip(mystr)
        self.folderLineEdit.setToolTip(folder)
        self.outtmplLineEdit.setToolTip(outtmpl)

        self.dl_gui_ToolButton.setToolTip("Click to edit URL, Folder, Output template and other settings\n\nURL:\n"+url+"\n\nFolder:\n"+folder+"\n\nOutput template:\n"+outtmpl)

        self.urlLineEdit.setToolTip("Current confirmed url:\n"+url)

        self.folderButtonToolbar.setToolTip("Edit url, folder and output template\n\nURL:\n"+url+"\n\nCurrent folder:\n"+folder+"\n\nCurrent output template:\n"+outtmpl)

        current_meta_checkstate = self.checkMetaEmbed.checkState()
        current_thumbnail_checkstate = self.checkThumbnails.checkState()
        current_overwrite_checkstate = self.checkOverwrite.checkState()

        if current_meta_checkstate == 0:
            metawill = "embed and overwrite"
        elif current_meta_checkstate == 1:
            metawill = "embed to new files, not overwrite to exisiting"
        elif current_meta_checkstate == 2:
            metawill = "not embed or overwrite"

        if current_thumbnail_checkstate == 0:
            thumbswill = "embed, not write copy"
        elif current_thumbnail_checkstate == 1:
            thumbswill = "not embed, but will write copy"
        elif current_thumbnail_checkstate == 2:
            thumbswill = "not embed or write"

        if current_overwrite_checkstate == 0:
            overwritewill = "do not overwrite anything"
        elif current_overwrite_checkstate == 1:
            overwritewill = "do not overwrite files, but overwrite metadata"
        elif current_overwrite_checkstate == 2:
            overwritewill = "overwrite everything"

        self.settingsButtonTool.setToolTip("Edit audio quality, output codec/filetype and overwrite/metadata/thumbnail settings\n\n"+"Overwrite policy is "+overwritewill+"\nThumbnails will "+thumbswill+"\nMetdata will "+metawill+"\n\nCurrent format:\n"+" "+current_format+"\n\nCurrent quality (0 is best):\n"+current_quality)





        #infoList.append(self.folderLineEdit.text())
        #infoList.append(self.outtmplLineEdit.text())
        #infoList.append(self.urlLineEdit.text())

    @pyqtSlot(int)
    def activated(self, index):

        if self.dl_gui_Title.itemData(index) == "url":
            self.dl_gui_Title.setHidden(True)
            self.urlEditClone.setHidden(False)
            self.urlEditClone.setText(self.urlLineEdit.text())
            self.urlEditClone.setFocus(True)
            self.urlEditClone.end(False)

        elif self.dl_gui_Title.itemData(index) == "folder":
            self.dl_gui_Title.setHidden(True)
            self.folderEditClone.setHidden(False)
            self.folderEditClone.setText(self.folderLineEdit.text())
            self.folderEditClone.setFocus(True)
            self.folderEditClone.end(False)

        elif self.dl_gui_Title.itemData(index) == "outtmpl":
            self.dl_gui_Title.setHidden(True)
            self.outtmplEditClone.setHidden(False)
            self.outtmplEditClone.setText(self.outtmplLineEdit.text())
            self.outtmplEditClone.setFocus(True)
            self.outtmplEditClone.end(False)

        elif self.dl_gui_Title.itemData(index) == "format":
            self.formatSelectClone.showPopup()
            self.dl_gui_Title.setCurrentIndex(0)

        elif self.dl_gui_Title.itemData(index) == "quality":
            self.dl_gui_Title.setHidden(True)
            self.qualityEditClone.setHidden(False)
            self.qualityEditClone.setValue(self.audioQualitySlider.value())
            self.qualityEditClone.setFocus(True)


    @pyqtSlot(str)
    def addMetaName(self, myName):
        self.gotNameSignal.emit(myName)
        self.dl_gui_Title.clear()
        self.dl_gui_Title.addItem(myName,                                                        "name")
        self.dl_gui_Title.addItem(self.urlLineEdit.text(),                                       "url")
        self.dl_gui_Title.addItem(self.folderLineEdit.text(),                                    "folder")
        self.dl_gui_Title.addItem(self.outtmplLineEdit.text(),                                   "outtmpl")
        self.dl_gui_Title.addItem(self.formatSelect.itemText(self.formatSelect.currentIndex()),  "format")
        self.dl_gui_Title.addItem(self.invertValueDownload(self.audioQualitySlider.value()),       "quality")

        #print(self.dl_gui_Title.itemData(0))
        #print(self.dl_gui_Title.itemData(1))
        #print(self.dl_gui_Title.itemData(2))
        #print(self.dl_gui_Title.itemData(3))
        #print(self.dl_gui_Title.itemData(4))  # Will be None
        self.updateTitle()
        self.update_dl_gui_ToolTips()

    @pyqtSlot()
    def addNoName(self):
        self.dl_gui_Title.clear()
        self.dl_gui_Title.addItem(self.urlLineEdit.text(),                                       "url")
        self.dl_gui_Title.addItem(self.folderLineEdit.text(),                                    "folder")
        self.dl_gui_Title.addItem(self.outtmplLineEdit.text(),                                   "outtmpl")
        self.dl_gui_Title.addItem(self.formatSelect.itemText(self.formatSelect.currentIndex()),  "format")
        self.dl_gui_Title.addItem(self.invertValueDownload(self.audioQualitySlider.value()),       "quality")
        #print(self.dl_gui_Title.itemData(0))
        #print(self.dl_gui_Title.itemData(1))
        #print(self.dl_gui_Title.itemData(2))
        self.updateTitle()
        self.update_dl_gui_ToolTips()
        #self.dl_gui_Title.setText(myName)
        #self.dl_gui_Title.adjustSize()


    @pyqtSlot()
    def press_clear(self):
        self.dl_gui_TextLog.clear()
        self.dl_gui_ButtonClearSelf.setHidden(True)
        #self.dl_gui_TotalProgress.setValue(0)
        self.dl_gui_TotalProgress.reset()

        self.my_twin.resetGUI()

    def press_textEdit(self):
        print("log clicked")
        return

    @pyqtSlot()
    def getMeta(self):
        print("getting meta..")
        url = self.url
        theProgram = 'yt-dlp'
        simulateFlag = '-s'
        outtmplFlag = '-O'
        outtmpl = self.meta_outtmpl
        noPlaylistFlag = '--no-playlist'
        playlistStartFlag = '--playlist-start'
        playlistEndFlag = '--playlist-end'
        playlistStart = '1'
        playlistEnd = '1'
        singleJsonFlag = '-J'
        flatPlaylist = '--flat-playlist'

        command = [theProgram,singleJsonFlag,flatPlaylist,playlistStartFlag,playlistStart,playlistEndFlag,playlistEnd,url]
        path = "./"
        self.workerMeta.run_command(command, cwd=path)

    @pyqtSlot()
    def press_playPause(self):
        if self.worker.proc == None:
            self.press_download()
        else:
            self.press_pause()


    @pyqtSlot()
    def press_stop(self):
        if self.worker.proc != None:
            self.worker.stop_event.set()
            self.dl_gui_ButtonPause.setHidden(True)
            self.dl_gui_ButtonStop.setHidden(True)

            #self.dl_gui_ButtonClearSelf.setHidden(False)
            self.dl_gui_ButtonDownload.setHidden(False)
            self.dl_gui_ButtonClearSelf.setHidden(False)


    @pyqtSlot()
    def press_pause(self):
        #print(self.paused)
        if self.worker.proc != None:
            if self.paused == 0:
                self.worker.proc.send_signal(signal.SIGSTOP)
                self.paused = 1
                self.dl_gui_ButtonPause.setText("")
            elif self.paused == 1:
                self.worker.proc.send_signal(signal.SIGCONT)
                self.dl_gui_ButtonPause.setText("")
                self.paused = 0

    @pyqtSlot()
    def setDefaultParentFolder(self):
        self.my_FinalPath = None
        my_MusicPath = None
        my_DownloadsPath = None
        my_HomePath = None
        self.places = []

        try:
            my_DownloadsPath = os.path.expanduser("~/Downloads")
            self.places.append(my_DownloadsPath)
            #my_DownloadsPath = my_DownloadsPath+"/QTubeDL"
        except:
            pass

        try:
            my_MusicPath = os.path.expanduser("~/Music")
            self.places.append(my_MusicPath)
            #my_MusicPath = my_MusicPath+"/QTubeDL"
        except:
            pass

        try:
            my_HomePath = os.path.expanduser("~")
            self.places.append(my_HomePath)
            #my_HomePath = my_HomePath+"/QTubeDL"
        except:
            pass

        if my_MusicPath != None:
            my_FinalPath = my_MusicPath
            self.my_DefaultPath = my_MusicPath

        elif my_DownloadsPath != None:
            my_FinalPath = my_DownloadsPath
            self.my_DefaultPath = my_DownloadsPath

        elif my_HomePath != None:
            my_FinalPath = my_HomePath
            self.my_DefaultPath = my_HomePath

        if my_FinalPath != None:
            self.folderLineEdit.setText(my_FinalPath)
            self.folderLineEdit.setToolTip(self.folderLineEdit.text())

    @pyqtSlot()
    def press_parentfolder(self):

        dialog = QFileDialog()
        dialog.setDirectory(self.folderLineEdit.text())
        dialog.setFileMode(QFileDialog.DirectoryOnly)
        dialog.setOption(QFileDialog.DontUseNativeDialog)

        dialog.setSidebarUrls([QUrl.fromLocalFile(self.places[2]), QUrl.fromLocalFile(self.places[0]), QUrl.fromLocalFile(self.places[1])])

        path = dialog.getExistingDirectory(self, "CHOOSE DESTINATION")
        if path != '':
            self.parentFolder = path
            self.folderLineEdit.setText(path)


    #@pyqtSlot()
    #def printPing(self):
        #print("ping")

    def downloadFinished(self):
        self.dl_gui_ButtonStop.setHidden(True)
        self.dl_gui_ButtonPause.setHidden(True)
        self.dl_gui_ButtonDownload.setHidden(False)
        self.dl_gui_ButtonClearSelf.setHidden(False)
        self.dl_gui_TotalProgress.setStyleSheet(
            """
                QProgressBar {
                    max-height: 2px;
                    background-color: rgba(255, 255, 255, 0); /* set transparent */
                    opacity: .4;
                    background-color: rgba(255, 255, 255, 0); /* set transparent */
                }

                QProgressBar:chunk {
                    background: #3a7000;
                }
            """
            )

        try:
            my_value = self.current_vid+1
            self.dl_gui_TotalProgress.setValue(my_value)
            self.my_twin._Progress.setValue(my_value)
        except:
            pass

        self.paused = 0




    @pyqtSlot(str)
    def handle_total_progress(self, string):
        #print(string)
        stringpiece = string.find("Downloading video")
        if stringpiece != -1:
            progress_re = re.compile("(\d+) of")
            progress_tot = re.compile("of (\d+)")
            my_current = progress_re.search(string)
            my_total = progress_tot.search(string)

            substring = "Downloading video"
            if my_current and my_total:

                self.current_vid = my_current.group(1)
                self.current_total = my_total.group(1)
                self.current_vid = int(self.current_vid)
                self.current_total = int(self.current_total)
                self.current_total = self.current_total+1
                self.dl_gui_TotalProgress.setMaximum(self.current_total)
                self.my_twin.progressTotal(self.current_total)
                #if self.current_vid != self.current_total:
                    #self.dl_gui_TotalProgress.setValue(self.current_vid)
                    #self.my_twin._Progress.setValue(self.current_vid)
                #elif self.current_vid == self.current_total:
                self.dl_gui_TotalProgress.setValue(self.current_vid)
                self.my_twin._Progress.setValue(self.current_vid)




    @pyqtSlot(str)
    def logging(self, string):
        cursor = QTextCursor(self.dl_gui_TextLog.document())


        self.dl_gui_TextLog.setTextCursor(cursor)

        # insert text at the cursor

        self.dl_gui_TextLog.appendPlainText(string.strip())

        string=string.strip()

        #print(string)

        bar = self.dl_gui_TextLog.verticalScrollBar()
        bar.setValue(bar.maximum())


# DRAG AND DROP -----

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
                    self.text = url.toLocalFile()
                    if os.path.isdir(self.text):
                        self.folderLineEdit.setText(self.text)
                        self.showDragAndDropFolder()
                else:
                    self.text = str(url.toString())
                    self.droppedUrlSignal.emit(self.text)

        else:
            event.ignore()
# -----

# ——————————————————————————————————————————————————————————
# DOWNLOAD FUNCTION ————————————————————————————————————————

    @pyqtSlot()
    def press_download(self):
        self.dl_gui_ButtonClearSelf.setHidden(True)
        if self.worker.proc == None:
            self.dl_gui_ButtonDownload.setHidden(True)
            self.dl_gui_ButtonStop.setHidden(False)
            self.dl_gui_ButtonPause.setHidden(False)

            # UNUSED
            #showProgress = '--progress'
            #showProgressNewline = '--newline'
            #ffmpegLocationFlag = '--ffmpeg-location'
            #ffmpegLocation = '\"/bin/ffmpeg\"'
            #

# REFRENCE URL FOR DOWNLOAD --------------------------------

            url = self.url

# ----------------------------------------------------------
# COMMAND FOR SUBPROCESS.POPEN -----------------------------

            theProgram = 'yt-dlp'

# ----------------------------------------------------------
# CONSIDER OUTTMPL -----------------------------------------

            outtmplFlag = '-o'
            if self.outtmplLineEdit.text() == '':
                outtmpl = self.default_outtmpl
            else:
                outtmpl = self.outtmplLineEdit.text()

            #if self.folderLineEdit.text() != '':
                #outtmpl = self.folderLineEdit.text()+"/"+outtmpl

# ----------------------------------------------------------
# SET AUDIO ------------------------------------------------

            f_Flag = '-f'
            f_Format = 'bestaudio'
            extractAudio = '--extract-audio'
            audioFormatFlag = '--audio-format'

# AUDIO FILETYPE - - - - - - - - - - - - - - - - - - - - - -
            audioFormat = self.formatSelect.itemData(self.formatSelect.currentIndex())
#  - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

            audioQualityFlag = '--audio-quality'

        #   DETERMINE AUDIO QUALITY FROM self.audioQualitySlider
            lst = [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
            index = [x for x in range(len(lst)) if lst[x] == self.audioQualitySlider.value()]

# AUDIO QUALITY - - - - - - - - - - - - - - - - - - - - - - -
            audioQuality = self.invertValueDownload(self.audioQualitySlider.value())
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

            print("selected audio quality: "+audioQuality)

# ----------------------------------------------------------

            ignoreErrors = '--ignore-errors'

            noOverwrites = '--no-overwrites'
            noPostOverwrites = '--no-post-overwrites'
            yesPostOverwrites = '--post-overwrites'
            forceOverwrites = '--force-overwrites'
            noForceOverwrites = '--no-force-overwrites'

            embedThumbnail = '--embed-thumbnail'
            noEmbedThumbnail = '--no-embed-thumbnail'
            noWriteThumbnail = '--no-write-thumbnail'
            writeThumbnail = '--write-thumbnail'

            addMetadata = '--embed-metadata'
            noAddMetadata = '--no-embed-metadata'

            if audioFormat == "vorbis" or audioFormat == "wav":
                thumbnail = noEmbedThumbnail
                if self.checkThumbnails.checkState() == 0:
                    writeThumbnail = writeThumbnail

                if self.checkThumbnails.checkState() == 1:
                    writeThumbnail = writeThumbnail

                if self.checkThumbnails.checkState() == 2:
                    writeThumbnail = noWriteThumbnail

            else:
                if self.checkThumbnails.checkState() == 0:
                    thumbnail = embedThumbnail
                    writeThumbnail = noWriteThumbnail

                elif self.checkThumbnails.checkState() == 1:
                    thumbnail = noEmbedThumbnail
                    writeThumbnail = writeThumbnail

                elif self.checkThumbnails.checkState() == 2:
                    thumbnail = noEmbedThumbnail
                    writeThumbnail = noWriteThumbnail


            if self.checkOverwrite.checkState() == 0:
                print("DL state: "+str(self.checkOverwrite.checkState()))
                overwrites = noOverwrites
                postOverwrites = noPostOverwrites

            elif self.checkOverwrite.checkState() == 1:
                print("DL state: "+str(self.checkOverwrite.checkState()))
                overwrites = noForceOverwrites
                postOverwrites = yesPostOverwrites

            elif self.checkOverwrite.checkState() == 2:
                print("DL state: "+str(self.checkOverwrite.checkState()))
                overwrites = forceOverwrites
                postOverwrites = yesPostOverwrites



            if self.checkMetaEmbed.checkState() == 0:
                metadata = addMetadata
                postOverwrites = yesPostOverwrites


            if self.checkMetaEmbed.checkState() == 1:
                metadata = addMetadata
                postOverwrites = noPostOverwrites

            if self.checkMetaEmbed.checkState() == 2:
                metadata = noAddMetadata
                postOverwrites = noPostOverwrites


# BUILD COMMAND FOR YT-DLP ---------------------------------

            command = [theProgram,f_Flag,f_Format,outtmplFlag,outtmpl,overwrites,postOverwrites,thumbnail,writeThumbnail,metadata,extractAudio,audioQualityFlag,audioQuality,audioFormatFlag,audioFormat,url]

# ----------------------------------------------------------

# CONSIDER PATH --------------------------------------------

            if self.folderLineEdit.text() != '':
                if os.path.isdir(self.folderLineEdit.text()):
                    path = self.folderLineEdit.text()
                else:
                    os.mkdir(self.folderLineEdit.text())
                    path = self.folderLineEdit.text()
            else:
                path = "./"

# -----------------------------------------------------------

# RUN DOWNLOAD ----------------------------------------------

            self.worker.run_command(command, cwd=path)

# -----------------------------------------------------------



#   —————————————————————————————————————————————————————————
#   SUBCLASSES AND OVERLOADS    —————————————————————————————
#   —————————————————————————————————————————————————————————


# HALP ME! The help menu ————————————————————————————————————

    def showHelp(self):
        mystr = ["""Instructions:
—————————————

    - Put options inside %()s
      to automatically name finished files and folders

    - Seperate with "/" to make folders


Example:
—————————————

    %(uploader)s/%(title)s.%(ext)s


This will:
—————————————

    - Put a single or all downloaded videos/files inside a folder named after the uploader of the video/playlist

    - Give all the files the title they have on youtube

    - Set the associated file-extension (webm, m4a, etc.)


————————————————————————————————————————————————————————————
LIST OF OPTIONS (if using yt-dlp/youtube-dl):
————————————————————————————————————————————————————————————
https://github.com/yt-dlp/yt-dlp#output-template

(string)    provides letters
(numeric)   provides numbers


id (string):                         Video identifier
title (string):                      Video title
url (string):                        Video URL
ext (string):                        Video filename extension
alt_title (string):                  A secondary title of the video
display_id (string):                 An alternative identifier for the video
uploader (string):                   Full name of the video uploader
license (string):                    License name the video is licensed under
creator (string):                    The creator of the video
release_date (string):               The date (YYYYMMDD) when the video was released
timestamp (numeric):                 UNIX timestamp of the moment the video became available
upload_date (string):                Video upload date (YYYYMMDD)
uploader_id (string):                Nickname or id of the video uploader
channel (string):                    Full name of the channel the video is uploaded on
channel_id (string):                 Id of the channel
location (string):                   Physical location where the video was filmed
duration (numeric):                  Length of the video in seconds
view_count (numeric):                How many users have watched the video on the platform
like_count (numeric):                Number of positive ratings of the video
dislike_count (numeric):             Number of negative ratings of the video
repost_count (numeric):              Number of reposts of the video
average_rating (numeric):            Average rating give by users, the scale used depends on the webpage
comment_count (numeric):             Number of comments on the video
age_limit (numeric):                 Age restriction for the video (years)
is_live (boolean):                   Whether this video is a live stream or a fixed-length video
start_time (numeric):                Time in seconds where the reproduction should start, as specified in the URL
end_time (numeric):                  Time in seconds where the reproduction should end, as specified in the URL
format (string):                     A human-readable description of the format
format_id (string):                  Format code specified by --format
format_note (string):                Additional info about the format
width (numeric):                     Width of the video
height (numeric):                    Height of the video
resolution (string):                 Textual description of width and height
tbr (numeric):                       Average bitrate of audio and video in KBit/s
abr (numeric):                       Average audio bitrate in KBit/s
acodec (string):                     Name of the audio codec in use
asr (numeric):                       Audio sampling rate in Hertz
vbr (numeric):                       Average video bitrate in KBit/s
fps (numeric):                       Frame rate
vcodec (string):                     Name of the video codec in use
container (string):                  Name of the container format
filesize (numeric):                  The number of bytes, if known in advance
filesize_approx (numeric):           An estimate for the number of bytes
protocol (string):                   The protocol that will be used for the actual download
extractor (string):                  Name of the extractor
extractor_key (string):              Key name of the extractor
epoch (numeric):                     Unix epoch when creating the file
autonumber (numeric):                Number that will be increased with each download
                                     starting at --autonumber-start
playlist (string):                   Name or id of the playlist that contains the video
playlist_index (numeric):            Index of the video in the playlist
                                     padded with leading zeros according to the total length of the playlist
playlist_id (string):                Playlist identifier
playlist_title (string):             Playlist title
playlist_uploader (string):          Full name of the playlist uploader
playlist_uploader_id (string):       Nickname or id of the playlist uploader

Available for the video that belongs to some logical chapter or section:

chapter (string):                    Name or title of the chapter the video belongs to
chapter_number (numeric):            Number of the chapter the video belongs to
chapter_id (string):                 Id of the chapter the video belongs to

Available for the video that is an episode of some series or programme:

series (string):                     Title of the series or programme the video episode belongs to
season (string):                     Title of the season the video episode belongs to
season_number (numeric):             Number of the season the video episode belongs to
season_id (string):                  Id of the season the video episode belongs to
episode (string):                    Title of the video episode
episode_number (numeric):            Number of the video episode within a season
episode_id (string):                 Id of the video episode

Available for the media that is a track or a part of a music album:

track (string):                      Title of the track
track_number (numeric):              Number of the track within an album or a disc
track_id (string):                   Id of the track
artist (string):                     Artist(s) of the track
genre (string):                      Genre(s) of the track
album (string):                      Title of the album the track belongs to
album_type (string):                 Type of the album
album_artist (string):               List of all artists appeared on the album
disc_number (numeric):               Number of the disc or other physical medium the track belongs to
release_year (numeric):              Year (YYYY) when the album was released
"""]
        result = ScrollMessageBox(mystr, None)
        result.exec_()

# SCROLLABLE HELP-WINDOW/ MESSAGEBOX
class ScrollMessageBox(QMessageBox):
   def __init__(self, l, *args, **kwargs):
    QMessageBox.__init__(self, *args, **kwargs)
    scroll = QScrollArea(self)
    scroll.setWidgetResizable(True)
    self.content = QWidget()
    self.setWindowTitle("OUTPUT TEMPLATE OPTIONS")
    self.setFont(QFont('Noto Mono', 9))
    scroll.setWidget(self.content)
    lay = QVBoxLayout(self.content)
    for item in l:
        theText = QLabel(item, self)
        lay.addWidget(theText)
    self.layout().addWidget(scroll, 0, 0, 1, self.layout().columnCount())
    self.setStyleSheet(
    """
        QScrollArea{min-width:900 px; min-height: 600px}
    """
    )

      #scroll.resize(theText.size())
      #scroll.setMinimumWidth()
      #scroll.setMinimumHeight(l.height()/2)

# END OF HALP ME! The help manu ——————————————————————————————

#   LINEEDIT    ---------------------------------------------


class MyFolderFrame(QWidget):
    clickedSignal = pyqtSignal()
    doubleclickedSignal = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class MyLineEditTitle(QLineEdit):
    lostFocus = pyqtSignal()
    def __init__(self, *args, **kwargs):
        super(QLineEdit, self).__init__(*args, **kwargs)
        self.sh_end = QShortcut(QKeySequence("Alt+Right"), self)
        self.sh_end.activated.connect(lambda:self.end(False))

        self.sh_home = QShortcut(QKeySequence("Alt+Left"), self)
        self.sh_home.activated.connect(lambda:self.home(False))

    def focusOutEvent(self, e):
        self.lostFocus.emit()
        super().focusInEvent(e)


class MyLineEdit(QLineEdit):
    lostFocus = pyqtSignal()
    clickedSignal = pyqtSignal()
    doubleclickedSignal = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(QLineEdit, self).__init__(*args, **kwargs)
        self.sh_end = QShortcut(QKeySequence("Alt+Right"), self)

        self.sh_home = QShortcut(QKeySequence("Alt+Left"), self)

    def focusOutEvent(self, e):
        self.lostFocus.emit()
        super().focusInEvent(e)

    #def keyPressEvent(self, e):
        #if e.key() == Qt.Key_Left:
            #self.cursorBackward(False,30)
        #elif e.key() == Qt.Key_Right:
            #self.cursorForward(False,30)
        #e.accept()


#   ---------------------------------------------------------

#   TEXTEDIT    ---------------------------------------------

class MySlider(QSlider):
    lostFocus = pyqtSignal()
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def focusOutEvent(self, e):
        self.lostFocus.emit()
        super().focusInEvent(e) # Do the default action on the parent class QLineEdit

class MyTextEdit(QPlainTextEdit):
    clickedSignal = pyqtSignal()
    doubleclickedSignal = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setReadOnly(True)
        self.setFocusPolicy(Qt.StrongFocus)
        self.scroll_bar = QScrollBar(self)
        self.setVerticalScrollBar(self.scroll_bar)

    def mousePressEvent(self, e):
        if e.button() == 1:
           self.clickedSignal.emit()


    #def mouseDoubleClickEvent(self, e):
        #if e.button() == 1:
           #self.clickedSignal.emit()

    def wheelEvent(self, e):
        if self.hasFocus():
            #print(self.verticalScrollBar().value())
            #print(self.verticalScrollBar().maximum())
            my_direction = e.angleDelta().y() // 120
            if self.scroll_bar.value() == self.scroll_bar.maximum() and my_direction == -1:
                e.accept()

            elif self.scroll_bar.value() == self.scroll_bar.minimum() and my_direction == 0:
                e.accept()
            else:
                super().wheelEvent(e)
    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Down:
            event.ignore()
        if key == Qt.Key_Up:
            event.ignore()


#   ---------------------------------------------------------

class MyQFormatBox(QComboBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFocusPolicy(Qt.StrongFocus)

    def mousePressEvent(self, e):
        #self.getSizesSignal.emit()

        if e.button() == 1:
            super().mousePressEvent(e)
            e.ignore()

    def mouseDoubleClickEvent(self, e):
        if e.button() == 1:
            super(MyQFormatBox, self).showPopup()

        e.accept()

    def wheelEvent(self, e):
        if self.hasFocus():
            #print(self.verticalScrollBar().value())
            #print(self.verticalScrollBar().maximum())
            #print(e.angleDelta().y())
            pass
            #super(MyQComboBox, self).wheelEvent(e)
        else:
            pass

class MyQComboBox(QComboBox):
    clickedSignal = pyqtSignal()
    editableUrlSignal = pyqtSignal()
    editableFolderSignal = pyqtSignal()
    editableOuttmplSignal = pyqtSignal()
    editNameSignal = pyqtSignal()
    finishedEditSignal = pyqtSignal()
    def __init__(self, scrollWidget=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scrollWidget=scrollWidget
        self.editableFlag = False
        self.setFocusPolicy(Qt.StrongFocus)

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Down:
            event.ignore()
        if key == Qt.Key_Up:
            event.ignore()



    def mousePressEvent(self, e):
        #self.getSizesSignal.emit()

        if e.button() == 1:
            self.clickedSignal.emit()
            self.editableFlag = True
            super(MyQComboBox, self).mousePressEvent(e)

        if e.button() == 2:
           super(MyQComboBox, self).showPopup()
           super(MyQComboBox, self).mousePressEvent(e)

        else:
            #self.showPopup()
            #self.clickedSignal.emit()

            super().mousePressEvent(e)
        e.accept()

    def showPopup(self):
        if self.editableFlag == True:
            pass
        else:
            super(MyQComboBox, self).showPopup()

    def mouseDoubleClickEvent(self, e):
        #self.getSizesSignal.emit()

        if e.button() == 1:
            super(MyQComboBox, self).showPopup()

        e.accept()

    def wheelEvent(self, e):
        if self.hasFocus():
            #print(self.verticalScrollBar().value())
            #print(self.verticalScrollBar().maximum())
            #print(e.angleDelta().y())
            pass
            #super(MyQComboBox, self).wheelEvent(e)
        else:
            pass

# ———————————————————————————————————————————————————————————
