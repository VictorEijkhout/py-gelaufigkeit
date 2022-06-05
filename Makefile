info ::
	@echo "This makefile does modest administration of the"
	@echo "py-gelaufigkeit repository."
	@echo
	@echo "Available rules:"

info ::
	@echo "make exercise (where exercise=....)"
% : %.py
	python $@.py > ./lilys/$@.ly
	cd lilys ; lilypond $@.ly ; mv $@.pdf ../pdfs

info ::
	@echo "make clean"
clean ::
	/bin/rm -f *~ *.pyc *.pdf *.ly
