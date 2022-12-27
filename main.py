import csv, os, time, tkinter
from netmiko import ConnectHandler
from tkinter import ttk, filedialog

class yottatechAutoAction:
    def __init__(self) -> None:        
        # self.csv,txt,conft,output的值由runBtn()回傳到init，系統會建立這些值。
        self.dcit = {"verbose": False}
        self.view()

    def csvFile(self):
    # 欲解析的CSV檔案路徑，內容為檔案命名與IP表，解析成二維List
        try:
            with open(self.csv) as csvFile:
                self.csv = list(csv.reader(csvFile))
        except:
            print("找不到CSV檔，請檢查檔案名稱")

    def txtFile(self):
    # 欲解析的txt檔案路徑，內容為欲下的指令，解析成List
        try:
            with open(self.txt) as File:
                self.txtList = File.read().split('\n')
        except:
            print("找不到TXT檔，請檢查檔案名稱")

    def run(self):
    # 遞迴ip表並執行欲下的指令，且將結果存成txt
        self.dirName = time.strftime('%Y-%m-%d_%H%M%S', time.localtime())
        os.mkdir(self.dirName)
        os.chdir(self.dirName)
        self.csvFile()
        self.txtFile()
        for fileList in self.csv:
            startingName = fileList[0]
            del fileList[0]
            for ipName in fileList:
                if ipName == '':
                    continue
                else:
                    try:
                        self.dcit['ip'] = ipName
                        connect = ConnectHandler(**self.dcit)
                        connect.enable()
                        if self.conft:
                            cmd = connect.send_config_from_file(self.txt)
                            print(cmd)
                            print(f"{startingName}_{ipName}執行成功\n")
                            connect.disconnect()
                        else:
                            if self.output:
                                with open("執行成功清單.txt", 'a') as newTxt:
                                    newTxt.write(f"==={startingName}_{ipName} : \n")
                                    for runTxt in self.txtList:   
                                        cmd = connect.send_command_timing(runTxt,delay_factor = 300)
                                        newTxt.write(f"{runTxt}\n")
                                        newTxt.write(f"{cmd}\n")
                                        newTxt.write(f"\n")
                                        print(f'{cmd}\n')
                                    print(f"{startingName}_{ipName}執行成功\n")
                            else:
                                with open(f"{startingName}_{ipName}.txt", 'a') as newTxt:
                                    for runTxt in self.txtList:
                                        cmd = connect.send_command_timing(runTxt,delay_factor = 300)
                                        newTxt.write(f'{runTxt}\n')
                                        newTxt.write(cmd)
                                        newTxt.write('\n\n\n')
                                        print(f'{cmd}\n')
                                    print(f"{startingName}_{ipName}執行成功\n")
                            connect.disconnect()
                    except Exception:
                        with open('執行失敗清單.txt', 'a') as err:
                            err.write(f"{startingName}_{ipName}\n\n")
                        print(f"{startingName}_{ipName}連線失敗\n")
        os.chdir('..')
        print('程式執行完畢')

    def importBtn(self,var):
        #開啟windows選擇檔案視窗。
        window = tkinter.Tk()
        window.wm_withdraw()
        path = filedialog.askopenfilename(filetypes =[('files', var)])
        window.destroy()
        return path

    def openCSV(self):
        path = self.importBtn('*.csv')
        self.csvPath = path
        self.textCSV.set(os.path.basename(path))

    def openTXT(self):
        path = self.importBtn('*.txt')
        self.txtPath = path
        self.textTXT.set(os.path.basename(path))

    def runBtn(self):
        # 點擊執行按鈕時將資料回傳至dict並且執行
        self.csv = self.csvPath
        self.txt = self.txtPath
        self.dcit['device_type'] = self.brandText.get()
        self.dcit['username'] = self.usrEntry.get()
        self.dcit['password'] = self.pasEntry.get()
        self.dcit['secret'] = self.enapsEntry.get()
        self.dcit['port'] = self.portEntry.get()
        if self.radVar.get() == 0:
            self.conft = False
        elif self.radVar.get() == 1:
            self.conft = True
        else:
            self.conft = False
        self.output = self.chkVar.get()
        self.run()

    def view(self):
        window = tkinter.Tk()
        window.title('yottatechAutoAction')
        window.geometry('300x300')
        window.resizable(False, False)
        window.grid()
        #第一區塊，匯入CSV、TXT按鈕------------------------------------------------
        fileFrame = tkinter.Frame(window)
        fileFrame.grid(row=0, sticky='w')
        self.textCSV = tkinter.StringVar()
        self.textCSV.set("尚未匯入")
        labelCSV = tkinter.Label(fileFrame, textvariable=self.textCSV)
        labelCSV.grid(row=0, column=1, ipadx=0, sticky="w")
        btnCSV = ttk.Button(fileFrame, text="import : CSV", command= self.openCSV)
        btnCSV.grid(row=0, column=0)
        self.textTXT = tkinter.StringVar()
        self.textTXT.set("尚未匯入")
        labelTXT = tkinter.Label(fileFrame, textvariable=self.textTXT)
        labelTXT.grid(row=1, column=1, ipadx=0, sticky="w")
        btnTXT = ttk.Button(fileFrame, text="import : TXT", command= self.openTXT)
        btnTXT.grid(row=1, column=0)
        #第二區塊，登入資訊--------------------------------------------------------
        loginFrame = tkinter.Frame(window)
        loginFrame.grid(row=1, sticky='w')
        brandLabel = ttk.Label(loginFrame,text='brand :')
        brandLabel.grid(row=0, column=0, ipadx=3, pady=5,  sticky="e")
        optionList = (
            "cisco_ios","cisco_ios","cisco_ios_telnet","cisco_xr","cisco_xr_telnet","cisco_nxos","cisco_nxos_telnet","cisco_asa","cisco_asa_telnet",
            "linux","linux_telnet","arista_eos","arista_eos_telnet","hp_comware","hp_comware_telnet","hp_procurve","hp_procurve_telnet",
            "juniper","juniper_telnet","juniper_junos","juniper_junos_telnet","f5_ltm","f5_ltm_telnet","autodetect","autodetect_telnet"
            )
        self.brandText = tkinter.StringVar()
        brandOtm = ttk.OptionMenu(loginFrame, self.brandText, *optionList)
        brandOtm.grid(row=0, column=1,sticky="w")
        usrLabel = ttk.Label(loginFrame,text='username :')
        usrLabel.grid(row=1, column=0, ipady=5, sticky="e")
        self.usrEntry = ttk.Entry(loginFrame, width=20)
        self.usrEntry.insert(0, 'admin')
        self.usrEntry.grid(row=1,column=1,sticky='w')
        pasLabel = ttk.Label(loginFrame,text='password :')
        pasLabel.grid(row=2, column=0, ipadx=3,sticky="e")
        self.pasEntry = ttk.Entry(loginFrame, width=20, show='*')
        self.pasEntry.grid(row=2,column=1,sticky='w')
        enapsLabel = ttk.Label(loginFrame,text='enable\npassword :')
        enapsLabel.grid(row=3, column=0, ipadx=3,sticky="e")
        self.enapsEntry = ttk.Entry(loginFrame, width=20, show='*')
        self.enapsEntry.insert(0, '')
        self.enapsEntry.grid(row=3,column=1, sticky='w')        
        portLabel = ttk.Label(loginFrame,text='port :')
        portLabel.grid(row=4, column=0, ipadx=3,sticky="e")
        self.portEntry = ttk.Entry(loginFrame, width=20,)
        self.portEntry.insert(0, '22')
        self.portEntry.grid(row=4,column=1, sticky='w')
        #第三區塊，選擇運作模式----------------------------------------------------
        frame3 = tkinter.Frame(window)
        frame3.grid(row=2, sticky='w')
        self.radVar = radioValue = tkinter.IntVar()
        self.RbtnShow =  ttk.Radiobutton(frame3, text='enable mode', variable=radioValue, value=0)
        self.RbtnShow.grid(row=0, column=0, pady=5,  sticky="w")
        self.chkVar = tkinter.BooleanVar() 
        self.chkVar.set(True)
        self.ckBtn = tkinter.Checkbutton(frame3, text='全部輸出到同一個.txt?', variable=self.chkVar)
        self.ckBtn.grid(row=0, column=1, pady=5,  sticky="w")
        self.RbtnConf = ttk.Radiobutton(frame3, text='conft mode', variable=radioValue, value=1)
        self.RbtnConf.grid(row=1, column=0, pady=5,  sticky="w")
        #第四區塊，執行按鈕---------------------------------------------------------
        frame4 = tkinter.Frame(window)
        frame4.grid(row=3, sticky='w')
        runBtn = ttk.Button(window, text="執行", command= self.runBtn)
        runBtn.grid(row=3, column=0, pady=5, sticky='w')
        #--------------------------------------------------------------------------
        window.update()
        window.mainloop()

if __name__ == "__main__":
    yottatechAutoAction()