#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile
from pybricks import ev3brick as brick

import ubinascii, urequests, ujson, utime
import passwords

# Write your program here
ev3 = EV3Brick()

draw = Motor(Port.C)
conveyor = Motor(Port.B)
dump = Motor(Port.A)
ballRelease = Motor(Port.D)

playerHand = []
playerTotal = 0
dealerHand = []
dealerTotal = 0

#initialize player and dealer hands as hard
playerSoft = False
dealerSoft = False

WIN = False
LOSE = False

def SL_setup():
     urlBase = "https://api.systemlinkcloud.com/nitag/v2/tags/"
     headers = {"Accept":"application/json","x-ni-api-key":Key}
     return urlBase, headers
     
def Put_SL(Tag, Type, Value):
     urlBase, headers = SL_setup()
     urlValue = urlBase + Tag + "/values/current"
     propValue = {"value":{"type":Type,"value":Value}}
     try:
          reply = urequests.put(urlValue,headers=headers,json=propValue).text
     except Exception as e:
          print(e)         
          reply = 'failed'
     return reply

def Get_SL(Tag):
     urlBase, headers = SL_setup()
     urlValue = urlBase + Tag + "/values/current"
     try:
          value = urequests.get(urlValue,headers=headers).text
          data = ujson.loads(value)
          #print(data)
          result = data.get("value").get("value")
     except Exception as e:
          print(e)
          result = 'failed'
     return result
     
def Create_SL(Tag, Type):
     urlBase, headers = SL_setup()
     urlTag = urlBase + Tag
     propName={"type":Type,"path":Tag}
     try:
          urequests.put(urlTag,headers=headers,json=propName).text
     except Exception as e:
          print(e)

def Draw_Card():
     #take a card off the top of the deck
     draw.run_angle(-200, 300)
     draw.run_angle(100, 100)

     #move the card to the edge of the conveyer
     conveyor.run_angle(200, 300)

     #drop the card to the viewer
     dump.run_angle(-100, 90)
     dump.run_angle(100, 90)

     #get card from teachable machines
     Put_SL("take_pic", "STRING", '1')
     pic = "1"
     while pic == "1":
          pic = Get_SL("take_pic")
          card = Get_SL("cardVal")

     print(card)
     return card

def Player_Draws():
     global playerHand

     #draw a card and add it to the end of the playerHand
     card = Draw_Card()
     if card == "A":
          playerHand.append(card)
     elif card == "F":
          playerHand.append(10)
     else:
          playerHand.append(int(card))

def Dealer_Draws():
     global dealerHand

     card = Draw_Card()
     if card == "A":
          dealerHand.append(card)
     elif card == "F":
          dealerHand.append(10)
     else:
          dealerHand.append(int(card))

def player_Decision(total):
     global playerHand
     global dealerUp
     global playerSoft

     if total > 21:
          #YOU LOSE
          LOSE = True
          return 0
     elif total == 21:
          #YOU WIN
          WIN = True
          return 21

     if playerSoft:
          if total <= 17:
               Player_Soft_Hit(total)
          elif (total == 18) and (dealerUp >= 9):
               Player_Soft_Hit(total)
     else:
          if total <= 11:
               Player_Hard_Hit(total)
          elif (13 <= total <= 16) and (dealerUp >= 7):
               Player_Hard_Hit(total)
          elif (total == 12) and ((dealerUp >= 7) or (dealerUp <= 3)):
               Player_Hard_Hit(total)

     return total

def dealer_Decision(total):
     global dealerHand
     global dealerSoft

     if total > 21:
          WIN = True
          return 0
     
     if total < 17:
          if dealerSoft:
               Dealer_Soft_Hit(total)
          else:
               Dealer_Hard_Hit(total)
     return total

def Player_Soft_Hit(total):
     global playerHand
     global playerSoft

     Player_Draws()
     if playerHand[-1] == 'A':
          total = total + 1
     else:
          total = total + playerHand[-1]
     
     if total > 21:
          total = total - 10
          playerSoft = False
     
     #call decision making function here
     player_Decision(total)
               
def Player_Hard_Hit(total):
     global playerHand
     global playerSoft

     Player_Draws()
     if playerHand[-1] == 'A':
          if total <= 10:
               total = total + 11
               playerSoft = True
          else:
               total = total + 1
     else:
          total = total + playerHand[-1]
     
     player_Decision(total)
     
def Dealer_Soft_Hit(total):
     global dealerHand
     global dealerSoft

     Dealer_Draws()
     if dealerHand[-1] == 'A':
          total = total + 1
     else:
          total = total + dealerHand[-1]
     
     if total > 21:
          total = total - 10
          dealerSoft = False
     
     #call decision making function here
     dealer_Decision(total)

def Dealer_Hard_Hit(total):
     global dealerHand
     global dealerSoft

     Dealer_Draws()
     if dealerHand[-1] == 'A':
          if total <= 10:
               total = total + 11
               dealerSoft = True
          else:
               total = total + 1
     else:
          total = total + dealerHand[-1]
     
     dealer_Decision(total)

ev3.speaker.beep()

Key = passwords.classKey

#wait to start until allowed
start = Get_SL("Start22")
while(start == 'false'):
    wait(100)
    start = Get_SL("Start22")

#switch to using my systemlink
Key = passwords.myKey

#initial drawing phase
print("Player Card:")
Player_Draws()
print("Dealer Up Card:")
Dealer_Draws()
print("Player Card:")
Player_Draws()

#do something with dealerhand to find initial total for comparisons
if dealerHand[0] == 'A':
     dealerUp = 11
else:
     dealerUp = dealerHand[0]

#determine player total here:
for i in range(2):
     if playerHand[i] == "A":
          playerTotal += 11
          playerSoft = True
     else:
          playerTotal += playerHand[i]

#in case of two Aces
if playerTotal == 22:
     playerTotal = 12

print("Player's Turn: ")
playerTotal = player_Decision(playerTotal)


#if player didn't get blackjack or bust dealer goes
if (WIN == False) and (LOSE == False):
     print("Dealer's Turn")
     Dealer_Draws()
     #determine dealer total here:
     for i in range(2):
          if dealerHand[i] == "A":
               dealerTotal += 11
               dealerSoft = True
          else:
               dealerTotal += dealerHand[i]

     #in case of two Aces
     if dealerTotal == 22:
          dealerTotal = 12
     
     dealerTotal = dealer_Decision(dealerTotal)


if (WIN == False) and (LOSE == False):
     if dealerTotal > playerTotal:
          LOSE = True
     else:
          WIN = True

print("Player's hand: ")
print(playerHand)
print("Dealer's hand: ")
print(dealerHand)
if WIN:
     print("YOU WIN")
     ballRelease.run_angle(100, 200)
elif LOSE:
     print("YOU LOSE")
     ballRelease.run_angle(100, -200)
          
#switch back to the class systemlink
Key = passwords.classKey

#trigger next person to go
Put_SL("Start22", "BOOL", 'false')
Put_SL("Start23", "BOOL", 'true')
