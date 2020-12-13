import jieba



def get_keywords(title):
    """
        進行斷詞斷句
    :param title:
    :return:斷詞後list
    """
    return list(jieba.cut(title))


class InvoiceWordCloudDict:
    def __init__(self):
        self.my_wordcloud_dict = {}

    def clean_word(self, w):
        """
            斷詞加清洗
        :param w: 字段
        :return:
        """
        remove_digits = str.maketrans('', '', '0123456789')
        w = w.translate(remove_digits)
        return jieba.cut(w, cut_all=False)

    def wordcloud_format(self, x):
        """
            紀錄字詞出現次數
        :param x:
        :return:
        """
        for word in x:
            if len(word) >= 2:
                if not self.my_wordcloud_dict.__contains__(word):  # 假如詞不再字典當中
                    self.my_wordcloud_dict[word] = 0  # 紀錄字詞出現次數
                self.my_wordcloud_dict[word] += 1

    def sort_wordcloud(self, topnum=20):
        """
            dict 按照 value 排序
        :param topnum:
        :return:
        """
        return {k: v for k, v in
                sorted(self.my_wordcloud_dict.items(), key=lambda item: item[1], reverse=True)[:topnum]}