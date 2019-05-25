import os
import unittest
import game

TESTS_PATH = os.path.dirname(os.path.abspath(__file__))
# dummy game.Game instance required for it's methods as first parameter to make them work
dummy = None


class TestGame(unittest.TestCase):
    """
    Test game.Game methods.
    """

    def test_load_config_files_with_docstrings(self):
        """
        Test if method correctly ignores docstrings in .txt config files.
        """
        test_files_path = TESTS_PATH + "/test_files/"
        os.chdir(test_files_path)
        player, hostiles, boosters, levels, weapons = "player.txt", "hostiles.txt", "powerups.txt", "levels.txt", \
                                                      "weapons.txt",
        content = "#\n#purpose of this file is testing\n#"
        with open(player, "w") as p, open(hostiles, "w") as h, open(boosters, "w") as b, open(levels, "w") as L,\
                open(weapons, "w") as w:
            for file in [p, h, b, L, w]:
                file.writelines(content)
                file.close()

        os.chdir(TESTS_PATH)
        expected = {}, {}, {}, {}, {}
        self.assertEqual(game.load_config_files(path=test_files_path), expected, "Should be: {[str*2]*4}.")

    def test_compare_with_best_scores_with_no_scores(self):
        """Check if provided with an empty list of dicts, method returns: True, None."""
        best_scores, score = [], 65290
        self.assertEqual(game.Game.compare_with_best_scores(best_scores, score), (True, None), "Should be: True, None.")

    def test_compare_with_best_scores_with_higher_scores(self):
        """Check if provided with scores higher than current one, method returns None."""
        best_scores, score = [{"name": "Jack", "score": 72900}, {"name": "Louis", "score": 80000}], 65290
        self.assertEqual(game.Game.compare_with_best_scores(best_scores, score), (True, None), "Should be: True, None.")

    def test_compare_with_best_scores_with_lower_scores(self):
        """Check if provided with scores lower than current one, method returns index 0."""
        best_scores, score = [{"name": "Louis", "score": 2500}, {"name": "Jack", "score": 44134}], 65290
        self.assertEqual(game.Game.compare_with_best_scores(best_scores, score), (True, 1), "Should be: True, 1.")

    def test_compare_with_best_scores_with_lower_and_higher_scores(self):
        """Check if provided with scores both lower and higher than current one, method returns index 1."""
        best_scores, score = [{"name": "Jack", "score": 50900}, {"name": "Louis", "score": 80000}], 65290
        self.assertEqual(game.Game.compare_with_best_scores(best_scores, score), (True, 0), "Should be: True, 0.")

    def test_load_best_scores_with_file(self):
        """Check if provided with no file in config directory it creates new file and returns an empty list."""
        os.chdir(TESTS_PATH + "/test_files")
        self.assertIsInstance(game.Game.load_best_scores(), list, "Should return list.")


if __name__ == "__main__":
    dummy = game.Game(game.SCREEN_WIDTH, game.SCREEN_HEIGHT, game.TITLE, False, True, test=True)
    unittest.main()
