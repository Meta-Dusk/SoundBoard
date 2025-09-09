from dataclasses import dataclass
from enum import Enum
from pathlib import Path


# Helper function
def resolve_path(file_name: str) -> Path:
    class FileExtensions(str, Enum):
        WAV = "wav"
        MP3 = "mp3"
        PNG = "png"
        JPG = "jpg"
    
    name = file_name.split(".")
    file_extension = name[1]
    
    if (file_extension == FileExtensions.WAV):
        return (PATHS.SFX_DIR.value / file_name).resolve()
    elif (file_extension == FileExtensions.MP3):
        return (PATHS.MUSIC_DIR.value / file_name).resolve()
    elif (file_extension == FileExtensions.PNG or FileExtensions.JPG):
        return (PATHS.IMAGES_DIR.value / file_name).resolve()
    else:
        raise ValueError(f"Invalid file type. Currently supported ones are: {[f.name.lower() for f in FileExtensions]}")


class PATHS(Path, Enum):
    SFX_DIR = Path("assets") / "sfx"
    MUSIC_DIR = Path("assets") / "music"
    IMAGES_DIR = Path("assets") / "images"
    SETTINGS_FILE = Path("app") / "settings.json"

@dataclass
class Sound:
    str_path: str
    title: str = "Unknown"
    description: str = "No description"
    explicit: bool = False

@dataclass
class Image:
    str_path: str
    description: str = "Unknown"


# 📷 Images
class Images(Enum):
    SEB = Image(resolve_path("sebicon.png"), "Seb when bored")


# 🎵 Music
class Music(Enum):
    PATRIOT = Sound(resolve_path("patriot.mp3"), "Feofilov - Patriot", "prod. DJ PIČKA x DJ PEDOPHILE feat. DJ CIGAN", explicit=True)
    NECKHURTS = Sound(resolve_path("neckhurts.mp3"), "Neckhurts (Tiktok remix bass boosted)", "Perfect club music", explicit=True)
    PATAPIM = Sound(resolve_path("patapim.mp3"), "Brr Brr Patapim Alarm😴⏰", "A perfect alarm to wake up to")
    CRAZY = Sound(resolve_path("crazy.mp3"), "CRAZY - LE SSERAFIM", "Acting like an angel dressed like?")
    HOTNFUN = Sound(resolve_path("1800.mp3"), "1-800-hot-n-fun", "I like to danc when I party")
    TV_OFF = Sound(resolve_path("tv_off.mp3"), "tv off - Kendrick Lamar", "Me when mustard")
    WHIPLASH = Sound(resolve_path("whiplash.mp3"), "WHIPLASH - AESPA", "One look... Give 'em what?")


# 🔊 Sound Effects
class SFX(Enum):
    FN = Sound(resolve_path("fn.wav"), "Puck Higgens", "ifykyk", explicit=True)
    ANEURYSM = Sound(resolve_path("aneurysm.wav"), "Brain Aneurysm", "Yep")
    AMONGUS = Sound(resolve_path("amongus.wav"), "Amongus", "It's just a dude shouting amongus")
    CATLAUGH = Sound(resolve_path("catlaugh.wav"), "Cat Laugh (Loud)", "A cat laughing at you at your expense")
    GOOFYHORN = Sound(resolve_path("goofyhorn.wav"), "Goofy Car Horn", "Goofy ahh horn... Use responsibly")
    HOLYMOLY = Sound(resolve_path("holymoly.wav"), "Holy Moly 😮", "Woah")
    KUYASHI = Sound(resolve_path("kuyashi.wav"), "くやし 😡", "It means frustration")
    YATTA = Sound(resolve_path("yatta.wav"), "やった 😆", "It means yippe")
    NESQUICK = Sound(resolve_path("nesquick.wav"), "Nesquick", "ifykyk", explicit=True)
    CRAZY = Sound(resolve_path("crazy.wav"), "Dressed Like...", "Acting like an angel dressed like?")
    DANCE = Sound(resolve_path("dance_when_party.wav"), "I Like to Dance when I Party", "Who the hell is Saki?")
    MUSTARD = Sound(resolve_path("mustard.wav"), "MUSTAAAAAAARD", "Mustard is a condiment made from the seeds of a mustard plant")
    WHIPLASH = Sound(resolve_path("whiplash.wav"), "One Look...", "Give 'em whiplash")


"""
Run with:
py -m app.file_declarations
"""

def test():
    def check_audio():
        """Checks integrity of all audio files"""
        sfx_count = 0
        music_count = 0

        print("\nChecking registered SFX...")
        for sfx in SFX:
            if Path(sfx.value.str_path).exists():
                print(f"{sfx.name}: {sfx.value.str_path}")
                sfx_count += 1
            else:
                print(f"SFX {sfx.name} does not exist at {sfx.value.str_path}!")
        print(f"Found {sfx_count}/{len(SFX)} SFX files\n")

        print("\nChecking registered Music...")
        for music in Music:
            if Path(music.value.str_path).exists():
                print(f"{music.name}: {music.value.str_path}")
                music_count += 1
            else:
                print(f"Music {music.name} does not exist at {music.value.str_path}!")
        print(f"Found {music_count}/{len(Music)} Music files\n")

        if sfx_count == len(SFX) and music_count == len(Music):
            print("[AudioManager] ✅ All sound files are fully registered!\n")
        else:
            print("[AudioManager] ⚠️ Some files are missing.\n")
            
    print("Test for validating assets...\n")
    check_audio()
    
if __name__ == "__main__":
    test()