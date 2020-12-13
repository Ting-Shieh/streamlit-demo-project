
"""
專門處理性別資料
"""
gender_data = {
    "data": [
        {
            "cat_id": 1,
            "cat_name": "飲料沖泡",
            "male_tag": [],
            "female_tag": []
        },
        {
            "cat_id": 2,
            "cat_name": "麵食料理",
            "male_tag": [],
            "female_tag": []
        },
        {
            "cat_id": 3,
            "cat_name": "美食生鮮",
            "male_tag": [],
            "female_tag": []
        },
        {
            "cat_id": 4,
            "cat_name": "保健生機",
            "male_tag": ['男', '乳清', '保險套'],
            "female_tag": ['女']
        },
        {
            "cat_id": 5,
            "cat_name": "居家生活",
            "male_tag": ['刮鬍刀'],
            "female_tag": []
        },
        {
            "cat_id": 6,
            "cat_name": "美容保養",
            "male_tag": ['落建', '剃刀', '刀組', '刀片'],
            "female_tag": ['衛生', '護墊', '私密處', '染髮', '日用', '夜用', '膠原', '化妝', '眼霜', '精華', '女']
        },
        {
            "cat_id": 7,
            "cat_name": "家電",
            "male_tag": ['防潮箱', '投影機'],
            "female_tag": ['吹風', '披肩']
        },
        {
            "cat_id": 8,
            "cat_name": "箱包服飾",
            "male_tag": ['男'],
            "female_tag": ['女']
        },
        {
            "cat_id": 9,
            "cat_name": "零食",
            "male_tag": [],
            "female_tag": []
        },
        {
            "cat_id": 10,
            "cat_name": "其他",
            "male_tag": [],
            "female_tag": []
        },
        {
            "cat_id": 11,
            "cat_name": "旅遊住宿",
            "male_tag": [],
            "female_tag": []
        },
        {
            "cat_id": 12,
            "cat_name": "3C",
            "male_tag": [],
            "female_tag": ['披肩']
        },
        {
            "cat_id": 13,
            "cat_name": "菸酒",
            "male_tag": [],
            "female_tag": []
        },
        {
            "cat_id": 14,
            "cat_name": "寵物專區",
            "male_tag": [],
            "female_tag": []
        },
        {
            "cat_id": 15,
            "cat_name": "生活休閒",
            "male_tag": [],
            "female_tag": []
        }
    ]
}


"""
專門處理年齡資料
'*' 表示 只要有買此類別商品即算加分條件
"""
ages_data = {
    "group_level": [
        {
            "group_id": 1,
            "age_range": "18-24"
        },
        {
            "group_id": 2,
            "age_range": "25-34"
        },
        {
            "group_id": 3,
            "age_range": "35-44"
        },
        {
            "group_id": 4,
            "age_range": "45-54"
        },
        {
            "group_id": 5,
            "age_range": "55以上"
        },

    ],
    "time_level": [
        {
            "time_id": 1,
            "time_range": [0, 12],
            "time_tags": "上午"
        }, {
            "time_id": 2,
            "time_range": [12, 14],
            "time_tags": "中午"
        }, {
            "time_id": 3,
            "time_range": [14, 18],
            "time_tags": "下午"
        }, {
            "time_id": 4,
            "time_range": [18, 24],
            "time_tags": "晚上"
        }
    ],
    "category_data": [
        {
            "cat_id": 1,
            "items_tag": [{'gid': 1, "tags": ['濾掛']},
                          {'gid': 2, "tags": ['薑茶', '濾掛', '大麥汁', '西雅圖', '春茶', '調理包', '紅龍']},
                          {'gid': 3, "tags": ['薑茶', '椰子汁', '濾掛', '牛蒡茶', '大麥汁', '西雅圖', '春茶', '咖啡膠囊']},
                          {'gid': 4, "tags": ['薑茶', '椰子汁', '牛蒡茶', '大麥汁', '西雅圖', '春茶', '咖啡膠囊']},
                          {'gid': 5, "tags": ['薑茶', '椰子汁', '牛蒡茶', '春茶', '咖啡膠囊']}],
            "is_used": True
        }, {
            "cat_id": 2,
            "items_tag": [{'gid': 1, "tags": ['調理包', '紅龍']},
                          {'gid': 2, "tags": ['紅棗', '味噌湯']},
                          {'gid': 3, "tags": ['佛跳牆', '蜂花粉', '紅棗', '薑黃粉', '麻油', '味噌湯']},
                          {'gid': 4, "tags": ['佛跳牆', '蜂花粉', '薑黃粉', '麻油', ]},
                          {'gid': 5, "tags": ['佛跳牆', '蜂花粉', '薑黃粉', '麻油', ]}],
            "is_used": True
        }, {
            "cat_id": 3,
            "items_tag": [{'gid': 1, "tags": []},
                          {'gid': 2, "tags": ['雞湯', '產銷履歷']},
                          {'gid': 3, "tags": ['雞湯', '產銷履歷']},
                          {'gid': 4, "tags": ['雞湯', '產銷履歷']},
                          {'gid': 5, "tags": []}, ],
            "is_used": True
        }, {
            "cat_id": 4,
            "items_tag": [{'gid': 1, "tags": ['乳清', '保險套', '胺基酸']},
                          {'gid': 2, "tags": ['乳清', '保險套', '胺基酸', '葉酸', ]},
                          {'gid': 3, "tags": ['乳清', '保險套', '膠原粉', '四物飲', '低週波', '胺基酸', '葉酸', '亞培', '美強生']},
                          {'gid': 4, "tags": ['護具', '膠原粉', '四物飲', '低週波', '亞培', '美強生']},
                          {'gid': 5, "tags": ['護具', '四物飲', '老花']}],
            "is_used": True
        }, {
            "cat_id": 5,
            "items_tag": [{'gid': 1, "tags": []},
                          {'gid': 2, "tags": ['滿意寶寶', '幫寶適', '敢動褲', '雙人', '氣炸鍋', '料理台', '油炸鍋', '快煮壺', '敢動褲', '兒童牙刷']},
                          {'gid': 3,
                           "tags": ['滿意寶寶', '幫寶適', '敢動褲', '雙人', '氣炸鍋', '兒童桌', '料理台', '電器組', '油炸鍋', '主管椅', '濾水箱', '敢動褲',
                                    '兒童牙刷']},
                          {'gid': 4,
                           "tags": ['滿意寶寶', '幫寶適', '敢動褲', '雙人', '氣炸鍋', '兒童桌', '料理台', '電器組', '油炸鍋', '主管椅', '濾水箱']},
                          {'gid': 5, "tags": ['來復易', '濾水箱']}, ],
            "is_used": True
        }, {
            "cat_id": 6,
            "scores_tag": [{'gid': 1, "tags": []},
                           {'gid': 2, "tags": []},
                           {'gid': 3, "tags": []},
                           {'gid': 4, "tags": []},
                           {'gid': 5, "tags": []}, ],
            "is_used": False
        }, {
            "cat_id": 7,
            "items_tag": [{'gid': 1, "tags": []},
                          {'gid': 2, "tags": ['顯示器', '洗碗機', '烤箱', '縫紉機', '冰箱']},
                          {'gid': 3, "tags": ['投影機', '淨水器', '乾衣機', '顯示器', '洗碗機', '烤箱', '縫紉機', '冰箱', '冰櫃']},
                          {'gid': 4, "tags": ['投影機', '淨水器', '乾衣機', '顯示器', '洗碗機', '冰櫃', '保險箱', '清淨機']},
                          {'gid': 5, "tags": ['淨水器', '乾衣機', '保險箱', '清淨機']}, ],
            "is_used": True
        }, {
            "cat_id": 8,
            "items_tag": [{'gid': 1, "tags": []},
                          {'gid': 2, "tags": []},
                          {'gid': 3, "tags": ['克拉']},
                          {'gid': 4, "tags": ['克拉']},
                          {'gid': 5, "tags": []}, ],
            "is_used": True
        }, {
            "cat_id": 9,
            "items_tag": [{'gid': 1, "tags": []},
                          {'gid': 2, "tags": []},
                          {'gid': 3, "tags": []},
                          {'gid': 4, "tags": []},
                          {'gid': 5, "tags": []}, ],
            "is_used": False
        }, {
            "cat_id": 10,
            "items_tag": [{'gid': 1, "tags": []},
                          {'gid': 2, "tags": []},
                          {'gid': 3, "tags": ['續約', '純金', '應稅']},
                          {'gid': 4, "tags": ['續約', '純金', '應稅']},
                          {'gid': 5, "tags": ['續約', '純金', '應稅']}],
            "is_used": True
        }, {
            "cat_id": 11,
            "items_tag": [{'gid': 1, "tags": []},
                          {'gid': 2, "tags": []},
                          {'gid': 3, "tags": ['專案', '六福', '喜來登']},
                          {'gid': 4, "tags": ['專案', '六福', '喜來登']},
                          {'gid': 5, "tags": []}, ],
            "is_used": True
        }, {
            "cat_id": 12,
            "items_tag": [{'gid': 1, "tags": ['羅技', '鍵盤', '耳機', '攝影機', 'IPAD']},
                          {'gid': 2, "tags": ['IPHONE', '羅技', '鍵盤', '耳機', '攝影機', '印表機', '播放器', 'IPAD']},
                          {'gid': 3, "tags": ['ASUS', '揚聲器', '監視器', 'IPHONE', '印表機', '播放器']},
                          {'gid': 4, "tags": ['氣象偵測', '警報器', 'ASUS', '揚聲器', '監視器', 'IPHONE', 'IPAD']},
                          {'gid': 5, "tags": ['氣象偵測', '警報器']}, ],
            "is_used": True
        }, {
            "cat_id": 13,
            "items_tag": [{'gid': 1, "tags": ['啤酒']},
                          {'gid': 2, "tags": ['啤酒']},
                          {'gid': 3, "tags": ['*']},
                          {'gid': 4, "tags": ['*']},
                          {'gid': 5, "tags": ['*']}, ],
            "is_used": True
        }, {
            "cat_id": 14,
            "items_tag": [{'gid': 1, "tags": []},
                          {'gid': 2, "tags": []},
                          {'gid': 3, "tags": []},
                          {'gid': 4, "tags": []},
                          {'gid': 5, "tags": []}, ],
            "is_used": False
        }, {
            "cat_id": 15,
            "items_tag": [{'gid': 1, "tags": []},
                          {'gid': 2, "tags": []},
                          {'gid': 3, "tags": []},
                          {'gid': 4, "tags": []},
                          {'gid': 5, "tags": []}, ],
            "is_used": False
        }
    ],
    "time_data": [{'gid': 1, "tags": [1, 2, 3]},
                  {'gid': 2, "tags": [2, 4]},
                  {'gid': 3, "tags": [2, 4]},
                  {'gid': 4, "tags": [2, 4]},
                  {'gid': 5, "tags": [1, 2, 3, 4]}

                  ],
    "weekday_data": [
        {'gid': 1, "tags": [1, 2, 3, 4, 5]},
        {'gid': 2, "tags": [5, 6, 7]},
        {'gid': 3, "tags": [5, 6, 7]},
        {'gid': 4, "tags": [5, 6, 7]},
        {'gid': 5, "tags": [5, 6, 7]}
    ]
}


"""
專門處理收入資料
這邊以後只有有新的 group id
皆要重新配值 xxx_data 中 gid/tags..的關聯!!!
"""
income_data = {
    "group_level": [
        {
            "group_id": 1,
            "income_range": "35萬以下"
        },
        {
            "group_id": 2,
            "income_range": "35萬-50萬"
        },
        {
            "group_id": 3,
            "income_range": "50萬-75萬"
        },
        {
            "group_id": 4,
            "income_range": "75萬-100萬"
        },
        {
            "group_id": 5,
            "income_range": "100萬以上"
        },

    ],
    # 之後這邊改成自動化excel處理
    "citys_data": [
        {'gid': 1, "tags": ['臺南市', '苗栗縣', '彰化縣', '南投縣', '雲林縣', '嘉義縣', '屏東縣', '臺東縣', '花蓮縣'], "city_cat_list": []},
        {'gid': 2, "tags": ['高雄市', '宜蘭縣', '澎湖縣', '基隆市'], "city_cat_list": []},
        {'gid': 3, "tags": ['新北市', '桃園市', '臺中市'], "city_cat_list": []},
        {'gid': 4, "tags": ['新竹縣', '嘉義市', '新竹市'], "city_cat_list": []},
        {'gid': 5, "tags": ['臺北市'], "city_cat_list": []},
    ],
    # 年齡層對收入可能性
    "ages_data": [
        {'gid': 1, "tags": ['18-24'], "age_cat_list": []},
        {'gid': 2, "tags": ['25-34'], "age_cat_list": []},
        {'gid': 3, "tags": ['35-44', '45-54'], "age_cat_list": []},
        {'gid': 4, "tags": ['35-44', '45-54', '55以上'], "age_cat_list": []},
        {'gid': 5, "tags": ['55以上'], "age_cat_list": []},
    ],

}


