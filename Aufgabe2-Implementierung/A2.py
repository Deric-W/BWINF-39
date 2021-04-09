#!/usr/bin/python3

"""Lösung für Aufgabe2 des 39. BWINF"""

import sys
import argparse
from itertools import chain
from typing import TextIO, Iterator, Tuple, List, Dict, Set, Iterable

__version__ = "0.1"
__author__ = "Eric Wolf"
__email__ = "robo-eric@gmx.de"


argparser = argparse.ArgumentParser(
    description=__doc__
)
argparser.add_argument(
    "-v",
    "--version",
    help="zeige Versionsnummer",
    action="version",
    version=f"%(prog)s {__version__}"
)
argparser.add_argument(
    "-d",
    "--debug",
    help="zeige Kandidaten aller Früchte",
    action="store_true"
)
argparser.add_argument(
    "Datei",
    type=argparse.FileType("r"),
    help="Pfad zu einer Datei mit den erforderlichen Daten, beim Fehlen wird von Stdin gelesen",
    nargs="?",
    default=sys.stdin
)


class InvalidDataError(ValueError):
    """Fehler, welcher bei invaliden Daten ausgelöst wird"""
    __slots__ = ()


class MissingDataError(ValueError):
    """Fehler, welcher bei unvollständigen Daten ausgelöst wird"""
    __slots__ = ()


class Candidates(Dict[str, Set[int]]):  # Set hat eine effiziente Schnittmengenoperation
    """Repräsentation der Kandidaten"""
    __slots__ = ("all_candidates",)

    all_candidates: Set[int]

    def __init__(self, all_candidates: Set[int]) -> None:
        self.all_candidates = all_candidates

    def add_skewer(self, fruits: Iterable[str], bowls: Iterable[int]) -> None:
        """füge die Daten eines Spießes hinzu"""
        for fruit in fruits:
            try:
                current_candidates = self[fruit]
            except KeyError:
                self[fruit] = set(bowls)    # füge im Falle von fehlenden Kandidaten die eigenen Schüsseln hinzu
            else:
                current_candidates &= frozenset(bowls)  # entferne Kandidaten, die für den neuen Spieß nicht in frage kommen

    def add_skewers(self, skewers: Iterator[Tuple[Iterable[str], Iterable[int]]]) -> None:
        """füge die Daten mehrerer Spieße hinzu"""
        for fruits, bowls in skewers:
            self.add_skewer(fruits, bowls)

    def remove_impossible(self) -> None:
        """entferne unmögliche Kandidaten"""
        removed_candidate = True
        while removed_candidate:        # entferne unmögliche Kandidaten, bis keine weiteren mehr gibt
            removed_candidate = False   # im Falle eines Entfernes wird die Variable auf True gesetzt
            for fruit, bowls in filter(lambda item: len(item[1]) == 1, self.items()):
                # entferne alle Kandidaten, welche bereits eindeutig vergeben sind
                bowl = tuple(bowls)[0]
                # ignoriere beim Iterieren dich selbst
                for other_fruit, other_bowls in filter(lambda item: item[0] != fruit, self.items()):
                    if bowl in other_bowls:       # entferne unmöglichen Kandidaten
                        if len(other_bowls) < 2:  # andere Frucht ist auch eindeutig zugeordnet
                            raise InvalidDataError(
                                f"{fruit} und {other_fruit} werden beide eineindeutig Schüssel {bowl} zugeordnet"
                            )
                        other_bowls.remove(bowl)    # kann die Frucht eindeutig machen
                        removed_candidate = True

    def bowls(self, wanted: Iterable[str]) -> Set[int]:
        """gebe die Schüsseln einer Menge von Früchten zurück"""
        solution = set()
        # Kandidaten für alle Früchte welche nicht in Spießen vorkommen
        unknown_candidates = self.all_candidates - set(chain(*self.values()))   # alle Kandidaten - alle bereits vergebenen Kandidaten
        for fruit in wanted:
            try:
                solution |= self[fruit]     # füge die Kandidaten der Frucht der Lösung hinzu
            except KeyError:
                solution |= unknown_candidates  # füge die noch nicht vergeben Kandidaten der Lösung hinzu
        return solution


def parse_input(file: TextIO) -> Tuple[Set[int], List[str], Iterator[Tuple[List[str], List[int]]]]:
    """parse die bereitgestellte Datei und gebe alle Schüsseln, die Wunschsorten und alle Spieße mit Schüsseln zurück"""
    all_bowls = int(file.readline())    # Anzahl der Früchte
    wanted = file.readline().split()    # Wunschsorten
    return set(range(1, all_bowls + 1)), wanted, parse_skewers(file, int(file.readline()))


def parse_skewers(file: TextIO, skewers: int) -> Iterator[Tuple[List[str], List[int]]]:
    """parse die bereitgestellte Datei und gebe alle Spieße mit Schüsseln zurück"""
    for skewer in range(skewers):
        bowls = file.readline().split()     # Schüsseln eines Spießes, durch Leerzeichen getrennt
        fruits = file.readline().split()    # Früchte eines Spießes, durch Leerzeichen getrennt
        if len(bowls) != len(fruits):
            raise ValueError(
                f"Anzahl der Früchte und Schüsseln bei Spieß {skewer} stimmen nicht überein"
            )
        yield fruits, [int(bowl) for bowl in bowls]


if __name__ == "__main__":
    args = argparser.parse_args()
    all_bowls, wanted, skewers = parse_input(args.Datei)
    candidates = Candidates(all_bowls)
    candidates.add_skewers(skewers)
    candidates.remove_impossible()
    if args.debug:
        for fruit, bowls in candidates.items():
            print(f"{fruit}: {bowls}")
    solution = candidates.bowls(wanted)
    if len(solution) != len(wanted):    # Lösung enthält unerwünschte Früchte
        raise MissingDataError(
            f"es müssen mehr Schüsseln ({solution}) als gewünschte Früchte ({wanted}) besucht werden, "
            "es Fehlen weitere Daten"
        )
    print("Zu besuchende Schüsseln:", solution)
