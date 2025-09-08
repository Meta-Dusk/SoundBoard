from dataclasses import dataclass
from enum import Enum
from pathlib import Path


# Helper function
def resolve_path(file_name: str) -> Path:
    name = file_name.split(".")
    file_extension = name[1]
    
    if (file_extension == "wav"):
        return (PATHS.SFX_DIR.value / file_name).resolve()
    elif (file_extension == "mp3"):
        return (PATHS.MUSIC_DIR.value / file_name).resolve()
    else:
        raise ValueError("Invalid file type. Currently supported ones are .wav and .mp3")


class PATHS(Path, Enum):
    SFX_DIR = Path("assets") / "sfx"
    MUSIC_DIR = Path("assets") / "music"
    SETTINGS_FILE = Path("app") / "settings.json"

@dataclass
class Sound:
    str_path: str
    title: str = "Unknown"
    description: str = "No description"
    explicit: bool = False


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