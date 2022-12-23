import re
from functools import reduce
from sides import WhiteSide, BlackSide
from pieces import Pawn, Rook, Knight, Bishop, Queen, King

class Square(object):
  _all = {}
  
  @classmethod
  def from_repr(cls, brd, repr):
    x, y = ord(repr[0])-96, int(repr[1])
    return cls._all.get((brd.code, x, y))
  
  @classmethod
  def is_valid(cls, v):
	  return 1 <= v//10 <= 8 and 1 <= v%10 <= 8
  
  def __new__(cls, board, x, y=None):
    if y==None:
      x, y = x//10, x%10
    if not (1 <= x < 9 and 1 <= y < 9):
      return None
    if not (board.code, x, y) in cls._all:
      obj = object.__new__(cls)
      cls._all[(board.code, x, y)] = obj
    else:
      obj = cls._all[(board.code, x, y)]
    return obj

  def __init__(self, board, x, y=None):
    if hasattr(self, "x"):
      return

    if y == None:
      x, y = x//10, x%10
    
    self.board = board
    self.x = chr(x+96)
    self.y = y 
    self.value = x*10+y
    self.set_piece(None)
  
  def besides(self):
    return tuple(filter(lambda i:i, (self.L1, self.R1)))
  
  def __getattr__(self, k):
    if re.match(r"[B,A,R,L,U,D][1-7]", k):
      f = {
        "B" : self.board.current_side.BEFORE,
        "A" : self.board.current_side.AFTER,
        "R" : 10,
        "L" : -10,
        "U" : 1,
        "D" : -1
      }
      return Square(self.board, self.value + int(k[1])*f[k[0]])
    return super().__getattribute__(k)

  def set_piece(self, piece):
    self.piece = piece
  
  def __str__(self):
    return "Square({}{})".format(self.x, self.y)
  
  def __repr__(self):
    return self.__str__()


class Board(object):
  _board = {}
  
  def __new__(cls, code, pgn=None):
    if code in cls._board:
      return cls._board[code]
    obj = object.__new__(cls)
    cls._board[code] = obj
    return obj
  
  def __init__(self, code, pgn=None):
    self.pgn_moves = None
    self.code = code
    self.enpassant_piece = None
    self._sides = (WhiteSide(self), BlackSide(self))
    self._turn_index = 0
    self.whiteSide = self._sides[0]
    self.blackSide = self._sides[1]
    if pgn:
      pgn.strip()
      p = re.split(r"([0-9]+)[.]\s", pgn)
      p = map(str.strip, p)
      p = filter(lambda s: s and not s.isdigit(), p)
      p = tuple(map(lambda s: s.split(" "), p))
      p = reduce(lambda a, b: a+b, p)
      #remove result of game
      if p[-1][1] == "-":
        p.pop()
      self.pgn_moves = p
        
    
    cavalries = (Rook, Knight, Bishop)
    cavalries = cavalries + (Queen, King) + tuple(reversed(cavalries))
    
    for i in range(1, 9):
      for j in range(1, 9):
        square = Square(self, i, j)
        setattr(self, f"{chr(i+96)}{j}", square)
        if j == 1:
          cavalries[i-1](square, self.whiteSide)
        if j == 2:
          Pawn(square, self.whiteSide)
        if j == 7:
          Pawn(square, self.blackSide)
        if j == 8:
          cavalries[i-1](square, self.blackSide)
  
  def go_ahead(self):
    if not self.pgn_moves:
      raise ValueError("There is no left moves")
    
    s = self.pgn_moves.pop(0)
    print(s)
    match = lambda r: re.match(r, s)
    side = self.current_side
    if s == "O-O":
      side.do_king_side_castling()
    elif s == "O-O-O":
      side.do_queen_side_castling()
    elif match(r"[a-h]\d"):
      sq = Square.from_repr(self, s)
      if isinstance(sq.B1.piece, Pawn):
        sq.B1.piece.move(sq)
      else:
        sq.B2.piece.move(sq)
    elif match(r"^[a-h][x][a-h][1-8]"):
      to = Square.from_repr(self, s[2:4])
      if (fr:=to.B1.besides())[0].x == s[0]:
        fr[0].piece.move(to)
      else:
        fr[1].piece.move(to)
    elif (st:=match(r"^[R,N,B,Q,K][a-h][1-8]")) or match(r"^[R,N,B,Q,K][x][a-h][1-8]"):
      to = Square.from_repr(self, s[2-bool(st):4-bool(st)])
      pieces = side.piece_of(s[0])
      for piece in pieces:
        if piece in side.in_control_squares[to]:
          piece.move(to)
          break
  
  def do_pgn(self, end=None):
    if not end:
      end = len(self.pgn_moves)
    for i in range(0, end):
      print(i+1, end=") ")
      self.go_ahead()
  
  @property
  def current_side(self):
    return self._sides[self._turn_index]
  
  @property
  def non_current_side(self):
    return self._sides[~self._turn_index]
    
  def change_turn(self):
    self._turn_index= ~self._turn_index
    
  
  def column(self, col_name):
    return [getattr(self, f"{col_name}{i}") for i in range(1, 9)]


