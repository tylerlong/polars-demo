'''
统计一只股票在过去所有天的表现, 然后按照日期分组, 看具体到每一天上涨的有多少年, 下跌的有多少年

注意: 有一段代码是用来过滤数据测试选举年的
'''
import yfinance
import polars
import plotly.express as px

ticker = 'QQQ'

pandas_df = yfinance.download(ticker)
pandas_df.reset_index(inplace=True)
df: polars.DataFrame = polars.from_pandas(pandas_df)
df = df.rename({'Date': 'date', 'Adj Close': 'aClose'})
df.drop_in_place('Open')
df.drop_in_place('High')
df.drop_in_place('Low')
df.drop_in_place('Close')
df.drop_in_place('Volume')
df = df.with_columns([
    polars.col('aClose').shift(1).alias('pClose').fill_null(polars.col('aClose')),
])
df = df.with_columns([
    polars.when(polars.col('aClose') >= polars.col('pClose'))
    .then(1)
    .otherwise(-1)
    .alias('winLose')
])

# election year filter
df = df.filter(polars.col('date').dt.year() % 4 == 0)
df = df.filter(polars.col('date').dt.year() < 2024)

df = df.with_columns([
    (polars.col('date').dt.month().cast(polars.Int16) * 100 + polars.col('date').dt.day()).alias('monthDay'),
])
df = df.group_by('monthDay').agg([
    polars.col('winLose').sum().alias('winLose'),
]).sort('monthDay')
print(df.head())
print(df.tail())
df.write_csv('output2.csv')

fig = px.bar(df, x='monthDay', y='winLose', title=f'Win - Lost times in {ticker}')
fig.update_layout(xaxis_title='MonthDay', yaxis_title='Win - Lose (times)')
fig.show()
