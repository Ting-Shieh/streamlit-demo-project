import pandas as pd
class UserProfileData:
    def __init__(self, dbfunc):
        self.user_df = dbfunc('select * from users')
        age_df = dbfunc('select * from ages')
        self.age_dict = dict(zip(age_df['age_id'], age_df['age_level_name']))
        income_df = dbfunc('select * from incomes')
        self.income_dict = dict(zip(income_df['income_id'], income_df['income_level_name']))

    def get_userprofile(self, user_list):
        res = dict()
        """排重複的 carrier_number"""
        final_df = self.user_df.loc[self.user_df['carrier_id'].isin(user_list)]
        final_df['district_name'] = final_df['district'].map(self.income_dict)
        final_df['age_name'] = final_df['age'].map(self.age_dict)

        #
        new_income_result_df = final_df['district_name'].value_counts().to_frame()
        new_income_result_df['por'] = new_income_result_df['district_name'] / new_income_result_df[
            'district_name'].sum()
        income_list = [{"name": idx, "value": '{:.2f}'.format(round(col['por'], 3) * 100)} for idx, col in
                       new_income_result_df.iterrows()]
        res['income_distribution'] = income_list
        #
        new_age_result_df = final_df['age_name'].value_counts().to_frame()
        new_age_result_df['por'] = new_age_result_df['age_name'] / new_age_result_df['age_name'].sum()
        age_list = [{"name": idx, "value": '{:.2f}'.format(round(col['por'], 3) * 100)} for idx, col in
                    new_age_result_df.iterrows()]
        res['age_distribution'] = age_list
        #
        new_city_result_df = final_df['city'].value_counts().to_frame()
        new_city_result_df['por'] = new_city_result_df['city'] / new_city_result_df['city'].sum()
        city_list = [{"name": idx, "value": '{:.2f}'.format(round(col['por'], 3) * 100)} for idx, col in
                     new_city_result_df.iterrows()]
        res['city_distribution'] = city_list
        #
        new_gender_result_df = final_df['gender'].value_counts().to_frame()
        new_gender_result_df['por'] = new_gender_result_df['gender'] / new_gender_result_df['gender'].sum()
        gender_list = [{"name": '未知' if idx == '' else idx, "value": '{:.2f}'.format(round(col['por'], 3) * 100)} for
                       idx, col in new_gender_result_df.iterrows()]
        res['gender_distribution'] = gender_list

        return res