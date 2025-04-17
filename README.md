# 🎼 Data Ingestion Tool for MEI → Cypher

This tool converts music scores modeled in the [MEI XML dialect](https://music-encoding.org/) into **Cypher dumps**, which can be used to populate a **Neo4j** graph database (tested with version **4.2.1.X**). It powers the **graph-based representation** of digital scores used in the [SKRID project](https://gitlab.inria.fr/skrid).

---

## ✨ Features

- Parses **MEI** files into internal graph structures.
- Translates internal representations into **Cypher queries**.
- Designed for integration with **Neo4j** for symbolic music analysis.
- Includes CLI for file-based operations.

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://gitlab.inria.fr/skrid/data-ingestion.git
cd data-ingestion
```

### 2. Dependencies
Requires Python 3.6+

(You can use a virtual environment if desired)

```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 🧪 Usage

Run the converter
```bash
python3 main.py -h
```

CLI Options

```text
usage: python3 main.py [-h] [-V] [-v] [-n] [-o OUTPUT_FOLDER] [-q CQL] files [files ...]

Compiles MEI files into Cypher queries for Neo4j ingestion.

positional arguments:
  files                   MEI files to convert. Appends '_dump.cypher' to basename.

options:
  -h, --help              Show this help message and exit
  -V, --version           Show version and exit
  -v, --verbose           Print logs during conversion
  -n, --no-confirmation   Skip confirmation prompts
  -o, --output-folder     Output folder for the generated Cypher files
  -q, --cql               Also generate a .cql loader file for all output
```

---

### 📁 Project Structure

```text
data-ingestion/
├── main.py                 # Main CLI entry point
├── src/
│   ├── graph/              # Internal graph model components
│   │   ├── Event.py
│   │   ├── Fact.py
│   │   ├── Measure.py
│   │   ├── Score.py
│   │   ├── TopRhythmic.py
│   │   ├── Voice.py
│   │   └── utils_graph.py
│   ├── MeiToGraph.py       # MEI parser
│   ├── ParserUi.py         # CLI logic
│   └── utils.py
│
├── mei/                    # Sample MEI files for testing
├── LICENSE.md              # Project license
├── README.md               # You’re reading it!
└── TODO.md                 # Development roadmap

```

### 🛠️ Development Notes

Each MEI file goes through a two-phase process:

1. Parsing: The file is parsed into an internal object graph (with classes like Score, Voice, Measure, etc.).

2. Exporting: That graph is compiled into Cypher statements for Neo4j ingestion.

This modular separation allows you to inspect or manipulate the graph before export if needed.

---

## TODO

See [TODO.md](TODO.md) for the current list of planned enhancements, open issues, and known limitations.

---

## License

This project is distributed under the MIT License.  
See [LICENSE](./LICENSE) for details.  
(Copyright © 2023–2025 IRISA)