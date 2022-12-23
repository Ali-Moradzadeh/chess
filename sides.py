from pieces import Rook, Knight, Bishop, Queen,King


WHITE = "White"
BLACK = "Black"

SYMBOLS = {
  "R" : Rook,
  "N" : Knight,
  "B" : Bishop,
  "Q" : Queen,
  "K" : King
}

class Side(object):
  _sides = {}
  
  def __new__(cls, board):
    if (pare:=(cls, board)) in cls._sides:
      return cls._sides[pare]
    else:
      obj = object.__new__(cls)
      cls._sides[pare] = obj
      return obj

  def __init__(self, board):
    self.board = board
    self.king_moved = self.king_side_rook_moved = self.queen_side_rook_moved = self.never_can_castling = self.never_can_king_side_castling = self.never_can_queen_side_castling = self.never_can_castling = self.castling_time = False
    self.pieces = []
  
  def piece_of(self, symbol):
    return tuple(filter(lambda p:p.__class__ is SYMBOLS[symbol], self.pieces))
  
  def _can_side_castling(self, side):
    if self.king_moved:
      return False
    if self.is_checked():
      return False
    if list(filter(lambda p : p.piece, side)):
      return False
    in_ctrl = set(self.get_opossite().in_control_squares.keys())
    if list(filter(lambda p : p in in_ctrl, side)):
      return False
    return True

  def _update_can_king_side_castling(self):
    self.never_can_king_side_castling = self.king_moved or self.king_side_rook_moved
    self.can_king_side_castling = not self.king_moved and not self.king_side_rook_moved and self._can_side_castling(self.KING_SIDE_CASTLING_KING_CROSS)

  def _update_can_queen_side_castling(self):
    self.never_can_queen_side_castling = self.king_moved or self.queen_side_rook_moved
    self.can_queen_side_castling = not self.king_moved and not self.queen_side_rook_moved and self._can_side_castling(self.QUEEN_SIDE_CASTLING_KING_CROSS)

  def update_can_castling(self):
    if not self.never_can_king_side_castling:
      self._update_can_king_side_castling()
    if not self.never_can_queen_side_castling:
      self._update_can_queen_side_castling()
    
    self.never_can_castling = self.never_can_king_side_castling and self.never_can_queen_side_castling
    
    self.can_castling = self.can_king_side_castling or self.can_queen_side_castling
  
  def do_king_side_castling(self):
    self.castling_time = True
    if self.never_can_king_side_castling:
      raise ValueError(f"{self._side} never allow king castling")
    if not self.can_king_side_castling:
      raise ValueError("cant king side castling now")
    
    castling_type = self.KING_SIDE_CASTLING_KING_CROSS
    
    self.king_square.piece.move(castling_type[-1])
    self.KING_SIDE_ROOK_INITIAL_SQUARE.piece.move(castling_type[0])
    self.castling_time = False
    self.board.change_turn()
  
  def do_queen_side_castling(self):
    self.castling_time = True
    if self.never_can_queen_side_castling:
      raise ValueError(f"{self._side} never allow queen castling")
    if not self.can_king_side_castling:
      raise ValueError("cant queen side castling now")
    
    castling_type = self.QUEEN_SIDE_CASTLING_KING_CROSS
    
    self.king_square.piece.move(castling_type[-1])
    self.QUEEN_SIDE_ROOK_INITIAL_SQUARE.piece.move(castling_type[0])
    self.castling_time = False
    self.board.change_turn()
  
  def add_piece(self, piece):
    if piece not in self.pieces:
      self.pieces.append(piece)
    if len(self.pieces) >= 16:
      self.update_in_control_squares()
  
  def remove_piece(self, piece):
    if piece in self.pieces:
      self.pieces.remove(piece)
  
  def update_in_control_squares(self):
    controls = {}
    pieces = [p for p in self.pieces if hasattr(p, "square") and hasattr(p.square, "piece")]
    
    for piece in pieces:
      for on_control in piece.control_squares(flat=True):
        controls[on_control] = controls.get(on_control, tuple()) + (piece, )
    self.in_control_squares = controls
 
  def get_opossite(self):
    return self.board.blackSide if self._side == WHITE else self.board.whiteSide
  
  def opposite_checker_pieces(self):
    return self.get_opossite().in_control_squares.get(self.king_square, [])
    
  def is_double_checked(self):
    return len(self.opposite_checker_pieces()) == 2
  
  def is_checked(self):
    return len(self.opposite_checker_pieces()) != 0
  
  def is_checkmated(self):
    checkmated = True
    for piece in self.pieces:
      if piece.valid_moves(flat=True):
        checkmated = False 
        break

    return self.is_checked and checkmated
  
  def __str__(self):
    return self._side
  
  def __repr__(self):
    return self.__str__()
  

class WhiteSide(Side):
  _side = WHITE
  BEFORE = -1
  AFTER = 1
  UPGRADE_LINE = 8
  
  
  @property
  def KING_SIDE_ROOK_INITIAL_SQUARE(self):
    return self.board.h1
  
  @property
  def QUEEN_SIDE_ROOK_INITIAL_SQUARE(self):
    return self.board.a1
  
  @property
  def KING_SIDE_CASTLING_KING_CROSS(self):
    brd = self.board
    return (brd.f1, brd.g1)
  
  @property
  def QUEEN_SIDE_CASTLING_KING_CROSS(self):
    brd = self.board
    return (brd.d1, brd.c1)


class BlackSide(Side):
  _side = BLACK
  BEFORE = 1
  AFTER = -1
  UPGRADE_LINE = 1

  @property
  def KING_SIDE_ROOK_INITIAL_SQUARE(self):
    return self.board.h8
  
  @property
  def QUEEN_SIDE_ROOK_INITIAL_SQUARE(self):
    return self.board.a8

  @property
  def KING_SIDE_CASTLING_KING_CROSS(self):
    brd = self.board
    return (brd.f8, brd.g8)

  @property
  def QUEEN_SIDE_CASTLING_KING_CROSS(self):
    brd = self.board
    return (brd.d8, brd.c8)
