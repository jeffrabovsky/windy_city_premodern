import csv
from dataclasses import dataclass
from datetime import date
import IPython
from typing import Any, Iterable
from enum import Enum, auto


@dataclass(frozen=True)
class MatchResult:
    date: date
    player_1: str
    player_2: str
    player_1_wins: int
    player_2_wins: int
    player_1_deck: str
    player_2_deck: str
    round_number: int | None

    @classmethod
    def from_dict(
        cls: type[MatchResult],
        row_dict: dict[str, Any],
    ) -> MatchResult:
        parsed_date = date.strptime(row_dict["date"], "%m/%d/%y")
        player_1_wins = int(row_dict["player_1_wins"])
        player_2_wins = int(row_dict["player_2_wins"])
        round_number = int(row_dict["round_number"]) if row_dict["round_number"] else None

        return MatchResult(**{
            **row_dict,
            "date": parsed_date,
            "player_1_wins": player_1_wins,
            "player_2_wins": player_2_wins,
            "round_number": round_number,
        })


@dataclass(frozen=True)
class DeckMatchups:
    deck: str
    matchups: list[Matchup]

    @property
    def total_wins(self) -> int:
        wins = 0

        for matchup in self.matchups:
            wins += matchup.wins
        
        return wins

    @property
    def total_losses(self) -> int:
        losses = 0

        for matchup in self.matchups:
            losses += matchup.losses
        
        return losses
    
    @property
    def total_matches(self) -> int:
        return self.total_wins + self.total_losses
    
    @property
    def win_percentage(self) -> float | None:
        if self.total_matches == 0:
            return None

        return float(self.total_wins) / float(self.total_matches) * 100


@dataclass(frozen=True)
class Matchup:
    other_deck: str
    wins: int
    losses: int

""" reveal_type(
[
    ("UG Gro", [
        ("Red Deck", 2, 0)
    ])
]
) """

def match_winner(result: MatchResult) -> str | None:
    if result.player_1_wins > result.player_2_wins:
        return result.player_1_deck

    if result.player_2_wins > result.player_1_wins:
        return result.player_2_deck
    
    return None


def matchups_for_deck_pair(
    deck: str,
    other_deck: str,
    match_results: list[MatchResult]
) -> Matchup:
    relevant_results = [
        match_result for match_result in match_results
        if {match_result.player_1_deck, match_result.player_2_deck} == {deck, other_deck}
    ]

    match_wins = 0
    match_losses = 0

    for result in relevant_results:
        winner = match_winner(result)
        if winner == deck:
            match_wins += 1
        elif winner == other_deck:
            match_losses += 1

    return Matchup(
        other_deck,
        match_wins,
        match_losses,
    )


def results_to_matchups(match_results: list[MatchResult]) -> list[DeckMatchups]:
    deck_names = {match_result.player_1_deck for match_result in match_results}.union(
        {match_result.player_2_deck for match_result in match_results}
    )
    deck_names.remove("")  # Bye's deck is empty string

    deck_matchups = []
    for deck in deck_names:
        matchups = []
        for other_deck in deck_names:
            if deck != other_deck:
                matchups.append(matchups_for_deck_pair(deck, other_deck, match_results))
        deck_matchups.append(DeckMatchups(deck=deck, matchups=matchups))

    return deck_matchups


def row_to_html(row: list[str]) -> str:
    html = "<tr>\n"
    for td in row:
        html += f"<td>{td}</td>\n"
    html += "</tr>\n"
    return html
        

def html_table(deck_matchups: list[DeckMatchups]) -> str:
    archtypes = sorted([deck_matchup.deck for deck_matchup in deck_matchups])

    rows = []
    for archtype in archtypes:
        matchups = [matchup for matchup in deck_matchups if matchup.deck == archtype][0]
        row = [f"{archtype} ({matchups.total_wins} - {matchups.total_losses})"]
        for other_archtype in archtypes:
            if other_archtype == archtype:
                row.append("")
            else:
                matchup = [matchup for matchup in matchups.matchups if matchup.other_deck == other_archtype][0]
                row.append(f"{matchup.wins} - {matchup.losses}")
        rows.append(row)

    return f"""
    <figure>
        <table>
        <thead>
            <tr>
                <th>Archetype</th>
                {"\n                ".join(["<th>{}</th>".format(archtype) for archtype in archtypes])}
            </tr>
        </thead>
    <tbody>
        {"\n".join([row_to_html(row) for row in rows])}
    </tbody>
    </table>
    </figure>
    """



def main() -> None:
    with open('matches.csv', 'r') as file:
        reader = csv.DictReader(file)
        match_results = [
            MatchResult.from_dict(row) for row in reader
        ]
    matchups = results_to_matchups(match_results)
    # import IPython; IPython.embed()
    print(html_table(matchups))

if __name__ == "__main__":
    main()
