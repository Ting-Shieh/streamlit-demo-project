import datetime
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
# my package
from rfm_grouping import RFM_Model
from rfm_recommand import handle_group_dict, RFM_Group_Recommand_Model, ModelOutPut
from templates.template_var import card_temp,imageListShow
matplotlib.use('Agg')
import streamlit.components.v1 as components

# 全域變數
selected_cat_list=None
getwordListStr=None
date_from=None
date_to=None

class DataFrameHelper:
    def __init__(self):
        pass

    def get_cat_group(self,group_df,cat_df):
        t_id_dict = dict(zip(cat_df['cat_id'], cat_df['cat_name']))
        g_id_dict = dict(zip(group_df['group_name'], group_df['group_id']))
        return (g_id_dict,t_id_dict)

@st.cache
def getInitDataFrame():
    usecolumns = ['user_id', 'invoice_number', 'invoice_date',
                  'invoice_time', 'unit_price', 'product_name', 'brand_id', 'cat_id',
                  'amount', 'quantity', 'row_num', 'is_discount', 'is_point', 'store_name',
                  'store_address', 'lat', 'lng', 'carrier_number']
    init_invoice_df = pd.read_csv('./data/new_invoice.csv', low_memory=False)
    init_invoice_df = init_invoice_df[usecolumns]
    init_invoice_df['invoice_date'] = pd.to_datetime(init_invoice_df['invoice_date'], format='%Y/%m/%d')


    return init_invoice_df
@st.cache
def getCategoryDataFrame():
    cat_df = pd.read_csv('./data/category.csv',index_col=0, low_memory=False)
    return cat_df


def getRFMDataFrame(invoice_df):
    # TODO 删除/某行含有特定数值的列
    invoice_df = invoice_df[invoice_df['is_discount'] != 1]
    invoice_df = invoice_df[invoice_df['is_point'] != 1]

    # ----
    rfm_model = RFM_Model()
    try:
        # step1
        rfm_df = rfm_model.uniform_rfm_format(invoice_df)
        # step2
        rfm_df = rfm_model.rfm_graded2group(rfm_df)
        # step3
        rfm_df = rfm_model.rfm_group2scores(rfm_df)
        # step4
        rfm_df = rfm_model.is_rfm_label_score_mean(rfm_df)
        # step5
        rfm_df = rfm_model.get_rfm_8_client_type(rfm_df)
        # strp6
        resdf = rfm_model.uni_rfm_result(rfm_df)  # Ans
    except Exception as ec:
        print('main: ' + str(ec))


    try:
        # ----------------------------- 推薦部分 --------------------------------- #
        df_helper = DataFrameHelper()
        invoice_df = getInitDataFrame()
        cat_df = getCategoryDataFrame()
        group_df = resdf[['group_name', 'group_id']]
        group_dict = handle_group_dict(dict(zip(resdf['group_name'], resdf['users'])))
        rfm_group_recommand_model = RFM_Group_Recommand_Model(cat_df, 'cat', 'cat_id')

        a_test = rfm_group_recommand_model.get_request_group(df=invoice_df, g_dict=group_dict, uid_col="carrier_number")

        if a_test != None:

            try:
                mat_candidate = rfm_group_recommand_model.calculation_fractional()
                urm = rfm_group_recommand_model.construct_matrix(mat_candidate)
                U, S, Vt = rfm_group_recommand_model.compute_svd(urm)
                uTest = [i for i in range(len(group_dict.keys()))]
                uTest_recommended_items = rfm_group_recommand_model.compute_estimated_matrix(urm, U, S, Vt, uTest,
                                                                                             max_recommendation_num=14,
                                                                                             subtract_K=1)
                recommand_list = rfm_group_recommand_model.get_recommand_result_dict(uTest, uTest_recommended_items, 10)
                g_id_dict, t_id_dict = df_helper.get_cat_group(group_df, cat_df)
                model = ModelOutPut(g_id_dict=g_id_dict, t_id_dict=t_id_dict, top_num=10)
                final_dict = model.output(a_test, recommand_list)  # Ans
            except Exception as e:
                print('main: ' + str(e))
            else:
                return resdf,final_dict
    except Exception as ec:
        print('main: ' + str(ec))

@st.cache
def getFilterDataFrame(init_invoice_df,cat_list,word_list_str):
    print(word_list_str)
    # date_from = datetime.date.fromisoformat(date_from)
    # date_to = datetime.date.fromisoformat(date_to)
    invoice_df = init_invoice_df.loc[init_invoice_df['cat_id'].isin(cat_list)]
    print(type(invoice_df['invoice_date'][0]))
    print(date_from)
    mask = (invoice_df['invoice_date'].dt.date >= date_from) & (invoice_df['invoice_date'].dt.date <= date_to)
    invoice_df = invoice_df.loc[mask]
    invoice_df = invoice_df.loc[invoice_df['product_name'].str.contains(word_list_str, regex=True)]
    resdf,final_dict = getRFMDataFrame(invoice_df)
    return invoice_df,resdf,final_dict

def showSideBar():
    """
    sidebar part
    """
    multiselectList = ["飲料沖泡", "麵食料理", "美食生鮮", "保健生機", "居家生活", "美容保養", "家電", "箱包服飾", "零食", "其他", "旅遊住宿", "3C", "菸酒",
                       "寵物專區", "生活休閒", ]
    catDict = dict(zip(multiselectList, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]))
    # 類別選擇
    global selected_cat_list
    cat_list = st.sidebar.multiselect('類別選擇', multiselectList)
    selected_cat_list = [catDict[i] for i in cat_list if i in catDict]
    # selected_cat_list = st.sidebar.multiselect('類別選擇', multiselectList)
    # 商品特性

    getword = st.sidebar.text_input('商品特性')
    separator = '|'
    getwordList = getword.split(',')
    global getwordListStr
    getwordListStr = separator.join(getwordList)  # 'w1|w2...'
    # 日期 (label, value=None, min_value=None, max_value=None, key=None)
    global date_from
    date_from = st.sidebar.date_input(label='From', value=datetime.date(2018, 2, 1), min_value=datetime.date(2018, 2, 1), max_value=datetime.date(2018, 8, 30))  # <class 'datetime.date'> # 2018-02-01 00:00:00

    global date_to
    date_to = st.sidebar.date_input(label='To', value=datetime.date(2018, 2, 1), min_value=datetime.date(2018, 2, 1), max_value=datetime.date(2018, 8, 30))  # 2018-08-30 00:00:00

    start_btn = st.sidebar.button('Start')
    if start_btn:
        return True



def main():
    init_invoice_df = getInitDataFrame()
    # TODO show sidebar
    start_btn= showSideBar()
    if start_btn:
        invoice_afterFilter_df,resdf,final_dict= getFilterDataFrame(init_invoice_df, selected_cat_list, getwordListStr)
        # TODO 主頁
        st.dataframe(invoice_afterFilter_df.head(25))
        st.dataframe(resdf.head(25))

        group_users_cal_dict = resdf.set_index(['group_name'])['users'].to_dict()
        st.write(group_users_cal_dict)
        st.text("此次查詢共{}筆".format(invoice_afterFilter_df.shape[0]))

        # st.subheader('曾經購買')
        # used_buy_items=final_dict['used_buy']
        # for item in used_buy_items:
        #     group_name = item['group_name']
        #     result = item['result']
        #     outputHtmlList = imageListShow(result)
        #     st.markdown(card_temp.format(group_name,
        #                                  outputHtmlList[0],
        #                                  outputHtmlList[1],
        #                                  outputHtmlList[2],
        #                                  outputHtmlList[3],
        #                                  outputHtmlList[4],
        #                                  outputHtmlList[5],
        #                                  outputHtmlList[6],
        #                                  outputHtmlList[7],
        #                                  outputHtmlList[8],
        #                                  outputHtmlList[9],
        #                                  ),
        #                 unsafe_allow_html=True)
            # st.write(result)
        # st.subheader('未來可能購買')
        # feature_buy_items=final_dict['feature_buy']
        # st.write(feature_buy_items)


        # TODO 分欄
        left_column, right_column = st.beta_columns(2)
        # Or even better, call Streamlit functions inside a "with" block:
        with left_column:
            left_column.header('曾經購買')
            used_buy_items = final_dict['used_buy']
            left_column.write(used_buy_items)
            for item in used_buy_items:

                group_name = item['group_name']
                result = item['result']
                outputHtmlList = imageListShow(result)
                print(type(group_users_cal_dict[group_name]))
                users_list = [n.strip() for n in group_users_cal_dict[group_name]]
                left_column.markdown(card_temp.format(group_name,
                                             len(users_list),
                                             outputHtmlList[0],
                                             outputHtmlList[1],
                                             outputHtmlList[2],
                                             outputHtmlList[3],
                                             outputHtmlList[4],
                                             outputHtmlList[5],
                                             outputHtmlList[6],
                                             outputHtmlList[7],
                                             outputHtmlList[8],
                                             outputHtmlList[9],
                                             ),
                            unsafe_allow_html=True)
            # left_column.button('Press me!')

        with right_column:
            right_column.header('未來可能購買')
            feature_buy_items=final_dict['feature_buy']
            for item in used_buy_items:
                group_name = item['group_name']
                result = item['result']
                outputHtmlList = imageListShow(result)
                right_column.markdown(card_temp.format(group_name,
                                             outputHtmlList[0],
                                             outputHtmlList[1],
                                             outputHtmlList[2],
                                             outputHtmlList[3],
                                             outputHtmlList[4],
                                             outputHtmlList[5],
                                             outputHtmlList[6],
                                             outputHtmlList[7],
                                             outputHtmlList[8],
                                             outputHtmlList[9],
                                             ),
                            unsafe_allow_html=True)

        # components.html(components_temp, height=600,)

if __name__ == '__main__':
    main()



