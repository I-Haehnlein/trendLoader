from customtkinter import CTk, CTkButton, CTkRadioButton, CTkTextbox, CTkLabel, CTkFrame, CTkCheckBox
from tkinter import LEFT, Text, BOTH, BooleanVar
from utils import FileSelection, Plotter
from os.path import basename, dirname, exists
from pandas import read_csv

class App():
    app = CTk()
    fSelect = FileSelection()
    runName = ''
    unifiedHover:BooleanVar = BooleanVar(app,True,"unifiedHoverState")

    frameSelectedFile = CTkFrame(app)
    frameSelectedDir = CTkFrame(app)
    tbSelectedFile = CTkTextbox(frameSelectedFile, width = 200, height = 25)
    tbSelectedDir = CTkTextbox(frameSelectedDir, width = 200, height = 25)
    lbSelectedFile = CTkLabel(frameSelectedFile,text='Selected File:', width = 70, height=25)
    lbSelectedDir = CTkLabel(frameSelectedDir,text='Selected Directory:', width = 70, height=25)
    frameSave = CTkFrame(app)

    def __init__(self) -> None:
        try:
            icon = 'GP_Plasma_StackedOrg.ico'
            if exists(icon):
                self.app.iconbitmap('GP_Plasma_StackedOrg.ico')
            else:
                self.app.iconbitmap('_internal\\'+icon)
        except Exception as e:
            print(e)
        self.app.title('Siemens Trend Export Plotter')
        self.app.resizable(True,True)
        self.app.geometry('400x400')

        self.open_button = CTkButton(
            self.app,
            text = 'Select Trend File',
            command = self.open_file
        )
        self.btnPlotFile = CTkButton(self.app, text='PlotData', state='disabled', command = self.plot_selected_file)
        self.btnSaveInteractive = CTkButton(self.frameSave, text = 'Save Interactive', state = 'disabled', command = self.saveInteractive)
        self.btnSavePng = CTkButton(self.frameSave, text = 'Save PNG', state = 'disabled', command = self.savePng)
        self.cbSelectHoverMode = CTkCheckBox(self.app, text = "Unified Marker Display", variable=self.unifiedHover)

        padX = 5
        padY = 5
        anchor = 'center'
        self.open_button.pack(anchor=anchor, expand=True, fill=BOTH, padx=padX*2, pady=padY)
        self.frameSelectedDir.pack(anchor=anchor, expand=True, fill=BOTH, padx=padX, pady=padY)
        self.frameSelectedFile.pack(anchor=anchor, expand=True, fill=BOTH, padx=padX, pady=padY)
        self.lbSelectedFile.pack(padx=padX, pady=padY, anchor=anchor, expand=False, fill=BOTH, side=LEFT)
        self.lbSelectedDir.pack(padx=padX, pady=padY, anchor=anchor, expand=False, fill=BOTH, side=LEFT)
        self.tbSelectedFile.pack(padx=padX, pady=padY, anchor=anchor, expand=True, fill=BOTH, side=LEFT)
        self.tbSelectedDir.pack(padx=padX, pady=padY, anchor=anchor, expand=True, fill=BOTH, side=LEFT)

        self.cbSelectHoverMode.pack(anchor=anchor)
        self.btnPlotFile.pack(anchor=anchor, expand=True, fill=BOTH, padx=padX*2, pady=padY)
        self.frameSave.pack(anchor=anchor, expand=True, fill=BOTH, padx=padX, pady=padY)
        self.btnSaveInteractive.pack(anchor=anchor, padx=padX, pady=padY, expand=True, fill=BOTH, side=LEFT)
        self.btnSavePng.pack(anchor=anchor, padx=padX, pady=padY, expand=True, fill=BOTH, side=LEFT)

    
    def open_file(self):
        fName = self.fSelect.select_file()
        self.runName = basename(self.fSelect.filename.rstrip('.csv'))
        self.btnPlotFile.configure(state='normal')
        self.tbSelectedFile.configure(require_redraw=False,state='normal')
        self.tbSelectedFile.delete('0.0','end')
        self.tbSelectedFile.insert('0.0',basename(fName))
        self.tbSelectedFile.configure(require_redraw=False,state='disabled')
        self.tbSelectedDir.configure(require_redraw=False,state='normal')
        self.tbSelectedDir.delete('0.0','end')
        self.tbSelectedDir.insert('0.0',dirname(fName))
        self.tbSelectedDir.configure(require_redraw=False,state='disabled')
        pass

    def plot_selected_file(self):
        self.plotter = Plotter(basename(self.fSelect.filename.rstrip('.csv')),self.unifiedHover.get())
        sysData = read_csv(self.fSelect.filename, delimiter=';')
        self.plotter.plotData_siemensTrendExport(sysData)
        self.plotter.fig.show()
        self.btnSaveInteractive.configure(state='noraml')
        self.btnSavePng.configure(state='noraml')
        pass

    def saveInteractive(self):
        saveFile = FileSelection()
        saveFile.select_save(fType='.html',defaultFile=self.runName)
        self.plotter.fig.write_html(file=saveFile.filename, include_plotlyjs=True)
        pass

    def savePng(self):
        saveFile = FileSelection()
        saveFile.select_save(fType='.png',defaultFile=self.runName)
        self.plotter.fig.write_image(file=saveFile.filename, format='png',width=1600, height=900)
        pass

plotter = App()
plotter.app.mainloop()