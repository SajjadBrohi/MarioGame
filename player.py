"""Class for representing a Player entity within the game."""

__version__ = "1.1.0"

from game.entity import DynamicEntity


class Player(DynamicEntity):
    """A player in the game"""
    _type = 3

    def __init__(self, name: str = "Mario", max_health: float = 20):
        """Construct a new instance of the player.

        Parameters:
            name (str): The player's name
            max_health (float): The player's maximum & starting health
        """
        super().__init__(max_health=max_health)

        self._name = name
        self._score = 0
        self._invincible = False
        self._invincibility_time = 0
        self._invincibility_health = 5
        self._id = 'player'

    def get_id(self):
        return self._id

    def get_name(self) -> str:
        """(str): Returns the name of the player."""
        return self._name

    def get_score(self) -> int:
        """(int): Get the players current score."""
        return self._score

    def change_score(self, change: float = 1):
        """Increase the players score by the given change value."""
        self._score += change

    def set_invincible(self, change):
        """Sets the invincibility status of the player"""
        self._invincible = change
        if self._invincible:
            #450 is roughly equal to 10 seconds
            self._invincibility_time += 450

    def get_invincible_value(self):
        """Retrieves the invincibility status of the player"""
        return self._invincible

    def get_invincibility_time(self):
        """Retrieves the invincibility time of the player"""
        return self._invincibility_time

    def health_in_invincibility(self):
        """Retrieves the health of the player during invincibility"""
        return self._invincibility_health

    def __repr__(self):
        return f"Player({self._name!r})"
