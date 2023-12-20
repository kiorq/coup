class GameError(Exception):
    """ Generic game error """
    pass

class EligiblePlayerNotFound(GameError):
    """ used during automation and a eligible target player could not be found """
    pass