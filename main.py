#!/usr/bin/python3
from animeflv import *
import curses
import sys
animeflv = Animeflv()

KEYS = {"UP": [ord('w'), ord('k'), curses.KEY_UP], "DOWN": [ord('s'), ord('j'), curses.KEY_DOWN], "LEFT": [ord('a'), ord('h'), curses.KEY_LEFT], "RIGHT": [ord('d'), ord('l'), curses.KEY_RIGHT], "BACK": [ord('z')]}

def my_raw_input(stdscr, r, c, prompt_string):
    stdscr.addstr(r, c, prompt_string)
    stdscr.refresh()
    inp  = stdscr.getstr(r, c+len(prompt_string), 50)
    inp = inp.decode()
    return inp

def input_anime(screen, *args):
    screen.clear()
    screen.keypad(0)
    _pretitle = "AnimeT"
    screen.addstr(f"{'=' * (len(_pretitle)+4)}\n| {_pretitle} |\n{'=' * (len(_pretitle)+4)}\n\n", curses.color_pair(1))
    anime_keyword = my_raw_input(screen, 4, 0, "Anime? (default Overlord): ") or "Overlord"
    data = animeflv.search(anime_keyword)
    q = None; x=0; y=0
    screen.keypad(1)
    return [True if data else False, data, None]
    

def get_anime(screen, *args):
    data = args[0]
    q = None; x=0; y=0
    _title = 'Anime List'
    while q != 10:
        screen.clear()
        
        screen.addstr(f"{'=' * (len(_title)+4)}\n| {_title} |\n{'=' * (len(_title)+4)}\n\n", curses.color_pair(1))
        for i, item in enumerate(data.items()):
            title, v = item
            title_str = ""
            if i == y: title_str += "> "
            title_str += f"[{i}] {title}\n"
            #title_str += f"\t{v['description']}\n"
            screen.addstr(title_str, curses.color_pair(0 if i != y else 1))
        screen.addstr('\n')
        screen.addstr(f" {'> ' * int(y==len(data.keys()))}[Volver]", curses.color_pair(2))
        screen.refresh()
        q = screen.getch()
        if q == 27: return -23
        
        if q in KEYS["UP"]: y -= 1
        elif q in KEYS["DOWN"]: y += 1
        if y >= len(data.keys()) + 1: y = 0
        if y < 0: y = len(data.keys())
        if(q in KEYS["BACK"]): return [False, None, None]
    selected_anime = None
    for i, key in enumerate(data.keys()):
        if i == y:
            selected_anime = key
            break

    return [selected_anime != None, data, selected_anime]

def get_anime_chapters(screen, *args):
    animes = dict(args[0])
    selected_anime = args[1]
    og_url = animes[selected_anime]["URL"]
    animes[selected_anime]["URL"] = BASE_URL + animes[selected_anime]["URL"]
    q = None; x=0; y=0
    
    while q != 10:
        screen.clear()
        screen.addstr(f"{'=' * (len(selected_anime)+4)}\n| {selected_anime} |\n{'=' * (len(selected_anime)+4)}\n\n", curses.color_pair(1))
        for key, value in animes[selected_anime].items():

            key = f"[{key}]"
            screen.addstr(key, curses.color_pair(2))
            title_str = f": {value}\n"
            screen.addstr(title_str)
            
        screen.addstr(f"\n {'>' * (y == 0)} [Ver Capitulos]\n", curses.color_pair(0 if y == 1 else 2))
        screen.addstr(f" {'>' * (y == 1)} [Volver]\n", curses.color_pair(0 if y == 0 else 2))
        
        screen.refresh()
        q = screen.getch()
        if q == 27: return -23
        if q in KEYS["UP"]: y -= 1
        elif q in KEYS["DOWN"]: y += 1
        if(q in KEYS["BACK"]): return [False, None, None]
        
        if y < 0: y = 1
        if y > 1: y = 0
    animes[selected_anime]["URL"] = og_url
    chapters = animeflv.get_chapters(og_url)
    return [y==0, chapters, selected_anime] 

def get_anime_servers(screen, *args):

    chapters = args[0]
    selected_anime = args[1]
    yex = screen.getmaxyx()
    cuanto_mostrar = 20 if (len(chapters) > 20) else len(chapters) + 1
    current_shift = len(chapters) - cuanto_mostrar//2 if len(chapters) >= cuanto_mostrar else 0
    scroll_amount = cuanto_mostrar>>1
    
    q = None; x=0; y=len(chapters) - 1
    while 1:
        screen.clear()

        screen.addstr(f"{'=' * (len(selected_anime)+4)}\n| {selected_anime} |\n{'=' * (len(selected_anime)+4)}\n\n", curses.color_pair(1))

        for i in range(current_shift, current_shift + cuanto_mostrar):
            if(i >= len(chapters)): break
            screen.addstr(f"{'> ' * int(y == i)}[+] Capitulo {i+1}\n", curses.color_pair(0 if y != i else 1))
        screen.addstr('\n')
        screen.addstr(f"{'> ' * int(y == len(chapters))} [Volver]", curses.color_pair(0 if y != len(chapters) else 2))
        
        screen.refresh()
        q = screen.getch()
        
        if q == 27: return -23
        if q in KEYS["UP"]: y -= 1
        elif q in KEYS["DOWN"]:y += 1
         
        if(y >= cuanto_mostrar + current_shift): current_shift += scroll_amount 
        if(y < current_shift): current_shift -= scroll_amount 
        if(current_shift < 0): current_shift = 0
        if(q in KEYS["BACK"]): return [False, None, None]
        
        if y < 0:
            y = len(chapters)
            current_shift = y-cuanto_mostrar + 1
        if y > len(chapters): 
            y = 0
            current_shift = 0
        
        if q == 10:
            if(y >= len(chapters)):
                print("VOLVIENDO")
                return [False, None, None]
    
            servers = animeflv.get_servers(chapters[y])
            if not servers:
                raise Exception("yo")
            stream(screen, servers)

def stream(screen, *args):
    servers = args[0]
    for server in servers:
        if 'zippy' in server:
            url = animeflv.stream_from_zippy(server)
            if url:
                animeflv.stream(url)
                break
        if 'streamtape' in server:
            url = animeflv.stream_from_streamtape(server)
            if url:
                animeflv.stream(url)
                break
    #zippy_url = servers[1]
    #animeflv.stream_from_zippy(zippy_url)
    return [True, None, None]
    

def main():
    index = 0
    order = [input_anime, get_anime, get_anime_chapters, get_anime_servers]
    stored_results = [None for _ in range(len(order))]
    result = [None, None, None]
    last_result = [None, None, None]
    screen = curses.initscr()
    dims = screen.getmaxyx()
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_RED, -1)
    curses.init_pair(2, curses.COLOR_BLUE, -1)
    curses.curs_set(0)
    while 1:
        result = order[index](screen, result[1], result[2])
        if result == -23: break
        stored_results[index] = list(result)

        if result[0]:
            index += 1
        else:
            index -= 1
            target = index - 1
            if target < 0: target = 0
            result = list(stored_results[target])

        if index < 0: index = 0
        if index >= len(order):
            index = 0
            index = 3
            result = list(stored_results[2])

    # for res in stored_results:
    #     print(len(res))
    #     while(1):
    #         pass

        # anime = get_anime(screen)
        # if anime == -23: break
        # url = get_anime_chapters(screen, anime)
        # if url == -23: break
        # if not url: continue
        # chapters = animeflv.get_chapters(url)
        # result = get_anime_servers(screen, chapters, anime)
        # if result == -23: break
        # zippy_url = animeflv.get_servers(result)[1]
        # animeflv.stream_from_zippy(zippy_url)

    
    #print(url)
    #print(chapters)
    #print(servers)
    curses.endwin()

def n_main():
    anime = input("Anime? (default Overlord): ") or "Overlord"
    animeflv = Animeflv()
    result = animeflv.search(anime)
    
    animeflv.print_animes_json(result)
    index = int(input(f"Index (0-{len(result)-1})(default 0): ") or "0") 
    key = None
    for i, k in enumerate(result):
        if i == index:
            key = k
            break
    if key:
        result = animeflv.get_chapters(result[key]["URL"])

        for i in range(len(result)):
            print(f"Capitulo {i+1}")

        cap = int(input("Capitulo (default 1): ") or "0") - 1
        servers = animeflv.get_servers(result[cap])
        for server in servers:
            if 'zippy' in server:
                url = animeflv.stream_from_zippy(server)
                if url:
                    animeflv.stream(url)
                    break
            if 'streamtape' in server:
                url = animeflv.stream_from_streamtape(server)
                if url:
                    animeflv.stream(url)
                    break

    
if __name__ == "__main__":
    if len(sys.argv) > 1: n_main()
    else:
        try:
            main()
        except KeyboardInterrupt:
            curses.endwin()
