from PIL import Image
from natsort import natsorted
from pdf2image import convert_from_path
import os

class Pecha(object):
	def __init__(self, inputFormat, inputLocation, outputName, outputLocation, outputSize):
		super(Pecha, self).__init__()
		self.inputFormat = inputFormat
		self.inputLocation = inputLocation
		self.outputName = outputName
		self.outputLocation = outputLocation
		self.outputSize = outputSize
		self.jpgImages = []
		self.totalImages = 0
		self.resizedImages = []
		self.imagesStack = [[], [], []]
		self.finalFiles = []
		self.totalPages = 0
		self.difference = 0
		self.aspectRatio = 3508 / 827
		self.optimalWidth = 0
		self.optimalHeight = 0
		self.optimalHeightTotal = 0
	
	def potiMaker(self):
		if self.outputSize == "A4":
			self.optimalWidth, self.optimalHeight, self.optimalHeightTotal = (3508, 827, 2481)
		elif self.outputSize == "A3":
			self.optimalWidth, self.optimalHeight, self.optimalHeightTotal = (4961, 1168, 3508)

		self.collectFiles()
		self.resizeImages()
		self.orderImages()
		self.savePdf()
		print("Done! ;)")

	def collectFiles(self):
		if self.inputFormat == "pdf":
#			file = open(self.inputLocation, "rb")
#			pdf = file.read()
#
#			startmark = b"\xff\xd8"
#			startfix = 0
#			endmark = b"\xff\xd9"
#			endfix = 2
#			i = 0
#
#			njpg = 1
#			while True:
#				istream = pdf.find(b"stream", i)
#				if istream < 0:
#					break
#
#				istart = pdf.find(startmark, istream, istream+20)
#				if istart < 0:
#					i = istream+20
#					continue
#
#				iend = pdf.find(b"endstream", istart)
#				if iend < 0:
#					raise Exception("Didn't find end of stream!")
#
#				iend = pdf.find(endmark, iend-20)
#				if iend < 0:
#					raise Exception("Didn't find end of JPG!")
#
#				istart += startfix
#				iend += endfix
#				jpg = pdf[istart:iend]
#
#				self.jpgImages.append(Image.frombytes('RGB', (self.optimalWidth,self.optimalHeight), jpg))
#
#				njpg += 1
#				i = iend
			self.jpgImages = convert_from_path(self.inputLocation, 300)

		elif self.inputFormat == "jpg":
			inputJpgs = [file for file in natsorted(os.listdir(self.inputLocation)) if file.endswith(".jpg")]
			for i in range(len(inputJpgs)):
				currentImg = Image.open(self.inputLocation+inputJpgs[i])
				self.jpgImages.append(currentImg)
			pass

		self.totalImages = len(self.jpgImages)
		self.totalPages = self.totalImages // 3
		self.difference = self.totalImages % 3
		if self.difference != 0:
			self.totalPages += 1
			pass

	def resizeImages(self):
		for i in range(0,self.totalImages,1):
			currentImg = self.jpgImages[i]
			width, height = currentImg.size
			currentAspectRatio = width / height
			if self.aspectRatio >= currentAspectRatio:
				proportionalWith = (self.optimalHeight / height)*width
				resizedImage = currentImg.resize([int(proportionalWith), self.optimalHeight], resample=0)
				resizedWidth, resizedHeight = resizedImage.size
				newImage = Image.new("RGB", (self.optimalWidth, self.optimalHeight),(255,255,255))
				newImage.paste(resizedImage, ((self.optimalWidth-resizedWidth)//2, (self.optimalHeight-resizedHeight)//2))
			else:
				proportionalHeight = (self.optimalWidth / width)*height
				resizedImage = currentImg.resize([self.optimalWidth, int(proportionalHeight)], resample=0)
				resizedWidth, resizedHeight = resizedImage.size
				newImage = Image.new("RGB", (self.optimalWidth, self.optimalHeight),(255,255,255))
				newImage.paste(resizedImage, ((self.optimalWidth-resizedWidth)//2, (self.optimalHeight-resizedHeight)//2))
				pass
			self.resizedImages.append(newImage)

	def orderImages(self):
		if self.difference == 0:
			for i in range(0,self.totalPages,1):
				self.imagesStack[0].append(self.resizedImages[i])
			for i in range(self.totalPages,self.totalPages*2,1):
				self.imagesStack[1].append(self.resizedImages[i])
			for i in range(self.totalPages*2,self.totalImages,1):
				self.imagesStack[2].append(self.resizedImages[i])
		if self.difference != 0:
			for i in range(0,self.totalPages,1):
				self.imagesStack[0].append(self.resizedImages[i])
			for i in range(self.totalPages,self.totalPages*2,1):
				self.imagesStack[1].append(self.resizedImages[i])
			for i in range(self.totalPages*2,self.totalImages,1):
				self.imagesStack[2].append(self.resizedImages[i])

		if len(self.imagesStack[0]) % 2 != 0:
			self.imagesStack[0].append(self.imagesStack[1][0])
			self.imagesStack[1].append(self.imagesStack[2][0])
			self.imagesStack[1].append(self.imagesStack[2][1])
			del self.imagesStack[1][0]
			del self.imagesStack[2][1]
			del self.imagesStack[2][0]

		for i in range(0, len(self.imagesStack[0]), 1):
			finalPage = Image.new('RGB', (self.optimalWidth, self.optimalHeightTotal), "white")
			if i % 2 == 0:
				finalPage.paste(self.imagesStack[0][i],(0, 0))
				finalPage.paste(self.imagesStack[1][i],(0, self.optimalHeight))
				if len(self.imagesStack[2])-1 >= i:
					finalPage.paste(self.imagesStack[2][i],(0, self.optimalHeight*2))
					pass
			else:
				finalPage.paste(self.imagesStack[0][i],(0, self.optimalHeight*2))
				finalPage.paste(self.imagesStack[1][i],(0, self.optimalHeight))
				if len(self.imagesStack[2])-1 >= i:
					finalPage.paste(self.imagesStack[2][i],(0, 0))
					pass
				pass		
			self.finalFiles.append(finalPage)

	def savePdf(self):
		self.outputName = self.outputName+".pdf"
		self.finalFiles[0].save(self.outputLocation+self.outputName, save_all=True, append_images=self.finalFiles[1:])






#inputFormat, inputLocation, ouputName, outputLocation, outputSize

#poti = Pecha("pdf", "./inputFiles/test.pdf", "out", "./", "A4")
poti = Pecha("jpg", "./inputFiles/", "out", "./", "A4")

poti.potiMaker()