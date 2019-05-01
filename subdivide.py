# through cmd: cd desktop/desktop/3d_cornrow/python

# cynlindracal 

#adaptor refinement


import matplotlib.pyplot as plt
import numpy as np
import cv2
import math
import sys
from PIL import Image
import extract
import time
import objects as obj



'''
image plotting helper functions
'''
def plotPixels(pixelList, title):
	coordx = []
	coordy = []
	for v in pixelList:
		p = obj.Points([0,0], False)
		p.fromPixels(v)
		coordx.append(p.x)
		coordy.append(p.y)
	plt.plot(coordx, coordy, "b*", markersize=0.1)
	plt.title(title)

def plotPoints(pointList, title):
	coordx = []
	coordy = []
	for v in pointList:
		coordx.append(v.x)
		coordy.append(v.y)
	plt.plot(coordx, coordy, "g*", markersize=0.1)
	plt.title(title)

# check if the pixel is at edge
def isEdge(image, i, j, grade):
	edge = False
	if (image[i][j]>grade):
		if (i!=0):
			if (image[i-1][j]<=grade):
				edge = True
		if (i!=len(image)-1):
			if (image[i+1][j]<=grade):
				edge = True
		if (j!=0):
			if (image[i][j-1]<=grade):
				edge = True	
		if (j!=len(image[i])-1):
			if (image[i][j+1]<=grade):
				edge = True	
	return edge

def saveAsFile(fm, filename):
	f = open(filename, "w")
	f.write("# Blender v2.79 (sub 0) OBJ File: 'base1.blend'\n")
	f.write("# www.blender.org\n")
	f.write("mtllib base1_smart.mtl\n")
	f.write("o baseHeadSh\n")
	for i in fm.vDict.keys():
		f.write("v "+str(fm.vDict[i].x)+" "+str(fm.vDict[i].y)+" "+str(fm.vDict[i].z)+"\n")
	for i in fm.vtDict.keys():
		f.write("vt "+str(fm.vtDict[i].x)+" "+str(fm.vtDict[i].y)+"\n")
	for i in fm.vnDict.keys():
		f.write("vn "+str(fm.vnDict[i][0])+" "+str(fm.vnDict[i][1])+" "+str(fm.vnDict[i][2])+"\n")
	for i in fm.fDict.keys():
		f.write("f")
		for j in fm.fDict[i]:
			f.write(" "+str(fm.fvDict[j][0])+"/"+str(fm.fvDict[j][1])+"/"+str(fm.fvDict[j][2]))
		f.write("\n")
	f.close()
	print ("Saved as %s." %(filename))
	return 0

def saveAsReducedFile(fm, filename):
	f = open(filename, "w")
	f.write("# Blender v2.79 (sub 0) OBJ File: 'base1.blend'\n")
	f.write("# www.blender.org\n")
	f.write("mtllib base1_smart.mtl\n")
	f.write("o baseHeadSh\n")
	for i in fm.vDict.keys():
		f.write("v "+str(fm.vDict[i].x)+" "+str(fm.vDict[i].y)+" "+str(fm.vDict[i].z)+"\n")
	for i in fm.vtDict.keys():
		f.write("vt "+str(fm.vtDict[i].x)+" "+str(fm.vtDict[i].y)+"\n")
	for i in fm.fDict.keys():
		f.write("f")
		for j in fm.fDict[i]:
			f.write(" "+str(fm.fvDict[j][0])+"/"+str(fm.fvDict[j][1]))
		f.write("\n")
	f.close()
	print ("Saved as %s." %(filename))
	return 0

def getInfo(filename):
	info = []
	f = open(filename, "r")
	for line in f:
		lst = line.strip("\n").split(" ")
		newlst = [float(x) for x in lst]
		info.append(newlst)
	return info

def getFace(filename):
	face = []
	f = open(filename, "r")
	for line in f:
		lst = line.strip("\n").split(" ")
		sub = []
		for l in lst:
			sublst = l.split("/")
			sublst = [int(j) for j in sublst]
			sub.append(sublst)
		face.append(sub)
	return face

if __name__ == '__main__':
	'''extract information from file into list objects'''
	if (len(sys.argv)!=5):
		print ("please enter: obj filename, pattern filename, iteration number, allowPlot\n")
		print ("Sample Input: obj_base10.obj img_base10.png 2 YES/NO")
		sys.exit(-1)

	startTime = time.time()
	filename = sys.argv[1]
	imgname = sys.argv[2]
	subIteNum = int(sys.argv[3])
	canPlot = sys.argv[4]
	extract.extractFile(filename)
	vertexPoints = getInfo("info/vertex_v.txt")
	vertexNormal = getInfo("info/vertex_vn.txt")
	vtDict = getInfo("info/vertex_vt.txt")
	fDict = getFace("info/vertex_f.txt")
	print (vertexPoints[-1], vertexNormal[-1], vtDict[-1])


	'''parse information into facemodel class'''
	fm = obj.FaceModel(vertexPoints, vtDict, fDict, vertexNormal)
	print ("size of face: %d" %(len(fm.fDict.keys())))
	print ("size of vertex: %d" %(len(fm.vDict.keys())))
	print ("size of facepoints: %d" %(len(fm.fvDict.keys())))

	### get vertexmap into points class ###
	img = cv2.imread("base/"+imgname, 0)
	height, width = img.shape
	print (height, width)
	dup = []

	pixelAtEdge = set([])
	dup = []

	for i in range(len(img)):
		for j in range(len(img[i])):
			if (isEdge(img, i, j, 160)): 
				   p = obj.Pixels(i, j)
				   pixelAtEdge.add(p)
	print ("%d pixels at edge" %(len(pixelAtEdge)))
	if (canPlot=="YES"):
		fm.plotTexture()
		plotPixels(pixelAtEdge, "Pattern Mapping in Texture Map")
		plt.show()

	endTime = time.time()
	print ("%.2f s passed for initializing" %(endTime-startTime))

	ite = 0
	searchList = fm.vtDict.keys()
	markedPointsID = set([])
	markedPoints = []
	while (ite < subIteNum):### mark vertex
		ite+=1
		cutGraph = {}
		ptCut = {}
		for i in range(1024):
			cutGraph[i] = {}
			for j in range(1024):
				cutGraph[i][j] = []
		for vti in fm.vtDict.keys():
			pt = fm.vtDict[vti]
			px = obj.Pixels(0,0)
			px.fromPoints(pt)
			cutGraph[px.x][px.y].append(vti)
			ptCut[vti] = (px.x,px.y)
		markedPointsID = set([])
		count = 0

		for px in pixelAtEdge:
			sublist = cutGraph[px.x][px.y]
			kernel = 1
			while (len(sublist) == 0):
				for i in range(px.x-kernel,px.x+kernel+1):
					for j in range(px.y-kernel, px.y+kernel+1):
						if ((i != px.x-kernel or i != px.x+kernel) and (j != px.y-kernel or j !=px.y+kernel)):
							sublist = sublist + cutGraph[i][j]
						
				kernel+=1
			markedPointsID = markedPointsID.union(set(sublist))

		print ("marked %d points" %(len(markedPointsID)))
		for k in markedPointsID:
			fm.vtDict[k].mark(7)
		markedPointsID = fm.incrementMark(3)
		print ("marked %d expanded points" %(len(markedPointsID)))
		markedPoints = []
		for vtid in markedPointsID:
			markedPoints.append(fm.vtDict[vtid])
		if (canPlot=="YES"):
			fm.plotTexture()
			plotPoints(markedPoints, "UV Map before Subdivision #%d" %(ite))
			plt.show()
		### subdivide face
		fm.subDivide()
		endTime = time.time()
		print ("%.2f s passed for subdivision %d" %(endTime-startTime,ite))

		### save every subdivision result for future use
		fname = "object/obj_subdivide_"+str(ite)+"_reduced.obj"
		saveAsReducedFile(fm, fname)
		fname = "object/obj_subdivide_"+str(ite)+".obj"
		saveAsFile(fm, fname)

		for k in fm.vtDict.keys():
			fm.vtDict[k].unmark()
		searchList = markedPointsID
	if (canPlot=="YES"):
		fm.plotTexture()
		plotPoints(markedPoints, "UV Map after All Subdivision")
		plt.show()
	print (len(fm.vtDict.keys()))

	endTime = time.time()
	print ("%.2fs passed for subdivision" %(endTime-startTime))
