#-----------------------------------------------------------------------

import socket, threading
import tabuleiro

#-----------------------------------------------------------------------

class ServidorDoJogo:

  def __init__(self):
    self.local = ('localhost', 8000)
    self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.udp.bind(self.local)
    print('Servidor está no ar...')
    self.recebimento_de_msgs()

  # Gerencia as mensagens recebidas
  def recebimento_de_msgs(self):
    self.lock = threading.Lock()
    self.jogadores = []
    self.estado_jogo = 'esperando'
    while True:
      msg, cliente = self.udp.recvfrom(1024)
      msg = msg.decode().split('/')
      print(msg)
      self.lock.acquire()
      if msg[0] == 'Request':
        self.verificar_sala(cliente)
      if (len(self.jogadores) == 2 and self.estado_jogo == 'esperando'):
        self.iniciar_jogo()
      elif (self.estado_jogo == 'rodando'):
        partida = self.jogo_rodando(cliente, msg)
        if partida == 'exit':
          break
      self.lock.release()

  # Verifica a quantidade de jogadores que estão na sala
  def verificar_sala(self, cliente):
    if len(self.jogadores) < 2:
      self.jogadores.append(cliente)
      self.udp.sendto('Confirm/Você entrou na partida!'.encode(), cliente)
      print(f'Jogador {len(self.jogadores)} entrou na partida.')
  
      if len(self.jogadores) < 2:
        self.udp.sendto('Wait/esperando outro jogador entrar...'.encode(), cliente)

    else:
      resposta = 'Full/A Sala está Cheia.'
      self.udp.sendto(resposta.encode(), cliente)

  # Inicia a partida
  def iniciar_jogo(self):
    self.tab = tabuleiro.Tabuleiro()
    self.jogador_da_vez = 0
    self.turno = 'X'
    self.estado_jogo = 'rodando'
    self.thread_enviar(self.comecar_jogo, 'Start/Jogo Comecou!!')
    self.thread_enviar(self.mandar_representacao, self.tab)
    self.jogue()

  # Faz o jogo rodar enviando comandos para o jogador
  def jogo_rodando(self, cliente, msg):
    if cliente == self.jogadores[self.jogador_da_vez]:
      if msg[0] == 'Insert':
          
        valido = self.jogada_atual(msg[1])

        if valido == False:
          self.jogue()

        if valido == True:

          self.thread_enviar(self.mandar_representacao, self.tab)

          result = self.verificar_tabuleiro()
          if result == 'X' or result == 'O':
            self.thread_enviar(self.alguem_venceu, result)
            print(f'O Jogador {self.jogador_da_vez+1} venceu!')
            return 'exit'

          if result == 'empate':
            self.thread_enviar(self.empate, 'Draw/EMPATE!!')
            print(f'O Jogo Empatou!')
            return 'exit'
              
          self.mudar_turno()
          self.jogue()

#--------------------------------------------------------

  def comecar_jogo(self, i, resposta):
    self.udp.sendto(resposta.encode(), self.jogadores[i])

  # Representação do tabuleiro
  def mandar_representacao(self, i, tabuleiro):
    resposta = 'Content/' + tabuleiro.repr()
    self.udp.sendto(resposta.encode(), self.jogadores[i])

  # Turno do jogador
  def jogue(self):
    resposta = 'Insert/' + f'Turno do {self.turno}, qual sua jogada?'
    self.udp.sendto(resposta.encode(), self.jogadores[self.jogador_da_vez])

  # Checagem de jogada válida
  def jogada_atual(self, jogada):
    if jogada in ('1', '2', '3', '4', '5', '6', '7', '8', '9'):
      if self.verificar_jogada(jogada):
        self.tab.add(jogada, self.turno)
        print(f'Jogador {self.jogador_da_vez+1} jogou na posição {jogada}')
        return True
      else:
        resposta = 'ERROR/Posição invalida, tente novamente!'
        self.udp.sendto(resposta.encode(), self.jogadores[self.jogador_da_vez])
        return False
    else:
      resposta = 'ERROR/jogada invalida, tente novamente!'
      self.udp.sendto(resposta.encode(), self.jogadores[self.jogador_da_vez])
      return False

  # Verifica se jogou em um espaço vazio
  def verificar_jogada(self, jogada):
    if self.tab.tabuleiro[int(jogada)-1] == ' ':
      return True
    else:
      return False

  # Muda o turno a cada jogada
  def mudar_turno(self):
    if self.turno == 'X':
      self.turno = 'O'
      self.jogador_da_vez = 1
    else:
      self.turno = 'X'
      self.jogador_da_vez = 0

  # Informa que alguém venceu
  def alguem_venceu(self, jogador, result):
    resposta = (f'Win/{result} é o vencedor')
    self.udp.sendto(resposta.encode(), self.jogadores[jogador])

  # Informa que a partida empatou
  def empate(self, jogador, result):
    resposta = result
    self.udp.sendto(resposta.encode(), self.jogadores[jogador])

  # Faz o envio das mensagens para os jogadores
  def thread_enviar(self, funcao, result):
    thr1 = threading.Thread(target=funcao, args=[0, result])
    thr2 = threading.Thread(target=funcao, args=[1, result])
    thr1.start(), thr2.start()
    thr1.join(), thr2.join()

  # Verifica se alguém venceu checando vertical, horizontal e diagonal
  def verificar_tabuleiro(self):
    global result_v
    result_v = ' '
    v1 = threading.Thread(target=self.verificar_vertical)
    v2 = threading.Thread(target=self.verificar_horizontal)
    v3 = threading.Thread(target=self.verificar_diagonal)
    v1.start(), v2.start(), v3.start()
    v1.join(), v2.join(), v3.join()
    if result_v != ' ':
      return result_v
    else:
      if self.tab.tabuleiro.count(' ') == 0:
        return 'empate'
      else:
        return self.tab.tabuleiro.count(' ')

  # Verifica se alguém venceu na vertical
  def verificar_vertical(self):
    global result_v
    if self.tab.tabuleiro[0] != ' ' and self.tab.tabuleiro[0] == self.tab.tabuleiro[3] and self.tab.tabuleiro[3] == self.tab.tabuleiro[6]:
      result_v = self.tab.tabuleiro[0]
    elif self.tab.tabuleiro[1] != ' ' and self.tab.tabuleiro[1] == self.tab.tabuleiro[4] and self.tab.tabuleiro[4] == self.tab.tabuleiro[7]:
      result_v = self.tab.tabuleiro[1]
    elif self.tab.tabuleiro[2] != ' ' and self.tab.tabuleiro[2] == self.tab.tabuleiro[5] and self.tab.tabuleiro[5] == self.tab.tabuleiro[8]:
      result_v = self.tab.tabuleiro[2]

  # Verifica se alguém venceu na horizontal
  def verificar_horizontal(self):
    global result_v
    if self.tab.tabuleiro[0] != ' ' and self.tab.tabuleiro[0] == self.tab.tabuleiro[1] and self.tab.tabuleiro[1] == self.tab.tabuleiro[2]:
      result_v = self.tab.tabuleiro[0]
    elif self.tab.tabuleiro[3] != ' ' and self.tab.tabuleiro[3] == self.tab.tabuleiro[4] and self.tab.tabuleiro[4] == self.tab.tabuleiro[5]:
      result_v = self.tab.tabuleiro[3]
    elif self.tab.tabuleiro[6] != ' ' and self.tab.tabuleiro[6] == self.tab.tabuleiro[7] and self.tab.tabuleiro[7] == self.tab.tabuleiro[8]:
      result_v = self.tab.tabuleiro[6]

  # Verifica se alguém venceu na diagonal
  def verificar_diagonal(self):
    global result_v
    if self.tab.tabuleiro[0] != ' ' and self.tab.tabuleiro[0] == self.tab.tabuleiro[4] and self.tab.tabuleiro[4] == self.tab.tabuleiro[8]:
      result_v = self.tab.tabuleiro[0]
    elif self.tab.tabuleiro[6] != ' ' and self.tab.tabuleiro[6] == self.tab.tabuleiro[4] and self.tab.tabuleiro[4] == self.tab.tabuleiro[2]:
      result_v = self.tab.tabuleiro[6]

servidor = ServidorDoJogo()
