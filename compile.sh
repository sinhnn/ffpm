pyinstaller --onedir \
	-n ffpm \
	--version-file=version.txt \
	--icon="icons/program_icon.ico" \
	main.py --noconsole

cp -r icons dist/ffpm/
cp -r locale dist/ffpm/
cp LICENSE dist/ffpm/
