import os, shutil, tempfile
import dovalapi
from IPython.display import IFrame
from ipywidgets import Layout
import json

class plotcanvas:
    def __init__(self, dataset, parameters, plottype='boxplot', additionalconfig={}):
        self.dataset = dataset
        self.keys = parameters
        self.type = plottype.lower()
        self.additionalconfig = additionalconfig
        self.supportedplots = ['boxplot', 'scatter', 'scatter2d', 'scatter3d', 'heatmap']
        self.filename = str(self.__repr__)[-18:-1]+'.html'
        self.plot_canvas()

    def plot_canvas(self):
        if len(self.dataset) == 0 or len(self.keys) == 0:
            print("The input dataset or input parameters are empty.")
            return
        self.clean_inputs()
        handle, path = tempfile.mkstemp()
        self.prepare_workspace()
        open('canvasplots/'+self.filename, 'w')
        with open('canvasplots/'+self.filename, 'a') as f:
            f.write("<head>"
                    "<script src='https://code.jquery.com/jquery-3.4.0.min.js'></script>"
                    "<script type=\"text/javascript\" src=\"https://canvasxpress.org/js/canvasXpress.min.js\"></script>"
                    "<link rel=\"stylesheet\" href=\"https://canvasxpress.org/css/canvasXpress.css\" type=\"text/css\">"
                    "</head>"
                    "<body>"
                    "<canvas id='canvas' responsive='true' width=200 height=200></canvas>"
                    "<script>"
                    "x = new CanvasXpress('canvas', {y: "+self.make_y()+", x: "+self.make_x()+", z: "+self.make_z()+"}, "+self.make_styles()+", false);x.clickGraphMaxMin();"
                    "</script>"
                    "</body>")
        return display(IFrame('canvasplots/'+self.filename, width=700, height=500, layout=Layout(width='50%', height="500px")))

    def make_y(self):
        datas = self.dataset.set_index(self.dataset.columns[0])
        data = []
        for key in self.keys:
            data.append(list(datas[key]))
        samps = {
            "smps": list(datas.index),
            "data": data,
            "vars": self.keys,
        }
        if self.type == 'Scatter2D' or self.type == 'Scatter3D':
            samps = {
                "smps": self.keys,
                "data": self.dataset[self.keys].to_dict('split')['data'],
                "vars": list(datas.index),
            }
        return json.dumps(samps)

    def make_x(self):
        annot = {}
        annotkeys = [col for col in list(self.dataset.columns) if col not in self.keys]
        annotframe = self.dataset[annotkeys].copy()
        x = []
        [x.append('No group') for _ in range(len(annotframe))]
        annot['No group'] = x
        for key in annotkeys:
            annot[key] = list(annotframe[key])
        if self.type == 'Scatter2D' or self.type == 'Scatter3D':
            annot = {}
        return json.dumps(annot)

    def make_z(self):
        zannot = None
        if self.type == 'Scatter2D' or self.type == 'Scatter3D':
            zannot = {}
            datas = self.dataset.set_index(self.dataset.columns[0])
            annotkeys = [col for col in list(datas.columns) if col not in self.keys]
            for key in annotkeys:
                zannot[key] = list(datas[key])
        return json.dumps(zannot)

    def make_styles(self):
        typestyles = {}
        styles = {
          "axisAlgorithm": "rPretty",
          "axisTickScaleFontFactor": 1.0,
          "axisTitleFontStyle": "bold",
          "axisTitleScaleFontFactor": 1.0,
          "background": "white",
          "backgroundType": "window",
          "backgroundWindow": "#E5E5E5",
          "barLollipopOpen": False,
          "colorScheme": "cx",
          "confidenceIntervalColor": "rgb(50,50,50)",
          "fitLineStyle": "solid",
          "guides": "solid",
          "guidesColor": "white",
          "layoutConfig": [],
          "saveFilename": True,
          "showLegend": True,
          "smpLabelRotate": 45,
          "smpLabelScaleFontFactor": 1.8,
          "smpTitleFontStyle": "bold",
          "smpTitleScaleFontFactor": 1.8,
          "standardDeviationType": "unbiased",
          "swimHigh": False,
          "xAxis2Show": False,
          "xAxisMinorTicks": False,
          "xAxisTickColor": "white",
          "showDataTable": False,
          "lineThickness": 1.5,
          "maxCols": 5,
          "maxRows": 20,
          "graphOrientation": "vertical",
          "adjustAspectRatio": True,
          "graphType": self.type,
        }
        if self.type == 'Boxplot':
            typestyles = {
                "summaryType": "iqr",
                "groupingFactors": ["No group"]
            }
        elif self.type == 'Scatter2D' or self.type == 'Scatter3D':
            typestyles = {
                "summaryType": "raw",
                "smpLabelRotate": 0
            }
        elif self.type == 'Heatmap':
            typestyles = {
                "summaryType": "raw",
                "heatmapIndicatorHeight": 60,
                "heatmapIndicatorHistogram": True,
                "showHeatmapIndicator": True,
                "smpLabelRotate": 0
            }
        styles.update(typestyles)
        if len(self.additionalconfig) > 0:
            styles.update(self.additionalconfig)
        return json.dumps(styles)

    def clean_inputs(self):
        if self.type in self.supportedplots:
            if (self.type == 'scatter2d' or self.type == 'scatter3d' or self.type == 'scatter') and len(self.keys) >= 3:
                self.keys = self.keys[0:3]
            if self.type == 'scatter':
                if len(self.keys) == 2:
                    self.type = 'Scatter2D'
                elif len(self.keys) == 3:
                    self.type = 'Scatter3D'
            if self.type == 'scatter3d':
                self.type = 'Scatter3D'
            if self.type == 'boxplot':
                self.type = 'Boxplot'
            if self.type == 'heatmap':
                self.type = 'Heatmap'
        else:
            self.type = self.type.capitalize()

    def prepare_workspace(self):
        try:
            shutil.rmtree(os.path.join(os.path.curdir, 'canvasplots'))
        except:
            pass
        finally:
            try:
                os.mkdir(os.path.join(os.path.curdir, 'canvasplots'))
            except:
                pass
