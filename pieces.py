Square = None

def _set_Square_class(_cls):
  global Square
  Square = _cls

class Piece(object):
  def __init__(self, square, side):
    square.set_piece(self)
    side.add_piece(self)
    self.side = side
    self.square = square
    global Square
    if not Square:
      Square = self.square.__class__
  
  def __setattr__(self, k, v):
    if k == "square" and v == None:
      self.side.remove_piece(self)
    if k == "square" and v != None:
      self.side.add_piece(self)
    super().__setattr__(k, v)
  
  def is_checked_after_move(self, to=None):
    is_checked = False
    from_sq = self.square
    to_piece = to.piece if to else None

    from_sq.set_piece(None)
    self.square = to
    if to:
      to.set_piece(self)
    if to_piece:
      to_piece.square = None
    
    self.side.get_opossite().update_in_control_squares()
    is_checked = self.side.is_checked()
    
    self.square = from_sq
    from_sq.set_piece(self)
    if to:
      to.set_piece(to_piece)
    if to_piece:
      to_piece.square = to
      
    self.side.get_opossite().update_in_control_squares()
    return is_checked
  
  def valid_moves(self, flat=False):
    if self.square == None:
      raise ValueError(f"{self} has knocked out")
    valids = []
    _all = self.__class__.valid_squares_value(self.square.value)
    for pack in _all:
      valid = []
      for sq_v in pack:
        if self.is_checked_after_move((square:=(Square(self.square.board, sq_v)))):
          continue
        elif square.piece != None:
          if square.piece.side != self.side:
            valid.append(square)
          break
        valid.append(square)
      if flat:
        valids.extend(valid)
      else:
        valids.append(tuple(valid))
    return tuple(valids)

  def control_squares(self, flat=False):
    if self.square == None:
      return ValueError(f"{self} has knocked out")
    valids = []
    _all = self.__class__.valid_squares_value(self.square.value)
    for pack in _all:
      valid = []
      for sq_v in pack:
        if (square:=Square(self.square.board, sq_v)).piece != None:
          valid.append(square)
          break
        valid.append(square)
      if flat:
        valids.extend(valid)
      else:
        valids.append(tuple(valid))
    return tuple(valids)
  
  def move(self, to):
    side = self.side
    oppo_side = self.side.get_opossite()
    
    if self.square.board.current_side != self.side:
      raise ValueError(f"turn is not for {self.side}")
    if self.side.is_checkmated():
      raise ValueError("checkmate happend")
    elif not side.castling_time and not to in self.valid_moves(flat=True):
      raise ValueError("invalid move")
    else:
      if not side.castling_time:
        to.board.change_turn()
      self.square.set_piece(None)
      if to.piece != None:
        to.board.current_side.pieces.remove(to.piece)
        to.piece.square = None
      self.square = to
      to.set_piece(self)
      
      side.update_in_control_squares()
      oppo_side.update_in_control_squares()
      
      side.update_can_castling()
      oppo_side.update_can_castling()
      
      side.board.enpassant_piece = None

  def __str__(self):
    return "Piece({}, {}, {}{})".format(self.__class__.__name__, self.side, self.square.x, self.square.y)

  def __repr__(self):
    return self.__str__()


class Pawn(Piece):
  def valid_moves(self, flat=False):
    x, y = self.square.value//10, self.square.y
    board = self.square.board
    white = board.whiteSide
    black = board.blackSide
    zarib = 1 if self.side == board.whiteSide else -1
    valids = []
    #for moving forward
    if (square:=Square(self.square.board, x, y+zarib)).piece == None and not self.is_checked_after_move(square):
      valids.append(square)
      #for moving forward two square in start position
      if ((self.side == white and y == 2) or (self.side == black and y == 7)) and (square:=Square(self.square.board, x, y+2*zarib)).piece == None:
        valids.append(square)
    
    #for capture opposite pieces
    condition = (x != 8 and (square:=Square(self.square.board, x+1, y+zarib)).piece != None) or (x != 1 and (square:=Square(self.square.board, x-1, y+zarib)).piece != None)
    
    if condition and not self.is_checked_after_move(square):
      valids.append(square)
    
    #for enpassant move
    enpassant_condition = (x != 8 and (square:=Square(self.square.board, x+1, y)).piece is self.side.board.enpassant_piece) or (x != 1 and (square:=Square(self.square.board, x-1, y)).piece is self.side.board.enpassant_piece)
    
    if enpassant_condition and not self.is_checked_after_move(square):
      valids.append(Square(self.square.board, square.value+zarib))
    
    if flat:
      return tuple(valids)
    return (tuple(valids), )

  def control_squares(self, flat=False):
    x, y = self.square.value//10, self.square.y
    zarib = 1 if self.side == self.square.board.whiteSide else -1
    valids = []
    
    if x != 1:
      valids.append(Square(self.square.board, x-1, y+zarib))
    if x != 8:
      valids.append(Square(self.square.board, x+1, y+zarib))
      
    if flat:
      return tuple(valids)
    return (tuple(valids), )

  def move(self, to):
    pre_y = self.square.y
    enpass_piece = self.side.board.enpassant_piece
    super().move(to)
    if enpass_piece and abs(self.square.y - enpass_piece.square.y) == 1:
      enpass_piece.square.piece = None
      enpass_piece.square = None
      enpass_piece.side.remove_piece(enpass_piece)
    
    #print(self.square, Square(self.square.board, self.square.value + 10).piece)
    if abs(pre_y - self.square.y) == 2 and ((Square.is_valid(self.square.value + 10) and (sq:=Square(self.square.board, self.square.value + 10)).piece and sq.piece.side != self.side) or (Square.is_valid(self.square.value - 10) and (sq:=Square(self.square.board, self.square.value - 10)).piece and sq.piece.side != self.side)):
      self.side.board.enpassant_piece = self
    
    if self.square.y == self.side.UPGRADE_LINE :
      choice = input("what piece use to upgrade Q for Queen, R for Rook, N for Knight and B for bishop : ")
      
      valid_choices = {
        "Q" : Queen,
        "R" : Rook,
        "N" : Knight,
        "B" : Bishop
      }
      
      if choice in valid_choices:
        upg_piece = valid_choices[choice](self.square, self.side)
        self.side.add_piece(upg_piece)
        self.square = None
        self.side.remove_piece(self)
        self.side.update_in_control_squares()


class Rook(Piece):
  @classmethod
  def valid_squares_value(cls, v, flat=False):
    valids = []
    incs = (-10, 10, -1, 1)
    for inc in incs:
      valid = []
      for i in range(1, 8):
        new_v = v+i*inc
        if not Square.is_valid(new_v):
          break
        valid.append(new_v)
      if flat:
        valids.extend(valid)
      else:
        valids.append(tuple(valid))
    return tuple(valids)
  
  def move(self, to):
    brd = self.square.board
    sq = self.square
    self.side.queen_side_rook_moved = sq is brd.a1 or sq is brd.a8
    self.side.king_side_rook_moved = sq is brd.h1 or sq is brd.h8
    super().move(to)


class Knight(Piece):
  @classmethod
  def valid_squares_value(cls, v, flat=False):
    incs = (-21, -19, -12, -8, 8, 12, 19, 21)
    #return tuple(map(lambda i:(i, ), filter(lambda v:Square.is_valid(v+self.value), incs)))
    valid = []
    for inc in incs:
      if Square.is_valid(v+inc):
        if flat:
          valid.append(v+inc)
        else:
          valid.append((v+inc, ))
    return tuple(valid)


class Bishop(Piece):
  @classmethod
  def valid_squares_value(cls, v, flat=False):
    valids = []
    incs = (-11, +11, -9, +9)
    for inc in incs:
      valid = []
      for i in range(1, 8):
        new_v = v + i*inc
        if not Square.is_valid(new_v):
          break 
        valid.append(new_v)
      if flat:
        valids.extend(valid)
      else:
        valids.append(tuple(valid))
    return tuple(valids)


class Queen(Piece):
  @classmethod
  def valid_squares_value(cls, v, flat=False):
    return Bishop.valid_squares_value(v, flat) + Rook.valid_squares_value(v, flat)


class King(Piece):
  @classmethod
  def valid_squares_value(cls, v, flat=False):
    incs = (-11, -10, -9, -1, 1, 9, 10, 11)
    valid = []
    for inc in incs:
      if Square.is_valid(v+inc):
        if flat:
          valid.append(v+inc)
        else:
          valid.append((v+inc, ))
    return tuple(valid)

  def __init__(self, x, y=None):
    super().__init__(x, y)
    self.side.king_square = self.square
  
  def __setattr__(self, k, v):
    if k == "square":
      self.side.king_square = v
    super().__setattr__(k, v)
  
  def move(self, to):
    super().move(to)
    self.side.king_moved = True
