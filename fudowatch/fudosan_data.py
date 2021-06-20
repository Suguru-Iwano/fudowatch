class Fudosan():
    """システム内で使用する不動産情報
    各不動産サイトごとに、取得したいパラメータがある場合は、
    このクラスを継承し、パラメータを追加する
    """

    def __init__(self, id='', name='', site='', price=-1, rent=-1.0, parkings=0, url_detail='', url_image='', else_data_list=[], is_published=True):
        self.id = id  # document名　全サイト内で一意である必要がある
        self.name = name  # 物件の名前
        self.site = site  # 監視対象サイト名
        self.price = price  # 物件の売値
        self.rent = rent  # 物件の賃料
        self.parkings = parkings   # 駐車可能台数
        self.url_detail = url_detail  # 詳細ページへのリンク
        self.url_image = url_image  # 物件画像へのリンク
        self.else_data_list = else_data_list  # その他の情報リスト
        self.is_published = is_published  # 公開・非公開フラグ


class Fudosan_akiyabank_nagato(Fudosan):
    def __init__(self, id='', name='', site='', price=-1, rent=-1.0, parkings=0, url_detail='', url_image='', else_data_list=[], is_published=True):
        super().__init__(id, name, site, price, rent, parkings,
                         url_detail, url_image, else_data_list, is_published)
