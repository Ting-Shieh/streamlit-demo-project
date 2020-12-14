import jieba.analyse
import jieba
import pandas as pd
# from sklearn.externals import joblib  # 模型持久化
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB


class ClassifierByName():
    def __init__(self, df):
        self.df = df
        self.stopwords_df = pd.read_csv("./data/stopwords_zh.txt", index_col=False, sep="\t", quoting=3,
                                        names=['stopword'], encoding='utf-8')

    def showStopwords(self):
        print(self.stopwords_df)

    def drop_stopwords(self, contents, stopwords):
        """去掉停用詞"""

        products_clean = []  # 最後會是 list of list
        for line in contents:
            line_clean = []
            for word in line:
                remove_digits = str.maketrans('', '', '0123456789')
                word = word.translate(remove_digits)
                # 出現停用詞 => 過濾掉
                if word in stopwords:
                    continue
                # 未出現在停用詞 => 留下
                line_clean.append(word)
            products_clean.append(line_clean)
        return products_clean

    def transdorm_data(self):
        """"""
        jieba.load_userdict('./data/mydict.txt')
        # step1. => 去數字並斷出關鍵字
        ori_product_list = self.df["product_name"].values.tolist()
        product_S = []
        for line in ori_product_list:
            remove_digits = str.maketrans('', '', '0123456789')
            line = line.translate(remove_digits)
            #             # 法1
            #             segment = jieba.analyse.extract_tags(line)
            # 法2
            segment = jieba.cut(line)
            product_S.append(segment)
        self.df["product_S"] = product_S

        # step2. => 去掉停用詞(在清洗)
        products_list = self.df["product_S"].values.tolist()
        stopwords_list = self.stopwords_df["stopword"].values.tolist()
        self.df["products_clean"] = self.drop_stopwords(products_list, stopwords_list)
        return self.df[['products_clean', "cat_id"]]

    def transdorm_test_data(self, test_df, col_name):
        """"""
        jieba.load_userdict('./data/mydict.txt')
        res_df = pd.DataFrame()
        # step1. => 去數字並斷出關鍵字
        ori_product_list = test_df[col_name].values.tolist()
        product_S = []
        for line in ori_product_list:
            remove_digits = str.maketrans('', '', '0123456789')
            line = line.translate(remove_digits)
            #             # 法1
            #             segment = jieba.analyse.extract_tags(line)
            # 法2
            segment = jieba.cut(line)
            product_S.append(segment)
        res_df["product_S"] = product_S

        # step2. => 去掉停用詞(在清洗)
        products_list = res_df["product_S"].values.tolist()
        stopwords_list = self.stopwords_df["stopword"].values.tolist()
        res_df["products_clean"] = self.drop_stopwords(products_list, stopwords_list)
        return res_df['products_clean']

    def getTrainData(self):
        """"""
        df_train = self.transdorm_data()
        return train_test_split(self.df["products_clean"].values, self.df["cat_id"].values, random_state=1)

    def transform_data(self, x_data):
        words = []
        for line_index in range(len(x_data)):
            try:
                # x_train[line_index][word_index] = str(x_train[line_index][word_index])
                words.append(' '.join(x_data[line_index]))
            except Exception as e:
                print(e)
        return words

    def run_naive_bayes(self):
        """"""
        # get data
        x_train, x_test, y_train, y_test = self.getTrainData()
        #
        words = self.transform_data(x_train)

        #
        vec = CountVectorizer(analyzer='word', max_features=4000, lowercase=False)
        vec.fit_transform(words)
        # 模型持久化 - CountVectorizer()
        joblib.dump(vec, "./model/CountVectorizer.model")

        #
        classifier = MultinomialNB()
        classifier.fit(vec.transform(words), y_train)
        # 模型持久化 - MultinomialNB()
        joblib.dump(classifier, "./model/naive_CountV.model")

        # 藉由模型對測試數據進行預測結果
        test_words = self.transform_data(x_test)
        y_predict_naive_bayes = classifier.predict(vec.transform(test_words))

        # 準確率為
        score = classifier.score(vec.transform(test_words), y_test)
        print("測試集結果=>", str(y_predict_naive_bayes))
        print("準確率為：" + str(score))

    def testByData(self, data_list, col_name="product_name"):
        """
        data_list = ['','','','']
        """
        data_list = pd.DataFrame({col_name: data_list})
        CountV_model = joblib.load("./model/CountVectorizer.model")
        naive_model = joblib.load("./model/naive_CountV.model")
        #         stopwords_list = self.stopwords_df["stopword"].values.tolist()

        # 過濾停用詞

        test_data = self.transdorm_test_data(data_list, col_name)

        words = self.transform_data(test_data)

        #         CountV_model = CountVectorizer(analyzer='word', max_features=4000,  lowercase = False)
        #         CountV_model.fit_transform(words)
        predict = naive_model.predict(CountV_model.transform(words))
        return predict