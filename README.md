# Musypher
<!-- Convert XML MEI music files to cypher dumps that can be used to load a graph representing the music score in the Neo4j database. -->
Converts a music score, modelled by a XML file that respects the dialect MEI, in a Cypher dump, which can be used in the graph database management system Neo4J in order to produce a graph representation of the music score.

The primary goal of this software is to generate a graph database for the [SKRID](https://github.com/lasercata/SKRIDPlatform) interface.

## Project structure
```
├── main.py                 Main file
├── src/
│   ├── graph/              Internal graph representation of the scores
│   │   ├── Event.py
│   │   ├── Fact.py
│   │   ├── Measure.py
│   │   ├── Score.py
│   │   ├── TopRhythmic.py
│   │   ├── utils_graph.py
│   │   └── Voice.py
│   │
│   ├── MeiToGraph.py       Parser of the MEI files, uses files in `graph/` to represent the parsed result
│   ├── ParserUi.py         User interface (argument parser)
│   └── utils.py
│
├── mei/                    Examples MEI files to test to program
│
├── README.md
└── TODO.md
```

General principle : Each MEI file is parsed and converted to an internal graph representation on the fly, and the internal graph representation is then converted to a cypher dump.

## Usage
### Setup
Get the code :
```
git clone --depth=1 https://github.com/lasercata/Musypher.git
cd Musypher
```

Make the main file executable :
```
chmod u+x main.py
```

### Run
```
$ ./main.py -h
usage: Musypher [-h] [-V] [-v] [-n] [-o OUTPUT_FOLDER] [-q CQL] files [files ...]

Compiles fuzzy queries to cypher queries

positional arguments:
  files                 the MEI files to convert. For each file, it adds "_dump.cypher" to the
                        basename of the file.

options:
  -h, --help            show this help message and exit
  -V, --version         show version and exit
  -v, --verbose         print logs when a file is converted
  -n, --no-confirmation
                        Do not ask for confirmation before overwriting a file
  -o OUTPUT_FOLDER, --output-folder OUTPUT_FOLDER
                        save all dumps in the given folder
  -q CQL, --cql CQL     If enabled, also create the .cql file (that is useful to load all the
                        generated .cypher in the database)

Examples :
    convert `file.mei`                       : ./main.py file.mei
    convert all mei files in the mei/ folder : ./main.py mei/*.mei
    convert all mei files in the sub path    : ./main.py **/*.mei
    convert all, overwrite, save in cypher/,
    generate .cql, show progression         : ./main.py -nv -q load_all.cql -o cypher/ **/*.mei
```

## TODO
See [TODO](TODO.md)
