#!/usr/bin/python3

"""Lösung für Aufgabe2 des 39. BWINF"""

from __future__ import annotations
import sys
import argparse
from itertools import chain
from typing import TextIO, Iterator, Tuple, List, Dict, Set, Iterable, TypeVar, MutableSequence, MutableMapping, Mapping

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

T = TypeVar("T")


class InvalidDataError(ValueError):
    """Fehler, welcher bei invaliden Daten ausgelöst wird"""
    __slots__ = ()


class MissingDataError(ValueError):
    """Fehler, welcher bei unvollständigen Daten ausgelöst wird"""
    __slots__ = ()


def iter_possible(candidates: MutableSequence[Tuple[str, Set[int]]], used: MutableMapping[str, int]) -> Iterator[Mapping[str, int]]:
    """Funktion, welche rekursiv für eine Menge an Früchten mit Kandidaten mögliche Zuordnungen findet"""
    # WARNUNG: die zurückgegebenen Zuordnungen stellen ein "Schnappschuss" des Mapping welches als 'used' übergeben wird dar.
    #          Dies bedeutet, dass diese beim weiteriterieren verändert werden können.
    #          Aus diesem Grund sollten die zurückgegebenen Mappings unverzüglich verwendet oder kopiert werden.
    try:
        fruit, bowls = candidates.pop()    # entferne noch nicht vergebe Frucht, sie wird zugeordnet
    except IndexError:
        yield used                          # alle Früchte vergeben, die aktuelle Kombination aus Früchten und Schüsseln ist möglich
    else:
        for bowl in filter(lambda x: x not in used.values(), bowls):    # als Kandidaten kommen alle freien Schüsseln in Betracht
            used[fruit] = bowl                                          # weise der Frucht ein Kandidat zu
            yield from iter_possible(candidates, used)                  # gebe alle Kombinationen zurück, welche mit dieser Zuordnung möglich sind
            used.pop(fruit)                                             # entferne den Kandidaten wieder für den nächsten Durchlauf
        candidates.append((fruit, bowls))    # füge die eigene Frucht wieder hinzu für den nächsten rekursiven Aufruf


class Candidates(Dict[str, Set[int]]):  # Set besitzt eine effiziente Schnittmengenoperation
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

    def add_unknown_fruits(self, fruits: Iterable[str]) -> None:
        """füge eine Menge an Früchten hinzu, welche nicht in den Spießen vorkommen könnten"""
        # Kandidaten für alle Früchte welche nicht in Spießen vorkommen
        unknown_candidates = self.all_candidates - set(chain.from_iterable(self.values()))   # alle Kandidaten - alle bereits vergebenen Kandidaten
        for fruit in fruits:
            if fruit not in self:   # Frucht kommt nicht in Tabelle vor
                self[fruit] = unknown_candidates.copy()     # könnte modifiziert werden, kopiere

    def strip_impossible(self) -> Candidates:
        """gebe nur die Kandidaten zurück, für welche eine Zuordnung aller Früchte zu Schüsseln funktionieren würde"""
        possible = Candidates(self.all_candidates)      # Untermenge von self welche nur mögliche Kandidaten enthält (momentan 0)
        candidates = list(self.items())
        candidates.sort(key=lambda item: len(item[1]), reverse=True)    # sorge für eine möglicherweise kürzere Laufzeit
        for combination in iter_possible(candidates, {}):   # befülle die möglichen kandidaten
            for fruit, bowl in combination.items():     # füge die zugeordnete Schüssel jeder Frucht deren möglichen Kandidaten hinzu
                try:
                    possible[fruit].add(bowl)
                except KeyError:
                    possible[fruit] = {bowl}
        if len(possible) == 0:  # es gibt keine mögliche Zuordnungen, Fehler
            raise InvalidDataError("Es gibt keine möglichen Zuordnungen von Früchten und Schüsseln, Daten fehlerhaft")
        return possible

    def bowls(self, wanted: Iterable[str]) -> Set[int]:
        """gebe die Schüsseln einer Menge von Früchten zurück"""
        solution = set()
        for fruit in wanted:
            solution |= self[fruit]     # füge die Kandidaten der Frucht der Lösung hinzu
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
    candidates.add_unknown_fruits(wanted)
    possible_candidates = candidates.strip_impossible()
    if args.debug:
        print("Kandidaten:")
        for fruit, bowls in candidates.items():
            print(f"{fruit}: {bowls}")
        print("mögliche Kandidaten:")
        for fruit, bowls in possible_candidates.items():
            print(f"{fruit}: {bowls}")
    solution = possible_candidates.bowls(wanted)
    if len(solution) != len(wanted):    # Lösung enthält unerwünschte Früchte
        raise MissingDataError(
            f"es müssen mehr Schüsseln ({solution}) als gewünschte Früchte ({wanted}) besucht werden, "
            "es fehlen weitere Daten"
        )
    print("Zu besuchende Schüsseln:", solution)
