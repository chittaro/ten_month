PROJECTID   := 0E04A31E0D60C01986ACB20081C9D8722A1899B6
EXECUTABLE  := market
PROJECTNAME := p2-stocks

files: $(PROJECTNAME)/*
	rm -f $(PROJECTNAME)-files.tgz
	wget -q -O - https://raw.githubusercontent.com/eecs281staff/Makefile/main/Makefile \
    | sed 's/EEC50281EEC50281EEC50281EEC50281EEC50281/$(PROJECTID)/' \
    | sed 's/= executable/= $(EXECUTABLE)/' \
    > $(PROJECTNAME)/Makefile
	COPYFILE_DISABLE=true tar cvzf $(PROJECTNAME)-files.tgz $(PROJECTNAME)
	echo "" >> files.md
	echo "* [Makefile]($(PROJECTNAME)/Makefile)" >> files.md
	$(foreach fil,$(sort $^),echo "* [$(subst $(PROJECTNAME)/,,$(fil))]($(fil))" >> files.md;)

.PHONY: files
