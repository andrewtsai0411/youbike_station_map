# YouBike 站點地圖

## 簡介

這個專案「YouBike 站點地圖」抓取台北、台中、高雄三個城市的公共自行車即時資訊，建立互動式的介面並將資料以視覺化的方式呈現，讓使用者能夠依所選城市、行政區即時查詢公共自行車站點可借、可還數量。專案使用 `requests` 與 `pandas` 抓取與整理資料、以`plotly`繪圖並利用 `gradio` 建立使用者介面做出成品。

## 如何重現 

- 安裝 [Miniconda](https://docs.anaconda.com/miniconda/)
- 依據 `environment.yml` 建立環境：
  
```bash
conda env create -f environment.yml
```
- 啟動環境並執行 `python youbike_station_map.py` 並前往 `http://127.0.0.1:7860`瀏覽成品。
