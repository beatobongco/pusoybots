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
botname = "MEDIOCRE BOT"
hand = ""
shadow_hand = ""
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

  if len(cards) > 1:
    shadow_hand.remove(cards)
  elif len(cards) == 1:
    # Check if there are any in any pairs then remove
    for x in shadow_hand:
      if len(x) > 0:
        for y in x:
          if y == cards[0]:
            shadow_hand.remove(x)
    if cards[0] in shadow_hand:
      shadow_hand.remove(cards[0])
  if len(cards) > 0:
    bot_speak("Playing...{0}".format(card_text(cards)))
  else:
    bot_speak("Pass...")
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
    bot_speak("Singles lang.")
    return "{0} of {1}".format(r, s)
  elif len(cards) == 2:
    bot_speak("Boom pa niss!")
    return "pair {0}".format(r)
  elif len(cards) == 3:
    bot_speak("Three baby! Suck this.")
    return "trio {0}".format(r)

def get_shadow_hand(hand):
  shadow_hand = hand[:] # clone list
  three_pairs = get_available_matches(3, hand)

  for x in three_pairs:
    # Remove requirements from shadow hand
    for y in x:
      shadow_hand.remove(y)
    shadow_hand.append(x)

  two_pairs = get_available_matches(2, hand)

  for x in two_pairs:
    # Remove requirements from shadow hand
    for y in x:
      shadow_hand.remove(y)
    shadow_hand.append(x)

  return shadow_hand

def get_available_matches(number, hand):
  r_list = []
  counter = Counter([x[0] for x in hand])
  for x in counter:
    # Check if any of these are higher than prev played pair
    if counter[x] == number:
      r_list.append([y for y in hand if y[0] == x])
  return r_list

while 1:
  if state != "T":
    line = read_line()

  print "Server: " + line

  if state == "R":
    player_number = line.split(" ")[1][1]
    write_line("G")
    bot_speak("I'm {0} {1} and I'm ready to roll.".format(botname, player_number))
    state = "D"
  elif state == "D":
    hand = line[2:].split(" ")
    hand.sort(key=get_card_value)
    shadow_hand = get_shadow_hand(hand)
    print hand
    print shadow_hand
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
    bot_speak("I'm {0} {1}.".format(botname, player_number))
    if turn_type == "S":
      bot_speak("I start.")
      card_to_play = ["3C"]
      print card_to_play
      # Any pairs containing three
      for x in shadow_hand:
        if len(x) == 3 and x[0][0] == "3":
          card_to_play = x
        elif isinstance(x, list) and len(x) == 2 and x[0][0] == "3":
          card_to_play = x
      print card_to_play
      play_cards(card_to_play)
    elif turn_type == "F":
      # Get latest history
      cards = history[-1][1:]
      available = []
      if len(cards) == 1:
        last_play_value = get_card_value(history[-1][1])
        available = [[card] for card in hand if get_card_value(card) > last_play_value]
        # Check available cards if reserved in shadow hand
        original = []
        if len(available) > 0:
          original = available[0]
        for x in available:
          ## Only check combos
          if len(x) > 1:
            for y in x:
              if available[0] == y:
                available.pop(0)

        # if len(available) == 0:
        #   available.append(original)
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
        play_cards(available[0])
      else:
        play_cards([])
    elif turn_type == "A":
      bot_speak("Taking control.")
      card_to_play = [hand[0]]
      # Any pairs
      for x in shadow_hand:
        if len(x) == 3:
          card_to_play = x
        elif len(x) == 2 and isinstance(x, list): #Prevent bug where "ss" is len 2 also
          card_to_play = x
      print card_to_play
      play_cards(card_to_play)

    state = "G"

