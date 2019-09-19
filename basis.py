#
# import matplotlib.pyplot as plt
# from scipy.stats import pearsonr
#
#
# # voorbeeld dijken
# x = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19]
y1 = [0,2,4,6,8,8,8,10,11,12,13,13,13,12,11,9,8,7,6,5]
y2 = [0,2,4,6,6,6,8,10,10,10,10,10,10,9,10,9,8,7,6,5]
y3 = [0,2,4,6,8,8,8,8,8,8,8,8,8,8,8,8,8,7,6,5]
#
#
# corr, p_value = pearsonr(y1, y2)
# corr2, p_value2 = pearsonr(y2, y3)
# print corr, corr2
#
# # fig = plt.figure(figsize=(60, 20))
# #
# # ax1 = fig.add_subplot(111, label ="1")
#
# plt.plot(x,y1)
# plt.plot(x,y2)
# plt.plot(x,y3)
# # plt.show()
#
# from scipy import stats
# import numpy
#
# def getDistribution(data):
#     kernel = stats.gaussian_kde(data)
#     class rv(stats.rv_continuous):
#         def _cdf(self, x):
#             return kernel.integrate_box_1d(-numpy.Inf, x)
#     return rv()
#
# test = getDistribution(y1)
# print test.rvs(size=100)
#
# plt.plot(test.rvs(size=100))
# plt.show()

import pandas as pd
import numpy as np
# from sklearn import preprocessing
# import matplotlib
# import matplotlib.pyplot as plt
# import seaborn as sns
#
# matplotlib.style.use('ggplot')
#
# df = pd.DataFrame({
#     # positive skew
#     'x1': y1,
#     # negative skew
#     'x2': y2,
#     # no skew
#     'x3': y3
# })
#
# scaler = preprocessing.MinMaxScaler()
# scaled_df = scaler.fit_transform(df)
# scaled_df = pd.DataFrame(scaled_df, columns=['x1', 'x2', 'x3'])
#
# fig, (ax1, ax2) = plt.subplots(ncols=2, figsize=(6, 5))
# ax1.set_title('Before Scaling')
# sns.kdeplot(df['x1'], ax=ax1)
# sns.kdeplot(df['x2'], ax=ax1)
# sns.kdeplot(df['x3'], ax=ax1)
# ax2.set_title('After Min-Max Scaling')
# sns.kdeplot(scaled_df['x1'], ax=ax2)
# sns.kdeplot(scaled_df['x2'], ax=ax2)
# sns.kdeplot(scaled_df['x3'], ax=ax2)
# plt.show()
#

x1 = [1,2,3,4,5,6,7,8,9,10]
y1 = [2,2,3,4,25,6,7,8,np.nan,10]
y2 = [2,2,3,4,np.nan,6,7,8,np.nan,10]
df = pd.DataFrame({
    # positive skew
    'x1': y1,
    # negative skew
    'x2': y2,
    # no skew
    'x3': y3
})