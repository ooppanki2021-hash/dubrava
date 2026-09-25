# Логотип ДУБИНА 40+: знак v2_A + надпись, пропорции как на лице мыла v6
from PIL import Image,ImageDraw,ImageFont
F='/home/user/tools/fonts/Montserrat-';INK=(43,32,26);OC=(187,136,58)
K=20  # масштаб относительно макета (знак 42 px -> 840 px)
mark=Image.open('../исходники_дизайнера/знак_v2_A_для_скрипта.png').convert('RGBA');mark=mark.crop(mark.getbbox()); mark=mark.resize((round(mark.size[0]*42*K/mark.size[1]),42*K),Image.LANCZOS)
def cap(font,px):
    for sz in range(8,2000):
        f=ImageFont.truetype(font,sz);b=f.getbbox('Н')
        if b[3]-b[1]>=px: return f
fb=cap(F+'Bold.ttf',14*K);f4=cap(F+'Regular.ttf',12*K)
b1=fb.getbbox('ДУБИНА');b2=f4.getbbox('40+');hb=fb.getbbox('Н');h4=f4.getbbox('Н')
W=mark.size[0]+9*K+(b1[2]-b1[0])+4*K+(b2[2]-b2[0]);H=42*K;M=6*K
out=Image.new('RGBA',(W+2*M,H+2*M),(0,0,0,0));out.alpha_composite(mark,(M,M));d=ImageDraw.Draw(out)
ty=M+(H-14*K)//2;x=M+mark.size[0]+9*K
d.text((x-b1[0],ty-hb[1]),'ДУБИНА',font=fb,fill=INK)
x2=x+(b1[2]-b1[0])+4*K;d.text((x2-b2[0],ty+K-h4[1]),'40+',font=f4,fill=OC)
out.save('ДУБИНА_логотип.png')
w=Image.new('RGB',out.size,'white');w.paste(out,(0,0),out);w.save('ДУБИНА_логотип_на_белом.png');print(out.size)
