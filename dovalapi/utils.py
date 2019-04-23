import re
import pandas as pd
import numpy as np
from decimal import *


class NAN(object):
    def __eq__(self, v):
        return np.isnan(v)

    def __hash__(self):
        return hash(np.nan)

    def __repr__(self):
        return 'NaN'


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
        elif re.search('(.+;.+)+', first_line):
            return ';'
        return None

    @staticmethod
    def get_nominal_values(dataframe, feature):
        '''
        lists the unique values of a feature in the dataframe.
        '''
        return df[feature].unique()

    @staticmethod
    def subset_partialselect(dataframe, restrictions):
        '''
        subsets a dataframe with a list of restrictions, then returns dataframe.
        '''
        nan = NAN()
        print(restrictions)
        def checkvals(val):
            print('restr', restrictions[val])
            for i, key in enumerate(restrictions[val]):
                if key == 'NA':
                    restrictions[val][i] = nan
                    return restrictions[val]
                if key == 'true' or key == 'false':
                    restrictions[val][i] = (restrictions[val][i] in ['true'])
            print(restrictions[val])
            return restrictions[val]

        for restr in restrictions:
            restrictions[restr] = checkvals(restr)
            dataframe = dataframe[dataframe[restr].isin(restrictions[restr])]
        return dataframe

    def subset_full(self, dataframe, indexes, restrictions):
        if len(indexes) > 0:
            dataframe = dataframe.set_index(dataframe.columns[0])
            dataframe = dataframe.loc[indexes, :]
            dataframe = dataframe.reset_index()
        if len(restrictions) > 0:
            dataframe = self.subset_partialselect(dataframe, restrictions)
        return dataframe

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
        for feat in features:
            if str(dataframe[feat].dtype).startswith('int'):
                if len(df[feat].unique()) <= 3:
                    df[feat] = df[feat].apply(lambda x: self.boolify(x))
        print(df)
        fill = df[features[1::]].fillna('NA')
        df = pd.DataFrame(df[features[0]]).join(fill)
        agg = df.groupby(features[1::]).agg('count')
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
                        html.append("<div class='group-item'><div class='group-left'>" + str(item) + "</div><div class='group-right'>" + str(
                            agg[features[0]][levelindexes[levelindex]].sum()) + "</div></div>")
                    except:
                        html.append(
                            "<div class='group-item'><div class='group-left'>" + str(item) + "</div><div class='group-right'>" + str(
                                0) + "</div></div>")
                    ind = get_next_ind(level)
                    if (ind is not None):
                        try:
                            calc_level(ind, start=False, levelindex=levelindexes[levelindex])
                        except IndexError:
                            continue
                else:
                    html.append(
                        "<div class='group-item'><div class='group-left'>" + str(item) + "</div><div class='group-right'>" + str(
                            agg[features[0]][group[levelindex]].sum()) + "</div></div>")
            unset = grouplen - total
            if start:
                html.append("<div class='group-bottom'><div class='group-left'>Filled datapoints</div><div class='group-right'>" + str(total) +
                            "</div></div><div class='group-bottom'><div class='group-left'>Missing datapoints</div><div class='group-right'>" + str(unset) +
                            "</div></div><div class='group-bottom'><div class='group-left'>Total datapoints</div><div class='group-right'>" + str(grouplen) +
                            "</div></div> </div></div>")
            else:
                html.append('</div>')

        if len(features) == 2:
            calc_level(index)
        else:
            calc_level(index.levels[0])

        return ''.join(html)

    @staticmethod
    def boolify(bool):
        if bool in [1, 0, '1', '0', 'yes', 'no', 'true', 'false', True, False]:
            return bool in [1, '1', 'yes', 'true', True]
        return bool

    @staticmethod
    def limitedsubselect(features, limit=4):
        '''
        generates multiple lists of features of limit length from one list. The first 3 features are the same and the
        4th feature unique.
        :param features:
        :param limit:
        :return:
        '''
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
