import pandas as pd
import numpy as np
from bokeh.layouts import widgetbox
from bokeh.models import ColumnDataSource, FactorRange, HoverTool, LinearColorMapper
from bokeh.plotting import figure
from bokeh.palettes import Paired
import dovalapi


class BokehResources:

    def __init__(self, dataframe):
        self.dataframe = dataframe
        self.headers = list(self.dataframe.columns)
        self.columns = list(self.dataframe.set_index(self.headers[0]).index)

    def get_table(self):
        '''
        creates a bokeh table widget from provided dataframe.
        :param dataframe: A pandas dataframe
        :return: data_table: A Bokeh widget
        '''

        from bokeh.models.widgets import DataTable, TableColumn

        source = ColumnDataSource(self.dataframe)
        columns = [TableColumn(field=f, title=f) for f in self.headers]
        data_table = DataTable(source=source, columns=columns, width=1200)

        return data_table

    def explore_data_vis(self, dataframe):
        '''
        Generates 1D bar chart visualisations for every element in the provided pandas dataframe.
        :param dataframe:
        :return: a list of 4 length lists of plots.
        '''
        charts = []
        count = 0
        subplotbox = []
        dataframe = dataframe.dropna(how='all', axis=1)
        headers, _ = self.df_rowinfo(dataframe)
        TOOLS = 'save,pan,reset,wheel_zoom,zoom_in,zoom_out,box_zoom'
        for header in headers:
            if dataframe[header].dtype == 'object' or dataframe[header].dtype == bool:  # String data
                counts = dataframe[header].value_counts()
                x = [(header, str(count)) for count in counts.keys()]
                numbers = [numb for numb in counts]
                source = ColumnDataSource(data=dict(x=x, counts=numbers))
                p = figure(x_range=FactorRange(*x), title="Distribution for {}".format(header),
                           tools=TOOLS, sizing_mode="scale_both")
                p.yaxis.axis_label = "Occurrences"
                p.vbar(x='x', top='counts', width=0.9, source=source)
                p.y_range.start = 0
                p.x_range.range_padding = 0.1
                p.xaxis.major_label_orientation = 1
                p.xgrid.grid_line_color = None
                p.add_tools(self.default_hovertool(header, 'x', 'Occurrences', 'counts'))
                if count < 4:
                    subplotbox.append(p)
                else:
                    charts.append(subplotbox)
                    subplotbox = [p]
                    count = 0
                count += 1
            elif dataframe[header].dtype == 'float64' or dataframe[header].dtype == 'int64':
                idxsort = dataframe[header].value_counts().sort_index()
                bins = np.round(len(idxsort) / 10)
                if bins < 10:
                    bins = 10
                gsort = idxsort.groupby(pd.cut(idxsort.index, bins=bins))
                distribution = gsort.describe()['count']
                x = [str(g) for g in distribution.keys()]
                countnum = [num for num in distribution]
                source = ColumnDataSource(data=dict(x=x, counts=countnum))
                p1 = figure(title="Distribution for {}".format(header), tools=TOOLS, x_range=FactorRange(*x))
                p1.yaxis.axis_label = "Occurrences"
                p1.vbar(x='x', top='counts', width=0.9, source=source)
                p1.y_range.start = 0
                p1.x_range.range_padding = 0.1
                p1.xaxis.major_label_orientation = 1
                p1.xgrid.grid_line_color = None
                p1.add_tools(self.default_hovertool(header, 'x', 'Occurrences', 'counts'))
                if count < 4:
                    subplotbox.append(p1)
                else:
                    charts.append(subplotbox)
                    subplotbox = [p1]
                    count = 0
                count += 1
        charts.append(subplotbox)
        return charts

    def colorgen(self, colors):
        num = 0
        while num < len(colors):
            color = colors[num]
            print(color)
            yield color
            num = num + 1

    def make_boxplot(self, quant1, quant2, quant3, upper, lower, outx, outy, colors):
        xranges = quant2.index.tolist()
        p = figure(background_fill_color="#efefef", x_range=xranges, toolbar_location='above')
        p.segment(xranges, upper.score, xranges, quant3.score, line_color="black")
        p.segment(xranges, lower.score, xranges, quant1.score, line_color="black")
        p.vbar(xranges, 0.7, quant2.score, quant3.score, fill_color=colors.topcolor, line_color="black")
        p.vbar(xranges, 0.7, quant1.score, quant2.score, fill_color=colors.botcolor, line_color="black")
        p.rect(xranges, lower.score, 0.2, 0.01, line_color="black")
        p.rect(xranges, upper.score, 0.2, 0.01, line_color="black")
        if len(outx) > 0:
            p.circle(outx, outy, size=6, color='#9ecae1', fill_alpha=0.6)
        p.xaxis.major_label_orientation = 1
        p.legend.location = 'top_right'
        return p

    def pivotboxplot(self, dataframe, features, rettable=False):
        if len(features) > 1:
            du = dovalapi.utils()
            pivottable = du.pivottable(dataframe, features)
            q1 = pivottable['quant1']
            q2 = pivottable['median']
            q3 = pivottable['quant3']
            iqr = q3 - q1
            upper = q3 + 1.5 * iqr
            lower = q1 - 1.5 * iqr

            downoutliers = []
            upoutliers = []
            lowerdf = pd.DataFrame()
            upperdf = pd.DataFrame()
            quant3 = pd.DataFrame()
            quant2 = pd.DataFrame()
            quant1 = pd.DataFrame()
            colors = pd.DataFrame()
            outx = []
            outy = []

            smallerdf = dataframe[features]

            for iclas, clas in enumerate(lower):
                for iindex, index in enumerate(lower.index):
                    data6 = smallerdf[smallerdf[features[1]] == clas]
                    data7 = lower[clas]
                    for i in range(len(index)):
                        if len(features) > 3:
                            data6 = data6[data6[features[i + 2]] == index[i]]
                        elif len(features) > 2:
                            data6 = data6[data6[features[2]] == index]
                    if iclas > 11:
                        iclas = iclas % 11
                    iindex = iindex + len(lower)+1
                    if iindex > 11:
                        iindex = iindex % 11
                    lowerdf = lowerdf.append(pd.Series({'score': data7.loc[index]}, name='{} {}'.format(clas, index)))
                    quant3 = quant3.append(pd.Series({'score': q3[clas].loc[index]}, name='{} {}'.format(clas, index)))
                    quant2 = quant2.append(pd.Series({'score': q2[clas].loc[index]}, name='{} {}'.format(clas, index)))
                    quant1 = quant1.append(pd.Series({'score': q1[clas].loc[index]}, name='{} {}'.format(clas, index)))
                    colors = colors.append(pd.Series({'topcolor': Paired[12][iindex], 'botcolor': Paired[12][iclas]}, name='{} {}'.format(clas, index)))
                    downoutliers.append(data6[features[0]].where(data6[features[0]] < data7.loc[index]).dropna())
                    if len(data6[features[0]].where(data6[features[0]] < data7.loc[index]).dropna()) > 0:
                        for key in data6[features[0]].where(data6[features[0]] < data7.loc[index]).dropna():
                            outx.append('{} {}'.format(clas, index))
                            outy.append(key)
            for clas in upper:
                for index in upper.index:
                    data6 = smallerdf[smallerdf[features[1]] == clas]
                    data7 = upper[clas]
                    for i in range(len(index)):
                        if len(features) > 3:
                            data6 = data6[data6[features[i + 2]] == index[i]]
                        elif len(features) > 2:
                            data6 = data6[data6[features[2]] == index]
                    upperdf = upperdf.append(pd.Series({'score': data7.loc[index]}, name='{} {}'.format(clas, index)))
                    upoutliers.append(data6[features[0]].where(data6[features[0]] > data7.loc[index]).dropna())
                    if len(data6[features[0]].where(data6[features[0]] > data7.loc[index]).dropna()) > 0:
                        for key in data6[features[0]].where(data6[features[0]] > data7.loc[index]).dropna():
                            outx.append('{} {}'.format(clas, index))
                            outy.append(key)
            if rettable is True:
                return self.make_boxplot(quant1, quant2, quant3, upperdf, lowerdf, outx, outy, colors), pivottable
            return self.make_boxplot(quant1, quant2, quant3, upperdf, lowerdf, outx, outy, colors)
        return figure(background_fill_color="#efefef", toolbar_location='above')

    def multi_pivotboxplot(self, dataframe, features):
        boxplots = []
        if len(features) > 0:
            du = dovalapi.utils()
            print('features inside: ', du.limitedsubselect(features))
            for feature in du.limitedsubselect(features):
                boxplots.append(self.pivotboxplot(dataframe, feature))
            print('boxplots: ', boxplots)
        return boxplots

    def get_headers(self):
        return self.headers

    def get_columns(self):
        return self.columns

    @staticmethod
    def components_web(plot):
        '''
        Generates html components for web display.
        :param plot: A bokeh plot
        :return: script: A html <script> tag with render javascript, div a <div> tag with html to display a bokeh plot,
        resources: A <script> tag with javascript to render bokeh plots.
        '''

        from bokeh.resources import CDN
        from bokeh.embed import components

        script, div = components(plot, CDN)

        return script, div

    @staticmethod
    def bokeh_web_resources():
        '''
        generates bokeh resources for web viewing
        :return:
        '''
        from bokeh.resources import INLINE
        return INLINE.render()

    def default_hovertool(self, x1, x2, y1, y2):
        '''
        Creates the default hovertool for plots
        :param x1: first string
        :param x2: first reference
        :param y1: second string
        :param y2: second reference
        :return: hovertool
        '''
        hover = HoverTool(
            tooltips=[
                (x1+' ', '@'+x2),
                (y1+' ', '@'+y2),
            ],
            mode='vline'
        )
        return hover

    @staticmethod
    def df_rowinfo(dataframe):
        '''
        Reads the headers / columns of any dataframe and returns the header and columns.
        '''
        headers = list(dataframe.columns)
        #print(headers)
        columns = list(dataframe.set_index(headers[0]).index)
        return headers, columns
