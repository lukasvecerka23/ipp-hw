archive:
	zip  xvecer30 readme2.md interpret.py lib/* images/*
test:
	sudo bash is_it_ok.sh xvecer30.zip testdir
clean:
	rm -rf xvecer30.zip