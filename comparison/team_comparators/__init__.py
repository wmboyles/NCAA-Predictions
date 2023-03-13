from .team_comparator import TeamComparator, HydridComparator
from .bradley_terry_comparator import BradleyTerryComparator
from .elo_comparator import EloComparator
from .pagerank_comparator import PageRankComparator
from .path_weight_comparator import PathWeightComparator
from .seed_comparator import SeedComparator
from .resistance_comparator import ResistanceComparator

COMPARATORS = [
    BradleyTerryComparator,
    EloComparator,
    PageRankComparator,
    PathWeightComparator,
    SeedComparator,
    ResistanceComparator,
]
