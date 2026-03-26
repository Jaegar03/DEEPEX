# Deep Research Agent with GEMINI Agents SDK and Firecrawl



## Features

- **Deep Web Research**: Automatically searches the web, extracts content, and synthesizes findings
- **Enhanced Analysis**: Uses Google's Gemini SDK to elaborate on research findings with additional context and insights
- **Interactive UI**: Clean Streamlit interface for easy interaction
- **Downloadable Reports**: Export research findings as markdown files

## How It Works

1. **Input Phase**: User provides a research topic and API credentials
2. **Research Phase**: The tool uses Firecrawl to search the web and extract relevant information
3. **Analysis Phase**: An initial research report is generated based on the findings
4. **Enhancement Phase**: A second agent elaborates on the initial report, adding depth and context
5. **Output Phase**: The enhanced report is presented to the user and available for download

## Requirements

- Python 3.8+
- Gemini API key
- Firecrawl API key
- Required Python packages (see `requirements.txt`)

## Example Run

![Topic Submission](assets/example-1.png)
![Deep Research Execution](assets/example-2.png)
![Full Report Generation](assets/example-3.png)

## Usage

1. Run the Streamlit app:
   ```bash
   streamlit run deep_research_gemini.py
   ```

2. API Keys are automatically loaded from your `.env` file. Make sure your `.env` file is properly configured.

3. Enter your research topic in the main input field

4. Click "Start Research" and wait for the process to complete

5. View and download your enhanced research report

## Example Research Topics

- "Latest developments in quantum computing"
- "Impact of climate change on marine ecosystems"
- "Advancements in renewable energy storage"
- "Ethical considerations in artificial intelligence"
- "Emerging trends in remote work technologies"

## Technical Details

The application uses two specialized agents:

1. **Research Agent**: Utilizes Firecrawl's deep research endpoint to gather comprehensive information from multiple web sources.

2. **Elaboration Agent**: Enhances the initial research by adding detailed explanations, examples, case studies, and practical implications.

The Firecrawl deep research tool performs multiple iterations of web searches, content extraction, and analysis to provide thorough coverage of the topic.

