import pandas as pd

title_temp="""

"""

card_temp ="""
	<div style="background-color:#C6C7C4;padding:10px;border-radius:10px;margin:10px;">
	<h3 style="color:white;text-align:center; background-color:#F6800A;border-radius:10px;">客群:{}<span>{} 人</span></h3>
	{}<span style="color:white;font-size:24px;font-weight:bold;">&rarr;</span>
	{}<span style="color:white;font-size:24px;font-weight:bold;">&rarr;</span>
	{}<span style="color:white;font-size:24px;font-weight:bold;">&rarr;</span>
	{}<span style="color:white;font-size:24px;font-weight:bold;">&rarr;</span>
	{}<span style="color:white;font-size:24px;font-weight:bold;">&rarr;</span>
	{}<span style="color:white;font-size:24px;font-weight:bold;">&rarr;</span>
	{}<span style="color:white;font-size:24px;font-weight:bold;">&rarr;</span>
	{}<span style="color:white;font-size:24px;font-weight:bold;">&rarr;</span>
	{}<span style="color:white;font-size:24px;font-weight:bold;">&rarr;</span>
	{}
	</div>
	"""





icon_temp ="""
    <img src="{}" style="width: 30px;height: 30px;border-radius: 50%;margin-left:5px;">
"""


iconFileNameData ={
    "category":["飲料沖泡", "麵食料理", "美食生鮮", "保健生機", "居家生活", "美容保養", "家電", "箱包服飾", "零食", "其他", "旅遊住宿", "3C", "菸酒",
                       "寵物專區", "生活休閒", ],
    "finename": ['https://www.flaticon.com/svg/static/icons/svg/2405/2405479.svg',
        'https://www.flaticon.com/svg/static/icons/svg/1205/1205091.svg',
        'https://www.flaticon.com/svg/static/icons/svg/2329/2329865.svg',
        'https://www.flaticon.com/svg/static/icons/svg/3867/3867897.svg',
        'https://www.flaticon.com/svg/static/icons/svg/578/578008.svg',
        'https://www.flaticon.com/svg/static/icons/svg/3465/3465292.svg',
        'https://www.flaticon.com/svg/static/icons/svg/3578/3578208.svg',
        'https://www.flaticon.com/svg/static/icons/svg/2744/2744313.svg',
        'https://www.flaticon.com/svg/static/icons/svg/2553/2553691.svg',
        'https://www.flaticon.com/svg/static/icons/svg/2898/2898378.svg',
        'https://www.flaticon.com/svg/static/icons/svg/3022/3022937.svg',
        'https://www.flaticon.com/svg/static/icons/svg/997/997276.svg',
        'https://www.flaticon.com/svg/static/icons/svg/2451/2451685.svg',
        'https://www.flaticon.com/svg/static/icons/svg/2439/2439769.svg',
        'https://www.flaticon.com/svg/static/icons/svg/3557/3557907.svg']
     }
iconFileName_df = pd.DataFrame.from_dict(iconFileNameData)



def imageListShow(img_list):
    global iconFileName_df
    outputHtmlList=[]
    icon_temp = """<div style="display:inline-block;"><img src="{}" style="width: 35px;height: 35px;border-radius: 50%;margin-left:5px;"><span>{}</span></div>"""

    for img in img_list:
        name = iconFileName_df.loc[iconFileName_df['category']==img,'finename'].values[0]
        outputHtmlList.append(icon_temp.format(name,img))

    return outputHtmlList
components_temp= """
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
    <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.7.0/css/all.css" integrity="sha384-lZN37f5QGtY3VHgisS14W3ExzMWZxybE1SJSEsQp9S+oqd12jhcu+A56Ebc1zFSJ" crossorigin="anonymous">
    <script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>
    <div style="background-color:#C6C7C4;padding:10px;border-radius:10px;margin:10px;">
	<h3 style="color:white;text-align:center; background-color:#F6800A;border-radius:10px;">客群:{}</h3>
	{}{}<i>&rarr;</span>{}{}{}{}{}{}{}{}
	</div>
   
  
    """



