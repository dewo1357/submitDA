import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

def daily_orders_df(df):
    daily_orders_df = df.resample(rule='M', on='order_approved_at').agg({
    'order_id' : 'nunique',
    'price' : 'sum' 
    })
    
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
    'order_id' : 'order_count',
    'price' : 'Revenue'
    },inplace=True)
    
    return daily_orders_df

def items_price_df(df):
    items_price_df = df.groupby('product_category_name_english').agg({
        'order_id' : 'nunique',
        'price' : 'sum'
    }).reset_index()

    items_price_df.rename(columns={
        'order_id' : 'order_count',
        'price' : 'Revenue'
    },inplace=True)

    return items_price_df

def create_bycity_df(df):
    bycity_df = df.groupby(by='customer_city',as_index=False).agg({
        'order_id' : 'nunique',
        'price' : 'sum'
    })

    bycity_df.rename(columns={
        'order_id' : 'order_count',
        'price' : 'Revenue'
    },inplace=True)
    
    return bycity_df

def create_bystate_df(df):
    bystate_df = df.groupby('customer_state',as_index=False).agg({
        'order_id' : 'nunique',
        'price' : 'sum'
    })

    bystate_df.rename(columns={
        'order_id' : 'order_count',
        'price' : 'Revenue'
    },inplace=True)

def create_category_product(df):
    category_product = join_all.groupby('product_category_name_english').agg({
    'order_id' : 'nunique',
    'price' : 'sum'
    }).sort_values(by='order_id',ascending=False).reset_index()
    
    category_product.rename(columns={
    'order_id' : 'order_count',
    'price' : 'Total_price'
    },inplace=True)

    return category_product

def create_rfm_analysis(df):
    rfm_analysis = df.groupby('customer_city').agg({
    'order_approved_at' : 'max',
    'order_id' : 'nunique',
    'price' : 'sum'
    }).reset_index()
    
    rfm_analysis.columns = ['customer_city', 'max_order_timestamp', 'frequency', 'monetary']
    
    rfm_analysis['max_order_timestamp'] = rfm_analysis['max_order_timestamp'].dt.date
    recent_date = df['order_approved_at'].dt.date.max()
    rfm_analysis["recency"] = rfm_analysis['max_order_timestamp'].apply(lambda x: (recent_date - x).days)
    
    rfm_analysis.drop('max_order_timestamp', axis=1, inplace=True)

    return rfm_analysis

join_all = pd.read_csv('join_all.csv')

review_rate = join_all.groupby('review_comment_title').review_id.nunique().reset_index()

import datetime

date_column = ['order_approved_at']
join_all.sort_values(by='order_approved_at',inplace=True)
join_all.reset_index(inplace=True)

for column in date_column:
    join_all[column] = pd.to_datetime(join_all[column])

min_date = join_all['order_approved_at'].min()
max_date = join_all['order_approved_at'].max()

with st.sidebar:
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")

    start_date,end_date = st.date_input(
        label='Order Date',min_value=min_date,
        max_value=max_date,
        value=[min_date,max_date]
    )

main_df = join_all[(join_all["order_approved_at"] >= str(start_date)) & 
                (join_all["order_approved_at"] <= str(end_date))]

daily_orders_df = daily_orders_df(main_df)
items_price_df = items_price_df(main_df)
bycity_df = create_bycity_df(main_df)
bystate_df = create_bystate_df(main_df)
category_product = create_category_product(main_df)
rfm_analysis = create_rfm_analysis(main_df)

st.header('E-Commerce Public Dataset :sparkles:')

st.subheader('Daily Orders')
 
col1, col2 = st.columns(2)
 
with col1:
    total_orders = daily_orders_df.order_count.sum()
    st.metric("Total orders", value=total_orders)
 
with col2:
    total_revenue = format_currency(daily_orders_df.Revenue.sum(), "AUD", locale='es_CO') 
    st.metric("Total Revenue", value=total_revenue)
 
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_orders_df["order_approved_at"],
    daily_orders_df["order_count"],
    marker='o', 
    linewidth=5,
    color="#00688B"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
 
st.pyplot(fig)

st.subheader("BEST & WORST CITY CONTRIBUTION")
 
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(15,4))

color = ['#00688B','#97FFFF','#97FFFF','#97FFFF','#97FFFF','#97FFFF']

sns.barplot(x='order_count',y='customer_city',data=bycity_df.sort_values(by='order_count',ascending=False).head(5),palette=color,ax=ax[0])
ax[0].set_title ('Top 5 contributions',loc='center',fontsize=20)
ax[0].set_ylabel ('Customer_city')
ax[0].set_xlabel ('Order Count')

sns.barplot(x='order_count',y='customer_city',data=bycity_df.sort_values(by='order_count',ascending=True).head(5),palette=color,ax=ax[1])
ax[1].yaxis.tick_right()
ax[1].yaxis.set_label_position('right')
ax[1].invert_xaxis()
ax[1].set_title ('The 5 lowest contributions',loc='center',fontsize=20)
ax[1].set_ylabel ('Customer_city')
ax[1].set_xlabel ('Order Count')
 
st.pyplot(fig)

st.subheader("Product Demographics")

col1, col2 = st.columns(2)
 
with col1:
    
    fig, ax = plt.subplots(figsize=(20, 10))

    sns.barplot(x='product_category_name_english',y='order_count',data=category_product.sort_values(by='order_count',ascending=False).head(5),palette=color,ax=ax)
    ax.set_title("Top Five Product)", loc="center", fontsize=50)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='x', labelsize=25)
    ax.tick_params(axis='y', labelsize=30)
    st.pyplot(fig)

with col2:
    
    fig, ax = plt.subplots(figsize=(20, 10))

    color = ['#00688B','#97FFFF','#97FFFF','#97FFFF','#97FFFF','#97FFFF']
    
    sns.barplot(x='product_category_name_english',y='Total_price',data=category_product.sort_values(by='Total_price',ascending=False).head(5),palette=color,ax=ax)
    ax.set_title("Top Five Revenue Product", loc="center", fontsize=50)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='x', labelsize=20)
    ax.tick_params(axis='y', labelsize=30)
    st.pyplot(fig)

st.subheader("Best City Based on RFM Parameters")
 
col1, col2, col3 = st.columns(3)
 
with col1:
    avg_recency = round(rfm_analysis.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)
 
with col2:
    avg_frequency = round(rfm_analysis.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)
 
with col3:
    avg_frequency = format_currency(rfm_analysis.monetary.mean(), "AUD", locale='es_CO') 
    st.metric("Average Monetary", value=avg_frequency)
 
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
color = ['#00688B','#97FFFF','#97FFFF','#97FFFF','#97FFFF','#97FFFF']

sns.barplot(x='customer_city',y='recency',data=rfm_analysis.sort_values(by='recency',ascending=True).head(5),palette=color,ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("customer_city", fontsize=30)
ax[0].set_title("By Recency (days)", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=30)

sns.barplot(y="frequency", x="customer_city", data=rfm_analysis.sort_values(by="frequency", ascending=False).head(5), palette=color, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("customer_city", fontsize=30)
ax[1].set_title("By Frequency", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=30)

sns.barplot(y="monetary", x="customer_city", data=rfm_analysis.sort_values(by="monetary", ascending=False).head(5), palette=color, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel("customer_city", fontsize=30)
ax[2].set_title("By Monetary", loc="center", fontsize=50)
ax[2].tick_params(axis='y', labelsize=30)
ax[2].tick_params(axis='x', labelsize=30)

st.pyplot(fig)

st.caption('Sudied at dicoding academy')