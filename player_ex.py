#!/usr/bin/env python
# -*- coding: utf-8 -*- 

"""
An example triangle AI.
This AI simply picks a random line from all the possible set of lines.
The AI must be replaced!

Homework for AI 2013
Written by Vandolf Estrellado
"""

from triangle_client import TriangleClient
from triangle import line_overlaps, line_is_valid

class MyTriangleClient(TriangleClient):
    
    def drawLine(self, lines):
        """ 
        This is called when it's this player's turn to draw a line.
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
        * There are 42 possible lines, 33 of which will be used
            in a single game (discounting the overlapping lines)

        ** This method needs to return a valid, non-overlapping 
            line or you lose. So, you should definitely check the
            validity of the line first before returning it to avoid
            disqualification. Do this by:

            if not line_overlaps(my_line, lines) and\
                line_is_valid(my_line):
                # fix it. It should never go here if you know what you
                # are doing.
            return my_line

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
        if 'randint' not in dir():
            from random import randint

        # note that a good algorithm will not store 
        # all possible lines in memory but instead determine
        # the viability of the next line to draw from the 
        # current lines
        # note that I know how to generate all the lines
        # but I hardcoded it here instead for readability
        if not hasattr(self, 'all_possible_valid_lines'):
            self.all_possible_valid_lines = [
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

        all_lines = self.all_possible_valid_lines
        
        # choose a random line
        chosen_line_index = randint(0, len(all_lines)-1)
        chosen_line = all_lines[chosen_line_index]
        
        # if the line is invalid, remove it and choose another
        if all_lines: # not empty
            while line_overlaps(chosen_line, lines) or\
                not line_is_valid(chosen_line):
                all_lines.remove(chosen_line)
                chosen_line_index = randint(0, len(all_lines)-1)
                chosen_line = all_lines[chosen_line_index]

        return chosen_line     

if __name__ == "__main__":
    my_player = MyTriangleClient()
    my_player.play()
