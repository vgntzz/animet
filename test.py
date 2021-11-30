import subprocess as sp
from bs4 import BeautifulSoup
import cloudscraper

def stream_from_zippy(self, received_url):
    zippy_base_url = received_url.split('.com')[0] + ".com"    

#received_url = "https://www118.zippyshare.com/v/SbMQnCDk/file.html"
#c = cloudscraper.create_scraper()
r = c.get(received_url)
soup = BeautifulSoup(r.text, 'lxml')
scripts = soup.find_all('script')
res_url = ""
for script in scripts:
    desired = str(script)
    if "document.getElementById('dlbutton')" in desired:
        resource = desired.split("document.getElementById('dlbutton').href = ")[1].split(';')[0]

        res_split = resource.split(" + ")
        res_split =[res_split[0], res_split[1] + " + " + res_split[2],  res_split[3]]
        
        for piece in res_split:
            res_url += str(eval(piece))
        break

if res_url:
    d = sp.Popen(['mpv', zippy_base_url + res_url])
    d.wait()
#sp.Popen(['mpv', '--msg-level=all=trace', "https://www60.zippyshare.com/downloadM4V?key=mPGJ1Wpe&res=ORG&time=764860", '--cookies', '--http-header-fields="Cookie: zippop=2; zippyadb=0; JSESSIONID=8A533ACC8A08E1B478D149CB1AB4ACF2; ppu_main_1d3584ff950f38d5b2e10bc2994be620=1; sb_main_ca6621f64bcdfd0a5aa2af7c57675832=1; sb_count_ca6621f64bcdfd0a5aa2af7c57675832=1; ppu_sub_1d3584ff950f38d5b2e10bc2994be620=3'])
