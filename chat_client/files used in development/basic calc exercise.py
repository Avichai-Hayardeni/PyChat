from tkinter import *
import time

root = Tk()


def button_click(num):
    current = e.get()
    e.delete(0, END)
    e.insert(0, str(current) + str(num))


def click_clear():
    e.delete(0, END)


def click_add():
    e.insert(END, "+")


def click_equal():
    numbers = e.get().split("+")
    e.delete(0, END)
    sum = 0
    for num in numbers:
        sum += int(num)
    e.insert(0, str(sum))


e = Entry(root, width=30, borderwidth=5)
e.grid(row=0, column=0, columnspan=3)


button1 = Button(root, text="1", command=lambda: button_click(1), padx=30, pady=20)
button2 = Button(root, text="2", command=lambda: button_click(2), padx=30, pady=20)
button3 = Button(root, text="3", command=lambda: button_click(3), padx=30, pady=20)
button4 = Button(root, text="4", command=lambda: button_click(4), padx=30, pady=20)
button5 = Button(root, text="5", command=lambda: button_click(5), padx=30, pady=20)
button6 = Button(root, text="6", command=lambda: button_click(6), padx=30, pady=20)
button7 = Button(root, text="7", command=lambda: button_click(7), padx=30, pady=20)
button8 = Button(root, text="8", command=lambda: button_click(8), padx=30, pady=20)
button9 = Button(root, text="9", command=lambda: button_click(9), padx=30, pady=20)
button0 = Button(root, text="0", command=lambda: button_click(0), padx=30, pady=20)
button_add = Button(root, text="+", command=click_add, padx=29, pady=20)
button_equal = Button(root, text="=", command=click_equal, padx=67, pady=20)
button_clear = Button(root, text="clear", command=click_clear, padx=59, pady=20)

button1.grid(row=3, column=0)
button2.grid(row=3, column=1)
button3.grid(row=3, column=2)
button4.grid(row=2, column=0)
button5.grid(row=2, column=1)
button6.grid(row=2, column=2)
button7.grid(row=1, column=0)
button8.grid(row=1, column=1)
button9.grid(row=1, column=2)
button0.grid(row=4, column=0)
button_add.grid(row=5, column=0)
button_equal.grid(row=4, column=1, columnspan=2)
button_clear.grid(row=5, column=1, columnspan=2)


root.mainloop()