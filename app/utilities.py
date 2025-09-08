from typing import Tuple, List
from .file_declarations import Sound, PATHS, SFX, Music


def format_ms(ms: int | float) -> str:
    """Converts the input of `milliseconds` into \"`minutes`:`seconds`\""""
    total_seconds = int(ms) // 1000
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f"{minutes}:{seconds:02d}"

def generate_non_explicits() -> Tuple[List[Sound], List[Sound]]:
    """
    Generates lists of `Audio` excluding those tagged as `explicit=True`
    Returns:
        Tuple: A tuple of lists, containing `Sound`, two of which are `safe_sfx` and `safe_music`
    """
    safe_sfx = []
    safe_music = []
    
    print("Generating safe_sfx")
    for sfx in SFX:
        if (not sfx.value.explicit):
            safe_sfx.append(sfx)
    print(f"Finished generation. Original size: {len(SFX)} -> New size: {len(safe_sfx)}\n")
    
    print("Generating safe_music")
    for music in Music:
        if (not music.value.explicit):
            safe_music.append(music)
    print(f"Finished generation. Original size: {len(Music)} -> New size: {len(safe_music)}\n")
    
    return safe_sfx, safe_music


def test():
    ms = 12345
    
    print("Testing utilities...\n")
    print(f"{ms}ms -> {format_ms(ms)}")
    

if __name__ == "__main__":
    test()