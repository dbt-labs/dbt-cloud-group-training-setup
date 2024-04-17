under-armour-setup:
	python3 setup.py jumpstart_under_armour_20210223.yml setup

under-armour-followup:
	python3 setup.py jumpstart_under_armour_20210223.yml followup


geico-setup-test:
	python3 setup.py --config 2023-01-18_private_geico.yml setup  -- test

geico-followup:
	python3 setup.py --config 2023-01-18_private_geico.yml followup

	python3 setup.py 2023-01-18_private_geico.yml setup --test