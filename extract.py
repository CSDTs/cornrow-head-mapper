import pathlib

def extractFile(filename):
	filename = 'base/'+filename
	fdr = open(filename, "r")
	pathlib.Path('info').mkdir(parents=True, exist_ok=True)
	fdvt = open("info/vertex_vt.txt", "w")
	fdv = open("info/vertex_v.txt", "w")
	fdvn = open("info/vertex_vn.txt", "w")
	fdf = open("info/vertex_f.txt","w")
	print ("here")

	leng = [0,0,0,0]
	for lines in fdr:
		lst = lines.strip().split(" ")
		if (lst[0]=="v"):
			fdv.write(lst[1]+" "+lst[2]+" "+lst[3]+"\n")
			leng[0]+=1
		elif (lst[0]=="vt"):
			fdvt.write(lst[1]+" "+lst[2]+"\n")
			leng[1]+=1
		elif (lst[0]=="vn"):
			fdvn.write(lst[1]+" "+lst[2]+" "+lst[3]+"\n")
			leng[2]+=1
		elif (lst[0]=="f"):
			fdf.write(lst[1]+" "+lst[2]+" "+lst[3]+"\n")
			leng[3]+=1
	print (leng)
