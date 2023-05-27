import os
from collections import defaultdict
from typing import List

import matplotlib.pyplot as plt
from dotenv import load_dotenv
from solana.rpc.api import Client
from tabulate import tabulate

from decalls_idl.accounts import UserStats
from decalls_idl.program_id import PROGRAM_ID

LAMPORT_PER_SOL = 1000000000
GAMES_LIMIT = 30
SECONDS_TO_HOURS = 1 / 3600


def leaderboard(user_statistics: List[UserStats]):
    """
    Prints the leaderboard data for the provided user statistics.

    Args:
        user_statistics: A list of UserStats objects.
    """
    table_data = [
        [
            user.owner,
            user.total_games,
            round((winnings := round(user.total_winnings / LAMPORT_PER_SOL, 2))
                  / (spent := round(user.total_prediction_funds / LAMPORT_PER_SOL, 2)), 2),
            winnings - spent,
            spent
        ]
        for user in user_statistics
    ]

    table_data.sort(key=lambda row: row[1], reverse=True)

    total_volume = sum(row[4] for row in table_data)

    print(f'\n        Players: {len(user_statistics)} Volume: {total_volume} Fees: {total_volume * 0.025}\n')
    print(tabulate(table_data, headers=['Owner', 'Total Games', 'Ratio', 'Result', 'Volume'], showindex="always"))


def get_user_statistic(client: Client) -> List[UserStats]:
    """Fetches user statistics from the Solana client.

    Args:
        client: The Solana client.

    Returns:
        A list of UserStats objects.
    """
    user_statistics = []

    response = client.get_program_accounts(PROGRAM_ID)

    for account_data in response.value:
        data: bytes = account_data.account.data
        match data[0]:
            case 0xb0:
                user_statistics.append(UserStats.decode(data))
            case _:
                continue
    return user_statistics


def games_per_user_subplot(ax, user_statistics: List[UserStats]):
    """Creates a subplot of games per user.

    Args:
        ax: The Axes object to draw on.
        user_statistics: A list of UserStats objects.
    """
    chart_data = defaultdict(int)
    n_users = len(user_statistics)
    for info in user_statistics:
        if info.total_games <= GAMES_LIMIT:
            chart_data[info.total_games] += 1 / n_users * 100

    ax.bar(chart_data.keys(), chart_data.values(), color='skyblue', edgecolor='darkblue', width=1)
    ax.set_title('DeCalls users info (graph cut on 30 games played)')
    ax.set_xlabel('Games played')
    ax.set_ylabel('Percentage of players')


def unique_users_subplot(ax, user_statistics: List[UserStats]):
    """Creates a subplot of unique users over time.

    Args:
        ax: The Axes object to draw on.
        user_statistics: A list of UserStats objects.
    """
    user_statistics = sorted(user_statistics, key=lambda x: x.created_at)[3:]
    all_time_start = user_statistics[0].created_at
    times = [(u.created_at - all_time_start + 1) * SECONDS_TO_HOURS for u in user_statistics]
    ax.plot(times, range(1, len(user_statistics) + 1))
    ax.set_xlabel('Time (hours)')
    ax.set_ylabel('Number of Users')
    ax.set_title('Unique users over time')


def combined_graph(user_statistics: List[UserStats]):
    """Creates a combined graph of the two subplots.

    Args:
        user_statistics: A list of UserStats objects.
    """
    fig, axs = plt.subplots(1, 2, figsize=(15, 5))

    games_per_user_subplot(axs[0], user_statistics)
    unique_users_subplot(axs[1], user_statistics)

    plt.tight_layout()
    plt.show()


load_dotenv()

solana_endpoint: str = os.getenv('RPC_NODE', 'https://api.mainnet-beta.solana.com')

solana_client: Client = Client(solana_endpoint)

user_stats = get_user_statistic(solana_client)

leaderboard(user_stats)

combined_graph(user_stats)
