### Changed:
#		potiMaker()

from PIL import Image
from natsort import natsorted
import os, string, subprocess, shutil, argparse

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
		self.imageStacks = [[], [], []]
		self.finalPages = []
		self.totalPages = 0
		self.difference = 0
		self.aspectRatio = 3508 / 827
		self.optimalWidth = 0
		self.optimalHeight = 0
		self.optimalHeightTotal = 0
	
	def Main(self):
		if self.outputSize == "A4":
			self.optimalWidth, self.optimalHeight, self.optimalHeightTotal = (3508, 827, 2481)
		elif self.outputSize == "A3":
			self.optimalWidth, self.optimalHeight, self.optimalHeightTotal = (4961, 1168, 3508)

		if self.inputFormat == "img":
			self.collectFiles()
			self.resizeImages()
			self.orderImages()
			self.savePdf()
			print("Done! ;)")
		elif self.inputFormat == "pdf":
			os.mkdir("./tempFolder/")
			p = subprocess.Popen("pdfimages -all %s ./tempFolder/tempImg" % self.inputLocation)			
			self.inputLocation = "./tempfolder/"
			while p.poll() == None:
#				print("Waiting")
				if p.poll() != None:
					break

			self.collectFiles()
			self.resizeImages()
			self.orderImages()
			self.savePdf()
			print("Done! ;)")
			pass

	def collectFiles(self):
		inputJpgs = [file for file in natsorted(os.listdir(self.inputLocation)) if file.endswith(".jpg") or file.endswith(".png") or file.endswith(".tiff") ]
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
				self.imageStacks[0].append(self.resizedImages[i])
			for i in range(self.totalPages,self.totalPages*2,1):
				self.imageStacks[1].append(self.resizedImages[i])
			for i in range(self.totalPages*2,self.totalImages,1):
				self.imageStacks[2].append(self.resizedImages[i])
		if self.difference != 0:
			for i in range(0,self.totalPages,1):
				self.imageStacks[0].append(self.resizedImages[i])
			for i in range(self.totalPages,self.totalPages*2,1):
				self.imageStacks[1].append(self.resizedImages[i])
			for i in range(self.totalPages*2,self.totalImages,1):
				self.imageStacks[2].append(self.resizedImages[i])

		if len(self.imageStacks[0]) % 2 != 0:
			self.imageStacks[0].append(self.imageStacks[1][0])
			self.imageStacks[1].append(self.imageStacks[2][0])
			self.imageStacks[1].append(self.imageStacks[2][1])
			del self.imageStacks[1][0]
			del self.imageStacks[2][1]
			del self.imageStacks[2][0]

		for i in range(0, len(self.imageStacks[0]), 1):
			finalPage = Image.new('RGB', (self.optimalWidth, self.optimalHeightTotal), "white")
			if i % 2 == 0:
				finalPage.paste(self.imageStacks[0][i],(0, 0))
				finalPage.paste(self.imageStacks[1][i],(0, self.optimalHeight))
				if len(self.imageStacks[2])-1 >= i:
					finalPage.paste(self.imageStacks[2][i],(0, self.optimalHeight*2))
					pass
			else:
				finalPage.paste(self.imageStacks[0][i],(0, self.optimalHeight*2))
				finalPage.paste(self.imageStacks[1][i],(0, self.optimalHeight))
				if len(self.imageStacks[2])-1 >= i:
					finalPage.paste(self.imageStacks[2][i],(0, 0))
					pass
				pass		
			self.finalPages.append(finalPage)

	def savePdf(self):
		self.outputName = self.outputName+".pdf"
		self.finalPages[0].save(self.outputLocation+self.outputName, save_all=True, append_images=self.finalPages[1:])
		if os.path.isdir('./tempFolder/'):
			shutil.rmtree('./tempFolder/')

### Added:

def potiMaker():
	parser = argparse.ArgumentParser()
	parser.add_argument("input_format", help="Input format: [pdf] or [img] (img includes: jpg, png and tiff)", type=str)
	parser.add_argument("input_location", help="Input location: pdf file location or image folder location", type=str)
	parser.add_argument("output_name", help="Output name", type=str)
	parser.add_argument("output_location", help="Output location", type=str)
	parser.add_argument("output_size", help="Output size: [A4] or [A3]", type=str)
	args = parser.parse_args()

	if not (args.input_format or args.input_location or args.output_name or args.output_location or args.output_size):
		parser.error('No arguments provided, -h for help')

	poti = Pecha(args.input_format, args.input_location, args.output_name, args.output_location, args.output_size)

	### From PDF
	#poti = Pecha("pdf", "./inputFiles/test.pdf", "out", "./", "A4")

	### From image folder
	#poti = Pecha("img", "./format test/", "out", "./", "A4")

	### From input:
		#input_format: pdf / img
		#input_location: pdf file / image folder
		#output_name
		#output_location
		#output_size: A4 / A3
	#poti = Pecha(input("Enter input format:"), input("Enter input location:"), input("Enter output name:"), input("Enter output location:"), input("Enter output size:"))

	poti.Main()

if __name__ == '__main__':
	potiMaker()