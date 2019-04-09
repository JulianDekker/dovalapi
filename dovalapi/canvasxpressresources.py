import pandas as pd
import numpy as np
from IPython.display import display, HTML


class CanvasxpressResources:
    def __init__(self, dataframe):
        pass

    @staticmethod
    def jupyterembed(df, key): #failed
        key = "'{}'".format(key)
        df = df.to_json(orient='split')
        tag = "<script src='https://canvasxpress.org/js/canvasXpress.min.js'></script>" \
              "<link rel='stylesheet' href='https://canvasxpress.org/css/canvasXpress.css' >"
        tag += "<script>\r\nvar obj = %s;\r\n var key = %s;\r\n    const arrayColumne = (arr, n) => arr.map(x => x[n]);\r\n    function create_annotations(obj){\r\n        xobj = {}\r\n        for (i in obj.columns){\r\n            xobj[obj.columns[i]] = arrayColumne(obj.data, i)\r\n        }\r\n        xobj[\"No group\"] = Array(obj.data.length).fill(\"No group\")\r\n        return xobj\r\n    }\r\n    annotations = create_annotations(obj)\r\n    new CanvasXpress(\"canvas\", {\r\n      y: {\r\n        smps:\r\n            obj.index\r\n        ,\r\n        data: [\r\n          arrayColumne(obj.data, obj.columns.indexOf(key))\r\n        ],\r\n        vars: [\r\n          key\r\n        ]\r\n      },\r\n      x: annotations\r\n    }, {\r\n      axisAlgorithm: \"rPretty\",\r\n      axisTickScaleFontFactor: 1.8,\r\n      axisTitleFontStyle: \"bold\",\r\n      axisTitleScaleFontFactor: 1.8,\r\n      background: \"white\",\r\n      backgroundType: \"window\",\r\n      backgroundWindow: \"#E5E5E5\",\r\n      barLollipopOpen: false,\r\n      colorScheme: \"Economist\",\r\n      confidenceIntervalColor: \"rgb(50,50,50)\",\r\n      fitLineStyle: \"solid\",\r\n      graphOrientation: \"vertical\",\r\n      graphType: \"Boxplot\",\r\n      groupingFactors: [\r\n        \"No group\"\r\n      ],\r\n      guides: \"solid\",\r\n      guidesColor: \"white\",\r\n      \"layoutConfig\": [],\r\n      saveFilename: false,\r\n      showLegend: false,\r\n      smpLabelRotate: 90,\r\n      smpLabelScaleFontFactor: 1.8,\r\n      smpTitle: obj.name,\r\n      smpTitleFontStyle: \"bold\",\r\n      smpTitleScaleFontFactor: 1.8,\r\n      standardDeviationType: \"unbiased\",\r\n      summaryType: \"iqr\",\r\n      swimHigh: false,\r\n      title: `Graphtype of ${key}`,\r\n      xAxis2Show: false,\r\n      xAxisMinorTicks: false,\r\n      xAxisTickColor: \"white\",\r\n    }, false);</script>" % (df, key)
        return display(HTML(tag))
