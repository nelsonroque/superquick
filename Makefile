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

t:
	sq --ext xlsx --table "~/Documents/Github" --sort size

csv:
	sq --ext xlsx --csv "~/Documents/Github" > results.csv
	python -c "import pandas as pd; df=pd.read_csv('results.csv'); print(df.head())"

json:
	sq --min-size 5g --json "~/Desktop" > bigfiles.json
	sq --ext xlsx --json "~/Documents/Github" > results.json 