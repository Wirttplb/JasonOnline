from subprocess import *
import time
import pyautogui
import string
from operator import add
import keyboard

import math
import random
import numpy as np

JasonExe = 'C:\SOURCE\JasonOnline\JasonUCI.exe'

#Chessboard has to be in white point of view!! (for now)
#Board corners coordinates in window
topLeftCorner = [270, 140]
bottomLeftCorner = [270, 970]
topRightCorner = [1105, 140]
bottomRightCorner = [1105, 970]
#Against computer:
#topLeftCorner = [385, 140]
#bottomLeftCorner = [385, 955]
#topRightCorner = [1200, 140]
#bottomRightCorner = [1200, 955]
#Square size
dX = (topRightCorner[0] - topLeftCorner[0]) / 8
dY = (bottomLeftCorner[1] - topLeftCorner[1]) / 8
#Square colors
highlightLightSquare = [187, 203, 43] #two different moved pieces colors (according to light or dark square)
highlightDarkSquare = [247, 247, 105]
greenSquare = [118, 150,  86]
#To find computer's color
topPortrait = [290, 110]
topPortraitRematch = [330, 110]
bottomPortrait = [290, 1000]
bottomPortraitRematch = [330, 1000]
jasonPortraitColor = [128, 0, 128]
#Button positions
newGameButton = [1500, 750]
#Game ended pop up
gameEndPopupColor = [255, 255, 255]
gameEndPopup = [690, 590]

def MoveStringToSquares(moveString):
    fromX = FileLetterToIdx(moveString[0])
    fromY = int(moveString[1])
    toX = FileLetterToIdx(moveString[2])
    toY = int(moveString[3])
    return [[fromX, fromY], [toX, toY]]

def GetSquareScreenCoordinates(file, row):
    fileShift = file - 1
    rowShift = row - 1
    coordinates = list(map(add, bottomLeftCorner, [(0.5 + fileShift) * dX, -(0.5 + rowShift) *dY]))
    return coordinates

def FileLetterToIdx(file):
    return (string.ascii_lowercase.index(file)) + 1

def MoveStringToScreenCoordinates(moveString):
    [[fromX, fromY], [toX, toY]] = MoveStringToSquares(moveString)
    return [GetSquareScreenCoordinates(fromX, fromY), GetSquareScreenCoordinates(toX, toY)]

files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
def MoveSquaresToMoveString(moveSquares):
    moveString = ""
    moveString += files[moveSquares[0][0] - 1]
    moveString += str(moveSquares[0][1])
    moveString += files[moveSquares[1][0] - 1]
    moveString += str(moveSquares[1][1])
    return moveString

def ColorDistance(color1, color2):
    dR = (color1[0] - color2[0])
    dG = (color1[1] - color2[1])
    dB = (color1[2] - color2[2])
    return math.sqrt(dR*dR + dG*dG + dB*dB)


def InitBoard():
    global whitePieces
    global blackPieces
    global canWhiteOO
    global canWhiteOOO
    global canBlackOO
    global canBlackOOO
    whitePieces = [[1, 1], [2, 1], [3, 1], [4, 1], [5, 1], [6, 1], [7, 1], [8, 1], [1, 2], [2, 2], [3, 2], [4, 2], [5, 2], [6, 2], [7, 2], [8, 2]]
    blackPieces = [[1, 8], [2, 8], [3, 8], [4, 8], [5, 8], [6, 8], [7, 8], [8, 8], [1, 7], [2, 7], [3, 7], [4, 7], [5, 7], [6, 7], [7, 7], [8, 7]]
    canWhiteOO = True
    canWhiteOOO = True
    canBlackOO = True
    canBlackOOO = True

def rotate(l, n):
    return l[n:] + l[:n]

def GetOpponentMove(isJasonWhite):
    screenScreenshot = pyautogui.screenshot()
    s = np.array(screenScreenshot)

    moveSquares = []
    #440, 200 to 475, 160 (against computer)
    #330, 930 to 365, 890 (against human)
    shift = [35, -40]#shift from center to get color of square and not piece

    for i in range(1, 9):

        for j in range(1, 9):
            [x, y] = GetSquareScreenCoordinates(i, j)
            [x, y] = list(map(add, [x, y], shift))
            color = s[int(y)][int(x)]
            dRGB = min(ColorDistance(color, highlightLightSquare), ColorDistance(color, highlightDarkSquare))
            if (dRGB < 10.0):
                moveSquares.append([i,j])
            if (len(moveSquares) == 2):
                break

        if (len(moveSquares) == 2):
            break

    if (moveSquares == []):
        return "" #opponent has not played yet

    if (len(moveSquares) != 2):
        return "" #page still refreshing?   ###raise SystemExit('Invalid mode read!')

    friendlyPieces = whitePieces
    if isJasonWhite:
        friendlyPieces = blackPieces

    if (moveSquares[0] not in friendlyPieces and moveSquares[1] not in friendlyPieces):
        return "" #still reading last move, opponent has not played yet
    if (moveSquares[0] not in friendlyPieces):
        moveSquares = rotate(moveSquares, 1)

    return MoveSquaresToMoveString(moveSquares)

def IsWhiteOO(moveString):
    return ((moveString == "e1g1") and canWhiteOO)

def IsWhiteOOO(moveString):
    return ((moveString == "e1c1") and canWhiteOOO)

def IsBlackOO(moveString):
    return ((moveString == "e8g8") and canBlackOO)

def IsBlackOOO(moveString):
    return ((moveString == "e8c8") and canBlackOOO)

def UpdatePieceLists(moveString):
    [fromSq, toSq] = MoveStringToSquares(moveString)
    if (fromSq in whitePieces):
        whitePieces.remove(fromSq)
        whitePieces.append(toSq)
        if (toSq in blackPieces):
            blackPieces.remove(toSq)
    else:
        if (fromSq not in blackPieces):
            raise SystemExit('Invalid piece lists update!')
        blackPieces.remove(fromSq)
        blackPieces.append(toSq)
        if (toSq in whitePieces):
            whitePieces.remove(toSq)

    #Rook to update for castles  
    if IsWhiteOO(moveString):
        whitePieces.remove([8, 1])
        whitePieces.append([6, 1])
    elif IsWhiteOOO(moveString):
        whitePieces.remove([1, 1])
        whitePieces.append([4, 1])
    elif IsBlackOO(moveString):
        blackPieces.remove([8, 8])
        blackPieces.append([6, 8])
    elif IsBlackOOO(moveString):
        blackPieces.remove([1, 8])
        blackPieces.append([4, 8])

    #Update castle flags (we dont care about rook captures, we just check if king has moved)
    if (fromSq[0] == 5 and fromSq[1] == 1):
        global canWhiteOO
        global canWhiteOOO
        canWhiteOO = False
        canWhiteOOO = False
    if (fromSq[0] == 5 and fromSq[1] == 8):
        global canBlackOO
        global canBlackOOO
        canBlackOO = False
        canBlackOOO = False


def GetJasonColor(): #return True for white
    screenScreenshot = pyautogui.screenshot()
    s = np.array(screenScreenshot)
    bottomColor = s[bottomPortrait[1]][bottomPortrait[0]]
    bottomColorRematch = s[bottomPortraitRematch[1]][bottomPortraitRematch[0]]
    dRGB = min(ColorDistance(bottomColor, jasonPortraitColor), ColorDistance(bottomColorRematch, jasonPortraitColor))
    return (dRGB < 3)

def IsGameFinished():
    screenScreenshot = pyautogui.screenshot()
    s = np.array(screenScreenshot)
    color = s[gameEndPopup[1]][gameEndPopup[0]]
    dRGB = ColorDistance(color, gameEndPopupColor)
    return (dRGB < 3)

def PlayGame():

    #FOR TESTING MOUSE INPUT/OUTPUT
    #while True:
    #    x, y = pyautogui.position()
    #    scrnn = pyautogui.screenshot()
    #    s = np.array(scrnn)
    #    color = s[int(y)][int(x)]
    #    print(str(x) + ', ' + str(y) + ' color: ' + str(color[0]) + ' ' + str(color[1]) + ' ' + str(color[2]))
    #    time.sleep(0.1)

    InitBoard()
    isJasonWhite = True
    #jasonColor = input("Jason plays Black or White? (B/W): ")
    #if (jasonColor == 'B'):
    #    isJasonWhite = False
    time.sleep(2.0)
    isJasonWhite = GetJasonColor()

    moves = ""
    if not isJasonWhite:
        #Get opponent move
        opponentMoveString = ""
        while (opponentMoveString == ""):
            time.sleep(1.0)
            opponentMoveString = GetOpponentMove(isJasonWhite)
        UpdatePieceLists(opponentMoveString)
        moves += opponentMoveString + " "

    p = Popen([JasonExe], stdout=PIPE, stdin=PIPE, stderr=PIPE, universal_newlines=True)

    isFirstMove = True;
    isGameRunning = True
    while isGameRunning: #Game loop

        if (IsGameFinished()):
            return

        if keyboard.is_pressed('c') and keyboard.is_pressed('ctrl'):
            break #kill keyboard command

        #Send uci command
        goStartTime = time.time()
        p.stdin.write("position startpos moves " + moves + '\n')
        p.stdin.write("go movetime 5000\n") #5s max
        p.stdin.flush() 
        bestmove = p.stdout.readline()
        print(bestmove)
        if (bestmove.find("no move found") > -1):
            return

        print(p.stdout.readline()) #print move info
        bestmove = bestmove.replace("bestmove ", "")
        bestmove = bestmove[0:4]
        spentTime = time.time() - goStartTime

        if (IsGameFinished()):
            return

        [fromCoordinates , toCoordinates] = MoveStringToScreenCoordinates(bestmove)

        #Add random sleep duration for more humanlike behavior
        maxTimePerMove = 13 #increased from 10
        if (not isFirstMove):
            maxTimeToWait = max(0, maxTimePerMove - spentTime)
            maxTimeToWait = math.floor(maxTimeToWait)
            time.sleep(random.randint(min(2, maxTimeToWait), maxTimeToWait))

        #Make move with mouse
        #fast mouse command:
        #pyautogui.click(fromCoordinates[0], fromCoordinates[1])
        #pyautogui.click(toCoordinates[0], toCoordinates[1])
        #random mouse move time and add some noise on square center coordinates (more "humanlike")
        mouseDragDuration = 0.1 * random.randint(0, 2) #0.1 to 0.2s
        mouseDragDuration2 = 0.1 * random.randint(0, 2) #0.1 to 0.2s
        pyautogui.moveTo(fromCoordinates[0] + random.randint(-10, 10), fromCoordinates[1] + random.randint(-10, 10), mouseDragDuration, pyautogui.easeInBounce)
        pyautogui.click()
        pyautogui.moveTo(toCoordinates[0] + random.randint(-10, 10), toCoordinates[1] + random.randint(-10, 10), mouseDragDuration2, pyautogui.easeInBounce)
        pyautogui.click()

        #Update piece lists
        UpdatePieceLists(bestmove)
        moves += bestmove + " "

        if (IsGameFinished()):
            return

        #Get opponent move
        opponentMoveString = ""
        while (opponentMoveString == ""):

            if (IsGameFinished()):
                return

            time.sleep(1.0)
            opponentMoveString = GetOpponentMove(isJasonWhite)

        UpdatePieceLists(opponentMoveString)
        moves += opponentMoveString + " "

        isFirstMove = False


def main():
    
    #PlayGame()
    time.sleep(2)
    #New game loop, should be run from live game screen
    while True:
        mouseDragDuration = 0.1 * random.randint(0, 2) #0.1 to 0.2s 
        pyautogui.moveTo(newGameButton[0] + random.randint(-10, 10), newGameButton[1] + random.randint(-10, 10), mouseDragDuration, pyautogui.easeInBounce)
        pyautogui.click()
        time.sleep(10)

        if (not IsGameFinished()):
            PlayGame()
            time.sleep(random.randint(20, 60)) #wait 20s to 1 min before next game

            

if __name__ == "__main__":
    main()

