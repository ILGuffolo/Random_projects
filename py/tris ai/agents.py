'''
the various agents
- minmax
-  - alpha beta pruning


'''

from game_runner import grid, p1, p2, EMPTY

class MinimaxAgent:
    def select_move(self, grid):
        best_score = -float("inf")
        best_move = None
        
        
        for move in game.available_moves():
            g = game.clone()
            g.move(move)

            score = self.minimax(g, game.player, -float("inf"), float("inf"))

            if score > best_score:
                best_score = score
                best_move = move

        return best_move

    def minimax(self, game, player, alpha, beta, depth =0):
        
        #print(f"=== Debug: {depth} turn===")
        #print("Board:", game.state)
        #print("Moves:", game.available_moves())
        
        winner = game.check_winner()
        if depth > 10:
            print("WARNING: too deep")
            print("Board:", game.board)
            print("Moves:", game.available_moves())
            raise Exception("Depth overflow")
        
        if winner is not None:
            return winner * (10 - depth) #prefer faster wins
        
        moves = game.available_moves()
        if not moves:
            return 0
        
        if game.player == player:
            # MAXIMIZING
            value = -float("inf")
            for move in moves:
                g = game.clone()
                g.move(move)
                
                value = max(value, self.minimax(g, player, alpha, beta))
                alpha = max(alpha, value)
                
                if beta <= alpha:
                    break  # PRUNE
            return value
        
        else:
            # MINIMIZING
            value = float("inf")
            
            for move in moves:
                g = game.clone()
                g.move(move)
                
                value = min(value, self.minimax(g, player, alpha, beta))
                beta = min(beta, value)
                
                if beta <= alpha:
                        break  # PRUNE

            return value
        
        