#!/usr/bin/python3

"""Lösung für Aufgabe 3 des 39. BWINF Stufe 2"""

import sys
from argparse import ArgumentParser, FileType
from enum import Enum
from itertools import combinations
from typing import TextIO, Tuple, Iterator, Sequence, List


argparser = ArgumentParser(__doc__)
argparser.add_argument(
    "-l",
    "--lazy",
    help="brechne das Ermitteln von weiteren stabilen Standorten nach dem ersten ab",
    action="store_true"
)
argparser.add_argument(
    "-s",
    "--stalls",
    help="Anzahl an Eisbuden",
    type=int,
    default=3
)
argparser.add_argument(
    "Datei",
    help="Datei mit Daten des Dorfes (beim Fehlen wird von der Standarteingabe gelesen)",
    type=FileType("r"),
    nargs="?",
    default=sys.stdin
)


class VoteResult(Enum):
    """Ergebnis einer Wahl"""
    FAILED = 0
    APPROVED = 1


def parse_input(file: TextIO) -> Tuple[int, Iterator[int]]:
    """parse die als Datenstrom übergeben Daten"""
    adresses = int(file.readline().split()[0])
    houses = map(int, file.readline().split())
    return adresses, houses


class Village:
    __slots__ = ("adresses", "houses")

    adresses: int

    houses: List[int]

    def __init__(self, adresses: int, houses: List[int]) -> None:
        self.adresses = adresses
        self.houses = houses

    def distance(self, house: int, position: Sequence[int]) -> int:
        """ermittle die Distanz zur nächsten Eisbude"""
        distances = []
        for stall in position:
            distance1 = stall - house   # Distanz gegen den Uhrzeigersinn
            distance2 = abs(distance1 - self.adresses)   # Distanz im Uhrzeigersinn
            distances.append(distance1 if distance1 < distance2 else distance2)
        return min(distances)

    def simulate_vote(self, position1: Sequence[int], position2: Sequence[int]) -> VoteResult:
        """Simuliere eine Wahl zwischen zwei Positionen"""
        approved = 0    # Anzahl der Stimmen für position2
        for house in self.houses:
            if self.distance(house, position2) < self.distance(house, position1):
                approved += 1
        half = len(self.houses) / 2
        if approved > half:
            return VoteResult.APPROVED
        else:
            return VoteResult.FAILED

    def positions(self, stalls: int) -> Iterator[Tuple[int, ...]]:
        """ermittle alle möglichen Positionierungen der Buden"""
        return combinations(range(self.adresses), stalls)


if __name__ == "__main__":
    args = argparser.parse_args()
    adresses, houses = parse_input(args.Datei)
    village = Village(adresses, list(houses))
    positions = list(village.positions(args.stalls))
    better_positions = [0] * len(positions)
    for index1, position1 in enumerate(positions):
        for index2, position2 in enumerate(positions[index1 + 1:]):
            if village.simulate_vote(position1, position2) is VoteResult.APPROVED:
                better_positions[index1] += 1
            else:
                better_positions[index2] += 1
        if better_positions[index1] == 0:
            print("stabile Position:", position1)
            if args.lazy:
                break
