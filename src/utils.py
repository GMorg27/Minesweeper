def time_to_str(time: float) -> str:
    """
        Helper function to convert a time in seconds to a string in 'mm:ss' format.

        Params:
            float: An amount of time, in seconds.
        
        Returns:
            str: The time in 'mm:ss' format.
    """
    seconds = int(time)
    minutes_text = str(int(seconds / 60)).rjust(2, '0')
    seconds_text =  str(seconds % 60).rjust(2, '0')
    return minutes_text + ':' + seconds_text
