from pprint import pprint
from customtkinter import CTkTextbox
from tkinter import filedialog
from plotly.graph_objects import Figure, Scatter, Table
from plotly.subplots import make_subplots
import plotly.express as px
import plotly.io as pio
from pandas import DataFrame

class FileSelection():
    filename:str = ''

    def select_file(self,fType:str='.csv',defaultFile=''):
        match fType:
            case '.csv': filetypes = [('Comma Separated Values', '*.csv')]
            case '.html': filetypes = [('Interactive Plot', '*.html')]
            case '.png': filetypes = [('Portable Network Graphic', '*.png')]
            case _: filetypes = [('All Files', '*')]

        filename = filedialog.askopenfilename(
            title = 'Select trend export file',
            initialdir = 'C:/',
            filetypes=filetypes,
            initialfile=defaultFile  
        )
        self.filename = filename
        return filename
    
    def select_save(self,fType:str='.html',defaultFile=''):
        match fType:
            case '.csv': filetypes = [('Comma Separated Values', '*.csv')]
            case '.html': filetypes = [('Interactive Plot', '*.html')]
            case '.png': filetypes = [('Portable Network Graphic', '*.png')]
            case _: filetypes = [('All Files', '*')]

        filename = filedialog.asksaveasfilename(defaultextension=fType, filetypes=filetypes, initialfile=defaultFile)
        self.filename = filename
        return filename

        
    
class Plotter():
    fig:Figure
    colorMap:list[str] = px.colors.qualitative.Light24
    pressuresList: list[str] = []
    processTrends: list[str] = []
    config:dict = {}

    def __init__(self,runName:str, withHoverUnified:bool = True) -> None:
        h_space = 0.05
        v_space = 0.05
        widths = []
        self.fig = make_subplots(
            rows=2,
            cols=1,
            vertical_spacing=v_space,
            horizontal_spacing=h_space,
            specs= [
                [{"secondary_y":False}],
                [{"secondary_y":False}]
            ],
            subplot_titles=(
                'System Pressures',
                'Process Trends'
            ),
            shared_xaxes=True
        )
        self.fig.update_yaxes(row=1,col=1, type='log', tickformat='0.0e', title_text='Pressure [mTorr]', minor=dict(showgrid=True), tickmode='array', tickvals=[1e-6,1e-5,1e-4,1e-3,1e-2,1e-1,1,1e1,1e2])
        self.fig.update_xaxes(row=1,col=1, nticks = 20)
        self.fig.update_yaxes(row=2,col=1, type='linear', title_text='Trends')
        self.fig.update_xaxes(
            row=2,
            col=1,
            title_text='Time Stamp',
            tickangle = 360-45,
            nticks = 20
        )
        if withHoverUnified:
            hovermode = "x unified"
        else:
            hovermode = "closest"
        self.fig.update_layout(
            title = dict(text=runName),
            margin = dict(l=10,r=10,t=50,b=10),
            template = 'plotly_dark',
            hovermode = hovermode
        )

    def addPlotTrace(self, data:DataFrame, dataKey:str, lineColor:str, lineDash:str='solid', row:int=1, col:int=1, secondary_y:bool=False,log_y:bool=False):
        if secondary_y:
            label = dataKey + ' (right)'
        else:
            label = dataKey

        if log_y:
            htemp = "%{y:0.3e}"
        else:
            htemp = "%{y:0.2f}"
        self.fig.add_trace(
            Scatter(
                x = data[self.config[dataKey]['x']],
                y = data[self.config[dataKey]['y']],
                line_color = lineColor,
                line_dash = lineDash,
                name = f'{label}',
                hovertemplate=htemp
            ),
            row = row,
            col = col,
            secondary_y = secondary_y
        )
        pass

    def plotData_siemensTrendExport(self, data:DataFrame):
        dataKeys = self.sortKeys_siemensTrendExport(data.columns.to_list())
        colorIteration = 0
        lineIteration = 0
        for tag in self.config:
            if tag in self.pressuresList:
                rowSet = 1
                colSet = 1
                log_y = True
            elif tag in self.processTrends:
                rowSet = 2
                colSet = 1
                log_y = False
            else:
                break

            color = self.colorMap[colorIteration%len(self.colorMap)]
            if colorIteration%len(self.colorMap) == len(self.colorMap):
                lineIteration += 1
            
            match lineIteration:
                case 0: dash = 'solid'
                case 1: dash = 'dash'
                case 2: dash = 'dashdot'
                case 3: dash = 'longdash'
                case 4: dash = 'longdashdot'
                case _: dash = 'dot'

            self.addPlotTrace(
                data = data,
                dataKey = tag,
                lineColor = color,
                lineDash = dash,
                row = rowSet,
                col = colSet,
                log_y=log_y
            )
            colorIteration += 1

    def sortKeys_siemensTrendExport(self, columns:list[str]):
        allkeys = []
        pprint(columns)
        for key in columns:
            if 'Time' not in key:
                tag = key.replace('Y value','').rstrip()
                if 'Gauge' in key:
                    self.pressuresList.append(tag)
                else:
                    self.processTrends.append(tag)
                allkeys.append(tag)
                self.config.update(
                    {
                        tag:{
                            'x': tag + ' Time',
                            'y': key
                        }
                    }
                )
        print(allkeys)
        pprint(self.config)
        return allkeys
