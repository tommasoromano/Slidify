import os
import cv2
from fpdf import FPDF

def generate_slides(video_source, slide_location, interval=1500, difference=7000):
    try:
        frm_cnt = 0
        frame_mult = interval
        count = frame_mult
        prev_count = 0
        cap = cv2.VideoCapture(video_source)
        while True:
            print(count)
            cap.set(cv2.CAP_PROP_POS_MSEC,count)
            ret, frame = cap.read()
            cv2.imwrite(slide_location+"/_"+str(count)+'.jpg',frame)

            # compare with prev
            if prev_count > 1:
                prev_img = cv2.imread(slide_location+"/_"+str(prev_count)+".jpg")
                prev_gray = cv2.cvtColor(prev_img, cv2.COLOR_BGR2GRAY)
                prev_hist = cv2.calcHist([prev_gray], [0],
                                        None, [256], [0, 256])

                cur_img = cv2.imread(slide_location+"/_"+str(count)+".jpg")
                cur_gray = cv2.cvtColor(cur_img, cv2.COLOR_BGR2GRAY)
                cur_hist = cv2.calcHist([cur_gray], [0],
                                        None, [256], [0, 256])

                c1 = 0
                i = 0
                while i<len(prev_hist) and i<len(cur_hist):
                    c1+=(prev_hist[i]-cur_hist[i])**2
                    i+= 1
                c1 = c1**(1 / 2)
                if c1 <= difference:
                    os.remove(slide_location+"/_"+str(count)+".jpg")
                else:
                    prev_count = count
                print(c1, "different frames..." if c1 > difference else "deleting for similarity...")

            #
            if prev_count == 0:
                prev_count = count
            count += frame_mult
            frm_cnt += 1
    except Exception as e:
        print("error at",frm_cnt,prev_count,count,e)
        cap.release()
        cv2.destroyAllWindows()

def to_pdf(slides_folder, pdf_name):
    try:
        dir = slides_folder+"/"
        pdf = FPDF()
        pdf.set_auto_page_break(0)
        imglst = [x for x in os.listdir(dir)] 
        for img in imglst:
            if len(img) < 11:
                n = str("0"*(11-len(img)))+img
                os.rename(dir+img,dir+n)
        
        imglst = [x for x in os.listdir(dir)] 
        j = 0
        k=0
        for img in imglst:
            if j % 10==0:
                pdf.add_page()
            print(img)
            pdf.image(dir+img, w=105,h=59,y=((k%5)*59),x=(0 if j%2==0 else 104))
            j+=1
            if j%2==0:
                k+=1
        pdf.output(pdf_name+".pdf")
    except Exception as e:
        print(e)