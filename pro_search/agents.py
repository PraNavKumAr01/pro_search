from datetime import date
from groq import Groq

class GroqClient:
    def __init__(self, api_key):
        self.client = Groq(api_key=api_key)

    def generate_context(self, user_query, summaries):
        """
        Aggregate multiple website summaries and generate a comprehensive context
        to help answer the user's original query.

        Args:
            user_query (str): The original user's query
            summaries (list): A list of summarized content from different sources

        Returns:
            str: A comprehensive, synthesized context that provides useful 
                 information for addressing the user query
        """
        try:
            system_message = (
                "You are an advanced research assistant specializing in synthesizing "
                "information from multiple sources. Your task is to:"
                "1. Carefully review all provided summaries"
                "2. Identify key themes, overlapping information, and unique insights"
                "3. Create a coherent, well-structured context that provides "
                "   comprehensive background information"
                "4. Ensure the generated context is directly relevant to the original query"
                "5. Maintain objectivity and stick closely to the source material"
                "6. Do not directly answer the query, but provide context that "
                "   would help someone understand the topic deeply"
            )

            user_message = (
                f"Original User Query: '{user_query}'\n\n"
                "Summaries from Multiple Sources:\n"
                + "\n\n".join(f"Source {i+1}:\n{summary}" for i, summary in enumerate(summaries))
                + "\n\nPlease synthesize these summaries into a comprehensive, "
                "well-structured context that provides depth and clarity."
            )

            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                model="llama-3.1-8b-instant",
                temperature=0.5, 
            )

            synthesized_context = chat_completion.choices[0].message.content.strip()
            return synthesized_context

        except Exception as e:
            print(f"Error during summary aggregation: {e}")
            return None

    def generate_content_summary(self, user_query, site_content):
        try:
            system_message = (
                "You are an assistant that specializes in formatting and summarizing unstructured web content. "
                "Your task is to take scraped content from web pages and reorganize it into a clear, concise, and well-written summary. "
                "Try not to add too much information on your own or add useless context. Stick to what is provided in the scraped content, "
                "occasionally adding some information if absolutely necessary."
                "Do not directly answer the user query but ensure the formatted content provides useful context that could support answering it."
            )

            user_message = (
                f"Here is the user query for context: '{user_query}'. "
                f"Below is the scraped site content: \n\n{site_content}\n\n"
                "Please format the site content into a well-written and structured summary."
            )

            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                model="llama-3.1-8b-instant",
                temperature=0.6,
            )

            res = chat_completion.choices[0].message.content.strip()
            return res

        except Exception as e:
            print(f"Error occurred: {e}")
            return None

    def generate_search_query(self, user_query):
        try:

            today = date.today()
            formatted_date = today.strftime("%B %d, %Y")

            system_message = (
                "You are an assistant that specializes in refining user queries into effective search queries. "
                "Your task is to take the user's input and convert it into a precise and optimized query suitable for search engines. "
                f"If the query involves events, results, or time-sensitive information, include the current date (e.g., {formatted_date}) to ensure relevance. Use the year usually, unless and untill month and date are also neccesary"
                "Return only the search query and nothing else, no text before or after that."
            )

            user_message = (
                f"User's original query: '{user_query}'. "
                "Please rewrite this as a more effective search query while incorporating the current date if applicable."
            )

            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                model="llama-3.1-8b-instant",
                temperature=0.5,
            )

            res = chat_completion.choices[0].message.content.strip()
            return res

        except Exception as e:
            print(f"Error occurred: {e}")
            return None
