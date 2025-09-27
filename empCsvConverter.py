#!venv/bin/python3
from pprint import pprint
from customtkinter import CTk, CTkButton, CTkRadioButton, CTkTextbox, CTkLabel, CTkFrame, CTkCheckBox, CTkComboBox
import customtkinter
from tkinter import LEFT, IntVar, PhotoImage, Text, BOTH, BooleanVar, StringVar
from utils import FileSelection, Plotter, EmperionCsvConverter
from os.path import basename, dirname, exists
import os
from pandas import read_csv
from pytz import common_timezones
from tzlocal import get_localzone_name
from glob import glob
from time import time

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("green")

class Converter():
    app = CTk()
    fSelect = FileSelection()
    localTz:str = get_localzone_name()
    timezone:StringVar = StringVar(app,value=localTz)
    # Deafults to linux
    strVarFileDir:StringVar = StringVar(app,value='./',name='fileDir')
    fileSep:str = '/'
    fileDirectory:str = './'
    saveFileDirectory:str = fileDirectory + fileSep + 'converted'

    frameImport:CTkFrame = CTkFrame(app, width=400, height=50)
    btnSelectDir:CTkButton
    txtSelectedDir:CTkTextbox
    txtFileList:CTkTextbox

    frameConvertType:CTkFrame = CTkFrame(app, width=400, height=50)
    rbtnConvertAll:CTkRadioButton
    rbtnConvertNew:CTkRadioButton
    convertNew:BooleanVar = BooleanVar(app,True,'convertNew')
    btnConvert:CTkButton

    def __init__(self):
        try:
            icon = 'GP_Plasma_StackedOrg.ico'
            if exists(icon):
                self.app.iconbitmap(icon)
            else:
                self.app.iconbitmap('_internal/'+icon)
        except Exception as e:
            print(e)
        self.app.title('Emperion Runfile Converter')
        self.app.resizable(True,True)
        self.app.geometry('400x400')

        match os.name:
            case 'nt': self.fileSep = '\\'
            case 'posix': self.fileSep = '/'
            case _: self.fileSep = '/'

        # Define Items
        ## Direcotry Selection
        self.btnSelectDir = CTkButton(self.frameImport,command=self.selectDir, width=100, height=50, text='Select File Directory')
        self.txtSelectedDir = CTkTextbox(self.frameImport, width=300, height=50)
        self.txtFileList = CTkTextbox(self.app, width=400, height=200)
        ## Submission
        self.rbtnConvertNew = CTkRadioButton(self.frameConvertType, variable=self.convertNew, value=True, width=200, height=50, text='Convert New')
        self.rbtnConvertAll = CTkRadioButton(self.frameConvertType, variable=self.convertNew, value=False, width=200, height=50, text='Convert All (Override)')
        self.btnConvert = CTkButton(self.app,command=self.convertFiles, width=200, height=50, text='Convert Files in Directory', state = 'disabled')
        # Pack Items
        padX = 5
        padY = 5
        anchor = 'center'
        ## Directory Slection
        self.btnSelectDir.pack(padx=padX, pady=padY, anchor=anchor, expand=True, fill=BOTH, side=LEFT)
        self.txtSelectedDir.pack(padx=padX, pady=padY, anchor=anchor, expand=True, fill=BOTH, side=LEFT)
        self.frameImport.pack(padx=padX, pady=padY, anchor=anchor, expand=True, fill=BOTH)
        self.txtFileList.pack(padx=padX, pady=padY, anchor=anchor, expand=True, fill=BOTH)
        ## Submission
        self.rbtnConvertNew.pack(padx=padX, pady=padY, anchor=anchor, expand=True, fill=BOTH, side=LEFT)
        self.rbtnConvertAll.pack(padx=padX, pady=padY, anchor=anchor, expand=True, fill=BOTH, side=LEFT)
        self.frameConvertType.pack(padx=padX, pady=padY, anchor=anchor, expand=True, fill=BOTH)
        self.btnConvert.pack(padx=padX, pady=padY, anchor=anchor, expand=True, fill=BOTH)

    def makeSaveDir(self):
        try:
            os.mkdir(self.saveFileDirectory)
            print(f"Directory '{self.saveFileDirectory}' created successfully.")
        except FileExistsError:
            print(f"Directory '{self.saveFileDirectory}' already exists.")
        except PermissionError:
            print(f"Permission denied: Unable to create '{self.saveFileDirectory}'.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def selectDir(self):
        directory = self.fSelect.select_dir()
        self.fileDirectory = directory
        self.saveFileDirectory = directory + self.fileSep + 'converted'
        self.makeSaveDir()
        if directory != None:
            self.btnConvert.configure(state = 'disabled')
        self.txtSelectedDir.configure(require_redraw=False,state='normal')
        self.txtSelectedDir.delete('0.0','end')
        self.txtSelectedDir.insert('0.0',directory)
        self.txtSelectedDir.configure(require_redraw=False,state='disabled')
        self.getFileList(directory)
        return directory

    def getFileList(self,dir):
        fList = glob(dir+self.fileSep+'*.csv')
        self.fileList = fList
        pprint(fList)
        fNames = []
        for f in sorted(fList):
            fNames.append(basename(f))
        
        strFileList = '\n'.join(fNames)
        self.txtFileList.configure(require_redraw=False,state='normal')
        self.txtFileList.delete('0.0','end')
        self.txtFileList.insert('0.0',strFileList)
        self.txtFileList.configure(require_redraw=False,state='disabled')
        self.btnConvert.configure(state='normal')

    def filterFiles(self, onlyNew:bool):
        match onlyNew:
            case True:
                existList = glob(self.saveFileDirectory+self.fileSep+'*.csv')
                print('Exists')
                pprint(existList)
                exists = []
                tmpFileList = []
                for item in sorted(existList):
                    exists.append(basename(item))
                for file in self.fileList:
                    if basename(file) not in exists:
                        tmpFileList.append(file)
                self.fileList = tmpFileList
            case False:
                pass

    def convertFiles(self):
        message = ''
        self.filterFiles(self.convertNew.get())
        pprint(self.fileList)
        if len(self.fileList) == 0:
            message += 'No new files detected\n'
        for file in sorted(self.fileList):
            try:
                converter = EmperionCsvConverter(filepath=file,gui=self)
                saveFile = self.saveFileDirectory + self.fileSep + basename(file)
                converter.saveCsv(saveFile)
                message += f'Converted: {basename(file)}\n'
            except Exception as e:
                message += f'Error converting: {basename(file)}\n'
                print(f'Error Converting Files: {e}')
                raise e

        self.txtFileList.configure(require_redraw=False,state='normal')
        self.txtFileList.delete('0.0','end')
        self.txtFileList.insert('0.0',message)
        self.txtFileList.configure(require_redraw=False,state='disabled')

if '__main__' in __name__:
    converter = Converter()
    converter.app.mainloop()