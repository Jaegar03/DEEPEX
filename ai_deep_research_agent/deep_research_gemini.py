import asyncio
import streamlit as st
from firecrawl import FirecrawlApp
from google import genai

# Set page configuration
st.set_page_config(
    page_title="Gemini Deep Research Agent",
    page_icon="📘",
    layout="wide"
)

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

# Always fetch the latest keys from .env on every rerun
gemini_api_key = os.getenv("GEMINI_API_KEY", "")
firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY", "")

# Store in session state for downstream functions
st.session_state.gemini_api_key = gemini_api_key
st.session_state.firecrawl_api_key = firecrawl_api_key

# Main content
st.title("📘 Gemini Deep Research Agent")
st.markdown("This Agent performs deep research on any topic using Firecrawl and Google's Gemini API.")

# Research topic input
research_topic = st.text_input("Enter your research topic:", placeholder="e.g., Latest developments in AI")

async def run_research_process(topic: str):
    """Run the complete research process."""
    client = genai.Client(api_key=st.session_state.gemini_api_key)
    
    # Step 1: Deep Research with Firecrawl
    with st.spinner("1/3 Conduct deep web research with Firecrawl..."):
        import requests
        import time
        
        activity_placeholder = st.empty()
        activity_placeholder.info(f"[Activity] Initializing deep research...")
        
        headers = {
            "Authorization": f"Bearer {st.session_state.firecrawl_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "query": topic,
            "maxDepth": 3,
            "timeLimit": 180,
            "maxUrls": 10
        }
        
        try:
            # 1. Start Job
            response = requests.post("https://api.firecrawl.dev/v1/deep-research", headers=headers, json=payload)
            response_data = response.json()
            job_id = response_data.get("id")
            
            if not job_id:
                raise Exception(f"Failed to start Firecrawl job: {response_data}")
            
            # 2. Poll Job
            results = None
            while True:
                activity_placeholder.info(f"[Activity] Deep research is running: Polling job {job_id}...")
                time.sleep(5)
                status_resp = requests.get(f"https://api.firecrawl.dev/v1/deep-research/{job_id}", headers=headers)
                status_data = status_resp.json()
                status = status_data.get("status", "unknown")
                
                if status == "completed":
                    results = status_data
                    activity_placeholder.info(f"[Activity] Deep research completed!")
                    break
                elif status == "failed":
                    raise Exception(f"Firecrawl task failed: {status_data}")
                    
            activity_placeholder.empty()
            
            # 3. Parse Results
            final_analysis = results.get('data', {}).get('data', {}).get('finalAnalysis', results.get('data', {}).get('finalAnalysis', 'No analysis returned'))
            sources = results.get('data', {}).get('data', {}).get('sources', results.get('data', {}).get('sources', []))
            
            # Format sources for prompt
            sources_text = "\n".join([f"- {s.get('url', 'Unknown URL')} (Title: {s.get('title', 'No Title')})" for s in sources])
            research_context = f"Final Analysis from Firecrawl:\n{final_analysis}\n\nSources used:\n{sources_text}"
            
        except Exception as parse_e:
            research_context = f"Error during Firecrawl process: {parse_e}"

    # Step 2: Synthesize initial report with Gemini
    with st.spinner("2/3 Synthesizing initial report with Gemini..."):
        synthesis_prompt = f"""You are a research assistant. 
        Based on the following deep research context from Firecrawl about the topic: "{topic}", 
        organize the results into a well-structured report.
        Include proper citations for all sources and highlight key findings and insights.
        
        Research Context:
        {research_context}
        """
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=synthesis_prompt,
        )
        initial_report = response.text
    
    # Display initial report in an expander
    with st.expander("View Initial Research Report"):
        st.markdown(initial_report)
    
    # Step 3: Enhance the report
    with st.spinner("3/3 Enhancing the report with deeper insights..."):
        elaboration_input = f"""
        RESEARCH TOPIC: {topic}
        
        INITIAL RESEARCH REPORT:
        {initial_report}
        
        You are an expert content enhancer specializing in research elaboration.
        Please enhance this research report with additional information, examples, case examples (if applicable), 
        and deeper insights while maintaining its academic rigor and factual accuracy.
        - Add more detailed explanations of complex concepts.
        - Include relevant practical applications.
        - Expand on key points with additional context and nuance.
        - Maintain proper citations to the sources in the original report.
        - Preserve the original structure while making it more comprehensive.
        """
        
        elaboration_response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=elaboration_input,
        )
        enhanced_report = elaboration_response.text
    
    return enhanced_report

# Main research process
if st.button("Start Research", disabled=not research_topic):
    if not research_topic:
        st.warning("Please enter a research topic.")
    else:
        try:
            # Create placeholder for the final report
            report_placeholder = st.empty()
            
            # Run the research process
            enhanced_report = asyncio.run(run_research_process(research_topic))
            
            # Display the enhanced report
            report_placeholder.markdown("## Enhanced Research Report")
            report_placeholder.markdown(enhanced_report)
            
            # Add download button
            st.download_button(
                "Download Report",
                enhanced_report,
                file_name=f"{research_topic.replace(' ', '_')}_report.md",
                mime="text/markdown"
            )
            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# Footer
st.markdown("---")
st.markdown("Powered by Google GenAI and Firecrawl")
