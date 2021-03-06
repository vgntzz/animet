import cloudscraper
import re, json
import textwrap
from bs4 import BeautifulSoup
import subprocess as sp

BASE_URL = 'https://animeflv.net'
BROWSE_URL = BASE_URL + "/browse"
WATCH_URL = BASE_URL + "/ver"
QUERY_PARAM = "?q="

DEFAULT_PLAYER = 'mpv'

class Animeflv:
    
    def __init__(self):
        self.scraper = cloudscraper.create_scraper(browser={
        'browser': 'firefox',
        'platform': 'windows',
        'mobile': False
        },
                                                   interpreter ='js2py', debug=False
                                                   )

    def search(self, words):
        r = self.scraper.get(BROWSE_URL + QUERY_PARAM + words)
        body = r.text
        bs = BeautifulSoup(body, 'lxml')
        table = bs.find(class_='ListAnimes')
        animes_json = self.parse_anime_list(table)
        #return animes_json
        animes_json = dict(sorted(animes_json.items()))
        return animes_json
        self.print_animes_json(animes_json)

    def parse_anime_list(self, table):
        animes = table.find_all('li')
        anime_dict = {}

        wrap_width = 75
        first_line_width = wrap_width - len("Description: ")

        
        for anime in animes:
            lines = []
            description = ""
            splitted = ""
            first_line = ""
            try:
                description = anime.find(class_='Description').find_all('p')[-1].contents[0]
                splitted = "\n".join(textwrap.wrap(description, width=first_line_width)).split("\n")
                first_line = splitted[0]
                description = "\n".join(splitted[1:])
                lines.append(first_line)
            except:
                pass

            anime_dict[anime.find(class_='Title').contents[0]] = {
                "Type": anime.find(class_='Type').contents[0],
                "Description": "\n".join(lines + textwrap.wrap(description, width=wrap_width)) if description else "",
                "Rating": anime.find(class_='Description').find(class_='Vts').contents[0],
                "Followers": anime.find(class_='Description').find(class_='Flwrs').find('span').contents[0],
                "URL": anime.find(class_='Vrnmlk')["href"]
            }
        return anime_dict
        
    def print_animes_json(self, anime_dict):
        for k, v in anime_dict.items():
            print(k)
            for i, j in v.items():
                print(f"\t{i}: {j}")

    def get_chapters(self, anime_url):
        #print(BASE_URL + anime_url)
        r = self.scraper.get(BASE_URL + anime_url)
        body = r.text
        bs = BeautifulSoup(body, 'lxml')
        scripts = bs.find_all('script')
        anime_information = []
        anime_episodes = []
        for script in scripts:
            desired = str(script)
            if 'var anime_info =' in desired:
                anime_information = json.loads(desired.split('var anime_info = ')[1].split(';')[0])
            if 'var episodes = ' in desired:
                anime_episodes = json.loads(desired.split('var episodes = ')[1].split(';')[0])
        #print(anime_information)
        #print(anime_episodes)
        chapters = [0 for _ in range(len(anime_episodes))]
        for chapter in anime_episodes:
            chapters[chapter[0]-1] = f"/{chapter[1]}/{anime_information[2]}-{chapter[0]}"
        #print(chapters)
        return chapters

    def get_servers(self, cid):
        #print(WATCH_URL + cid)
        r = self.scraper.get(WATCH_URL + cid)
        body = r.text
        bs = BeautifulSoup(body, 'lxml')
        servers_data_json = {"SUB": [], "LAT": []}
        servers_data = []
        #print(bs.prettify())
        trs = bs.find_all('tr')[1:]
        for tr in trs:
            for td in tr.find_all('td'):
                if 'LAT' in str(td):
                    servers_data_json['LAT'].append(tr.find('a', class_="Button Sm fa-download")["href"])
                elif 'SUB' in str(td):
                    servers_data_json['SUB'].append(tr.find('a', class_="Button Sm fa-download")["href"])

        return servers_data_json
        # print(servers_data_json)
        # buttons = bs.find_all('a', class_="Button Sm fa-download")
        # for button in buttons:
        #     servers_data.append(button["href"])
        # return servers_data
        # scripts = bs.find_all('script')
        # servers_data = {}
        # for script in scripts:
        #     desired = str(script)
        #     if 'var videos = ' in desired:
        #         servers_data = json.loads(desired.split('var videos =')[1].split(';')[0])
        #         servers_data = servers_data["SUB"]
        #         break
        
        # servers_data_json = {}
        # for element in servers_data:
        #     servers_data_json[element["server"]] = {k:v for k,v in element.items() if k != "server"}
            
        #text = json.dumps(servers_data_json, indent=4)
        #print(text)
        return servers_data_json

    def get_video_url(self, url):
        r = self.scraper.get(url)
        print(r.text)

    def stream_from_zippy(self, received_url):
        zippy_base_url = received_url.split('.com')[0] + ".com"
        res_url = ""
        r = self.scraper.get(received_url)
        soup = BeautifulSoup(r.text, 'lxml')
        scripts = soup.find_all('script')

        for script in scripts:
            desired = str(script)
            if "document.getElementById('dlbutton')" in desired:
                resource = desired.split("document.getElementById('dlbutton').href = ")[1].split(';')[0]

                res_split = resource.split(" + ")
                res_split =[res_split[0], res_split[1] + " + " + res_split[2],  res_split[3]]

                import ast
                try: tree = ast.parse(res_split[1][1:-1], mode='eval')
                except: break
                whitelist = (ast.Expression,
                             ast.BinOp, ast.UnaryOp, ast.operator, ast.unaryop,
                             ast.Num,
                             )
                if all(isinstance(node, whitelist) for node in ast.walk(tree)): res_url = res_split[0][1:-1] + str(eval(compile(tree, filename='', mode='eval'), {"__builtins__": None}, None)) + res_split[2][1:-1]
                break


        return zippy_base_url + res_url
        # if res_url:
        #     d = sp.Popen(['mpv', zippy_base_url + res_url]).communicate()

    def stream_from_streamtape(self, received_url):
        r = self.scraper.get(received_url)
        rb = self.scraper.head(received_url)
        soup = BeautifulSoup(r.text, 'lxml')
        url = ""
        scripts = soup.find_all('script')
        for script in scripts:
            desired = str(script)
            if "document.getElementById('norobotlink')" in desired:
                result =desired.split("document.getElementById('norobotlink').innerHTML = ")[-1].split(';')[0]
                splitted =result.split(' + ')
                url = "https:" + splitted[0][1:-1] + splitted[1].split('.subs')[0][5:-2]
                #print(url)
                break
        
        return url            
        
    def stream(self, url):
        d = sp.Popen([DEFAULT_PLAYER, url]).communicate()        

            
#animeflv = Animeflv()
#print(animeflv.stream_from_zippy("https://www100.zippyshare.com/v/9hv1eSkj/file.html"))
#animeflv.stream_from_streamtape("https://strtpe.link/v/yAgpJxZW1BCdje/")
#print(animeflv.search('re zero')["Re:Zero kara Hajimeru Isekai Seikatsu"]["URL"])
#print(animeflv.get_chapters('/anime/rezero-kara-hajimeru-isekai-seikatsu'))
#x = animeflv.get_servers("/41916/rezero-kara-hajimeru-isekai-seikatsu-16")
#print(x)
