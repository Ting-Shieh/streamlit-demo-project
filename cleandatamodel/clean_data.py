import pandas as pd
from collections import Counter
# from sqlhelpertool.dbhelper import SqlHelper
from cleandatamodel import settings

def do_Insert(df, dbobj):
    """
        將整理完的用戶資料， 插入至DB
    :param df: 結果 dataframe
    :param dbobj: SQL 類
    :return:
    """
    row_count = 1
    _db = dbobj()
    for index, col in df.iterrows():

        sql = "Insert into users(carrier_id,gender,city,age,district,created_at)"
        sql += " values(%s,%s,%s,%s,%s,%s)"
        nowTime = _db.getnowtime()
        info_tuple = (str(col["carrier_id"]),
                      str(col["gender"]),
                      str(col["city"]),
                      int(col["age_level"]),
                      int(col["income_level"]),
                     nowTime
                     )

        try:
            mycursor = _db.get_mycursor()
            mycursor.execute(sql, info_tuple)
            mydb=_db.get_mydb()
            mydb.commit()
            print("id:%s =>record inserted." % row_count)
        except Exception as e:
            print(e)
        finally:
            row_count += 1
        mycursor.close()
        mydb.close()

def id_mapping(df):
    """
        把分群中文名改成 DB(ages table， incomes table) 的 id
    :param df:
    :return:
    """
    age_dict = { item['age_range']:item['group_id'] for item in settings.ages_data['group_level'] }
    income_dict = { item['income_range']:item['group_id'] for item in settings.income_data['group_level'] }
    df['age_level'] = df['age_level'].map(age_dict)
    df['income_level'] = df['income_level'].map(income_dict)

class CleanGender:
    def __init__(self, data=settings.gender_data):
        self.__data = data

    def mapTagStr(self, pname, _list, gender):
        for item in _list:
            if item in pname:
                return gender

    def get_Gender(self, c_id, pname):
        if self.__data['data'][int(c_id) - 1]['male_tag']:
            gender = self.mapTagStr(pname, self.__data['data'][int(c_id) - 1]['male_tag'], '男性')
            if gender:
                return gender
            else:
                if self.__data['data'][int(c_id) - 1]['female_tag']:
                    gender = self.mapTagStr(pname, self.__data['data'][int(c_id) - 1]['female_tag'], '女性')
                    if gender:
                        return gender

    def do_CleanGender(self, invoice_df):
        res_df = pd.DataFrame()
        invoice_df.set_index(keys=['carrier_number', 'cat_id'], inplace=True)
        for uid in invoice_df.index.get_level_values('carrier_number').unique():
            gender = ''
            _dict = dict()
            _dict['carrier_id'] = uid
            _dict['gender'] = ''
            _dict['pname'] = ''
            # print('===>', uid, '---', invoice_df.loc[uid].index.unique())
            for cid in invoice_df.loc[uid].index.unique():
                if cid == 0:
                    # 跳過不執行代表
                    continue

                # print(cid, '---', invoice_df.loc[(uid, cid), 'product_name'].values.tolist())
                for pname in invoice_df.loc[(uid, cid), 'product_name'].values.tolist():
                    gender = self.get_Gender(cid, str(pname))
                    if gender is not None:
                        _dict['gender'] = gender
                        _dict['pname'] = pname
                        break
                if _dict['pname']:
                    # 代表已經匹配到性別
                    break
            res_df = res_df.append(_dict, ignore_index=True)
        return res_df




class CleanRegion:

    def clean_col(self, df, region_col='store_address'):
        # step1. 删掉空行
        df = df[~(df[region_col].isnull())]

        # step2. 切割地域
        df['city'] = df[region_col].apply(lambda x: self.tagCity(x))

        return df.groupby(['carrier_number', 'city']).size().to_frame()

    def tagCity(self, address):
        """
            抓取縣市字元，判別地域
        :param address: 地理欄位
        :return: 地域字串  '新北市'
        """
        if '縣' not in address:
            _idx = address.find('市')
            return address[:_idx + 1]
        else:
            _idx = address.find('縣')
            return address[:_idx + 1]

    def getCity(self, region_df, x):

        return \
        region_df.loc[region_df.index.get_level_values('carrier_number') == x].index.get_level_values('city').values[0]

    def do_CleanRegion(self, add2df, region_df, _fun):
        add2df["city"] = add2df['carrier_id'].apply(
            lambda x: _fun(region_df, x)
        )
        return add2df


class CleanAge:
    def __init__(self, data=settings.ages_data):
        self.__data = data  # == ages_data

    def __get_souptime(self, t):
        """
            區別哪一個 time_level 裡的 time_id
        :param t: 購買時  ex.12點
        :return:
        """
        if t < 12:
            return 1
        elif 12 <= t < 14:
            return 2
        elif 14 <= t < 18:
            return 3
        else:
            return 4

    def __get_scoredf(self):
        """
            建構計算分表
            carrier_id, 18-24, 25-34, 35-44, 45-54, 55以上
        :return: 計算分表
        """
        score_df = pd.DataFrame()
        score_df['carrier_id'] = ''
        score_df[self.__data['group_level'][0]['age_range']] = 0
        score_df[self.__data['group_level'][1]['age_range']] = 0
        score_df[self.__data['group_level'][2]['age_range']] = 0
        score_df[self.__data['group_level'][3]['age_range']] = 0
        score_df[self.__data['group_level'][4]['age_range']] = 0
        return score_df

    def __is_tag_list(self, cid, pname):
        """
            查看 category_data
            某一個商品名稱 是否含有特定關鍵字
        :param cid: 品項id
        :param pname: 商品名稱
        :return: group_id
        """

        glist = self.__data['category_data'][cid - 1]['items_tag']
        for gitem in glist:
            for tag in gitem['tags']:
                if tag not in pname and tag != '*':
                    continue
                if tag == '*' or tag in pname:
                    yield gitem['gid']
                break

    def __is_weekday_list(self, wk):
        """
            查看 weekday_data
            購買星期 是否含在特定族群星期內
        :param wk: 1~7 (表 禮拜 一 ~ 日)
        :return: group_id
        """
        """
        購買星期是否含在特定族群星期內
        """
        glist = self.__data['weekday_data']
        for gitem in glist:
            if wk not in gitem['tags']:
                continue
            yield gitem['gid']

    def __is_buytime_list(self, _t):
        """
            查看 time_data
            購買時間是否含在特定族群時間內
        :param _t: 購買時段  ex. ~12 (id = 1)/ 12~14 (id = 2)/ 14~16 (id = 3)/ 16~ (id = 4)
        :return: group_id
        """
        glist = self.__data['time_data']
        for gitem in glist:
            if _t not in gitem['tags']:
                continue
            yield gitem['gid']

    def add_scores(self, _dict, _add, _li):
        """
            加分功能
            (未來可以調控擴大)
        :param _dict: {'carrier_id': uid,'18-24': 0,'25-34': 0,'35-44': 0,'45-54': 0,'55以上': 0}
        :param _add: 預計加給幾
        :param _li: group_id list 個別項
        :return: 加分後的 _dict
        """
        _dict[self.get_groupname(_li)] += 1
        return _dict

    def cal_age_scores(self, df):
        """
            計算每一用戶對於符合某條件下的加分運算邏輯
        :param df: 用戶購買多重索引df
        :return: 年齡計算分表 df
        """
        score_df = self.__get_scoredf()
        for uid in df.index.get_level_values('carrier_number').unique():
            user_dict = {'carrier_id': uid,
                         '18-24': 0,
                         '25-34': 0,
                         '35-44': 0,
                         '45-54': 0,
                         '55以上': 0}

            # Todo =============================== cid 部分 ===============================
            # print(" ============================== Start cid Part ============================== ")
            for cid in df.loc[uid].index.unique():

                if cid == 0:
                    break
                for pname in df.loc[(uid, cid), 'product_name']:
                    if not self.__data['category_data'][cid - 1]['is_used']:
                        break

                    for li in self.__is_tag_list(cid, pname):
                        # user_dict[self.get_groupname(li)]+=1    # 加一分  舊版
                        user_dict = self.add_scores(_dict=user_dict, _add=1, _li=li)  # 加一分  新版(之後可調)

            #     print('next category')  # 測試打印
            # print(user_dict)  # 測試打印

            # Todo =============================== weekday 部分 ===============================
            # print(" ============================== Start WeekDay Part ============================== ")
            wk = df.loc[uid, 'weekday'].unique()[0]
            for li in self.__is_weekday_list(wk):
                # user_dict[self.get_groupname(li)]+=1            # 加一分  舊版
                user_dict = self.add_scores(_dict=user_dict, _add=1, _li=li)  # 加一分  新版(之後可調)

            # print(user_dict)  # 測試打印
            # Todo =============================== 購買時段 部分 ===============================
            # print(" ============================== Start 購買時段 Part ============================== ")
            for tt in df.loc[(uid, slice(None)), 'time_tags'].unique().tolist():
                for li in self.__is_buytime_list(tt):
                    # user_dict[self.get_groupname(li)]+=1        # 加一分  舊版
                    user_dict = self.add_scores(_dict=user_dict, _add=1, _li=li)  # 加一分  新版(之後可調)

            # print('用戶: ', uid, '探索完畢 !!', '以下為分數=>', user_dict)  # 測試打印
            score_df = score_df.append(user_dict, ignore_index=True)

        return score_df

    def get_groupname(self, gid):
        """
            取得此 group_id 的年齡層名稱
        :param gid: group_id
        :return: 年齡層名稱
        """

        return self.__data['group_level'][gid - 1]['age_range']

    def clean_col(self, df):
        """
            # step-1
            清理欄位資料
        :param df: 初始df
        :return: 清理後的 df
        """

        # step1 cat_id 補值 (df=invoice_df)
        df['cat_id'] = df['cat_id'].fillna(0).astype('int32')

        # step2 處理時間數據
        df['invoice_date'] = pd.to_datetime(df['invoice_date'])

        df['dates'] = df['invoice_date'] + df['invoice_time']  # 轉乘 datetime

        # step3 標記購買時間段
        df['time_tags'] = df['dates'].dt.hour.apply(lambda x: self.__get_souptime(x))  #

        # step4 標記購買日為星期幾
        df['weekday'] = df['dates'].dt.weekday.apply(lambda x: x + 1)

        # step5 再次清理columns
        df.drop(columns=['invoice_date', 'invoice_time'], inplace=True)

        # step6 多重索引 df 化
        df.set_index(keys=['carrier_number', 'cat_id'], inplace=True)

        return df

    def do_CleanAge(self, df, res_df):
        """
            執行 年齡層分布清洗 流程
        :param df: 用戶購買多重索引df
        :param res_df: 做完 地域分布的結果
        :return: 和 地域分布的結果合併的產出 df
        """

        # step 1 執行年齡層分布運算
        score_df = self.cal_age_scores(df)

        # step 2 找出每一 user 分數最高的值為何
        score_df['max_value'] = score_df[['18-24', '25-34', '35-44', '45-54', '55以上']].max(axis=1)

        # step 3 tag 分數最高的年齡層，並寫入欄位資料
        score_df['age_level'] = score_df[['18-24', '25-34', '35-44', '45-54', '55以上']].idxmax(axis=1)

        # step 4 結果合併
        res_df = pd.merge(res_df, score_df, how='outer')

        # step 4 去除欄位
        res_df.drop(columns=['18-24', '25-34', '35-44', '45-54', '55以上', 'max_value'], inplace=True)

        return res_df





class CleanIncome:
    def __init__(self, data = settings.income_data):
        self.__data = data

    def __cal_ucctp_value(self, df):
        """
                        uc(該用戶該類別)          /ct(該類別所有)
            該用戶 => 該類別消費額佔所有該類別總消費額的比例
        :param df:
        :return:
        """
        for i in range(15):
            cid = i + 1
            colname = 'uc_ct_p' + str(cid)
            df[colname] = (df[cid] / df[cid].sum()) * 100
        return df

    def __cal_ucutp_value(self, df):
        """
                    uc(該用戶該類別)  / ut(該用戶所有)
            該用戶 => 該類別消費額佔所有該用戶總消費額的比例
        :param df:
        :return:
        """
        for i in range(15):
            cid = i + 1
            colname = 'uc_ut_p' + str(cid)
            df[colname] = df[cid] / df["total_comsump"]
        return df

    def __ucctp_max_category(self, df):
        """
            找出對每個 user 來說，類別消費占整體類別最高的
        :param df:
        :return:
        """
        tag_col = ['uc_ct_p' + str(i + 1) for i in range(15)]
        df['max_partial_category'] = df[tag_col].idxmax(axis=1).str.replace('uc_ct_p', '')
        return df

    def __ucutp_max_category(self, df):
        """
            找出對每個 user 來說，自己消費最高的類別
        :param df:
        :return:
        """
        tag_col = ['uc_ut_p' + str(i + 1) for i in range(15)]
        df['max_comsump_category'] = df[tag_col].idxmax(axis=1).str.replace('uc_ut_p', '')
        return df

    def __get_scoredf(self, df):
        """
            建構計算分表
        :param df:
        :return:
        """
        for i in range(len(self.__data['group_level'])):
            df[self.__data['group_level'][i]['income_range']] = 0

    def group_name(self, _id):
        """
            依照 groupid，找回group_name
            之後可以對照 column name
        :param _id:
        :return:
        """
        for item in self.__data['group_level']:
            if item['group_id'] == _id:
                return item['income_range']

    def citys_data_scores(self, x, y, _type):
        """
            計分條件 - citys_data
        :param x: 是否在 citys_data 中的 tags 地區中
        :param y: 是否在 citys_data 中的 city_cat_list 類別中
        :param _type: 哪種幾分方式 'tags' / 'cat_list'
        :return: 收入分群名
        """
        if _type == 'tags':
            for item in self.__data['citys_data']:
                if x in item['tags']:
                    return self.group_name(item['gid'])
        elif _type == 'cat_list':
            for item in self.__data['citys_data']:
                if x in item['tags'] and y in item['city_cat_list']:
                    return self.group_name(item['gid'])

    def ages_data_scores(self, x, y, _type):
        """
            計分條件 - ages_data
        :param x: 是否在 ages_data 中的 tags 年齡層中
        :param y: 是否在 ages_data 中的 age_cat_list 類別中
        :param _type: 哪種幾分方式 'tags' / 'cat_list'
        :return: 收入分群名
        """
        _list = []
        if _type == 'tags':
            for item in self.__data['ages_data']:
                if x in item['tags']:
                    _list.append(self.group_name(item['gid']))
            return _list
        elif _type == 'cat_list':
            for item in self.__data['ages_data']:
                if x in item['tags'] and y in item['age_cat_list']:
                    _list.append(self.group_name(item['gid']))
            return _list


    def get_top_num(self, _list, num=3):
        """
            抓各縣市或是年齡層的各類別購買量排序
        :param _list: 各類別購買量排序
        :param num:取出前幾名
        :return:
        """
        sorted_data = sorted(enumerate(_list), key=lambda x: x[1], reverse=True)
        idx = [i[0] for i in sorted_data]
        datas = [i[1] for i in sorted_data]
        return idx[:num], datas[:num]

    def get_cat(self, enum, idx_list):
        """

        :param enum:
        :param idx_list:
        :return:
        """
        _list = []
        for item in enum:
            if item[0] in idx_list:
                _list.append(int(item[1]))
        return _list

    def cal_age_cat_values(self, df):
        """
            計分條件 - age_level vs max_partial_category
        :param df: 含記分板的表
        :return:
        """
        _dict = {}

        col_enum = list(enumerate(df.groupby(['age_level', 'max_partial_category']).size().unstack().columns.tolist()))

        # 建用各年齡層各類消費量前幾名 dict
        for idx in df.groupby(['age_level', 'max_partial_category']).size().unstack().fillna(0).astype('int32').index:
            _dict[idx] = df.groupby(['age_level', 'max_partial_category']).size().unstack().fillna(0).astype(
                'int32').loc[idx, :].tolist()

            idx_list, datas_list = self.get_top_num(_dict[idx], num=5)
            _dict[idx] = self.get_cat(enum=col_enum, idx_list=idx_list)

        #  匹對年齡層屬於何 gid ( 因為年齡層不會重複採此法)
        for age in _dict.keys():  # 此事發票源的縣市
            for i in range(len(self.__data['ages_data'])):
                if age in self.__data['ages_data'][i]['tags']:
                    self.__data['ages_data'][i]['age_cat_list'].extend(_dict[age])

                    # 每一 gid 必有多個年齡層，取合併 list 後排序最多前幾名
        # 賦予到原始data
        for item in self.__data['ages_data']:
            dic = sorted(Counter(item['age_cat_list']).items(), key=lambda item: item[1], reverse=True)

            item['age_cat_list'] = [item[0] for item in dic][:5]

        # 計算
        for idx, col in df.iterrows():
            _list = self.ages_data_scores(x=col['age_level'], y=int(col['max_partial_category']), _type='cat_list')
            if _list:
                col[_list] += 2

    def cal_city_cat_values(self, df):
        """
            計分條件 - city vs max_partial_category
        :param df:
        :return:
        """
        _dict = {}

        col_enum = list(enumerate(df.groupby(['city', 'max_partial_category']).size().unstack().columns.tolist()))

        # 建用各縣市各類消費量前幾名 dict
        for idx in df.groupby(['city', 'max_partial_category']).size().unstack().fillna(0).astype('int32').index:
            _dict[idx] = df.groupby(['city', 'max_partial_category']).size().unstack().fillna(0).astype('int32').loc[
                         idx, :].tolist()

            idx_list, datas_list = self.get_top_num(_dict[idx], num=5)
            _dict[idx] = self.get_cat(enum=col_enum, idx_list=idx_list)

        #  匹對縣市屬於何 gid ( 因為縣市不會重複採此法)
        for city in _dict.keys():  # 此事發票源的縣市

            for item in self.__data['citys_data']:  # 在 DI分層 為哪一級 gid
                if city in item['tags']:
                    item['city_cat_list'].extend(_dict[city])
                    break

        # 每一 gid 必有多個縣市，取合併 list 後排序最多前幾名
        # 賦予到原始data
        for item in self.__data['citys_data']:
            dic = sorted(Counter(item['city_cat_list']).items(), key=lambda item: item[1], reverse=True)
            item['city_cat_list'] = [item[0] for item in dic][:5]

        # 計算
        for idx, col in df.iterrows():
            col_name = self.citys_data_scores(x=col['city'], y=int(col['max_partial_category']), _type='cat_list')
            if col_name:  # 有東西
                col[col_name] += 2


    def do_CleanAge(self, df):
        """
            執行計算
        :param df:
        :return:
        """

        # step-1 計分條件 - citys_data
        for a, b in df['city'].apply(lambda x: self.citys_data_scores(x, y=0, _type='tags')).to_dict().items():
            df.loc[a, b] += 1

        # step-2 計分條件 - ages_data
        for a, b in df['age_level'].apply(lambda x: self.ages_data_scores(x, y=0, _type='tags')).to_dict().items():
            df.loc[a, b] += 1

        # step-3 age_level vs max_partial_category
        self.cal_age_cat_values(df=df)

        # step-4 citys vs max_partial_category
        self.cal_city_cat_values(df=df)

        # 找出每一 user 最大的收入分布
        df['income_level'] = df[['35萬以下', '35萬-50萬', '50萬-75萬', '75萬-100萬', '100萬以上']].idxmax(axis=1)

    def clean_col(self, df):
        df.rename(columns={"carrier_number": "carrier_id"}, inplace=True)  # 重命名
        df['cat_id'] = df['cat_id'].fillna(0).astype('int32')
        df = df[~(df['cat_id'] == 0)]  # 去除 cad_id = 0 的 row data

        # 消費量計算
        df['total_buy'] = df['unit_price'] * df['quantity']

        # 統計各 carrier_id，花費在各 category 的消費額。
        invoice_pivot = df.pivot_table(index='carrier_id',
                                       columns='cat_id',
                                       values='total_buy',
                                       margins=True,  # row
                                       margins_name='total_comsump',  # 列
                                       fill_value=0,
                                       aggfunc='sum')
        # 清除最後一行(清理用)
        invoice_pivot = invoice_pivot[:-1]

        # 該用戶 => 該類別消費額佔所有該類別總消費額的比例
        invoice_pivot = self.__cal_ucctp_value(df=invoice_pivot)

        # 該用戶 => 該類別消費額佔所有該用戶總消費額的比例
        invoice_pivot = self.__cal_ucutp_value(df=invoice_pivot)

        # 把不要用的，欄位先刪除，單純看占比(清理用)
        drop_col = [i + 1 for i in range(15)]
        invoice_pivot.drop(columns=drop_col, inplace=True)

        # 最後再轉回成 一般 DataFrame 型態
        invoice_pivot = pd.DataFrame(invoice_pivot.to_records())

        # 合併
        invoice_pivot = pd.merge(invoice_pivot, res_df, how='outer')
        invoice_pivot.drop(columns=['pname'], inplace=True)  # ????????????????????????????????????????????????????

        # 找出對每個 user 來說，類別消費占整體類別最高的
        invoice_pivot = self.__ucctp_max_category(df=invoice_pivot)

        # 找出對每個 user 來說，自己消費最高的類別
        invoice_pivot = self.__ucutp_max_category(df=invoice_pivot)

        # 只找出需要的欄位
        cols_need = ['carrier_id', 'gender', 'total_comsump', 'city', 'age_level', 'max_comsump_category',
                     'max_partial_category']
        invoice_pivot = invoice_pivot[cols_need]

        # 建構計算分表
        self.__get_scoredf(df=invoice_pivot)

        return invoice_pivot