import numpy as np
import pandas as pd


def apply(dataframe, operation, *args, **kwargs):
    if operation == vector_aggregator:
        return vector_aggregator(dataframe, *args)
    elif operation == vector_merger:
        return vector_merger(dataframe)
    else:
        condition = kwargs.pop('condition', None)
        clone = dataframe.copy()
        clone.apply(lambda row: operation(row, *args, **kwargs) if not condition or condition(row) else row, axis='columns')
        return clone


def compute(dataframe, operation, *args, **kwargs):
    if operation == vector_aggregator:
        return dataframe.append(vector_aggregator(dataframe, *args))
    elif operation == vector_merger:
        return dataframe.append(vector_merger(dataframe))
    else:
        condition = kwargs.pop('condition', None)
        clone = dataframe.copy()
        clone.apply(lambda row: operation(row, *args, **kwargs) if not condition or condition(row) else row, axis='columns')
        return dataframe.append(clone)


def vector_aggregator(df, function='average'):
    vectimes = df[('result', 'vectime')]
    vecvalues = df[('result', 'vecvalue')]

    # the number of rows in the DataFrame
    n = len(df.index)
    indices = [0] * n

    # the sum of all vector lengths
    capacity = vectimes.apply(len).sum()
    # print(capacity)
    # these are uninitialized, and might be oversized, but always large enough
    out_times = np.empty(capacity)
    out_values = np.empty(capacity)
    out_index = 0

    while True:
        current_time = 0
        times = []
        for i in range(n):
            if len(vectimes[i]) > indices[i]:
                times.append(vectimes[i][indices[i]])

        if times:
            current_time = np.min(times)
        else:
            break

        values_now = []

        for i in range(n):
            while len(vectimes[i]) > indices[i]:
                time = vectimes[i][indices[i]]
                value = vecvalues[i][indices[i]]

                if time == current_time:
                    values_now.append(value)
                    indices[i] += 1
                else:
                    break

        if values_now:
            outval = 0

            if function == 'sum':
                outval = np.sum(values_now)
            elif function == 'average':
                outval = np.average(values_now)
            elif function == 'count':
                outval = len(values_now)
            elif function == 'maximum':
                outval = np.max(values_now)
            elif function == 'minimum':
                outval = np.min(values_now)
            else:
                raise Exception("unknown aggregation function")

            out_times[out_index] = current_time
            out_values[out_index] = outval

            out_index += 1
            # ASSERT out_index < len(out_values)

    out_times = np.resize(out_times, out_index)
    out_values = np.resize(out_values, out_index)

    index = pd.MultiIndex.from_tuples([('Computed', '', '#0', 'various', 'various')], names=['experiment', 'measurement', 'replication', 'module', 'name'])
    cols = pd.MultiIndex(levels=[['result', 'attr'], ['vectime', 'vecvalue', 'title', 'unit']],
                          labels=[[0, 0, 1, 1], [0, 1, 2, 3]])

    result = pd.DataFrame([(out_times, out_values, 'aggregated', 'various')], index=index, columns=cols)
    return result


def vector_merger(df):
    vectimes = df[('result', 'vectime')]
    vecvalues = df[('result', 'vecvalue')]

    # the number of rows in the DataFrame
    n = len(df.index)
    indices = [0] * n

    # the sum of all vector lengths
    capacity = vectimes.apply(len).sum()
    # these are uninitialized
    out_times = np.empty(capacity)
    out_values = np.empty(capacity)
    out_index = 0

    while True:
        current_time = 0
        times = []
        for i in range(n):
            if len(vectimes[i]) > indices[i]:
                times.append(vectimes[i][indices[i]])

        if times:
            current_time = np.min(times)
        else:
            break

        values_now = []

        for i in range(n):
            while len(vectimes[i]) > indices[i]:
                time = vectimes[i][indices[i]]
                value = vecvalues[i][indices[i]]

                if time == current_time:
                    values_now.append(value)
                    indices[i] += 1
                else:
                    break

        for v in values_now:
            out_times[out_index] = current_time
            out_values[out_index] = v

            out_index += 1
            # ASSERT out_index < len(out_values)

    out_times = np.resize(out_times, out_index)
    out_values = np.resize(out_values, out_index)

    index = pd.MultiIndex.from_tuples([('Computed', '', '#0', 'various', 'various')], names=['experiment', 'measurement', 'replication', 'module', 'name'])
    cols = pd.MultiIndex(levels=[['result', 'attr'], ['vectime', 'vecvalue', 'title', 'unit']],
                          labels=[[0, 0, 1, 1], [0, 1, 2, 3]])

    result = pd.DataFrame([(out_times, out_values, 'merged', 'various')], index=index, columns=cols)
    return result


def vector_mean(r):
    v = r[('result', 'vecvalue')]
    r[('result', 'vecvalue')] = np.cumsum(v) / np.arange(1, len(v) + 1)
    r[('attr', 'title')] = 'Mean of ' + r[('attr', 'title')]
    return r


def vector_sum(r):
    r[('result', 'vecvalue')] = np.cumsum(r[('result', 'vecvalue')])
    r[('attr', 'title')] = 'Cumulative sum of ' + r[('attr', 'title')]
    return r


def vector_add(r, c):
    v = r[('result', 'vecvalue')]
    r[('result', 'vecvalue')] = v + c
    r[('attr', 'title')] = r[('attr', 'title')] + " + " + str(c)
    return r


def vector_compare(r, threshold, less=None, equal=None, greater=None):
    v = r[('result', 'vecvalue')]

    if less is not None:
        less_mask = v < threshold
        v = np.where(less_mask, less, v)

    if equal is not None:
        equal_mask = v == threshold
        v = np.where(equal_mask, equal, v)

    if greater is not None:
        greater_mask = v > threshold
        v = np.where(greater_mask, greater, v)

    r[('result', 'vecvalue')] = v

    r[('attr', 'title')] = r[('attr', 'title')] + " compared to " + str(threshold)

    return r


def vector_crop(r, from_time, to_time):
    t = r[('result', 'vectime')]
    v = r[('result', 'vecvalue')]

    from_index = np.searchsorted(t, from_time, 'left')
    to_index = np.searchsorted(t, to_time, 'right')

    r[('result', 'vectime')] = t[from_index:to_index]
    r[('result', 'vecvalue')] = v[from_index:to_index]

    r[('attr', 'title')] = r[('attr', 'title')] + " from {}s to {}s".format(from_time, to_time)
    return r


def vector_difference(r):
    v = r[('result', 'vecvalue')]

    r[('result', 'vecvalue')] = v - np.concatenate([np.array([0]), v[:-1]])

    r[('attr', 'title')] = "Difference of " + r[('attr', 'title')]
    return r


def vector_diffquot(r):
    t = r[('result', 'vectime')]
    v = r[('result', 'vecvalue')]

    dt = t[1:] - t[:-1]
    dv = v[1:] - v[:-1]

    r[('result', 'vecvalue')] = dv / dt
    r[('result', 'vectime')] = t[:-1]

    r[('attr', 'title')] = "Difference quotient of " + r[('attr', 'title')]
    return r


def vector_divide_by(r, a):
    v = r[('result', 'vecvalue')]
    r[('result', 'vecvalue')] = v / a
    r[('attr', 'title')] = r[('attr', 'title')] + " / " + str(a)
    return r


def vector_divtime(r):
    t = r[('result', 'vectime')]
    v = r[('result', 'vecvalue')]
    r[('result', 'vecvalue')] = v / t
    r[('attr', 'title')] = r[('attr', 'title')] + " / t "
    return r


def vector_expression(r, expr):
    t = r[('result', 'vectime')]
    y = r[('result', 'vecvalue')]

    tprev = np.concatenate([np.array([0]), t[:-1]])
    yprev = np.concatenate([np.array([0]), y[:-1]])

    r[('result', 'vecvalue')] = eval(expr)  # TODO - sanitize expr

    r[('attr', 'title')] = r[('attr', 'title')] + ": " + expr
    return r


def _integrate_helper(t, v, interpolation):
    dt = np.concatenate([np.array([0]), t[1:] - t[:-1]])
    vprev = np.concatenate([np.array([0]), v[:-1]])

    if interpolation == 'sample-hold':
        increments = dt * vprev
    elif interpolation == 'backward-sample-hold':
        increments = dt * v
    elif interpolation == 'linear':
        increments = dt * (v + vprev) / 2
    else:
        raise Exception("unknown interpolation")

    return np.cumsum(increments)


def vector_integrate(r, interpolation):
    t = r[('result', 'vectime')]
    v = r[('result', 'vecvalue')]

    r[('result', 'vecvalue')] = _integrate_helper(t, v, interpolation)

    r[('attr', 'title')] = r[('attr', 'title')] + " integrated " + interpolation
    return r


def vector_lineartrend(r, a):
    t = r[('result', 'vectime')]
    v = r[('result', 'vecvalue')]

    r[('result', 'vecvalue')] = v + a * t

    r[('attr', 'title')] = r[('attr', 'title')] + " + " + str(a) + " * t"
    return r


def vector_modulo(r, a):
    v = r[('result', 'vecvalue')]
    r[('result', 'vecvalue')] = np.remainder(v, a)
    r[('attr', 'title')] = r[('attr', 'title')] + " mod " + str(a)
    return r


def vector_movingavg(r, alpha):
    v = r[('result', 'vecvalue')]
    s = pd.Series(v, dtype=np.dtype('f8'))
    r[('result', 'vecvalue')] = s.ewm(alpha=alpha).mean()
    r[('attr', 'title')] = r[('attr', 'title')] + " mean " + str(alpha)
    return r


def vector_multiply_by(r, a):
    v = r[('result', 'vecvalue')]
    r[('result', 'vecvalue')] = v * a
    r[('attr', 'title')] = r[('attr', 'title')] + " * " + str(a)
    return r


def vector_removerepeats(r):
    t = r[('result', 'vectime')]
    v = r[('result', 'vecvalue')]

    is_repeating = v[:-1] == v[1:]
    not_repeating = np.concatenate([[1], 1 - is_repeating])

    r[('result', 'vecvalue')] = np.compress(not_repeating, v)
    r[('result', 'vectime')] = np.compress(not_repeating, t)

    r[('attr', 'title')] = r[('attr', 'title')] + " removerepeats"
    return r


def vector_slidingwinavg(r, window_size):
    v = r[('result', 'vecvalue')]
    s = pd.Series(v, dtype=np.dtype('f8'))
    r[('result', 'vecvalue')] = s.rolling(window_size).mean()
    r[('attr', 'title')] = r[('attr', 'title')] + " windowmean " + str(window_size)
    return r


def vector_subtractfirstval(r):
    v = r[('result', 'vecvalue')]
    r[('result', 'vecvalue')] = v - v[0]
    r[('attr', 'title')] = r[('attr', 'title')] + " - v[0]"
    return r


def vector_timeavg(r, interpolation):
    t = r[('result', 'vectime')]
    v = r[('result', 'vecvalue')]

    integrated = _integrate_helper(t, v, interpolation)

    r[('result', 'vecvalue')] = integrated / t
    r[('attr', 'title')] = r[('attr', 'title')] + " timeavg"
    return r


def vector_timediff(r):
    t = r[('result', 'vectime')]

    r[('result', 'vecvalue')] = np.concatenate([np.array([0]), t[1:] - t[:-1]])

    r[('attr', 'title')] = r[('attr', 'title')] + " timediff"
    return r


def vector_timeshift(r, dt):
    t = r[('result', 'vectime')]

    r[('result', 'vectime')] = t + dt

    r[('attr', 'title')] = r[('attr', 'title')] + " shifted by " + str(dt)
    return r


def vector_timetoserial(r):
    t = r[('result', 'vectime')]

    r[('result', 'vectime')] = np.arange(0, len(t))

    r[('attr', 'title')] = r[('attr', 'title')] + " timetoserial"
    return r


def vector_timewinavg(r, window_size=1):
    t = r[('result', 'vectime')]
    v = r[('result', 'vecvalue')]

    t2 = t / window_size
    bucket = np.floor(t2)

    grouped = pd.Series(v, dtype=np.dtype('f8')).groupby(bucket).mean()

    r[('result', 'vectime')] = grouped.index.values * window_size
    r[('result', 'vecvalue')] = grouped.values

    r[('attr', 'title')] = r[('attr', 'title')] + " timewinavg"
    return r


def vector_winavg(r, window_size=10):
    t = r[('result', 'vectime')]
    v = r[('result', 'vecvalue')]

    t2 = np.arange(0, len(t)) / window_size
    bucket = np.floor(t2)

    grouped = pd.Series(v, dtype=np.dtype('f8')).groupby(bucket).mean()

    r[('result', 'vectime')] = t[::window_size]
    r[('result', 'vecvalue')] = grouped.values

    r[('attr', 'title')] = r[('attr', 'title')] + " timewinavg"
    return r
