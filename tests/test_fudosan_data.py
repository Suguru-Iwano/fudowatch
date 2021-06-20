from fudowatch.fudosan_data import Fudosan_akiyabank_nagato


def test_Fudosan_akiyabank_nagato():
    fudosan = Fudosan_akiyabank_nagato()
    # 初期値確認
    assert fudosan.name == ''
    assert fudosan.price == -1
    assert fudosan.rent == -1
    assert fudosan.parkings == 0
    assert fudosan.url_detail == ''
    assert fudosan.url_image == ''
    assert fudosan.else_data_list == []
    assert fudosan.is_published == True


def Fudosan_akiyabank_nagato_from_dict():
    d = {'name': 'name',
         'price': 1,
         # 'rent': 2,
         'parkings': 3,
         'url_detail': 'http://detail',
         # 'url_image': 'http://image',
         'else_data_list': ['one', 'two']
         }

    fudosan = Fudosan_akiyabank_nagato(**d)
    assert fudosan.name == 'name'
    assert fudosan.price == 1
    assert fudosan.rent == -1
    assert fudosan.parkings == 3
    assert fudosan.url_detail == 'http://detail'
    assert fudosan.url_image == ''
    assert fudosan.else_data_list == ['one', 'two']
