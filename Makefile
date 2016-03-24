CRUFT_HERE = .tox cover src/*.pyc test/src/*.pyc src/__pycache__ test/src/__pycache__ Glancing.egg-info

NPROC = grep -c ^processor /proc/cpuinfo

clean:
	rm -rf $(CRUFT_HERE)
	find . -type f -name .coverage -print0 | xargs -0 rm

nosetests:
	./run_tests.sh

pytests:
	py.test -n $(call NPROC)

tox:
	tox
