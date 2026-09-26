# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw, ImageFont

SRC='УСТАРЕЛО_спина_гель_v1.png'; OUT='УСТАРЕЛО_спина_гель_v2.png'
GREEN=(31,69,53); INK=(59,44,30)
F ="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FB="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

im=Image.open(SRC).convert('RGB'); W,H=im.size
BL, BR, BT, BB = 22, 839, 22, 1217          # рамка исходника
ADD=430                                      # насколько удлиняем панель

canvas=Image.new('RGB',(W,H+ADD),(250,238,212))
# 1) всё до нижней рамки
canvas.paste(im.crop((0,0,W,BB-2)),(0,0))
# 2) растянутая полоса фона внутри рамки (берём чистый участок над QR)
tile=im.crop((0,674,W,692))          # чистая полоса фона без текста и колец
ty=BB-2
while ty < BB-2+ADD+2:
    canvas.paste(tile,(0,ty)); ty+=tile.size[1]
# 3) нижняя кромка с рамкой
canvas.paste(im.crop((0,BB-2,W,H)),(0,BB-2+ADD))

d=ImageDraw.Draw(canvas)
MX=int(W*0.055); MAXW=W-2*MX
S=int(W*0.0245); f=ImageFont.truetype(F,S); fb=ImageFont.truetype(FB,int(S*1.08))
LH=int(S*1.45)

y=BB-2+int(ADD*0.10)
d.line([(MX,y),(W-MX,y)],fill=GREEN,width=2); y+=int(S*1.2)

def para(runs,y):
    words=[]
    for t,fn,c in runs:
        for w in t.split(' '):
            if w: words.append((w+' ',fn,c))
    line=[];lw=0
    for w,fn,c in words:
        wl=d.textlength(w,font=fn)
        if lw+wl>MAXW and line:
            x=MX
            for tt,ff,cc in line: d.text((x,y),tt,font=ff,fill=cc); x+=d.textlength(tt,font=ff)
            y+=LH; line=[];lw=0
        line.append((w,fn,c)); lw+=wl
    if line:
        x=MX
        for tt,ff,cc in line: d.text((x,y),tt,font=ff,fill=cc); x+=d.textlength(tt,font=ff)
        y+=LH
    return y

y=para([("СОСТАВ (INCI): ",fb,GREEN),
 ("Aqua, Sodium Laureth Sulfate, Cocamidopropyl Betaine, Glycerin, Quercus Robur Bark Extract, Phenoxyethanol, Xanthan Gum, Polysorbate 20, Disodium EDTA, Potassium Sorbate, Camellia Sinensis Leaf Extract, o-Cymen-5-Ol, Citric Acid, Sodium Chloride.",f,INK)],y)
y+=int(S*0.8)
y=para([("Объём: 250 мл · pH 5,2 · Дата изготовления и срок годности: см. на упаковке · Партия: см. на упаковке · Хранить при +5…+25 °С, беречь от прямых солнечных лучей · Избегать попадания в глаза; при попадании промыть водой · Страна: Россия · Изготовитель: ООО «____________», адрес ____________ · Декларация ЕАЭС № ____________",f,INK)],y)

canvas.save(OUT); print('ok',canvas.size,'кегль',S,'низ текста',y,'рамка',BB+ADD)
