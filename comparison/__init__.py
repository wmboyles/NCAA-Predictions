"""
When using the comparison module, you'll likely want to do the following:

import comparison

tourney = comparision.Tournament(...)
comparator = comparison.team_comparators.SomeComparator(...)
tourney.simulate(comparator)
"""

from .team_comparators import *
from .tournament import Tournament
