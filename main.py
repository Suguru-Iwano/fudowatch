import os
import traceback

from fudowatch.akiyabank_nagato import get_fudosan_generator
from fudowatch.common import (get_pubsub_message, get_secret, get_soup,
                              read_config, send_message)
from fudowatch.fudosan_data import Fudosan, Fudosan_akiyabank_nagato
from fudowatch.storage_access import FiresoreClient


def whether_to_notify(f: Fudosan):
    """通知するかどうか決定する
    """


def main(event, context):
    # TODO:引数で監視サイト切り替え

    site_to_monitor = get_pubsub_message(event)

    try:
        # 設定値を取得
        config_ini_path = 'config.ini'
        config_ini = read_config(config_ini_path)
        # PubSubのメッセージ = 設定値区分
        load_url = config_ini.get(site_to_monitor, 'Url')
        collection_name = config_ini.get(site_to_monitor, 'Collection')
        messenger_token_key = config_ini.get('common', 'Messenger_token_key')
        messenger_token_key_version = config_ini.get(
            'common', 'Messenger_token_key_version')

        # 物件情報サイトの物件リストを、Generetorにパース
        # ここのみサイト毎に変わる
        fudosan_gen = get_fudosan_generator(get_soup(load_url))

        project_id = os.getenv('GCLOUD_PROJECT') or ''
        messenger_token = get_secret(
            project_id, messenger_token_key, messenger_token_key_version)

        client = FiresoreClient(project_id)
        # 物件情報を取得
        fudosan_collection = client.get_collection(collection_name)

        # 公開されている物件情報を取得しておく（fudosan_genにないものをFalseしたい）
        doc_is_pub = fudosan_collection.where(
            u'is_published', u'==', True)

        published_id_list = []

        # TODO:ここを関数に切り分け、テストを書きたい
        for f in fudosan_gen:
            # すでに登録されている情報を取得
            pre_f = fudosan_collection.document(f.id).get()
            # 公開物件リストに登録
            published_id_list.append(pre_f.id)
            # すでに登録されている場合
            if pre_f.exists:
                # 変更がある場合
                if pre_f._data != f.__dict__:
                    # 文字列からクラスを生成
                    pre_f_obj = globals()['Fudosan_' +
                                          site_to_monitor](**pre_f.to_dict())
                    # 登録
                    # TODO:物件情報変更時の登録・通知

                    # 登録されていない場合
            else:
                # TODO:通知する物件の絞り込み
                client.set_document(collection_name, 'id', f)
                message = f"""
新しい物件情報があります。
物件名: {f.name}
売値: 　{f.price}万円
{f.url_detail}"""
                send_message(messenger_token, message)

        # 非公開になった物件を更新
        for f in doc_is_pub.stream():
            if f.id not in published_id_list:
                fudosan_collection.document(
                    f.id).update({'is_published': False})

    except Exception:
        print(traceback.format_exc())
        raise
