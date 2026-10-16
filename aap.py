from bs4 import BeautifulSoup
from google import genai
import streamlit as st
import requests

# Page Configuration
st.set_page_config(
    page_title="AI Support & Web Scraping Agent", page_icon="🤖", layout="centered"
)

# Initialize Gemini Client
try:
  client = genai.Client()
except Exception as e:
  st.error(
      "Failed to initialize Gemini Client. Please check your API Key. Error:"
      f" {e}"
  )


def read_website_content(url):
  """Specific website se text data extract karne ke liye function"""
  try:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
    }
    response = requests.get(url, headers=headers, timeout=10)
    if response.status_code == 200:
      soup = BeautifulSoup(response.text, "html.parser")
      for script in soup(["script", "style", "nav", "footer"]):
        script.extract()
      text = soup.get_text(separator=" ", strip=True)
      return text[:8000]
    else:
      return None
  except Exception as e:
    return None


# UI Header
st.title("🤖 AI Customer Support & Research Agent")
st.markdown(
    "Yeh agent kisi bhi website ko read karke uske base par aapke sawalon ke"
    " jawab dega!"
)

# Sidebar for Configuration
with st.sidebar:
  st.header("⚙️ Agent Settings")
  website_url = st.text_input(
      "Target Website URL",
      placeholder="https://example.com",
      help="Jis website ka data read karwana hai uska link yahan dalein.",
  )

  if st.button("Clear Chat History"):
    st.session_state.messages = []
    st.rerun()

  st.markdown("---")
  st.markdown("**Powered by:** Google Gemini & Streamlit")

# Initialize Chat History
if "messages" not in st.session_state:
  st.session_state.messages = []

# Display Chat History
for message in st.session_state.messages:
  with st.chat_message(message["role"]):
    st.markdown(message["content"])

# User Input Box
if user_query := st.chat_input("Apna sawal yahan puchein..."):
  if not website_url:
    st.warning("⚠️ Pehle sidebar mein koi valid Target Website URL toh daalo!")
  else:
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
      st.markdown(user_query)

    with st.chat_message("assistant"):
      with st.spinner("Agent website read kar raha hai aur soch raha hai..."):
        scraped_data = read_website_content(website_url)

        if not scraped_data:
          response_text = (
              "❌ Sorry, main yeh website read nahi kar paaya. Kripya URL"
              " check karein ya koi aur website try karein."
          )
        else:
          prompt = f"""
                    You are an expert, professional, and friendly Customer Support AI Agent.
                    Your primary job is to answer the user's questions strictly based on the provided website data below.
                    If the answer is not available in the website data, politely inform the user and use your general knowledge to provide a helpful alternative response.

                    --- WEBSITE CONTEXT START ---
                    {scraped_data}
                    --- WEBSITE CONTEXT END ---

                    User's Question: {user_query}

                    Answer in a clean, structured, and helpful format:
                    """

          try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )
            response_text = response.text
          except Exception as e:
            response_text = (
                f"⚠️ Error generating response with Gemini API: {e}"
            )

        st.markdown(response_text)

    st.session_state.messages.append(
        {"role": "assistant", "content": response_text}
    )
