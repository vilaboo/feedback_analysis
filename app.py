import streamlit as st
import pandas as pd
import google.generativeai as genai
import numpy as np

# Initialize the client
genai.configure(api_key="AIzaSyC2ngziHY2mFK7_epi4U-gzNqq0BQ1pW4s")

generation_config = {
  "temperature":0,
  "top_p": 1,
  "top_k": 1,
  "max_output_tokens": 2048
}

llm = genai.GenerativeModel(model_name="gemini-pro", generation_config=generation_config)

template = """
Please analyze the customer feedback on their service experience, in a few words, come up with the next best course of action to improve the customer's experience or Net Promoter Score to be returned as 'Next Actions'. The 'Next Actions' are not mutually exclusive, and a single feedback may lead to multiple 'Next Actions' joined by '; ', but the 'Next Actions' should be as few and concise as possible and please limit the number of 'Next Actions' to be three or the fewer the better. If you are unable to come up with any 'Next Actions', return as 'Not Applicable'.

Some non-exhaustive examples of customer feedbacks and their respective 'Next Actions':
- Feedbacks like "lousy" should be returned with "Provide better service" as its 'Next Actions'.
- Feedbacks like "Took me sometime to figure out how to submit claim, the layout is not easily understood" should be returned with "Improve UI/UX for claim submission; Provide guidance for claim submission" as its 'Next Actions'.
- Feedbacks like "I claim $1200 premium increase 100%" should be returned with "Provide fair rates; Provide justification for premium increase" as its 'Next Actions'.
- Non-meaningful feedbacks like "yes", "No", "na", "Nil", "Nothing", "no comment", "not applicable" or "N/A" etc should be returned with "Not Applicable" as its 'Next Actions'.

Feedback: "{feedback}"
Next Actions:
"""

def analyze_sentiment(feedback, explanation):
    if pd.isna(feedback) or feedback.strip() == '':
        return ''
    explanation_text = 'short explanation:' if explanation else 'no explanation'

    # Configure the sentiment analysis prompt or question with the explanation text
    question = f"Analyze the sentiment of this customer feedback: '{feedback}'\n{explanation_text}"

    try:
        # Call Gemini Pro model to analyze the sentiment
        response = llm.generate_content(question)  # Replace with the correct method
        result = response.text.strip()
        return result

    except Exception as e:
        print(f"Error processing row: {e}")
        return np.nan

def action(feedback):
    if pd.isna(feedback) or feedback.strip() == '':
        return ''

    prompt = template.format(feedback=feedback)

    try:
        # Call Gemini Pro model to generate the next best actions
        response = llm.generate_content(prompt)  # Replace with the correct method
        result = response.text.strip()
        actions = result.split('Next Actions:')[-1]
        actions = actions.strip()
        return actions

    except Exception as e:
        print(f"Error processing row: {e}")
        return np.nan

st.title('Feedback Analysis with Gemini Pro')

uploaded_file = st.file_uploader("Choose an excel file", type='xlsx')

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    if set(['DateTime', 'UserID', 'Feedback']).issubset(df.columns):
        df['Sentiment'] = df['Feedback'].apply(lambda x: analyze_sentiment(x, explanation=False))
        df['Next Actions'] = df['Feedback'].apply(action)
        st.write(df)
        st.markdown(f'<a href="data:application/octet-stream;base64,{df.to_csv(index=False).encode().to_base64()}" download="output.csv">Download output CSV</a>', unsafe_allow_html=True)
    else:
        st.error("Uploaded file does not have the required columns: 'DateTime', 'UserID', 'Feedback'")
