.PHONY: test clean docs pypi

test:
	python setup.py test

clean:
	rm -rf dist *.egg-info

docs:
	sphinx-build --version
	$(MAKE) -C docs html

pypi:
	pandoc -v >/dev/null
	python setup.py sdist upload -r pypi
