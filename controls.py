import numpy as np
import cv2
from mss import mss
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
from datetime import datetime
print("Loading ...")
import pytesseract
# from pytesseract import Output
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

print("Loaded Pytesseract ...")
bounding_box = {"top":394,"left":535,"width":294,"height":310}
# bounding_box2 = {"top":30,"left":10,"width":376,"height":672}

sct = mss()
count_img = 1

def predict(each_n,next):
    # print("searching number : ",ccc)
    target = pytesseract.image_to_string(each_n, lang='eng', config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789')
    
    # print(target)
    # cv2.imshow(str(ccc),each_n)
    
    # cv2.waitKey(0)
    if(target=="") and next==True:
        target = predict(cv2.bitwise_not(each_n),False)
    try:
        if target!="" and (int(target)%2 != 0) and next==True:
            target = predict(cv2.bitwise_not(each_n),False)
    except:
        target = ""
        print("Could not fetch number")
    return target


def predict2(data):
    x,y,w,h = data["points"]
    each_n = data["orig"][y:y+h,x:x+w]
    if(data["next"]==False):
        # print("Trying second time : ")
        each_n = cv2.bitwise_not(each_n)

    # print("searching number : ",ccc)
    target = pytesseract.image_to_string(each_n, lang='eng', config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789')
    
    # print(target)
    # cv2.imshow(str(ccc),each_n)
    
    # cv2.waitKey(0)
    if(target=="") and data["next"]==True:
        data["next"] = False
        # data["orig"] = cv2.bitwise_not(each_n)
        target = predict2(data)
    try:
        if target!="" and (int(target)%2 != 0) and data["next"]==True:
            data["next"] = False
            # data["orig"] = cv2.bitwise_not(each_n)
            target = predict2(data)
    except:
        target = ""
        print("Could not fetch number")
    cv2.imwrite(target+"_.jpg",each_n)
    return target

def proc(data):
    points = data["points"]
    row = data["row"]
    orig = data["orig"]
    res = {row:[]}
    col = 0
    for i in range(4):
        x,y,w,h = points[i]
        each_n = orig[y:y+h,x:x+w]
        target = (col,predict(each_n,True))
        res[row].append(target)
        col = col + 1
    return res

while True:
	sct_img = sct.grab(bounding_box)
	cv2.imwrite(str(count_img)+".jpg",np.array(sct_img))
	img = cv2.imread('./1.jpg')
	edges = img.copy()

	img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

	img = cv2.GaussianBlur(img,(5,5),0)
	orig = img.copy()
	cv2.imwrite("2.jpg",orig)

	# _,orig = cv2.threshold(orig,0,255,cv2.THRESH_BINARY_INV)
	# o = np.ones((img.shape[0],img.shape[1]))
	img = cv2.inRange(img,146,148)
	img = cv2.bitwise_not(img)
	cv2.imshow("image",img)
	# cv2.imwrite("2.jpg",orig)
	# mask = cv2.inRange(img,0,40)
	# img = cv2.bitwise_and(img,img,mask=mask)
	# _,img = cv2.threshold(img,145,148,cv2.THRESH_BINARY)
	# d = pytesseract.image_to_data(img, output_type=Output.DICT)
	# n_boxes = len(d['level'])
	# print("N boxes : ",n_boxes)
	# for i in range(n_boxes):
	#     (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
	#     cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
	# cv2.imwrite("2.jpg",img)
	# cv2.imshow('img', img)

	# edges = cv2.Canny(img,146,148)
	c,h = cv2.findContours(img,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
	cont = []
	for cnt in c:
		area = cv2.contourArea(cnt)
		# print(area)

		if area>=4000:
			peri = cv2.arcLength(cnt,True)
			approx = cv2.approxPolyDP(cnt,0.02*peri,True)
			# print(len(approx))
			bb = list(cv2.boundingRect(approx))
			bb[2] = 68
			bb[3] = 68
			cont.append(bb)
			cv2.drawContours(edges,cnt,-1,(255,0,0),3)

	max_width = max(cont, key=lambda r: r[0] + r[2])[0]
	max_height = max(cont, key=lambda r: r[3])[3]
	nearest = max_height * 1.4
	cont.sort(key=lambda r: (int(nearest * round(float(r[1])/nearest)) * max_width + r[0]))

	print("Contours : ",len(cont),"\n",cont)
	cv2.imshow("edges",edges)

	###########################
	##########################
	# points = []
	# s = datetime.now()
	# print("Searching")
	# for i in range(4):
	#     points.append({"orig":orig,"row":i,"points":cont[i*4:i*4 + 4]})
	# # print(points)
	# with ThreadPoolExecutor(max_workers = 4) as executor:
	#     results = executor.map(proc, points)
	# for result in results:
	#     print(result)
	# e = datetime.now()
	# td = e-s
	# print("Total seconds for 1 :  ",td.total_seconds())
	#################################
	############################

	# cv2.imshow("edges",edges)
	# points = []
	# for i in cont:
		# points.append({"orig":orig,"points":i,"next":True})

	# s = datetime.now()
	# print("Searching 2")
	# with ThreadPoolExecutor(max_workers = 14) as executor:
		# results = executor.map(predict2, points)
	cv2.waitKey(0)
	# for result in results:
		# print(result)
	# e = datetime.now()
	# td = e-s
	# print("Total seconds for 2 :  ",td.total_seconds())

	break