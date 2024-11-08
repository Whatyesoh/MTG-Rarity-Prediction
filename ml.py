import csv
import matplotlib.pyplot as plt
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
import math

cardList = []

with open('all_mtg_cards.csv', encoding="utf8") as csvFile:
    csvReader = csv.DictReader(csvFile)

    for card in csvReader:
        cardList.append(card)

numCards = 0

vanillaCards = {}

trainingSet = []
trainingSetClassifications = []

testSet = []
testSetClassifications = []

for card in cardList:
    if (card["text"] == "" and len(card["colors"]) == 5 and card["layout"] == "normal"):
        vanillaCard = [[0,round(float(card["power"])),round(float(card["cmc"])),round(float(card["cmc"]))-(.5*round(float(card["power"]))+.5*round(float(card["toughness"])))],[0,0,0,0]]
        if ((card["name"] in vanillaCards) == False):
            numCards += 1

            match card["colors"][2]:
                case "W":
                    vanillaCard[0][0] = 0
                case "U":
                    vanillaCard[0][0] = 0                    
                case "B":
                    vanillaCard[0][0] = 0
                case "R":
                    vanillaCard[0][0] = 0
                case "G":
                    vanillaCard[0][0] = 0

            match card["rarity"]:
                case "Common":
                    vanillaCard[1][0] = 1
                case "Uncommon":
                    vanillaCard[1][1] = 1                    
                case "Rare":
                    vanillaCard[1][2] = 1
                case "Mythic":
                    vanillaCard[1][3] = 1

            vanillaCards[card["name"]] = vanillaCard

            if (numCards > 200):
                testSet.append(vanillaCard[0])
                testSetClassifications.append(vanillaCard[1])
            else:
                trainingSet.append(vanillaCard[0])
                trainingSetClassifications.append(vanillaCard[1])

trainingSet = np.array(trainingSet)
trainingSetClassifications = np.array(trainingSetClassifications)

testSet = np.array(testSet)
testSetClassifications = np.array(testSetClassifications)

scaler = StandardScaler()

scaler.fit(trainingSet)

trainingStandardised = scaler.transform(trainingSet)
testStandardised = scaler.transform(testSet)

pca = PCA(n_components=2).fit(trainingStandardised)

trainingStandardised = pca.transform(trainingStandardised)
testStandardised = pca.transform(testStandardised)

scaler = StandardScaler().fit(trainingStandardised)

trainingStandardised = scaler.transform(trainingStandardised)
testStandardised = scaler.transform(testStandardised)



def plotDataset(dataset, classification, subplot):
    class0 = []
    class1 = []
    class2 = []

    for i in range(0,len(dataset)):
        if (classification[i][0] == 1):
            class0.append(i)
        if (classification[i][1] == 1):
            class1.append(i)
        if (classification[i][2] == 1):
            class2.append(i)

    subplot.scatter(
        dataset[class0, 0], dataset[class0, 1], color="r", edgecolor="k"
    )
    subplot.scatter(
        dataset[class1, 0], dataset[class1, 1], color="g", edgecolor="k"
    )
    subplot.scatter(
        dataset[class2, 0], dataset[class2, 1], color="b", edgecolor="k"
    )

logCommon = LogisticRegression(random_state=0).fit(trainingStandardised,[i[0] for i in trainingSetClassifications])
logUncommon = LogisticRegression(random_state=0).fit(trainingStandardised,[i[1] for i in trainingSetClassifications])
logRare = LogisticRegression(random_state=0).fit(trainingStandardised,[i[2] for i in trainingSetClassifications])

logCommon_train = logCommon.score(trainingStandardised,[i[0] for i in trainingSetClassifications])
logUncommon_train = logUncommon.score(trainingStandardised,[i[1] for i in trainingSetClassifications])
logRare_train = logRare.score(trainingStandardised,[i[2] for i in trainingSetClassifications])

logCommon_test = logCommon.score(testStandardised,[i[0] for i in testSetClassifications])
logUncommon_test = logUncommon.score(testStandardised,[i[1] for i in testSetClassifications])
logRare_test = logRare.score(testStandardised,[i[2] for i in testSetClassifications])

print(logCommon_train,logUncommon_train,logRare_train)
print(logCommon_test,logUncommon_test,logRare_test)

chartX = np.linspace(-2.5,3.5,50)
chartY = np.linspace(-1.5,9,50)

chartXY = []

for i in range(0,len(chartX)):
    for j in range(0,len(chartY)):
        chartXY.append([chartX[i],chartY[j]])

chartClassification = []

chartCommon = logCommon.predict_proba(chartXY)
chartUncommon = logUncommon.predict_proba(chartXY) * 3
chartRare = logRare.predict_proba(chartXY) * 3

for i in range(0,len(chartCommon)):
    if (chartCommon[i][1] > chartUncommon[i][1] and chartCommon[i][1] > chartRare[i][1]):
        chartClassification.append([1,0,0,0])
    elif (chartUncommon[i][1] > chartRare[i][1]):
        chartClassification.append([0,1,0,0])
    else:
        chartClassification.append([0,0,1,0])

chartClassification = np.array(chartClassification)
chartXY = np.array(chartXY)

testCommon = logCommon.predict_proba(testStandardised)
testUncommon = logUncommon.predict_proba(testStandardised) * 3
testRare = logRare.predict_proba(testStandardised) * 3

figure, axis = plt.subplots(2,2)

plotDataset(testStandardised,testSetClassifications,axis[1,0])

incorrect = 0
correct = 0

commons = 0
overall = 0

for i in testSetClassifications:
    if (i[0]==1):
        commons += 1
    overall += 1

for i in range(0,len(testCommon)):
    if (testCommon[i][1] > testUncommon[i][1] and testCommon[i][1] > testRare[i][1]):
        if (testSetClassifications[i][0] == 1):    
            testSetClassifications[i] = ([0,1,0,0])
            correct+=1
        else:
            testSetClassifications[i] = ([1,0,0,0])
            incorrect+=1
    elif (testUncommon[i][1] > testRare[i][1]):
        if (testSetClassifications[i][1] == 1):    
            testSetClassifications[i] = ([0,1,0,0])
            correct+=1
        else:
            testSetClassifications[i] = ([1,0,0,0])
            incorrect+=1
    else:
        if (testSetClassifications[i][2] == 1):    
            testSetClassifications[i] = ([0,1,0,0])
            correct+=1
        else:
            testSetClassifications[i] = ([1,0,0,0])
            incorrect+=1



plotDataset(trainingStandardised,trainingSetClassifications,axis[0,0])
plotDataset(chartXY,chartClassification,axis[0,1])
plotDataset(testStandardised,testSetClassifications,axis[1,1])

print(correct/(correct+incorrect),commons/overall)

axis[0,0].legend(["Common", "Uncommon","Rare"])
axis[0,0].set_title("Training Dataset")
axis[0,1].legend(["Common", "Uncommon","Rare"])
axis[0,1].set_title("Decision Boundry")
axis[1,0].legend(["Common", "Uncommon","Rare"])
axis[1,0].set_title("Test Dataset")
axis[1,1].legend(["Incorrect","Correct"])
axis[1,1].set_title("Test Dataset Prediction")
axis[0,0].set_xlim(-2.5,3.5)
axis[0,0].set_ylim(-2.5,10)
axis[0,1].set_xlim(-2.5,3.5)
axis[0,1].set_ylim(-2.5,10)
axis[1,1].set_xlim(-2.5,3.5)
axis[1,1].set_ylim(-2.5,10)
axis[1,0].set_xlim(-2.5,3.5)
axis[1,0].set_ylim(-2.5,10)
plt.show()
