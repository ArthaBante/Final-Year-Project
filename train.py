import json
import re
import pandas as pd
import random


class CoinGame:

    def __init__(self, player):
        self.player = player
        self.coins_earned = 0
        self.target_coins = 100

    def play(self):
        print(f"\n=== COIN GAME ===")
        print(
            f"Choose 1 for 1 coin or 2 to choose randomly from 0, 1, or 2 coins. First to {self.target_coins} wins!\nType exit to leave the game\n")

        while self.coins_earned < self.target_coins:
            self.display_status()
            result = self.handle_turn()
            if result == 'exit':
                # Add earned coins to player's total before exiting
                self.player["coins"] += self.coins_earned
                print(f"Total coins now: {self.player['coins']}")
                input("\nPress Enter to continue...")
                return  # Exit the game early

        self.award_winnings()

    def display_status(self):

        print(f"Coins Earned: {self.coins_earned}/{self.target_coins} coins")

    def handle_turn(self):
        global coins_won
        try:
            user_input = input("Enter choice 1 or 2 (or 'exit' to quit): ")

            # Check for exit command
            if user_input.lower() == 'exit':
                print("\nThanks for playing! Come back anytime.")
                return 'exit'  # This will terminate the program

            choice = int(user_input)
            if choice not in [1, 2]:
                print("Invalid choice. Please choose 1 or 2.")
                return

            if choice == 1:
                coins_won = 1
                print(f"You earned {coins_won} coin!")
            elif choice == 2:  # choice == 2
                coins_won = random.randint(0, 2)  # Randomly gives 0, 1, or 2 coins
                print(f"You rolled: {coins_won} coins!")

            self.coins_earned += coins_won
        except ValueError:
            print("Enter a valid number (1 or 2).")

    def award_winnings(self):

        self.player["coins"] += self.coins_earned
        print(f"\nYou won {self.coins_earned} coins! Total now: {self.player['coins']}")



class SentimentAnalyzer:
    def __init__(self, emotion_words_path, modifier_words_path):
        self.lexicon = self.load_data(emotion_words_path)
        self.modifiers, self.negations = self.load_modifier_words(modifier_words_path)

    def load_data(self, path):
        df = pd.read_csv(path, encoding='latin1')
        return dict(zip(df['word'], df['sentiment']))

    def load_modifier_words(self, path):
        modifiers = {}
        negations = set()
        df = pd.read_csv(path, encoding='latin1')

        for _, row in df.iterrows():
            if row['weight'] > 0:
                modifiers[row['word']] = row['weight']
            else:
                negations.add(row['word'])
        return modifiers, negations

    def _preprocess(self, text):
        text = text.lower()
        return re.findall(r"\w+(?:'\w+)?", text)

    def analyze(self, text):
        words = self._preprocess(text)
        if not words:
            return 0.0, "neutral"

        pos, neg = 0, 0
        current_weight = 1

        for word in words:
            sentiment = self.lexicon.get(word)

            if sentiment == "positive":
                pos += current_weight
                current_weight = 1
            elif sentiment == "negative":
                neg += current_weight
                current_weight = 1
            elif word in self.modifiers:
                current_weight *= self.modifiers[word]
            elif word in self.negations:
                current_weight *= -1

        score = (pos - neg) / len(words)
        sentiment = "positive" if score > 0.1 else "negative" if score < -0.1 else "neutral"
        return score, sentiment


# Initialize sentiment analyzer
analyzer = SentimentAnalyzer(
    emotion_words_path=r"C:\Users\Dell\OneDrive - University of Hertfordshire\Lexicon Based Approach\Bing.csv",
    modifier_words_path=r"C:\Users\Dell\OneDrive - University of Hertfordshire\Lexicon Based Approach\Afinn.csv"
)


SHOPKEEPER_DATA_PATH = r"C:\Users\Dell\OneDrive - University of Hertfordshire\Lexicon Based Approach\shopkeeper_data.json"

def load_shop_items(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)["items"]

def load_shopkeeper_data():
    with open(SHOPKEEPER_DATA_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


SHOPKEEPER_DIALOGUE = load_shopkeeper_data()
shop_items = load_shop_items(r'C:\Users\Dell\OneDrive - University of Hertfordshire\Lexicon Based Approach\shop_items.json')


def shop(player):
    print("\n=== FRIENDLY SHOPKEEPER ===")

    if player.get('shopkeeper_rejected', False):
        for line in SHOPKEEPER_DIALOGUE["revisit_dialogue"]:
            print(f"Shopkeeper: {line}")

        # Simple shop for returning players
        print("\nAvailable items:")
        for item, data in shop_items.items():
            print(f"{item.title():<8} - {data['cost']} coins\t{data['description']}")

        while True:
            print(f"\nYour coins: {player['coins']}")
            choice = input("\nBuy something or 'leave': ").lower()

            if choice == 'leave':
                print(f"\nShopkeeper: {SHOPKEEPER_DIALOGUE['shopkeeper_end']['no_gift']}")
                input("\nPress Enter to continue...")
                return

            if choice in shop_items:
                item = shop_items[choice]
                if player['coins'] >= item['cost']:
                    player['coins'] -= item['cost']
                    print(f"\nShopkeeper: Thank you for the {choice}! Now, let's chat properly.")
                    break
                else:
                    print("\nShopkeeper: You don't have enough coins for that.")
            else:
                print("\nShopkeeper: I don't have that item.")

    # Conversation section
    for line in SHOPKEEPER_DIALOGUE["conversation_intro"]:
        print(f"Shopkeeper: {line.format(name=player['name'])}")

    positive_responses = 0
    for i, question in enumerate(SHOPKEEPER_DIALOGUE['questions'], 1):
        print(f"\nShopkeeper ({i}/5): {question.format(name=player['name'])}")
        response = input("Your response: ")
        score, sentiment = analyzer.analyze(response)

        print(f"[Your response was {sentiment} (score: {score:.2f})]")

        if sentiment == "positive":
            positive_responses += 1
            print("Shopkeeper: That makes me happy!")
        elif sentiment == "negative":
            print("Shopkeeper: Oh, that's unfortunate...")
        else:
            print("Shopkeeper: I see...")

    # Discounted item logic
    discounted_price = {
        item: {
            'cost': data['cost'] // 2,
            'description': data['description']
        }
        for item, data in shop_items.items()
    }

    if positive_responses >= 3:
        mood = 'returning' if player.get('shopkeeper_rejected', False) else 'new'
        print(f"\nShopkeeper: {SHOPKEEPER_DIALOGUE['discount_offer'][mood].format(name=player['name'])}")

        if input("(y/n): ").lower() == 'y':
            print("\nAvailable items:")
            for item, data in discounted_price.items():
                print(f"{item.title():<8} - {data['cost']} coins\t{data['description']}")

            while True:
                print(f"\nYour coins: {player['coins']}")
                choice = input("\nBuy something or 'leave': ").lower()

                if choice == 'leave':
                    if input(f"\n{SHOPKEEPER_DIALOGUE['gift_offer' ]['ask'].format(name=player['name'])} (y/n): ").lower() == "y":
                        print(SHOPKEEPER_DIALOGUE["gift_offer"]["confirm"].format(name=player['name']))
                        player['inventory'].append('gem')
                    else:
                        print(SHOPKEEPER_DIALOGUE["shopkeeper_end"]["no_gift"])
                    input("\nPress Enter to continue...")
                    return

                if choice in discounted_price:
                    item = discounted_price[choice]
                    if player['coins'] >= item['cost']:
                        player['coins'] -= item['cost']
                        print(f"\nShopkeeper: Thank you for the {choice}!")
                        print("Also, I have something for you, which can help you to win the game")

                        if input("\nDo you want the Gem? (y/n): ").lower() == "y":
                            print(SHOPKEEPER_DIALOGUE["gift_offer"]["confirm"])
                            player['inventory'].append('gem')
                        else:
                            print(SHOPKEEPER_DIALOGUE["shopkeeper_end"]["no_gift"])
                        input("\nPress Enter to continue...")
                        return
                    else:
                        print("\nShopkeeper: You don't have enough coins for that.")
                else:
                    print("\nShopkeeper: I don't have that item.")
        else:
            print("That's fine. But I do have something for you...")
            if input("\nDo you want the Gem? (y/n): ").lower() == "y":
                print(SHOPKEEPER_DIALOGUE["gift_offer"]["confirm"])
                player['inventory'].append('gem')
            else:
                print(SHOPKEEPER_DIALOGUE["shopkeeper_end"]["no_gift"])
            input("\nPress Enter to continue...")
            return
    else:
        print(f"\n{SHOPKEEPER_DIALOGUE['shopkeeper_end']['rejected']}")
        player['shopkeeper_rejected'] = True


def move_player(position, direction):
    """Handles player movement with boundaries"""
    x, y = position
    if direction == "up" and y < 3:
        return (x, y + 1)
    elif direction == "down" and y > 0:
        return (x, y - 1)
    elif direction == "left" and x > 0:
        return (x - 1, y)
    elif direction == "right" and x < 3:
        return (x + 1, y)
    return position  # Invalid move


def display_grid(position):
    """Displays a 4x4 grid with player position"""

    for y in range(3, -1, -1):
        row = []
        for x in range(4):
            if (x, y) == position:
                row.append("[P]")
            elif (x, y) == (1, 1):
                row.append("[G]")  # Game location
            elif (x, y) == (2, 2):
                row.append("[S]")  # Shop location
            elif (x, y) == (3, 3):
                row.append("[W]")  # Wizard location
            else:
                row.append("[ ]")
        print(" ".join(row))


def main():
    Player_name = input("Enter your name Adventurer: ")
    player = {"name": Player_name, "coins": 0, "inventory": []}
    position = (0, 0)

    print(
        f"Welcome to the Game {Player_name}, where your emotions decide which way you will take. \nThe Long way or the Shortcut \nEither earn 100 coins (long way), or be nice and get the Gem (shortcut)")
    print("**********")
    print("Move with: up/down/left/right. \nQuit with 'quit'.")
    print("**********")
    print("Locations: [G] = Game, [S] = Shop, [W] = Wizard, [P] = You\n")


    while True:
        display_grid(position)
        print(f"Coins: {player['coins']}")
        print("Inventory:", ', '.join(player['inventory']) or "Empty")

        cmd = input("\nMove: ").lower()
        if cmd == "quit":
            break

        new_pos = move_player(position, cmd)
        if new_pos == position:
            print("Can't move that way!")
            continue
        position = new_pos

        # Location triggers
        if position == (1, 1):
            print("\nYou found the Coin Game!")
            if input("Play? (y/n): ").lower() == 'y':
                game = CoinGame(player)
                game.play()

        elif position == (2, 2):
            print("\nYou meet a friendly shopkeeper!")
            shop(player)

        elif position == (3, 3):
            if 'gem' in player['inventory']:
                print("\nWizard: Ah! You brought me the gem!")
                print("Wizard: You've proven yourself worthy. You win the game!")
                return
            else:
                print("\nWizard: Come back when you have something interesting for me...")

    print("\nThanks for playing!")


if __name__ == "__main__":
    main()
