from pathlib import Path

import numpy as np
import pandas as pd


DATA_DIR = Path(__file__).parent
PLAYER_SOURCE = DATA_DIR / "player_stats.csv"
PLAYER_OUTPUT = DATA_DIR / "player_stats_curated.csv"
TEAM_OUTPUT = DATA_DIR / "team_stats_curated.csv"


def safe_divide(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    return numerator.div(denominator).replace([np.inf, -np.inf], np.nan)


def read_nhl_table(name: str) -> pd.DataFrame:
    frame = pd.read_csv(DATA_DIR / name, low_memory=False)
    frame.columns = frame.columns.str.strip()
    return frame.loc[frame["lgID"].astype("string").str.strip().eq("NHL")].copy()


def curate_player_stats() -> tuple[pd.DataFrame, pd.Series]:
    players = pd.read_csv(PLAYER_SOURCE, low_memory=False)
    players.columns = players.columns.str.strip()

    demographic_date_columns = {
        "birthYear", "birthMon", "birthDay",
        "deathYear", "deathMon", "deathDay",
    }
    columns_to_drop = [
        column for column in players.columns
        if column in demographic_date_columns or column.lower().endswith("city")
    ]
    players = players.drop(columns=columns_to_drop)
    if "pos" not in players.columns:
        raise KeyError("The player stats data must contain a 'pos' column.")

    stat_columns = [
        column for column in players.columns
        if column.startswith(("skater_", "goalie_"))
    ]
    players[stat_columns] = players[stat_columns].apply(pd.to_numeric, errors="coerce")
    players["year"] = pd.to_numeric(players["year"], errors="coerce")
    players["pos"] = players["pos"].astype("string").str.strip().str.upper()
    players["pos"] = players["pos"].replace("", pd.NA)

    goalie_rows = players["pos"].eq("G")
    known_position = players["pos"].notna()
    skater_rows = known_position & ~goalie_rows
    skater_columns = [column for column in players if column.startswith("skater_")]
    goalie_columns = [column for column in players if column.startswith("goalie_")]
    players.loc[goalie_rows | ~known_position, skater_columns] = np.nan
    players.loc[skater_rows | ~known_position, goalie_columns] = np.nan

    if "is_goalie" in players:
        players["is_goalie"] = pd.Series(pd.NA, index=players.index, dtype="boolean")
        players.loc[known_position, "is_goalie"] = goalie_rows.loc[known_position]

    for metric in ["G_PG", "A_PG", "SOG_PG", "PIM_PG", "PM_PG", "SH_Pct", "SER"]:
        players[metric] = np.nan

    for metric, numerator, denominator in [
        ("G_PG", "skater_G", "skater_GP"),
        ("A_PG", "skater_A", "skater_GP"),
        ("SOG_PG", "skater_SOG", "skater_GP"),
        ("PIM_PG", "skater_PIM", "skater_GP"),
        ("PM_PG", "skater_+/-", "skater_GP"),
        ("SH_Pct", "skater_G", "skater_SOG"),
    ]:
        players.loc[skater_rows, metric] = safe_divide(
            players.loc[skater_rows, numerator],
            players.loc[skater_rows, denominator],
        )
    players.loc[skater_rows, "SH_Pct"] *= 100
    players.loc[skater_rows, "SER"] = (
        players.loc[skater_rows, "G_PG"] * 2.0
        + players.loc[skater_rows, "A_PG"] * 1.7
        + players.loc[skater_rows, "SOG_PG"] * 0.5
        + players.loc[skater_rows, "PM_PG"] * 0.3
        - players.loc[skater_rows, "PIM_PG"] * 0.25
    )

    for metric in ["League_SV_Pct", "Goalie_SV_Pct", "GSAx_Total", "GSAx_PG"]:
        players[metric] = np.nan
    players.loc[goalie_rows, "Goalie_SV_Pct"] = 1 - safe_divide(
        players.loc[goalie_rows, "goalie_GA"],
        players.loc[goalie_rows, "goalie_SA"],
    )
    nhl_goalies = read_nhl_table("Goalies.csv")
    for column in ["GA", "SA"]:
        nhl_goalies[column] = pd.to_numeric(nhl_goalies[column], errors="coerce").fillna(0)
    nhl_goalies["year"] = pd.to_numeric(nhl_goalies["year"], errors="coerce")
    nhl_goalies = nhl_goalies.groupby(["playerID", "year"], as_index=False).agg(
        GA=("GA", "sum"), SA=("SA", "sum")
    )
    nhl_goalies["Goalie_SV_Pct"] = 1 - safe_divide(nhl_goalies["GA"], nhl_goalies["SA"])
    league_sv_pct = nhl_goalies.groupby("year")["Goalie_SV_Pct"].mean()
    players["League_SV_Pct"] = players["year"].map(league_sv_pct)
    players.loc[~goalie_rows, "League_SV_Pct"] = np.nan
    players.loc[goalie_rows, "GSAx_Total"] = players.loc[goalie_rows, "goalie_SA"] * (
        players.loc[goalie_rows, "Goalie_SV_Pct"]
        - players.loc[goalie_rows, "League_SV_Pct"]
    )
    players.loc[goalie_rows, "GSAx_PG"] = safe_divide(
        players.loc[goalie_rows, "GSAx_Total"],
        players.loc[goalie_rows, "goalie_GP"],
    )

    assert not any(
        column in demographic_date_columns or column.lower().endswith("city")
        for column in players.columns
    )
    assert players.loc[goalie_rows, skater_columns + ["SER"]].isna().all().all()
    assert players.loc[skater_rows, goalie_columns + ["Goalie_SV_Pct", "GSAx_Total", "GSAx_PG"]].isna().all().all()
    assert players.loc[~known_position, skater_columns + goalie_columns].isna().all().all()
    return players, league_sv_pct


def curate_team_stats(players: pd.DataFrame, league_sv_pct: pd.Series) -> pd.DataFrame:
    scoring = read_nhl_table("Scoring.csv")
    scoring_columns = ["GP", "G", "A", "PIM", "+/-", "SOG", "PostGP"]
    for column in scoring_columns:
        scoring[column] = pd.to_numeric(scoring[column], errors="coerce").fillna(0)
    scoring["year"] = pd.to_numeric(scoring["year"], errors="coerce")
    scoring["tmID"] = scoring["tmID"].astype("string").str.strip()
    scoring["pos"] = scoring["pos"].astype("string").str.strip().str.upper()

    skaters = scoring.groupby(
        ["playerID", "year", "tmID"], as_index=False
    ).agg(
        pos=("pos", "first"),
        GP=("GP", "sum"),
        G=("G", "sum"),
        A=("A", "sum"),
        PIM=("PIM", "sum"),
        PM=("+/-", "sum"),
        SOG=("SOG", "sum"),
        PostGP=("PostGP", "sum"),
    )
    for metric, numerator, denominator in [
        ("G_PG", "G", "GP"),
        ("A_PG", "A", "GP"),
        ("SOG_PG", "SOG", "GP"),
        ("PIM_PG", "PIM", "GP"),
        ("PM_PG", "PM", "GP"),
    ]:
        skaters[metric] = safe_divide(skaters[numerator], skaters[denominator])
    skaters["SER"] = (
        skaters["G_PG"] * 2.0
        + skaters["A_PG"] * 1.7
        + skaters["SOG_PG"] * 0.5
        + skaters["PM_PG"] * 0.3
        - skaters["PIM_PG"] * 0.25
    )

    def top_roster_average(positions: set[str], count: int, output_name: str) -> pd.Series:
        selected = skaters.loc[skaters["pos"].isin(positions)].sort_values(
            ["GP", "playerID"], ascending=[False, True]
        ).groupby(["tmID", "year"], sort=False).head(count)
        return selected.groupby(["tmID", "year"])["SER"].mean().rename(output_name)

    forward_ser = top_roster_average({"F", "C", "LW", "RW", "L", "R"}, 12, "Forward_SER_Avg")
    defense_ser = top_roster_average({"D"}, 6, "Defense_SER_Avg")

    goalies = read_nhl_table("Goalies.csv")
    for column in ["GP", "Min", "GA", "SA"]:
        goalies[column] = pd.to_numeric(goalies[column], errors="coerce").fillna(0)
    goalies["year"] = pd.to_numeric(goalies["year"], errors="coerce")
    goalies["tmID"] = goalies["tmID"].astype("string").str.strip()
    goalies = goalies.groupby(
        ["playerID", "year", "tmID"], as_index=False
    ).agg(GP=("GP", "sum"), Min=("Min", "sum"), GA=("GA", "sum"), SA=("SA", "sum"))
    goalies["Goalie_SV_Pct"] = 1 - safe_divide(goalies["GA"], goalies["SA"])
    goalies["League_SV_Pct"] = goalies["year"].map(league_sv_pct)
    goalies["GSAx_Total"] = goalies["SA"] * (
        goalies["Goalie_SV_Pct"] - goalies["League_SV_Pct"]
    )
    goalies["GSAx_PG"] = safe_divide(goalies["GSAx_Total"], goalies["GP"])
    starters = goalies.sort_values(
        ["Min", "playerID"], ascending=[False, True]
    ).groupby(["tmID", "year"], sort=False).head(1).set_index(["tmID", "year"])

    team_index = pd.MultiIndex.from_frame(
        pd.concat(
            [skaters[["tmID", "year"]], goalies[["tmID", "year"]]],
            ignore_index=True,
        ).drop_duplicates()
    )
    team_index.names = ["tmID", "year"]
    teams = pd.DataFrame(index=team_index)
    teams = teams.join(forward_ser).join(defense_ser)
    teams["Goalie_GSAx_PG"] = starters["GSAx_PG"]
    teams["Starting_Goalie_SV_Pct"] = starters["Goalie_SV_Pct"]

    team_shooting = skaters.groupby(["tmID", "year"])[["G", "SOG"]].sum()
    teams["Team_PDO"] = (
        safe_divide(team_shooting["G"], team_shooting["SOG"])
        + teams["Starting_Goalie_SV_Pct"]
    )

    skater_roster = skaters[["playerID", "year", "tmID", "GP", "PostGP"]].copy()
    goalie_roster = goalies[["playerID", "year", "tmID", "GP"]].copy()
    goalie_roster["PostGP"] = 0
    roster = pd.concat([skater_roster, goalie_roster], ignore_index=True)
    first_nhl = players[["playerID", "firstNHL"]].drop_duplicates("playerID").copy()
    first_nhl["firstNHL"] = pd.to_numeric(first_nhl["firstNHL"], errors="coerce")
    roster = roster.merge(first_nhl, on="playerID", how="left")
    roster["age_gp_weight"] = roster["GP"].where(roster["firstNHL"].notna(), 0)
    roster["weighted_experience"] = (
        (roster["year"] - roster["firstNHL"]) * roster["age_gp_weight"]
    )
    experience = roster.groupby(["tmID", "year"]).agg(
        Experience_Factor=("PostGP", "sum"),
        weighted_experience=("weighted_experience", "sum"),
        games_weight=("age_gp_weight", "sum"),
    )
    teams["Experience_Factor"] = experience["Experience_Factor"]
    teams["Age_Index"] = safe_divide(
        experience["weighted_experience"], experience["games_weight"]
    )

    output_columns = [
        "Forward_SER_Avg", "Defense_SER_Avg", "Goalie_GSAx_PG",
        "Team_PDO", "Experience_Factor", "Age_Index",
    ]
    return teams.reset_index().sort_values(["year", "tmID"])[
        ["tmID", "year"] + output_columns
    ]


if __name__ == "__main__":
    player_stats, league_save_pct = curate_player_stats()
    team_stats = curate_team_stats(player_stats, league_save_pct)
    player_stats.to_csv(PLAYER_OUTPUT, index=False)
    team_stats.to_csv(TEAM_OUTPUT, index=False)
    print(f"Player-season rows: {len(player_stats):,}")
    print(f"Team-season rows: {len(team_stats):,}")
    print(f"Player output: {PLAYER_OUTPUT}")
    print(f"Team output: {TEAM_OUTPUT}")
