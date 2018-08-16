# This source code is part of the Biotite package and is distributed
# under the 3-Clause BSD License. Please see 'LICENSE.rst' for further
# information.

from typing import (
    Dict,
    Tuple,
    Union,
    Optional,
    Iterable,
    Iterator,
    List,
    Container,
    overload,
    Hashable
)
from typing import Sequence as _Sequence
from enum import IntEnum
from .sequence import Sequence


class Location:
    class Defect(IntEnum):
        NONE         = 0
        MISS_LEFT    = 1
        MISS_RIGHT   = 2
        BEYOND_LEFT  = 4
        BEYOND_RIGHT = 8
        UNK_LOC      = 16
        BETWEEN      = 32

    class Strand(IntEnum):
        FORWARD = 1
        REVERSE = -1
    
    first: int
    last: int
    strand: Strand
    defect: Defect
    def __init__(
        self, first: int, last: int,
        strand: Strand = Strand.FORWARD, defect: Defect = Defect.NONE
    ) -> None:
    def __str__(self) -> str: ...
    def __eq__(self, item: object) -> bool: ...


class Feature:
    key: str
    locs: List[Location]
    qual: Dict[str, str]
    def __init__(
        self, key: str, locs: Iterable[Location], qual: Dict[str, str] = {}
    ) -> None: ...
    def __eq__(self, item: object) -> bool: ...


class Annotation(Iterable[Feature], Container):
    def __init__(self, features: Optional[Iterable[Feature]] = None) -> None: ...
    def get_features(self) -> List[Feature]: ...
    def add_feature(self, feature: Feature) -> None: ...
    def get_location_range(self) -> Tuple[int, int]: ...
    def del_feature(self, feature: Feature) -> None: ...
    def __add__(self, item: Union[Annotation, Feature]) -> Annotation: ...
    def __getitem__(self, index: slice) -> Annotation: ...
    def __delitem__(self, item: Feature) -> None: ...
    def __iter__(self) -> Iterator[Feature]: ...
    def __contains__(self, item: object) -> bool:
    def __eq__(self, item: object) -> bool:


class AnnotatedSequence:
    sequence: Sequence
    annotation: Annotation
    def __init__(
        self,
        annotation: Annotation,
        sequence: Sequence,
        sequence_start: int = 1
    ) -> None: ...
    @overload
    def __getitem__(self, index: slice) -> AnnotatedSequence: ...
    @overload
    def __getitem__(self, index: Feature) -> Sequence: ...
    @overload
    def __getitem__(self, index: int) -> Hashable: ...
    @overload
    def __setitem__(self, index: slice, item: Sequence) -> None: ...
    @overload
    def __setitem__(self, index: Feature, item: Sequence) -> None: ...
    @overload
    def __setitem__(self, index: int, item: Hashable) -> None: ...
    def __eq__(self, item: object) -> bool: