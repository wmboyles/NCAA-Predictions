"""
When using the comparison module, you'll likely want to do the following:

import comparison

tourney = comparision.Tournament(...)
comparator = comparison.team_comparators.SomeComparator(...)
tourney.simulate(comparator)
"""

from .game_attrs import TeamSeeding
from .tournament import Tournament
from .team_comparators import TeamComparator
