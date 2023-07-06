class Tabuleiro:

  def __init__(self):
    self.tabuleiro = [' '] * 9

  def add(self, jogada, turno):
    # Adiciona a jogada ao tabuleiro
    self.tabuleiro[int(jogada) - 1] = turno

  def repr(self):
    # Retorna a representação do tabuleiro
    return f'''Tabuleiro:
┌───┬───┬───┐
│ {self.tabuleiro[0]} │ {self.tabuleiro[1]} │ {self.tabuleiro[2]} │
├───┼───┼───┤
│ {self.tabuleiro[3]} │ {self.tabuleiro[4]} │ {self.tabuleiro[5]} │
├───┼───┼───┤
│ {self.tabuleiro[6]} │ {self.tabuleiro[7]} │ {self.tabuleiro[8]} │
└───┴───┴───┘'''
