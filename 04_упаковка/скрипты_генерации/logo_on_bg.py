# -*- coding: utf-8 -*-
"""Логотип на фирменном кремовом фоне (взят с лицевой стороны коробки)."""
from PIL import Image
import numpy as np

logo=Image.open('УСТАРЕЛО_логотип.png').convert('RGBA')
face=Image.open('uploads/УСТАРЕЛО_порошок_цветной_40plus_лицо.png').convert('RGB')

# чистый кусок фона коробки -> плитка
tile=face.crop((200,400,300,440))
LW,LH=logo.size
M=int(LH*0.45)                       # поля вокруг знака
W,H=LW+2*M, LH+2*M

bg=Image.new('RGB',(W,H))
for y in range(0,H,tile.size[1]):
    for x in range(0,W,tile.size[0]):
        bg.paste(tile,(x,y))
# лёгкое усреднение, чтобы не было видно стыков плитки
a=np.array(bg).astype(float)
a=a*0.35+np.array([243,229,207])*0.65
bg=Image.fromarray(a.astype(np.uint8))

bg.paste(logo,(M,M),logo)
bg.save('УСТАРЕЛО_логотип_на_фоне.png')
print('ok',bg.size)

# крупная версия для читаемости
bg.resize((W*2,H*2),Image.LANCZOS).save('УСТАРЕЛО_логотип_на_фоне@2x.png')
