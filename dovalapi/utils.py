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

    def hierarchical_pivottable(self, dataframe, features):
        """
        Creates a hierarchical pivot table html strucuture. Recursively calculates the amounts of datapoints in each level
        of pivot.
        :param dataframe:
        :param features:
        :return:
        """
        df = dataframe[features]
        agg = df.groupby(features[1:]).agg('count')
        index = agg.index
        grouplen = len(df)
        html = []

        #for i, feature in enumerate(features):
        #    if (dataframe[feature].dtype == 'int64' or dataframe[feature].dtype == 'float64') and i > 0:
        #        dataframe = self.categorise_intdata(dataframe, feature)
        #        features[i] += '_cat'

        def get_next_ind(level):
            for i, _ in enumerate(index.levels):
                if index.levels[i] is level:
                    ind = i
                    if (ind < len(index.levels)):
                        try:
                            return index.levels[ind + 1]
                        except IndexError:
                            return None
            return None

        def calc_level(level, start=True, levelindex=()):
            total = 0
            group = []
            levelindexes = []
            for i in level:
                levelsindex = levelindex + (i,)
                levelindexes.append(levelsindex)
                group.append(i)
                if len(features) > 2:
                    try:
                        total += agg[features[0]][levelsindex].sum()
                    except:
                        continue
                else:
                    total += agg[features[0]][i]
            html.append("<div class='cat-group'><div class='group-title'>" + level.name + "</div>")
            for levelindex, item in enumerate(group):
                if len(features) > 2:
                    try:
                        html.append("<div class='group-item'><div class='group-left'>" + item + "</div><div class='group-right'>" + str(
                            agg[features[0]][levelindexes[levelindex]].sum()) + "</div></div>")
                    except:
                        html.append(
                            "<div class='group-item'><div class='group-left'>" + item + "</div><div class='group-right'>" + str(
                                0) + "</div></div>")
                    ind = get_next_ind(level)
                    if (ind is not None):
                        try:
                            calc_level(ind, start=False, levelindex=levelindexes[levelindex])
                        except IndexError:
                            continue
                else:
                    html.append(
                        "<div class='group-item'><div class='group-left'>" + item + "</div><div class='group-right'>" + str(
                            agg[features[0]][group[levelindex]].sum()) + "</div></div>")
            unset = grouplen - total
            if start:
                html.append("<div class='group-item'><div class='group-left'>No Value</div><div class='group-right'>" + str(unset) + "</div></div></div>")
            else:
                html.append('</div>')

        if len(features) == 2:
            calc_level(index)
        else:
            calc_level(index.levels[0])

        return ''.join(html)

    @staticmethod
    def limitedsubselect(features, limit=4):
        selections = []
        if len(features) > limit:
            print('in', features)
            for i in range(len(features) - limit):
                feat = features[0:3]
                feat.append(features[limit+i])
                print('what happend?', feat)
                selections.append(feat)
            return selections
        print('We need to go deeper!', features)
        return [features]
