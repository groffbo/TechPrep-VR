import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
# This import is correct for the 'google-genai' package 
# (which you must install with pip install google-genai)
from google import genai 
from google.genai import types # Import the types module to access GenerationConfig

# --- INTERVIEW SCRIPT CONTENT (SYSTEM INSTRUCTION) ---
# This block sets the model's role as the INTERVIEWER and embeds the structured agenda.
INTERVIEW_SCRIPT_INSTRUCTION = """
You are a highly skilled and challenging technical interviewer focusing on Binary Search Trees (BSTs).
Your role is the Interviewer. The user is the Candidate.

**Persona Rules:**
1.  **Tone:** Maintain a **neutral, challenging, and concise** tone. Respond in short sentences. Do not offer praise or hints.
2.  **Goal:** Guide the candidate through all points listed in the Agenda. Your primary goal is to assess depth of understanding, not just correctness.
3.  **Flexibility:** Do NOT rigidly follow the agenda line-by-line. Instead, use the listed points as a **structured checklist**.
4.  **Reaction:**
    * **If the candidate's answer is incomplete or vague:** Ask a short, probing follow-up question to challenge the candidate or probe for more depth (e.g., "Elaborate on that," or "What are the edge cases?").
    * **If the candidate introduces a tangent:** Acknowledge it briefly and gently pivot back to the current agenda topic (e.g., "That's interesting, but let's focus on the validation strategy for now.").
    * **Once a specific Agenda Point is sufficiently addressed:** Move naturally to the next point in the list.

**Interview Agenda (Points to Cover in Order):**

1.  Initial Greeting. (Start with: "Thank you for joining us. We will now proceed to a medium-difficulty technical problem.")
2.  Problem Statement (BST Validation) and Structural Constraints.
3.  High-level strategy (Identify if recursive, iterative, etc.).
4.  Challenge/Flaw of simple recursive check (Identify the local vs. global constraint issue, e.g., challenge with the (10, 5, 15) example).
5.  Refining the signature (Adapt function to track min/max bounds).
6.  Initial and Subtree Constraints (Define the initial global range and the precise constraints passed to left/right subtrees).
7.  Implementation (Request the full code solution).
8.  Runtime Challenge (Challenge the code with a test case, e.g., negative numbers or specific edge cases).
9.  Final Time Complexity (Request and justification of the O(N) complexity).
10. Conclusion (End with: "Thank you for attending this interview.").

Begin the interview now.
"""

# --- Setup and Initialization ---

# Initialize global variables for client and chat session
client = None
chat_session = None

# Load environment variables from .env file (looks for GEMINI_API_KEY)
load_dotenv() 

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    # Use a print statement instead of a hard crash (raise) in web app setup
    print("FATAL ERROR: GEMINI_API_KEY not found in environment!")

# Initialize the GenAI Client and Chat Session
try:
    # 1. Initialize the client
    client = genai.Client(api_key=api_key)
    
    # 2. Create the configuration object to pass the system instruction
    config = types.GenerateContentConfig(
        system_instruction=INTERVIEW_SCRIPT_INSTRUCTION
    )
    
    # 3. Create a global chat session that includes the system instruction
    # The Chat object automatically manages conversation history.
    chat_session = client.chats.create(
        model="gemini-2.5-flash", 
        config=config
    )
    print("Gemini chat session initialized successfully.")
    
except Exception as e:
    # Handle initialization error gracefully
    print(f"Error initializing Gemini client or chat session: {e}")
    client = None
    chat_session = None

app = Flask(__name__)

@app.route("/api/interview", methods=["POST"])
def query():
    """
    Handles POST requests to query the Gemini model using the persistent chat session.
    """
    # Check if both client and chat session are ready
    if not client or not chat_session:
        return jsonify({"error": "Gemini API client or chat session not initialized. Check server logs and API key."}), 503

    # Safely extract the 'text' field from the request JSON
    data = request.json or {}
    user_input = data.get("text", "")

    if not user_input:
        # Prevent calling the API with genuinely empty input
        return jsonify({"error": "No text provided in the 'text' field."}), 400

    try:
        # Use the persistent chat session to send the message. 
        # The history is automatically included.
        response = chat_session.send_message(user_input)
        
        # Access the text property of the response object
        return jsonify({"reply": response.text})

    except Exception as e:
        # Log the full exception for debugging
        print(f"An error occurred during API call: {e}")
        # Return a 500 server error response
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

if __name__ == "__main__":
    # Runs the Flask development server
    app.run(host="0.0.0.0", port=8000, debug=True)
