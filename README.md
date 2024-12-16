# Ontology Chat Builder

An interactive tool that uses AI to help build and visualize ontologies. The system creates OWL files that can be visualized using WebVOWL.

## Features

- Interactive ontology creation using AI assistance
- Support for both Anthropic (Claude) and OpenAI GPT models
- Automatic naming and structuring of ontologies
- WebVOWL visualization support
- Available as both a Python script and Jupyter notebook

## Prerequisites

- Python 3.9+
- Docker Desktop
- Anthropic API key or OpenAI API key
- Jupyter (optional, for notebook interface)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ontology-chat-builder.git
cd ontology-chat-builder
```

2. Create and activate a conda environment:
```bash
conda create -n ontology python=3.9
conda activate ontology
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
- Copy `.env.example` to `.env`
- Add your API configuration (see API Configuration section below)

5. Download WebVOWL:
- Download WebVOWL 1.1.7 from http://vowl.visualdataweb.org/downloads/
- Rename it to `webvowl_1.1.7.war`
- Place it in the project root directory

## API Configuration

This tool supports both Anthropic and OpenAI APIs. To configure:

1. Copy `.env.example` to `.env`
2. Choose your API provider by setting `API_PROVIDER` to either `anthropic` or `openai`
3. Add the appropriate API key:
   - For Anthropic: Add your Claude API key as `ANTHROPIC_API_KEY`
   - For OpenAI: Add your OpenAI API key as `OPENAI_API_KEY`

Example `.env` for Anthropic:
```plaintext
API_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-xxx...
```

Example `.env` for OpenAI:
```plaintext
API_PROVIDER=openai
OPENAI_API_KEY=sk-xxx...
```

## Running the Application

### Using Docker (Required for Visualization)

1. Start the WebVOWL visualization server:
```bash
docker build . -t webvowl:v1
docker-compose up -d
```

### Option 1: Python Script

Run the ontology builder script:
```bash
python ontology_builder.py
```

### Option 2: Jupyter Notebook

1. Start Jupyter:
```bash
jupyter notebook
```

2. Open `ontology_builder.ipynb`
3. Follow the notebook cells and instructions

### Visualizing the Ontology

1. Open http://localhost:8081/webvowl in your browser
2. Click "Ontology" in the menu
3. Select "Upload ontology from file"
4. Choose the generated .owl file from the data directory

## Usage

1. When prompted, describe the ontology you want to create:
```
Describe what you want to add to the ontology: Create an ontology about a university system
```

2. The system will:
- Generate a meaningful name for the ontology
- Create classes and properties based on your description
- Save the ontology as an OWL file
- Allow you to visualize it using WebVOWL

3. Continue adding to your ontology or type 'quit' to exit

## Project Structure

```
ontology-chat-builder/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env
├── .env.example
├── .gitignore
├── README.md
├── config.py
├── api_client.py
├── ontology_builder.py
├── ontology_builder.ipynb
├── webvowl_1.1.7.war
└── data/
    └── *.owl
```

## Development

- The script version (`ontology_builder.py`) is suitable for command-line usage
- The notebook version (`ontology_builder.ipynb`) provides an interactive interface
- Both versions share the same core functionality through the OntologyBuilder class

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)


