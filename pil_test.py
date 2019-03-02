from PIL import Image
from natsort import natsorted
import os
import string
import random
import shutil

inputFormat = "jpg" #pdf or jpg
inputLocation = "./inputFiles/" #A folder of images or a pdf file
outputName = "out"
outputLocation = "./"
ouputSize = "A4"#A4 or A3

#FILE IMPORTATION
#Creating a temporary folder
tempFolder = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
if os.path.isdir("./%s/" % tempFolder):
	tempFolder = ''.join(random.choices(string.ascii_uppercase + string.digits, k=15))
os.mkdir("./%s/" % tempFolder)

if inputFormat == "pdf":
	#Extract the images from a pdf
	file = open(inputLocation, "rb")
	pdf = file.read()

	startmark = b"\xff\xd8"
	startfix = 0
	endmark = b"\xff\xd9"
	endfix = 2
	i = 0

	njpg = 1
	while True:
		istream = pdf.find(b"stream", i)
		if istream < 0:
			break

		istart = pdf.find(startmark, istream, istream+20)
		if istart < 0:
			i = istream+20
			continue

		iend = pdf.find(b"endstream", istart)
		if iend < 0:
			raise Exception("Didn't find end of stream!")

		iend = pdf.find(endmark, iend-20)
		if iend < 0:
			raise Exception("Didn't find end of JPG!")

		istart += startfix
		iend += endfix
		#print("JPG %d from %d to %d" % (njpg, istart, iend))
		jpg = pdf[istart:iend]

		#Save the images in the temporary folder
		if njpg < 10:
			num = 0
			jpgfile = open("./%s/jpg%d%d.jpg" % (tempFolder, num, njpg), "wb")
		else:
			jpgfile = open("./%s/jpg%d.jpg" % (tempFolder, njpg), "wb")
			pass

		jpgfile.write(jpg)
		jpgfile.close()
 
		njpg += 1
		i = iend

elif inputFormat == "jpg":
	#Save the images in the temporary folder
	inputJpgs = [file for file in natsorted(os.listdir(inputLocation)) if file.endswith(".jpg")]
	#print(inputJpgs)
	for i in range(len(inputJpgs)):
		currentImg = Image.open(inputLocation+inputJpgs[i])
		if i < 9:
			num = 0
			currentImg.save('./%s/jpg%d%d.jpg' % (tempFolder, num, (i+1)))
		else:
			currentImg.save('./%s/jpg%d.jpg' % (tempFolder, (i+1)))
			pass
		pass
	pass

#Defining variables
jpgImages = [file for file in os.listdir('./%s/' % tempFolder) if file.endswith(".jpg")]
#jpgImages.sort()
files = []
totalFiles = len(jpgImages)
finalFiles = []
totalPages = totalFiles // 3
difference = totalFiles % 3
aspectRatio = 3508 / 827

#print(jpgImages)
#print(totalFiles)
#print(totalPages)
#print(difference)

if difference != 0:
	totalPages += 1

#RESIZE IMAGES
if ouputSize == "A4":
	optimalWidth, optimalHeight, optimalHeightTotal = (3508, 827, 2481)
elif ouputSize == "A3":
	optimalWidth, optimalHeight, optimalHeightTotal = (4961, 1168, 3508)

for i in range(0,totalFiles,1):
	currentImg = Image.open('./%s/'% tempFolder+jpgImages[i])
	width, height = currentImg.size
	currentAspectRatio = width / height
	if aspectRatio >= currentAspectRatio:
		proportionalWith = (optimalHeight / height)*width
		resizedImage = currentImg.resize([int(proportionalWith), optimalHeight], resample=0)
		resizedWidth, resizedHeight = resizedImage.size
		newImage = Image.new("RGB", (optimalWidth, optimalHeight),(255,255,255))
		newImage.paste(resizedImage, ((optimalWidth-resizedWidth)//2, (optimalHeight-resizedHeight)//2))
	else:
		proportionalHeight = (optimalWidth / width)*height
		resizedImage = currentImg.resize([optimalWidth, int(proportionalHeight)], resample=0)
		resizedWidth, resizedHeight = resizedImage.size
		newImage = Image.new("RGB", (optimalWidth, optimalHeight),(255,255,255))
		newImage.paste(resizedImage, ((optimalWidth-resizedWidth)//2, (optimalHeight-resizedHeight)//2))
		pass
	files.append(newImage)

imgPile = [[], [], []] #Multidimensional array that represent the 3 image piles (top, medium and bottom)

#DIVIDE THE IMAGES IN THE 3 PILES
if difference == 0:
	for i in range(0,totalPages,1):
		imgPile[0].append(files[i])
	for i in range(totalPages,totalPages*2,1):
		imgPile[1].append(files[i])
	for i in range(totalPages*2,totalFiles,1):
		imgPile[2].append(files[i])
if difference != 0:
	for i in range(0,totalPages,1):
		imgPile[0].append(files[i])
	for i in range(totalPages,totalPages*2,1):
		imgPile[1].append(files[i])
	for i in range(totalPages*2,totalFiles,1):
		imgPile[2].append(files[i])

#print(imgPile[0])
#print(imgPile[1])
#print(imgPile[2])

#REORGANIZE THE 3 PILES SO THEY ARE ALWAYS PAIR
if len(imgPile[0]) % 2 != 0:
	imgPile[0].append(imgPile[1][0])
	imgPile[1].append(imgPile[2][0])
	imgPile[1].append(imgPile[2][1])
	del imgPile[1][0]
	del imgPile[2][1]
	del imgPile[2][0]

#print(imgPile[0])
#print(imgPile[1])
#print(imgPile[2])

#JOINING THE IMAGES FROM THE 3 PILES IN 1 SAME IMAGE
for i in range(0, len(imgPile[0]), 1):
	finalPage = Image.new('RGB', (optimalWidth, optimalHeightTotal), "white")
	if i % 2 == 0:
		finalPage.paste(imgPile[0][i],(0, 0))
		finalPage.paste(imgPile[1][i],(0, optimalHeight))
		if len(imgPile[2])-1 >= i:
			finalPage.paste(imgPile[2][i],(0, optimalHeight*2))
			pass
	else:
		finalPage.paste(imgPile[0][i],(0, optimalHeight*2))
		finalPage.paste(imgPile[1][i],(0, optimalHeight))
		if len(imgPile[2])-1 >= i:
			finalPage.paste(imgPile[2][i],(0, 0))
			pass
		pass		
	finalFiles.append(finalPage)

#SAVE AS NEW PDF
outputName = outputName+".pdf"
finalFiles[0].save(outputLocation+outputName, save_all=True, append_images=finalFiles[1:])

shutil.rmtree('./%s/' % tempFolder)