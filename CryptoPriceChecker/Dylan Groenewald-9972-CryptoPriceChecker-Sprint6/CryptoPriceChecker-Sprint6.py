from operator import itemgetter
import bitmex
import json
import threading
from datetime import datetime
import winsound

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    CBLUEBG   = '\33[44m'
    CREDBG    = '\33[41m'
    CGREENBG  = '\33[42m'
    CYELLOW = '\33[33m'
    CBLACK  = '\33[30m'

class Tick():
    def __init__(self, time, price):
        self.time = time
        self.price = price
        

class PriceChecker():
    # Constructor 
    def __init__(self):
        self.levelsList = []      # call the @levelslist.setter method and pass it an empty list
        self.currentPrice = 0.0   # call the currentPrice.setter method and pass it 0.0
        self.BitmexClient = bitmex.bitmex(test=False)
        self.previousPrice = 0.0 # call the @previous Price.setter method and pass it as 0.0

    # Properties 
    # A property is defined like a method, but you use it in your 
    # code like a variable (no parentheses need to followed it when used in your code)
    # Refer: https://www.youtube.com/watch?v=jCzT9XFZ5bw
    # Refer BP411 slides: Week 2 - Chapter 10 - Slides about Encapsulation and properties 
    @property
    def levelsList(self):
        return self.__levelsList   #return the value of __levelsList
    @levelsList.setter
    def levelsList(self, newValue):  #set the value of __levelsList
        self.__levelsList = newValue    

    @property
    def currentPrice(self):           #return the value of __currentPrice
        return self.__currentPrice             

    @currentPrice.setter
    def currentPrice(self,NewValue):  #set the value of __currentPrice
        self.__currentPrice = NewValue              

    @property
    def previousPrice(self):
       return self.__previousPrice     #Return the value of __previousPrice
    @previousPrice.setter
    def previousPrice(self, newValue):
        self.__previousPrice = newValue  # Set the value of __previousPrice

    # Class Methods
    # =============

    # Method: Sort and Display the levelsList
    def displayList(self):
        print(chr(27) + "[2J") # Clear the screen
        print("Price Levels In The List")
        print("========================")
        # Sort the list in reverse order 
        n = len(self.levelsList)
        for i in range(n-1):
         for j in range(0,n-i-1):
          if self.levelsList[j] < self.levelsList[j +1]:
            self.levelsList[j],self.levelsList[j+1] = self.levelsList[j+1],self.levelsList[j]
        
        
        
        for i in range(n):
         print(self.levelsList[i])
          
    
        # Print the items in the list (Based on the above sort, numbers should appear from large to small.)
    

    # Display the menu and get user input about what methods to execute next
    def displayMenu(self):
        min = 0
        max = 5
        errorMsg = "Please enter a valid option between " + str(min) + " and " + str(max)

        print("MENU OPTIONS")
        print("============")
        print("1. Add a price level")
        print("2. Remove a price level")
        print("3. Remove all price levels")
        if(self.currentPrice > 0):
            print("4. Display the currnet bitcoin price here: " + f"${self.currentPrice:,}")
        else:
            print("4. Display the current bitcoin price here")
        print("5. start monitoring")
        print("0. Exit the program")
        print(" ")   
        
        # Get user input. Keep on requesting input until the user enters a valid number between min and max 
        selection = 99
        while selection < min or selection > max:
            try:
                selection = int(input("Please enter one of the options: "))
            except:
                print(errorMsg) # user did not enter a number
                continue # skip the following if statement
            if(selection < min or selection > max):
                print(errorMsg) # user entered a number outside the required range
        return selection # When this return is finally reached, selection will have a value between (and including) min and max

    # Method: Append a new price level to the levelsList
    def addLevel(self):
        try:
            # Let the user enter a new float value and append it to the list  
         arrNew = []
         newNum = float(input("Enter a price level to add to list:"))   
         arrNew.append(newNum)
         self.levelsList = self.levelsList + arrNew
        except:
            print("Invalid Value")
            

    # Method: Remove an existing price level from the levelsList
    def removeLevel(self):
        try:
            # Let the user enter a new float value. If found in the list, remove it from the list
            self.levelsList.remove(float(input("Enter a float value you wish to remove: ")))
        except:
            # Print and error message if the user entered invalid input
            print("Invalid value was entered")

    # Method: Set levelsList to an empty list
    def removeAllLevels(self):
        # Set levelsList to an empty list
        self.levelsList.clear()
    # Method: Load levelslist using the data in levelsFile
    def readLevelsFromFile(self):
        try:
            #set levelsList to an empty list
            self.levelsList = []
            
            #open the file
            file = open('levelsFile.txt',"r")
            #use a loop to read through the file line by line
            n = len(file.readlines())
            file.seek(0,0)
            for i in range(n):
                line = file.readline()
                #if the last two characters in the line is "\n",remove them
                if(line == '\n'):
                    if(line == '\n'):
                             line = ''             
                #append the line to levelsList
                self.levelsList.append(float(line))
            #close the file
            file.close()
           
        except:
            return
    #Method: Write levelslist to levelsFile(overide the existing file)
    def writeLevelsToFile(self):
        #open the file in a way that will override the existing file (if it already exists)
        file = open('levelsFile.txt',"w+")
        #use a loop to iterate over levelslist item by item
        n = len(self.levelsList)
        for i in range(n):
            items = str(self.levelsList[i])
             #convert everything in the item to a string and then add \n to it - before writing it to the file
            file.write(items+"\n")

        #close the file
        file.close()

    # Function: Display the Bitcoin price in the menu item - to assist the user when setting price levels
    def updateMenuPrice(self):
        # Get the latest Bitcoin info (as a Tick object) from GetBitMexPrice(). name it tickobj.
        tickObj = self.getBitMexPrice()
        #update the currentPrice property with the bitcoin price in tickObj.
        self.currentPrice = tickObj.price
    # Function: call the Bitmex Exchange
    def getBitMexPrice(self):
        #send a request to the exchange for Bitcoin's data in $USD ("XBTUSD").
        #The json response is converted into a tuple which we name responseTuple.
        responseTuple = self.BitmexClient.Instrument.Instrument_get(filter=json.dumps({'symbol':'XBTUSD'})).result()
        #The tuple consist of the bitcoin information (in the form of a dictionary with key>value pairs) plus
        #some additional meta data rreceived from the exchange.
        #extractonly the dictionary (Bitcoin information) from the tuple.
        responseDictionary = responseTuple[0:1][0][0]
        #Create a Tick object and set its variables to the timestamp and lastPrice data from the dictionary.
        return Tick(responseDictionary["timestamp"], responseDictionary["lastPrice"])

    #once this method has been called, it uses a Timer toexecute every 2 seconds
    def monitorLevels(self):
        #Create timer to call this method every 2 seconds
        threading.Timer(2.0, self.monitorLevels).start()

        #Since we will obtain the latest current price from the exchange,
        #store the existing value of currentPrice in previousPrice
        self.previousPrice = self.currentPrice

        # Similar to  updateMenuPrice(),call the getBitMexPrice() Methode to get
        # a Ticker object containing the Latest Bitcoin information. then store
        # the Bitcoin price in currentPrice
        tickObj = self.getBitMexPrice()
        self.currentPrice = tickObj.price
        # During the first loop of this method, previousPrice will still be 0 here,
        # because it was set to currentPrice above, whice also was 0 before we updated
        # it above via getBitMexPrice().
        # So, when we reach this point during the first loop, previousPrice will be 0
        # while cirrentPrice would have just been updated via getBitMexPrice().
        # We don't want to create the impression that the price shot up from 0 to
        # currentPrice.
        # Therefore, if previousPrice == 0.0, it must be set equal to currentPrice here. 
        if(self.previousPrice == 0.0):
            self.previousPrice = self.currentPrice

        # Print the current data and time plus instructions for stopping the app while this
        # method is looping.
        print("")
        print("Price Check at "+ str(datetime.now()) + "  (Press Ctrl + c to stop the monitoring)")
        print("==================================================================================")

        # Each time this method executes, we want to print the items in levelsList togeter with previousPrice
        # and curentPrice in the right order. However, as we loop through levelsList, how do we know were to
        # insert previousPrice and currentPrice - especially if currentPrice crossed one or two of our price 
        # levels?
        # we could try to use an elaborate set of IF-statements (I dare you to try this), but a much easier
        # way is to simply add previousPrice and currentPrice to the list and then sort the list.
        #
        # However, we cannot simply use levelsList for this purpose, because it only stores values, while we
        # also want to print labeling text with these values  - such as "Price Level" , "Current Price" and
        # "Previous Price".
        # Therefore, we need to create a temporary list - called displayList - used for displaying purposes only.
        # this new list must consist of sub-lists. Each sub-List will contain two items.
        # the first item will be the label we want to print - consisting of the labeling text and the price.
        # the second item consists of the price only.
        # we will use the second item to sort the list - since it makes no sence to sort the list based on
        # the label (the first item).
        #
        # Example of displayList (containing sub-lists) after it was sorted:
        #
        #    [
        #         ["Price Level: 9700.00", 9700.00     ]
        #         ["Price Level: 9690.00", 9690.00     ]  
        #         ["Current Price: 9700.00", 9700.00   ]
        #         ["Previous Price: 9700.00", 9700.00  ]
        #         ["Price Level: 9700.00", 9700.00     ]
        #    ]
        
        # Create displayList
        displayList = []

        # loop through the price in levelsList.
        # During each loop:
        # - create a variable called priceLevelLabel consisting of the text "Price level: "followed
        # by the price.
        # - Add priceLevelLabel and the price as two separate items to a new list (the sub-list).
        # - Append the sub-List to displayList.
        subList = []
        for price in self.levelsList:
            priceLevelLabel = "Price level: "+ str(price)
            subList.append(priceLevelLabel)
            subList.append(price)
            displayList.append(subList)
            subList = []
    


        # Create a variable called previousPriceLabel consisting of the text "previous Price:" followed 
        # by previousPrice.
        # Format the background colour of previousPriceLabel to be blue. Refer to the following site:
        # https://stackoverflow.com/questions/287871/how-to-print-colored-text-in-terminal-in-python
        # Follow the above site to add special text characters to the label, which the console will interpret
        # as backround colour settings. If the above site's code does not work for your console (I am using
        # Visual Studio Code), resesrch a different way for setting the background colour.
        # Add previousPriceLabel and previousPrice as two seperate items to a new list (the sub-list)
        # append the sub-list to displaylist
        previousPriceLabel = f"{bcolors.CBLUEBG}{bcolors.OKGREEN}Previous Price: " + str(self.previousPrice)+f"{bcolors.ENDC}"
        subList.append(previousPriceLabel)
        subList.append(self.previousPrice)
        displayList.append(subList)
        subList = []
     

        # Create a varible called currentPrice consisting of the text "Current Price: "followed
        # by currentPrice.
        # Format the background colour of currentPriceLabel as follows:
        # - if currentPrice > previousPrice: set currentPriceLabel background colour to green 
        # - if currentPrice < previousPrice: set currentPriceLabel background colour to red
        # - if currentPrice == previousPrice: set currentPriceLabel background colour to blue 
        # add currentPriceLabel and previousPrice as two seperate items to a new list (the sub-List).
        #Append the sub-list to displayList.
    
        currentPrice = "current Price: "+ str(self.currentPrice)
        if (self.currentPrice > self.previousPrice):
                currentPrice = f"{bcolors.CGREENBG}{bcolors.CBLACK}current Price: " + str(self.currentPrice)+f"{bcolors.ENDC}"
        elif(self.currentPrice < self.previousPrice):
             currentPrice = f"{bcolors.CREDBG}{bcolors.CYELLOW}current Price: " + str(self.currentPrice)+f"{bcolors.ENDC}"
        elif(self.currentPrice == self.previousPrice):
             currentPrice = f"{bcolors.CBLUEBG}{bcolors.OKGREEN}current Price: " + str(self.currentPrice)+f"{bcolors.ENDC}"
        subList.append(currentPrice)
        subList.append(self.currentPrice)
        displayList.append(subList)
        subList = []
        

        #sort displyList using the Second item(price) in its sub-Lists
        subllist = sorted(displayList,key=itemgetter(1),reverse=False)

        # for each sub-list in displayList, print only the label (first item) in the sub-list
        for i in range(0,len(displayList)):
            print(subllist[i][0])


        # loop through displayList
        for i in range(0,len(subllist)):
            if ("Price level" in subllist[i][0]):

            # Test if the first item in the current sub-list contains the text "Price level"
            # TIp: remember that each sub-list is a list within a list (displayList). so you have
            # to access its items via displayList followed by TWO indexes.
                pricelevel = subllist[i][1]
              # Extract the second item from the current sub-list into a variable called pricelevel
              # Test if pricelevel is between previousPrice and currentPrice OR
              #         pricelevel == previousPrice OR
              #         pricelevel == currentPrice
                if(self.currentPrice <= pricelevel <= self.previousPrice) or (self.currentPrice >= pricelevel >= self.previousPrice) or (pricelevel == self.previousPrice) or(pricelevel == self.currentPrice):
                  ## sound the alarm. pass in the frequency and duration. 
                  if self.currentPrice > self.previousPrice:
                      frequency = 800
                      duration = 700
                      winsound.Beep(frequency,duration)
                  else:
                      frequency = 400
                      duration = 700
                      winsound.Beep(frequency,duration)

                      # Print the Text "Alarm" with a green background colour, so that the user
                      # can go back into the historical data to see what prices raised the alarm.
                      print(f"{bcolors.CGREENBG}{bcolors.CBLACK}ALARM!"+f"{bcolors.ENDC}")


        

# *************************************************************************************************
#                                           Main Code Section
# *************************************************************************************************

# Create an object based on the PriceChecker class
checkerObj = PriceChecker()

# load levelslist from the records in levelsFile
checkerObj.readLevelsFromFile()

# Display the levelsList and Menu; and then get user input for what actions to take
userInput = 99
while userInput != 0:
    checkerObj.displayList()
    userInput = checkerObj.displayMenu()
    if(userInput == 1):
        checkerObj.addLevel()
        checkerObj.writeLevelsToFile() #Write levelsList to levelsFile
    elif(userInput == 2):
        checkerObj.removeLevel()
        checkerObj.writeLevelsToFile() #Write levelsList to levelsFile
    elif(userInput == 3):
        checkerObj.removeAllLevels()
        checkerObj.writeLevelsToFile() #Write levelsList to levelsFile
    elif(userInput == 4):
        checkerObj.updateMenuPrice()
    elif(userInput == 5):
        userInput = 0 # prevents the app from continuing is the user pressd Ctrl+c to stop it
        checkerObj.monitorLevels()