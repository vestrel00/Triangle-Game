#!/usr/bin/env python
# -*- coding: utf-8 -*- 

"""
The server for interfacing between two triangle programs.

Homework for AI 2013
Written by Vandolf Estrelado
"""

from threading import Thread
import socket


class TriangleBoard(object):
    """ 
    Contains the game components such as the current matrix 

    The matrix is a 4by4 2d list of zeros
    [ [(0,0), (0,1), (0,2), (0,3)],
      [(1,0), (1,1), (1,2), (1,3)],
      [(2,0), (2,1), (2,2), (2,3)],
      [(3,0), (3,1), (3,2), (3,3)] ]

    """
    
    def __init__(self):
        self.matrix = [ [0 for i in range(4)] for i in range(4) ]
        self.lines = []
        self.is_ongoing = True

    def join_lines(self):
        """ 
        return the lines as a joined string.
        e.g.
        ['0011', '0001'] 
        returns '00110001'
        """
        return ''.join(self.lines)

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
        if not self.is_valid(line) or self.overlaps(line): 
            return '0'

        # add the line
        self.lines.append(line)

        # check if the line creates a new triangle
        l = [int(i) for i in list(line)]
        points, convert = 0, self.ints_to_line
        # if line is horizontal
        if l[0] == l[2]:
            # UPPER
            l_neg = [l[0]-1, l[1], l[0], l[1]+1]
            l_pos = [l[0], l[1], l[0]-1, l[1]+1]
            # negative slope exist
            if convert(l_neg) in self.lines:
                l0 = [l[0]-1, l[1], l[0], l[1]]
                if convert(l0) in self.lines:
                    points += 1
            # positive slope exist
            elif convert(l_pos) in self.lines:
                l0 = [l[0]-1, l[1]+1, l[0], l[1]+1]
                if convert(l0) in self.lines:
                    points += 1

            # LOWER
            l_neg = [l[0], l[1], l[0]+1, l[1]+1]
            l_pos = [l[0]+1, l[1], l[0], l[1]+1]
            # negative slope exist
            if convert(l_neg) in self.lines:
                l0 = [l[0], l[1], l[0]+1, l[1]]
                if convert(l0) in self.lines:
                    points += 1
            # positive slope exist
            elif convert(l_pos) in self.lines:
                l0 = [l[0], l[1]+1, l[0]+1, l[1]+1]
                if convert(l0) in self.lines:
                    points += 1
    
        # if line is vertical
        elif l[1] == l[3]:
            pass # TODO
       
        # if line is a positive slope /
        elif l[2]-l[0] < 0 and l[3]-l[1] > 0:
            pass #TODO

        # if line is a negative slope \
        elif l[2]-l[0] > 0 and l[3]-l[1] > 0:
            pass #TODO

        if points:
            service.score += points
            return '2'
        else:
            return '1'        

    def is_valid(self, line):
        """ 
        Returns True if the line is a valid line.
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
        m = self.matrix
        try:
            m[l[0]][l[1]]
            m[l[2]][l[3]]
        except IndexError:
            return False
        else:
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

    def overlaps(self, line):
        """ returns True if the given line overlaps another """
        if line in self.lines: return True

        l = [int(i) for i in list(line)]

        # line is a positive slope /
        # remember that row index grows downwards
        if l[2]-l[0] < 0:
            for lin in self.lines:
                x = [int(i) for i in list(lin)]
                # if x is a negative slope and overlaps
                if x[2]-x[0] > 0 and l[3] == x[3] and l[1] == x[1]:
                    return True

        # line is a negative slope \
        else:
            for lin in self.lines:
                x = [int(i) for i in list(lin)]
                # if x is a positive slope and overlaps
                if x[2]-x[0] < 0 and l[3] == x[3] and l[1] == x[1]:
                    return True

        return False

class TriangleGUIManager(Thread):
    """ Handles communication with the GUI module """
    
    def __init__(self, server, sock):
        super(TriangleGUIManager, self).__init__()
        self.server = server
        self.sock = sock

    def update(self):
        """ 
        Sends a flag to the GUI module to update its screen
        with the drawn lines
        """
        pass # TODO

    def run(self):
        pass # TODO
                

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
        self.triangle = TriangleBoard()
        self.gui = None

    def run(self):
        servs = self.services
        tri = self.triangle

        print "Connect the GUI module."
        self.gui = TriangleGUIManager(self,
                                self.server_socket.accept()[0])

        print "Connect player 1 and 2."
        while len(servs) < 3:
            sock = self.server_socket.accept()[0]
            service = TriangleServerService(tri, sock, len(servs)+1)
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
        else: 
            winner, loser = 2, 1
    
        for service in servs:
            service.end(winner)

        print "%s won with score of %s." % (str(servs[winner]),
                                            servs[winner].score)
        print "%s lost with score of %s." % (str(servs[loser]),
                                            servs[loser].score)
        self.server_socket.close()  
        

class TriangleServerService(object):
    """
    A dedicated listener for a client in the TriangleServer.
    Accepts client requests including getting the matrix, sendind the
    next move, etc.
    """
    
    def __init__(self, triangle, sock, sid):
        super(TriangleServerService, self).__init__()
        self.tri = triangle
        self.sock = sock
        self.sid = sid
        self.score = 0

    def __str__(self):
        return 'Player %s' %s (str(self.sid),)

    def start_turn(self):
        """ 
        Receive input from the client and send back the result.

        First, send the start flag 1 to the client and all the 
        lines drawn so far.

        Then, see TriangleBoard.add_line doc string.
        """
        while True:
            self.sock.send('1'+self.tri.join_lines())
            line = self.sock.recv(4)    
            result = self.tri.add_line(self, line)
            self.sock.send(result+self.tri.join_lines())
            if result is 1: break

    def end(self, wsid):
        """ 
        Tells the client that it is game over by sending the game over
        flag 0, followed by a win or lose flag - 0:lose, 1:win
        """
        if wsid == self.sid: status = '1'
        else: status = '0'
        self.sock.send('0'+status)
        self.sock.close()
            

if __name__ == "__main__":
    server = TriangleServer()   
    server.start()
