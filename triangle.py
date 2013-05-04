#!/usr/bin/env python
# -*- coding: utf-8 -*- 

"""
The server for interfacing between two triangle programs.

Homework for AI 2013
Written by Vandolf Estrelado
"""

from threading import Thread
import socket, sys, time

# delays execution of each turn in seconds
TURN_DELAY = 1

# IMPORTANT! Clients must have the same values!
# status codes/flags used to communicate with clients
FAIL = '0'
SUCCESS = '1'
SUCCESS_NEW = '2'
START = '3'
END = '4'
TIE = '5'

# matrix dimension
MATRIX_D = (4, 4)

def line_is_valid(line):
    """ 
    Returns True if the line is a valid line.
    Note that we can simply store all the possible lines
    and check if line is in there but that does not help players
    understand what the form of a valid line is.

    A line is not valid if it contains an index 
    outside the matrix or it's horzontal or vertical
    length is greater than 1 or both are 0

    IMPORTANT! As a convention of the game, lines should be    
    written from left to right and from up to down
    e.g. 
    VALID 
        vertical lines: '0010', '1121', ...
        horizontal lines: '0001', '1112', ...
        positive slope: '1001', '1203', ...
        negative slope: '0011', '1223', ...
        
    INVALID 
        vertical lines: '1000', '2111', ...
        horizontal lines: '0100', '1211', ...
        positive slope: '0110', '0312', ...
        negative slope: '1100', '2312', ...
    """
    if type(line) is str:
        l = [int(i) for i in list(line)]
    else:
        l = line

    # validate index
    for n in l:
        if n < 0: return False
    if l[0] > MATRIX_D[0]-1 or l[2] > MATRIX_D[0]-1 or\
        l[1] > MATRIX_D[1]-1 or l[3] > MATRIX_D[1]-1:
        return False

    length  = abs(l[2]-l[0]) > 1 or abs(l[3]-l[1]) > 1
    point = l[2]-l[0] == 0 and l[3]-l[1] == 0
    vertical = l[1] == l[3] and l[2]-l[0] < 0
    horizontal = l[0] == l[2] and l[3]-l[1] < 0
    slope_pos = l[2]-l[0] > 0 and l[3]-l[1] < 0
    slope_neg = l[2]-l[0] < 0 and l[3]-l[1] < 0
    if length or point or vertical or horizontal or\
        slope_pos or slope_neg:
        return False 
    else:
        return True

def line_overlaps(line, lines):
    """ 
    returns True if the given line overlaps another.
    lines is a list of strings or ints: ['0010', ...] or [[0,0,1,0],]
    line can be a str or a list of ints: '0010' or [0,0,1,0]

    Usually, lines and line are both either composed of str or int!
    """
    if not lines: return False;

    assert type(line) == type(lines[0]) and\
            type(line[0]) == type(lines[0][0])

    if type(line) is str:
        if line in lines: return True
        l = [int(i) for i in list(line)]
    else:
        if line in lines: return True
        l = line

    
    # line is a positive slope /
    # remember that row index grows downwards
    if l[2]-l[0] < 0:
        for lin in lines:
            if type(lin) is str:
                x = [int(i) for i in list(lin)]
            else:
                x = lin
            # if x is a negative slope and line_overlaps
            if x[2]-x[0] > 0:
                if l[3] == x[3] and l[1] == x[1]:
                    return True

    # line is a negative slope \
    elif l[2]-l[0] > 0:
        for lin in lines:
            if type(lin) is str:
                x = [int(i) for i in list(lin)]
            else:
                x = lin
            # if x is a positive slope and overlaps
            if x[2]-x[0] < 0:
                if l[3] == x[3] and l[1] == x[1]:
                    return True

    return False

class TriangleBoard(object):
    """ 
    Contains the game components such as the current matrix 

    The matrix is a 4by4 2d list of zeros
    [ [(0,0), (0,1), (0,2), (0,3)],
      [(1,0), (1,1), (1,2), (1,3)],
      [(2,0), (2,1), (2,2), (2,3)],
      [(3,0), (3,1), (3,2), (3,3)] ]

    There are 42 possible lines (some slopes overlap):
    all_possible_valid_lines = [
            # all horizontal lines
            [0,0, 0,1], [0,1, 0,2], [0,2, 0,3], [1,0, 1,1],
            [1,1, 1,2], [1,2, 1,3], [2,0, 2,1], [2,1, 2,2],
            [2,2, 2,3], [3,0, 3,1], [3,1, 3,2], [3,2, 3,3],

            # all vertical lines
            [0,0, 1,0], [0,1, 1,1], [0,2, 1,2], [0,3, 1,3],
            [1,0, 2,0], [1,1, 2,1], [1,2, 2,2], [1,3, 2,3],
            [2,0, 3,0], [2,1, 3,1], [2,2, 3,2], [2,3, 3,3],

            # all positive slopes
            [1,0, 0,1], [1,1, 0,2], [1,2, 0,3], [2,0, 1,1],
            [2,1, 1,2], [2,2, 1,3], [3,0, 2,1], [3,1, 2,2],
            [3,2, 2,3], 

            # all negative slopes
            [0,0, 1,1], [0,1, 1,2], [0,2, 1,3], [1,0, 2,1],
            [1,1, 2,2], [1,2, 2,3], [2,0, 3,1], [2,1, 3,2],
            [2,2, 3,3],
        ]
    """
    
    def __init__(self, server):
        self.server = server
        self.lines = []

    def is_ongoing(self):
        """ 
        Check if all possible lines have been drawn.
        I counted 33 - no duplicates or overlaps.
        """
        return len(self.lines) < 33

    def join_lines(self):
        """ 
        return the lines as a joined string separated by commas.
        e.g.
        ['0011', '0001'] 
        returns '0011,0001,'
        """
        return ','.join(self.lines)

    def ints_to_line(self, ints):
        """ return a list of ints and join them to a string """
        return ''.join([str(i) for i in ints])

    def add_line(self, service, line):
        """
        The input is a string containing 4 numbers corresponding to
        the x1,y1 x2,y2 coordinates in the server's triangle's matrix.
            - this attempts to create a line in the matrix.

        The result is a string containing the status character 
        followed by the all the lines drawn so far.
            - the status character is either 0 or 1
                0 if failed (because of overlapping lines or 
                non-existing points or line is invalid)
                1 if success 
                2 if 1 occured and a new triangle has been produced
                    * if this is the case, another turn is given to 
                        this player
        """
        if not line_is_valid(line) or\
            line_overlaps(line, self.lines): 
            # New line is added - fail - update the gui
            self.server.gui.sendAddLineResult(FAIL, service, line)
            return FAIL

        # add the line
        self.lines.append(line)

        # check if the line creates a new triangle
        l = [int(i) for i in list(line)]
        points, convert = 0, self.ints_to_line

        def exists(*args):
            x = True
            for arg in args:
                if convert(arg) not in self.lines:
                    x = False
            if x: return 1
            else: return 0

        # if line is horizontal
        if l[0] == l[2]:
            # UPPER
            l_neg = [l[0]-1, l[1], l[2], l[3]]
            l_pos = [l[0], l[1], l[0]-1, l[1]+1]
            # negative slope exist
            if convert(l_neg) in self.lines:
                points += exists([l[0]-1, l[1], l[0], l[1]])
            # positive slope exist
            elif convert(l_pos) in self.lines:
                points += exists([l[2]-1, l[3], l[2], l[3]])

            # LOWER
            l_neg = [l[0], l[1], l[0]+1, l[1]+1]
            l_pos = [l[0]+1, l[1], l[2], l[3]]
            # negative slope exist
            if convert(l_neg) in self.lines:
                points += exists([l[2], l[3], l[2]+1, l[3]])
            # positive slope exist
            elif convert(l_pos) in self.lines:
                points += exists([l[0], l[1], l[0]+1, l[1]])
    
        # if line is vertical
        elif l[1] == l[3]:
            # LEFT
            l_neg = [l[0], l[1]-1, l[2], l[3]]
            l_pos = [l[2], l[3]-1, l[0], l[1]]
            # negative slope exist
            if convert(l_neg) in self.lines:
                points += exists([l[0], l[1]-1, l[0], l[1]])
            # positive slope exist
            elif convert(l_pos) in self.lines:
                points += exists([l[2], l[3]-1, l[2], l[3]])

            # RIGHT
            l_neg = [l[0], l[1], l[2], l[3]+1]
            l_pos = [l[2], l[3], l[0], l[1]+1]   
            # negative slope exist
            if convert(l_neg) in self.lines:
                points += exists([l[2], l[3], l[2], l[3]+1])
            # positive slope exist    
            elif convert(l_pos) in self.lines:
                points += exists([l[0], l[1], l[0], l[1]+1])

        # Note that unlike the vertical and horizontal lines,
        # slopes can only have 2 possible triangles (look at matrix!)

        # if line is a positive slope /
        elif l[2]-l[0] < 0 and l[3]-l[1] > 0:
            # TOP
            l_hor = [l[2], l[3]-1, l[2], l[3]]
            l_ver = [l[0]-1, l[1], l[0], l[1]]
            points += exists(l_hor, l_ver)
            # BOTTOM
            l_hor = [l[0], l[1], l[0], l[1]+1]
            l_ver = [l[2], l[3], l[2]+1, l[3]]
            points += exists(l_hor, l_ver)

        # if line is a negative slope \
        elif l[2]-l[0] > 0 and l[3]-l[1] > 0:
            # TOP
            l_hor = [l[0], l[1], l[0], l[1]+1]
            l_ver = [l[2]-1, l[3], l[2], l[3]]
            points += exists(l_hor, l_ver)
            # BOTTOM
            l_hor = [l[2], l[3]-1, l[2], l[3]]
            l_ver = [l[0], l[1], l[0]+1, l[1]]
            points += exists(l_hor, l_ver)

        # add the points
        service.score += points
        # New line is added - success - update the gui
        self.server.gui.sendAddLineResult(SUCCESS, service, line)

        # return the result
        if points:
            return SUCCESS_NEW
        else:
            return SUCCESS        

class TriangleGUIManager(object):
    """ Handles communication with the GUI module written in JAVA """
    
    def __init__(self, server, sock):
        self.server = server
        self.sock = sock

    def end(self):
        """ 
        Posts the final scores.
        """
        servs = self.server.services
        self.sock.sendall('4'+','+str(servs[1].score)+','+\
                            str(servs[2].score)+','+'\n')
        

    def sendAddLineResult(self, result, service, line):
        """ 
        sends result of line drawn, player service id
        and score that drew the line 
        and the line itself separated by commas
        Notes:
            1. sendall does not block like recv does so sending 
                in the same thread as main will not block the game!
                We may want to block for safety...
            2. need to append '\n' to strings being sent to Java code.
               In the Java gui source, BufferedReader.readLine is used
        
        """
        self.sock.sendall(result+','+str(service.sid)+','+\
                        str(service.score)+','+line+'\n')

class TriangleServer(Thread):
    """
    Accepts 3 connections.
    The first connection must be the GUI.
    For each connection that is accepted, a new thread is launched.

    Once both players have connected, the game begins.
    The first player to connect will get to have the first turn.
    """

    def __init__(self, host='localhost', port=8000):
        super(TriangleServer, self).__init__()
        config = (socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket = socket.socket(*config)
        self.server_socket.bind( (host, port) )
        self.server_socket.listen(2)

        self.services = {}
        self.triangle = TriangleBoard(self)
        self.gui = None

    def run(self):
        servs = self.services
        tri = self.triangle

        print "Connect the GUI module."
        self.gui = TriangleGUIManager(self,
                                self.server_socket.accept()[0])

        print "Connect player 1 and 2."
        while len(servs) < 2:
            sock = self.server_socket.accept()[0]
            service = TriangleServerService(self, tri, sock, 
                                        len(servs)+1)
            servs[service.sid] = service
            
        print "All set. Let the game begin."
        # Player 1 starts first
        turn = 1
        while tri.is_ongoing():
            servs[turn].start_turn()
            if turn == 1: turn = 2
            else: turn = 1

        # game is over - flag both clients
        if servs[1].score > servs[2].score: 
            winner, loser = 1, 2
        elif servs[1].score < servs[2].score: 
            winner, loser = 2, 1
        else: # tie
            winner, loser = int(TIE), int(TIE)

        self.end_game(winner, loser)  

    def player_violation(self, sid):
        """ 
        Player with the given sid drew an invalid line.
        Game is over. This player lost.
        """
        print "%s drew an invalid line and is disqualified." %\
                     (str(self.services[sid]),)
        loser = sid
        if loser is 1: winner = 2
        else: winner = 1
        self.end_game(winner, loser)
        
    def end_game(self, winner, loser):
        """ 
        Notifies the players that game is over and who won.
        Prints the winner and loser and closes all connections
        and finally exits 
        """
        self.gui.end()
        for service in self.services.itervalues():
            service.end(winner)        

        if winner is not TIE:
            print "%s won with score of %s." %\
                    (self.services[winner],
                         self.services[winner].score)
            print "%s lost with score of %s." %\
                    (self.services[loser], self.services[loser].score)
        else:
            print "It is a tie!"        

        self.server_socket.close()
        sys.exit(0)        

class TriangleServerService(object):
    """
    A dedicated listener for a client in the TriangleServer.
    Accepts client requests including getting the matrix, sendind the
    next move, etc.
    """
    
    def __init__(self, server, triangle, sock, sid):
        super(TriangleServerService, self).__init__()
        self.server = server
        self.tri = triangle
        self.sock = sock
        self.sid = sid
        self.score = 0
        self.in_service = True

    def __str__(self):
        return 'Player %s' % (str(self.sid),)

    def start_turn(self):
        """ 
        Receive input from the client and sendall back the result.

        First, sendall the start flag to the client and all the 
        lines drawn so far.
        Then, see TriangleBoard.add_line doc string.

        IMPORTANT! 
            1. need to append '\n' to all strings sent to clients
            because in the BufferedReader.readLine in Java expects it
        """
        while self.in_service:
            # delay before the next turn of the game
            time.sleep(TURN_DELAY)

            self.sock.sendall(START+self.tri.join_lines()+'\n')
            # line length is 4 but it may be followed by
            # '\r\n' or '\r' or '\n', an escape char is 1 byte
            # so max len of result is 6
            line = self.sock.recv(6) 
            # strip line feed and carriage return if any
            line = line.replace('\r', '').replace('\n', '')
            
            result = self.tri.add_line(self, line)
            if result is SUCCESS or\
                not self.server.triangle.is_ongoing(): 
                break
            elif result is FAIL:
                self.server.player_violation(self.sid)

    def end(self, wsid):
        """ 
        Tells the client that it is game over by sending the game over
        flag, followed by a win or lose flag - FAIL:lose, SUCCESS:win
        """
        if wsid == self.sid: status = SUCCESS
        elif wsid == int(TIE): status = TIE
        else: status = FAIL
        self.in_service = False
        self.sock.sendall(END+status+'\n')
        self.sock.close() 

if __name__ == "__main__":
    server = TriangleServer()   
    server.start()
