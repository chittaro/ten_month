PROJECTID   := AD48FB4835AF347EB0CA8009E24C3B13F8519882
EXECUTABLE  := galaxy
PROJECTNAME := p2-a-new-heap

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
