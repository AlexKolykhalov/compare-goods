from app        import db
from app.main   import bp
from app.models import Sku, News
from app.parcer import connecton_check, main_search, get_catalog, html_creator, get_news #(delete main_search & get_news)

from flask      import render_template, request, make_response, url_for



@bp.route('/')
def index():
    connecton_check()
    # get_news()
    print('News done.')
    news = db.session.query(News).get(1)
    return render_template('index.html', news=news)
        

@bp.route('/goods/')
@bp.route('/goods/<category_number>')
def goods(category_number=None):
    sku         = request.args.get('sku')
    search_text = request.args.get('search_text')
    checked     = request.cookies.get('switch_value')
            
    data = html_creator(sort_method='null',                                                           
                        search_text=search_text,
                        checked=checked,
                        sku=sku,
                        category_number=category_number,
                        offset=0,
                        count_of_products=12,
                        products_per_row=4,
                        add_loading=True)

    html_text        = data['html_text']
    show_load_button = data['show_load_button']
    title = 'Все предложения'
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
    return render_template('goods.html', html_text=html_text, show_load_button=show_load_button, title=title, checked=checked)

@bp.route('/search/')
def search():
    s = request.args.get('search_text')
    search_result = db.session.query(Sku).get(sku).sku_html_1
    product = '<div class="row"><div class="col-xs-12 col-sm-6 col-md-6 col-lg-3">' + search_result + '</div></div>'
    return render_template('goods.html', data=product)

@bp.route('/news')
def news():
    return render_template('news.html')

#ajax
@bp.route('/get_discount')
def get_discount():
    count_of_products = int(request.args.get('count_of_products')) # общее количество товаров в слайдере
    products_per_row  = int(request.args.get('products_per_row'))  # количество отображаемого товара для одного слайда    
    
    return html_creator(sort_method='null',                        
                        category_number=None,
                        offset=0,
                        count_of_products=count_of_products,
                        products_per_row=products_per_row,
                        add_loading=False)

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
    offset          = int(request.args.get('offset')) # количество товаров на странице discounts    
    sort_method     = request.args.get('sort_method') # метод сортировки (возр/убыв)
    search_text     = None if request.args.get('search_text') == '' else  request.args.get('search_text')        # текст поиска
    category_number = None if request.args.get('category_number') == '' else request.args.get('category_number') # номер категории товара
    checked         = request.cookies.get('switch_value')

    return html_creator(sort_method=sort_method,
                        search_text=search_text,
                        checked=checked,
                        category_number=category_number,
                        offset=offset,
                        count_of_products=12,
                        products_per_row=4,
                        add_loading=True)

#ajax
@bp.route('/products_search')
def products_search():
    search_text = request.args.get('search_text').lower()
    # --------------------
    #
    # --------------------
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