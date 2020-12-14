# -*- coding: utf-8 -*
import math as mt
import numpy as np
import pandas as pd
from sqlalchemy import create_engine

from scipy.sparse.linalg import *
from scipy.sparse.linalg import svds
from scipy.sparse import csc_matrix
from scipy.sparse import coo_matrix



# 測試效率代碼
import time
def timeit_wrapper(func):
    def wrapper(*args,**kwargs):
        start = time.perf_counter() #time.process_time()
        func_return_val =func(*args,**kwargs)
        end = time.perf_counter()
        print('{0:<10}.{1:<8} : {2:<8}'.format(func.__module__, func.__name__, end - start))
        return func_return_val
    return wrapper


def handle_group_dict(group_dict):
    for item in group_dict:
        group_dict[item] = group_dict[item].replace('[', '').replace(']', '').split(',')
    return group_dict

class MysqlHelper:
    def __init__(self, host="invoice-power.api.case5888.com", user="username", pwd="new-password", database="invoice_db",develop=True):
        self.host =  host if develop else "127.0.0.1"
        self.user = user
        self.passwd = pwd
        self.port = 3306
        self.database = database

    def __get_mycursor(self):
        return self.__mydb.cursor()

    def __use_sqlalchemy_connect(self):
        """
        用 sqlalchemy 建構數據庫連接engine
        """
        connect_info = 'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8'.format(self.user, self.passwd, self.host, self.port, self.database)
        return create_engine(connect_info)


    def mysql2df(self,sql):
        engine = self.__use_sqlalchemy_connect()
        return pd.read_sql_query(sql, engine)

class RFM_Group_Recommand_Model:
    def __init__(self, cat_df, model_type, column_name):
        """
            cat_df: 資料庫撈出的資料
            model_type: 是 brand or  cat
            columns name: 是 brand_id or cat_id
        """
        self.__cat_df = cat_df  # 品牌同購時這邊要改。
        self.column_name = column_name
        self.retain_columns = ['carrier_number', 'quantity', 'brand_id', 'cat_id', ]  # 保留 columns 做建模 feature

        self.rfm_group_dict = {}  # 針對 客戶群統計數量 字典化
        self.__model_type_str = model_type
        self.__g_df = self.__fix_column_name(column_name) #pd.DataFrame(columns=['group_id', column_name, "each_" + self.__model_type_str + "_total_counts"])
        self.__merge_df = None
        self.__small_set = None
        self._svd_max_k = None
        self.__reset_rfm_id_group_dict = {}  # 針對 重建客戶群 id 保存

    def __fix_column_name(self,column_name):
        if self.__model_type_str == 'cat':
            return pd.DataFrame(columns=['group_id', column_name, "each_cat_total_counts"])
        if self.__model_type_str == 'brand':
            return pd.DataFrame(columns=['group_id', column_name, "each_brand_total_counts"])
    def statistic_list2dataframe(self, s_list):
        """
            目標column所有統計數量 list 轉 dataframe
            返回: dataframe
        """
        id_list_df = pd.DataFrame(s_list)
        id_list_df = id_list_df.sort_values(by='num_counts', ascending=False)
        return id_list_df

    def __del_unused_col(self, target_df):
        """
            刪除不必要的欄位。
        """
        # for col in target_df.columns:
        #     if col not in self.retain_columns:
        #         del (target_df[col])
        target_df.drop(columns=[x for x in list(target_df.columns) if x not in self.retain_columns], inplace=True)

    def __handle_data(self, target_df):
        """
            整理數據，刪除DataFrame空值，會直接刪除整欄和整列
            t_col: 目標欄位
        """
        # target_df.dropna(axis=0, inplace=True)

        # astype實現dataframe欄位型別轉換
        target_df[self.column_name] = target_df[self.column_name].astype('int32')

    # @timeit_wrapper
    def get_group_list_statistic(self, target_df):
        """
            得到 目標column 去重後所有統計數量
            返回: list
        """
        # self.__del_unused_col(target_df)  # 自動刪除不必要的欄位。
        # self.__handle_data(target_df)  # 自動刪除DataFrame空值。

        # # 自動刪除不必要的欄位。
        # target_df.drop(columns=[x for x in list(target_df.columns) if x not in self.retain_columns], inplace=True)
        # # # 自動刪除DataFrame空值。
        # target_df.dropna(axis=0, inplace=True)

        output_dict = {}
        num_counts = 0
        for index, row in target_df.iterrows():
            if row[self.column_name] in output_dict.keys():
                # num_counts = output_dict[row[self.column_name]] + 1
                output_dict[row[self.column_name]] = output_dict[row[self.column_name]] + 1
            else:
                output_dict[row[self.column_name]] = num_counts + 1

        return [{self.column_name: k, 'num_counts': v} for k, v in output_dict.items()]

    # @timeit_wrapper
    def get_uid_dataframe_from_db(self, tg_df, target_id_list, uid_col='carrier_number'):
        """
            tg_df: 全部data轉成 dataframe的數據
            group_dict: 目標客戶群字典{"":['','',''...]}
            uid_col: 目標特徵(user_id 欄位)
        """

        tg_df = tg_df[tg_df[uid_col].isin(target_id_list)]
        # 自動刪除不必要的欄位。
        tg_df.drop(columns=[x for x in list(tg_df.columns) if x not in self.retain_columns], inplace=True)

        # 自動刪除DataFrame空值。
        tg_df.dropna(axis=0, inplace=True)
        return tg_df

    # @timeit_wrapper
    def get_request_group(self, df, g_dict, uid_col):
        """
            返回: {'新客戶': [{'cat_id': 5, 'num_counts': 33}]}
            g_dict: {group type:[uid,...]}
            uid_col: 目標特徵(user_id 欄位)
            column_name: 品牌同購還是品項同購(brand_id or cat_id)
        """
        g_dict_keys_list = list(g_dict.keys())
        for i in range(len(g_dict_keys_list)):
            t_df = self.get_uid_dataframe_from_db(df, g_dict[g_dict_keys_list[i]], uid_col=uid_col)
            self.rfm_group_dict[g_dict_keys_list[i]] = self.get_group_list_statistic(t_df)
        return self.rfm_group_dict

    # @timeit_wrapper
    # def get_request_group2(self, df, g_dict, uid_col):
    #     """
    #         返回: {'新客戶': [{'cat_id': 5, 'num_counts': 33}]}
    #         g_dict: {group type:[uid,...]}
    #         uid_col: 目標特徵(user_id 欄位)
    #         column_name: 品牌同購還是品項同購(brand_id or cat_id)
    #     """
    #     g_dict_keys_list = list(g_dict.keys())
    #     for i in range(len(g_dict_keys_list)):
    #         # t_df = self.get_uid_dataframe_from_db(df, g_dict[g_dict_keys_list[i]], uid_col=uid_col)
    #         df[df[uid_col].isin(g_dict[g_dict_keys_list[i]])]
    #         # 自動刪除不必要的欄位。
    #         df.drop(columns=[x for x in list(df.columns) if x not in self.retain_columns], inplace=True)
    #         # 自動刪除DataFrame空值。
    #         df.dropna(axis=0, inplace=True)
    #
    #         # self.rfm_group_dict[g_dict_keys_list[i]] = self.get_group_list_statistic(df)
    #         output_dict = {}
    #         num_counts = 0
    #         for index, row in df.iterrows():
    #             if row[self.column_name] in output_dict.keys():
    #                 num_counts = output_dict[row[self.column_name]] + 1
    #                 output_dict[row[self.column_name]] = num_counts
    #             output_dict[row[self.column_name]] = num_counts + 1
    #
    #         self.rfm_group_dict[g_dict_keys_list[i]] = [{self.column_name: k, 'num_counts': v} for k, v in output_dict.items()]
    #
    #     return self.rfm_group_dict


    def calculation_fractional(self):
        """
            column_name: 品牌同購還是品項同購(brand_id or cat_id)
        """
        if self.__model_type_str is None:
            return

        # 步驟 1-1
        for key, value in self.rfm_group_dict.items():
            for item_dict in self.rfm_group_dict[key]:
                row_list = [key, item_dict[self.column_name], item_dict['num_counts']]

                self.__g_df.loc[len(self.__g_df)] = row_list

        # 步驟 1-2
        for item in self.__g_df["group_id"].unique().tolist():
            res = self.__g_df.loc[self.__g_df["group_id"] == item, ("each_" + self.__model_type_str + "_total_counts")].sum()
            self.__g_df.loc[self.__g_df["group_id"] == item, "group_total_counts"] = res

        # 步驟 1-3
        for item in self.__g_df["group_id"].unique().tolist():
            res = self.__g_df.loc[self.__g_df["group_id"] == item, self.column_name].count()
            self.__g_df.loc[self.__g_df["group_id"] == item, ("each_group_" + self.__model_type_str + "_counts")] = res

        self.__g_df["group_total_counts"] = self.__g_df["group_total_counts"].astype('int')
        self.__g_df["each_group_" + self.__model_type_str + "_counts"] = self.__g_df["each_group_" + self.__model_type_str + "_counts"].astype('int')

        # 計算比率
        self.__g_df["fractional_" + self.__model_type_str + "_count"] = self.__g_df["each_" + self.__model_type_str + "_total_counts"]/self.__g_df["group_total_counts"]

        group_codes = self.__g_df['group_id'].drop_duplicates().reset_index()
        column_name_codes = self.__g_df[self.column_name].drop_duplicates().reset_index()

        # 重命名
        group_codes.rename(columns={'index': 'group_id_index'}, inplace=True)
        column_name_codes.rename(columns={'index': self.column_name + '_index'}, inplace=True)
        # 單獨取出 去重的 id list
        column_name_codes[self.column_name + '_index_value'] = list(column_name_codes.index)
        group_codes['group_index_value'] = list(group_codes.index)


        # # 第一次 merge
        # self.__small_set = pd.merge(self.__g_df, column_name_codes, how='left')
        self.__small_set = pd.merge(self.__g_df, column_name_codes, how='left')
        # 第二次 merge
        self.__small_set = pd.merge(self.__small_set, group_codes, how='left')

        #                                         重建的客戶群 id                      分群中文名
        self.__reset_rfm_id_group_dict = dict(zip(group_codes['group_index_value'], group_codes['group_id']))
        #                                         重建的目標 id                                  真實  目標id (之後用於回推資料庫中文)
        self.__reset_column_name_dict = dict(
            zip(column_name_codes[self.column_name + '_index_value'], column_name_codes[self.column_name]))

        return self.__small_set[['group_index_value', self.column_name + '_index_value', 'fractional_cat_count']]

    def construct_matrix(self, df):
        data_array = df['fractional_' + self.__model_type_str + '_count'].values
        row_array = df['group_index_value'].values
        col_array = df[self.column_name + '_index_value'].values
        # 建立矩陣
        data_sparse = coo_matrix((data_array, (row_array, col_array)), dtype=float)
        self._svd_max_k = data_sparse.shape[0]
        return data_sparse

    def compute_svd(self, urm, subtract_K=1):
        K = self._svd_max_k - subtract_K
        U, s, Vt = svds(urm, K)

        dim = (len(s), len(s))
        S = np.zeros(dim, dtype=np.float16)
        for i in range(0, len(s)):
            S[i, i] = mt.sqrt(s[i])

        U = csc_matrix(U, dtype=np.float16)
        S = csc_matrix(S, dtype=np.float16)
        Vt = csc_matrix(Vt, dtype=np.float16)

        return U, S, Vt

    def compute_estimated_matrix(self, urm, U, S, Vt, uTest, max_recommendation_num, subtract_K=1):
        K = self._svd_max_k - subtract_K
        MAX_CID = urm.shape[1]
        MAX_UID = urm.shape[0]
        rightTerm = S * Vt
        max_recommendation = max_recommendation_num  # 最大推薦類別
        estimatedRatings = np.zeros(shape=(MAX_UID, MAX_CID), dtype=np.float16)
        if estimatedRatings.shape[1]<max_recommendation_num:
            max_recommendation = estimatedRatings.shape[1]
        # print("estimatedRatings",estimatedRatings.shape)
        recomendRatings = np.zeros(shape=(MAX_UID, max_recommendation), dtype=np.float16)
        # print("recomendRatings",recomendRatings.shape)
        for userTest in uTest:
            prod = U[userTest, :] * rightTerm
            estimatedRatings[userTest, :] = prod.todense()
            recomendRatings[userTest, :] = (-estimatedRatings[userTest, :]).argsort()[:max_recommendation]
        return recomendRatings

    def get_recommand(self, df, uTest, subtract_K=1):
        """
        K=14  # 自己来衡量一下
        """
        K = self._svd_max_k - subtract_K
        urm = self.construct_matrix(df)
        U, S, Vt = self.compute_svd(urm, K)
        uTest_recommended_items = self.compute_estimated_matrix(urm, U, S, Vt, uTest, K, True)
        self.print_recommand(uTest, uTest_recommended_items)

    def __mapping_reset_group_id(self, reset_g_id):
        """
        """
        return self.__reset_rfm_id_group_dict[reset_g_id]

    def __get_target_dict(self):
        """
        """
        return dict(zip(self.__cat_df[self.column_name], self.__cat_df[self.__model_type_str + '_name']))

    def get_recommand_result_dict(self, uTest, uTest_recommended_items, r_num):
        final_feature_buy_list = []

        for user in uTest:
            result_list = []
            feature_buy_dict = {}
            feature_buy_dict['group_name'] = self.__mapping_reset_group_id(user)
            for i in uTest_recommended_items[user, 0:r_num]:
                model_type_details = \
                self.__small_set[self.__small_set[self.column_name + '_index_value'] == i].drop_duplicates(
                    self.column_name + '_index_value')[[self.column_name]]

                columns_name_id_list = list(model_type_details[self.column_name])[0]
                result_list.append(self.__get_target_dict()[columns_name_id_list])
            feature_buy_dict['result'] = result_list
            final_feature_buy_list.append(feature_buy_dict)
        return final_feature_buy_list


class ModelOutPut:

    def __init__(self, g_id_dict, t_id_dict, top_num=10):
        self.g_id_dict = g_id_dict
        self.t_id_dict = t_id_dict
        self.top_num = top_num
        self.ouptut = dict()

    def __cat_map(self, x):
        return self.t_id_dict[x]

    def handle_used_buy(self, request_group_dict):

        result_list = []

        for item in request_group_dict:
            temp_dict = {}
            df = pd.DataFrame(columns=['cat_id', 'num_counts'])
            for i in range(len(request_group_dict[item])):
                df = df.append(request_group_dict[item][i], ignore_index=True)
            df = df.sort_values(by='num_counts', ascending=False)
            temp_dict["group_id"] = self.g_id_dict[item]
            temp_dict["group_name"] = item
            temp_dict["result"] = list(map(self.__cat_map, df['cat_id'].values.tolist()))[:self.top_num]
            result_list.append(temp_dict)
        return result_list

    def handle_feature_buy(self, recommand_list):
        for item_dicts in recommand_list:
            item_dicts['group_id'] = self.g_id_dict[item_dicts['group_name']]

        return recommand_list

    def output(self, request_group_dict, recommand_list):

        self.ouptut["used_buy"] = self.handle_used_buy(request_group_dict)
        self.ouptut["feature_buy"] = self.handle_feature_buy(recommand_list)
        if len(self.ouptut["used_buy"]) == len(self.ouptut["feature_buy"]):
            self.ouptut["status"] = True
            self.ouptut["message"] = "successful"
            return self.ouptut
        else:
            return {"status": False, "message": "error"}