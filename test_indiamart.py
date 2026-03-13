import sys
import asyncio
from config.settings import load_settings
from utils.request_manager import RequestManager
from bs4 import BeautifulSoup
from pathlib import Path

settings = load_settings(Path('./'))

async def run():
    async with RequestManager(settings.proxies.__dict__) as rm:
        try:
            html = await rm.fetch('https://dir.indiamart.com/search.mp?ss=toy+manufacturer')
            
            soup = BeautifulSoup(html, 'lxml')
            cards = soup.select('div.l-cl.brdwhite.mkcl, div.cardbody, section.listing-card')
            
            if not cards:
                print("Fallback selectors:")
                cards = soup.select('.lst_cl')
            
            print('Found cards:', len(cards))
            if cards:
                card_html = str(cards[0])
                print('--- CARD HTML ---')
                print(card_html[:1000])
                
                # The profile URL on indiamart is usually in a company link:
                name_el = cards[0].select_one('a.fs20, a.comp-name, a[data-click="company-name"], a.lcname')
                
                if name_el:
                    profile_url = name_el.get('href')
                    if not profile_url.startswith('http'):
                        profile_url = 'https://www.indiamart.com' + profile_url
                    
                    print('Fetching profile:', profile_url)
                    profile_html = await rm.fetch(profile_url)
                    p_soup = BeautifulSoup(profile_html, 'lxml')
                    
                    for row in p_soup.select('tr, .fs14, .fs12, .table, li'):
                        rt = row.get_text(' ', strip=True).lower()
                        if 'turnover' in rt or 'employee' in rt or 'nature of business' in rt:
                            print('Found Stat:', row.get_text(' | ', strip=True))
                        
        except Exception as e:
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run())
