import json
import datetime
import matplotlib
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# my package
from rfm_grouping import RFM_Model
from rfm_recommand import handle_group_dict, RFM_Group_Recommand_Model, ModelOutPut
from templates.template_var import FrontEndTemplate, imageListShow, predictShow
from classifiy_name import ClassifierByName
import streamlit.components.v1 as components
matplotlib.use('Agg')

# 全域變數
selected_cat_list=None
getwordListStr=None
date_from=None
date_to=None
getproductword=None
btn_dic = {
    "btn_datashow": False,
    "btn_predict": False,
    "btn_rec": False,
}
catList = ["Drinks&Brewed Beverages", "Dish", "Fresh food", "Healthy & Organic", "Living Style", "Facial Treatment", "Home Appliances", "Luggage", "Snacks", "Others", "Tourist Accommodation", "3C", "Liquor & Tobacco",
                       "Pet Area", "Leisure Lifestyle", ]

class DataFrameHelper:
    def __init__(self):
        pass

    def get_cat_group(self,group_df,cat_df):
        t_id_dict = dict(zip(cat_df['cat_id'], cat_df['cat_name']))
        g_id_dict = dict(zip(group_df['group_name'], group_df['group_id']))
        return (g_id_dict,t_id_dict)

@st.cache
def getInitDataFrame():
    usecolumns = [ 'user_id', 'invoice_number', 'invoice_date',
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
    """
    執行推薦系統
    :param
    """
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
    invoice_df = init_invoice_df.loc[init_invoice_df['cat_id'].isin(cat_list)]
    mask = (invoice_df['invoice_date'].dt.date >= date_from) & (invoice_df['invoice_date'].dt.date <= date_to)
    invoice_df = invoice_df.loc[mask]
    invoice_df = invoice_df.loc[invoice_df['product_name'].str.contains(word_list_str, regex=True)]
    resdf,final_dict = getRFMDataFrame(invoice_df)
    return invoice_df,resdf,final_dict
@st.cache
def dfValueCount(df):
    global catList
    return df['cat_id'].apply(lambda x: catList[x-1])


def showSideBar():
    """
    sidebar part
    """
    frontendtemplate = FrontEndTemplate()
    multiselectList = ["飲料沖泡", "麵食料理", "美食生鮮", "保健生機", "居家生活", "美容保養", "家電", "箱包服飾", "零食", "其他", "旅遊住宿", "3C", "菸酒",
                       "寵物專區", "生活休閒", ]
    catDict = dict(zip(multiselectList, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]))
    st.sidebar.markdown(frontendtemplate.title_temp.format('選擇服務'), unsafe_allow_html=True)
    selected_service = st.sidebar.selectbox(
        label="",
    options=("資料情況", "類別預測",  "推薦系統")
    )
       
    if selected_service == "瀏覽資料":
        st.sidebar.markdown(frontendtemplate.title_temp.format('瀏覽資料'), unsafe_allow_html=True)
        if st.sidebar.button('Show Data'):
            global btn_dict
            btn_dic['btn_datashow']=True
            
    if selected_service == "類別預測":
        # TODO 類別預測
        st.sidebar.markdown(frontendtemplate.title_temp.format('類別預測'), unsafe_allow_html=True)
        global getproductword
        getproductword = st.sidebar.text_input('品項名稱')

        if st.sidebar.button('Run Predict'):
            global btn_dict
            btn_dic['btn_predict']=True

    if selected_service == "推薦系統":

        # TODO 推薦系統
        st.sidebar.markdown(frontendtemplate.title_temp.format('推薦系統'), unsafe_allow_html=True)
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
            global btn_dict
            btn_dic['btn_rec'] = True

@st.cache
def get_city_size(df):
    plot_catcity_cal = df.groupby(['cat_id', 'city'], as_index=False).size()
    # plot_one_df = plot_catcity_cal.loc[plot_catcity_cal['cat_id'] == num, ['city', 'size']]
    return plot_catcity_cal

def main():
    frontendtemplate = FrontEndTemplate()
    init_invoice_df = getInitDataFrame()
    plot_one_df = get_city_size(init_invoice_df)
    # TODO show sidebar
    showSideBar()
    
    
    if btn_dic['btn_datashow']:
        st.markdown(frontendtemplate.title_temp.format('Data 總攬'), unsafe_allow_html=True)
        st.dataframe(init_invoice_df[
                         ['invoice_number', 'product_name', 'quantity', 'unit_price', 'invoice_number',
                          'invoice_date', 'store_address', ]])
        
        # TODO
        st.markdown(frontendtemplate.title_temp.format('各列別數量 總攬'), unsafe_allow_html=True)
        plot_cat_cal = init_invoice_df.groupby('cat_id')['invoice_number'].count()
        plot_cat_cal.plot(kind='bar', rot=85, figsize=(10, 6))
        st.set_option('deprecation.showPyplotGlobalUse', False)
        st.pyplot()
        # st.bar_chart(plot_cat_cal, width=20,use_container_width=True)
        # st.dataframe(init_invoice_df.groupby('cat_id')['unit_price'].count())
        # TODO
        st.markdown(frontendtemplate.title_temp.format('各列載具畫個在樂別的數量總攬'), unsafe_allow_html=True)
        plot_catcnid_cal = init_invoice_df.groupby(['carrier_number', 'cat_id'], as_index=False).size()
        st.dataframe(plot_catcnid_cal)
        # TODO
        st.markdown(frontendtemplate.title_temp.format('各類別在各縣市上的數量總攬'), unsafe_allow_html=True)

        # TODO 分欄
        left_column, right_column = st.beta_columns(2)
        with left_column:

            left_column.write("飲料沖泡")
            plot_one_df.loc[plot_one_df['cat_id'] == 1, ['city', 'size']].plot.bar(x='city', y='size', rot=85)

            left_column.pyplot()
            left_column.write("美食生鮮")
            plot_one_df.loc[plot_one_df['cat_id'] == 3, ['city', 'size']].plot.bar(x='city', y='size', rot=85)

            left_column.pyplot()
            left_column.write("居家生活")
            plot_one_df.loc[plot_one_df['cat_id'] == 5, ['city', 'size']].plot.bar(x='city', y='size', rot=85)

            left_column.pyplot()
            left_column.write("家電")
            plot_one_df.loc[plot_one_df['cat_id'] == 7, ['city', 'size']].plot.bar(x='city', y='size', rot=85)

            left_column.pyplot()
            left_column.write("零食")
            plot_one_df.loc[plot_one_df['cat_id'] == 9, ['city', 'size']].plot.bar(x='city', y='size', rot=85)
            left_column.pyplot()
            left_column.write("菸酒")
            plot_one_df.loc[plot_one_df['cat_id'] == 13, ['city', 'size']].plot.bar(x='city', y='size', rot=85)
            left_column.pyplot()
            left_column.write("生活休閒")
            plot_one_df.loc[plot_one_df['cat_id'] == 15, ['city', 'size']].plot.bar(x='city', y='size', rot=85)
            left_column.pyplot()

        with right_column:
            right_column.write("麵食料理")
            plot_one_df.loc[plot_one_df['cat_id'] == 2, ['city', 'size']].plot.bar(x='city', y='size', rot=85)
            right_column.pyplot()
            right_column.write("保健生機")
            plot_one_df.loc[plot_one_df['cat_id'] == 4, ['city', 'size']].plot.bar(x='city', y='size', rot=85)
            right_column.pyplot()
            right_column.write("美容保養")
            plot_one_df.loc[plot_one_df['cat_id'] == 6, ['city', 'size']].plot.bar(x='city', y='size', rot=85)
            right_column.pyplot()
            right_column.write("箱包服飾")
            plot_one_df.loc[plot_one_df['cat_id'] == 8, ['city', 'size']].plot.bar(x='city', y='size', rot=85)
            right_column.pyplot()
            right_column.write("其他")
            plot_one_df.loc[plot_one_df['cat_id'] == 10, ['city', 'size']].plot.bar(x='city', y='size', rot=85)
            right_column.pyplot()
            right_column.write("3C")
            plot_one_df.loc[plot_one_df['cat_id'] == 12, ['city', 'size']].plot.bar(x='city', y='size', rot=85)
            right_column.pyplot()
            right_column.write("寵物專區")
            plot_one_df.loc[plot_one_df['cat_id'] == 14, ['city', 'size']].plot.bar(x='city', y='size', rot=85)
            right_column.pyplot()
        
        
    if btn_dic['btn_predict']:

        classifierName = ClassifierByName(df=init_invoice_df)
        result = classifierName.testByData([getproductword])
        st.markdown(frontendtemplate.title_temp.format('預測結果'), unsafe_allow_html=True)
        st.markdown("""<h3 style="color:#0877E3;font-weight:bold;">準確率為：0.9633427718680646</h3>""",
                    unsafe_allow_html=True)
        outputHtml= predictShow(getproductword, result[0])
        st.markdown(outputHtml, unsafe_allow_html=True)
        st.markdown("""<h3 style="color:#0877E3;font-weight:bold;">各類別數據量</h3>""", unsafe_allow_html=True)
        catval_df = dfValueCount(init_invoice_df)
        catval_df.value_counts().plot(kind='bar', rot=85, figsize=(10, 6))
        st.set_option('deprecation.showPyplotGlobalUse', False)
        st.pyplot()

        





    if btn_dic['btn_rec']:
        invoice_afterFilter_df,resdf,final_dict= getFilterDataFrame(init_invoice_df, selected_cat_list, getwordListStr)
        # TODO 主頁
        st.markdown(frontendtemplate.title_temp.format('此次查詢Infos'), unsafe_allow_html=True)
        st.subheader("此次查詢共{}筆".format(invoice_afterFilter_df.shape[0]))
        st.dataframe(invoice_afterFilter_df[['invoice_number','product_name','store_address','quantity','unit_price',]])
        # # 分群資料
        # st.dataframe(resdf.head(25))

        group_users_cal_dict = resdf.set_index(['group_name'])['users'].to_dict()
        group_users_count_dict = resdf.set_index(['group_name'])['users_count'].to_dict()
        # # 分群人數資料
        # st.write(group_users_cal_dict)
        # TODO 分欄
        left_column, right_column = st.beta_columns(2)
        # Or even better, call Streamlit functions inside a "with" block:
        with left_column:
            left_column.markdown(frontendtemplate.title_temp.format('曾經購買'),unsafe_allow_html=True)
            used_buy_items = final_dict['used_buy']
            # left_column.write(used_buy_items)
            for item in used_buy_items:
                card_temp_body = ""
                group_name = item['group_name']
                result = item['result']
                outputHtmlList = imageListShow(result)
                for item in outputHtmlList:
                    card_temp_body += item
                # print(type(group_users_cal_dict[group_name]))
                group_users_cal_dict[group_name] = group_users_cal_dict[group_name].replace('\r', '\\r').replace('\n', '\\n')
                # users_list = json.loads(group_users_cal_dict[group_name], strict=False)
                # print(users_list)
                card_temp = frontendtemplate.card_temp_up + card_temp_body + frontendtemplate.card_temp_down
                left_column.markdown(card_temp.format('#F6800A',group_name,group_users_count_dict[group_name]),unsafe_allow_html=True)
        with right_column:
            right_column.markdown(frontendtemplate.title_temp.format('未來可能購買'), unsafe_allow_html=True)
            feature_buy_items=final_dict['feature_buy']
            # right_column.write(feature_buy_items)
            for item in feature_buy_items:
                card_temp_body = ""
                group_name = item['group_name']
                result = item['result']
                outputHtmlList = imageListShow(result)
                for item in outputHtmlList:
                    card_temp_body += item
                card_temp=frontendtemplate.card_temp_up+card_temp_body+frontendtemplate.card_temp_down
                right_column.markdown(card_temp.format('#03b6fc',group_name,group_users_count_dict[group_name]),unsafe_allow_html=True)

       

if __name__ == '__main__':
    main()



