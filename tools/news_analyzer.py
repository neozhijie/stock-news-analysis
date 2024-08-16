from groq import Groq
from dotenv import load_dotenv
import os
import json
import requests
# Load environment variables from .env file
load_dotenv()

# Get the API key from the environment variables
api_key = os.getenv('GROQ_API_KEY')

class NewsAnalyzer:
    def __init__(self):
        self.client = Groq(api_key=api_key)

    def analysis1(self, article_text, ticker, counter):
        """Perform sentiment analysis on the article."""
        prompt = f"""
        You are an expert stock analyst. You are to perform 3 tasks on a given article:
        Task 1: Analyze the sentiment of the following news article of the stock with ticker {ticker}. Provide a brief summary of the overall tone 
        and emotional content. Rate the sentiment on a scale from -1 (very negative) to 1 (very positive). 
        
        Task 2: Extract the main key points from the following news article of the stock with ticker {ticker}. Provide a bullet-point list of 
        the most important information, facts, and arguments presented in the article.

        Task 3: Analyze the following news article for potential bias of the stock with ticker {ticker}. Consider the language used,

        Article:
        {article_text}

        Analysis:
        """
        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="gemma2-9b-it",
                temperature=0.5,
                max_tokens=500,

            )
           
            return response.choices[0].message.content
        except Exception as e:
            return None

    def analysis2(self, article_text, ticker, counter):
        """Perform sentiment analysis on the article."""
        prompt = f"""
        You are an expert stock analyst. You are to perform 3 tasks on a given article:
        Task 1: Analyze the sentiment of the following news article of the stock with ticker {ticker}. Provide a brief summary of the overall tone 
        and emotional content. Rate the sentiment on a scale from -1 (very negative) to 1 (very positive). 
        
        Task 2: Extract the main key points from the following news article of the stock with ticker {ticker}. Provide a bullet-point list of 
        the most important information, facts, and arguments presented in the article.

        Task 3: Analyze the following news article for potential bias of the stock with ticker {ticker}. Consider the language used,

        Article:
        {article_text}

        Analysis:
        """
        try:

            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-8b-8192",
                temperature=0.5,
                max_tokens=500,

            )

            return response.choices[0].message.content
        except Exception as e:
            return None
        
        

    def aggregate_results(self, analysis1, analysis2, ticker):
        """Aggregate and synthesize the results from the three analyses."""
        prompt = f"""
        You are an expert stock analyzer and evaluator. You are given 2 analysis of {ticker}. Synthesize the following 2 analyses of a news article into a comprehensive summary in a json format with no line breaks.

        First Analysis:
        {analysis1}

        Second Analysis:
        {analysis2}

        Synthesize these responses into a single, concise, high quality response by Giving a score rating of sentiment in the perspective of a stock analyst analyzing the stock with ticker {ticker} on a scale from -1 (very negative) to 1 (very positive), and give 2 reasons why you gave that score.  Your answer will strictly be a JSON object with keys: Sentiment Score, Reason 1, Reason 2.  Do not deviate from this template, do not add anything else.

        High quality summary:
        """
        
        response = self.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            temperature=0.5,
            max_tokens=500,
        )
        try:
            return json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            return self.json_check(response.choices[0].message.content)

    def analyze_news_article(self, article_text, ticker, counter):
        """Main function to analyze a news article using multiple models and aggregate results."""
        analysis1 = self.analysis1(article_text, ticker, counter)
        analysis2 = self.analysis2(article_text, ticker, counter)

        if analysis1 and analysis2:
            compiled_analysis = self.aggregate_results(analysis1, analysis2, ticker)
            return compiled_analysis
        
        return None
    
    def conclusion(self, compiled_analysis, ticker):
        """Aggregate and synthesize the results from all 10 articles."""
        prompt = f"""
        You are a stock analyst. Read each of the 10 articles one by one and provide a comprehensive analysis of the overall sentiment of the stock with ticker {ticker} and key points. Synthesize the individual analyses into a single, concise summary that captures the main insights and trends across all articles. Provide a final sentiment score for the collection of articles on a scale from -1 (very negative) to 1 (very positive), and give top 3 reasons why you gave that score. Your answer will strictly be a JSON object with keys: Sentiment Score, Reason 1, Reason 2, Reason 3. Do not deviate from this template, do not add anything else.

        Compiled Analyses:
        {compiled_analysis}

        High quality summary:
        """
        
        response = self.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            temperature=0.5,
            max_tokens=500,
        )
        try:
            return json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            return self.json_check(response.choices[0].message.content)

    
    #Ensures (or at least try to :P) output is always json format
    def json_check(self, output):
        """Ensure that the output is in JSON format."""
        
        try_counter = 0
        while try_counter < 3:
            print("Ouput of unexpected format. Reformatting to JSON format.")
        
        
            prompt = f"""
            You are to reformat the output into a JSON object. Ensure that the output is strictly in JSON format and nothing else. Do not change the content of the output, only the format. This is the output you need to reformat: {output}
            """
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.1-8b-instant",
                temperature=0.5,
                max_tokens=500,
            )
            try:
                return json.loads(response.choices[0].message.content)
            except json.JSONDecodeError:
                try_counter += 1
        
        return None

    

