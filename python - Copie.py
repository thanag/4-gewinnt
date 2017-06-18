from random import randrange
# -*- coding: utf-8 -*-
import time
import os
import pract04

###
# SpielfeldgrÃ¶ÃŸe und GewinnlÃ¤nge
COL = 7
ROW = 6
WIN = 4

###
# nur einzelene Ziffern vergeben
NONE = 0
MAXI=1
MINI=2
###
# Darstellung
REPR = { NONE: "- ", MAXI: "x ", MINI: "o " }


INFINITY = 10**100
BEST = 10**20


###
# Spielzustand
# Vorrausgesetzt wird, dass MAXI immer den ersten Zug macht.
class State:


	# Initialisierung.
	# S darf None, eine Liste (len == COL) von Listen (len == ROW), oder eine Instanz von State sein.
	# Wird etwas anderes Ãœbergeben, oder tritt ein Fehler in der Liste auf, wird eine Ausnahme erzeugt.
	# [ [int, ...], ... ] self.__F: Liste der LÃ¤nge COL von Listen der LÃ¤nge ROW. Die Spielfelder.
	# (int, int) self.__Last: enthÃ¤lt die Koordinaten des letzten Zugs.
	def __init__(self, S = None):
		self.__F = []
		if S == None:
			for c in range(COL):
				self.__F.append([0]*ROW)
		elif type(S) == list:
			self.__F = S
			if not self.is_legal():
				raise "*** FEHLER *** State.__init__  F = %s" % str(self.__F)
		else:
			try:
				for col in S.__F:
					self.__F.append( col[:] )
			except:
				raise "*** FEHLER *** State.__init__  F = %s" % str(self.__F)
		self.__Last = None


	# Darstellung des Spielzustands als String.
	def __repr__(self):
		s = "\n"
		for r in reversed(range(ROW)):
			for col in self.__F:
				s += REPR[col[r]]
			s += "\n"
		return s


	# Testet auf Gleichheit zweier SpielzustÃ¤nde.
	# True, wenn die ZustÃ¤nde gleich sind, sonst False.
	# State other: der Spielzustand, gegen den getestet werden soll.
	def __eq__(self, other):
		try:
			if self.__F == other.__F:
				return True
		except:
			return False
		return False


	# Testet die zulÃ¤ssigkeit des Spielzustands.
	# True, wenn in __F ein gÃ¼ltiger Zustand ist, sonst False.
	# Getestet wird die grÃ¶ÃŸe des Feldes, die EintrÃ¤ge, sowie deren Anzahl.
	# Nicht getestet wird, ob der Spielzustand wirklich im Spiel auftreten kann.
	def is_legal(self):
		if not (type(self.__F) == list and len(self.__F) == COL):
			return False
		for col in self.__F:
			if not (type(col) == list and len(col) == ROW):
				return False
			for field in col:
				if type(field) != int:
					return False
		all = reduce( lambda x,y: x+y, self.__F )
		Maxis = all.count( MAXI )
		Minis = all.count( MINI )
		Nones = all.count( NONE )
		if Maxis + Minis + Nones != COL*ROW:
			return False
		if not (Maxis == Minis or Maxis == Minis + 1):
			return False
		for col in self.__F:
			try:
				i = col.index(NONE)
			except:
				continue
			for field in col[i+1:ROW]:
				if field != NONE:
					return False
		if self.winner() == -1:
			return False
		return True


	# Gibt zurÃ¼ck, wer als nÃ¤chstes an der Reihe ist.
	# Gibt MAXI, MINI oder NONE zurÃ¼ck. Letzteres nur, wenn das Feld voll ist.
	# PrÃ¼ft insbesondere nicht auf Gewinn.
	def whos_next(self):
		all = reduce( lambda x,y: x+y, self.__F )
		Empty = all.count( NONE )
		if Empty == 0:
			return NONE
		if (COL*ROW - Empty) % 2 == 0:
			return MAXI
		else:
			return MINI


	# Liefert alle mÃ¶glichen FolgezstÃ¤nde, als Liste.
	def get_Successors(self, Complete = False):
		if self.winner() in (MAXI, MINI):
			return []
		who = self.whos_next()
		succs = []

		############################
		### TicTacToe
		#for c in range(COL):
			#for r in range(ROW):
				#if self.__F[c][r] == NONE:
					#S = State(self)
					#S.__F[c][r] = who
					#succs.append(S)
		############################

		############################
		### Connect Four
		for c in range(COL):
			try:
				r = self.__F[c].index(NONE)
				S = State(self)
				S.__F[c][r] = who
				S.__Last = (c,r)
				succs.append(S)
			except:
				if Complete:
					succs.append(None)
		############################

		return succs


	# ZÃ¤hlt die offenen GewinnmÃ¶glichkeiten auf dem Spielfeld.
	# GezÃ¤hlt wird vertikal, horizontal und in zwei Richtung diagonal.
	# RÃ¼ckgabe ist ein Dictionary mit jeweils einem Eintrag fÃ¼r MAXI und fÃ¼r MINI.
	# Der Eintrag ist jeweils eine Liste der LÃ¤nge WIN.
	# Dabei gilt: Eintrag[0] == Anzahl der "Einer", die noch zum Gewinn fÃ¼hren kÃ¶nnen.
	#             Eintrag[1] == Anzahl der "Zweier", ...
	def count(self):
		vert = self.__F                                                    # |
		horz = [ [col[row] for col in self.__F] for row in range(ROW) ]    # -
		dia1 = [ [] for x in range(COL+ROW-1) ]                            # \
		dia2 = [ [] for x in range(COL+ROW-1) ]                            # /
		for c in range(COL):
			for r in range(ROW):
				f = self.__F[c][r]
				dia1[c+r].append( f )
				dia2[c-r+ROW-1].append( f )

		counter = { MAXI: [0]*WIN, MINI: [0]*WIN }

		for strip in vert + horz + dia1 + dia2:
			for i in range(len(strip)-WIN+1):
				part = strip[i:i+WIN]
				c = dict( [(who, part.count(who)) for who in (NONE, MAXI, MINI)] )
				for who in (MAXI, MINI):
					if c[who] > 0 and c[NONE] + c[who] == WIN:
						counter[who][c[who]-1] += 1

		return counter


	# Wertet das Ergebnis aus self.count() aus, und liefert eine Bewertung zurÃ¼ck.
	# Positive Bewertugen sind gut fÃ¼r MAXI, negative fÃ¼r MINI.
	def value(self):
		counter = self.count()
		if counter[MAXI][WIN-1] > 0 and counter[MINI][WIN-1] == 0:
			return BEST
		if counter[MAXI][WIN-1] == 0 and counter[MINI][WIN-1] > 0:
			return -BEST
		maxval = reduce(lambda x,y: x*10+y, reversed(counter[MAXI]))
		minval = reduce(lambda x,y: x*10+y, reversed(counter[MINI]))
		return maxval - minval


	# Testet, ob der aktuellen Zustand eine Gewinnsituation ist.
	# -1, falls beide Spieler die SieglÃ¤nge erreicht haben.
	# MAXI oder MINI, falls der entsprechende Spieler gewonnen hat.
	# NONE, falls es noch keinen Gewinner gibt.
	def winner(self):
		counter = self.count()
		if counter[MAXI][WIN-1] > 0 and counter[MINI][WIN-1] > 0:
			return -1
		if counter[MAXI][WIN-1] > 0:
			return MAXI
		if counter[MINI][WIN-1] > 0:
			return MINI
		return NONE




class Player:

	def __init__(self, Name):
		self._Name = Name

	def __repr__(self):
		return "[Player] %s" % self._Name

	# Liefert das Tupel (Folgezustand, Bewertung) zurÃ¼ck.
	# State S: der Spielzustand, der gespielt werden soll.
	def move(self, S):
		return 0, None




class Human(Player):

	def __init__(self, Name):
		Player.__init__(self, Name)

	def __repr__(self):
		return "[Human Player] %s" % self._Name

	def move(self, S):
		succs = S.get_Successors(True)
		if succs == [None] * COL:
			return 0, None
		moves = [i+1 for i in range(len(succs)) if succs[i] != None]
		while True:
			x = raw_input("your move %s: " % moves)
			try:
				move = int(x)
			except:
				move = -1
			if move in moves:
				return 0, succs[move-1]




class AlphaBeta(Player):

	def __init__(self, Name, Depth = INFINITY):
		Player.__init__(self, Name)
		self._Depth = Depth
		if self._Depth < 1:
			self._Depth = 1

	def __repr__(self):
		s = "[AlphaBeta Player] %s" % self._Name
		if self._Depth != INFINITY:
			s += " <%d>" % self._Depth
		return s

	def move(self, S):
		return self._AlphaBeta(S, -INFINITY, INFINITY, 0, [])

	def _AlphaBeta(self, S, Alpha, Beta, Depth, Trace):
		if Depth >= self._Depth:
			return S.value(), None
		succs = S.get_Successors()
		if succs == []:
			return S.value(), None

		v, next = 0, None
		if S.whos_next() == MAXI:
			succs.sort(lambda x,y: -cmp(x.value(),y.value()))
			v = -INFINITY
			for i, s in enumerate(succs):
				m, null = self._AlphaBeta(s, Alpha, Beta, Depth + 1, Trace + [i])
				if v < m:
					v = m
					next = s
				if v >= Beta:
					return v, next
				Alpha = max( Alpha, v )
		else:
			succs.sort(lambda x,y: cmp(x.value(),y.value()))
			v = INFINITY
			for i, s in enumerate(succs):
				m, null = self._AlphaBeta(s, Alpha, Beta, Depth + 1, Trace + [i])
				if v > m:
					v = m
					next = s
				if v <= Alpha:
					return v, next
				Beta = min( Beta, v )

		return v, next




class SchwierigGame:

	def __init__(self):
		self.States = []
		self.OutDir = None

	def play(self, S, PlayerMaxi, PlayerMini = None, OutDir = None):
		self.States = []
		self.OutDir = OutDir
		if self.OutDir != None:
			try:
				os.mkdir( self.OutDir )
				os.chdir( self.OutDir )
			except:
				self.out( "Verzeichnis existiert bereits oder lÃ¤sst sich nicht erzeugen: %s !" % self.OutDir )
				self.OutDir = None

		if PlayerMini != None:
			Player = { MAXI: PlayerMaxi, MINI: PlayerMini }
		else:
			Player = { MAXI: PlayerMaxi, MINI: PlayerMaxi }

		if not S.is_legal():
			self.out( "illegal: %d" % str(S) )
			return -1

		N = S
		statenr = 0
		#self.out( "", True )
		self.out( "Connect Four" )
		self.out( "%s   - vs -   %s" % (str(Player[MAXI]), str(Player[MINI])) )
		self.out( "start state" )
		while True:
			self.States.append(N)
			self.out( N )
			if self.OutDir != None:
				N.export( "state-%02d.png" % statenr )
				statenr += 1

			self.out( "val: %s" % self.__val_to_str( N.value() ) )
			#self.out( "", True )

			if N.get_Successors() == []:
				break
			who = N.whos_next()

			self.out( "-" * 20 )
			self.out( Player[who] )
			t = time.time()
			w, N = Player[who].move(N)
			self.out( "%.3f sec" % (time.time()-t) )
			self.out( "prediction: %s" % self.__val_to_str(w) )

		self.out( "-" * 20 )
		win = N.winner()
		if win in (MAXI, MINI):
			self.out( "WINNER: %s (%s)" % (Player[win], REPR[win].strip()) )
		else:
			self.out( "TIE" )
		#self.out( "", True )

		if self.OutDir != None:
			os.chdir( ".." )

		return win


	def out(self, S, Timestamp = False):
		outfile = "out.txt"
		if Timestamp:
			S = "[%04d-%02d-%02d %02d:%02d:%02d]  " % time.localtime()[:6] + str(S)
		print str(S)
		if self.OutDir != None and outfile != None:
			try:
				f = open(outfile, 'a')
				f.write( str(S) + "\n" )
				f.close()
			except:
				print "*** FEHLER *** out: Datei \"%s\" lÃ¤sst sich nicht schreiben!" % outfile
				outfile = None


	def __val_to_str(self, val):
		if val == BEST:
			return REPR[MAXI] + "wins"
		if val == -BEST:
			return REPR[MINI] + "wins"
		return str(val)




col = 7
row = 6
coli = col -1 # max. index in col
rowi = row -1 # max. index in row
human = 0
global moves
moves=0
possible = [0,0,0,0,0,0,0]

#field = [zeile][spalte] wird definiert
field = [[i * j for j in range(col)] for i in range(row)]
for i in range(row):
    for j in range(col):
        field[i][j] = 0

# field Ursprung oben links
#   0 1 2 3 4 5 6 
# 0 . . . . . . .
# 1 . . . . . . .
# 2 . . . . . . . 
# 3 . . . . . . .
# 4 . . . . . . .
# 5 . . . . . . .



def movePossible(spalte):
  if (field[0][spalte] == 0):
    return True
  else:
    return False

def checkforWin():
    # horizontal:
    for a in range(row):    #to check each row
      for b in range (col - 3):   #to start at each columns but the last 3 to the right
        current = field [rowi - a][b]
        if (current != 0 and current == field [rowi - a][b + 1] and current == field [rowi - a][b + 2] and current == field [rowi - a][b + 3]):
          print ('\n---' + str(current) + ' WINS in row ' + str(a) + ' ---\n')
          return True
    # vertical:
    for a in range(row -3):    #to check each column
      for b in range (col):    #to start at each row but the top 3
        ## print (str(rowi - a) + ',' + str(b))  #to test order
        current  = field[rowi - a][b]
        if (current !=0 and current ==  field [rowi - a -1][b] and current == field [rowi - a -2][b] and current == field [rowi - a -3][b]):
          print ('\n---' + str(current) + ' WINS in column: ' + str(b) + ' ---\n')
          return True
    # posdiagonal (from bottom left to top right) /
    for a in range(row - 3):
      for b in range(col - 3):
        ## print (str(rowi - a) + ',' + str(b))
        current  = field[rowi - a][b]
        if (current !=0 and current == field[rowi - a -1][b +1] and current == field [rowi - a -2][b +2] and current == field [rowi - a -3][b +3]):
          print ('\n---' + str(current) + ' WINS diagonally ---\n')
          return True
    # negdiagonal (from top left to bottom right) \
    for a in range(row - 3):
      for b in range(col - 3):
        ## print (str(a) + ',' + str(b))
        current  = field[a][b]
        if (current !=0 and current == field[a +1][b +1] and current == field [a +2][b +2] and current == field [a +3][b +3]):
          print ('\n---' + str(current) + ' WINS diagonally ---\n')
          return True


def humanTurn(chip):
  retry = True
  while(retry):
    retry = False
    userInput = int(input('Du bist dran. 0 bis 6 eingeben: '))
    if (not(userInput <= row and userInput >= 0)):
      print('Ich habe gesagt zwischen 0 und 6!')
      retry = True
    elif (movePossible(userInput)):
        for i in range(row):
        ## print (i)
            if (field[rowi - i][userInput] == 0):
                field[rowi - i][userInput] = chip
                printboard()
                break
    else:
        print('Spalte voll!')
        retry = True

def listPossible():
  for i in range(col):
    if (field[0][i] == 0):
      possible[i] = 1
    else:
      possible[i] = 0
  ## print (possible)
      
def computerTurn(chip):
  summe = 0
  count = 0
  for i in possible:
    summe += i
  cominput = randrange(0, summe - 1)
  ## print ('Random number: ' + str(cominput))
  for i in range(col):
      count += possible[i]
      if (count == cominput +1):
        for j in range(row):
        ## print (i)
          if (field[rowi - j][i] == 0):
            field[rowi - j][i] = chip
            printboard()
            break
  count = 0
def printboard ():  #Update Board
    print ('\n\n0 1 2 3 4 5 6 \n-------------') #reference for user
    for n in field:
        print(' '.join([str(elem) for elem in n])) #print(field[i][j])
# kann man MAIN nennen
class RandomGame:
    def _init_(self):
        self.name="random game"
    def play(self):
            
            ans2=  int(input('Möchtest du gegen eine Person spielen (0 = NEIN, 1 = Ja)'))
            printboard()
            global moves
            for i in range (row * col):
              listPossible()
              if (not(checkforWin())):
                  human = (ans1 + 1) % 2
                  if (moves % 2 == human):
                      humanTurn('1')
                  else:
                      if (ans2==0):  
                         computerTurn('2')
                      if (ans2==1):
                           
                         humanTurn('2')
                                          
            
                  moves +=1
              else:
                  
                  break
              if (moves == 42):
                  print('Unentschieden!')
            return humanTurn,computerTurn
#kann man MAIN nennen
ans3=int(input('Waehle eine Schwierigkeit:1:random coputer 2:eifach  3:schwierig: '))
ans1 = int(input('Möchtest du anfangen? (0 = NEIN, 1 = JA)'))
H = Human("DU")
AB = AlphaBeta("AI", 4)
S=State()
g2=SchwierigGame()
if(ans3==1):
    g=RandomGame()
    print(g.play())
elif  (ans3==2):
    g1=EinfachGame()
    print(g1.play())
elif  ((ans3==3)&(ans1==1)):
    g2.play(S,H,AB)
elif ((ans3==3)&(ans1==0)):
    g2.play(S,AB,H)
else:
    ans3=int(input('Waehle eine gueltige schwierigkeit: '))
    


