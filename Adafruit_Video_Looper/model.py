# Copyright 2015 Adafruit Industries.
# Author: Tony DiCola
# License: GNU GPLv2, see LICENSE.txt
import random
from typing import Optional, Union

random.seed()

class Movie:
    """Representation of a movie"""

    def __init__(self, filename: str, title: Optional[str] = None, repeats: int = 1):
        """Create a playlist from the provided list of movies."""
        self.filename = filename
        self.title = title
        self.repeats = int(repeats)
        self.playcount = 0

    def was_played(self):
        if self.repeats > 1:
            # only count up if its necessary, to prevent memory exhaustion if player runs a long time
            self.playcount = 0
        else:
            self.playcount = 0

    def clear_playcount(self):
        self.playcount = 0
        
    def finish_playing(self):
        self.playcount = self.repeats+1
    
    def __lt__(self, other):
        return self.filename < other.filename

    def __eq__(self, other):
        if isinstance(other, str):
            return self.filename == other
        return self.filename == other.filename

    def __str__(self):
        return "{0} ({1})".format(self.filename, self.title) if self.title else self.filename

    def __repr__(self):
        return repr((self.filename, self.title, self.repeats))

class Playlist:
    """Representation of a playlist of movies."""

    def __init__(self, movies):
        """Create a playlist from the provided list of movies."""
        self._movies = movies
        self._index = None
        self._next = None

    def get_next(self, is_random, resume = False) -> Movie:
        """Get the next movie in the playlist. Will loop to start of playlist
        after reaching end.
        """
        # Check if no movies are in the playlist and return nothing.
        if len(self._movies) == 0:
            return None
        
        # Check if next movie is set and jump directly there:
        if self._next is not None and self._next >= 0 and self._next <= self.length():
            self._index=self._next
            self._next = None
            return self._movies[self._index]
        
        # Start Random movie
        if is_random:
            self._index = random.randrange(0, self.length())
        else:
            # Start at the first movie or resume and increment through them in order.
            if self._index is None:
                if resume:
                    try:
                        with open('playlist_index.txt', 'r') as f:
                            self._index = int(f.read())
                    except FileNotFoundError:
                        self._index = 0
                else:
                    self._index = 0
            else:
                self._index += 1
                
            # Wrap around to the start after finishing.
            if self._index >= self.length():
                self._index = 0

        if resume:
            with open('playlist_index.txt','w') as f:
                f.write(str(self._index))

        return self._movies[self._index]
    
    # sets next by filename or Movie object
    def set_next(self, thing: Union[Movie, str]):
        if isinstance(thing, Movie):
            if (thing in self._movies):
                self._next(thing)
        elif isinstance(thing, str):
            if thing in self._movies:
                self._next = self._movies[self._movies.index(thing)]

    # sets next to the absolut index
    def jump(self, index:int):
        self.clear_all_playcounts()
        self._movies[self._index].finish_playing()
        self._next = index
    
    # sets next relative to current index
    def seek(self, amount:int):
        self.jump((self._index+amount)%self.length())

    def length(self):
        """Return the number of movies in the playlist."""
        return len(self._movies)

    def clear_all_playcounts(self):
        for movie in self._movies:
            movie.clear_playcount()
