from PIL import Image
import os

#DEFINE VARIABLES
jpgImages = [file for file in os.listdir('./imgs/') if file.endswith(".jpg")] #Files location and file type from imput
files = []
totalFiles = len(jpgImages)
finalFiles = []
totalPages = totalFiles // 3
diference = totalFiles % 3
size = "A4" #from impunt
aspectRatio = 3508 / 827

#print(jpgImages)
#print(totalFiles)
#print(totalPages)
#print(diference)

if diference > 0:
	totalPages += 2

#RESIZE IMAGES
for i in range(0,totalFiles,1):
	var = Image.open('imgs/'+jpgImages[i])
	newImage = var.resize([3508, 827], resample=0)
	files.append(newImage)

imgPile = [[], [], []] #Multidimensional array that represent the 3 image piles (top, medium and bottom)

#DIVIDE THE IMAGES IN THE 3 PILES
if str(float(totalFiles) % 3) =='0':
	for i in range(0,(totalFiles//3)+1,1):
		imgPile[0].append(files[i])
	for i in range((totalFiles//3)+1,((totalFiles//3)*2)+1,1):
		imgPile[1].append(files[i])
	for i in range(((totalFiles//3)+1)*2,totalFiles,1):
		imgPile[2].append(files[i])
if str(float(totalFiles) % 3) !='0':
	for i in range(0,(totalFiles//3)+1,1):
		imgPile[0].append(files[i])
	for i in range((totalFiles//3)+1,((totalFiles//3)+1)*2,1):
		imgPile[1].append(files[i])
	for i in range(((totalFiles//3)+1)*2,totalFiles,1):
		imgPile[2].append(files[i])

#print(imgPile[0])
#print(imgPile[1])
#print(imgPile[2])

#REORGANIZE THE 3 PILES SO THEY ARE ALWAYS PAIR
if len(imgPile[0]) % 2 != '0':
	imgPile[0].append(imgPile[1][0])
	imgPile[1].append(imgPile[2][0])
	imgPile[1].append(imgPile[2][1])
	del imgPile[1][0]
	del imgPile[2][1]
	del imgPile[2][0]

#print(imgPile[0])
#print(imgPile[1])
#print(imgPile[2])

#imgPile[1][5].show()

#JOINING THE IMAGES FROM THE 3 PILES IN 1 SAME IMAGE
for i in range(0, len(imgPile[0]), 1):
	finalPage = Image.new('RGB', (3508, 2481), "white")
	if i % 2 == 0:
		finalPage.paste(imgPile[0][i],(0, 0))
		finalPage.paste(imgPile[1][i],(0, 827))
		if len(imgPile[2])-1 >= i:
			finalPage.paste(imgPile[2][i],(0, 1654))
			pass
	else:
		finalPage.paste(imgPile[0][i],(0, 1654))
		finalPage.paste(imgPile[1][i],(0, 827))
		if len(imgPile[2])-1 >= i:
			finalPage.paste(imgPile[2][i],(0, 0))
			pass
		finalPage = finalPage.rotate(180)
		pass		
	finalFiles.append(finalPage)

#print(finalFiles[5])
#finalFiles[5].show()

#SAVE AS PDF
finalFiles[0].save("out.pdf", save_all=True, append_images=finalFiles[1:])