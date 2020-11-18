from atm import atmApp

myATM = atmApp()
myATM.geometry("800x600")
myATM.title("ATM Software")
# myATM.populateDB() # only run this once
myATM.mainloop()
myATM.closeConn()