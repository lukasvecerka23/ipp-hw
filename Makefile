archive:
	zip  xvecer30 parse.php  readme1.pdf interpret.py rozsireni
test:
	sudo bash is_it_ok.sh xvecer30.zip testdir
clean:
	rm -rf xvecer30.zip