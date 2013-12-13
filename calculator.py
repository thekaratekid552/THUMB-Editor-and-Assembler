

from Tkinter import *

class Calculator:
    def __init__(self):
        self.root = Tk()
        self.menu = Menu(self.root)
        self.menu.add_command(label="Quit", command=self.root.destroy) 
        self.root.config(menu=self.menu)
        self.root.title("Calculator")
        self.display = Entry(self.root)
        self.display.grid(row=1, column=0, columnspan=5)
        self.dot = False
        self.equalsdone = False
        Label(self.root).grid(row=2, column=0)
        Button(self.root, text="1", width=5, foreground="blue", command=lambda: self.addNumber("1")).grid(row=4, column=0)
        Button(self.root, text="2", width=5, foreground="blue", command=lambda: self.addNumber("2")).grid(row=4, column=1)
        Button(self.root, text="3", width=5, foreground="blue", command=lambda: self.addNumber("3")).grid(row=4, column=2)
        Button(self.root, text="4", width=5, foreground="blue", command=lambda: self.addNumber("4")).grid(row=5, column=0)
        Button(self.root, text="5", width=5, foreground="blue", command=lambda: self.addNumber("5")).grid(row=5, column=1)
        Button(self.root, text="6", width=5, foreground="blue", command=lambda: self.addNumber("6")).grid(row=5, column=2)
        Button(self.root, text="7", width=5, foreground="blue", command=lambda: self.addNumber("7")).grid(row=6, column=0)
        Button(self.root, text="8", width=5, foreground="blue", command=lambda: self.addNumber("8")).grid(row=6, column=1)
        Button(self.root, text="9", width=5, foreground="blue", command=lambda: self.addNumber("9")).grid(row=6, column=2)
        Button(self.root, text="0", width=5, foreground="blue", command=lambda: self.addNumber("0")).grid(row=7, column=1)
        Button(self.root, text=".", width=5, command=lambda: self.addNumber(".")).grid(row=7, column=0)
        Button(self.root, text="=", width=12, command=lambda: self.Equals()).grid(row=8, column=2, columnspan=2)
        Button(self.root, text="(", width=5, foreground="red", command=lambda: self.addNumber("(")).grid(row=8, column=0)
        Button(self.root, text=")", width=5, foreground="red", command=lambda: self.addNumber(")")).grid(row=8, column=1)
        Button(self.root, text="X", width=5, foreground="red", command=lambda: self.addNumber("x")).grid(row=4, column=3)
        Button(self.root, text="/", width=5, foreground="red", command=lambda: self.addNumber("/")).grid(row=5, column=3)
        Button(self.root, text="-", width=5, foreground="red", command=lambda: self.addNumber("-")).grid(row=6, column=3)
        Button(self.root, text="+", width=5, foreground="red", command=lambda: self.addNumber("+")).grid(row=7, column=3)
        Button(self.root, text="C", width=5, command=lambda:self.clear("all")).grid(row=3, column=3)
        Button(self.root, text="Del.", width=5, command=lambda:self.clear("1")).grid(row=3, column=2)
        self.root.mainloop()
    def clear(self, amount):
        if amount == "all":
            self.display.delete(0, END)
        elif amount == "1":
            if self.equalsdone == True:
                self.equalsdone = False
                y = self.display.get()
                yAct = y[1:]
                self.display.delete(0, END)
                self.display.insert(0, yAct)
                self.display.delete(len(yAct)-1, END)
            else:
                z = len(self.display.get())
                self.display.delete(z-1, END) 
    def addNumber(self, number):
        if self.equalsdone == True:
            self.equalsdone = False
            if number == "x" or  number == "/" or  number == "+" or  number == "-":
                y = self.display.get()
                yAct = y[1:]
                self.display.delete(0, END)
                self.display.insert(0, yAct)
                self.display.insert(END, number)
            else:
                self.display.delete(0, END)
                self.display.insert(0, number)
        elif number == ".":
            if self.dot == True:
                pass
            else:
                self.dot = True
                self.display.insert(END, number)
        elif number == "x" or number == "-"or number == "+"or number == "/":
            self.dot = False
            self.display.insert(END, number)
        else:
            self.display.insert(END, number)     
    def doEquation(self, operator):
        def setwaiting(operator):
            if operator == "x":
                self.waitingx = True
            if operator == "/":
                self.waitingd = True
            if operator == "+":
                self.waitingp = True
            if operator == "-":
                self.waitingt = True
        if self.waiting == False:
            self.waiting = True
            setwaiting(operator)
        elif self.waitingx == True:
            self.waitingx = False
            setwaiting(operator)
            self.no1f = float(self.no1)
            self.no2f = float(self.no2)
            x = self.no1f*self.no2f
            self.no1 = str(x)
            self.no2 = ""
            print(self.no1)
        elif self.waitingd == True:
            self.waitingd = False
            setwaiting(operator)
            self.no1f = float(self.no1)
            self.no2f = float(self.no2)
            x = self.no1f/self.no2f
            self.no1 = str(x)
            self.no2 = ""
            print(self.no1)
        elif self.waitingt == True:
            self.waitingt = False
            setwaiting(operator)
            self.no1f = float(self.no1)
            self.no2f = float(self.no2)
            x = self.no1f-self.no2f
            self.no1 = str(x)
            self.no2 = ""
            print(self.no1)
        elif self.waitingp == True:
            self.waitingp = False
            setwaiting(operator)
            self.no1f = float(self.no1)
            self.no2f = float(self.no2)
            x = self.no1f+self.no2f
            self.no1 = str(x)
            self.no2 = ""
            print(self.no1)
        else:
            setwaiting(operator)
    def Equals(self):
        self.length = len(self.display.get())
        self.equation = self.display.get()
        self.waiting = False
        self.no1 = ""
        self.no2 = ""
        self.lena = 0
        self.waitingx = False
        self.waitingd = False
        self.waitingt = False
        self.waitingp = False
        for item in self.equation:
            self.lena += 1
            if item == "x":
                self.doEquation(operator="x")
            elif item == "/":
                self.doEquation(operator="/")
            elif item == "-":
                self.doEquation(operator="-")
            elif item == "+":
                self.doEquation(operator="+")
            else:
                if self.waiting == False:
                    self.no1 += item
                elif self.waiting == True:
                    self.no2 += item
            if self.lena == self.length:
                self.doEquation(operator=False)
        self.display.delete(0, END)
        self.display.insert(0, "=" + self.no1)
        self.equalsdone = True

Calculator()