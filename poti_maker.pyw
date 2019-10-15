# TODO when images get folder name + _size
# when changing size change the new file name

import sys
import os
import struct
import platform
import subprocess
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog
from PyQt5.uic import loadUi
from PIL import Image
from natsort import natsorted
import shutil


class Poti(object):
    def __init__(self):
        super(Poti, self).__init__()
        self.inputFormat = ""
        self.inputLocation = ""
        self.outputName = ""
        self.outputLocation = ""
        self.outputSize = "A4"
        self.jpgImages = []
        self.totalImages = 0
        self.resizedImages = []
        self.imageStacks = [[], [], []]
        self.finalPages = []
        self.totalPages = 0
        self.difference = 0
        self.aspectRatio = 3508 / 827
        self.optimalWidth = 0
        self.optimalHeight = 0
        self.optimalHeightTotal = 0
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
        )
        self.pdfimagesLocation = "{cwd}/dep/{platform}/bin{bits}/pdfimages{ext}".format(
            cwd=os.getcwd(),
            platform=("Mac" if platform.system() == "Darwin" else platform.system()),
            bits=8 * struct.calcsize("P"),
            ext=(".exe" if platform.system() == "Windows" else ""),
        )

    def Main(self):
        self.collectFiles()
        self.resizeImages()
        self.orderImages()
        self.savePdf()
        print("Done! ;)")
        return 1

    def collectFiles(self):
        if self.inputFormat == "img":
            for i in range(len(self.inputLocation)):
                currentImg = Image.open(self.inputLocation[i])
                self.jpgImages.append(currentImg)

        elif self.inputFormat == "pdf":
            path = "./tempFolder/"
            if not os.path.exists(path):
                os.makedirs(path)
            else:
                shutil.rmtree(path)  # removes all the subdirectories!
                os.makedirs(path)
            # 	os.path.join adds the trailing slash that's silently deleted by abspath
            p = subprocess.Popen(
                [
                    self.pdfimagesLocation,
                    "-j",
                    self.inputLocation,
                    os.path.join(os.path.abspath(path), ""),
                ]
            )
            self.inputLocation = "./tempFolder/"
            while p.poll() == None:
                # 				print("Waiting")
                if p.poll() != None:
                    break

            inputJpgs = [
                file
                for file in natsorted(os.listdir(self.inputLocation))
                if file.endswith(self.imgExt)
            ]
            # only keep required span
            for i in range(len(inputJpgs)):
                currentImg = Image.open(self.inputLocation + inputJpgs[i])
                self.jpgImages.append(currentImg)
            pass

        self.totalImages = len(self.jpgImages)
        self.totalPages = self.totalImages // 3
        self.difference = self.totalImages % 3
        if self.difference != 0:
            self.totalPages += 1
            pass

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

                elif self.imageStacks[2][1]:
                    self.imageStacks[1].append(self.imageStacks[2][1])

            if len(self.imageStacks[1]) - 1 >= 0:
                del self.imageStacks[1][0]
            if len(self.imageStacks[2]) - 1 >= 0:
                del self.imageStacks[2][0]
            if len(self.imageStacks[2]) - 1 >= 0:
                del self.imageStacks[2][0]

        for i in range(0, len(self.imageStacks[0]), 1):
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
        self.outputName = self.outputName + ".pdf"
        self.finalPages[0].save(
            self.outputLocation + self.outputName,
            save_all=True,
            append_images=self.finalPages[1:],
        )
        if os.path.isdir("./tempFolder/"):
            shutil.rmtree("./tempFolder/")


# Added


class Ui(QDialog):
    def __init__(self):
        super(Ui, self).__init__()
        loadUi("./window.ui", self)
        self.setWindowTitle("Poti Maker")
        self.setWindowIcon(QtGui.QIcon("print.ico"))
        self.stackedWidget.setCurrentIndex(0)
        self.stackedWidget_2.setCurrentIndex(0)
        self.pushButton.clicked.connect(self.button1)
        self.pushButton_2.clicked.connect(self.button2)
        self.pushButton_3.clicked.connect(self.button3and5)
        self.pushButton_4.clicked.connect(self.button4)
        self.pushButton_5.clicked.connect(self.button3and5)
        self.pushButton_6.clicked.connect(self.close)
        self.comboBox.currentTextChanged.connect(self.combo)
        self.spinBox_start.currentTextChanged.connect(self.spinbox)
        self.spinBox_end.currentTextChanged.connect(self.spinbox)
        self.poti = Poti()

    def spinbox(self):
        
        pass


    def button1(self):
        self.pushButton_2.setFocus()
        options = QFileDialog.Options()
        dir = os.path.expanduser('~/Desktop/')
        filters = "པར་རིགས། (*.png *.jpg *.jpeg *.tif *.tiff *.gif *.pdf);; ཡོངས་རྫོགས། ()"
        fileLocation, _ = QFileDialog.getOpenFileNames(
            self,
            "པར་འདེམས།",
            dir,
            filters,
            options=options,
        )

        if fileLocation:
            self.parentDir = os.path.basename(os.path.dirname(fileLocation[0]))
            self.label_8.setStyleSheet('')

            self.pushButton_2.setEnabled(True)
            # check if several files are selected
            if len(fileLocation) > 1:
                self.poti.inputLocation = fileLocation
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
                    self.pagePicker.setHidden(not self.pagePicker.isHidden())
                    if len(fileLocation) == 2:
                        self.label_8.setText(
                            fileLocation[0].rpartition("/")[2]
                            + ", "
                            + fileLocation[1].rpartition("/")[2]
                        )
                    elif len(fileLocation) == 3:
                        self.label_8.setText(
                            fileLocation[0].rpartition("/")[2]
                            + ", "
                            + fileLocation[1].rpartition("/")[2]
                            + ", "
                            + fileLocation[2].rpartition("/")[2]
                        )
                    elif len(fileLocation) == 4:
                        self.label_8.setText(
                            fileLocation[0].rpartition("/")[2]
                            + ", "
                            + fileLocation[1].rpartition("/")[2]
                            + ", "
                            + fileLocation[2].rpartition("/")[2]
                            + ", "
                            + fileLocation[3].rpartition("/")[2]
                        )
                    elif len(fileLocation) > 4:
                        self.label_8.setText(
                            fileLocation[0].rpartition("/")[2]
                            + ", "
                            + fileLocation[1].rpartition("/")[2]
                            + "   ...   "
                            + fileLocation[2].rpartition("/")[2]
                            + ", "
                            + fileLocation[-1].rpartition("/")[2]
                        )
                    # display new file name (folder for images)
                    self.outFilePrefix = self.parentDir
                    self.outFileName = self.outFilePrefix + f"_{self.poti.outputSize}"
                    self.textEdit_2.setText(self.outFileName)
                    self.poti.inputFormat = "img"
                    self.poti.inputLocation = fileLocation

            elif len(fileLocation) == 1:
                self.span = []
                self.fileLocationPartition = fileLocation[0].rpartition("/")
                self.label_8.setText(self.fileLocationPartition[2])
                self.outFilePrefix = self.fileLocationPartition[2].rpartition(".")[0]
                self.outFileName = self.outFilePrefix + f"_{self.poti.outputSize}"
                self.textEdit_2.setText(self.outFileName)
                if self.fileLocationPartition[2].rpartition(".")[2] == "pdf":
                    self.pagePicker.setHidden(False)
                    self.poti.inputFormat = "pdf"
                    self.poti.inputLocation = fileLocation[0]
                else:
                    self.label_8.setStyleSheet('color: red')
                    self.label_8.setText("ཉུང་མཐར་པར་གཉིས་དགོས།")
                    self.pushButton_2.setEnabled(False)

            self.poti.outputLocation = self.fileLocationPartition[0] + "/"

            self.stackedWidget_2.setCurrentIndex(1)

    def button2(self):
        self.stackedWidget.setCurrentIndex(1)
        self.pushButton_4.setFocus()

    def button3and5(self):
        self.stackedWidget.setCurrentIndex(0)
        self.stackedWidget_2.setCurrentIndex(0)

    def button4(self):
        self.poti.outputName = self.textEdit_2.toPlainText()
        if self.comboBox.currentIndex() == 0:
            self.poti.outputSize = "A4"
        elif self.comboBox.currentIndex() == 1:
            self.poti.outputSize = "A3"
        self.stackedWidget.setCurrentIndex(2)
        self.stackedWidget_3.setCurrentIndex(0)
        process = self.poti.Main()
        if process == 1:
            self.stackedWidget_3.setCurrentIndex(1)
        self.pushButton_6.setFocus()
    
    def combo(self):
        if self.comboBox.currentIndex() == 0:
            self.poti.outputSize = "A4"
        elif self.comboBox.currentIndex() == 1:
            self.poti.outputSize = "A3"
        # update name suffix
        self.outFileName = self.outFilePrefix + f"_{self.poti.outputSize}"
        self.textEdit_2.setText(self.outFileName)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Ui()
    window.show()
    sys.exit(app.exec_())
