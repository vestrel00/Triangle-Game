#!/usr/bin/env python
# -*- coding: utf-8 -*- 

"""
A client for interfacing with the triangle server.

Homework for AI 2013
Written by Vandolf Estrelado
"""

import socket, sys
from triangle import line_overlaps, line_is_valid,\
FAIL, SUCCESS, SUCCESS_NEW, START, END

class TriangleClient(object):
    """ client for the triangle server """
    
    def __init__(self, host='localhost', port=8000):
        """ connect to the server """
        config = (socket.AF_INET, socket.SOCK_STREAM)
        self.sock = socket.socket(*config)
        self.sock.connect( (host, port) )
        self.is_playing = True
        
    def end(self, status):
        """ 
        close the connection, print status and return the status
        """
        if status == FAIL:
            print "You Lost!"
        else:
            print "You Won!"

        self.is_playing = False
        self.sock.close()
        sys.exit(0)
        
    def play(self):
        """
        Communicate with the server.
        Data received comes from triangle.TriangleServerService

        Step 1,
            wait for the data from the server
            max_length(data) = max(lines)*len(line) + len(commas) + 2
            2 = flag(1) + line feed '\n' (1) 
            note that server will never send a carriage return '\r'
            max(lines) is 33 (I counted- not including the overlaping
            slopes ). So 33*4 + 33 + 2 = 157

        Step 2,
            depending on the first character of data (the flag),
            react accordingly.
        """
        while self.is_playing:
            # Step 1
            data = self.sock.recv(200) # max is 157 but to be safe
            # strip the line feed - 
            # not necessary since split() does this
            data = data.replace('\n', '')
        
            # Step 2
            flag = data[0]
            if flag == END:
                self.end(data[1])
            else:
                # convert lines to a list of lists
                lines_str = data[1:]
                lines_str = lines_str.split(',')
                lines_int = []
                
                # lines_str is initially [''] which is not None!
                # so prevent lines_int to be [ [] ] - which is None 2!
                if lines_str[0]:
                    for line in lines_str:
                        lines_int.append([int(i) for i in list(line)])
                l =''.join([str(i) for i in self.drawLine(lines_int)])
                self.sock.sendall(l)

    def drawLine(self, lines):
        """ 
        This is the method to implement by the student.
        This method provides the lines that are currently drawn
        in the matrix.

        Each line in lines is a list of ints in this format:
        [x1, y1, x2, y2]
        The above cartesian coordinates correspond to the matrix:
        The matrix is a 4by4 2d list containing useless integers
        [ [(0,0), (0,1), (0,2), (0,3)],
          [(1,0), (1,1), (1,2), (1,3)],
          [(2,0), (2,1), (2,2), (2,3)],
          [(3,0), (3,1), (3,2), (3,3)] ]

        e.g. lines = [ [0,0, 0,1], [1,0, 0,1], [0,0, 1,0], ]
            this contains 3 lines that forms a triangle 

        * Note that lines can be an empty list []

        ** This method needs to return a valid, non-overlapping 
            line or you lose. So, you should definitely check the
            validity of the line first before returning it to avoid
            disqualification. Do this by:

            if not line_overlaps(my_line, lines) and\
                line_is_valid(my_line):
                return my_line
            else:
                # fix it. It should never go here if you know what you
                # are doing.
            

        1) Use line_is_valid(line) to check if the line follows 
        the convention below.
        
        As a convention of the game, lines should be    
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

        2) Use line_overlaps(line, lines) to check if line is already
            drawn (already in lines) and if it overlaps another line.
        """
        # my_line = [] 
        # TODO: determine my_line
        #if line_overlaps(my_line, lines) or\
        #    not line_is_valid(my_line):
        #    fix it. It should never go here if you know what you
        #    are doing.
        #return my_line
        pass
    
