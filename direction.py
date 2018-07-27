import os
import urllib
import re

import pandas as pd
from bottlenose import Amazon
from retry import retry
from bs4 import BeautifulSoup

from requests_oauthlib import OAuth1Session
import json

# あとで環境変数に設定する
AWS_ACCESS_KEY_ID = "XXXXXX"
AWS_SECRET_ACCESS_KEY = "XXXXXXXX"
AWS_ASSOCIATE_TAG = "XXXXX"

# 検索するテキストのリスト 追ってinputから受け取るようにする

@retry(urllib.error.HTTPError, tries=7, delay=1)
def search(amazon, k, i, pg):
#    print('get products...')
    return amazon.ItemSearch(Keywords=k, SearchIndex=i, Sort="daterank", ResponseGroup="Medium", ItemPage=pg, Power="binding:not kindle")


def main(d_words1, d_words2, d_words3):
    direction_words =[]
    direction_words.append(d_words1)
    direction_words.append(d_words2)
    direction_words.append(d_words3)
    amazon = Amazon(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_ASSOCIATE_TAG, Region='JP',
                    Parser=lambda text: BeautifulSoup(text, 'xml')
                    )
    # 最終格納用のDF作成
    data_frame = pd.DataFrame(index=[], columns=['title', 'author', 'publisher', 'JAN',  'date', 'price', 'image', 'rank', 'content', 'url', 'keyword','ad' ])

    # ワードでアマゾン検索かける。本のジャンルだけ。
    for keyword in direction_words:
        for pg in range(1, 11):
            response = search(amazon, keyword, "Books", pg) #本だけじゃないときは"Books"を変える https://images-na.ssl-images-amazon.com/images/G/09/associates/paapi/dg/index.html
#            print(response)  #特にprintする必要はない

            # 検索によって返ってきた情報をデータフレームに格納していく
            for item in response.find_all('Item'):
 #               print(item.Title.string, item.LargeImage, item.DetailPageURL.string, item.SalesRank, item.IsAdultProduct, item.EAN, item.Label, item.ReleaseDate,item.FormattedPrice, item ) # ここも特にprintする必要はない
                sr = item.SalesRank
                if sr:
                    sr = sr.string
                else:
                    sr = 9999999

                li = item.LargeImage
                au = item.Author
                ad = item.IsAdultProduct

                jan = re.search("[0-9]{13}",str(item.EAN))
                if jan:
                    jan = jan.group()

                lab = item.Label
                if lab:
                    lab = lab.string

                date = item.ReleaseDate
                if date:
                    date = date.string

                price = item.FormattedPrice
                if price:
                    price = price.string

                content = item.Content
                if content:
                    content = content.string

                if sr and li and au : # Rank外じゃなく、表紙の画像があり、著者名がある場合
                    series = pd.Series([item.Title.string, au.string, lab, jan, date, price, li.URL.string, sr, content, item.DetailPageURL.string, keyword, ad], index=data_frame.columns)
                    data_frame = data_frame.append(series, ignore_index = True)
#                elif sr == None and li and au : # ランクがない場合は999999で埋める
#                   series = pd.Series([item.Title.string, li.URL.string, item.DetailPageURL.string, "9999999", au.string, keyword, ad, jan, lab, date, price], index=data_frame.columns)
#                    data_frame = data_frame.append(series, ignore_index = True)
                else: # 他欠損があるデータはスキップする
                    continue

    # 商品ランクでソートする
    data_frame[["rank"]]=data_frame[["rank"]].astype(int)
    output_df = data_frame.sort_values(by="rank")
#    table = tweet_df.to_html(escape=False)

    return output_df

if __name__ == '__main__':
    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    # load_dotenv(find_dotenv())

    book_list_df = main()
#    print(book_list_df)
