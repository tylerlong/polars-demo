import yfinance
import polars
import plotly.express as px

pandas_df = yfinance.download('QQQ')
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
    ((polars.col('aClose') - polars.col('pClose')) / polars.col('pClose') * 100).alias('change'),
])
df = df.with_columns([
    polars.col('change').fill_null(0),
])
df = df.with_columns([
    (polars.col('date').dt.month().cast(polars.Int16) * 100 + polars.col('date').dt.day()).alias('monthDay'),
])
df = df.group_by('monthDay').agg([
    polars.col('change').mean().alias('meanChange'),
])
df = df.sort('monthDay')
df = df.with_columns([
    polars.col('meanChange').cum_sum().alias('cumulative'),
])
print(df.head())
print(df.tail())
df.write_csv('output.csv')

fig = px.bar(df, x='monthDay', y='cumulative', title='Cumulative Change in QQQ')
fig.update_layout(xaxis_title='MonthDay', yaxis_title='Profit (%)')
fig.show()
