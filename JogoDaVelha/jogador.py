import socket

class Jogador:

  def __init__(self):
    self.destino = ('localhost', 8000)
    self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.entrar()

  # Tenta entrar na partida
  def entrar(self):
      self.udp.sendto('Request-C/Quero Jogar!'.encode(), self.destino)
      while True:
        resposta, servidor = self.udp.recvfrom(1024)
        resposta = resposta.decode().split('/')
        if resposta[0] == 'Confirm-C':
          print(resposta[1])
          continue
        if resposta[0] == 'Wait-C':
          print(resposta[1])
          self.sala_de_espera()
          break
        elif resposta[0] == 'Start-C':
          print(resposta[1])
          self.rodando(resposta)
          break
        elif resposta[0] == 'Full-C':
          print(resposta[1])
          break
        else:
          print('Erro.')
          break

  # Manda o jogador para sala de espera
  def sala_de_espera(self):
    resposta, servidor = self.udp.recvfrom(1024)
    resposta = resposta.decode().split('/')
    if resposta[0] == 'Start-C':
      print(resposta[1])
      self.rodando(resposta)

  # Realiza a jogada feita pelo jogador
  def jogar(self, resposta):
    while True:
      print(resposta)
      jogada = input('Jogada: ')
      msg = 'Insert-C/' + jogada
      self.udp.sendto(msg.encode(), self.destino)
      break

  # Faz o jogo rodar de acordo com os comandos recebidos
  def rodando(self, resposta):
    if resposta[0] == 'Start-C':
      while True:
        resposta, servidor = self.udp.recvfrom(1024)
        resposta = resposta.decode().split('/')
        if resposta[0] == 'Content-C':
          print(resposta[1])
        if resposta[0] == 'Get-C':
          self.jogar(resposta[1])
        if resposta[0] == 'Win-C':
          print(resposta[1])
          break
        if resposta[0] == 'Draw-C':
          print(resposta[1])
          break
        if resposta[0] == 'ERROR-C':
          print(resposta[1])

jogador = Jogador()
