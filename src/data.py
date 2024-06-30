import json

from const import ROOT_DIR


DEFAULT_SETTINGS = {
    'sound_enabled': True
}


class Data:
    """
    A class for managing file data, such as high scores and saved settings.
    """

    def __init__(self):
        """
        Initializes a Data object.
        """
        self.high_scores_path: str = ROOT_DIR + '/data/highscores.txt'
        self.settings_path: str = ROOT_DIR + '/data/settings.txt'
    
    def write_settings(self, data: dict):
        """
        Write settings to settings.txt to be saved.
        """
        file = open(self.settings_path, mode='w+', encoding='utf-8')
        file.write(json.dumps(data))
        file.close()
    
    def get_settings(self) -> dict:
        """
        Reads and returns settings saved in settings.txt.

        Returns:
            dict: Settings data.
        """
        try:
            file = open(self.settings_path, 'r', encoding='utf-8')
            settings_str = file.read()
            file.close()
            data = json.loads(settings_str)
            return data
        # file does not exist or is invalid
        except:
            return DEFAULT_SETTINGS

    def add_score(self, time: float, difficulty: str = 'beginner', name: str = '') -> int:
        """
        Adds a time to highscores.txt, placed in ascending order.

        Params:
            float: The time to add.
            str: The difficulty for which the time was achieved.
            str: The player name associated with the time.

        Returns:
            int: The position (0-based indexing) of the score within its difficulty.
                Returns -1 if the score was not added.
        """
        all_scores = self.get_all_scores()
        if difficulty in all_scores.keys():
            score_list = all_scores[difficulty]
            position = 0
            # search for position at which to insert new time
            for pair in score_list:
                if time >= pair[1]:
                    position += 1
                else:
                    break
            score_list.insert(position, (name, time))
            all_scores[difficulty] = score_list

            try:
                file = open(self.high_scores_path, mode='w+', encoding='utf-8')
                file.write(json.dumps(all_scores))
                file.close()
                return position
            except:
                return -1

        return -1

    
    def get_all_scores(self) -> dict[str, list[tuple[str, float]]]:
        """
        Reads and returns all high scores saved in highscores.txt.
        
        Returns:
            dict[str, list[tuple[str, float]]]: High score name-time pairs for each difficulty.
        """
        try:
            file = open(self.high_scores_path, 'r', encoding='utf-8')
            all_scores = file.read()
            file.close()
            return json.loads(all_scores)
        except:
            return {
                'beginner': [],
                'intermediate': [],
                'expert': []
            }
        