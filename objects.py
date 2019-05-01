import numpy as np
import cv2
import math
import matplotlib.pyplot as plt

'''
Texture Points Class
'''
class Points(object):
	'''
	initialize
	'''
	def __init__(self,coor, flag):
		self.x = coor[0]
		self.y = coor[1]
		self.flag = flag

	'''
	mapping from pixels
	'''
	def fromPixels(self, Pixel):### caused by indexing difference
		self.x = Pixel.y/1024
		self.y = 1-Pixel.x/1024

	'''
	Helper Functions
	'''
	def toList(self):
		return [self.x, self.y]

	def getFlag(self):
		return self.flag

	def mark(self, mark):
		self.flag = mark

	def unmark(self):
		self.flag = 0

'''
Pixel Points Class
'''
class Pixels(object):
	def __init__(self,x, y):
		self.x = x
		self.y = y

	def fromPoints(self, Point):### caused by indexing difference
		self.x = max(0,min(1023,round(1023-Point.y*1024)))
		self.y = max(0,min(1023,round(Point.x*1024-1)))

class Vertex(object):
	'''
	initialize
	'''
	def __init__(self, coor, flag):
		self.x = coor[0]
		self.y = coor[1]
		self.z = coor[2]
		self.flag = flag

	'''
	Helper Functions
	'''
	def getCoor(self):
		return self.coor

	def getFlag(self):
		return self.flag

	def mark(self):
		self.flag = True

	def unmark(self):
		self.flag = False

	def toList(self):
		return [self.x, self.y, self.z]


class FaceModel(object):
	vDict={}	# a dictionary of {vertex id: vertex Vertex(3)}
	vtDict={}	# a dictionary of {texture id: texture Point(2)}
	point_face_normal={}
	vnDict={}	# a dictionary of {vertex normal id: face normal vector(3)}
	fDict={}	# a dictionary of {face id: facePtID x 3}
	fvDict = {} # a dictionary of {facePtID: [vertex id, texture id, normal id]}
	vti_vi = {}	# mapping of vti and vi
	vi_mod={}		# a dictionary of {vertex id: modification status}
	midPoints = {}	# a dicitonary of {(texture id, texture id): (midpoint texture id, vertex id)}

	'''
	Initialize
	'''
	def __init__(self, vertex, texture, face, normal):
		for i in range(len(vertex)):
			self.vDict[i+1] = Vertex(vertex[i], False)
		self.vi_mod[-1]=False
		for i in range(len(texture)):
			self.vtDict[i+1] = Points(texture[i], False)
			self.vi_mod[i+1] = False
		for i in range(len(normal)):
			norm = np.array(normal[i])
			norm = norm / np.linalg.norm(norm)
			self.vnDict[i+1] = norm.tolist()
		index = 1
		for info in face:
			self.fDict[index] = []			
			for v in info:
				newi = len(self.fvDict.keys())
				self.fvDict[newi] = v
				if (v[1] in self.vti_vi.keys()):
					if (self.vti_vi[v[1]] != v[0]):
						print ("invalid")
				self.vti_vi[v[1]] = v[0]
				self.fDict[index].append(newi)
			index+=1			

	'''
	Get() Helper Functions
	'''
	def getfiFromvti(self, vti):
		ans = []
		for fi in self.fDict.keys():
			vtilist = self.getvtiFromfi(fi)
			if vti in vtilist:
				ans.append(fi)
		return ans

	def getviFromfi(self,fi):
		fv = self.fDict[fi]
		return [self.fvDict[x][0] for x in fv] 

	def getvtiFromfi(self,fi):
		fv = self.fDict[fi]
		return [self.fvDict[x][1] for x in fv] 

	def getvniFromfi(self,fi):
		fv = self.fDict[fi]
		return [self.fvDict[x][2] for x in fv] 
	
	def getMod(self, vi):
		return self.vi_mod[vi]

	def plotTexture(self):
		coordx = []
		coordy = []
		for ti in self.vtDict.keys():
			coordx.append(self.vtDict[ti].x)
			coordy.append(self.vtDict[ti].y)
		plt.plot(coordx, coordy, "r*", markersize=0.1)
		return 0

	def addfv(self,v,vt,vn):
		newi = len(self.fvDict.keys())
		self.fvDict[newi] = [v,vt,vn]
		return newi

	def updatefDict(self,fi,v1,v2,v3):
		self.fDict[fi] = [v1,v2,v3]

	def calcMidPoint(self,v1,vt1,vn1,v2,vt2,vn2):
		if (self.vtDict[vt1].getFlag() and self.vtDict[vt2].getFlag()):
			if ((vt1, vt2) not in self.midPoints.keys()):
				p1 = self.vtDict[vt1]
				p2 = self.vtDict[vt2]
				vector1 = self.vDict[v1]
				vector2 = self.vDict[v2]
				midt = Points([(p1.x+p2.x)/2, (p1.y+p2.y)/2], False)
				midv = Vertex([(vector1.x+vector2.x)/2, (vector1.y+vector2.y)/2, (vector1.z+vector2.z)/2], False)
				midvn = (np.array(self.vnDict[vn1])+np.array(self.vnDict[vn2]))
				midvn = midvn / np.linalg.norm(midvn)
				midvn = midvn.tolist()
				vt_index = len(self.vtDict.keys())+1
				v_index = len(self.vDict.keys())+1
				vn_index = len(self.vnDict.keys())+1
				self.vtDict[vt_index] = midt
				self.vDict[v_index] = midv
				self.vnDict[vn_index] = midvn
				self.vti_vi[vt_index] = v_index
				self.midPoints[(vt1, vt2)] = (v_index, vt_index, vn_index)
				self.midPoints[(vt2, vt1)] = (v_index, vt_index, vn_index)

	### update face with two markers
	def adjustFace(self, f, fv1, fv2, fv3):
		[v1,vt1,vn1] = self.fvDict[fv1]
		[v2,vt2,vn2] = self.fvDict[fv2]
		[v3,vt3,vn3] = self.fvDict[fv3]
		(v12,vt12,vn12) = self.midPoints[(vt1,vt2)]
		fv12 = self.addfv(v12, vt12, vn12)
		self.updatefDict(f, fv1, fv12, fv3)
		self.updatefDict(len(self.fDict.keys())+1, fv12, fv2, fv3)


	def incrementMark(self, degree):
		idans = set([])
		for fid in self.fDict.keys():
			textures = self.getvtiFromfi(fid)
			flag = 0
			for vti in textures:
				flag |= self.vtDict[vti].flag
			if (flag == 2**degree-1):
				for vti in textures:
					self.vtDict[vti].flag |= (2**(degree-1)-1)
					idans.add(vti)
		return idans

	'''
	The main subdivision function which upgrade performance
	'''
	def subDivide(self):
		### calculate new vertexes and textures
		for f in self.fDict.keys():
			vlist = self.getviFromfi(f)
			vtlist = self.getvtiFromfi(f)
			vnlist = self.getvniFromfi(f)
			[v1,v2, v3] = vlist
			[vt1, vt2, vt3] = vtlist
			[vn1,vn2,vn3] = vnlist
			self.calcMidPoint(v1,vt1,vn1,v2,vt2,vn2)
			self.calcMidPoint(v2,vt2,vn2,v3,vt3,vn3)
			self.calcMidPoint(v3,vt3,vn3,v1,vt1,vn1)

		flen = len(self.fDict.keys())
		for f in range(1,flen+1):
			[fv1,fv2,fv3] = self.fDict[f]
			vlist = self.getviFromfi(f)
			vtlist = self.getvtiFromfi(f)
			vnlist = self.getvniFromfi(f)
			[v1,v2, v3] = vlist
			[vt1, vt2, vt3] = vtlist
			[vn1, vn2, vn3] = vnlist

			### for faces with three flags, remove original face and substitute wth four faces
			if (self.vtDict[vt1].getFlag() and self.vtDict[vt2].getFlag() and self.vtDict[vt3].getFlag()):
				(v12,vt12,vn12) = self.midPoints[(vt1,vt2)]
				(v13,vt13,vn13) = self.midPoints[(vt3,vt1)]
				(v23,vt23,vn23) = self.midPoints[(vt2,vt3)]
				fv12 = self.addfv(v12,vt12,vn12)
				fv13 = self.addfv(v13,vt13,vn13)
				fv23 = self.addfv(v23,vt23,vn23)
				self.updatefDict(f, fv1,fv12,fv13)
				self.updatefDict(len(self.fDict.keys())+1, fv2,fv23,fv12)
				self.updatefDict(len(self.fDict.keys())+1, fv3,fv13,fv23)
				self.updatefDict(len(self.fDict.keys())+1, fv12,fv23,fv13)
			### for faces with two flags, remove original face and substitute with two faces
			elif (self.vtDict[vt1].getFlag() and self.vtDict[vt2].getFlag()):
				self.adjustFace(f, fv1, fv2, fv3)
			elif (self.vtDict[vt1].getFlag() and self.vtDict[vt3].getFlag()):
				self.adjustFace(f, fv3, fv1, fv2)
			elif (self.vtDict[vt2].getFlag() and self.vtDict[vt3].getFlag()):
				self.adjustFace(f, fv2, fv3, fv1)
		self.midPoints.clear()

	def updateDictNormal(self):
		for f in self.fDict.keys():
			[v1,v2,v3]=self.getviFromfi(f)
			vt12 = np.subtract(self.vDict[v2].toList(), self.vDict[v1].toList())
			vt23 = np.subtract(self.vDict[v3].toList(), self.vDict[v2].toList())
			vt31 = np.subtract(self.vDict[v1].toList(), self.vDict[v3].toList())
			fn2 = np.cross(vt12,vt23)
			fn2 = fn2/np.linalg.norm(fn2)
			fn3 = np.cross(vt23, vt31)
			fn3 = fn3/np.linalg.norm(fn3)
			fn1 = np.cross(vt31, vt12)
			fn1 = fn1/np.linalg.norm(fn1)
			[vn1, vn2, vn3] = self.getvniFromfi(f)
			self.vnDict[vn1] = fn1.tolist()
			self.vnDict[vn2] = fn2.tolist()
			self.vnDict[vn3] = fn3.tolist()

	def ZDeviation(self, points, cutGrpah, pointAtEdge, iteNum, img):
		mindis = 2
		maxdis = 0
		ptDict = {}
		count = 0
		total = len(points)
		for p in points:
			count+=1
			dis = 2 
			vt = self.vtDict[p]

			processList = []
			i = min(1023,math.floor(vt.x*1024))
			j = min(1023,math.floor(vt.y*1024)) 
			index = 2
			while (len(processList) == 0):
				processList = []
				for a in range(i-index,i+index-1):
					for b in range(j-index,j+index-1):
						processList += cutGrpah[a][b]
				index+=1
			for vtid in processList:
				pt = self.vtDict[vtid]
				dis = min(dis, math.sqrt((pt.x-vt.x)**2+(pt.y-vt.y)**2))
			ptDict[p] = dis
			if (dis<mindis):
				mindis = dis
			if (dis > maxdis):
				maxdis = dis

		print("finished %d points, mindis=%f,maxdis=%f\n" %(count,mindis,maxdis))

		total = len(points)		
		print ("total number of %d points" %(total))
		ite = 0
		while (ite<iteNum):
			vAreacDict = {}
			vNormDict = {}
			total = len(self.fDict.keys())
			print ("total number of %d faces" %(total))
			count = 0
			for f in self.fDict.keys():
				count+=1
				[v1,v2,v3] = self.getviFromfi(f)
				[vt1,vt2,vt3] = self.getvtiFromfi(f)
				vt12 = np.subtract(self.vDict[v2].toList(), self.vDict[v1].toList())
				vt23 = np.subtract(self.vDict[v3].toList(), self.vDict[v2].toList())
				vt31 = np.subtract(self.vDict[v1].toList(), self.vDict[v3].toList())
				s12 = np.linalg.norm(vt12)
				s23 = np.linalg.norm(vt23)
				s13 = np.linalg.norm(vt31)
				p = (s12+s23+s13)/2
				area = math.sqrt(p*(p-s12)*(p-s23)*(p-s13))
				if (vt1 not in vAreacDict.keys()): 
					vAreacDict[vt1] = area
				else:
					vAreacDict[vt1] += area
				if (vt2 not in vAreacDict.keys()):
					vAreacDict[vt2] = area
				else:
					vAreacDict[vt2] += area
				if (vt3 not in vAreacDict.keys()):
					vAreacDict[vt3] = area
				else:
					vAreacDict[vt3] += area

				fn2 = np.cross(vt12,vt23)
				fn2 = fn2/np.linalg.norm(fn2)
				if (vt2 not in vNormDict.keys()):
					vNormDict[vt2] = fn2*area
				else:
					vNormDict[vt2] = np.add(vNormDict[vt2], fn2*area)
				fn3 = np.cross(vt23, vt31)
				fn3 = fn3/np.linalg.norm(fn3)
				if (vt3 not in vNormDict.keys()):
					vNormDict[vt3] = fn3*area
				else:
					vNormDict[vt3] = np.add(vNormDict[vt3], fn3*area)
				fn1 = np.cross(vt31, vt12)
				fn1 = fn1/np.linalg.norm(fn1)
				if (vt1 not in vNormDict.keys()):
					vNormDict[vt1] = fn1*area
				else:
					vNormDict[vt1] = np.add(vNormDict[vt1], fn1*area)
			print ("finished %d points" %(total))
			ite+=1
			count = 0
			coorx = []
			coory = []
			colors = []
			for p in points:
				count+=1			
				vid= self.vti_vi[p]
				vn = vNormDict[p] / vAreacDict[p]

				### get direction through nearest pixel at edge
				### get amount by distance through nearest pixel at edge
				v = self.vDict[vid].toList()
				px = Pixels(0,0)
				px.fromPoints(self.vtDict[p])
				color = img[px.x][px.y]
				fx = min(0.01,np.sin(math.sin((ptDict[p]/2)/maxdis)*math.pi)*0.03)
				self.vDict[vid] =  Vertex(np.add(v,vn*fx).tolist(), False)
				coorx.append(self.vtDict[p].x)
				coory.append(self.vtDict[p].y)
				colors.append(fx/0.01*255)
			print ("finished %d points" %(count))
			self.updateDictNormal()