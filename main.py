import os
import traceback
from typing import Generator

# TODO:ここのimoprtを動的に呼び出したい
from fudowatch.akiyabank_nagato import get_fudosan_generator
from fudowatch.common import (get_pubsub_message, get_secret, get_soup,
                              read_config, send_message)
from fudowatch.fudosan_data import *  # 文字列でクラスが呼ばれるため、全てのクラスをimportしておく
from fudowatch.storage_access import FiresoreClient


def whether_to_notify(f: Fudosan):
    """通知するかどうか決定する
    """
    return -1 < f.price < 400


def notify_add(f: Fudosan, messenger_token):
    """whether_to_notifyの時のみ、通知する
    """
    if whether_to_notify(f):
        message = f"""
新しい物件情報があります。
name:    {f.name}
price:   {f.price}万円
parkings:{f.parkings}台
{f.url_detail}"""
        send_message(messenger_token, message)


def get_dict_diff(d_pre: dict, d: dict) -> Generator:
    for key in d_pre.keys():
        if d_pre[key] != d[key]:
            yield key


def notify_update(f: Fudosan, f_pre: Fudosan, messenger_token):
    """whether_to_notifyの時のみ、通知する
    """

    if whether_to_notify(f):
        diff_key_gen = get_dict_diff(f_pre.__dict__, f.__dict__)

        changed_txt = ''
        for key in diff_key_gen:
            changed_txt += f'{key}: {getattr(f_pre, key)} -> {getattr(f, key)}\n'

        message = f"""
物件情報が変更されました。
{changed_txt}
{f.url_detail}"""
        send_message(messenger_token, message)


def main(event, context):

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

        project_id = os.getenv('GCLOUD_PROJECT') or ''
        messenger_token = get_secret(
            project_id, messenger_token_key, messenger_token_key_version)

        # 物件情報サイトの物件リストを、Generetorにパース
        # ここのみサイト毎に変わる
        fudosan_gen = get_fudosan_generator(get_soup(load_url))

        client = FiresoreClient(project_id)
        # 物件情報を取得
        fudosan_collection = client.get_collection(collection_name)

        # 公開されている物件情報を取得しておく（fudosan_genにないものをFalseしたい）
        doc_is_pub = fudosan_collection.where(
            u'is_published', u'==', True)

        published_id_list = []

        # TODO:ここを関数に切り分け、テストを書きたい
        for f in fudosan_gen:
            # 公開物件リストに登録
            published_id_list.append(f.id)

            # すでに登録されている情報を取得
            pre_f = fudosan_collection.document(f.id).get()
            # すでに登録されている場合
            if pre_f.exists:
                # 文字列からクラスを生成
                pre_f_dic = pre_f.to_dict()
                del(pre_f_dic['timestamp'])
                del(pre_f_dic['timestamp_added'])
                pre_f_obj = globals()['Fudosan_' +
                                      site_to_monitor](**pre_f_dic)
                if pre_f_obj.__dict__ != f.__dict__:
                    # 値段が変更された場合、通知
                    if pre_f_obj.price != f.price:
                        notify_update(f, pre_f_obj, messenger_token)
                    # 登録
                    client.set_document(collection_name, f.id, f)
            # 登録されていない場合
            else:
                notify_add(f, messenger_token)
                # 登録
                client.set_document(collection_name, f.id, f,
                                    additional_timestamp_key='timestamp_added')

        # 非公開になった物件を更新
        for f in doc_is_pub.stream():
            if f.id not in published_id_list:
                fudosan_collection.document(
                    f.id).update({'is_published': False})

    except Exception:
        print(traceback.format_exc())
        raise
