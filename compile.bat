@echo off
pyinstaller --onedir -n firefoxProfileManager --version-file=version.txt main.py --noconsole
mkdir dist\firefoxProfileManager\locale
mkdir dist\firefoxProfileManager\icons
xcopy locale dist\firefoxProfileManager\locale /s /e
xcopy icons dist\firefoxProfileManager\icons /s /e
copy LICENSE dist\firefoxProfileManager
