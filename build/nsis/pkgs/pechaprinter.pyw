import sys
import os
import struct
import platform
import subprocess
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt
from PyQt5.uic import loadUi
from PIL import Image
from natsort import natsorted
import pathlib
import shutil
import time

BASEDIR = os.path.dirname(os.path.abspath(__file__))
TEMPDIR =  pathlib.Path(pathlib.Path.home(), 'Documents', '~temp')
TEMPDIRsep = f'{TEMPDIR}{os.sep}'

class Pecha(object):
    def __init__(self):
        super(Pecha, self).__init__()
        self.inputFormat = ""
        self.inputLocation = ""
        self.outputName = ""
        self.outputLocation = ""
        self.outputSize = "A4"
        self.startSide = "A"
        # dummy image to change start side, 3 is a highly improbable value
        self.dummyImg = Image.new('RGB', (3, 3), color = 'white')
        self.jpgImages = []
        self.totalImages = 0
        self.resizedImages = []
        self.imageStacks = [[], [], []]
        self.finalPages = []
        self.tempJpgs = []
        self.tempJpgsNumber = 0
        self.totalPages = 0
        self.difference = 0
        self.aspectRatio = 3508 / 827
        self.optimalWidth = 0
        self.optimalHeight = 0
        self.optimalHeightTotal = 0
        self.message = ''
        self.imgExt = (
            "tif",
            "tiff",
            "gif",
            "jpeg",
            "jpg",
            "jif",
            "jfif",
            "pgm",
            "jp2",
            "jpx",
            "j2k",
            "j2c",
            "fpx",
            "pcd",
            "png",
            "pbm",
            "ppm"
        )
        self.pdftoppmLocation = "{base}/dep/{platform}/bin{bits}/pdftoppm{ext}".format(
            base=BASEDIR,
            platform=("Mac" if platform.system() == "Darwin" else platform.system()),
            bits=8 * struct.calcsize("P"),
            ext=(".exe" if platform.system() == "Windows" else ""),
        )

    def Main(self):
        self.collectFiles()
        self.resizeImages()
        self.orderImages()
        self.savePdf()
        return 1

    def collectFiles(self):

        # insert extra first page by default
        self.jpgImages.insert(0, self.dummyImg)

        if self.inputFormat == "img":
            for i in range(len(self.inputLocation)):
                currentImg = Image.open(self.inputLocation[i])
                self.jpgImages.append(currentImg)

        elif self.inputFormat == "pdf":
            # get temp images
            for i in range(len(self.tempJpgs)):
                currentImg = Image.open(self.inputLocation + self.tempJpgs[i])
                self.jpgImages.append(currentImg)
            pass

        # check if it's needed, del if it's not needed
        if self.startSide == 'B':
            if self.jpgImages[0].size[0] != 3:
                self.jpgImages.insert(0, self.dummyImg)
        else:
            if self.jpgImages[0].size[0] == 3:
                del self.jpgImages[0]


        self.totalImages = len(self.jpgImages)
        self.totalPages = self.totalImages // 3
        self.difference = self.totalImages % 3
        if self.difference != 0:
            self.totalPages += 1
            pass
    
    def extractImages(self):
        if os.path.exists(TEMPDIR):
            shutil.rmtree(TEMPDIR)
        if not os.path.exists(TEMPDIR):
            os.makedirs(TEMPDIR)

        # hide cmd on Windows
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        print(f'{self.pdftoppmLocation} -r 300 {self.inputLocation} {TEMPDIRsep}')

        # pdftoppm [options] PDF-file PPM-root
        # -r number Specifies the X and Y resolution, in DPI.  The default is 150 DPI.
        # https://www.mankier.com/1/pdftoppm#Options
        p = subprocess.Popen(
            [
                self.pdftoppmLocation,
                '-r',
                '300',
                self.inputLocation,
                TEMPDIRsep,
            ],
            startupinfo=startupinfo
        )
        self.inputLocation = TEMPDIRsep
        while p.poll() == None:
            if p.poll() != None:
                break
 
        # list of images in the temp folder
        self.tempJpgs = [
            file
            for file in natsorted(os.listdir(self.inputLocation))
            if file.endswith(self.imgExt)
        ]
        self.tempJpgsNumber = len(self.tempJpgs)

    def resizeImages(self):
        if self.outputSize == "A4":
            self.optimalWidth, self.optimalHeight, self.optimalHeightTotal = (
                3508,
                827,
                2481,
            )
        elif self.outputSize == "A3":
            self.optimalWidth, self.optimalHeight, self.optimalHeightTotal = (
                4961,
                1168,
                3508,
            )

        for i in range(0, self.totalImages, 1):
            self.message = f'Resizing image {i}'
            print(self.message)
            currentImg = self.jpgImages[i]
            width, height = currentImg.size
            currentAspectRatio = width / height
            if self.aspectRatio >= currentAspectRatio:
                proportionalWidth = (self.optimalHeight / height) * width
                resizedImage = currentImg.resize(
                    [int(proportionalWidth), self.optimalHeight], resample=0
                )
                resizedWidth, resizedHeight = resizedImage.size
                newImage = Image.new(
                    "RGB", (self.optimalWidth, self.optimalHeight), (255, 255, 255)
                )
                newImage.paste(
                    resizedImage,
                    (
                        (self.optimalWidth - resizedWidth) // 2,
                        (self.optimalHeight - resizedHeight) // 2,
                    ),
                )
            else:
                proportionalHeight = (self.optimalWidth / width) * height
                resizedImage = currentImg.resize(
                    [self.optimalWidth, int(proportionalHeight)], resample=0
                )
                resizedWidth, resizedHeight = resizedImage.size
                newImage = Image.new(
                    "RGB", (self.optimalWidth, self.optimalHeight), (255, 255, 255)
                )
                newImage.paste(
                    resizedImage,
                    (
                        (self.optimalWidth - resizedWidth) // 2,
                        (self.optimalHeight - resizedHeight) // 2,
                    ),
                )
                pass
            self.resizedImages.append(newImage)

    def orderImages(self):
        self.message = f'Ordering images'
        print(self.message)


        if self.difference == 0:
            for i in range(0, self.totalPages, 1):
                self.imageStacks[0].append(self.resizedImages[i])
            for i in range(self.totalPages, self.totalPages * 2, 1):
                self.imageStacks[1].append(self.resizedImages[i])
            for i in range(self.totalPages * 2, self.totalImages, 1):
                self.imageStacks[2].append(self.resizedImages[i])
        if self.difference != 0:
            for i in range(0, self.totalPages, 1):
                self.imageStacks[0].append(self.resizedImages[i])
            for i in range(self.totalPages, self.totalPages * 2, 1):
                self.imageStacks[1].append(self.resizedImages[i])
            for i in range(self.totalPages * 2, self.totalImages, 1): 
                self.imageStacks[2].append(self.resizedImages[i])

        if len(self.imageStacks[0]) % 2 != 0:
            if self.imageStacks[1] and self.imageStacks[1][0]:
                self.imageStacks[0].append(self.imageStacks[1][0])

            if self.imageStacks[2]:
                if self.imageStacks[2][0]:
                    self.imageStacks[1].append(self.imageStacks[2][0])

                # HACK with `elif self.imageStacks[2][1]:` 3 and 7 bug
                # with `if` instead the last page of 1st stack disapears
                # page 8 and page 20 for example, go figure!
                if len(self.resizedImages) == 3:
                    pass 
                elif len(self.resizedImages) == 7:
                    pass
                elif self.imageStacks[2][1]:
                    self.imageStacks[1].append(self.imageStacks[2][1])

            if len(self.imageStacks[1]) - 1 >= 0:
                del self.imageStacks[1][0]
            if len(self.imageStacks[2]) - 1 >= 0:
                del self.imageStacks[2][0]
            if len(self.imageStacks[2]) - 1 >= 0:
                del self.imageStacks[2][0]

        for i in range(0, len(self.imageStacks[0]), 1):
            self.message = f'Stacking image {i}'
            print(self.message)
            finalPage = Image.new(
                "RGB", (self.optimalWidth, self.optimalHeightTotal), "white"
            )
            if i % 2 == 0:
                finalPage.paste(self.imageStacks[0][i], (0, 0))
                if self.imageStacks[1] and len(self.imageStacks[1]) - 1 >= i:
                    finalPage.paste(self.imageStacks[1][i], (0, self.optimalHeight))
                if self.imageStacks[2] and len(self.imageStacks[2]) - 1 >= i:
                    finalPage.paste(self.imageStacks[2][i], (0, self.optimalHeight * 2))
                    pass
                pass
            else:
                finalPage.paste(self.imageStacks[0][i], (0, self.optimalHeight * 2))
                if self.imageStacks[1] and len(self.imageStacks[1]) - 1 >= i:
                    finalPage.paste(self.imageStacks[1][i], (0, self.optimalHeight))
                if self.imageStacks[2] and len(self.imageStacks[2]) - 1 >= i:
                    finalPage.paste(self.imageStacks[2][i], (0, 0))
                    pass
                pass
            self.finalPages.append(finalPage)

    def savePdf(self):
        self.message = 'Saving images'
        print(self.message)


        self.outputName = self.outputName + ".pdf"
        self.finalPages[0].save(
            self.outputLocation + self.outputName,
            save_all=True,
            append_images=self.finalPages[1:],
        )


class Ui(QtWidgets.QDialog):
    def __init__(self):
        super(Ui, self).__init__()
        uiFile = os.path.join(BASEDIR, "rsc", "window.ui")
        loadUi(uiFile, self)
        self.pecha = Pecha()
        self.setWindowTitle("Pecha Printer")
        self.setWindowIcon(QtGui.QIcon(os.path.join(BASEDIR, "rsc", "print.ico")))
        self.setWindowFlag(Qt.CustomizeWindowHint, True)
        self.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
        self.stackedWidget.setCurrentIndex(0)
        self.stackedWidget_2.setCurrentIndex(0)
        self.pushButton.clicked.connect(self.button1)
        self.pushButton_2.clicked.connect(self.button2)
        self.pushButton_3.clicked.connect(self.button3and5)
        self.pushButton_4.clicked.connect(self.button4)
        self.pushButton_5.clicked.connect(self.button3and5)
        self.pushButton_6.clicked.connect(self.restart)
        self.pushButton_7.clicked.connect(self.close)
        self.comboBox.currentTextChanged.connect(self.combo)
        self.spinBox_end.setStyleSheet("color: grey")
        self.label_7.setStyleSheet("color: grey")
        self.label_8.setStyleSheet("color: grey")
        self.label_9.setStyleSheet("color: grey")
        self.label_10.setStyleSheet("color: grey")
        self.spinBox_start.valueChanged.connect(self.changePageSpan)
        self.spinBox_end.valueChanged.connect(self.changePageSpan)
        self.checkBox.stateChanged.connect(self.activateSpan)
        self.radioButton.toggled.connect(self.startingSide)

        self.setDefaults()

    def setDefaults(self):
        self.checkBox.setChecked(False)
        self.radioButton_2.setChecked(True)
        self.pagePicker.setEnabled(False)
        self.spinBox_start.setValue(5)
        self.spinBox_end.setValue(0)


    def restart(self):
        self.pecha = Pecha()
        self.pecha.tempJpgs = []
        self.setDefaults()
        self.button3and5()
        self.pushButton.click()

    # define if the starting side is recto or verso
    def startingSide(self):
        if self.radioButton.isChecked():
            self.pecha.startSide = 'B'
        else:
            self.pecha.startSide = 'A'


    def activateSpan(self):
        self.pagePicker.setEnabled(not self.pagePicker.isEnabled())
        self.spinBox_start.setStyleSheet("")
        self.spinBox_end.setStyleSheet("")
        self.startPage = self.spinBox_start.value()
        self.endPage = self.spinBox_end.value()
        self.changePageSpan()

    def changePageSpan(self):
        self.startPage = self.spinBox_start.value()
        self.endPage = self.spinBox_end.value()
        self.spinBox_end.setStyleSheet("color: grey")

        # flag cases where less than 2 pages are selected
        if self.pagePicker.isEnabled() and self.startPage+1 > self.endPage and self.endPage != 0:
            self.spinBox_start.setStyleSheet("color: red")
            self.spinBox_end.setStyleSheet("color: red")
            self.pushButton_2.setEnabled(False)
        elif self.endPage == 0:
            self.spinBox_end.setStyleSheet("color: grey")
            self.spinBox_start.setStyleSheet("")
            self.pushButton_2.setEnabled(True)

            # flag less than 2 pages
            if self.startPage > self.pecha.tempJpgsNumber-1 and self.pagePicker.isEnabled():
                self.spinBox_start.setStyleSheet("color: red")
                self.spinBox_end.setStyleSheet("color: red")
                self.pushButton_2.setEnabled(False)
        else:
            self.spinBox_start.setStyleSheet("")
            self.spinBox_end.setStyleSheet("")
            self.pushButton_2.setEnabled(True)

    def button1(self):
        self.pushButton_2.setFocus()
        options = QtWidgets.QFileDialog.Options()
        dir = os.path.expanduser('~/Desktop/')
        filters = "པར་རིགས། (*.png *.jpg *.jpeg *.tif *.tiff *.gif *.pdf);; ཡོངས་རྫོགས། ()"
        fileLocation, _ = QtWidgets.QFileDialog.getOpenFileNames(
            self,
            "པར་འདེམས།",
            dir,
            filters,
            options=options,
        )
        self.stackedWidget_2.setCurrentIndex(1)
        self.label_17.setText(self.pecha.message)
        QtGui.QGuiApplication.processEvents()

        if not fileLocation:
            self.stackedWidget_2.setCurrentIndex(0)
        elif fileLocation:
            self.parentDir = os.path.basename(os.path.dirname(fileLocation[0]))
            # self.label_8.setStyleSheet("font: italic; color: grey")
            self.label_8.setStyleSheet("color: blue")

            self.pushButton_2.setEnabled(True)
            # check if several files are selected
            if len(fileLocation) > 1:
                self.pecha.inputLocation = fileLocation
                multiplePdfs = False
                for i in range(0, len(fileLocation), 1):
                    self.fileLocationPartition = fileLocation[i].rpartition("/")
                    # error message if it's multiple pdfs
                    if self.fileLocationPartition[2].rpartition(".")[2] == "pdf":
                        self.label_8.setStyleSheet('color: red')
                        self.label_8.setText(
                            "PDF གཅིག་རང་དང་ཡང་ན། པར་ཁོ་ན་ཡིན་དགོས།"
                        )
                        self.pushButton_2.setEnabled(False)
                        multiplePdfs = True
                        break
                # if it's multiple images display first 2 or 3 filenames
                if multiplePdfs == False:
                    self.frame.setHidden(not self.frame.isHidden())

                    if len(fileLocation) == 1:
                        self.label_8.setStyleSheet('color: red')
                        self.label_8.setText(
                            "PDF གཅིག་རང་དང་ཡང་ན། པར་ཁོ་ན་ཡིན་དགོས།"
                        )
                        self.pushButton_2.setEnabled(False)

                    elif len(fileLocation) == 2:
                        self.label_8.setText(
                            "ཡིག་ཆ། "
                            + fileLocation[0].rpartition("/")[2]
                            + ", "
                            + fileLocation[1].rpartition("/")[2]
                        )
                    elif len(fileLocation) >= 3:
                        self.label_8.setText(
                            "ཡིག་ཆ། "
                            + fileLocation[0].rpartition("/")[2]
                            + ", ... "
                            + fileLocation[-1].rpartition("/")[2]
                        )
                    # display new file name (folder for images)
                    self.outFilePrefix = self.parentDir
                    self.outFileName = self.outFilePrefix + f"_{self.pecha.outputSize}"
                    self.textEdit_2.setText(self.outFileName)
                    self.pecha.inputFormat = "img"
                    self.pecha.inputLocation = fileLocation

            elif len(fileLocation) == 1:
                self.span = []
                self.fileLocationPartition = fileLocation[0].rpartition("/")
                # self.label_8.setText("ཡིག་ཆ། " + self.fileLocationPartition[2])
                self.outFilePrefix = self.fileLocationPartition[2].rpartition(".")[0]
                self.outFileName = self.outFilePrefix + f"_{self.pecha.outputSize}"
                self.textEdit_2.setText(self.outFileName)
                if self.fileLocationPartition[2].rpartition(".")[2] == "pdf":
                    self.frame.setHidden(False)
                    self.pecha.inputFormat = "pdf"
                    self.pecha.inputLocation = fileLocation[0]
                    # extract images from PDF to temp folder and create list
                    self.pecha.extractImages()
                    if self.pecha.tempJpgsNumber < 2:              
                        self.label_8.setStyleSheet('color: red')
                        self.label_8.setText("ཉུང་མཐར་པར་གཉིས་དགོས།")
                        self.pushButton_2.setEnabled(False)
                    else:
                        self.spinBox_end.setMaximum(self.pecha.tempJpgsNumber)
                        self.label_8.setText(f"ཡིག་ཆ། {self.fileLocationPartition[2]}    ཤོག་གྲངས། {self.pecha.tempJpgsNumber}")
                else:
                    self.label_8.setStyleSheet('color: red')
                    self.label_8.setText("ཉུང་མཐར་པར་གཉིས་དགོས།")
                    self.pushButton_2.setEnabled(False)

            self.pecha.outputLocation = self.fileLocationPartition[0] + "/"

            self.stackedWidget.setCurrentIndex(0)
            self.stackedWidget_2.setCurrentIndex(2)

    def setPageSpan(self):
        self.startPage = self.spinBox_start.value()
        self.endPage = self.spinBox_end.value()
        start = self.startPage-1
        end = self.endPage

        if self.pagePicker.isEnabled(): 
            if self.endPage == 0:
                del self.pecha.tempJpgs[:start]
            elif self.endPage != 0:
                del self.pecha.tempJpgs[end:]
                del self.pecha.tempJpgs[:start]
        pass

    def button2(self):
        self.setPageSpan()
        self.stackedWidget.setCurrentIndex(1)
        self.pushButton_4.setFocus()

    def button3and5(self):
        self.stackedWidget.setCurrentIndex(0)
        self.stackedWidget_2.setCurrentIndex(0)

    def button4(self):
        self.stackedWidget.setCurrentIndex(2)
        self.stackedWidget_3.setCurrentIndex(0)
        self.label.setText(self.pecha.message)
        QtGui.QGuiApplication.processEvents()

        self.pecha.outputName = self.textEdit_2.text()
        if self.comboBox.currentIndex() == 0:
            self.pecha.outputSize = "A4"
        elif self.comboBox.currentIndex() == 1:
            self.pecha.outputSize = "A3"

        process = self.pecha.Main()
        if process == 1:
            self.stackedWidget_3.setCurrentIndex(1)
        self.pushButton_6.setFocus()
    
    def combo(self):
        if self.comboBox.currentIndex() == 0:
            self.pecha.outputSize = "A4"
        elif self.comboBox.currentIndex() == 1:
            self.pecha.outputSize = "A3"
        # update name suffix
        self.outFileName = self.outFilePrefix + f"_{self.pecha.outputSize}"
        self.textEdit_2.setText(self.outFileName)

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    window.show()
    try:
        sys.exit(app.exec_())
    except:
        sys.exit(1)

if __name__ == "__main__":
    main()