#!/usr/bin/env python3
# Utilizando GrabCut e interface tkinter

from tkinter import *
from PIL import Image
from PIL import ImageTk
from tkinter.filedialog import askopenfilename
import cv2
import numpy as np

class GrabCutGUI(Frame):
    def __init__(self, master = None):
        Frame.__init__(self, master)
        self.iniciaUI()

    def iniciaUI(self):
        self.master.title("Janela da Imagem Segmentada")
        self.pack()

        self.computaAcoesDoMouse()

        self.imagem = self.carregaImagemASerExibida()

        self.canvas = Canvas(self.master, width = self.imagem.width(), height = self.imagem.height(), cursor = "cross")

        self.canvas.create_image( 0, 0, anchor = NW, image = self.imagem)
        self.canvas.image = self.imagem
        self.canvas.pack()

    def computaAcoesDoMouse(self):
        self.startX = None
        self.startY = None
        self.rect = None
        self.rectangleReady = None

        self.master.bind("<ButtonPress-1>", self.callbackBotaoPressionado )
        self.master.bind("<B1-Motion>", self.callbackBotaoPressionadoEmMovimento )
        self.master.bind("<ButtonRelease-1>", self.callbackBotaoSolto )

    def callbackBotaoSolto(self,event):
        if self.rectangleReady:
            #criar nova janela com resultado
            windowGrabCut = Toplevel(self.master)
            windowGrabCut.wm_title("Segmentacao")
            windowGrabCut.minsize( width=self.imagem.width(), height=self.imagem.height() )

            canvasGrabCut = Canvas(windowGrabCut, width=self.imagem.width(), height=self.imagem.height())
            canvasGrabCut.pack()

            #aplicar grabcut na imagem
            mask = np.zeros(self.imagemOpenCV.shape[:2], np.uint8)
            rectGcut = ( int(self.startX), int(self.startY), int(event.x - self.startX), int(event.y - self.startY) )
            fundoModel = np.zeros( (1,65), np.float64 )
            objModel = np.zeros( (1,65), np.float64 )

            #parametro antes de cv2.... ->refina o grabcut
            cv2.grabCut( self.imagemOpenCV, mask, rectGcut, fundoModel, objModel, 6, cv2.GC_INIT_WITH_RECT )

            maskFinal = np.where((mask == 2) | (mask == 0), 0, 1).astype("uint8")

            imgFinal = self.imagemOpenCV * maskFinal[:,:,np.newaxis]

            for x in range(0, self.imagemOpenCV.shape[1]):
                for y in range(0, self.imagemOpenCV.shape[0]):
                    if(maskFinal[y][x] == 0):
                        imgFinal[y][x][0] = imgFinal[y][x][1] = imgFinal[y][x][2] = 255

            #convertendo novamente imagem opncv para tkinter
            imgFinal = cv2.cvtColor(imgFinal, cv2.COLOR_BGR2RGB)
            imgFinal = Image.fromarray(imgFinal)
            imgFinal = ImageTk.PhotoImage(imgFinal)

            canvasGrabCut.create_image(0, 0, anchor = NW, image = imgFinal)
            canvasGrabCut.image = imgFinal

    def callbackBotaoPressionadoEmMovimento(self,event):
        currentX = self.canvas.canvasx(event.x)
        currentY = self.canvas.canvasy(event.y)

        #atualiza o retangulo que vai ser desenhado...
        self.canvas.coords(self.rect, self.startX, self.startY, currentX, currentY)

        #verifica retangulo
        self.rectangleReady = True


    def callbackBotaoPressionado(self, event):
        #convertendo x frama para x canvas...
        self.startX = self.canvas.canvasx(event.x)
        self.startY = self.canvas.canvasy(event.y)

        if not self.rect:
            self.rect =  self.canvas.create_rectangle( 0, 0, 0, 0, outline="orange")

    def carregaImagemASerExibida(self):

        caminhoDaImagem = askopenfilename()

        if(caminhoDaImagem != 0 ):
            self.imagemOpenCV = cv2.imread(caminhoDaImagem)

            image = cv2.cvtColor(self.imagemOpenCV, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(image)

            image = ImageTk.PhotoImage(image)

            return image



def main():

    root  = Tk()

    appcut = GrabCutGUI(master = root)

    appcut.mainloop()


if __name__ == "__main__":
    main()
