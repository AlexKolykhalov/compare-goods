from app        import db
# from app        import index_algoliasearch
from app.main   import bp
from app.parcer import get_catalog, html_creator, get_random_index, crud_operation
from app.models import Sku, News, Users, DbStatus

from flask       import render_template, request, url_for
from flask_login import current_user, login_user
from datetime    import datetime as dt

import json



@bp.before_app_request
def before_app_request():
    if current_user.is_authenticated:
        current_user.visit_time = dt.now()
        db.session.commit()
    
@bp.route('/')
def index():
    news = db.session.query(News).get(1)
    return render_template('index.html', news=news.html_news, updates=news.date_news.strftime('%d-%m-%Y %H:%M:%S'))

@bp.route('/goods/')
@bp.route('/goods/<category_number>')
def goods(category_number=None):
    sku                   = request.args.get('sku')
    hearts_values         = request.args.get('hearts_values') # нажали на heart в nav-bar
    search_text           = request.args.get('search_text')
    only_twin             = request.cookies.get('switch_value')
    
    heart_productsId = json.loads(current_user.heart_productsId)['id'] if current_user.is_authenticated else []

    data = html_creator(sort_method='null',
                        search_text=search_text,
                        only_twin=only_twin,
                        sku=sku,
                        hearts_values=None if hearts_values is None else heart_productsId,
                        category_number=category_number,
                        offset=0,
                        count_of_products=12,
                        products_per_row=4,
                        add_loading=True)

    html_text        = data['html_text']
    show_load_button = data['show_load_button']
    title = 'Все предложения'
    show_checkbox = True
    if search_text:
        title = 'Результат поиска: "'+search_text.replace('%', '')+'"'
    if category_number:
        catalog_keys = list(get_catalog().keys())
        for key in catalog_keys:
            if catalog_keys.index(key) == int(category_number):            
                title = key.replace('__', ', ').replace('_', ' ')
                break
    if sku:
        title = 'Карточка товара'
        show_checkbox = False
    
    if hearts_values is not None:
        title = 'Любимые товары'
    
    if current_user.is_authenticated:
        # set hearts
        html_text = set_heart_class(html_text=html_text, hearts_values=hearts_values) # значения hearts_values ('' или None)
                                                                                      # меняем класс fa fa-heart-o/fa fa-heart
                                                                                      # в зависимости от наличия current_user.heart_productsId
    
    return render_template('goods.html', html_text=html_text, 
                                         show_load_button=show_load_button, 
                                         title=title, 
                                         checked=only_twin, 
                                         show_checkbox=show_checkbox)

def set_heart_class(html_text, hearts_values=None):
    if hearts_values is not None:
        html_text = html_text.replace('class="fa fa-heart-o"', 'class="fa fa-heart"')
    else:
        for val in json.loads(current_user.heart_productsId)['id']:
            old = '<i id="{id}" class="fa fa-heart-o"></i>'.format(id=val)
            new = '<i id="{id}" class="fa fa-heart"></i>'.format(id=val)
            html_text = html_text.replace(old, new)

    return html_text

#ajax
@bp.route('/get_html_carousel_inner')
def get_html_carousel_inner():
    count_of_products = int(request.args.get('count_of_products')) # общее количество товаров в слайдере
    products_per_row  = int(request.args.get('products_per_row'))  # количество отображаемого товара для одного слайда    
    
    data = html_creator(sort_method='null',                        
                        category_number=None,
                        offset=0,
                        count_of_products=count_of_products,
                        products_per_row=products_per_row,
                        add_loading=False)
    
    if current_user.is_authenticated:
        # set hearts
        data['carousel_inner'] = set_heart_class(html_text=data['carousel_inner']) # меняем класс fa fa-heart-o/fa fa-heart
                                                                                   # в зависимости от наличия current_user.heart_productsId
    
    return data

#ajax
@bp.route('/get_catalog_tree')
def get_catalog_tree():
    lis = '<li><h4><a class="catalog-tree" href="/goods/">Все предложения</a></h4></li>'
    k = 0    
    for key in get_catalog().keys():
        li = '<li><h4><a class="catalog-tree" href="{}">'.format(k)+key.replace('__', ', ').replace('_', ' ')+'</a></h4></li>'
        lis = lis + li
        k += 1
    return '<ul class="catalog-tree">'+lis+'</ul>'

#ajax
@bp.route('/add_loading')
def add_loading():
    offset          = int(request.args.get('offset')) # скрытое число (см. offset на стр. goods, а также ajax-запросы)
    sort_method     = request.args.get('sort_method') # метод сортировки (возр/убыв)
    search_text     = None if request.args.get('search_text') == '' else  request.args.get('search_text')        # текст поиска
    category_number = None if request.args.get('category_number') == '' else request.args.get('category_number') # номер категории товара
    hearts_values   = None if request.args.get('hearts_values') is None else json.loads(current_user.heart_productsId)['id']   # id товаров, которые выбраны как любимые
    only_twin       = request.cookies.get('switch_value')
    
    data = html_creator(sort_method=sort_method,
                        search_text=search_text,
                        only_twin=only_twin,
                        hearts_values=hearts_values,
                        category_number=category_number,
                        offset=offset,
                        count_of_products=12,
                        products_per_row=4,
                        add_loading=True)

    if current_user.is_authenticated:
        # set hearts
        data['html_text'] = set_heart_class(html_text=data['html_text'], hearts_values=hearts_values) # меняем класс fa fa-heart-o/fa fa-heart 
                                                                                                  # в зависимости от наличия current_user.heart_productsId    
    
    return data

#ajax
@bp.route('/products_search')
def products_search():    
    # # -------for algolia-------------
    # search_text = request.args.get('search_text')
    # search_result = index_algoliasearch.search(search_text)
    # -------for postgresql----------    
    search_text = request.args.get('search_text').lower()
    result = 'Ничего не найдено'
    products = ''
    categories = ''
    search_text = '%{}%'.format(search_text)
    search_result = db.session.query(Sku.id, Sku.sku_name).filter(Sku.sku_lowercase.like(search_text)).limit(10).all()
    for search_element in search_result:
        products = products + '<a href="{}">'.format(url_for('main.goods', sku=search_element[0]))+search_element[1]+'</a><br>'
    if products:
        result = '<b>Товары</b><br>'+products+'<a href="{}">'.format(url_for('main.goods', search_text=search_text))+'<b>Показать всех <i class="fa fa-angle-double-right" aria-hidden="true"></i></b></a>'

    return result

#ajax
@bp.route('/check_db_status')
def check_db_status():
    dbStatus = db.session.query(DbStatus).get(1)
    result = dbStatus.status if dbStatus.status else '0'
    return result

#ajax
@bp.route('/db_operation', methods=['post'])
def db_operation():
    operation = request.form.get('operation') # create/delete
    userId    = request.form.get('userId')
    heartId   = request.form.get('heartId')   # id wish-icon
    if not userId:
        userId = get_random_index(size=24)
    count_of_hearts = crud_operation(operation=operation, userId=userId, heartId=heartId)
    
    return {'userId': userId, 'count_of_hearts': count_of_hearts}