from app        import db
# from app        import index_algoliasearch
from app.models import Sku, News

from fuzzywuzzy import fuzz
from threading  import Thread
from datetime   import datetime as dt, timedelta
from bs4        import BeautifulSoup
from string     import ascii_uppercase, ascii_lowercase, digits
from random     import choices
from sqlalchemy import desc

import requests, json



def get_data_slider(markets): # нужно ли?(слайдеры на первых страницах)
    data_slider = {}
    data_slider_lenta = []
    data_slider_perekrestok = []
    data_slider_5ka = []
    session = requests.Session()
    if 'lenta' in markets:
        number = 0
        url    = 'https://lenta.com'
        page   = session.get(url)
        slides = BeautifulSoup(page.content, 'html.parser').find_all('a', {'class': 'slider-block__slide'})
        for slide in slides:
            href   = slide['href']
            if slide['href'][0] == '/':
                href = url+slide['href']
            src    = slide.find('img', {'class': 'slider-block__img'})['src']            
            data_slider_lenta.append({'href': href, 'img_src': src, 'number': number})
            number += 1
        data_slider['lenta'] = data_slider_lenta
        data_slider['lenta'] = data_slider_lenta
    if 'perekrestok' in markets:
        # url = 'https://www.perekrestok.ru'
        # page = session.get(url)
        # slides = BeautifulSoup(page.content, 'html.parser').find_all('ul', {'class': 'xf-mp-main-offer__list js-xf-main-carousel__list swiper-wrapper xf-b js-xf-b _main'})
        # for slide in slides:
        #     li = slide.find_all('li')
        #     for lil in li:
        #         pass
        pass
    if '5ka' in markets:
        number = 0
        session.get('https://5ka.ru')
        kwargs = {'domain': '5ka.ru'}
        cookie = requests.cookies.create_cookie('location_id', '1871', **kwargs)
        session.cookies.set_cookie(cookie)
        slides = session.get('https://5ka.ru/api/index/index_banners/').json()
        for slide in slides['items']:
            data_slider_5ka.append({'href': slide['link'], 'img_src': slide['image_url'], 'number': number})
            number += 1
        data_slider['5ka'] = data_slider_5ka
    return data_slider


def PEREKRESTOK():
    # ПЕРЕКРЁСТОК
    session = requests.Session()
    cookie = requests.cookies.create_cookie('region', '16')
    session.cookies.set_cookie(cookie)
    num_page = 1
    _all = 0
    _in  = 0
    perekrestok_category_skus = {}    
    while True:
        url = 'https://www.perekrestok.ru/assortment?page='+str(num_page)+'&sort=rate_desc'
        page = session.get(url)
        products = BeautifulSoup(page.content, 'html.parser').find_all('div', {'class': ['xf-product js-product _not-online', 'xf-product js-product _not-active _not-online']})
        if len(products) == 0:
            break
        for product in products:        
            category = get_category(product['data-gtm-category-name'])        
            if category == '':
                _all += 1
                continue
            product_name = product['data-gtm-product-name'].replace('ё', 'е')
            try:
                new_price = round(float(product.find('div', {'class': 'xf-price xf-product-cost__current js-product__cost _highlight'})['data-cost']), 2)
                old_price = round(float(product.find('div', {'class': 'xf-price xf-product-cost__prev js-product__old-cost'})['data-cost']), 2)
                discount_text = product.find('div', {'class': 'xf-product-cost__old-price'}).find('p').text
                discount = int(discount_text[1:len(discount_text)-1])
            except TypeError:
                # записываем новую цену равной старой, т.к. скидки не оказалось
                new_price = round(float(product.find('div', {'class': 'xf-price xf-product-cost__current js-product__cost'})['data-cost']), 2)
                old_price = new_price
                discount = 0
            product_img = product.find('img', {'class': 'js-lazy swiper-lazy xf-product-picture__img'})['data-src']
            product_href = product.find('a', {'class': 'xf-product-title__link js-product__title'})['href']
            weight = product_name.split(' ')[len(product_name.split(' '))-1]
            perekrestok_skus = {'name': product_name,
                                'img': product_img,
                                'href': 'https://www.perekrestok.ru'+product_href,
                                'new_price': new_price,
                                'old_price': old_price,
                                'discount': discount,
                                'weight': weight,
                                'type': '(PEREKRESTOK)',
                                'indicator': 0, # индикатор, кот. показывает есть ли товар в списке похожих товаров
                                'favicon': 'https://www.perekrestok.ru/favicon.ico'}
            if category in perekrestok_category_skus.keys():
                perekrestok_category_skus[category].append(perekrestok_skus)
            else:
                perekrestok_category_skus[category] = [perekrestok_skus]            
            _all += 1
            _in += 1
        num_page += 1
    print('Всего товаров в ПЕРЕКРЁСТОК:', _all, 'Внесено:', _in)
    
    return perekrestok_category_skus

    # # КРУПА
    # session = requests.Session()
    # k = 0
    # krupa_category_skus = {}
    # page = session.get('https://www.krupa.promo')
    # product_categories = BeautifulSoup(page.content, 'html.parser').find_all('div', {'class': 'category'})
    # for product_category in product_categories:
    #     url_page = product_category.find('a')['href']
    #     print(url_page)
    #     url = 'https://www.krupa.promo'+url_page
    #     page = session.get(url)        
    #     products = BeautifulSoup(page.content, 'html.parser').find_all('div', {'class': 'product' })
    #     product_category = BeautifulSoup(page.content, 'html.parser').find('h1').text
    #     category = get_category(product_category)
    #     krupa_category_skus[category] = []
    #     for product in products:        
    #         product_name = product.find('h3').text            
    #         product_cost = product.find('div', {'class': 'price col-8 text-right'}).text.replace('.–', '.00')            
    #         product_type = product.find('span', {'class': 'measure'}).text
    #         krupa_skus = {'name': product_name, 'cost': product_cost, 'type': product_type}        
    #         krupa_category_skus[category].append(krupa_skus)        
    #         k += 1        
    # print('Всего товаров в КРУПА:', k)

    # METRO

def PKA(): # если разбить категории на подкатегории, то можно будет избавиться от двойного кода
    # ПЯТЁРОЧКА
    pka_category_skus = {}
    session = requests.Session()
    try:
        session.get('https://5ka.ru', timeout=25)
    except requests.exceptions.ConnectTimeout:
        print('------> 5ka FAILED')
        return pka_category_skus
    kwargs = {'domain': '5ka.ru'}
    cookie = requests.cookies.create_cookie('location_id', '1871', **kwargs)
    session.cookies.set_cookie(cookie)
    try:
        special_offers = session.get('https://5ka.ru/api/v2/special_offers/?store=&records_per_page=12&page=1&shopitem_category=', timeout=25).json()
    except (json.decoder.JSONDecodeError, requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout):
        print('--->  https://5ka.ru/api/v2/special_offers/?store=&records_per_page=12&page=1&shopitem_category=, special_offers FAILED')
    if len(special_offers['results']) == 0:
        return pka_category_skus
    try:
        groups = session.get('https://5ka.ru/api/v2/categories/', timeout=25).json()
    except (json.decoder.JSONDecodeError, requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout):
        print('--->  https://5ka.ru/api/v2/categories/, group FAILED')
        return pka_category_skus    
    for group in groups:
        category = get_category(group['parent_group_name'])
        if category == '':
            try:
                subgroups = session.get('https://5ka.ru/api/v2/categories/'+group['parent_group_code']).json()
            except json.decoder.JSONDecodeError:
                print('--->', 'https://5ka.ru/api/v2/categories/'+group['parent_group_code'], 'subgroup FAILED')
                continue            
            for subgroup in subgroups:
                category = get_category(subgroup['group_name'])
                if category == '':
                    continue
                if category not in pka_category_skus.keys():
                    pka_category_skus[category] = []
                url = 'https://5ka.ru/api/v2/special_offers/?categories='+subgroup['group_code']+'&ordering=&page=1&price_promo__gte=&price_promo__lte=&records_per_page=12&search=&store='
                k = 0
                while True:
                    try:
                        get = session.get(url).json()
                    except json.decoder.JSONDecodeError:
                        print('--->', category+' ('+subgroup['group_name']+')')
                        continue
                    for skus in get['results']:
                        name = costruct_name(skus['name'])
                        weight = name.split(' ')[len(name.split(' '))-1]
                        pka_skus = {'name': name,
                                    'img': skus['img_link'],
                                    'href': 'https://5ka.ru/special_offers/'+str(skus['id']),
                                    'new_price': skus['current_prices']['price_promo__min'],
                                    'old_price': skus['current_prices']['price_reg__min'],
                                    'discount': round((skus['current_prices']['price_reg__min']-skus['current_prices']['price_promo__min'])/skus['current_prices']['price_reg__min']*100),
                                    'weight': weight,
                                    'type': '(5KA)',
                                    'indicator': 0, # индикатор, кот. показывает есть ли товар в списке похожих товаров
                                    'favicon': 'https://5ka.ru/img/icons/favicon-32x32.png'}
                        pka_category_skus[category].append(pka_skus)
                        k += 1                    
                    url = get['next']
                    if url == None:
                        break                
                print('ПЯТЁРОЧКА кат. '+category+' ('+subgroup['group_name']+') внесено:', k)
        else:
            if category not in pka_category_skus.keys():
                pka_category_skus[category] = []
            url = 'https://5ka.ru/api/v2/special_offers/?categories='+group['parent_group_code']+'&ordering=&page=1&price_promo__gte=&price_promo__lte=&records_per_page=12&search=&store='
            k = 0
            while True:                
                try:
                    get = session.get(url).json()
                except json.decoder.JSONDecodeError:
                    print('--->', category)
                    continue
                for skus in get['results']:
                    name = costruct_name(skus['name'])
                    weight = name.split(' ')[len(name.split(' '))-1]
                    pka_skus = {'name': name, 
                                'img': skus['img_link'],                                
                                'href': 'https://5ka.ru/special_offers/'+str(skus['id']),
                                'new_price': skus['current_prices']['price_promo__min'], #format(float(skus['current_prices']['price_promo__min']), 2),
                                'old_price': skus['current_prices']['price_reg__min'],   #format(float(skus['current_prices']['price_reg__min']), 2),
                                'discount': round((skus['current_prices']['price_reg__min']-skus['current_prices']['price_promo__min'])/skus['current_prices']['price_reg__min']*100),
                                'weight': weight, 
                                'type': '(5KA)',
                                'indicator': 0, # индикатор, кот. показывает есть ли товар в списке похожих товаров
                                'favicon': 'https://5ka.ru/img/icons/favicon-32x32.png'} # << -- подумать над мерой измерения
                    pka_category_skus[category].append(pka_skus)
                    k += 1
                url = get['next']
                if url == None:
                    break            
            print('ПЯТЁРОЧКА кат. '+category+' ('+group['parent_group_name']+') внесено:', k)
    return pka_category_skus

def LENTA():
    # ЛЕНТА
    session = requests.Session()
    session.headers = {'Accept': 'application/json',                
                       'Content-Type': 'application/json',                
                       'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0'}

    for name, value in [('CityCookie', 'lpc'), ('lentaT2', 'lpc'), ('Store', '0148')]:    
        kwargs = {'domain': 'lenta.com'}
        cookie = requests.cookies.create_cookie(name, value, **kwargs)
        session.cookies.set_cookie(cookie)

    page = session.get('https://lenta.com/catalog/')
    lenta_category_skus = {}

    if page.status_code == 200:
        menu = json.loads(BeautifulSoup(page.content, 'html.parser').find('div', {'class': 'header__catalog-menu-container'})['data-menu'])
        if len(menu['groups']) == 0:
            print('Всего товаров в ЛЕНТА: 0 Внесено: 0')
        for group in menu['groups']:
            for group_category in group['childNodes']:
                offset     = 0
                limit      = 50        
                category = get_category(group_category['name'])        
                if category == '':
                    continue
                if category not in lenta_category_skus.keys():
                    lenta_category_skus[category] = []
                k = 0
                while True:
                    param = {
                        "nodeCode": group_category['code'],
                        "filters": [],
                        "tag": "",
                        "pricesRange": 'null',
                        "sortingType": "ByPriority",
                        "offset": offset,
                        "limit": limit
                    }
                    try:
                        post = session.post('https://lenta.com/api/v1/skus/list', json=param).json()                        
                    except json.JSONDecodeError:
                        print('--->', group_category['name'], 'offset', offset, 'limit', limit)
                        continue
                    if len(post['skus']) == 0:
                        break    
                    for skus in post['skus']:
                        title    = skus['title'].replace('ё', 'е').replace("'", '').replace('.', '')
                        subtitle = skus['subTitle'].strip().replace(' г', 'г').replace(' кг', 'кг').replace(' шт', 'шт').replace(' уп', 'уп')
                        weight  = subtitle.split(', ')[len(subtitle.split(', '))-1]
                        weight = '' if weight == '' or weight[0] not in list(digits) else weight
                        origin_name = title+' '+weight
                        name = ' '.join(origin_name.split())                        
                        lenta_skus = {'name': name,
                                      'img': skus['imageUrl'] if skus['imageUrl'] else 'https://lenta.gcdn.co/static/pics/image-default--thumb.305ca150c22262acb4c40de317e93d1a.png',
                                      'href': 'https://lenta.com'+skus['skuUrl'],
                                      'new_price': skus['cardPrice']['value'],
                                      'old_price': skus['regularPrice']['value'],
                                      'discount': skus['promoPercent'],
                                      'weight': weight,
                                      'type': '(LENTA)',
                                      'indicator': 0, # индикатор, кот. показывает есть ли товар в списке похожих товаров
                                      'favicon': 'https://lenta.gcdn.co/static/pics/shortcuts/favicon-32x32.fb90679fd6d6da31ec7059b1cd4985e1.png'} # << -- подумать над мерой измерения
                        lenta_category_skus[category].append(lenta_skus)
                        k += 1
                    offset = offset + limit
                print('ЛЕНТА кат. '+category+' ('+group_category['name']+') внесено:', k)
    else:
        print('LENTA', page.status_code, page.reason)

    return lenta_category_skus



def get_news():
    news_lenta       = ''
    news_perekrestok = ''
    news_pka         = ''
    print('In get_news.')
    #lenta
    session = requests.Session()
    session.headers = {'Accept': 'application/json',                
                       'Content-Type': 'application/json',                
                       'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0'}

    for name, value in [('CityCookie', 'lpc'), ('lentaT2', 'lpc'), ('Store', '0148')]:    
        kwargs = {'domain': 'lenta.com'}
        cookie = requests.cookies.create_cookie(name, value, **kwargs)
        session.cookies.set_cookie(cookie)

    page = session.get('https://lenta.com/goods-actions/')    
    lenta_news_content = BeautifulSoup(page.content, 'html.parser').find_all('div', {'class': 'news-item__content'})
    for news_content in lenta_news_content:        
        news_date = news_content.find('div', {'class': 'news-item__date'}).text.replace('\r\n', '').replace(' ', '')
        today = dt.today().strftime('%d.%m.%Y')        
        if news_date == today:
            news_title       = news_content.find('h3', {'class': 'news-item__title'}).text.replace('\r\n', '').strip()
            news_description = news_content.find('div', {'class': 'news-item__description'}).text.replace('\r\n', '').strip()
            news_href        = news_content.find('div', {'class': 'news-item__more'}).find('a', {'class': 'link'})['href']
            news_html        = '<hr><b>'+news_title+'</b><br>'+news_description+'<br><a href="'+news_href+'" target="_blank">Подробнее <i class="fa fa-angle-double-right" aria-hidden="true"></i></a>'
            news_lenta       = news_lenta + news_html
    print('Lenta news done.')
    # #perekrestok    
    # with requests.Session() as s:
    #     # s.headers = {}
    #     page = s.get('https://www.perekrestok.ru/promos')
    #     perekrestok_news_content = BeautifulSoup(page.content, 'html.parser').find_all('li', {'class': 'xf-promo__item'})
    #     for news_content in perekrestok_news_content:
    #         news_href              = news_content.find('a')['href']
    #         page_news              = s.get(news_href)        
    #         page_news_content_text = BeautifulSoup(page_news.content, 'html.parser').find_all('div', {'class': 'xf-promo-detail__description'})[0].text
    #         news_perekrestok       = news_perekrestok +'<hr>'+page_news_content_text+'<br><a href="'+news_href+'" target="_blank">Подробнее <i class="fa fa-angle-double-right" aria-hidden="true"></i></a>'    
    #     print('Perekrestok news done.')    
    # # session = requests.Session()
    # # cookie = requests.cookies.create_cookie('region', '16')
    # # session.cookies.set_cookie(cookie)
    # # page = session.get('https://www.perekrestok.ru/promos')
    # # perekrestok_news_content = BeautifulSoup(page.content, 'html.parser').find_all('li', {'class': 'xf-promo__item'})
    # # for news_content in perekrestok_news_content:
    # #     news_href              = news_content.find('a')['href']
    # #     page_news              = session.get(news_href)        
    # #     page_news_content_text = BeautifulSoup(page_news.content, 'html.parser').find_all('div', {'class': 'xf-promo-detail__description'})[0].text
    # #     news_perekrestok       = news_perekrestok +'<hr>'+page_news_content_text+'<br><a href="'+news_href+'" target="_blank">Подробнее <i class="fa fa-angle-double-right" aria-hidden="true"></i></a>'    
    # # print('Perekrestok news done.')
    #pka
    session = requests.Session()
    # session.headers = {
    #     'Host': '5ka.ru',
    #     'Connection': 'keep-alive',
    #     'Cache-Control': 'max-age=0',
    #     'Upgrade-Insecure-Requests': '1',
    #     'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
    #     'Sec-Fetch-User': '?1',
    #     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    #     'Sec-Fetch-Site': 'same-origin',
    #     'Sec-Fetch-Mode': 'navigate',
    #     'Accept-Encoding': 'gzip, deflate, br',
    #     'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    #     'Cookie': 'header_name=X-Authorization; token=Tokenb95a4ff300063da22317467c7babd8b1375685f0; location_id=1871; TS01658276=01a93f7547cfa9c2f66ad5f5cad135006cbccb428d34c2f228190ce11574ec68f47179de4a4dfbf194f8d634d272c56f6fc96a6fefb1cd88f4cbe535f0090c122c918e0762',
    #     'dnt': '1',
    #     'If-None-Match': 'W/"5ddbf791-a3c"',
    #     'If-Modified-Since': 'Mon, 25 Nov 2019 15:47:29 GMT'
    # }
    try:
        session.get('https://5ka.ru', timeout=25)
        kwargs = {'domain': '5ka.ru'}
        cookie = requests.cookies.create_cookie('location_id', '1871', **kwargs)
        session.cookies.set_cookie(cookie)
        pka_news_content = session.get('https://5ka.ru/api/news/', timeout=25).json()
        pka_news_array   = pka_news_content['results'][:4]
        for news_content in pka_news_array:
            news_pka = news_pka+'<hr>'+news_content['title']+'<br><a href="https://5ka.ru/news/'+str(news_content['id'])+'" target="_blank">Подробнее <i class="fa fa-angle-double-right" aria-hidden="true"></i></a>'
        print('5ka news done.')
    except (requests.exceptions.ConnectTimeout, requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
        news_pka = ''
        print('------> get_news, 5ka FAILED')

    
    news_lenta       = news_lenta if news_lenta else '<hr>На текущий момент свежих новостей нет.'
    news_perekrestok = news_perekrestok if news_perekrestok else '<hr>На текущий момент свежих новостей нет.'
    news_pka         = news_pka if news_pka else '<hr>На текущий момент свежих новостей нет.'

    news_array = '''<ul class="nav nav-tabs">
                        <li class="active"><a data-toggle="tab" href="#news_lenta"><img src="https://lenta.gcdn.co/static/pics/shortcuts/favicon-32x32.fb90679fd6d6da31ec7059b1cd4985e1.png"></a></li>
                        <li><a data-toggle="tab" href="#news_perekrestok"><img src="https://www.perekrestok.ru/favicon.ico"></a></li>
                        <li><a data-toggle="tab" href="#news_pka"><img src="https://5ka.ru/img/icons/favicon-32x32.png"></a></li>
                    </ul>
                    <div class="tab-content" style="margin-bottom: 20px;">
                        <div id="news_lenta" class="tab-pane fade in active">
                            {news_lenta}
                        </div>
                        <div id="news_perekrestok" class="tab-pane fade">
                            {news_perekrestok}
                        </div>
                        <div id="news_pka" class="tab-pane fade">
                            {news_pka}
                        </div>
                    </div>'''.format(news_lenta=news_lenta, news_perekrestok=news_perekrestok, news_pka=news_pka)    
    
    news = db.session.query(News).get(1)
    if news:
        news.html_news = news_array
        news.date_news = dt.now()
    else:
        news = News(html_news=news_array, date_news=dt.now())    
        db.session.add(news)
        
    db.session.commit()
    print('News updated')

def get_catalog():
    goods = {
        'Выпечка': ['Выпечка', 'Наша пекарня'],
        'Заправки__соусы': ['Маринады',
                           'Наборы для приготовления блюд',
                           'Растительные масла',
                           'Соусы, Майонезы и кетчуп',
                           'Заправки, соусы',
                           'Майонезы и майонезные заправки',
                           'Уксус',
                           'Томатные пасты, кетчуп',
                           'Соусы',
                           'Растительное масло',
                           'Майонез',
                           'Горчица, хрен'],
        'Каши': ['Сухие завтраки',
                 'Хлопья и каши',
                 'Подушечки, мюсли, хлопья',
                 'Каши',
                 'Каши и сухие смеси'],
        'Колбасные_изделия': ['Колбасные изделия',
                              'Колбасные изделия и мясные деликатесы',
                              'Сосиски и сардельки',
                              'Сосиски, сардельки, шпикачки',
                              'Колбасы, ветчина',
                              'Паштеты, зельцы',
                              'Деликатесы и копчености'],
        'Кондитерские_изделия': ['Сезонные кондитерские изделия',
                                 'Мучные кондитерские изделия',
                                 'Кондитерские изделия собственного производства',
                                 'Печенье, пряники, вафли',
                                 'Пироги, сдоба, кексы, рулеты',
                                 'Печенье, крекер, вафли, пряники'],
        'Консервация': ['Консервация',
                        'Консервированные овощи',
                        'Консервы рыбные',
                        'Фруктовые и ягодные консервы',
                        'Рыбные консервы и кулинария',
                        'Овощные консервы',
                        'Мёд',
                        'Мясные консервы',
                        'Варенье, джемы, сиропы'],
        'Конфеты': ['Конфеты',
                    'Конфеты, леденцы и жевательные резинки',
                    'Жевательная резинка'],
        'Крупы': ['Крупы, рис', 'Крупы и зерновые', 'Крупы и бобовые'],
        'Макароны': ['Макаронные изделия', 'Макароны, паста'],
        'Масло__маргарин': ['Масло, маргарин', 'Сливочное масло и маргарин', 'Масло, маргарин, спред'],
        'Молочная_продукция': ['Молочная продукция',
                               '"Йогурты*\n* Кроме йогуртов для детей"',
                               'Кефир, кисломолочные продукты',
                               'Молоко',
                               'Сметана',
                               'Сырки глазированные',
                               '"Творог и творожные продукты*\n* Кроме творожных продуктов дл',
                               'Творог, сырки',
                               'Сливки',
                               'Сгущенка, молочные консервы',
                               'Молочные продукты',
                               'Молочные коктейли и лакомства',
                               'Кисломолочные продукты и закваски',
                               'Йогурты, творожки, десерты'],
        'Мороженое': ['Мороженое'],
        'Мука': ['Мука блинная', 'Мука пшеничная', 'Мука ржаная', 'Все для выпечки', 'Мука', 'Компоненты для выпечки'],
        'Мясо': ['Мясо охлажденное',
                 'Охлажденные мясные субпродукты',
                 'Мясные продукты собственного производства',
                 'Продукты мясной переработки',
                 'Мясо глубокой заморозки',
                 'Фарш',
                 'Свинина',
                 'Говядина'],
        'Овощи': ['Томаты, перец и огурцы свежие', 'Овощи', 'Овощи и смеси', 'Зелень и  салаты', 'Грибы'], # << --- зелень и__салаты так и надо
        'Полуфабрикаты': ['Полуфабрикаты',
                          'Готовые блюда',
                          'Пельмени, манты, хинкали',
                          'Блины, вареники, сырники',
                          'Замороженные кондитерские изделия',
                          'Пельмени',
                          'Пицца, вареники, пельмени, блины',
                          'Котлеты, наггетсы, тесто'],
        'Продукты_быстрого_приготовления': ['Продукты быстрого приготовления', 'Другие'], # <<---- в кат. Другие есть корма для жив., сух. завтраки, соки и мнг. другое
        'Птица': ['Курица',
                  'Индейка',
                  'Птица глубокой заморозки',
                  'Охлажденное мясо птицы',
                  'Субпродукты',                # <<< ------ !! возможно в отдельную категорию Субпродукты (пока есть только в перекрестке)
                  'Мясо, птица и субпродукты',  # <<< ------ !! возможно отдельная категория (пока есть только в перекрестке)
                  'Мясо птицы',
                  'Яйцо',
                  'Яйца'],
        'Рыбная_продукция': ['Охлажденная и переработанная рыбная продукция',
                             'Готовая рыбная продукция',
                             'Рыба и морепродукты глубокой заморозки',
                             'Соленая, маринованная рыба',
                             'Рыба',
                             'Охлажденная рыба ', #<< -- так и должно быть
                             'Крабовое мясо и палочки',
                             'Копченая рыба',
                             'Вяленая, сушеная рыба и морепродукты'], # <<< --- в ПЯТЁРОЧКЕ в ДРУГИЕ есть суш рыба
        'Рыбные_деликатесы': ['Деликатесы из рыбы и морепродуктов',
                              'Деликатесы из рыбы и морепродуктов в рассоле/масле',
                              'Морепродукты',
                              'Морепродукты и креветки',
                              'Икра'],
        'Cладости': ['Зефир, мармелад, восточные сладости',
                     'Зефир, мармелад и пастила',
                     'Зефир, мармелад, пастила',
                     'Восточные сладости, халва'],
        'Соль__cахар': ['Сахар, соль',
                       'Сахар-песок',
                       'Сахар-рафинад',
                       'Сахар тростниковый',
                       'Соль морская',
                       'Соль поваренная',
                       'Соль',
                       'Сахар'],
        'Cпеции': ['Приправы, специи',
                   'Специи',
                   'Универсальные специи',
                   'Приправы',
                   'Смеси для вторых блюд',
                   'Специи и приправы'],
        # 'Нац_кухня': ['Продукты национальной кухни'], есть только в ЛЕНТЕ, содержит и макароны и специи и соусы и кокос молоко и много другое
        'Сухофрукты__орехи__семечки': ['Сухофрукты, орехи, семечки',
                                     'Семечки и орехи',
                                     'Семечки, сухофрукты',
                                     'Орехи'],
        'Сыры': ['Сыр', 'Мягкие и творожные сыры', 'Твердые сыры', 'Сыры'],
        'Торты': ['Торты, пирожные, выпечка', 'Торты, пирожные и десерты', 'Торты, пирожные'],
        'Фрукты': ['Цитрусовые фрукты', 'Яблоки', 'Бананы', 'Фрукты', 'Ягоды и фрукты', 'Ягоды'],
        'Хлеб': ['Хлеб', 'Хлеб, лаваш, лепешки'],
        'Хлебобулочные_изделия': ['Хлебобулочные изделия', 'Сушки, сухари, хлебцы'],
        'Чипсы__сухарики__снеки': ['Чипсы, сухарики, снеки', 'Чипсы и сухарики', 'Чипсы, снеки, попкорн'],
        'Шоколад': ['Шоколад', 'Шоколад и шоколадные изделия', 'Шоколад, батончики']
        }    
    return goods

def get_category(category_name):
    goods = get_catalog()
    for key, values in goods.items():
        if category_name in values:
            return key
    return ''

def costruct_name(name):
    costruct_name = name.replace('.', ' ')\
                        .replace(',', ' ')\
                        .replace('"', ' ')\
                        .replace('/', ' ')\
                        .replace("'", '')\
                        .replace('ё', 'е')\
                        .replace(' г', 'г')\
                        .replace(' мл', 'мл')\
                        .replace(' кг', 'кг')\
                        .replace(' шт', 'шт')\
                        .replace(' уп', 'уп')
    
    return ' '.join(costruct_name.split())

# варианты сортировок
def by_discount(elem):
    return elem['discount']

def by_price(elem):
    return elem['new_price']


def get_html_product(product_array, index, key, reverse):
    ul = ''
    div = ''    
    sort_product_array = sorted(product_array, key=key, reverse=reverse)
    for row in sort_product_array:
        row_index = str(sort_product_array.index(row))
        tab_href = index+'_'+row_index
        class_active = 'class="active"' if row_index == '0' else ''
        in_active = 'in active' if row_index == '0' else ''
        li ='''<li {class_active}>
                    <a data-toggle="tab" href="#{tab_href}">
                        <img src="{favicon}">
                    </a>
                </li>'''.format(class_active=class_active, tab_href=tab_href, favicon=row['favicon'])
        
        tab_content = '''<div id="{tab_href}" class="tab-pane fade {in_active}">
                            <div class="thumb-wrapper">
                                <span id='heart' class="wish-icon"><i class="fa fa-heart-o"></i></span>
                                <div class="img-box">
                                    <img src="{img}" class="img-responsive" alt="">
                                </div>
                                <div class="thumb-content">
                                    <a href="{href}" target="_blank"><h4>{name}</h4></a>
                                    <p class="discount"><b>-{discount}%</b></p>
                                    <div class="sku-card">
                                        <p class="item-price">Новая цена: <b><span>{new_price}<span></b></p>
                                        <p class="item-price">Старая цена: <span>{old_price}</span></p>
                                    </div>
                                </div>
                            </div>
                        </div>'''.format(in_active=in_active,
                                         tab_href=tab_href,
                                         img=row['img'],
                                         href=row['href'],
                                         name=row['name'],
                                         new_price="{:.2f}".format(row['new_price']),
                                         old_price="{:.2f}".format(row['old_price']),
                                         discount=row['discount'])
        ul = ul + li
        div = div + tab_content
    
    product_html = '''<ul class="nav nav-tabs">{ul}</ul>
                      <div class="tab-content">{div}</div>'''.format(ul=ul, div=div)

    return product_html

def html_creator(sort_method, category_number, offset, count_of_products, products_per_row, add_loading, checked=None, search_text=None, sku=None):

    if sku:
        sorted_products = db.session.query(Sku).get(sku).sku_html_1
        html_text = '<div class="row"><div class="col-xs-12 col-sm-6 col-md-6 col-lg-3">'+sorted_products+'</div></div>'
        return {'html_text': html_text, 'show_load_button': False}
    else:
        if sort_method == 'null':
            if category_number:
                if checked:
                    sorted_products = db.session.query(Sku.sku_html_1).filter(Sku.sku_category==category_number, Sku.sku_twin==True).order_by(desc(Sku.sku_discount_desc), Sku.sku_name).offset(offset).limit(13).all()
                else:
                    sorted_products = db.session.query(Sku.sku_html_1).filter_by(sku_category=category_number).order_by(desc(Sku.sku_discount_desc), Sku.sku_name).offset(offset).limit(13).all()
            else:
                if checked:
                    if search_text:
                        sorted_products = db.session.query(Sku.sku_html_1).filter(Sku.sku_twin==True, Sku.sku_lowercase.like(search_text)).order_by(desc(Sku.sku_discount_desc), Sku.sku_name).offset(offset).limit(13).all()
                    else:                        
                        sorted_products = db.session.query(Sku.sku_html_1).filter(Sku.sku_twin==True).order_by(desc(Sku.sku_discount_desc), Sku.sku_name).offset(offset).limit(13).all()
                else:
                    if search_text:
                        sorted_products = db.session.query(Sku.sku_html_1).filter(Sku.sku_lowercase.like(search_text)).order_by(desc(Sku.sku_discount_desc), Sku.sku_name).offset(offset).limit(13).all()
                    else:
                        sorted_products = db.session.query(Sku.sku_html_1).order_by(desc(Sku.sku_discount_desc), Sku.sku_name).offset(offset).limit(13).all()        
        elif sort_method == 'asc':
            if category_number:
                if checked:
                    sorted_products = db.session.query(Sku.sku_html_2).filter(Sku.sku_category==category_number, Sku.sku_twin==True).order_by(Sku.sku_price_asc, Sku.sku_name).offset(offset).limit(13).all()
                else:
                    sorted_products = db.session.query(Sku.sku_html_2).filter_by(sku_category=category_number).order_by(Sku.sku_price_asc, Sku.sku_name).offset(offset).limit(13).all()
            else:
                if checked:
                    if search_text:
                        sorted_products = db.session.query(Sku.sku_html_2).filter(Sku.sku_twin==True, Sku.sku_lowercase.like(search_text)).order_by(Sku.sku_price_asc, Sku.sku_name).offset(offset).limit(13).all()
                    else:
                        sorted_products = db.session.query(Sku.sku_html_2).filter(Sku.sku_twin==True).order_by(Sku.sku_price_asc, Sku.sku_name).offset(offset).limit(13).all()
                else:
                    if search_text:
                        sorted_products = db.session.query(Sku.sku_html_2).filter(Sku.sku_lowercase.like(search_text)).order_by(Sku.sku_price_asc, Sku.sku_name).offset(offset).limit(13).all()
                    else:
                        sorted_products = db.session.query(Sku.sku_html_2).order_by(Sku.sku_price_asc, Sku.sku_name).offset(offset).limit(13).all()
        elif sort_method == 'desc':
            if category_number:
                if checked:
                    sorted_products = db.session.query(Sku.sku_html_3).filter(Sku.sku_category==category_number, Sku.sku_twin==True).order_by(desc(Sku.sku_price_desc), Sku.sku_name).offset(offset).limit(13).all()
                else:
                    sorted_products = db.session.query(Sku.sku_html_3).filter_by(sku_category=category_number).order_by(desc(Sku.sku_price_desc), Sku.sku_name).offset(offset).limit(13).all()
            else:
                if checked:
                    if search_text:
                        sorted_products = db.session.query(Sku.sku_html_3).filter(Sku.sku_twin==True, Sku.sku_lowercase.like(search_text)).order_by(desc(Sku.sku_price_desc), Sku.sku_name).offset(offset).limit(13).all()
                    else:
                        sorted_products = db.session.query(Sku.sku_html_3).filter(Sku.sku_twin==True).order_by(desc(Sku.sku_price_desc), Sku.sku_name).offset(offset).limit(13).all()
                else:
                    if search_text:
                        sorted_products = db.session.query(Sku.sku_html_3).filter(Sku.sku_lowercase.like(search_text)).order_by(desc(Sku.sku_price_desc), Sku.sku_name).offset(offset).limit(13).all()
                    else:
                        sorted_products = db.session.query(Sku.sku_html_3).order_by(desc(Sku.sku_price_desc), Sku.sku_name).offset(offset).limit(13).all()
    
    html_text_carousel_indicators, html_text_carousel_inner, html_text, group_of_products = '', '', '', ''
    indexes = [i for i in range(products_per_row-1, count_of_products, products_per_row)] # получаем индексы, кот. помогают разбивать товары для слайда/строки

    for product_array in sorted_products[0:12]:
        product_index = sorted_products.index(product_array) # !!!!
        if add_loading:
            product = '<div class="col-xs-12 col-sm-6 col-md-6 col-lg-3">' + product_array[0] + '</div>'
        else:
            product = '<div class="col-sm-{size}">'.format(size=int(count_of_products/products_per_row)) + product_array[0] + '</div>'
        group_of_products = group_of_products + product
        if product_index in indexes:
            if add_loading:
                html_text = html_text + '<div class="row">' + group_of_products + '</div>'
            else:
                number_index = indexes.index(product_index)
                if number_index == 0:
                    html_text_carousel_indicators = '<li data-target="#myCarousel1" data-slide-to="0" class="active"></li>'
                    html_text_carousel_inner = '<div class="item carousel-item active">'+group_of_products+'</div>'
                else:
                    html_text_carousel_indicators = html_text_carousel_indicators + '<li data-target="#myCarousel1" data-slide-to="{}"></li>'.format(number_index)
                    html_text_carousel_inner = html_text_carousel_inner + '<div class="item carousel-item">'+group_of_products+'</div>'
            group_of_products = ''
    
    if len(group_of_products) > 0:
        html_text = html_text + '<div class="row">' + group_of_products + '</div>'
    
    show_load_button = True
    if len(sorted_products) < 13:
        show_load_button = False
    
    return {'carousel_indicators': html_text_carousel_indicators, 'carousel_inner': html_text_carousel_inner, 'html_text': html_text, 'show_load_button': show_load_button}

def main_search():
    get_news()
    lenta_category_skus       = LENTA()
    perekrestok_category_skus = PEREKRESTOK()
    pka_category_skus         = PKA()

    # удаляем все записи в таблице Sku
    db.session.query(Sku).delete()
    db.session.commit()
    
    beg             = dt.now()
    _all            = 0 # общее число одинаковых товаров
    _total          = 0 # общее число товаров
    category_number = 0 # счетчик для нумерования категорий товара
    
    for category in get_catalog().keys():
        lenta       = []
        perekrestok = []
        pka         = []
        if category in lenta_category_skus.keys():
            lenta = lenta_category_skus[category]
        if category in perekrestok_category_skus.keys():
            perekrestok = perekrestok_category_skus[category]
        if category in pka_category_skus.keys():
            pka = pka_category_skus[category]
        print('Объдиняем категорию:', category)
        start = dt.now()
        k   = 0 # для смещения по базам товаров
        _in = 0 # число одинаковых товаров в категории
        arrays = [lenta, perekrestok, pka]
        for arr1 in arrays:
            k += 1
            for elem1 in arr1:
                if elem1['indicator'] == 1:
                    continue
                product = []
                product.append(elem1)
                _total += 1
                for arr2 in arrays[k:len(arrays)]:
                    index_token_set_ratio = 0
                    for elem2 in arr2:
                        # сравнение элементов на схожесть
                        if elem1['weight'] != elem2['weight']:
                            continue
                        # первый способ сравнения
                        token_set_ratio = fuzz.token_set_ratio(elem1['name'], elem2['name'])
                        if token_set_ratio > index_token_set_ratio:
                            index_token_set_ratio = token_set_ratio
                            goods_token_set_ratio = elem2['name']
                            type_token_set_ratio  = elem2['type']
                            if token_set_ratio == 100: # если 100% совпадение, то дальше не нужно сравнивать
                                break
                    if index_token_set_ratio == 100:
                        elem2['indicator'] = 1 # elem2 внесен в похожие товары, вносить его еще раз в массив product не имеет смысла
                        product.append(elem2)
                        print('<<<<<', elem1['name'], elem1['type'], '   ',goods_token_set_ratio, type_token_set_ratio,' (token set ratio: ', index_token_set_ratio,')', sep='')
                        _in  += 1 # число одинаковых товаров в категории
                        _all += 1 # общее число одинаковых товаров
                
                # #algoliasearch
                # index_algoliasearch.save_object({'objectID': _total, 'product': product})
                
                #create a sku in database
                index = ''.join(choices(ascii_uppercase + ascii_lowercase + digits, k=12)) # получаем случайный индекс

                sku_discount_desc = sorted(product, key=by_discount, reverse=True) # макс скидка
                sku_price_asc     = sorted(product, key=by_price)                  # мин цена
                sku_price_desc    = sorted(product, key=by_price, reverse=True)    # макс цена

                sku_html_1 = get_html_product(product, index, by_discount, True)
                sku_html_2 = get_html_product(product, index, by_price, False)
                sku_html_3 = get_html_product(product, index, by_price, True)

                sku = Sku(id=index,
                          sku_category=category_number,
                          sku_name=elem1['name'],
                          sku_lowercase=elem1['name'].lower(), # по нему будет происходить поиск
                          sku_price_asc=sku_price_asc[0]['new_price'],
                          sku_price_desc=sku_price_desc[0]['new_price'],
                          sku_discount_desc=sku_discount_desc[0]['discount'],
                          sku_html_1=sku_html_1,
                          sku_html_2=sku_html_2,
                          sku_html_3=sku_html_3,
                          sku_twin=True if len(product)>1 else False)

                db.session.add(sku)
                db.session.commit()
        
        category_number += 1        
        finish = dt.now()
        print('')
        print('----Время анализа кат. '+category+' составило: '+ str(finish-start)+' сек.----')
        print('----Внесено: '+str(_in)+'----')
        print('')
    # фиксируем дату обновления данных

    end = dt.now()
    print('Общее время выполнения: '+str(end-beg)+' сек.')
    print('Всего внесено: '+str(_all))
    print('Общее количество товара: '+str(_total))
