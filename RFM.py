############################################
# PROJE: RFM ile Müşteri Segmentasyonu
############################################
# Bir e-ticaret şirketi müşterilerini segmentlere ayırıp bu segmentlere göre pazarlama stratejileri belirlemek istiyor.
# online_retail_II.xlsx veri setinin "Year 2010-2011" isimli sheet'ine RFM analizi uygulayınız.

import pandas as pd
import datetime as dt
#pd.set_option('display.max_rows', None)
#pd.set_option('display.max_columns', None)

df_= pd.read_excel("online_retail_II.xlsx", sheet_name="Year 2010-2011" )

df=df_.copy()
df.head()

#essiz urun sayisi:
df["Description"].nunique()

# hangi urunden kacar tane:
df["Description"].value_counts().head()

# en cok siparis edilen urun:
df.groupby("Description").agg({"Quantity": "sum"}).head()

# yukarıdaki çıktıyı nasil siralariz?
df.groupby("Description").agg({"Quantity": "sum"}).sort_values("Quantity", ascending=False).head()

# toplam kac fatura kesilmiştir?
df["Invoice"].nunique()

# fatura basina ortalama kac para kazanilmistir? ,
# (iki değişkeni çarparak yeni bir değişken oluşturmak gerekmektedir)
# iadeleri çıkararak yeniden df'i oluşturalım
df= df[~df["Invoice"].str.contains("C", na=False)] #iadeleri çıkardık

df["TotalPrice"] = df["Quantity"] * df["Price"]

#en pahali urunler:
df.sort_values("Price",ascending=False).head()

# hangi ulkeden kac siparis geldi?
df["Country"].value_counts()

# hangi ulke ne kadar kazandırdı?
df.groupby("Country").agg({"TotalPrice":"sum"}).sort_values("TotalPrice",ascending=False).head()

df.isnull().sum()
df.dropna(inplace=True)

df.describe([0.01, 0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99]).T

#RFM Calculating

df["InvoiceDate"].max() # veri setindeki max tarih Timestamp('2011-12-09 12:50:00')
today_date = dt.datetime(2011, 12, 11)

rfm = df.groupby('Customer ID').agg({'InvoiceDate': lambda date: (today_date - date.max()).days,
                                     'Invoice': lambda num: len(num),
                                     'TotalPrice': lambda TotalPrice: TotalPrice.sum()})

rfm.columns= ['Recency', 'Frequency', 'Monetary']


rfm = rfm[(rfm["Monetary"]) > 0 & (rfm["Frequency"] > 0)] #iki tane monetory sıfır değer vardı

#rfm scores

rfm["RecencyScore"]= pd.qcut(rfm['Recency'],5,labels=[5, 4, 3, 2, 1]) #qcut küçükten büyüğe sıralar

rfm

rfm["FrequencyScore"] = pd.qcut(rfm['Frequency'], 5, labels=[1, 2, 3, 4, 5])

rfm["MonetaryScore"] = pd.qcut(rfm['Monetary'], 5, labels=[1, 2, 3, 4, 5])

rfm["RFM_SCORE"] = (rfm['RecencyScore'].astype(str) +
                    rfm['FrequencyScore'].astype(str) +
                    rfm['MonetaryScore'].astype(str))

rfm[rfm["RFM_SCORE"] == "555"].head()

# RFM isimlendirmesi
seg_map = {
    r'[1-2][1-2]': 'Hibernating',
    r'[1-2][3-4]': 'At_Risk',
    r'[1-2]5': 'Cant_Loose',
    r'3[1-2]': 'About_to_Sleep',
    r'33': 'Need_Attention',
    r'[3-4][4-5]': 'Loyal_Customers',
    r'41': 'Promising',
    r'51': 'New_Customers',
    r'[4-5][2-3]': 'Potential_Loyalists',
    r'5[4-5]': 'Champions'
}

rfm

rfm['Segment'] = rfm['RecencyScore'].astype(str) + rfm['FrequencyScore'].astype(str)
rfm['Segment'] = rfm['Segment'].replace(seg_map, regex=True)

rfm[["Segment", "Recency", "Frequency", "Monetary"]].groupby("Segment").agg(["mean", "count"])
new_df = pd.DataFrame()
new_df["Loyal_Customers"] = rfm[rfm["Segment"] == "Loyal_Customers"].index
new_df.to_csv("Loyal_Customers.csv")

