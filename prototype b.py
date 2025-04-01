import random
import time
import logging
from typing import List, Dict, Optional

# Configure error logging
logging.basicConfig(
    filename="error_log.txt",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class Character:
    """Represents a battle character with abilities and stats."""

    def __init__(self, name: str, battle_power: int, char_type: str,
                 abilities: List[str], speed: int) -> None:
        self.name: str = name
        self.battle_power: int = battle_power
        self.char_type: str = char_type
        self.abilities: List[str] = abilities
        self.health: int = 100
        self.damage_dealt: int = 0
        self.speed: int = speed
        self.damage_reduction: int = 0  # For damage reduction

    def take_damage(self, damage: int) -> None:
        """
        Reduces character health when attacked, considering damage reduction.
        """
        effective_damage = max(0, damage - self.damage_reduction)
        self.health = max(0, self.health - effective_damage)
        self.damage_reduction = 0  # Reset after taking damage

    def is_alive(self) -> bool:
        """Returns True if character is still alive."""
        return self.health > 0

    def heal(self, amount: int) -> None:
        """Heals the character by a certain amount, up to a maximum of 100."""
        self.health = min(100, self.health + amount)

    def boost(self) -> None:
        """Boosts the character's attack power temporarily."""
        self.battle_power += 5

    def shield(self) -> None:
        """Temporarily reduces incoming damage for one turn."""
        self.damage_reduction = 5  # Reduces damage taken


class AINarrator:
    """
    Handles narration for battle events. The delay between narrations
    is configurable via the class variable 'delay'.
    """
    delay: float = 1.0  # default delay in seconds

    @staticmethod
    def narrate(action: str) -> None:
        """Prints a narrated action with a delay for dramatic effect."""
        print(f"\n* {action} *")
        time.sleep(AINarrator.delay)

    @classmethod
    def battle_start(cls, player_name: str, strategy: str) -> None:
        cls.narrate(f"{player_name}'s team enters the battlefield, executing a **{strategy} strategy**!")

    @classmethod
    def round_start(cls, round_num: int) -> None:
        cls.narrate(f"⚔️ **Round {round_num} begins!** Fighters brace themselves.")

    @classmethod
    def game_over(cls, winning_team: str) -> None:
        cls.narrate(f"🏆 **{winning_team} wins the battle!**")

    @classmethod
    def character_dead(cls, character: str) -> None:
        cls.narrate(f"💀 **{character} has been defeated!**")


class Battle:
    """
    Manages game flow and combat calculations.
    """

    def __init__(self, player_name: str, team1: Dict, team2: Dict) -> None:
        self.player_name: str = player_name
        self.team1: Dict = team1
        self.team2: Dict = team2
        self.round_num: int = 1
        self.narrator = AINarrator()
        self.apply_captain_boosts()

    def start(self) -> None:
        """Begins the battle sequence."""
        self.narrator.battle_start(self.player_name, self.team1["strategy"])

        while not self.is_game_over():
            self.narrator.round_start(self.round_num)
            self.play_round()
            self.round_num += 1

        self.announce_winner()
        self.post_battle_recap()

    def apply_captain_boosts(self) -> None:
        """
        Adjusts team performance based on captain type.
        """
        captain: Character = self.team1["captain"]
        for member in self.team1["members"]:
            if captain.char_type == "strategist":
                member.speed += 3  # Tactical advantage
            elif captain.char_type == "tank":
                member.health = min(100, member.health + 10)  # Extra durability
            elif captain.char_type == "energy":
                member.battle_power += 5  # More damage

    @staticmethod
    def get_random_alive(opponents: List[Character]) -> Optional[Character]:
        """
        Returns a random alive character from the list of opponents.
        """
        alive = [opponent for opponent in opponents if opponent.is_alive()]
        return random.choice(alive) if alive else None

    def play_round(self) -> None:
        """
        Handles a single round of combat.
        """
        all_characters = self.team1["members"] + self.team2["members"]
        # Sort by speed in descending order
        turn_order = sorted(all_characters, key=lambda x: x.speed, reverse=True)

        for character in turn_order:
            if character.is_alive():
                defending_team = self.team2["members"] if character in self.team1["members"] else self.team1["members"]
                self.perform_action(character, defending_team)

    def perform_action(self, attacker: Character, defending_team: List[Character]) -> None:
        """
        Executes an action (attack or ability) on a random opponent.
        """
        try:
            # Ensure there is at least one alive opponent
            target = self.get_random_alive(defending_team)
            if target is None:
                return

            action = random.choice(attacker.abilities)
            if action == "Heal":
                attacker.heal(20)
                AINarrator.narrate(f"{attacker.name} uses **Heal**, restoring 20 health!")
                return

            if action == "Boost":
                attacker.boost()
                AINarrator.narrate(f"{attacker.name} uses **Boost**, increasing attack power!")
                return

            if action == "Shield":
                attacker.shield()
                AINarrator.narrate(f"{attacker.name} uses **Shield**, reducing incoming damage next turn!")
                return

            # Calculate damage: base random damage adjusted by battle power
            damage = random.randint(10, 30) + attacker.battle_power // 10
            target.take_damage(damage)
            attacker.damage_dealt += damage

            AINarrator.narrate(f"{attacker.name} uses **{action}** on {target.name}, dealing {damage} damage!")
            if not target.is_alive():
                AINarrator.character_dead(target.name)

        except Exception as e:
            logging.exception("Error occurred in perform_action")

    def is_game_over(self) -> bool:
        """
        Returns True if all members of either team are defeated.
        """
        team1_defeated = all(not member.is_alive() for member in self.team1["members"])
        team2_defeated = all(not member.is_alive() for member in self.team2["members"])
        return team1_defeated or team2_defeated

    def announce_winner(self) -> None:
        """
        Declares the winning team based on which team still has alive members.
        """
        if all(not member.is_alive() for member in self.team1["members"]):
            winning_team = "AI Team"
        else:
            winning_team = f"{self.player_name}'s Team"
        AINarrator.game_over(winning_team)

    def post_battle_recap(self) -> None:
        """
        Provides a summary of the battle after it ends.
        """
        print("\n📜 **Post-Battle Recap:**")
        for team, label in [(self.team1, f"{self.player_name}'s Team"), (self.team2, "AI Team")]:
            print(f"\n🔹 {label}:")
            for character in team["members"]:
                status = "❌ Defeated" if not character.is_alive() else "✅ Survived"
                print(f"  - {character.name}: Damage Dealt: {character.damage_dealt} | {status}")


def choose_team(character_roster: List[Character]) -> List[Character]:
    """
    Allows the player to choose a team of three fighters with error handling.
    """
    print("\nChoose 3 fighters from the list below:")
    for idx, char in enumerate(character_roster):
        print(f"{idx + 1}. {char.name}")

    selected_indices = set()
    while len(selected_indices) < 3:
        try:
            choice = int(input(f"Enter character number {len(selected_indices) + 1}: ")) - 1
            if choice in selected_indices or not (0 <= choice < len(character_roster)):
                raise ValueError("Invalid selection. Choose a different character.")
            selected_indices.add(choice)
        except ValueError as e:
            print("Invalid input. Try again.")
            logging.error(f"Character Selection Error: {e}")

    return [character_roster[i] for i in selected_indices]


def main() -> None:
    """
    Main function to start the Epic AI Battle game.
    """
    print("⚡ Welcome to **Epic AI Battle!** ⚡")
    player_name = input("Enter your name: ").strip()

    # Create the character roster
    character_roster = [
        # Marvel Characters
        Character("Iron Man", 85, "energy", ["Repulsor Blast", "Unibeam", "Heal", "Boost"], 9),
        Character("Captain America", 80, "strategist", ["Shield Throw", "Super Strength", "Heal", "Shield"], 7),
        Character("Thor", 90, "energy", ["Mjolnir Strike", "Lightning Storm", "Boost", "Shield"], 8),
        Character("Black Widow", 75, "strategist", ["Widow's Bite", "Martial Arts", "Boost", "Shield"], 10),
        Character("Hulk", 100, "tank", ["Smash", "Thunder Clap", "Heal", "Shield"], 6),
        Character("Black Panther", 85, "tank", ["Vibranium Strike", "Kinetic Blast", "Boost", "Shield"], 9),
        Character("Spider-Man", 80, "energy", ["Web Shooters", "Spider Sense", "Boost", "Shield"], 10),
        Character("Scarlet Witch", 95, "energy", ["Chaos Magic", "Hex Bolts", "Boost", "Shield"], 8),
        Character("Doctor Strange", 92, "strategist", ["Time Stone", "Astral Projection", "Boost", "Shield"], 7),
        Character("Vision", 85, "energy", ["Solar Beam", "Mass Manipulation", "Boost", "Shield"], 8),
        Character("Deadpool", 80, "tank", ["Regeneration", "Sword Combat", "Boost", "Shield"], 9),
        Character("Wolverine", 85, "tank", ["Adamantium Claws", "Regeneration", "Boost", "Shield"], 8),
        Character("Gamora", 80, "strategist", ["Dagger Throw", "Deadly Accuracy", "Boost", "Shield"], 9),
        Character("Rocket Raccoon", 75, "energy", ["Gun Mastery", "Tech Gadgets", "Boost", "Shield"], 7),
        Character("Star-Lord", 75, "strategist", ["Element Guns", "Aerial Combat", "Boost", "Shield"], 8),
        Character("Ant-Man", 70, "strategist", ["Pym Particles", "Ant Control", "Boost", "Shield"], 6),

        # Dragon Ball Z Characters
        Character("Goku", 95, "energy", ["Kamehameha", "Instant Transmission", "Boost", "Shield"], 10),
        Character("Vegeta", 90, "energy", ["Final Flash", "Galick Gun", "Boost", "Shield"], 9),
        Character("Frieza", 90, "energy", ["Death Beam", "Frieza's Wrath", "Boost", "Shield"], 8),
        Character("Cell", 85, "tank", ["Solar Kamehameha", "Regeneration", "Boost", "Shield"], 7),
        Character("Majin Buu", 95, "tank", ["Chocolate Beam", "Absorption", "Boost", "Shield"], 6),
        Character("Piccolo", 80, "strategist", ["Special Beam Cannon", "Regeneration", "Boost", "Shield"], 8),
        Character("Trunks", 85, "energy", ["Burning Attack", "Sword Combat", "Boost", "Shield"], 9),
        Character("Gohan", 85, "energy", ["Masenko", "Super Kamehameha", "Boost", "Shield"], 8),
        Character("Krillin", 75, "energy", ["Destructo Disc", "Kienzan", "Boost", "Shield"], 7),
        Character("Tien Shinhan", 80, "strategist", ["Tri-Beam", "Solar Flare", "Boost", "Shield"], 8),
        Character("Yamcha", 70, "strategist", ["Wolf Fang Fist", "Destructo Disc", "Boost", "Shield"], 8),

        # DC Characters
        Character("Superman", 100, "tank", ["Heat Vision", "Super Punch", "Boost", "Shield"], 10),
        Character("Batman", 85, "strategist", ["Batarang", "Martial Arts", "Boost", "Shield"], 9),
        Character("Wonder Woman", 90, "tank", ["Lasso of Truth", "Bracelets of Submission", "Boost", "Shield"], 8),
        Character("The Flash", 80, "strategist", ["Speed Force", "Time Travel", "Boost", "Shield"], 10),
        Character("Green Lantern", 85, "energy", ["Power Ring", "Light Constructs", "Boost", "Shield"], 8),
        Character("Aquaman", 85, "tank", ["Trident Strike", "Aquatic Speed", "Boost", "Shield"], 8),
        Character("Lex Luthor", 80, "strategist", ["Kryptonite Weapon", "Mechanical Armor", "Boost", "Shield"], 7),
        Character("Joker", 75, "energy", ["Acid Flower", "Crazed Gadgets", "Boost", "Shield"], 7),
        Character("Harley Quinn", 75, "energy", ["Hammer Smash", "Toxic Gas", "Boost", "Shield"], 8),
        Character("Shazam", 95, "energy", ["Lightning Strike", "Shazam Punch", "Boost", "Shield"], 9),
        Character("Cyborg", 85, "energy", ["Boom Tube", "Energy Cannon", "Boost", "Shield"], 7),
        Character("Green Arrow", 80, "strategist", ["Explosive Arrows", "Archery", "Boost", "Shield"], 8),
        Character("Catwoman", 75, "tank", ["Cat Claws", "Agility", "Boost", "Shield"], 9),
        Character("Ra's al Ghul", 80, "strategist", ["Lazarus Pit", "Sword Combat", "Boost", "Shield"], 7),
        Character("Deathstroke", 85, "tank", ["Sword Strike", "Tactical Combat", "Boost", "Shield"], 8)
    ]

    player_team = choose_team(character_roster)

    # Select team captain
    print("\nSelect your team captain:")
    for i, char in enumerate(player_team):
        print(f"{i + 1}. {char.name}")
    while True:
        try:
            captain_choice = int(input(f"Choose captain (1-{len(player_team)}): "))
            if 1 <= captain_choice <= len(player_team):
                captain = player_team[captain_choice - 1]
                break
            else:
                raise ValueError("Choice out of range.")
        except ValueError as e:
            print("Invalid input. Please try again.")
            logging.error(f"Captain Selection Error: {e}")

    strategy = input("Choose your battle strategy (Offensive, Defensive, Balanced): ").strip().capitalize()

    # Randomly choose AI team and captain
    ai_team = random.sample(character_roster, 3)
    ai_captain = random.choice(ai_team)

    battle = Battle(
        player_name,
        {"members": player_team, "captain": captain, "strategy": strategy},
        {"members": ai_team, "captain": ai_captain, "strategy": "Balanced"}
    )

    battle.start()


if __name__ == "__main__":
    main()