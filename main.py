import multiprocessing
import sqlite3
from selenium import webdriver
from bs4 import BeautifulSoup
import listcpu
from selenium.webdriver.edge.options import Options
import lxml

conn = sqlite3.connect('all.db')
cur = conn.cursor()


def parc(listinsite, konec):
    options = Options()
    options.page_load_strategy = 'eager'
    chrome_prefs = {}
    options.experimental_options["prefs"] = chrome_prefs
    chrome_prefs["profile.default_content_settings"] = {"images": 2}
    chrome_prefs["profile.managed_default_content_settings"] = {"images": 2}
    driver = webdriver.Edge(options=options)
    #driver = webdriver.Chrome(options=options)
    # chrome_options = webdriver.ChromeOptions()
    # prefs = {"profile.managed_default_content_settings.images": 2}
    # chrome_options.add_experimental_option("prefs", prefs)
    # driver = webdriver.Chrome(chrome_options=chrome_options)
    url = 'https://www.avito.ru/moskva_i_mo/nastolnye_kompyutery?p='
    while listinsite <= konec:
        urlp = url + str(listinsite)
        driver.get(urlp)
        html = driver.page_source
        opis = []
        price = []
        name = []
        links = []
        comp = []

        soup = BeautifulSoup(html, 'lxml')
        items = soup.select('div.items-items-kAJAg')

        for item in items:
            opis = item.select('div.iva-item-root-_lk9K')
            price = item.select('span.price-price-JP7qe')
            name = item.select('h3.title-root-zZCwT')
            links = item.select('a.link-link-MbQDP.link-design-default-_nSbv.title-root-zZCwT.iva-item-title-py3i_')
            comp = item.select('div.iva-item-sellerInfo-_q_Uw')
        for iterat in range(1, len(links)):
            linkselem = links[iterat]
            dblink = 'https://www.avito.ru' + str(linkselem["href"])
            cur.execute("INSERT INTO one VALUES(NULL, NULL, NULL, NULL, NULL, ?,  NULL, CURRENT_TIMESTAMP);", (dblink,))
            conn.commit()
            cur.execute("UPDATE one SET DateLast = date(CURRENT_TIMESTAMP) WHERE link = (?);", (dblink,))
            conn.commit()
            opiselem = opis[iterat]
            for opislist in opiselem:
                opisitem = str(opislist.text)
                for elemlist in listcpu.cpulist:
                    if elemlist in opisitem:
                        dbcpu = str(elemlist).replace('-', ' ')
                        cur.execute("UPDATE one SET CPU = (?) WHERE link = (?);", (dbcpu, dblink))
                        conn.commit()
                for elemlist in listcpu.gpulist:
                    if elemlist in opisitem:
                        dbgpu = str(elemlist)
                        cur.execute("UPDATE one SET GPU = (?) WHERE link = (?);", (dbgpu, dblink))
                        conn.commit()
                for elemlist in listcpu.mblist:
                    if elemlist in opisitem:
                        dbmb = str(elemlist)
                        cur.execute("UPDATE one SET MB = (?) WHERE link = (?);", (dbmb, dblink))
                        conn.commit()
            nameelem = name[iterat]
            dbname = str(nameelem.text)
            cur.execute("UPDATE one SET Name = (?) WHERE link = (?);", (dbname, dblink))
            conn.commit()
            priceelem = price[iterat]
            compelem = comp[iterat]
            dbcomp = str(compelem.text)
            cur.execute("UPDATE one SET Seller = CAST((?) AS VARCHAR(15)) WHERE link = (?);", (dbcomp, dblink))
            conn.commit()
            try:
                dbprice = int(priceelem.text.replace(' ', '').replace('₽', ''))
                cur.execute("UPDATE one SET Price = (?) WHERE link = (?);", (dbprice, dblink))
                conn.commit()
            except ValueError:
                pass
        listinsite += 1


if __name__ == "__main__":
    proclist = []
    i, k = 1, 10
    for _ in range(1, 10):
        proclist.append((i, k))
        i += 10
        k += 10
    print(proclist)
    with multiprocessing.Pool(processes=2) as proc:
        proc.starmap(parc, proclist)
