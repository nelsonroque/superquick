ir:
	uv venv
	uv pip install -e .

h:
	sq --help

ts:
	sq --ext xlsx -c "~/Documents/Github"

ap:
	sq --ext xlsx --absolute "~/Documents/Github"

fi:
	sq --ext xlsx --absolute --include-hidden --no-skip "~/Documents/Github"

scary:
	sq --substring .env "~/Documents/Github"

sm:
	sq --min-size 1GB "~/Documents/Github"