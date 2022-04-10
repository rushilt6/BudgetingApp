
import argparse
import io
import json
import os
import numpy as np
from google.cloud import language_v1
import six

from email.base64mime import header_length
from os import link
from tkinter import messagebox
from tkinter import *
from tkinter import ttk, filedialog
import tkinter
from tkinter.filedialog import askopenfile
from turtle import width

from sqlalchemy import false, true

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

from http import client
import io, os
from google.cloud import vision
from google.cloud.vision_v1 import types
import pandas as pd

os.environ['GOOGLE_APPLICATION_CREDENTIALS']="/Users/rushilthummaluru/Desktop/projects/Budget/VisionApiKey.json"
cred = credentials.Certificate("/Users/rushilthummaluru/Desktop/projects/Budget/budgetpyrebase-firebase-adminsdk-1ynss-148fd78c19.json")
firebase_admin.initialize_app(cred, {
  'databaseURL':'https://budgetpyrebase-default-rtdb.firebaseio.com/'
})

t = 0
cattotal = [0,0,0,0,0,0,0]
categories = ["Food","Transportation","Personal Spending","Electronics","Other","Health\SkinCare","Entertainment"]
foodList = []
elecList = []
psList = []
transList = []
otherList = []
healthList = []
entList = []

client = vision.ImageAnnotatorClient()


#def splitText(df):


expenses = 0
food = 0
transportation = 0
personalspending = 0
electronics = 0
health = 0
entertainment = 0
other = 0

def sort(cat,word):
    cat.append(" ")
    if(cat[0]=="Arts & Entertainment" or cat[0]=="Books & Literature" or cat[0]=="Games" or cat[0]=="Hobbies & Leisure" or cat[0]=="Sports"):
        entList.append(word)
    elif(cat[0]=="Autos & Vehicles"):
        transList.append(word)
    elif(cat[0]=="Beauty & Fitness"):
        healthList.append(word)
    elif(cat[0]=="Jobs & Education" or cat[0]=="Shopping"):
        psList.append(word)
    elif(cat[0]=="Business & Industrial"):
        if(cat[1]=="Transportation & Logistics"):
            transList.append(word)
        else: 
            otherList.append(word)
    elif(cat[0]=="Computers & Electronics"):
        elecList.append(word)
    elif(cat[0]=="Finance" or cat[0]=="Pets & Animals" or cat[0]=="Reference"):
        otherList.append(word)
    elif(cat[0]=="Food & Drink"):
        foodList.append(word)
    elif(cat[0]=="Travel"):
        foodList.append(word)
    elif(cat[0]=="Health"):
        healthList.append(word)
    
def classify(text,verbose =True):
    language_client = language_v1.LanguageServiceClient()
    document = language_v1.Document(content=text,type_=language_v1.Document.Type.PLAIN_TEXT)
    response = language_client.classify_text(request={"document":document})
    categories = response.categories
    result = {}
    for category in categories:
        result[category.name] = category.confidence
    if verbose:
        #print(text)
        #print(categories[0].name)
        #print(categories[0].confidence)
        fcat = categories[0].name.split("/")
        del(fcat[0])            
        # for category in categories:
        #     print("="*20)
        #     print("{:<16}: {}".format("category", category.name))
        #     print("{:<16}: {}".format("confidence", category.confidence))
    else:
        print("no work")
        
            
    return fcat
# = "Wad w"
# try:
#     sort(classify(20*(word+" ")),word )
# except:
#     print("Not related")
# print(otherList)
def checkWork(s):
    try:
        if(classify(20*(s+ " ")),s):
            return True
    except:
        return False
#print(checkWork(word))
pl = []
connect = {}
def detectText(img):
    total = 0
    #picture name
    items = []
    prices = []

    with io.open(img, 'rb') as image_file:
        content = image_file.read()

    image = types.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations

    df = pd.DataFrame(columns=['locale','description'])
    for text in texts:
        df = df.append(
            dict(
                Locale=text.locale, 
                description=text.description
            ),
            ignore_index=True
        )
    #print(df['description'][0])
    line = df['description'][0]
    splitLine = line.split('\n')
    for str in splitLine:
        if '$' in str:
            prices.append(str[1:len(str)])

        if not '$' in str and any(c.isalpha() for c in str.lower()) and not 'total' in str.lower():
            items.append(str)
    
    while len(prices) > len(items):
        del(prices[-1])

    #This removes all prices that are not linked with an item
    itemCount = 0
    for str in items:
        if not checkWork(str) or len(str)<3: #checks whether item works in correlation
            #stuff
            try:
                del prices[itemCount]
            except:
                print("")
            try:
                del items[itemCount]
            except:
                print("")
        itemCount+=1
    for i in prices:
        total+=float(i)
    t = total        
    a = db.reference("Budget")
    b = db.reference('Budget/Total').get() + t
    a.update({'Total':b})
    #print(items)
    #print(prices)
    pl = prices
    c = 0
    for i in items:
        connect[i] = prices[c]
        c+=1
    print(connect)
    return items
def send_to_firebase(category,object,price):
  f = db.reference('data/'+category)
  temp_ref = f.push({
    object:price
  })
  
def transfer_to_firebase(category,list,index):
    for i in list:
        send_to_firebase(category,i,connect[i])
        cattotal[index]+= float(connect[i])
def category_totals(category):
    w = db.reference("data/"+category+"/Total")
    w.update({"Value":cattotal[categories.index(category)]})
    elecList.clear()
    foodList.clear()
    psList.clear()
    otherList.clear()
    entList.clear()
    healthList.clear()
    transList.clear()
def editBudget():
    firstFrame.pack_forget()
    budgetFrame.pack(fill="both",expand=1)
def helpMe():
    messagebox.showinfo("","Enter an item by scanning a recipt or manually entering an item and this will let you see your monthly expenses and how much of your budget you spent")
def enter():
    #enter shit
    firstFrame.pack_forget()
    secondFrame.pack(fill="both",expand=1)
def optionEnter():
    catagory.append(clicked.get())
    monkey = cost.get(1.0, "end-1c").split(",")
    print(monkey)
    price.append((int)(monkey[0]))
    item.append(monkey[1])
    print(price)
    print(item)
def enter4():
    budget = budgetAmount.get(1.0, "end-1c")
    b = db.reference("Limit")
    a = db.reference("Budget/Total").get()
    b.update({"Total":budget})
    linkName = tkinter.Label(firstFrame, text = "Budget Amount: "+str(budget))
    linkName.config(fg='#e5eaf5')
    linkName.config(font =("Courier", 20))
    linkName.config(bg='#494D5F')
    spacer3.pack()
    linkName.pack()
    sum = 0
    for i in range(0, len(price)):
        sum = sum + (int)(price[i])
    remaining = int(budget) - int(sum+a)
    l = tkinter.Label(firstFrame, text = "Budget Remaining: "+str(remaining))
    l.config(fg='#e5eaf5')
    l.config(font =("Courier", 20))
    l.config(bg='#494D5F')
    l.pack()


def view():
    firstFrame.pack_forget()
    viewFrame.pack(fill="both",expand=1)
    sum = 0
    for i in range(0, len(price)):    
        sum = sum + (int)(price[i])

    
def back():
    secondFrame.pack_forget()
    firstFrame.pack(fill="both",expand=1)
def back2():
    scanFrame.pack_forget()
    secondFrame.pack(fill="both",expand=1)
def back3():
    manualFrame.pack_forget()
    secondFrame.pack(fill="both",expand=1)
def back4():
    viewFrame.pack_forget()
    firstFrame.pack(fill="both",expand=1)
def back5():
    budgetFrame.pack_forget()
    firstFrame.pack(fill="both",expand=1)
    budget = budgetAmount.get(1.0, "end-1c")

def scan():
    firstFrame.pack_forget()
    secondFrame.pack_forget()
    thirdFrame.pack_forget()
    scanFrame.pack(fill="both",expand=1)
def manual():
    secondFrame.pack_forget()
    manualFrame.pack(fill="both",expand=1)
def explore():
   file = filedialog.askopenfile(mode='r', filetypes=[('Image Files', '.png .jpg .jpeg')])
   if file:
        linkNameText.delete("1.0","end-1c")
        filepath = os.path.abspath(file.name)
        fname = os.path.basename(file.name)
        il = detectText(filepath)
        #elecList = []
        for item in il:
            try:
                sort(classify(20*(item+" ")),item)
            except:
                print("Not related")   
        transfer_to_firebase("Food",foodList,0)
        transfer_to_firebase("Personal Spending",psList,2)
        transfer_to_firebase("Electronics",elecList,3)
        transfer_to_firebase("Other",otherList,4)
        transfer_to_firebase("Health\SkinCare",healthList,5)
        transfer_to_firebase("Entertainment",entList,6)
        transfer_to_firebase("Transportation\Travel",transList,1)
        ref = db.reference("data")
        firejson = ref.get()
        for i in range(0,len(categories)):
            category_totals(categories[i])
        #print(elecList)
        file.close()
ref = db.reference("/")
def reset():
    ref.set({
    "Budget":{
        "Total":0
    },
    "Limit":{
        "Total":0
    },
    "data":{
        "Entertainment":
        {
        "Total":
            {
            "Value":0
            }
        },
        "Food":
        {
        "Total":
            {
            "Value":0
            }
        },
        "Transportation\Travel":
        {
        "Total":
            {
            "Value":0
            }
        },
        "Personal Spending":
        {
        "Total":
            {
            "Value":0
            }
        },
        "Electronics":
        {
        "Total":
            {
            "Value":0
            }
        },
        "Other":
        {
        "Total":
            {
            "Value":0
            }
        },
        "Health\SkinCare":
        {
        "Total":
            {
            "Value":0
            }
        }
    }
    })      
#reset()    

root = tkinter.Tk()

firstFrame= Frame(root,width = 550,height = 400,bg='#494D5F')
secondFrame= Frame(root,width = 550,height = 400,bg='#494D5F')
thirdFrame= Frame(root,width = 550,height = 400,bg='#494D5F')
manualFrame= Frame(root,width = 550,height = 400,bg='#494D5F')
scanFrame= Frame(root,width = 550,height = 400,bg='#494D5F')
viewFrame= Frame(root,width = 550,height = 400,bg='#494D5F')
budgetFrame = Frame(root,width = 550,height = 400,bg='#494D5F')
item = list()
price = list() 
catagory = list()


l9 = tkinter.Label(viewFrame, text = "Total Expenses: "+str(db.reference('Budget/Total').get()))
l9.config(fg='#e5eaf5')
l9.config(font =("Courier", 20))
l9.config(bg='#494D5F')

food = db.reference("data/Food/Total/Value").get()
l10 = tkinter.Label(viewFrame, text = "Food Expenses: "+str(food))
l10.config(fg='#e5eaf5')
l10.config(font =("Courier", 20))
l10.config(bg='#494D5F')

transportation = db.reference("data/Transportation\Travel/Total/Value").get()
l11 = tkinter.Label(viewFrame, text = "Transportation Expenses: "+str(transportation))
l11.config(fg='#e5eaf5')
l11.config(font =("Courier", 20))
l11.config(bg='#494D5F')

personalspending = db.reference("data/Personal Spending/Total/Value").get()
l12 = tkinter.Label(viewFrame, text = "Personal Spending Expenses: "+str(personalspending))
l12.config(fg='#e5eaf5')
l12.config(font =("Courier", 20))
l12.config(bg='#494D5F')

electronics = db.reference("data/Electronics/Total/Value").get()
l13 = tkinter.Label(viewFrame, text = "Electronics Expenses: "+str(electronics))
l13.config(fg='#e5eaf5')
l13.config(font =("Courier", 20))
l13.config(bg='#494D5F')

health = db.reference("data/Health\SkinCare/Total/Value").get()
l14 = tkinter.Label(viewFrame, text = "Health/Selfcare Expenses: "+str(health))
l14.config(fg='#e5eaf5')
l14.config(font =("Courier", 20))
l14.config(bg='#494D5F')

entertainment = db.reference("data/Entertainment/Total/Value").get()
l15 = tkinter.Label(viewFrame, text = "Entertainment Expenses: "+str(entertainment))
l15.config(fg='#e5eaf5')
l15.config(font =("Courier", 20))
l15.config(bg='#494D5F')

other = db.reference("data/Other/Total/Value").get()
l16 = tkinter.Label(viewFrame, text = "Other Expenses: "+str(other))
l16.config(fg='#e5eaf5')
l16.config(font =("Courier", 20))
l16.config(bg='#494D5F')
# specify size of window.
root.geometry("1000x750")

# Create text widget and specify size.
T = tkinter.Text(root, height = 50, width = 520)

# Create label
linkNameText = tkinter.Text(firstFrame, height = 50, width = 520)
linkNameText.text = "hi"
linkNameText.config(bg='#494D5F')
linkNameText.config(fg='#e5eaf5')

Fact = """"""
# Create button for next text.

spacer = tkinter.Label(firstFrame, text="",height=1)
spacer.config(bg='#494D5F')
spacer1 = tkinter.Label(firstFrame, text="",height=1)
spacer1.config(bg='#494D5F')
b3 = tkinter.Button(firstFrame, text = "Help",command = helpMe,height=2,width=40,bg="#d0bdf4")
b3.config(font =("Courier"))
# Create an Exit button.
b2 = tkinter.Button(firstFrame, text = "Exit",command = root.destroy,height=2,width=40,bg="#d0bdf4")
editBudgetButton = tkinter.Button(firstFrame, text = "Edit Budget",command = editBudget,height=2,width=40,bg="#d0bdf4")
editBudgetButton.config(font =("Courier"))

spacer2 = tkinter.Label(firstFrame, text="",height=1)
spacer2.config(bg='#494D5F')
b2.config(font =("Courier"))

b4 = tkinter.Button(firstFrame, text = "Enter Values",command = enter,height=2,width=40,bg="#d0bdf4")
b4.config(font =("Courier"))

spacer3 = tkinter.Label(firstFrame, text="",height=1)
spacer3.config(bg='#494D5F')
spacer4 = tkinter.Label(firstFrame, text="",height=1)
spacer4.config(bg='#494D5F')
b5 = tkinter.Button(firstFrame, text = "Monthly Spending Breakdown",command = view,height=2,width=40,bg="#d0bdf4")
b5.config(font =("Courier"))

scanButton = tkinter.Button(secondFrame, text = "Scan Recipts",command = scan,height=2,width=40,bg="#d0bdf4")
scanButton.config(font =("Courier"))

manualInput = tkinter.Button(secondFrame, text = "Input Expense",command = manual,height=2,width=40,bg="#d0bdf4")
manualInput.config(font =("Courier"))
BackButton = tkinter.Button(secondFrame, text = "Back",command = back,height=2,width=40,bg="#d0bdf4")
BackButton.config(font =("Courier"))
back2Button = tkinter.Button(scanFrame, text = "Back",command = back2,height=2,width=40,bg="#d0bdf4")
back2Button.config(font =("Courier"))
back3Button = tkinter.Button(manualFrame, text = "Back",command = back3,height=2,width=40,bg="#d0bdf4")
back3Button.config(font =("Courier"))
back4Button = tkinter.Button(viewFrame, text = "Back",command = back4,height=2,width=40,bg="#d0bdf4")
back4Button.config(font =("Courier"))
back5Button = tkinter.Button(budgetFrame, text = "Back",command = back5,height=2,width=40,bg="#d0bdf4")
back5Button.config(font =("Courier"))
inputEnter = tkinter.Button(manualFrame, text = "Enter",command = optionEnter,height=2,width=40,bg="#d0bdf4")
inputEnter.config(font =("Courier"))
fileButton = tkinter.Button(scanFrame, text = "Upload Image",command = explore,height=2,width=40,bg="#d0bdf4")
fileButton.config(font =("Courier"))
spacer5= tkinter.Label(secondFrame, text="",height=7)
spacer5.config(bg='#494D5F')
spacer6= tkinter.Label(secondFrame, text="",height=1)
spacer6.config(bg='#494D5F')
spacer7= tkinter.Label(secondFrame, text="",height=1)
spacer7.config(bg='#494D5F')
spacer8= tkinter.Label(manualFrame, text="",height=7)
spacer8.config(bg='#494D5F')
spacer9= tkinter.Label(manualFrame, text="",height=1)
spacer9.config(bg='#494D5F')
spacer10= tkinter.Label(manualFrame, text="",height=1)
spacer10.config(bg='#494D5F')
spacer11= tkinter.Label(manualFrame, text="",height=1)
spacer11.config(bg='#494D5F')
spacer12= tkinter.Label(manualFrame, text="",height=1)
spacer12.config(bg='#494D5F')
spacer13= tkinter.Label(manualFrame, text="",height=1)
spacer13.config(bg='#494D5F')
spacer14= tkinter.Label(scanFrame, text="",height=7)
spacer14.config(bg='#494D5F')
spacer15= tkinter.Label(scanFrame, text="",height=1)
spacer15.config(bg='#494D5F')
spacer16= tkinter.Label(scanFrame, text="",height=1)
spacer16.config(bg='#494D5F')
spacer17= tkinter.Label(scanFrame, text="",height=1)
spacer17.config(bg='#494D5F')
spacer18= tkinter.Label(viewFrame, text="",height=7)
spacer18.config(bg='#494D5F')
spacer19= tkinter.Label(firstFrame, text="",height=6)
spacer19.config(bg='#494D5F')
spacer20= tkinter.Label(firstFrame, text="",height=1)
spacer20.config(bg='#494D5F')
spacer21= tkinter.Label(budgetFrame, text="",height=7)
spacer21.config(bg='#494D5F')
spacer22= tkinter.Label(budgetFrame, text="",height=1)
spacer22.config(bg='#494D5F')
spacer23= tkinter.Label(budgetFrame, text="",height=1)
spacer23.config(bg='#494D5F')
spacer24= tkinter.Label(budgetFrame, text="",height=1)
spacer24.config(bg='#494D5F')
spacer25= tkinter.Label(viewFrame, text="",height=7)
spacer25.config(bg='#494D5F')
spacer26= tkinter.Label(viewFrame, text="",height=1)
spacer26.config(bg='#494D5F')
spacer27= tkinter.Label(viewFrame, text="",height=1)
spacer27.config(bg='#494D5F')
spacer28= tkinter.Label(viewFrame, text="",height=1)
spacer28.config(bg='#494D5F')
spacer29= tkinter.Label(viewFrame, text="",height=1)
spacer29.config(bg='#494D5F')
spacer30= tkinter.Label(viewFrame, text="",height=1)
spacer30.config(bg='#494D5F')
spacer31= tkinter.Label(viewFrame, text="",height=1)
spacer31.config(bg='#494D5F')
spacer32= tkinter.Label(viewFrame, text="",height=1)
spacer32.config(bg='#494D5F')
spacer33= tkinter.Label(viewFrame, text="",height=1)
spacer33.config(bg='#494D5F')

options = ["Food","Transportation","Personal Spending","Electronics","Health/Selfcare","Entertainment","Other",]

clicked = StringVar()
clicked.set( "Catagory" )

cat = tkinter.OptionMenu( manualFrame, clicked, *options)
cat.config(width=37,height=2)
cat.config(font =("Courier"))
cat.config(bg="#d0bdf4")
cost = tkinter.Text(manualFrame, height = 3, width = 61)
catagoryTitle = tkinter.Label(manualFrame, text = "Catagory")
costTItle = tkinter.Label(manualFrame, text = 'Cost and Item (Input as "Cost, Item") ',bg='#494D5F')
costTItle.config(fg='#e5eaf5')
costTItle.config(font =("Courier"))
firstFrame.pack(fill="both",expand=1)
kush = tkinter.Label(budgetFrame, text = "Enter Budget")
kush.config(bg='#494D5F')
kush.config(fg='#e5eaf5')
kush.config(font =("Courier", 20))
budgetAmount = tkinter.Text(budgetFrame, height = 3, width = 61)
bud = tkinter.Button(budgetFrame, text = "Enter",command = enter4,height=2,width=40,bg="#d0bdf4")
bud.config(font =("Courier"))

spacer19.pack()
#linkName.pack()
#spacer20.pack()
editBudgetButton.pack()
spacer1.pack()
#l.pack()
#spacer3.pack()
b4.pack()
spacer4.pack()
b5.pack()
spacer.pack()
b3.pack()
spacer2.pack()

spacer25.pack()
l9.pack()
spacer26.pack()
l10.pack()
spacer27.pack()
l11.pack()
spacer28.pack()
l12.pack()
spacer29.pack()
l13.pack()
spacer30.pack()
l14.pack()
spacer31.pack()
l15.pack()
spacer32.pack()
l16.pack()
spacer33.pack()

b2.pack()
spacer5.pack()
scanButton.pack()
spacer6.pack()
manualInput.pack()
spacer7.pack()
spacer8.pack()
cat.pack()
spacer10.pack()
costTItle.pack()
cost.pack()
spacer11.pack()
inputEnter.pack()
spacer9.pack()
spacer14.pack()
fileButton.pack()
spacer15.pack()
spacer18.pack()
spacer21.pack()
kush.pack()
spacer24.pack()
budgetAmount.pack()
spacer22.pack()
bud.pack()
BackButton.pack()
back2Button.pack()
back3Button.pack()
back4Button.pack()
spacer23.pack()

back5Button.pack()
#exploreButton.pack()

# Insert The Fact.
T.insert(tkinter.END, Fact)

tkinter.mainloop()
 