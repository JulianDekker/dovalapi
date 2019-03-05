import pandas as pd
import numpy as np
from bokeh.layouts import widgetbox
from bokeh.models import ColumnDataSource, FactorRange
from bokeh.plotting import figure


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
        charts = []
        count = 0
        subplotbox = []
        headers, _ = self.df_rowinfo(dataframe)
        TOOLS = 'save,hover,pan,reset,wheel_zoom,zoom_in,zoom_out,box_zoom'
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
                source = ColumnDataSource(data=dict(X=x, counts=countnum))
                p1 = figure(title="Distribution for {}".format(header), tools=TOOLS, x_range=FactorRange(*x))
                p1.yaxis.axis_label = "Occurrences"
                p1.vbar(x='X', top='counts', width=0.9, source=source)
                p1.y_range.start = 0
                p1.x_range.range_padding = 0.1
                p1.xaxis.major_label_orientation = 1
                p1.xgrid.grid_line_color = None
                if count < 4:
                    subplotbox.append(p1)
                else:
                    charts.append(subplotbox)
                    subplotbox = [p1]
                    count = 0
                count += 1
        charts.append(subplotbox)
        return charts

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

    @staticmethod
    def df_rowinfo(dataframe):
        '''
        Reads the headers / columns of any dataframe and returns the header and columns.
        '''
        headers = list(dataframe.columns)
        columns = list(dataframe.set_index(headers[0]).index)
        return headers, columns
