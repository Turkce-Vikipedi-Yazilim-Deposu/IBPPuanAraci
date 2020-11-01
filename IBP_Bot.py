import pywikibot
from pywikibot import pagegenerators
from pywikibot import textlib, pagegenerators
from bs4 import BeautifulSoup
import requests
import math

################
##### MAIN #####
################

def utf8len(s):
    return len(s.encode('utf-8'))

# BAYT SAYACI
def baytsayaci(oku):
    uzunluk = utf8len(oku.text)
    return uzunluk
    
# RESİM SAYACI
def resim_sayaci(oku):
    i = 0
    for x in oku.imagelinks(total=None, content=True):
        i +=1
    return i

# KATEGORİ SAYACI
def kategori_sayaci(oku):
    i = 0
    for x in oku.categories(with_sort_key=False, total=None, content=False):
        try:
            if x.categoryinfo["hidden"]:
                pass
        except KeyError:
            i +=1
    return i

# ŞABLON SAYACI
def sablon_sayaci(oku):
    sonuc = []
    for item in oku.itertemplates(total=None, content=False):
        if "Modül:" in item.title():
            pass
        elif "Kaynakça" in item.title():
            pass
        elif "kaynağı" in item.title():
            pass
        elif "cite" in item.title():
            pass
        elif "bilgi kutusu" in item.title():
            sonuc.append("***"+str(item.title()))
        elif "infobox" in item.title():
            sonuc.append("***"+str(item.title()))
        else:
            sonuc.append(item.title())
    return sorted(sonuc)


## BeautifulSoup ile ref'leri saydırmaca
def ref_sayaci(okunacak):
    page=requests.get('https://tr.wikipedia.org/wiki/'+okunacak)       
    soup=BeautifulSoup(page.content,'html.parser') 
    count = 0
    for eachref in soup.find_all('span', attrs={'class':'reference-text'}):
        count = count + 1
    return count


## ANA LOOP
def main(okunacak):    
    # Sayfayi oku
    oku = pywikibot.Page(site, okunacak)
    print("# [["+okunacak+"]]")

    #print(dir(oku))
    #print(oku.section())
    #quit()


    ## Puanlar için temel veriler
    baytlar = baytsayaci(oku)
    kategoriler = kategori_sayaci(oku)
    sablonlar = sablon_sayaci(oku)
    referanslar = ref_sayaci(okunacak)

    ## Madde puanlamaya uygun mu kontrolü
    if baytlar < 3000:
        print("#:Madde kriterlere uygun değil, 3kb'tan dakha kısa.")
        print("#::Toplam: 0 puan")
        puan = 0
    elif referanslar < 2:
        print("#:Madde kriterlere uygun değil, 2'den az kaynak içeriyor.")
        print("#::Toplam: 0 puan")
        puan = 0
    else:
        puan = puan_yazici(baytlar, kategoriler, sablonlar, referanslar)
    return puan


## PUAN HESAPLAMA
def puan_yazici(baytlar, kategoriler, sablonlar, referanslar):        
    puan = 0

    # 3kb+ madde?
    if baytlar > 2999:
        print("#:Yeni madde: 30 puan")
        puan += 30
    else:
        print("#:Yeni madde: 0 puan, 3kb'den kısa")
        gecerlilik = 0

    # 3kb sonrası her 5kb?        
    carpan = math.floor((baytlar-3000)/5000)
    if carpan > 0:
        print("#:5000 baytlık ekleme: 10*"+str(carpan)+"="+str(carpan*10)+" puan")
        puan += carpan*10
    else:
        print("#:5000 baytlık ekleme: 10*0=0 puan")
    
    # Bilgi kutusu var mı?
    try:
        if "***" in sablonlar[0]:
            print("#:Bilgi kutusu ekleme: 4*1=4 puan ([["+sablonlar[0].replace("***","")+"]])")
            puan += 4
        else:
            print("#:Bilgi kutusu ekleme: 4*0=0 puan")
    except IndexError:
        print("HATA")

    # 2 veya daha fazla kaynak?
    if referanslar >= 2:
        ref_2 = referanslar-2
        print("#:Kaynak ekleme: 2*"+str(ref_2)+"="+str(ref_2*2)+" puan")
        puan += ref_2*2
    else:
        print("#:Kaynak ekleme: Maddede 2'den az kaynak bulunuyor.")

    # Kategori ekleme?
    print("#:Kategori ekleme: 1*"+str(kategoriler)+"="+str(kategoriler)+" puan")
    puan += kategoriler

    # Dış bağlantılar?
    ########################
    #### DAHA YAZILMADI ####   
    ########################

    # Madde için toplam puan
    print("#::Toplam: "+str(puan)+" puan")

    return puan
    
if __name__ == '__main__':
    # Burasi hangi vikiden hangi sayfanin cekilecegi kismi
    project = pywikibot.Site('tr','wikipedia')
    site = pywikibot.Site()
    site.throttle.maxdelay = 0

    # Buradaki listeyi daha iyi şekilde alacak bişi yapmalı
    
    liste = [
        "Varna Nekropolü",
        "Sabiha Kasimati",
        "Nina Kusturica",
        "Alwin Mittasch",
        "Maguba Sırtlanova",
        "Gece Cadıları",
        "Tango (oyun)",
        "Makedonya Antifaşist Kadın Cephesi",
        "Yugoslavya Antifaşist Kadın Cephesi",
        "Leyla Tepe Medeniyeti",
        "Gevork Vartanyan",
    ]

    total_puan = 0
    for okunacak in liste:
        total_puan += main(okunacak)
    

    ## Buradaki gibi! TestPages.txt adını değiştirebiliriz.
    ## TXT dosyası içinden sadece [[Madde]] şeklindeki kısımları alır. 
    gen = pagegenerators.TextfilePageGenerator(filename='TestPages.txt')

    total_puan = 0
    for sayfa in gen:
        okunacak = str(sayfa).replace("[[tr:","").replace("]]","")
        total_puan += main(okunacak)
        
    print("#:::Genel toplam:"+str(total_puan)+" puan. --~~~~")
