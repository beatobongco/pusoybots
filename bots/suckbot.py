import socket
import pyttsx
from collections import Counter

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("localhost", 2222))

# Rankings
ranks = "3456789TJQKA2"
suits = "CSHD"

card_to_english = {
  "T": "ten",
  "J": "jack",
  "Q": "queen",
  "K": "king",
  "A": "ace",
  "C": "clubs",
  "S": "spades",
  "H": "hearts",
  "D": "diamonds",
}

# Player vars
botname = "SUCKBOT"
hand = ""
state = "R"
player_number = ""
history = []

def read_line():
  line = ""
  while 1:
    b = s.recv(1)
    line += b
    if b == "\n":
      break
  return line.strip()

def write_line(line):
  s.send(line + "\r\n")

def play_cards(cards):
  for card in cards:
    hand.remove(card)
  write_line("P {0}".format(" ".join(cards)))

def get_card_value(s):
  return (ranks.index(s[0]), suits.index(s[1]))

def bot_speak(s):
  engine = pyttsx.init()
  engine.say(s)
  engine.runAndWait()
  print "{0}: {1}".format(botname, s)

def card_text(cards):
  s = ""
  r = card_to_english.get(cards[0][0], cards[0][0])
  s = card_to_english.get(cards[0][1], cards[0][1])

  if len(cards) == 1:
    bot_speak("Singles game strong.")
    return "{0} of {1}".format(r, s)
  elif len(cards) == 2:
    bot_speak("Double trouble!")
    return "pair {0}".format(r)
  elif len(cards) == 3:
    bot_speak("Threesome!")
    return "trio {0}".format(r)

while 1:
  if state != "T":
    line = read_line()

  print "Server: " + line

  if state == "R":
    player_number = line.split(" ")[1][1]
    write_line("G")
    bot_speak("I'm {0} number {1} and I'm game.".format(botname, player_number))
    state = "D"
  elif state == "D":
    hand = line[2:].split(" ")
    hand.sort(key=get_card_value)
    print hand
    state = "G"
  elif state == "G":
    tokens = line.split(" ", 1)
    command = tokens[0]
    args = ""
    if len(tokens) == 2:
      args = tokens[1]
    # Commands: !, P, T, W, E
    if command in ["!", "W", "E"]:
      print line
    elif command == "P":
      # store history of plays in memory
      play = args.split(" ")
      if len(play) > 1:
        history.append(play)
    elif command == "T":
      pn, turn_type = args.split(" ")
      if pn[1] == player_number:
        state = "T"

  elif state == "T":
    bot_speak("I'm {0} number {1} and it's my turn.".format(botname, player_number))
    if turn_type == "S":
      bot_speak("I'm starting. Mah bah bah lung.")
      bot_speak(card_text(["3C"]))
      play_cards(["3C"])
    elif turn_type == "F":
      # Get latest history
      cards = history[-1][1:]
      available = []
      if len(cards) == 1:
        last_play_value = get_card_value(history[-1][1])
        available = [[card] for card in hand if get_card_value(card) > last_play_value]
      elif len(cards) == 2:
        counter = Counter([x[0] for x in hand if ranks.index(x[0]) > ranks.index(history[-1][1][0])])
        for x in counter:
          # Check if any of these are higher than prev played pair
          if counter[x] == 2:
            available.append([y for y in hand if y[0] == x])

      elif len(cards) == 3:
        counter = Counter([x[0] for x in hand if ranks.index(x[0]) > ranks.index(history[-1][1][0])])
        for x in counter:
          # Check if any of these are higher than prev played pair
          if counter[x] == 3:
            available.append([y for y in hand if y[0] == x])
      elif len(cards) == 5:
        pass
        # bot_speak("Combo wombo.")

      if len(available) > 0:
        bot_speak("Playing..." + card_text(available[0]))
        play_cards(available[0])
      else:
        bot_speak("I pass.")
        play_cards([])
    elif turn_type == "A":
      play_cards([hand[0]])

    state = "G"

