from board import Board

x = "1. d4 d5 2. c4 e5 3. dxe5 c6 4. Nf3 Bb4+ 5. Nc3 Qa5 6. Bd2 dxc4 7. a3 Be7 8. Nd5 Qxd5 9. g3 Bf5 10. Bg2 Nd7 11. O-O Nxe5 12. Nh4 Qe6 13. Bc3 Rd8 14. Qa4 Bxh4 15. gxh4 Bh3 16. Bxe5 Bxg2 17. Kxg2 Qxe5 18. Qxc4 Rd4 19. Qc3 Rg4+ 20. Kh1 Qd5+ 21. f3 Nf6 22. Rg1 Rxh4 23. Rxg7 Qh5 24. Rg2 Rg8 25. Rag1"

x = "1. e4 e5 2. d3 Bc5 3. Nf3 Qe7 4. d4 exd4 5. Nxd4 d5 6. Be2 Qxe4 7. Be3 Qxg2 8. Rf1 Nf6 9. Nb5 Qxh2 10. Bxc5 Bh3 11. Nxc7+ Qxc7 12. Rg1 Qxc5 13. Rxg7 Ne4 14. Rxf7 Kxf7 15. Bh5+ Ke7 16. Qe2 Re8 17. f3 Qg1+ 18. Qf1 Qxf1# 0-1"

brd = Board("e", x)
brd.do_pgn()

#print(brd.h2.piece.valid_moves(flat=True))
#print(brd.current_side.can_king_side_castling)