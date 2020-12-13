import pandas as pd
import numpy as np

class LifeModel:
    def __init__(self):
        self.life_status_index = ['最小值', '20%分位數', '40%分位數', '60%分位數', '80%分位數', '最大值']

    def life_status(self, x):
        return pd.Series([x.min(), x.quantile(.20), x.quantile(.40), x.quantile(.60), x.quantile(.80), x.max()],
                         index=self.life_status_index)
    def clean_data(self,df):
        # 轉換成標準 datatime 時間
        df["invoice_date"] = pd.to_datetime(df["invoice_date"])
        df["consumption"] = df["unit_price"] * df["quantity"]
        df['month'] = df.invoice_date.values.astype('datetime64[M]')
        example_pivot = df.pivot_table(index='carrier_number', columns='month', values='consumption', fill_value=0,
                                       aggfunc='mean')
        # 按行求和
        example_pivot['SUM'] = example_pivot.apply(lambda x: x.sum(), axis=1)

        res_df = example_pivot.apply(self.life_status)
        res_df["SUM"] = res_df["SUM"].astype('int64')
        return res_df

    def output_result(self,df):
        res_list = []
        for i in range(len(df)):
            _dict = {}
            if i + 1 < len(df):
                _dict["id"] = i + 1
                _dict["value"] = str(int(df.iloc[i]['SUM'])) + "~" + str(int(df.iloc[i + 1]['SUM']))

                res_list.append(_dict)
        return res_list

    def get_comsume_value(self,range_id,obj):
        """

        :param range_id: comsume_level 表的 comsume_id
        :param obj: comsume_level 表的 value 轉成物件
        :return:
        """
        for item in obj:
            if item['comsume_id'] == str(range_id):
                return item['comsume_value']

    def getQuery_v1(self):
        return "select * from invoice where vender_id=2;"

    def get_quantile(self, df, type):
        res = []
        if type == 'OneConsume':
            _range = [0.2, 0.4, 0.6, 0.8]
            for i in range(len(_range)):
                res.append(df['consumption'].quantile(_range[i]))
            return res
        elif type == 'FuncDemand':
            _range = [20, 40, 60, 80]
            count_num = np.array(df['invoice_number'].value_counts().index)
            for i in range(len(_range)):
                res.append(int(np.percentile(count_num, _range[i])))
            return res

    def get_tag(self, x, df,type):
        res_list = self.get_quantile(df,type)
        if x < res_list[0]:
            return '1'
        elif res_list[0] <= x < res_list[1]:
            return "2"
        elif res_list[1] <= x < res_list[2]:
            return "3"
        elif res_list[2] <= x < res_list[3]:
            return "4"
        elif res_list[3] <= x:
            return "5"

    def __tag_dict(self, df, tag_col='_tag'):
        return df[tag_col].value_counts().sort_index().to_dict()

    def do_AvgMonth(self, df, comsume_val):
        """
            分群運算流程
        :param df:
        :param comsume_val: 每月平均 消費的 range list
        :return:
        """
        # step1 => 擷取自己需要的欄位部分
        invoice_df = df[["carrier_number", "invoice_number", "invoice_date", "unit_price", "quantity"]]
        # step2 => 增加消費量欄位
        invoice_df["consumption"] = invoice_df["unit_price"] * invoice_df["quantity"]
        # step3 => 轉換成標準 datatime 時間
        invoice_df["invoice_date"] = pd.to_datetime(invoice_df["invoice_date"])
        invoice_df['month'] = invoice_df["invoice_date"].values.astype('datetime64[M]')
        # step4 => 以user_id 分群 and 以發票 分群
        user_base_df = invoice_df.groupby('carrier_number').agg({'consumption': 'sum', 'invoice_number': 'nunique'})
        month_count = invoice_df['month'].nunique()
        # step5 => 總消費量/月份
        user_base_df['consumption'] = (user_base_df['consumption'] / month_count)  # 總消費量/月份
        user_base_df['consumption'] = user_base_df['consumption'].astype('int64')
        # step6 => 匹配range 區間值
        user_base_df = user_base_df.loc[
            user_base_df['consumption'].between(comsume_val[0], comsume_val[1]), ['consumption', 'invoice_number']]
        return user_base_df

    def do_FuncDemand(self,df):
        # step1 => 擷取自己需要的欄位部分
        invoice_df = df[["carrier_number", "invoice_number", "invoice_date", "unit_price", "quantity"]]
        # step2 => 增加消費量欄位
        invoice_df["consumption"] = invoice_df["unit_price"] * invoice_df["quantity"]
        # step3 => 轉換成標準 datatime 時間
        invoice_df["invoice_date"] = pd.to_datetime(invoice_df["invoice_date"])
        invoice_df['month'] = invoice_df["invoice_date"].values.astype('datetime64[M]')
        # step4 => 以user_id 分群 and 以發票 分群
        user_base_df = invoice_df.groupby('carrier_number').agg({'consumption': 'sum', 'invoice_number': 'nunique'})
        month_count = invoice_df['month'].nunique()
        # step5 => 總消費量
        user_base_df['consumption'] = user_base_df['consumption'].astype('int64')
        # step6 => 總消費量/月份 區間分群 新增tag
        user_base_df["_tag"] = user_base_df['invoice_number'].apply(self.get_tag, args=(user_base_df, 'FuncDemand'))
        user_base_df = user_base_df.sort_values('_tag', ascending=True)
        # step7 => tag 分群結果 總計
        _count_dict = self.__tag_dict(df=user_base_df, tag_col='_tag')
        return (user_base_df, _count_dict)

    def do_OneConsume(self,df):
        # step1 => 擷取自己需要的欄位部分
        invoice_df = df[["carrier_number", "invoice_number", "invoice_date", "unit_price", "quantity"]]
        # step2 => 增加消費量欄位
        invoice_df["consumption"] = invoice_df["unit_price"] * invoice_df["quantity"]
        # step3 => 轉換成標準 datatime 時間
        invoice_df["invoice_date"] = pd.to_datetime(invoice_df["invoice_date"])
        invoice_df['month'] = invoice_df["invoice_date"].values.astype('datetime64[M]')
        # step4 => 以user_id 分群 and 以發票 分群
        user_base_df = invoice_df.groupby('carrier_number').agg({'consumption': 'sum', 'invoice_number': 'nunique'})
        month_count = invoice_df['month'].nunique()
        # step5 => 總消費量/月份
        user_base_df['consumption'] = (user_base_df['consumption'] / month_count)  # 總消費量/月份
        user_base_df['consumption'] = user_base_df['consumption'].astype('int64')
        # step6 => 總消費量/月份 區間分群 新增tag
        user_base_df["_tag"] = user_base_df['consumption'].apply(self.get_tag, args=(user_base_df, 'OneConsume'))
        user_base_df = user_base_df.sort_values('_tag', ascending=True)
        # step7 => tag 分群結果 總計
        _count_dict =self.__tag_dict(df=user_base_df,tag_col='_tag')
        return (user_base_df,_count_dict)





class LifeOutput:
    @staticmethod
    def getAvgMonthOutput(df):
        item_dict = {}
        item_dict['ad_id'] = len(df.index)
        item_dict['user_num'] = len(df.index)
        item_dict['invoice_num'] = int(df['invoice_number'].sum())
        item_dict['amo_user'] = int(df['consumption'].sum() / item_dict['user_num'])
        item_dict['amo_user'] = '$' + format(item_dict['amo_user'], ",")
        item_dict['amo_invoice'] = int(df['consumption'].sum() / item_dict['invoice_num'])
        item_dict['amo_invoice'] = '$' + format(item_dict['amo_invoice'], ",")
        item_dict['status'] = True
        item_dict['message'] = "successful"
        return item_dict

    @staticmethod
    def trans_tag_OneConsume(k, consumption_range):
        """
            tag 區間轉換成文字表示
        :param k:
        :param consumption_range:
        :return:
        """
        if k == '1':
            return '$0 ~ $' + format(int(consumption_range[int(k) - 1]), ",")  #str(int(consumption_range[int(k) - 1]))
        elif k == '2':
            #return '$' + str(int(consumption_range[int(k) - 2])) + ' ~ $' + str(int(consumption_range[int(k) - 1]))
            return '$' + format(int(consumption_range[int(k) - 2]), ",") + ' ~ $' + format(int(consumption_range[int(k) - 1]), ",")
        elif k == '3':
            return '$' + format(int(consumption_range[int(k) - 2]), ",") + ' ~ $' + format(int(consumption_range[int(k) - 1]), ",")
        elif k == '4':
            return '$' + format(int(consumption_range[int(k) - 2]), ",") + ' ~ $' + format(int(consumption_range[int(k) - 1]), ",")
        elif k == '5':
            return '$' + format(int(consumption_range[int(k) - 2]), ",") + ' 以上'

    @staticmethod
    def trans_tag_FuncDemand(k, invoice_num_range):
        if len(set(invoice_num_range)) == 1:
            return "{}次".format(int(invoice_num_range[0]))
        else:
            if k == '1':
                return '0 ~ ' + str(int(invoice_num_range[int(k) - 1])) + '次'
            elif k == '2':
                return str(int(invoice_num_range[int(k) - 2])) + '次 ~ ' + str(int(invoice_num_range[int(k) - 1])) + '次'
            elif k == '3':
                return str(int(invoice_num_range[int(k) - 2])) + '次 ~ ' + str(int(invoice_num_range[int(k) - 1])) + '次'
            elif k == '4':
                return str(int(invoice_num_range[int(k) - 2])) + '次 ~ ' + str(int(invoice_num_range[int(k) - 1])) + '次'
            elif k == '5':
                return str(int(invoice_num_range[int(k) - 2])) + '次 以上'

    @staticmethod
    def getOneConsumeOutput(df, _count_dict, consumption_range):
        # 轉 dict output 格式
        data_res = []
        for k, v in _count_dict.items():
            item_dict = {}
            item_dict['category'] = LifeOutput.trans_tag_OneConsume(k, consumption_range)
            item_dict['ad_id'] = int(v)
            item_dict['user_num'] = int(v)
            item_dict['invoice_num'] = int(df.loc[df["_tag"] == k, 'invoice_number'].sum())
            item_dict['amo_user'] = int(df.loc[df["_tag"] == k, 'consumption'].sum() / v)
            item_dict['amo_user'] = '$' + format(item_dict['amo_user'], ",")
            item_dict['amo_invoice'] = int(
                df.loc[df["_tag"] == k, 'consumption'].sum() / df.loc[
                    df["_tag"] == k, 'invoice_number'].sum())
            item_dict['amo_invoice'] = '$' + format(item_dict['amo_invoice'], ",")

            data_res.append(item_dict)
        return data_res

    @staticmethod
    def getFuncDemandOutput(df, _count_dict, invoice_num_range):
        data_res = []
        for k, v in _count_dict.items():
            item_dict = {}
            item_dict['category'] = LifeOutput.trans_tag_FuncDemand(k, invoice_num_range)
            item_dict['ad_id'] = int(v)
            item_dict['user_num'] = int(v)
            item_dict['invoice_num'] = int(df.loc[df["_tag"] == k, 'invoice_number'].sum())
            item_dict['amo_user'] = int(df.loc[df["_tag"] == k, 'consumption'].sum() / item_dict['user_num'])
            item_dict['amo_user'] = '$' + format(item_dict['amo_user'], ",")
            item_dict['amo_invoice'] = int(df.loc[df["_tag"] == k, 'consumption'].sum() / item_dict['invoice_num'])
            item_dict['amo_invoice'] = '$' + format(item_dict['amo_invoice'], ",")
            data_res.append(item_dict)
        return data_res