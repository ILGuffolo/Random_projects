'''
set of small programs to help me optimize blackjack

'''
import matplotlib.pyplot as plt
from collections import Counter
import functools

def average_pull(size):
    deck = list(range(1, 11))
    total = sum(size)

    probabilities = [s / total for s in size]
    expected = sum(d * p for d, p in zip(deck, probabilities))

    return deck, expected, probabilities

def print_probs(values, expected, probs):
    fig, ax = plt.subplots(figsize=(8,5))

    ax.bar(values, probs)
    ax.axvline(expected, color='red', linestyle='--',
               label=f'Expected = {expected:.2f}')

    ax.set_xticks(values)
    ax.set_xlabel("Card Value")
    ax.set_ylabel("Probability")
    ax.legend()
    plt.show()


DEFAULT_DECK = {
    1: 4,
    2: 4,
    3: 4,
    4: 4,
    5: 4,
    6: 4,
    7: 4,
    8: 4,
    9: 4,
    10: 16
}


def hand_value(hand):
    """
    Blackjack hand evaluator.
    Ace counts as 11 when possible, otherwise 1.
    """

    total = 0
    aces = 0

    for c in hand:
        if c == 1:
            total += 11
            aces += 1
        else:
            total += c

    while total > 21 and aces:
        total -= 10
        aces -= 1

    return total


def remove_cards(deck, cards):

    for c in cards:
        if c in deck and deck[c] > 0:
            deck[c] -= 1

    return deck


# ==========================================================
# Dealer simulation
# Change dealer rules here if needed
# ==========================================================

def dealer_probability(hand, deck):

    value = hand_value(hand)

    # Dealer stands on 17
    if value >= 17:
        return Counter({value if value <= 21 else "Bust": 1})


    total_cards = sum(deck.values())

    result = Counter()


    for card, amount in deck.items():

        if amount <= 0:
            continue

        new_deck = deck.copy()
        new_deck[card] -= 1

        child_result = dealer_probability(
            hand + [card],
            new_deck
        )

        probability = amount / total_cards

        for outcome, chance in child_result.items():
            result[outcome] += chance * probability

    return result



def analyze_hand(
        my_hand,
        dealer_upcard=None,
        other_players=None):


    deck = DEFAULT_DECK.copy()


    # remove your cards
    deck = remove_cards(deck, my_hand)


    # remove dealer visible card
    if dealer_upcard:
        deck = remove_cards(deck, [dealer_upcard])


    # remove other players cards
    if other_players:
        deck = remove_cards(deck, other_players)



    remaining = sum(deck.values())

    current = hand_value(my_hand)


    # -----------------------------
    # Player next card analysis
    # -----------------------------

    distribution = Counter()
    card_prob = {}

    bust = 0
    expected_draw = 0
    blackjack = 0


    for card, amount in deck.items():

        if amount <= 0:
            continue


        p = amount / remaining

        card_prob[card] = p

        expected_draw += card * p


        new_value = hand_value(my_hand + [card])
        if new_value == 21:
            blackjack += p


        if new_value > 21:
            bust += p
            distribution["Bust"] += p

        else:
            distribution[new_value] += p



    stats = {

        "current": current,
        
        "dealer": dealer_upcard,

        "cards_left": remaining,

        "expected_draw": expected_draw,

        "expected_total": current + expected_draw,

        "bust": bust,
        
        "blackjack": blackjack,

        "safe": 1-bust,

        "card_prob": card_prob,

        "distribution": dict(distribution),

        "deck": deck,

    }



    # -----------------------------
    # Dealer statistics
    # -----------------------------

    if dealer_upcard:

        dealer = dealer_probability(
            [dealer_upcard],
            deck.copy()
        )


        stats["dealer_distribution"] = dict(dealer)

        stats["dealer_bust"] = dealer["Bust"]

        stats["dealer_expected"] = sum(
            k*v for k,v in dealer.items()
            if k != "Bust"
        )

    else:

        stats["dealer_distribution"] = None



    # =====================================================
    # PLAYER STRATEGY
    #
    # MODIFY THIS SECTION TO CREATE YOUR OWN STRATEGY
    # =====================================================

    if current >= 17:
        stats["recommendation"] = "Stand"

    elif bust < 0.30:
        stats["recommendation"] = "Hit"

    else:
        stats["recommendation"] = "Consider"


    return stats

def blackjack_dashboard(stats):

    fig = plt.figure(figsize=(12,7))

    gs = fig.add_gridspec(2,2)

    ax1 = fig.add_subplot(gs[:,0])
    ax2 = fig.add_subplot(gs[0,1])
    ax3 = fig.add_subplot(gs[1,1])

    # ---------------- Card probabilities -----------------

    ax1.bar(stats["card_prob"].keys(),
            stats["card_prob"].values(),
            color="steelblue")

    ax1.set_title("Remaining deck")
    ax1.set_xlabel("Card")
    ax1.set_ylabel("Probability")

    # ---------------- Result distribution ----------------

    labels = list(stats["distribution"].keys())
    values = list(stats["distribution"].values())

    colors = [
        "crimson" if l=="Bust" else "seagreen"
        for l in labels
    ]

    ax2.bar(range(len(labels)), values, color=colors)

    ax2.set_xticks(range(len(labels)))
    ax2.set_xticklabels(labels)

    ax2.set_ylabel("Probability")
    ax2.set_title("After one hit")

    # ---------------- Dashboard text ----------------

    ax3.axis("off")

    text = f"""
Current hand      : {stats['current']}

Expected draw / total     : {stats['expected_draw']:.2f} / {stats['expected_total']:.2f}

Safe hit / 21             : {stats['safe']:.1%} / {stats['blackjack']:.1%}

Bust                      : {stats['bust']:.1%}

Dealer bust               : {stats['dealer_bust']:.1%}

Dealer expected           : {stats['dealer_expected']:.2f}

- Recommendation          : {stats['recommendation']}
"""

    ax3.text(
        0,
        1,
        text,
        fontsize=13,
        family="monospace",
        va="top"
    )

    plt.tight_layout()
    plt.show()

# ________________ MAIN _____________________#

stats = analyze_hand(
    my_hand=[5,4,1],
    dealer_upcard=10,
    other_players=[]
)

blackjack_dashboard(stats)


