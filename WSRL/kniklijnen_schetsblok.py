import pandas as pd
import numpy as np
from sklearn import preprocessing
import matplotlib
import matplotlib.pyplot as plt
# import seaborn as sns
#
#
#
#
# y1 = [1,2,3,4,5,6,6,6,7,8,9,12,12,12,12,12,9,8,7,6,5,4,3,2,1]
# y2 = [1,2,3,4,5,6,6,6,7,8,9,10,10,10,10,10,9,8,7,6,5,4,3,2,1]
#
#
#
# x1 = list(range(0,49,2))
# x2 = list(range(0,25,1))
#
#
# # x2 = [1,2,3,4,5,6,6,6,7,8,9,12,12,12,12,12,9,8,7,6,5,4,3,2,1]
# # x3 = [1,2,3,4,5,6,6,6,7,8,9,12,12,12,12,12,9,8,7,6,5,4,3,2,1]
# #
# df = pd.DataFrame({
#     # positive skew
#     'x1': x1,
#     # negative skew
#     'x2': x2
# })
# #
# # # plt.plot(x,dijk1)
# scaler = preprocessing.MinMaxScaler()
# scaled_df = scaler.fit_transform(df)
# scaled_df = pd.DataFrame(scaled_df, columns=['x1', 'x2'])
#
# print scaled_df
# fig, (ax1, ax2) = plt.subplots(ncols=2, figsize=(6, 5))
# ax1.set_title('Before Scaling')
# sns.kdeplot(df['y1'], ax=ax1)
# sns.kdeplot(df['y2'], ax=ax1)
# sns.kdeplot(df['y3'], ax=ax1)
# ax2.set_title('After Min-Max Scaling')
# sns.kdeplot(scaled_df['y1'], ax=ax2)
# sns.kdeplot(scaled_df['y2'], ax=ax2)
# sns.kdeplot(scaled_df['y3'], ax=ax2)

# plt.plot(scaled_df['x1'], y1)
# plt.plot(scaled_df['x2'], y2)
# # plt.show()
#
# df = pd.DataFrame([(0.0, np.nan, -1.0, 1.0),
#                    (np.nan, 2.0, np.nan, np.nan),
#                    (2.0, 3.0, np.nan, 9.0),
#                     (np.nan, 4.0, -4.0, 16.0)],
#                     columns=list('abcd'))
#
# df_intterp = df.interpolate(method='linear', limit_direction='forward', axis=0)

index = [1,2,3,4,5,6,7,8,9,10]

x_sample = [1,2,4,6,14]
y_sample = [1,2,10,10,6]
x_werkelijk = [1,2,3,4,5,7,8,9,10]
y_werkelijk = [1,1,3,4,6,6,5,4,2]

df1 = pd.DataFrame({'index': x_sample,
                   'y_as': y_sample})

df2 = pd.DataFrame({'index': x_werkelijk,
                   'y_as': y_werkelijk})

df2 = df2.set_index('index')
df2['y_sample'] = df2.index.to_series().map(df1.set_index('index')['y_as'])

print df2

df_intterp = df2.interpolate(method='linear', limit_direction='forward', axis=0)
print df_intterp


plt.plot(df_intterp.index,df_intterp['y_as'])
plt.plot(df_intterp.index,df_intterp['y_sample'])
plt.show()