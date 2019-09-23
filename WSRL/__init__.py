import pandas as pd
import numpy as np
from sklearn import preprocessing
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns




y1 = [1,2,3,4,5,6,6,6,7,8,9,12,12,12,12,12,9,8,7,6,5,4,3,2,1]
y2 = [1,2,3,4,5,6,6,6,7,8,9,10,10,10,10,10,9,8,7,6,5,4,3,2,1]



x1 = list(range(0,49,2))
x2 = list(range(0,25,1))


# x2 = [1,2,3,4,5,6,6,6,7,8,9,12,12,12,12,12,9,8,7,6,5,4,3,2,1]
# x3 = [1,2,3,4,5,6,6,6,7,8,9,12,12,12,12,12,9,8,7,6,5,4,3,2,1]
#
df = pd.DataFrame({
    # positive skew
    'x1': x1,
    # negative skew
    'x2': x2
})
#
# # plt.plot(x,dijk1)
scaler = preprocessing.MinMaxScaler()
scaled_df = scaler.fit_transform(df)
scaled_df = pd.DataFrame(scaled_df, columns=['x1', 'x2'])
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

plt.plot(scaled_df['x1'], y1)
plt.plot(scaled_df['x2'], y2)
plt.show()