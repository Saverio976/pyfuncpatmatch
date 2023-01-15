from typing import Any, Dict, List, Tuple, Union

from pyfuncpatmatch.pat_match_types import (PatEqMatch, PatGtEqMatch,
                                            PatGtMatch, PatListExtract,
                                            PatLtEqMatch, PatLtMatch,
                                            PatMatchAll)

PatternMatch = Union[
    Any,
    PatListExtract,
    PatEqMatch,
    PatMatchAll,
    PatGtMatch,
    PatGtEqMatch,
    PatLtMatch,
    PatLtEqMatch,
]
LArgsPatternMatch = Union[List[PatternMatch], Tuple[PatternMatch], PatMatchAll]
LArgsPatternEqMatch = Union[List[PatEqMatch], Tuple[PatEqMatch]]
LArgsPatternExtractMatch = Union[List[PatListExtract], Tuple[PatListExtract]]
KArgsPatternMatch = Dict[str, PatternMatch]
