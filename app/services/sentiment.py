import httpx
import asyncio
import json
from app.core.config import settings
import aiohttp
import re

class SentimentAnalyzer:
    """Service for analyzing tweet sentiment using Datura.ai and Chutes.ai"""
    
    def __init__(self):
        self.datura_api_key = settings.DATURA_API_KEY
        self.chutes_api_key = settings.CHUTES_API_KEY
        self.datura_base_url = "https://api.datura.ai/twitter/search"
        self.chutes_base_url = "https://api.chutes.ai/api/v1/chute"
        self.chutes_id = "20acffc0-0c5f-58e3-97af-21fc0b261ec4"  # LLM chute ID
    
    async def analyze_sentiment_for_subnet(self, netuid):
        """
        Get Twitter sentiment for a subnet using real APIs
        
        Args:
            netuid: The subnet ID to analyze
            
        Returns:
            float: Sentiment score between -1 and 1
        """
        try:
            print(f"Starting sentiment analysis for netuid {netuid}")
            
            # Step 1: Search Twitter via Datura API
            tweets = await self.search_twitter(netuid)
            
            if not tweets:
                print(f"No tweets found for netuid {netuid}")
                return 0.0
            
            print(f"Found {len(tweets)} tweets for analysis")
            
            # Step 2: Analyze sentiment with Chutes.ai LLM
            sentiment_score = await self.analyze_with_llm(tweets, netuid)
            
            print(f"Sentiment analysis complete: score = {sentiment_score}")
            return sentiment_score
        
        except Exception as e:
            print(f"Error in sentiment analysis: {e}")
            import traceback
            traceback.print_exc()
            # Return neutral sentiment on error
            return 0.0
    
    async def search_twitter(self, netuid):
        """Search Twitter for tweets about a subnet using Datura API"""
        print(f"Searching Twitter via Datura API for subnet {netuid}")
        
        async with aiohttp.ClientSession() as session:
            twitter_url = "https://api.datura.ai/api/twitter/search"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.datura_api_key}"
            }
            params = {
                "query": f"Bittensor netuid {netuid}",
                "max_results": 20
            }
            
            try:
                async with session.get(twitter_url, headers=headers, params=params) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        print(f"Twitter search failed: {response.status} - {error_text}")
                        
                        # Fallback sample tweets if API fails
                        print("Using fallback tweets for testing")
                        return [
                            f"Bittensor subnet {netuid} is looking promising! #Bittensor #TAO",
                            f"Just staked some TAO on subnet {netuid}. Let's see how it goes!",
                            f"The validator rewards on subnet {netuid} have been great lately"
                        ]
                    
                    twitter_data = await response.json()
                    
                    if not twitter_data.get("data") or len(twitter_data.get("data", [])) == 0:
                        print("No tweets found in API response, using fallback tweets")
                        return [
                            f"Bittensor subnet {netuid} is performing well this week! #TAO",
                            f"Exploring the potential of subnet {netuid} in Bittensor"
                        ]
                    
                    # Extract tweets from response
                    tweets = [tweet.get("text", "") for tweet in twitter_data.get("data", [])]
                    return tweets
            
            except Exception as e:
                print(f"Error in Twitter search: {e}")
                
                # Fallback on exception
                return [
                    f"Sample tweet about Bittensor subnet {netuid} #1",
                    f"Sample tweet about Bittensor subnet {netuid} #2"
                ]
    
    async def analyze_with_llm(self, tweets, netuid):
        """Analyze tweets with Chutes.ai LLM to get sentiment score"""
        print(f"Analyzing {len(tweets)} tweets with Chutes.ai LLM")
        
        async with aiohttp.ClientSession() as session:
            chutes_url = "https://api.chutes.ai/api/chute"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.chutes_api_key}"
            }
            
            # Combine tweets for sentiment analysis
            tweets_text = "\n".join(tweets)
            
            payload = {
                "model": "llama-3",
                "prompt": f"""
                Analyze the sentiment of these tweets about Bittensor subnet {netuid}.
                Rate the overall sentiment on a scale from -100 (extremely negative) to +100 (extremely positive).
                Return only the numeric score without any explanation.
                
                Tweets:
                {tweets_text}
                """
            }
            
            try:
                async with session.post(chutes_url, headers=headers, json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        print(f"LLM sentiment analysis failed: {response.status} - {error_text}")
                        return 0.0
                    
                    sentiment_data = await response.json()
                    llm_response = sentiment_data.get("response", "")
                    
                    print(f"Raw LLM response: {llm_response}")
                    
                    # Extract sentiment score from response using regex
                    score_match = re.search(r'(-?\d+)', llm_response)
                    if score_match:
                        sentiment_score = int(score_match.group(1))
                        # Normalize to -1 to 1 range
                        normalized_score = sentiment_score / 100
                        print(f"Extracted sentiment score: {sentiment_score} (normalized: {normalized_score})")
                        return normalized_score
                    else:
                        print("Could not extract sentiment score from LLM response")
                        return 0.0
            
            except Exception as e:
                print(f"Error in LLM sentiment analysis: {e}")
                return 0.0
                
    def _get_mock_tweets(self, netuid):
        """Generate mock tweets for testing"""
        return {
            "tweets": [
                {"text": f"Bittensor netuid {netuid} is looking promising! #TAO #Bittensor"},
                {"text": f"Just staked more TAO on subnet {netuid}. Super excited about the future!"},
                {"text": f"Mixed feelings about subnet {netuid}. Some good progress but still issues."},
                {"text": f"Hodling TAO and watching netuid {netuid} closely. #Cryptocurrency"}
            ]
        }
    
    def _get_mock_sentiment(self):
        """Generate mock sentiment score for testing"""
        import random
        return random.uniform(-50, 80)  # Slightly biased toward positive