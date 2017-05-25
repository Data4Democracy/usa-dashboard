import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt
import seaborn as sns

# My personal aesthetic
sns.set_context('talk')
sns.set_style('white')

unrate = pd.read_csv('../data/national/LNS14000000.2009 2017.csv', index_col=0)

training_slice = 40
test_slice = 8

# ARIMA parameters
p, q, r = 4, 1, 0

unrate = unrate.iloc[-training_slice:]
unrate.index = unrate.index.to_datetime()

pred_range = unrate.index[-test_slice - 1:]

# Actually training on the first order differencing of the data
model = sm.tsa.ARIMA(unrate.diff().iloc[1:-test_slice], (p, q, r))
result = model.fit()

conf_int = np.empty((test_slice + 1, 2))
conf_int[0] = (0, 0)
forecast, stderr, conf_int[1:, :] = result.forecast(test_slice)

# Probably a simpler way to do this in pandas
simulated = np.empty(test_slice + 1)
simulated[0] = unrate.iloc[-test_slice - 1].values
simulated[1:] = unrate.iloc[-test_slice].values + forecast.cumsum()

fig, ax = plt.subplots(1, 1)

ax.plot(unrate, 'k-', label='Unemployment Rate')
ax.plot(pred_range, simulated, 'b', label='Prediction (with 95% CI)')  # is it 95?
ax.plot(pred_range, simulated + conf_int[:, 0], 'b--')
ax.plot(pred_range, simulated + conf_int[:, 1], 'b--')

ax.fill_between(pred_range, simulated, simulated + conf_int[:, 0],
                where=simulated + conf_int[:, 0] <= simulated, facecolor='blue',
                interpolate=True, alpha=0.1)

ax.fill_between(pred_range, simulated, simulated + conf_int[:, 1],
                where=simulated + conf_int[:, 1] >= simulated, facecolor='blue',
                interpolate=True, alpha=0.1)

ax.set_xlabel('Month')
ax.set_ylabel('Unemployment rate (National)')
ax.set_title('Unemployment rate with ARIMA({},{},{}) model prediction'.format(p, q, r))
ax.legend()
sns.despine()

plt.savefig('../figures/ur-arima({},{},{}).svg'.format(p, q, r), bbox_inches='tight')
