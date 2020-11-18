import tkinter as tk
from tkinter import font as tkfont
from tkinter import messagebox as tkmessage
import sqlite3
import datetime

d = datetime.datetime.now()
conn = sqlite3.connect('atm.db')
cur=conn.cursor()

class atmApp(tk.Tk): 
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.atmFont = tkfont.Font(family="Helvetica", size="14", weight="bold")
        self.titleFont = tkfont.Font(family="Helvetica", size="18", weight="bold")
        self.loggedInAcc = -1
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (loginPage, mainMenu, deposit, withdraw, transfer, wire, showTrans):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
    
        self.show_frame("loginPage")
    
    def show_frame(self, name):
        frame = self.frames[name]
        if name=="mainMenu":
            frame.updateBalances()
        if name=="loginPage":
            self.loggedInAcc = -1
        frame.tkraise()
    
    def populateDB(self):
        cur.executescript("CREATE TABLE IF NOT EXISTS accounts (accNO VARCHAR(20), PIN smallint, savings real, checking real, transactions text, PRIMARY KEY (accNO));")
        cur.executescript("INSERT INTO accounts (accNO, PIN, savings, checking, transactions) VALUES (123546, 1234, 53.25, 684.21, ''), (234523, 2345, 523.25, 6284.21, ''), (4673456, 3456, 532.25, 1684.21, ''), (3566234, 4567, 153.25, 64284.21, ''), (281385118, 5678, 53.25, 684.21, ''), (51681583, 6789, 3.25, 898104.21, ''), (198646, 7890, 51233.25, 6123484.21, '');")
        conn.commit()
    
    def closeConn(self):
        conn.close()
    
    def addTransaction(self, Trans="", wireAccNo=-1, wireTrans=""):
        if self.loggedInAcc == -1:
            return
        tempTrans = ""
        cur.execute("SELECT transactions FROM accounts WHERE accNo=" + str(self.loggedInAcc) + ";")
        dbTrans = cur.fetchone()
        if dbTrans is not None:
            tempTrans = str(dbTrans[0])
        tempTrans = tempTrans +Trans+ ","
        cur.execute("UPDATE accounts SET transactions='" + tempTrans +"' WHERE accNO=" + str(self.loggedInAcc)+";")
        conn.commit()
        if wireAccNo==-1:
            return
        tempTrans = ""
        cur.execute("SELECT transactions FROM accounts WHERE accNo=" + str(wireAccNo) + ";")
        dbTrans = cur.fetchone()
        if dbTrans is not None:
            tempTrans = str(dbTrans[0])
        tempTrans = tempTrans+wireTrans+""
        cur.execute("UPDATE accounts SET transactions='" + tempTrans +"' WHERE accNO=" + str(wireAccNo) +";")
        conn.commit()



    
class loginPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        can = tk.Canvas(self)
        can.place(anchor=tk.CENTER, relx=0.5, rely=0.5)
        tk.Label(can, text="Account Number", font=controller.atmFont).grid(row=0, column=0)
        tk.Label(can, text="PIN", font=controller.atmFont).grid(row=2,column=0)
        self.accNo = tk.Entry(can, bd=5, justify=tk.CENTER)
        self.PIN = tk.Entry(can, bd=3, show="*", justify=tk.CENTER)
        self.accNo.grid(row=0, column=1)
        self.PIN.grid(row=2, column=1)

        loginButton = tk.Button(can, text="Login", command=lambda: self.loginPressed(self.accNo.get(), self.PIN.get()))
        exitButton = tk.Button(can, text="Exit", command=controller.destroy)

        loginButton.grid(row = 5, column = 0)
        exitButton.grid(row=5, column = 1)

    def loginPressed(self, accNo, PIN):
        self.accNo.delete(0, 'end')
        self.PIN.delete(0, 'end')
        cur.execute("SELECT accNO FROM accounts WHERE accNO='"+str(accNo)+"';")
        DBaccNo=cur.fetchone()
        if DBaccNo is None:
            tkmessage.showinfo("Invalid Account", "The account number you entered was not found!")
            return
        cur.execute("SELECT PIN FROM accounts WHERE accNO='"+str(accNo)+"';")
        DBPIN=cur.fetchone()[0]

        if DBaccNo[0]==accNo and str(DBPIN)==str(PIN):
            self.controller.loggedInAcc = accNo
            self.controller.show_frame("mainMenu")
        else:
            tkmessage.showinfo("Invalid Credentials", "Account number and PIN do not match! Please try again!")

class mainMenu(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.checkingBAL = tk.StringVar(value="Checking needs update")
        self.savingsBAL = tk.StringVar(value="Savings needs update")
        menuCanvas = tk.Canvas(self)
        menuCanvas.pack(anchor=tk.W, side=tk.LEFT, padx = (15,0))
        balanceCanvas = tk.Canvas(self)
        balanceCanvas.pack(anchor=tk.E, padx=(0, 15), side=tk.RIGHT)
        tk.Label(self, text="Welcome to your account!", font=controller.atmFont).pack(anchor=tk.N, fill=tk.X, side=tk.TOP, padx=(0,0))
        tk.Label(menuCanvas, text="What would you like to do? ", font=controller.atmFont).pack(side=tk.TOP, padx=2, pady=5)
        withdrawButton= tk.Button(menuCanvas, text="Withdraw", font=controller.atmFont, command=lambda: controller.show_frame("withdraw"))
        withdrawButton.pack(side=tk.TOP, padx=2, pady=5)
        depositButton= tk.Button(menuCanvas, text="Deposit", font=controller.atmFont, command=lambda: controller.show_frame("deposit"))
        depositButton.pack(side=tk.TOP, padx=2, pady=5)
        transferButton= tk.Button(menuCanvas, text="Transfer Funds", font=controller.atmFont, command=lambda: controller.show_frame("transfer"))
        transferButton.pack(side=tk.TOP, padx=2, pady=5)
        wireButton= tk.Button(menuCanvas, text="Wire", font=controller.atmFont, command=lambda: controller.show_frame("wire"))
        wireButton.pack(side=tk.TOP, padx=2, pady=5)
        transButton= tk.Button(menuCanvas, text="View Transactions", font=controller.atmFont, command=lambda: controller.show_frame("showTrans"))
        transButton.pack(side=tk.TOP, padx=2, pady=5)
        logoutButton= tk.Button(menuCanvas, text="Logout", font=controller.atmFont, command=lambda: controller.show_frame("loginPage"))
        logoutButton.pack(side=tk.TOP, padx=2, pady=5)
        tk.Label(balanceCanvas, text="Your Balances: ", font=controller.atmFont).pack(side=tk.TOP, padx=2, pady=5)
        self.updateBalances()
        tk.Label(balanceCanvas, textvariable=self.checkingBAL, font=controller.atmFont).pack(side=tk.TOP, padx=2, pady=5)
        tk.Label(balanceCanvas, textvariable=self.savingsBAL, font=controller.atmFont).pack(side=tk.TOP, padx=2, pady=5)

    
    def updateBalances(self):
        tempC = "0.00"
        tempS = "0.00"
        cur.execute("SELECT checking FROM accounts WHERE accNO=" + str(self.controller.loggedInAcc)+";")
        row = cur.fetchone()
        if row is not None:
            tempC = str(row[0])
        self.checkingBAL.set("Checking Account: $ " + tempC)
        cur.execute("SELECT savings FROM accounts WHERE accNO=" + str(self.controller.loggedInAcc)+";")
        row = cur.fetchone()
        if row is not None:
            tempS = str(row[0])
        self.savingsBAL.set("Savings Account: $ " + tempS)


class deposit(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        canv = tk.Canvas(self)
        canv.place(anchor=tk.CENTER, relx=0.5, rely=0.5)
        tk.Label(canv, text="Enter Deposit Amount (Insert Cash into cash dispenser): ", font=controller.atmFont).grid(row= 0, column=0)
        self.dAmt = tk.Entry(canv, bd=5, justify=tk.CENTER)
        self.dAmt.grid(row= 0, column = 2)
        self.accType = tk.IntVar()
        self.accType.set(1)
        # CHECKING = 1  SAVINGS = 2
        tk.Radiobutton(canv, text="Deposit to Checking", variable=self.accType, value=1, font=controller.atmFont, indicatoron=0).grid(row = 4, column = 2)
        tk.Radiobutton(canv, text="Deposit to Savings", variable=self.accType, value=2, font=controller.atmFont, indicatoron=0).grid(row=5, column=2)
        tk.Button(canv, text="Cancel", font=controller.atmFont, command=self.cancelPressed).grid(row = 9, rowspan=2, column = 0)
        tk.Button(canv, text="Confirm", font=controller.atmFont, command=self.confirmPressed).grid(row= 9, rowspan=2, column=2)
    def cancelPressed(self):
        self.dAmt.delete(0, 'end')
        self.controller.show_frame("mainMenu")

    def confirmPressed(self):
        Amt = float(self.dAmt.get())
        self.dAmt.delete(0,'end')
        acct = "checking"
        accbal = 0.00
        if Amt<0.00:
            tkmessage.showerror("Error", "Deposit amount cannot be negative")
            return
        if Amt==0.00:
            depZ = tkmessage.askyesno("Depositing Zero", "You are depositing $0. This will have no effect. Want to continue?", icon="warning")
            if depZ== False:
                return
        if self.accType.get()==1:
            acct = "checking"
        if self.accType.get()==2:
            acct = "savings"
        cur.execute("SELECT "+ acct + " FROM accounts WHERE accNO=" + str(self.controller.loggedInAcc)+";")
        row = cur.fetchone()
        if row is not None:
            accbal = row[0]
        newbal = accbal + Amt
        cur.execute("UPDATE accounts SET " + acct + " = " + str(newbal) + " WHERE accNO=" + str(self.controller.loggedInAcc)+";")
        transaction = "You Deposited $" + str(Amt) + " to " + acct + " on " + str(d.strftime("%m/%d/%Y")) + " at " + str(d.strftime("%H:%M:%S"))
        self.controller.addTransaction(transaction)
        tkmessage.showinfo("Success!", "Successfully added $"+ str(Amt) + " to " + acct)
        conn.commit()
        self.controller.show_frame("mainMenu")
        
       

class withdraw(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        canv = tk.Canvas(self)
        canv.place(anchor=tk.CENTER, relx=0.5, rely=0.5)
        tk.Label(canv, text="Enter Withdraw Amount: ", font=controller.atmFont).grid(row= 0, column=0)
        self.dAmt = tk.Entry(canv, bd=5, justify=tk.CENTER)
        self.dAmt.grid(row= 0, column = 2)
        self.accType = tk.IntVar()
        self.accType.set(1)
        # CHECKING = 1  SAVINGS = 2
        tk.Radiobutton(canv, text="Withdraw from Checking", variable=self.accType, value=1, font=controller.atmFont, indicatoron=0).grid(row = 4, column = 2)
        tk.Radiobutton(canv, text="Withdraw from Savings", variable=self.accType, value=2, font=controller.atmFont, indicatoron=0).grid(row=5, column=2)
        tk.Button(canv, text="Cancel", font=controller.atmFont, command=self.cancelPressed).grid(row = 9, rowspan=2, column = 0)
        tk.Button(canv, text="Confirm", font=controller.atmFont, command=self.confirmPressed).grid(row= 9, rowspan=2, column=2)
    def cancelPressed(self):
        self.dAmt.delete(0, 'end')
        self.controller.show_frame("mainMenu")

    def confirmPressed(self):
        Amt = float(self.dAmt.get())
        self.dAmt.delete(0,'end')
        acct = "checking"
        accbal = 0.00
        if Amt<0.00:
            tkmessage.showerror("Error", "Deposit amount cannot be negative")
            return
        if Amt==0.00:
            depZ = tkmessage.askyesno("Depositing Zero", "You are depositing $0. This will have no effect. Want to continue?", icon="warning")
            if depZ== False:
                return
        if self.accType.get()==1:
            acct = "checking"
        if self.accType.get()==2:
            acct = "savings"
        cur.execute("SELECT "+ acct + " FROM accounts WHERE accNO=" + str(self.controller.loggedInAcc)+";")
        row = cur.fetchone()
        if row is not None:
            accbal = row[0]
        if accbal - Amt < 0.00:
            tkmessage.showinfo("Error!", "Insufficient funds. Amount withdrew will be " + str(accbal) + " instead.")
            Amt = accbal
        newbal = accbal - Amt
        cur.execute("UPDATE accounts SET " + acct + " = " + str(newbal) + " WHERE accNO=" + str(self.controller.loggedInAcc)+";")
        transaction = "You Withdrew $" + str(Amt) + " from " + acct + " on " + str(d.strftime("%m/%d/%Y")) + " at " + str(d.strftime("%H:%M:%S"))
        self.controller.addTransaction(transaction)
        tkmessage.showinfo("Success!", "Successfully withdrew $"+ str(Amt) + " from " + acct)
        conn.commit()
        self.controller.show_frame("mainMenu")   


class transfer(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        canv = tk.Canvas(self)
        canv.place(anchor=tk.CENTER, relx=0.5, rely=0.5)
        tk.Label(canv, text="Enter Transfer Amount: ", font=controller.atmFont).grid(row= 0, column=0)
        self.dAmt = tk.Entry(canv, bd=5, justify=tk.CENTER)
        self.dAmt.grid(row= 0, column = 2)
        self.accType = tk.IntVar()
        self.accType.set(1)
        # CHECKING -> SAVINGS = 1  SAVINGS -> CHECKING = 2
        tk.Radiobutton(canv, text="Checking to Savings", variable=self.accType, value=1, font=controller.atmFont, indicatoron=0).grid(row = 4, column = 2)
        tk.Radiobutton(canv, text="Savings to Checking", variable=self.accType, value=2, font=controller.atmFont, indicatoron=0).grid(row=5, column=2)
        tk.Button(canv, text="Cancel", font=controller.atmFont, command=self.cancelPressed).grid(row = 9, rowspan=2, column = 0)
        tk.Button(canv, text="Confirm", font=controller.atmFont, command=self.confirmPressed).grid(row= 9, rowspan=2, column=2)
    def cancelPressed(self):
        self.dAmt.delete(0, 'end')
        self.controller.show_frame("mainMenu")

    def confirmPressed(self):
        Amt = float(self.dAmt.get())
        self.dAmt.delete(0,'end')
        sender = "checking"
        to = "savings"
        accbal = 0.00
        if Amt<0.00:
            tkmessage.showerror("Error", "Deposit amount cannot be negative")
            return
        if Amt==0.00:
            depZ = tkmessage.askyesno("Transfering Zero", "You are depositing $0. This will have no effect. Want to continue?", icon="warning")
            if depZ== False:
                return
        if self.accType.get()==1:
            sender = "checking"
            to = "savings"
        if self.accType.get()==2:
            sender = "savings"
            to = "checking"
        cur.execute("SELECT "+ sender + " FROM accounts WHERE accNO=" + str(self.controller.loggedInAcc)+";")
        row = cur.fetchone()
        if row is not None:
            accbal = row[0]
        if accbal - Amt < 0.00:
            tkmessage.showinfo("Error!", "Insufficient funds. Amount transfered will be " + str(accbal) + " instead.")
            Amt = accbal
        newbal = accbal - Amt
        cur.execute("UPDATE accounts SET " + sender + " = " + str(newbal) + " WHERE accNO=" + str(self.controller.loggedInAcc)+";")
        conn.commit()
        cur.execute("SELECT "+ to + " FROM accounts WHERE accNO=" + str(self.controller.loggedInAcc)+";")
        row = cur.fetchone()
        if row is not None:
            accbal = row[0]
        newbal = accbal + Amt
        cur.execute("UPDATE accounts SET " + to + " = " + str(newbal) + " WHERE accNO=" + str(self.controller.loggedInAcc)+";")
        transaction = "You Transfered $" + str(Amt) + " from " + sender + " to " + to + " on " + str(d.strftime("%m/%d/%Y")) + " at " + str(d.strftime("%H:%M:%S"))
        self.controller.addTransaction(transaction)
        tkmessage.showinfo("Success!", "Successfully transfered $"+ str(Amt) + " to " + to + " from " + sender)
        conn.commit()
        self.controller.show_frame("mainMenu")


class wire(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        # More widgets here

class showTrans(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        tk.Label(self, text="Your Transaction History", font=controller.titleFont, justify=tk.CENTER).pack(side=tk.TOP, fill=tk.X)
        scrollbar = tk.Scrollbar(self)
        scrollbar.pack(side=tk.RIGHT, fill=tk.BOTH)
        self.listbox = tk.Listbox(self)
        self.listbox.pack(fill=tk.BOTH, expand=1)
        self.updateListBox()
        self.listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.listbox.yview)
        tk.Button(self, text="Back", font=controller.atmFont, justify=tk.CENTER, command=lambda: controller.show_frame("mainMenu")).pack(side=tk.BOTTOM)
    
    def updateListBox(self):
        self.listbox.delete(0, tk.END)
        cur.execute("SELECT transactions FROM accounts WHERE accNO=" + str(self.controller.loggedInAcc) + ";")
        dbTrans = cur.fetchone()
        if dbTrans is not None:
            dbTrans = str(dbTrans[0])
        else:
            self.listbox.insert(tk.END, "NO TRANSACTIONS YET")
            return
        dbTrans = dbTrans.split(",")
        for transaction in dbTrans:
            self.listbox.insert(tk.END, str(transaction))
