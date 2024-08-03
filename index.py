'''
统计一只股票在过去所有天的表现, 然后按照日期分组, 看具体到每一天的涨跌幅平均有多少.
意义: 我可以知道历史上, 每个月的每一天平均是涨是跌, 从而可以在未来的交易中, 根据历史数据来预测未来的涨跌.
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
    polars.col('aClose').shift(1).alias('pClose'),
])
df = df.with_columns([
    ((polars.col('aClose') - polars.col('pClose')) / polars.col('pClose') * 100).alias('change').fill_null(0),
])
df = df.with_columns([
    (polars.col('date').dt.month().cast(polars.Int16) * 100 + polars.col('date').dt.day()).alias('monthDay'),
])
df = df.group_by('monthDay').agg([
    polars.col('change').mean().alias('meanChange'),
]).sort('monthDay')
df = df.with_columns([
    polars.col('meanChange').cum_sum().alias('cumulative'),
])
print(df.head())
print(df.tail())
df.write_csv('output.csv')

fig = px.bar(df, x='monthDay', y='cumulative', title=f'Cumulative Change in {ticker}')
fig.update_layout(xaxis_title='MonthDay', yaxis_title='Profit (%)')
fig.show()
