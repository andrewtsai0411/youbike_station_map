import requests
import pandas as pd
import plotly.express as px
import gradio as gr

def create_youbike_df():
    # 台北
    headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15"
    }
    url = 'https://tcgbusfs.blob.core.windows.net/dotapp/youbike/v2/youbike_immediate.json'
    web = requests.get(url, headers = headers)
    web.encoding = "utf-8"
    data = web.json()
    tpe_df = pd.DataFrame(data)
    tpe_df = tpe_df.loc[:,['sarea','sna', 'total', 'available_rent_bikes', 'available_return_bikes', 'latitude', 'longitude']]
    tpe_df.rename(columns={ 'sarea':'行政區','sna':'站名','total':'停車格數','available_rent_bikes':'可借數量',
                        'available_return_bikes':'可還數量','latitude':'緯度','longitude':'經度'}, inplace=True)
    tpe_df['站名'] = tpe_df['站名'].str.lstrip('YouBike2.0_')
    tpe_df['行政區'] = tpe_df['行政區'].replace('臺大公館校區','大安區')
    tpe_df['城市'] = '台北市'
    tpe_df = tpe_df.reindex(columns=['城市','行政區','站名','停車格數','可借數量','可還數量','緯度','經度'])

    # 台中
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15"
    }
    url = 'https://datacenter.taichung.gov.tw/swagger/OpenData/34a848ab-eeb3-44fd-a842-a09cb3209a7d'
    web = requests.get(url, headers = headers)
    web.encoding = "utf-8"
    data = web.json()
    txg_df = pd.json_normalize(data['retVal'])
    txg_df = txg_df.loc[:,['scity','sarea','sna', 'tot', 'sbi', 'bemp', 'lat', 'lng']]
    txg_df.rename(columns={ 'scity':'城市','sarea':'行政區','sna':'站名','tot':'停車格數','sbi':'可借數量',
                            'bemp':'可還數量','lat':'緯度','lng':'經度'}, inplace=True)
    txg_df['站名'] = txg_df['站名'].str.lstrip('YouBike2.0_')

    # 高雄
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15"
    }
    url = 'https://api.kcg.gov.tw/api/service/Get/b4dd9c40-9027-4125-8666-06bef1756092'
    web = requests.get(url, headers = headers)
    web.encoding = "utf-8"
    data = web.json()
    khh_df = pd.json_normalize(data["data"]["retVal"])
    khh_df = khh_df.loc[:,['scity','sarea','sna', 'tot', 'sbi', 'bemp', 'lat', 'lng']]
    khh_df.rename(columns={ 'scity':'城市','sarea':'行政區','sna':'站名','tot':'停車格數','sbi':'可借數量',
                            'bemp':'可還數量','lat':'緯度','lng':'經度'}, inplace=True)
    khh_df['站名'] = khh_df['站名'].str.lstrip('YouBike2.0_')

    youbike_df = pd.concat([tpe_df, txg_df, khh_df])
    youbike_df = youbike_df.astype({'停車格數': 'int', '可借數量': 'int', '可還數量': 'int', '緯度': 'float', '經度': 'float'})
    return youbike_df

df = create_youbike_df()

def create_station_map(city, district):
    filtered_df = df[(df['城市'] == city) & (df['行政區'] == district)]
    
    fig = px.scatter_map(filtered_df,
        lat='緯度',
        lon='經度',
        color='可借數量',
        color_continuous_scale=px.colors.cyclical.IceFire,
        size='可借數量',
        map_style='carto-voyager',
        center=dict(lat=filtered_df['緯度'].mean(), lon=filtered_df['經度'].mean()),
        zoom=13,
        hover_name='站名',
        hover_data=dict(可借數量=True, 可還數量=True, 停車格數=True, 緯度=False, 經度=False)
    )
    return fig

def update_districts(city):
    # 依城市更新行政區下拉選單的方法
    districts = df[df['城市'] == city]['行政區'].unique().tolist()
    return gr.Dropdown(choices=districts)

with gr.Blocks(theme='earneleh/paris') as demo:
    gr.Markdown('# YouBike 站點地圖')
    
    city_dropdown = gr.Dropdown(
        choices=df['城市'].unique().tolist(),
        label="選擇城市"
    )
    
    district_dropdown = gr.Dropdown(
        choices=df[df['城市'] == df['城市'].unique()[0]]['行政區'].unique().tolist(),
        label="選擇行政區"
    )
    
    plot_map = gr.Plot()

    # 初始化地圖
    demo.load(
        fn=create_station_map,
        inputs=[city_dropdown, district_dropdown],
        outputs=plot_map
    )
    
    # 依城市更新行政區下拉選單
    city_dropdown.change(
        fn=update_districts,
        inputs=city_dropdown,
        outputs=district_dropdown
    )
    
    # 城市或行政區改變時更新地圖
    gr.on(
        triggers=[city_dropdown.change, district_dropdown.change], 
        fn=create_station_map,
        inputs=[city_dropdown,district_dropdown],
        outputs=plot_map
    )

demo.launch()