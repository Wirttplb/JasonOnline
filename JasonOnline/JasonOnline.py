from subprocess import *
import time
import pyautogui
import string
from operator import add
import keyboard

import math
import numpy as np

JasonExe = 'C:\SOURCE\JasonOnline\JasonUCI.exe'

#Chessboard has to be in white point of view!!
#Board corners coordinates in chess.com window
topLeftCorner = [385, 140]
bottomLeftCorner = [385, 955]
topRightCorner = [1200, 140]
bottomRightCorner = [1200, 955]
#Square size
dX = (topRightCorner[0] - topLeftCorner[0]) / 8
dY = (bottomLeftCorner[1] - topLeftCorner[1]) / 8
#Chess.com square colors
highlightLightSquare = [187, 203, 43] #two different moved pieces colors (according to light or dark square)
highlightDarkSquare = [247, 247, 105]
greenSquare = [118, 150,  86]

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

whitePieces = [[1, 1], [2, 1], [3, 1], [4, 1], [5, 1], [6, 1], [7, 1], [8, 1], [1, 2], [2, 2], [3, 2], [4, 2], [5, 2], [6, 2], [7, 2], [8, 2]]
blackPieces = [[1, 8], [2, 8], [3, 8], [4, 8], [5, 8], [6, 8], [7, 8], [8, 8], [1, 7], [2, 7], [3, 7], [4, 7], [5, 7], [6, 7], [7, 7], [8, 7]]

def rotate(l, n):
    return l[n:] + l[:n]

def GetOpponentMove(isJasonWhite):
    screenScreenshot = pyautogui.screenshot()
    s = np.array(screenScreenshot)

    moveSquares = []
    #440, 200 to 475, 160
    shift = [35, -40]#shift from center to get color of square and not piece

    for i in range(1, 9):

        for j in range(1, 9):
            [x, y] = GetSquareScreenCoordinates(i, j)
            [x, y] = list(map(add, [x, y], shift))
            color = s[int(y)][int(x)]
            if (i == 7 and j == 8):
                eheh = ""
            if (i == 6 and j == 6):
                eheh = ""

            dRGB2 = min(ColorDistance(color, highlightLightSquare), ColorDistance(color, highlightDarkSquare))
            if (dRGB2 < 5.0):
                moveSquares.append([i,j])
            if (len(moveSquares) == 2):
                break

        if (len(moveSquares) == 2):
            break

    if (moveSquares == []):
        return "" #opponent has not played yet

    if (len(moveSquares) != 2):
        raise SystemExit('Invalid mode read!')

    friendlyPieces = whitePieces
    if isJasonWhite:
        friendlyPieces = blackPieces

    if (moveSquares[0] not in friendlyPieces and moveSquares[1] not in friendlyPieces):
        return "" #still reading last move, opponent has not played yet
    if (moveSquares[0] not in friendlyPieces):
        moveSquares = rotate(moveSquares, 1)

    return MoveSquaresToMoveString(moveSquares)

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

def main():

    #FOR TESTING MOUSE INPUT/OUTPUT
    #while True:
    #    x, y = pyautogui.position()
    #    scrnn = pyautogui.screenshot()
    #    s = np.array(scrnn)
    #    color = s[int(y)][int(x)]
    #    print(str(x) + ', ' + str(y) + ' color: ' + str(color[0]) + ' ' + str(color[1]) + ' ' + str(color[2]))
    #    time.sleep(0.1)

    isJasonWhite = True
    jasonColor = input("Jason plays Black or White? (B/W): ")
    time.sleep(2.0)

    moves = ""
    if jasonColor == 'B':
        isJasonWhite = False
        #Get opponent move
        opponentMoveString = ""
        while (opponentMoveString == ""):
            time.sleep(1.0)
            opponentMoveString = GetOpponentMove(isJasonWhite)
        UpdatePieceLists(opponentMoveString)
        moves += opponentMoveString + " "

    p = Popen([JasonExe], stdout=PIPE, stdin=PIPE, stderr=PIPE, universal_newlines=True)

    while True: #Game loop

        if keyboard.is_pressed('c') and keyboard.is_pressed('ctrl'):
            break #kill keyboard command

        p.stdin.write("position startpos moves " + moves + '\n')
        p.stdin.write("go wtime 10000 btime 10000\n") #10s max
        p.stdin.flush() 
        bestmove = p.stdout.readline()
        print(bestmove)
        print(p.stdout.readline()) #print move info
        #Make move with mouse
        bestmove = bestmove.replace("bestmove ", "")
        bestmove = bestmove[0:4]
        [fromCoordinates , toCoordinates] = MoveStringToScreenCoordinates(bestmove)
        pyautogui.click(fromCoordinates[0], fromCoordinates[1])
        time.sleep(0.3)
        pyautogui.click(toCoordinates[0], toCoordinates[1])

        #Update piece lists
        UpdatePieceLists(bestmove)
        moves += bestmove + " "

        #Get opponent move
        opponentMoveString = ""
        while (opponentMoveString == ""):
            time.sleep(1.0)
            opponentMoveString = GetOpponentMove(isJasonWhite)
        UpdatePieceLists(opponentMoveString)
        moves += opponentMoveString + " "


if __name__ == "__main__":
    main()

