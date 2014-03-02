#!/usr/bin/env python
# -*- coding: utf-8 -*- 

"""
This is my implementation of a somewhat "smart" AI player for the 
triangle game. This AI only thinks 1 step ahead but is still much
better than a random picker. It thinks 1 step ahead in that it draws
lines in a way that will not leave the other player make a triangle
in the next turn. It is a look-ahead algorithm.

Homework for AI 2013
Written by Vandolf Estrellado
"""

from random import shuffle

from triangle_client import TriangleClient
from triangle import line_overlaps, line_is_valid

class MyTriangleClient(TriangleClient):
    
    def incomplete_exist(self, line, lines, inc_type):
        """
        Returns True if the given line forms a triangle given an    
        inc_type, which is the type of incomplete triangle that
        needs to exist in lines for line to form a triangle.

        inc_type can be:
            1. hor_top
            2. hor_bot
            3. ver_left
            4. ver_right
            5. pos_top
            6. pos_bot
            7. neg_top
            8. neg_bot
        """
        if inc_type == "hor_top":
            neg = [line[0]-1, line[1], line[2], line[3]]
            pos = [line[0], line[1], line[0]-1, line[1]+1]
            l = [line[0]-1, line[1], line[0], line[1]]
            r = [line[2]-1, line[3], line[2], line[3]]
            return (neg in lines and l in lines) or\
                        (pos in lines and r in lines)
        elif inc_type == "hor_bot":
            neg = [line[0], line[1], line[0]+1, line[1]+1]
            pos = [line[0]+1, line[1], line[2], line[3]]
            l = [line[0], line[1], line[0]+1, line[1]]
            r = [line[2], line[3], line[2]+1, line[3]]
            return (neg in lines and r in lines) or\
                        (pos in lines and l in lines)
        elif inc_type == "ver_left":
            neg = [line[0], line[1]-1, line[2], line[3]]
            t = [line[0], line[1]-1, line[0], line[1]]
            pos = [line[2], line[3]-1, line[0], line[1]]
            b = [line[2], line[3]-1, line[2], line[3]]
            return (neg in lines and t in lines) or\
                        (pos in lines and b in lines)
        elif inc_type == "ver_right":
            neg = [line[0], line[1], line[2], line[3]+1]
            pos = [line[2], line[3], line[0], line[1]+1] 
            t = [line[0], line[1], line[0], line[1]+1]
            b = [line[2], line[3], line[2], line[3]+1]
            return (neg in lines and b in lines) or\
                        (pos in lines and t in lines)
        elif inc_type == "pos_top":
            hor = [line[2], line[3]-1, line[2], line[3]]
            ver = [line[0]-1, line[1], line[0], line[1]]
            return (hor in lines and ver in lines) 
        elif inc_type == "pos_bot":
            hor = [line[0], line[1], line[0], line[1]+1]
            ver = [line[2], line[3], line[2]+1, line[3]]
            return (hor in lines and ver in lines) 
        elif inc_type == "neg_top":
            hor = [line[0], line[1], line[0], line[1]+1]
            ver = [line[2]-1, line[3], line[2], line[3]]
            return (hor in lines and ver in lines)  
        elif inc_type == "neg_bot":
            hor = [line[2], line[3]-1, line[2], line[3]]
            ver = [line[0], line[1], line[0]+1, line[1]]
            return (hor in lines and ver in lines)

    def line_complete(self, lines):
        """
        Checks for an incomplete triangle in lines and returns the
        line that will make it complete as well as the number of
        triangles that will be completed (1 or 2).
        Note that since I know that the lines I create are valid,
        I do not use line_is_valid in this method.
        """
        for l in lines:
            ### line is horizontal
            if l[0] == l[2]:
                # UPPER
                l_neg = [l[0]-1, l[1], l[2], l[3]]
                l_pos = [l[0], l[1], l[0]-1, l[1]+1]
                l_v = [l[0]-1, l[1], l[0], l[1]]
                r_v = [l[2]-1, l[3], l[2], l[3]]
                # negative slope exist
                if l_neg in lines and not line_overlaps(l_v, lines):
                    if self.incomplete_exist(l_v, lines, "ver_left"):
                        return l_v, 2
                    return l_v, 1
                # positive slope exist
                elif l_pos in lines and not line_overlaps(r_v, lines):
                    if self.incomplete_exist(r_v, lines, "ver_right"):
                        return r_v, 2
                    return r_v, 1
                # left vertical line exist
                elif l_v in lines and not line_overlaps(l_neg, lines):
                    if self.incomplete_exist(l_neg, lines, "neg_top"):
                        return l_neg, 2
                    return l_neg, 1
                # right vertical line exist
                elif r_v in lines and not line_overlaps(l_pos, lines):
                    if self.incomplete_exist(l_pos, lines, "pos_top"):
                        return l_pos, 2
                    return l_pos, 1

                # LOWER
                l_neg = [l[0], l[1], l[0]+1, l[1]+1]
                l_pos = [l[0]+1, l[1], l[2], l[3]]
                l_v = [l[0], l[1], l[0]+1, l[1]]
                r_v = [l[2], l[3], l[2]+1, l[3]]
                # negative slope exist
                if l_neg in lines and not line_overlaps(r_v, lines):
                    if self.incomplete_exist(r_v, lines, "ver_right"):
                        return r_v, 2
                    return r_v, 1
                # positive slope exist
                elif l_pos in lines and not line_overlaps(l_v, lines):
                    if self.incomplete_exist(l_v, lines, "ver_left"):
                        return l_v, 2
                    return l_v, 1
                # left vertical line exist
                elif l_v in lines and not line_overlaps(l_pos, lines):
                    if self.incomplete_exist(l_pos, lines, "pos_bot"):
                        return l_pos, 2
                    return l_pos, 1
                # right vertical line exist
                elif r_v in lines and not line_overlaps(l_neg, lines):
                    if self.incomplete_exist(l_neg, lines, "neg_bot"):
                        return l_neg, 2
                    return l_neg, 1

            # if line is vertical
            elif l[1] == l[3]:
                # LEFT
                l_neg = [l[0], l[1]-1, l[2], l[3]]
                l_pos = [l[2], l[3]-1, l[0], l[1]]
                t_h = [l[0], l[1]-1, l[0], l[1]]
                b_h = [l[2], l[3]-1, l[2], l[3]]
                # negative slope exist
                if l_neg in lines and not line_overlaps(t_h, lines):
                    if self.incomplete_exist(t_h, lines, "hor_top"):
                        return t_h, 2
                    return t_h, 1
                # positive slope exist
                elif l_pos in lines and not line_overlaps(b_h, lines):
                    if self.incomplete_exist(b_h, lines, "hor_bot"):
                        return b_h, 2
                    return b_h, 1
                # top horizontal line exist
                elif t_h in lines and not line_overlaps(l_neg, lines):
                    if self.incomplete_exist(l_neg, lines, "neg_bot"):
                        return l_neg, 2
                    return l_neg, 1
                # bottom horizontal line exist
                elif b_h in lines and not line_overlaps(l_pos, lines):
                    if self.incomplete_exist(l_pos, lines, "pos_top"):
                        return l_pos, 2
                    return l_pos, 1

                # RIGHT
                l_neg = [l[0], l[1], l[2], l[3]+1]
                l_pos = [l[2], l[3], l[0], l[1]+1] 
                t_h = [l[0], l[1], l[0], l[1]+1]
                b_h = [l[2], l[3], l[2], l[3]+1] 
                # negative slope exist
                if l_neg in lines and not line_overlaps(b_h, lines):
                    if self.incomplete_exist(b_h, lines, "hor_bot"):
                        return b_h, 2
                    return b_h, 1
                # positive slope exist    
                elif l_pos in lines and not line_overlaps(t_h, lines):
                    if self.incomplete_exist(t_h, lines, "hor_top"):
                        return t_h, 2
                    return t_h, 1
                # top horizontal line exist
                elif t_h in lines and not line_overlaps(l_pos, lines):
                    if self.incomplete_exist(l_pos, lines, "pos_bot"):
                        return l_pos, 2
                    return l_pos, 1
                # bottom horizontal line exist
                elif b_h in lines and not line_overlaps(l_neg, lines):
                    if self.incomplete_exist(l_neg, lines, "neg_top"):
                        return l_neg, 2
                    return l_neg, 1

            # Note that unlike the vertical and horizontal lines,
            # slopes can only have 2 possible triangles

            # if line is a positive slope /
            elif l[2]-l[0] < 0 and l[3]-l[1] > 0:
                # TOP
                t_h = [l[2], l[3]-1, l[2], l[3]]
                l_v = [l[0]-1, l[1], l[0], l[1]]
                if t_h in lines and not line_overlaps(l_v, lines):
                    if self.incomplete_exist(l_v, lines, "ver_left"):
                        return l_v, 2
                    return l_v, 1
                elif l_v in lines and\
                        not line_overlaps(t_h, lines):
                    if self.incomplete_exist(t_h, lines, "hor_top"):
                        return t_h, 2
                    return t_h, 1
                # BOTTOM
                b_h = [l[0], l[1], l[0], l[1]+1]
                r_v = [l[2], l[3], l[2]+1, l[3]]
                if b_h in lines and not line_overlaps(r_v, lines):
                    if self.incomplete_exist(r_v, lines, "ver_right"):
                        return r_v, 2
                    return r_v, 1
                elif r_v in lines and\
                        not line_overlaps(b_h, lines):
                    if self.incomplete_exist(b_h, lines, "hor_bot"):
                        return b_h, 2
                    return b_h, 1

            # if line is a negative slope \
            elif l[2]-l[0] > 0 and l[3]-l[1] > 0:
                # TOP
                t_h = [l[0], l[1], l[0], l[1]+1]
                r_v = [l[2]-1, l[3], l[2], l[3]]
                if t_h in lines and not line_overlaps(r_v, lines):
                    if self.incomplete_exist(r_v, lines, "ver_right"):
                        return r_v, 2
                    return r_v, 1
                elif r_v in lines and\
                        not line_overlaps(t_h, lines):
                    if self.incomplete_exist(t_h, lines, "hor_top"):
                        return t_h, 2
                    return t_h, 1
                # BOTTOM
                b_h = [l[2], l[3]-1, l[2], l[3]]
                l_v = [l[0], l[1], l[0]+1, l[1]]
                if b_h in lines and not line_overlaps(l_v, lines):
                    if self.incomplete_exist(l_v, lines, "ver_left"):
                        return l_v, 2
                    return l_v, 1
                elif l_v in lines and\
                        not line_overlaps(b_h, lines):
                    if self.incomplete_exist(b_h, lines, "hor_bot"):
                        return b_h, 2
                    return b_h, 1
    
    def drawLine(self, lines):
        """
        Strategy -----------------------------------------------------
        Step 1: check for incomplete triangles in lines
            - if there is such a triangle, then complete it.
        Step 2: if step 1 does not return a line, choose a line that
                will not leave in an incomplete triangle for the other
                player after this turn. 
        Step 3: if step 2 does not return a line, choose a line that
                will result in an incomplete triangle but will result
                in the least amount of triangles being completed
                by the other player in the following turn.
        Notes --------------------------------------------------------
        The gameboard is an imaginary object that has 
        the following layout:
        --------------------------> m
        | (0,0) (0,1) (0,2) (0,3)   
        | (1,0) (1,1) (1,2) (1,3)   
        | (2,0) (2,1) (2,2) (2,3)   
        | (3,0) (3,1) (3,2) (3,3)   
        n (grows downwards)
        """
        # first turn of the game, choose arbitrary line.
        if not lines:
            return [0, 0, 0, 1] 
        # update the list of lines that are not yet drawn
        lines_to_rmv = []
        for line in self.all_possible_valid_lines:
            if line_overlaps(line, lines) or\
                not line_is_valid(line):
                lines_to_rmv.append(line)
        for l in lines_to_rmv:
            self.all_possible_valid_lines.remove(l)

        # if step 1 fails, do not let opponent predict what
        # we will draw        
        shuffle(self.all_possible_valid_lines)

        # Step 1
        c = self.line_complete(lines)
        if c:
            return c[0]
        # Step 2
        for line in self.all_possible_valid_lines:
            tmp = lines[:]
            tmp.append(line)
            c = self.line_complete(tmp)
            if not c:
                return line
        # Step 3
        min_score, l = 9001, None
        for line in self.all_possible_valid_lines:
            score = 0
            tmp = lines[:]
            tmp.append(line)
            while True:
                c = self.line_complete(tmp)
                if c:
                    score += c[1]
                    tmp.append(c[0])
                    continue
                break
            if score < min_score or not l:
                min_score = score
                l = line

        return l

if __name__ == "__main__":
    my_player = MyTriangleClient()
    my_player.play()
