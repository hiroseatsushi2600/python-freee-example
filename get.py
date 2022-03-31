import requests

# freeeの事業所ID
company_id = 9999999
# アクセストークン 初回発行とリフレッシュは自力でやってください。
access_token = "*******************************************"

common_headers = {
    "accept": "application/json",
    "X-Api-Version": "2020-06-15",
    "Authorization": f"Bearer {access_token}",
}


# data = {"company_id": company_id}


# 勘定科目
def get_account_items():
    response = get_freee("account_items", {"company_id": company_id})
    list = response.json()
    f = open('account_items.txt', 'w')
    for item in list['account_items']:
        # print(item)
        f.write(str(item['id']) + ', ' + item['name'] + '\n')
    f.close()


# 品目
def get_items():
    response = get_freee("items", {"company_id": company_id})
    list = response.json()
    f = open('items.txt', 'w')
    for item in list['items']:
        # print(item)
        f.write(str(item['id']) + ', ' + item['name'] + '\n')
    f.close()


# レポート 損益計算書
def get_report_trial_pl():
    data = {
        "company_id": company_id,
        "fiscal_year": 2022,
        "account_item_display_type": "account_item",
        # 品目ごとのお金の集計を見たいのでitemを指定する
        "breakdown_display_type": "item",
    }
    response = get_freee("reports/trial_pl", data)
    list = response.json()
    # print(list['trial_pl'])
    print(list['trial_pl']['company_id'])
    print(list['trial_pl']['fiscal_year'])
    print(list['trial_pl']['account_item_display_type'])
    print(list['trial_pl']['breakdown_display_type'])
    print(list['trial_pl']['created_at'])
    print(list['trial_pl']['balances'])
    print("----------------------------")

    # ぐるぐる
    for it in list['trial_pl']['balances']:
        print(it.get('account_item_id'))  # account_item_idは一番上の1行目だけっぽい
        print(it.get('account_item_name'))
        print(it.get('account_category_name'))  # account_category_nameは2行目からっぽい
        print(it.get('hierarchy_level'))
        print(it.get('parent_account_category_name'))
        print(it.get('opening_balance'))
        print(it.get('debit_amount'))
        print(it.get('credit_amount'))
        print(it.get('closing_balance'))
        print(it.get('composition_ratio'))
        if it.get('items') is not None:
            for it2 in it.get('items'):
                print("    " + str(it2))
                print("    ----------------------------")
        print("----------------------------")


def get_freee(resourse, in_data):
    response = requests.get(
        "https://api.freee.co.jp/api/1/" + resourse,
        headers=common_headers,
        data=in_data,
    )
    return response


# 使いたければコメントはずして
# 勘定科目
# get_account_items()
# 品目
# get_items()
# 損益計算書
get_report_trial_pl()
