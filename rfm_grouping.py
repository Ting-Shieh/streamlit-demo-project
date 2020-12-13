
import pandas as pd
import datetime
import time
from datetime import datetime


def get_feauture_result(k_name,target_list):
    for item in target_list:
        if item['group_name'] == k_name:
            return item['result']


class RFM_Model:
    def __init__(self, recency_label=None, frequency_label=None, monetary_label=None, recency_label_scores=None,
                 frequency_label_scores=None, monetary_label_scores=None):
        """
            label 一律由低到高
        """
        self.recency_label = ['0~30', '30~60', '60~90', '90~120', '120 up']
        self.frequency_label = ['<1 times', '2 times', '3 times', '4 times', '>=5 times']
        self.monetary_label = ['50 down', '50~100', '100~150', '150~200', '200 up']
        self.recency_label_scores = [5, 4, 3, 2, 1]
        self.frequency_label_scores = [1, 2, 3, 4, 5]
        self.monetary_label_scores = [1, 2, 3, 4, 5]
        self.__client_label = [0, 1, 10, 11, 100, 101, 110, 111]
        self.__client_label_meanings = ['流失客戶', '高消費喚回客戶', '一般客戶', '重要價值流失預警客戶', '新客戶', '消費頻繁客戶', '消費潛力客戶', '重要價值客戶']
        self.__client_label_meanings_dict = dict(zip(self.__client_label, self.__client_label_meanings))
        self.__recency_dict = dict(zip(self.recency_label, self.recency_label_scores))  # 最後要私有化
        self.__frequency_dict = dict(zip(self.frequency_label, self.frequency_label_scores))  # 最後要私有化
        self.__monetary_dict = dict(zip(self.monetary_label, self.monetary_label_scores))  # 最後要私有化

    def get_client_label(self, label_name):
        """
        原本是 k:v = 0:"流失客戶"
        :param label_name:
        :return:
        """
        return [k for k, v in self.__client_label_meanings_dict.items() if v == label_name]

    def __recency_identify(self, col_val):

        if 0 <= col_val < 30:
            return self.recency_label[0]
        elif 30 <= col_val < 60:
            return self.recency_label[1]
        elif 60 <= col_val < 90:
            return self.recency_label[2]
        elif 90 <= col_val < 120:
            return self.recency_label[3]
        else:
            return self.recency_label[4]

    def __frequency_identify(self, col_val):

        if col_val <= 1:
            return '<1 times'
        elif col_val == 2:
            return '2 times'
        elif col_val == 3:
            return '3 times'
        elif col_val == 4:
            return '4 times'
        elif col_val >= 5:
            return '>=5 times'

    def __monetary_identify(self, col_val):

        if 0 <= col_val < 50:
            return self.monetary_label[0]
        elif 50 <= col_val < 100:
            return self.monetary_label[1]
        elif 100 <= col_val < 150:
            return self.monetary_label[2]
        elif 150 <= col_val < 200:
            return self.monetary_label[3]
        elif col_val >= 200:
            return self.monetary_label[4]

    # step 1    
    def uniform_rfm_format(self, original_df):
        """
        original_df: 原始df數據
        datetime_col:日期欄位名

        #         kw[0],     kw[1],           kw[2],         kw[3],       kw[4]
        """
        kw = ('carrier_number', 'invoice_number', 'invoice_date', 'unit_price', 'quantity')
        # 日期轉換
        original_df[kw[2]] = pd.to_datetime(original_df[kw[2]])
        # print(original_df.head())
        # 查看數據最後一日為多少
        last_day = original_df[kw[2]].tail(1)

        # 最後一日之隔日
        Now = pd.Timestamp(last_day.values[0]) + pd.DateOffset(days=1)  # Timestamp 型態
        Now = Now.to_pydatetime()  # datetime 型態
        # 收益計算
        original_df['Revenue'] = original_df[kw[3]] * original_df[kw[4]]

        # encrypt
        rfm_df = original_df.groupby(kw[0]).agg({
            kw[2]: lambda x: (Now - x.max()).days,  # 近一次消費天
            kw[1]: lambda x: x.nunique(),  # 消費次數
            'Revenue': lambda x: x.sum()  # 消費金額
        }).reset_index()

        # 重新命名
        rfm_df.rename(
            columns={'invoice_date': 'recency',
                     'invoice_number': 'frequency',
                     'Revenue': 'monetary'},
            inplace=True
        )

        # 繪圖計數用
        rfm_df['user'] = 1

        return rfm_df

    # step 2 
    def rfm_graded2group(self, rfm_df):
        """
            分級(先分組)
        """
        rfm_df['recency_label'] = rfm_df['recency'].apply(
            lambda x: self.get_rfm_levels(x, type='r')
        )

        rfm_df['frequency_label'] = rfm_df['frequency'].apply(
            lambda x: self.get_rfm_levels(x, type='f')
        )

        rfm_df['monetary_label'] = rfm_df['monetary'].apply(
            lambda x: self.get_rfm_levels(x, type='m')
        )

        return rfm_df

    # step 3
    def rfm_group2scores(self, rfm_df):
        """
            分級(在打分)
        """

        rfm_df['recency_label_score'] = rfm_df['recency_label'].apply(
            lambda x: self.get_rfm_scores(col_val=x, type='r')
        )

        rfm_df['frequency_label_score'] = rfm_df['frequency_label'].apply(
            lambda x: self.get_rfm_scores(col_val=x, type='f')
        )

        rfm_df['monetary_label_score'] = rfm_df['monetary_label'].apply(
            lambda x: self.get_rfm_scores(col_val=x, type='m')
        )

        return rfm_df

    # step 4
    def is_rfm_label_score_mean(self, rfm_df):
        """
            通過判斷每個客戶的 R、F、M 值是否大於平均值，來簡化分類結果。
            只有 0 和 1 （0 表示小於平均值，1 表示大於平均值）兩種結果。
            整體組合下來共有 8 個分組，是比較合理的一個情況。我們來判斷用戶的每個分值是否大於平均值。         
        """
        rfm_df['R 是否大於平均值'] = (rfm_df['recency_label_score'] > rfm_df['recency_label_score'].mean()) * 1
        rfm_df['F 是否大於平均值'] = (rfm_df['frequency_label_score'] > rfm_df['frequency_label_score'].mean()) * 1
        rfm_df['M 是否大於平均值'] = (rfm_df['monetary_label_score'] > rfm_df['monetary_label_score'].mean()) * 1
        return rfm_df

    # step 5    
    def get_rfm_8_client_type(self, rfm_df):
        """
            用戶劃分爲 8 類
        """
        rfm_df['client_type_id'] = (rfm_df['R 是否大於平均值'] * 100 + rfm_df['F 是否大於平均值'] * 10 + rfm_df['M 是否大於平均值'] * 1)
        rfm_df['client_type'] = rfm_df['client_type_id'].apply(
            lambda x: self.transform_label(col_val=x)
        )
        return rfm_df

    def check_client_percentage(self, rfm_df):
        """
            查看各類用戶佔比情況
        """
        client_percentage_count_df = rfm_df['client_type'].value_counts().reset_index()
        client_percentage_count_df.columns = ['客戶類型', '人數']
        client_percentage_count_df['人數占比'] = client_percentage_count_df['人數'] / client_percentage_count_df['人數'].sum()
        return client_percentage_count_df

    def check_client_CCP(self, rfm_df):
        """
            CCP = consumption_contribution_percentage
            不同類型客戶消費金額貢獻佔比
        """
        rfm_df['購買總金額'] = rfm_df['frequency'] * rfm_df['monetary']
        contribution_df = rfm_df.groupby('client_type')['購買總金額'].sum().reset_index()
        contribution_df.columns = ['客戶類型', '消費金額']
        contribution_df['金額占比'] = contribution_df['消費金額'] / contribution_df['消費金額'].sum()
        return contribution_df


    def get_target_client_id_list(self, rfm_df, uid_col, c_type):
        """
            篩選出特定客戶分類的 user_id list。
            rfm_df: 轉化為 df 的rmf數據。
            c_type: 目標客戶群名稱(初版先用字符串型態)。
        """
        if c_type is None or c_type not in self.__client_label_meanings:
            return
        target_df = rfm_df[rfm_df['client_type'] == c_type]
        return target_df[uid_col].tolist()

    def get_uid_dataframe(self, original_df, rfm_df, uid_col, c_type):
        """
            由user_id list篩選出特定客戶的dataframe。      
            original_df: 最初撈出數據。
            uid_col: User_id 所在的 columns name。
        """
        if c_type is None or c_type not in self.__client_label_meanings:
            return
        target_id_list = self.get_target_client_id_list(rfm_df, uid_col, c_type)
        return original_df[original_df[uid_col].isin(target_id_list)]

    def get_rfm_levels(self, col_val, type=None):
        """
            根據值將資料分級
        """
        if type == 'r':
            return self.__recency_identify(col_val)
        elif type == 'f':
            return self.__frequency_identify(col_val)
        elif type == 'm':
            return self.__monetary_identify(col_val)

    def get_rfm_scores(self, col_val, type=''):
        """
            分級 分數化
        """
        if type == 'r':
            return self.__recency_dict[col_val]
        elif type == 'f':
            return self.__frequency_dict[col_val]
        elif type == 'm':
            return self.__monetary_dict[col_val]

    def transform_label(self, col_val):
        if int(col_val) in self.__client_label_meanings_dict.keys():  # 判斷是否在key中
            return self.__client_label_meanings_dict[col_val]
        else:
            return

    def uni_rfm_result(self, rfm_df):
        """

        :param rfm_df:
        :param _sn: transaction_sn
        :return:
        """
        group_name_list = []
        group_id_list = []
        r_scores_list = []
        f_scores_list = []
        m_scores_list = []
        users_list = []
        for item in rfm_df["client_type"].unique().tolist():

            group_name_list.append(item)
            r_scores_list.append(rfm_df.loc[rfm_df["client_type"] == item, "recency_label_score"].values.tolist())
            f_scores_list.append(rfm_df.loc[rfm_df["client_type"] == item, "frequency_label_score"].values.tolist())
            m_scores_list.append(rfm_df.loc[rfm_df["client_type"] == item, "monetary_label_score"].values.tolist())
            temp_list = rfm_df.loc[rfm_df["client_type"] == item, "carrier_number"].values.tolist()
            ",".join(temp_list)
            users_list.append("[" + ",".join(temp_list) + "]")


        resdf = pd.DataFrame({
            "group_name": group_name_list,
            "r_scores": r_scores_list,
            "f_scores": f_scores_list,
            "m_scores": m_scores_list,
            "users": users_list
        })
        resdf["group_id"] = resdf['group_name'].apply(
            lambda x: self.get_client_label(label_name=x)
        )
        return resdf

