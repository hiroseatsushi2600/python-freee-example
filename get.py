import json
import time
import requests
import yaml
import shutil
import datetime

t_delta = datetime.timedelta(hours=9)
JST = datetime.timezone(t_delta, 'JST')
now = datetime.datetime.now(JST)

env_yaml_filename = 'env1.yaml'
env_yaml_file = open(env_yaml_filename)
env_yaml = yaml.safe_load(env_yaml_file)
print(env_yaml)
client_id = env_yaml['client_id']
client_secret = env_yaml['client_secret']
company_id = env_yaml['company_id']
access_token = env_yaml['tokens']['access_token']
refresh_token = env_yaml['tokens']['refresh_token']

env_yaml_file.close()


# 認証
def check_auth():
    print("check_auth()")
    # 試しに勘定科目を取ってみる
    response = get_freee("items", {"company_id": company_id})
    if response.status_code == 401:
        print("トークンが有効期限切れでした")
        new_token = get_refresh_token()
        env_yaml['tokens']['access_token'] = new_token['access_token']
        env_yaml['tokens']['refresh_token'] = new_token['refresh_token']
        refresh_env_file(env_yaml, env_yaml_filename)
        print("リフレッシュしました")
        return True
    elif response.status_code == 200:
        print("トークンはまだ有効みたい")
        # print(response.json())
        return True
    else:
        print("トークン認証が失敗しました")
        return False


def get_refresh_token():
    refresh_token_params = {
        "grant_type": "refresh_token",
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token
    }
    authorization_url = 'https://accounts.secure.freee.co.jp/public_api/token'
    r = requests.post(authorization_url, data=refresh_token_params)
    if r.ok:
        return r.json()
    else:
        print("-------------------------")
        print(r.json())
        print("-------------------------")
        return None


def refresh_env_file(yaml_json, current_file):
    d = now.strftime('%Y%m%d%H%M%S')
    backup_file = current_file + '.' + d + '.bk'
    shutil.copy(current_file, backup_file)
    with open(current_file, 'w') as f:
        yaml.dump(yaml_json, f, default_flow_style=False)


def get_freee(resourse, in_data):
    time.sleep(1)
    headers = {
        "accept": "application/json",
        "X-Api-Version": "2020-06-15",
        "Authorization": f"Bearer {env_yaml['tokens']['access_token']}"
    }
    response = requests.get(
        "https://api.freee.co.jp/api/1/" + resourse,
        headers=headers,
        data=in_data,
    )
    return response


# 事業所
# https://developer.freee.co.jp/docs/accounting/reference#/Companies/get_companies
def get_companies():
    print("<<<<<<事業所>>>>>>")
    response = get_freee("companies", {})
    print(response.json())
    f = open('companies.json', 'w')
    json.dump(response.json(), f)
    f.close()


# 品目タグ
def get_items():
    print("<<<<<<品目>>>>>>")
    response = get_freee("items", {"company_id": company_id})
    list = response.json()
    f = open('items.csv', 'w')
    for item in list['items']:
        f.write(str(item['id']) + ', ' + item['name'] + '\n')
    f.close()


# 明細
def get_wallet_txns():
    print("<<<<<<明細>>>>>>")
    data = {
        "company_id": company_id,
        "entry_side": "income",
    }
    response = get_freee("wallet_txns", data)
    print(response.json())


# とりひき
def get_deals():
    print("<<<<<<取引>>>>>>")
    data = {
        "company_id": company_id,
        "entry_side": "income",
    }
    response = get_freee("deals", data)
    print(response.json())
    f = open('deals.json', 'w')
    json.dump(response.json(), f)
    f.close()


# レポート 損益計算書
# https://developer.freee.co.jp/docs/accounting/reference#/Trial%20balance/get_trial_pl
def get_reports_trial_pl():
    print("<<<<<<損益計算書>>>>>>")
    data = {
        "company_id": company_id,
        "fiscal_year": 2022,
        "account_item_display_type": "account_item",
        # 品目ごとのお金の集計を見たいのでitemを指定する
        "breakdown_display_type": "item",
    }
    response = get_freee("reports/trial_pl", data)
    pl_json = response.json()
    f = open('report_trial_pl.json', 'w')
    json.dump(pl_json, f)
    f.close()
    balance_breaker_h(pl_json['trial_pl']['balances'])


# 貸借対照表
# https://developer.freee.co.jp/docs/accounting/reference#/Trial%20balance/get_trial_bs
def get_reports_trial_bs():
    print("<<<<<<貸借対照表>>>>>>")
    data = {
        "company_id": company_id,
        "fiscal_year": 2022,
        "account_item_display_type": "account_item",
        "breakdown_display_type": "item",
    }
    response = get_freee("reports/trial_bs", data)
    bs_json = response.json()
    f = open('report_trial_bs.json', 'w')
    json.dump(bs_json, f)
    f.close()
    balance_breaker_h(bs_json['trial_bs']['balances'])


def balance_breaker_v(balances):
    for it in balances:
        indent = ""
        if type(it.get('hierarchy_level')) is int:
            indent = "    " * it.get('hierarchy_level')
        print(indent + "勘定科目 : " + yoshinani(it.get('account_item_name')))
        print(indent + "勘定科目ID : " + yoshinani(it.get('account_item_id')))
        print(indent + "hierarchy_level : " + yoshinani(it.get('hierarchy_level')))
        print(indent + "account_category_name : " + yoshinani(it.get('account_category_name')))
        print(indent + "parent_account_category_name : " + yoshinani(it.get('parent_account_category_name')))
        print(indent + "opening_balance : " + yoshinani(it.get('opening_balance')))
        print(indent + "debit_amount : " + yoshinani(it.get('debit_amount')))
        print(indent + "credit_amount : " + yoshinani(it.get('credit_amount')))
        print(indent + "closing_balance : " + yoshinani(it.get('closing_balance')))
        print(indent + "composition_ratio : " + yoshinani(it.get('composition_ratio')))
        if it.get('items') is not None:
            print(indent + "    明細 : ")
            for it2 in it.get('items'):
                print("        " + str(it2))  # もうめんどくせ


def balance_breaker_h(balances):
    for it in balances:
        indent = ""
        if type(it.get('hierarchy_level')) is int and it.get('hierarchy_level') > 0:
            indent = "    " * (it.get('hierarchy_level') - 1)
        end_str = " | "
        print(indent, end=end_str)
        print(yoshinani(it.get('account_item_name')), end=end_str)
        print(yoshinani(it.get('account_item_id')), end=end_str)
        print(yoshinani(it.get('hierarchy_level')), end=end_str)
        print(yoshinani(it.get('account_category_name')), end=end_str)
        print(yoshinani(it.get('parent_account_category_name')), end=end_str)
        print(yoshinani(it.get('opening_balance')), end=end_str)
        print(yoshinani(it.get('debit_amount')), end=end_str)
        print(yoshinani(it.get('credit_amount')), end=end_str)
        print(yoshinani(it.get('closing_balance')), end=end_str)
        print(yoshinani(it.get('composition_ratio')))
        if it.get('items') is not None:
            for it2 in it.get('items'):
                print(indent + "  ∟ " + str(it2))  # もうめんどくせ


def yoshinani(value):
    if type(value) is str:
        return value
    elif type(value) is int or type(value) is float:
        return str(value)
    else:
        return ''


if check_auth():
    # get_wallet_txns()
    # get_reports_trial_pl()
    # get_reports_trial_bs()
    get_companies()
    get_deals()
