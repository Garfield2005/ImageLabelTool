#coding=utf-8

#-------------------------------------------------------------------------------
# Name:        Object bounding box label tool
# Purpose:     Label object bboxes for ImageNet Detection data
# Author:      Qiushi: https://github.com/puzzledqs/BBox-Label-Tool
# Created:     06/06/2014
# Modifier: mm.zhang
# ModifiedDate: 01/15/2018

#-------------------------------------------------------------------------------
from __future__ import division
from Tkinter import *
import tkMessageBox
from PIL import Image, ImageTk
import os
import glob
import random

# colors for the bboxes
COLORS = ['red', 'blue', 'pink', 'cyan', 'green', 'black']
# image sizes for the examples
SIZE = 256, 256

class LabelTool():
    def __init__(self, master):
        # set up the main frame
        self.parent = master
        self.parent.title("ImageLabelTool/jolly.ming2005@gmail.com")
        self.frame = Frame(self.parent)
        self.frame.pack(fill=BOTH, expand=1)
        self.parent.resizable(width = FALSE, height = FALSE)

        # initialize global state
        # self.save_dir = ''
        self.imageDir = ''
        self.imageList= []
        self.egDir = ''
        self.egList = []
        self.outDir = ''
        self.cur = 0
        self.total = 0
        self.category = ''
        self.imagename = ''
        self.labelfilename = ''
        self.tkimg = None

        # initialize mouse state
        self.STATE = {}
        self.STATE['click'] = 0
        self.STATE['x'], self.STATE['y'] = 0, 0

        # reference to bbox
        self.bboxIdList = []
        self.bboxId = None
        self.bboxList = []
        self.hl = None
        self.vl = None

        # ----------------- GUI stuff ---------------------
        # dir entry & load
        self.label = Label(self.frame, text = "Image/Label Dir:")
        self.label.grid(row = 0, column = 0, sticky = E)
        self.entry = Entry(self.frame)
        self.entry.grid(row = 0, column = 1, sticky = W+E)
        self.ldBtn = Button(self.frame, text = "Load", command = self.loadDir)
        self.ldBtn.grid(row = 0, column = 2, sticky = W+E)
        self.ldBtn_save = Button(self.frame, text="SaveDirConfig", command=self.loadSaveDir)
        self.ldBtn_save.grid(row=0, column=3, sticky=W + E)

        # main panel for labeling
        self.mainPanel = Canvas(self.frame, cursor='tcross')
        self.mainPanel.bind("<Button-1>", self.mouseClick)
        self.mainPanel.bind("<Motion>", self.mouseMove)
        self.parent.bind("<Escape>", self.cancelBBox)  # press <Espace> to cancel current bbox
        self.parent.bind("s", self.cancelBBox)
        self.parent.bind("a", self.prevImage) # press 'a' to go backforward
        self.parent.bind("d", self.nextImage) # press 'd' to go forward
        self.mainPanel.grid(row = 1, column = 1, rowspan = 4, sticky = W+N)

        # showing bbox info & delete bbox
        self.lb1 = Label(self.frame, text = 'Bounding boxes:')
        self.lb1.grid(row = 1, column = 2,  sticky = W+N)
        self.listbox = Listbox(self.frame, width = 22, height = 12)
        self.listbox.grid(row = 2, column = 2, sticky = N)
        self.btnDel = Button(self.frame, text = 'Delete', command = self.delBBox)
        self.btnDel.grid(row = 3, column = 2, sticky = W+E+N)
        self.btnClear = Button(self.frame, text = 'ClearAll', command = self.clearBBox)
        self.btnClear.grid(row = 4, column = 2, sticky = W+E+N)

        # control panel for image navigation
        self.ctrPanel = Frame(self.frame)
        self.ctrPanel.grid(row = 5, column = 1, columnspan = 2, sticky = W+E)
        self.prevBtn = Button(self.ctrPanel, text='<< Prev', width = 12, command = self.prevImage)
        self.prevBtn.pack(side = LEFT, padx = 5, pady = 3)
        self.nextBtn = Button(self.ctrPanel, text='Next/Save >>', width = 12, command = self.nextImage)
        self.nextBtn.pack(side = LEFT, padx = 5, pady = 3)
        self.progLabel = Label(self.ctrPanel, text = "Progress:     /    ")
        self.progLabel.pack(side = LEFT, padx = 5)
        self.tmpLabel = Label(self.ctrPanel, text = "Go to Image No.")
        self.tmpLabel.pack(side = LEFT, padx = 5)
        self.idxEntry = Entry(self.ctrPanel, width = 5)
        self.idxEntry.pack(side = LEFT)
        self.goBtn = Button(self.ctrPanel, text = 'Go', command = self.gotoImage)
        self.goBtn.pack(side = LEFT)

        # example pannel for illustration
        self.egPanel = Frame(self.frame, border = 10)
        self.egPanel.grid(row = 1, column = 0, rowspan = 5, sticky = N)
        self.tmpLabel2 = Label(self.egPanel, text = "Examples:")
        self.tmpLabel2.pack(side = TOP, pady = 5)
        self.egLabels = []
        for i in range(3):
            self.egLabels.append(Label(self.egPanel))
            self.egLabels[-1].pack(side = TOP)

        # display mouse position
        self.disp = Label(self.ctrPanel, text='')
        self.disp.pack(side = RIGHT)

        self.frame.columnconfigure(1, weight = 1)
        self.frame.rowconfigure(4, weight = 1)

    def loadSaveDir(self, dbg=False):
        self.save_dir = self.entry.get()
        self.entry.delete(0, END)
        if not self.save_dir:
            print "LabelInfo Dir is empty"
            tkMessageBox.showerror("Error!", message = "标记信息保存目录为空!")
            return
        print "LabelInfo Dir: %s" % self.save_dir

    def loadDir(self, dbg = False):
        self.imageDir = self.entry.get()
        self.parent.focus()
        if not self.imageDir:
            print "Image Dir is empty"
            tkMessageBox.showerror("Error!", message = "原始目录为空!")
            return

        dirs = os.listdir(self.imageDir)
        if len(dirs) == 0:
            print "No category in image dir"
            tkMessageBox.showerror("Error!", message="图片根目录下类别目录为空!")
            return
        print "Find categories: %d" % len(dirs)

        for dir in dirs:
            self.loadCategory(dir)

    def loadCategory(self, category):
        print "Processing: %s" % category
        if self.category is None or self.category == '':
            self.category = category

        tempImageDir = os.path.join(self.imageDir,category)
        tempImageList = glob.glob(os.path.join(tempImageDir, '*.jpg'))
        if len(tempImageList) == 0:
            print('No .JPEG images found in the specified dir：%s!' % tempImageDir)
            return
        self.imageList.extend(tempImageList)

        # default to the 1st image in the collection
        self.total = len(self.imageList)

        # set up output dir
        self.outDir = os.path.join(self.save_dir, category)
        if not os.path.exists(self.outDir):
            os.mkdir(self.outDir)

        # load example bboxes
        self.egDir = os.path.join(r'./Examples', '001')
        if not os.path.exists(self.egDir):
            print "No example images"
            return
        filelist = glob.glob(os.path.join(self.egDir, '*.JPEG'))
        self.tmp = []
        self.egList = []
        random.shuffle(filelist)
        for (i, f) in enumerate(filelist):
            if i == 3:
                break
            im = Image.open(f)
            r = min(SIZE[0] / im.size[0], SIZE[1] / im.size[1])
            new_size = int(r * im.size[0]), int(r * im.size[1])
            self.tmp.append(im.resize(new_size, Image.ANTIALIAS))
            self.egList.append(ImageTk.PhotoImage(self.tmp[-1]))
            self.egLabels[i].config(image = self.egList[-1], width = SIZE[0], height = SIZE[1])

        self.loadImage()
        print('%d images loaded from %s' %(self.total, category))

    def loadImage(self):
        # load image
        imagepath = self.imageList[self.cur]
        self.entry.delete(0, END)
        self.entry.insert(0, imagepath)
        self.img = Image.open(imagepath)
        self.tkimg = ImageTk.PhotoImage(self.img)
        self.mainPanel.config(width = max(self.tkimg.width(), 400), height = max(self.tkimg.height(), 400))
        self.mainPanel.create_image(0, 0, image = self.tkimg, anchor=NW)
        self.progLabel.config(text = "%04d/%04d" %(self.cur + 1, self.total))

        # load labels
        self.clearBBox()
        self.imagenamewithsuffix = os.path.split(imagepath)[-1]
        self.imagename = os.path.split(imagepath)[-1].split('.')[0]
        labelname = self.imagename + '.txt'
        self.category = os.path.split(imagepath)[0][len(self.imageDir)+1:]
        self.labelfilename = os.path.join(os.path.join(self.save_dir, self.category), labelname)
        bbox_cnt = 0
        if os.path.exists(self.labelfilename):
            with open(self.labelfilename) as f:
                for (i, lineAll) in enumerate(f):
                    if i == 0:
                        bbox_cnt = int(lineAll.strip())
                        continue
                    line = lineAll.split('\t')[-1]
                    tmp = [int(t.strip()) for t in line.split()]
                    self.bboxList.append(tuple(tmp))
                    tmpId = self.mainPanel.create_rectangle(tmp[0], tmp[1], \
                                                            tmp[0] + tmp[2], tmp[1] + tmp[3], \
                                                            width = 2, \
                                                            outline = COLORS[(len(self.bboxList)-1) % len(COLORS)])
                    self.bboxIdList.append(tmpId)
                    self.listbox.insert(END, '(%d, %d) -> (%d, %d)' %(tmp[0], tmp[1], tmp[2], tmp[3]))
                    self.listbox.itemconfig(len(self.bboxIdList) - 1, fg = COLORS[(len(self.bboxIdList) - 1) % len(COLORS)])

    def saveImage(self):
        with open(self.labelfilename, 'w') as f:
            f.write('%d\n' %len(self.bboxList))
            for bbox in self.bboxList:
                f.write('{0}\t{1}\t{2}\n'.format(self.category, self.imagenamewithsuffix, ' '.join(map(str, bbox))))
        print('Image No. %d saved: %s' %(self.cur, self.labelfilename))


    def mouseClick(self, event):
        if self.STATE['click'] == 0:
            self.STATE['x'], self.STATE['y'] = event.x, event.y
        else:
            x1, x2 = min(self.STATE['x'], event.x), max(self.STATE['x'], event.x)
            y1, y2 = min(self.STATE['y'], event.y), max(self.STATE['y'], event.y)
            self.bboxList.append((x1, y1, x2-x1, y2-y1))
            self.bboxIdList.append(self.bboxId)
            self.bboxId = None
            self.listbox.insert(END, '(%d, %d) -> (%d, %d)' %(x1, y1, x2, y2))
            self.listbox.itemconfig(len(self.bboxIdList) - 1, fg = COLORS[(len(self.bboxIdList) - 1) % len(COLORS)])
        self.STATE['click'] = 1 - self.STATE['click']

    def mouseMove(self, event):
        self.disp.config(text = 'x: %d, y: %d' %(event.x, event.y))
        if self.tkimg:
            if self.hl:
                self.mainPanel.delete(self.hl)
            self.hl = self.mainPanel.create_line(0, event.y, self.tkimg.width(), event.y, width = 2)
            if self.vl:
                self.mainPanel.delete(self.vl)
            self.vl = self.mainPanel.create_line(event.x, 0, event.x, self.tkimg.height(), width = 2)
        if 1 == self.STATE['click']:
            if self.bboxId:
                self.mainPanel.delete(self.bboxId)
            self.bboxId = self.mainPanel.create_rectangle(self.STATE['x'], self.STATE['y'], \
                                                            event.x, event.y, \
                                                            width = 2, \
                                                            outline = COLORS[len(self.bboxList) % len(COLORS)])

    def cancelBBox(self, event):
        if 1 == self.STATE['click']:
            if self.bboxId:
                self.mainPanel.delete(self.bboxId)
                self.bboxId = None
                self.STATE['click'] = 0

    def delBBox(self):
        sel = self.listbox.curselection()
        if len(sel) != 1 :
            return
        idx = int(sel[0])
        self.mainPanel.delete(self.bboxIdList[idx])
        self.bboxIdList.pop(idx)
        self.bboxList.pop(idx)
        self.listbox.delete(idx)

    def clearBBox(self):
        for idx in range(len(self.bboxIdList)):
            self.mainPanel.delete(self.bboxIdList[idx])
        self.listbox.delete(0, len(self.bboxList))
        self.bboxIdList = []
        self.bboxList = []

    def prevImage(self, event = None):
        self.saveImage()
        if self.cur >= 1:
            self.cur -= 1
            self.loadImage()

    def nextImage(self, event = None):
        self.saveImage()
        self.cur += 1
        if self.cur >= self.total:
            tkMessageBox.showerror("WARN!", message="已标记完成!")
            return
        self.loadImage()


    def gotoImage(self):
        idx = int(self.idxEntry.get())
        if 1 <= idx and idx <= self.total:
            self.saveImage()
            self.cur = idx
            self.loadImage()

if __name__ == '__main__':
    root = Tk()
    tool = LabelTool(root)
    root.resizable(width =  True, height = True)
    root.mainloop()
