pyinstaller --onedir -n firefoxProfileManager --version-file=version.txt main.py --noconsole
cp -r icons dist/firefoxProfileManager/
cp -r locale dist/firefoxProfileManager
cp LICENSE dist/firefoxProfileManager
