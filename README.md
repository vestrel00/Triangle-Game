# What is this?
This was an assignment for AI that required students' programs to
compete in order to win the triangle game. This provides an interface
for the students' programs- implementing the 'gameboard' backend logic
written in Python and a visual front-end to show the current status of
the game written in Java using LibGDX for rendering.

Each module communicates with one another via sockets.  
Server to client, client to server, and server to gui.

The client may be written in C/C++, Java, or Python.   
The base code for each language is provided with methods needed to parse server and game data. Therefore, students will simply need
to subclass the given class and implement the AI.

# The triangle game's mechanics

1. There is a 4 by 4 matrix in the form of a 2d list/array with the
    following indices containing an arbitrary value of zeros.

    [ [(0,0), (0,1), (0,2), (0,3)],  
      [(1,0), (1,1), (1,2), (1,3)],   
      [(2,0), (2,1), (2,2), (2,3)],  
      [(3,0), (3,1), (3,2), (3,3)] ]  

2. Two players are required to play.
3. Each player is a program written in any language.
4. Each player takes turns 'drawing' a line in the matrix.
5. There can be no duplicate or overlapping lines.
6. If a player draws a valid line and 1 or more triangle is formed
    then the player receives 1 point for each triangle formed.
    
    * If a triangle is formed, then the player who formed the 
        triangle(s) gets another turn.
    * Player with most points win.

# Client and server communication

1. Player 1 and 2 connects to server 'localhost' at port 8000.
2. Player 1 goes first and alternates with player 2.
3. The server sends a flag and the currently drawn lines as a string  
   (to the player to start its turn)
4. Player's AI determines the best line to draw next and sends this
    coordinate to the server.
5. Server sends client the result of drawing the line.
    
    * If 1 or more triangles are formed by drawing the line, then the
       server flags the player to draw another line.
    * If the line drawn is an invalid line then the player
        automatically loses.
 
        * An invalid line is a line that is already drawn, 
            overlaps another line, or does not represent a line
            in the matrix (IndexError or wrong format).

**Note:** each student need only to implement the AI to determine the
line to draw. For more specifics (like what object the client sends to
the server) see the base code to be subclassed. Documentation and
examples are provided.

# Code License : WTFPL
Do what ever you want with the code - [WTFPL](http://www.wtfpl.net/)

