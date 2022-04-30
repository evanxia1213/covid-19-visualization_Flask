from flask import Flask, jsonify
import requests, json, time
from flask_cors import CORS
pip3 install flask, flask_cors # 安装依赖

app = Flask(__name__)
CORS(app,  resources={r"/*": {"origins": "*"}})   # 允许所有域名跨域
"""
此处为数据爬取部分
"""

def parse_alldata():
    res = requests.get(
        url='https://c.m.163.com/ug/api/wuhan/app/data/list-total',
        headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:99.0) Gecko/20100101 Firefox/99.0',
        }
    ).json()

    if res['msg'] == '成功':
        overall_Data = res['data']['chinaTotal']
        daily_Data = res['data']['chinaDayList']
        province_Data = res['data']['areaTree']
        return [overall_Data, daily_Data, province_Data]

    else:
        return print(f"数据爬取失败, 原因：{res['msg']}")


@app.route('/api/covid-19/overall')
def get_overall():
    overall_Data = parse_alldata()[0]
    json_overall = {
        "success": True,
        "code": 200,
        "message": "成功",
        "data": {
            "confirmedCount": overall_Data.get('total').get('confirm'),  # 历史累计确诊
            "confirmedIncr": overall_Data.get('today').get('confirm'),  # 今日确诊
            "curedCount": overall_Data.get('total').get('heal'),  # 历史累计治愈
            "curedIncr": overall_Data.get('today').get('heal'),  # 今日治愈
            "currentConfirmedCount": overall_Data.get('total').get('confirm')
                                     - overall_Data.get('total').get('dead')
                                     - overall_Data.get('total').get('heal'),  # 现有确诊
            "currentConfirmedIncr": overall_Data.get('today').get('storeConfirm'),  # 今日确诊增加
            "deadCount": overall_Data.get('total').get('dead'),  # 历史累计死亡
            "deadIncr": overall_Data.get('today').get('dead'),  # 今日死亡
            "importedCount": overall_Data.get('total').get('input'),  # 现有境外输入
            "importedIncr": overall_Data.get('today').get('input'),  # 今日境外输入增加
            "noInFectCount": overall_Data.get('extData').get('noSymptom'),  # 现有无症状感染
            "noInFectIncr": overall_Data.get('extData').get('incrNoSymptom'),  # 今日无症状感染增加
            "suspectIncr": 0,
            "suspectCount": 0,
            "updateTime": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            "curedRate": round(overall_Data.get('total').get('heal') / overall_Data.get('total').get('confirm')*100, 2),  # 治愈率(%)
            "deadRate": round(overall_Data.get('total').get('dead') / overall_Data.get('total').get('confirm')*100, 2)  # 死亡率(%)
        }
    }
    with open('data/covid19-overall.json', 'w') as f:
        json.dump(json_overall, f)
        print(f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}：Request: get_overall | Respond：json_overall.js')
    return json_overall


@app.route('/api/covid-19/daily')
def get_daily():
    daily_Data = parse_alldata()[1]
    importedIncrList = []
    curedCountList = []
    confirmedCountList = []
    currentConfirmedIncrList = []
    importedCountList = []
    noInFectCountList = []
    currentConfirmedCountList = []

    for i in daily_Data:
        importedIncrList.append([i.get('date'), i.get('today').get('input')])  # 该日境外输入
        curedCountList.append([i.get('date'), i.get('total').get('heal')])  # 累计治愈
        confirmedCountList.append([i.get('date'), i.get('total').get('confirm')])  # 累计确诊
        currentConfirmedIncrList.append([i.get('date'), i.get('today').get('confirm')])  # 当日确诊
        importedCountList.append([i.get('date'), i.get('total').get('input')])  # 累计境外输入
        noInFectCountList.append([i.get('date'), i.get('today').get('suspect')])  # 新增无症状感染者
        currentConfirmedCountList.append([i.get('date'), i.get('total').get('input')])  # 现有确诊

    # noInFectCountList.append([today, res.get('data').get('chinaTotal').get('extData').get('noSymptom')])
    json_daily = {
        "success": True,
        "code": 200,
        "message": "操作成功",
        "data": {
            "importedIncrList": importedIncrList,  # 该日境外输入
            "curedCountList": curedCountList,  # 累计治愈
            "confirmedCountList": confirmedCountList,  # 累计确诊
            "currentConfirmedIncrList": currentConfirmedIncrList,  # 当日确诊
            "importedCountList": importedCountList,  # 累计境外输入
            "noInFectCountList": noInFectCountList,  # 新增无症状感染者
            "currentConfirmedCountList": currentConfirmedCountList  # 现有确诊
        }
    }
    with open('data/covid19-daily-list.json', 'w') as f:
        json.dump(json_daily, f)
        print(f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}：Request: get_daily | Respond：json_daily.js')
    return json_daily


@app.route('/api/covid-19/province')
def get_province():
    province_Data = parse_alldata()[2]

    provinces = province_Data[2]['children']
    all_provinces_ls = []
    for province in provinces:
        province_dict = {
            "confirmedCount": province['total']['confirm'],  # 确诊人数
            "countryLabel": "中国",
            "countryName": "China",
            "curedCount": province['total']['heal'],  # 治愈人数
            "curedRate": province['total']['heal'] / province['total']['confirm'] * 100.00,  # 治愈率
            "currentConfirmedCount": 28,
            "deadCount": province['total']['dead'],  # 死亡人数
            "deadRate": province['total']['dead'] / province['total']['confirm'] * 100.00,  # 死亡率
            "provinceLabel": province['name'],
            "provinceName": province['name'],
            "suspectCount": 0,
            "todayConfirmedCount": province['today']['confirm'],  # 今日确诊人数
            "updateTime": 'null'
        }
        all_provinces_ls.append(province_dict)

    json_province={
        "success": True,
        "code": 200,
        "message": "操作成功",
        "data": all_provinces_ls
    }
    with open('data/covid19-province.json', 'w') as f:
        json.dump(json_province, f)
        print(f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}：Request: get_province | Respond：json_province.js')
    return json_province


if __name__ == '__main__':
    app.run(host="0.0.0.0")
