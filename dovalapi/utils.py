import re
import pandas as pd
import numpy as np
from decimal import *


class utils:

    def __init__(self):
        pass

    @staticmethod
    def check_sep(file):
        '''
        searches the first line for the seperator type.
        :param file:
        :return: seperator type
        '''
        with open(file) as f:
            first_line = f.readline()
        if re.search('(.+\t.+)+', first_line):
            return '\t'
        elif re.search('(.+,.+)+', first_line):
            return ','
        elif re.search('(.+ .+)+', first_line):
            return '\\s'
        return None

    @staticmethod
    def categorise_intdata(dataframe, column):
        '''
        Divides Integer data into a minumum of 5 groups. Number of groups to devide into is number of unique values/10
        :param dataframe:
        :param column:
        :return:
        '''
        uniqlen = len(dataframe[column].value_counts().sort_index())
        bins = int(np.round(uniqlen / 10))
        if bins < 10:
            bins = 10
        getcontext().prec = 4
        bins = pd.cut(dataframe[column], bins=bins, retbins=True)

        def catstring(interval):
            string = str(column) + ' ' + str(interval.left) + '-' + str(interval.right)
            return string
        dataframe[column + '_cat'] = bins[0].apply(catstring)
        return dataframe

    def pivottable(self, dataframe, features, aggfun=[], delna=False):
        '''
        Generates a pivot-table from a provided list of features, first value is the measured value.
        :param dataframe:
        :param features:
        :param aggfun:
        :param delna:
        :return:
        '''
        def quant0(values):
            if values.dtype == 'int64' or values.dtype == 'float64':
                q00 = np.nanpercentile(values, 0)
                return q00
            return values

        def quant1(values):
            if values.dtype == 'int64' or values.dtype == 'float64':
                q11 = np.nanpercentile(values, 25)
                return q11
            return values

        def quant3(values):
            if values.dtype == 'int64' or values.dtype == 'float64':
                q33 = np.nanpercentile(values, 75)
                return q33
            return values

        def quant4(values):
            if values.dtype == 'int64' or values.dtype == 'float64':
                q44 = np.nanpercentile(values, 100)
                return q44
            return values

        for feature in features:
            try:
                del features[features.index(feature+'_cat')]
                dataframe.drop(column=feature+'_cat')
            except:
                pass

        if len(aggfun) is 0:
            aggfun = [np.mean, 'count', 'min', 'max', np.std, quant0, quant1, np.median, quant3, quant4]
        for i, feature in enumerate(features):
            if (dataframe[feature].dtype == 'int64' or dataframe[feature].dtype == 'float64') and i > 0:
                dataframe = self.categorise_intdata(dataframe, feature)
                features[i] += '_cat'
        rest = []
        if len(features) > 2:
            rest = pd.Series(features)[2:].tolist()
        pivottable = pd.pivot_table(dataframe, values=features[0], columns=features[1], index=rest, dropna=delna,
                                    aggfunc=aggfun)
        return pivottable
