# -*- coding: utf-8 -*-
# Code written by Gabriel Mailhot, 25/10/2026.
# Installs the "Calradia Remembers - Adult Tales" module (this repository) into the game's Modules
# folder, beside Calradia Remembers and never inside it. Gabriel (25/10/2026): "un mod Calradia Remembers Adult Tales. Le
# mod aura sa propre page sur Nexus lorsque je serai pret a le mettre en ligne. Mais en attendant je pourrai l'installer
# sur mon poste pour le tester avec le jeu sans risquer de l'uploader dans CR."
#
#   python Tools/install.py              install (or refresh) the module
#   python Tools/install.py --play-test  also the play-test rule (the night at every chance)
#   python Tools/install.py --remove     take the module out of the game
#
# The installed folder is replaced whole each time, so a file removed from the pack does not linger. Git's own files
# (.git, .gitignore), this Tools folder and the PlayTest folder are not copied (the repository is its own folder since
# 27/10/2026); the play-test rule goes in only when asked. Then enable
# "Calradia Remembers - Adult Tales" in the launcher, after Calradia Remembers.
import os, shutil, subprocess, sys

SRC = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
MODULES = r"C:\Program Files (x86)\Steam\steamapps\common\Mount & Blade II Bannerlord\Modules"
DEST = os.path.join(MODULES, "CalradiaRemembersAdultTales")
SKIP_NAMES = {".git", ".gitignore", ".gitattributes", "Tools", "PlayTest"}


def game_running():
    try:
        out = subprocess.run(["tasklist"], capture_output=True, text=True).stdout.lower()
        return "bannerlord" in out or "blse" in out
    except OSError:
        return False


def main():
    args = set(sys.argv[1:])
    if game_running():
        print("Note: the game is running; it reads tales when a campaign loads, so reload one (or restart) to see the change.")

    if "--remove" in args:
        if os.path.isdir(DEST):
            shutil.rmtree(DEST)
            print("removed", DEST)
        else:
            print("not installed:", DEST)
        return

    if not os.path.isfile(os.path.join(SRC, "SubModule.xml")):
        sys.exit("no module at " + SRC)
    if os.path.isdir(DEST):
        # A folder held open (an Explorer window, a player) cannot be removed; its files are, and the copy fills it again.
        shutil.rmtree(DEST, ignore_errors=True)
    shutil.copytree(SRC, DEST, ignore=lambda folder, names: [n for n in names if n in SKIP_NAMES], dirs_exist_ok=True)

    if "--play-test" in args:
        test = os.path.join(SRC, "PlayTest", "play_test_scenario.json")
        shutil.copy2(test, os.path.join(DEST, "ModuleData", "cr_scenarios", "zz_play_test.json"))
        print("play-test rule installed: the night opens at every chance (cr.scenario_fire ON_CAPTIVE_NIGHT).")

    files = sum(len(f) for _, _, f in os.walk(DEST))
    size = sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk(DEST) for f in fs)
    print(f"installed {DEST}: {files} files, {size / 1048576:.0f} MB. Enable it in the launcher, after Calradia Remembers.")


if __name__ == "__main__":
    main()
