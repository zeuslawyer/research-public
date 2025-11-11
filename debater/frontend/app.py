import gradio as gr
import requests
import json
from typing import Optional, Tuple, List

# Configuration
BACKEND_URL = "http://localhost:9000"  # Update this for production

# Available models
AVAILABLE_MODELS = {
    "claude": ["claude-sonnet-4-5-20250929", "claude-3-5-sonnet-20241022"],
    "gpt": ["gpt-4o", "gpt-4-turbo"],
    "gemini": ["gemini-2.0-flash-exp", "gemini-1.5-pro"]
}

ALL_MODELS = AVAILABLE_MODELS["claude"] + AVAILABLE_MODELS["gpt"] + AVAILABLE_MODELS["gemini"]


def create_debate(
    proposition: str,
    for_model: str,
    against_model: str,
    anthropic_key: str,
    openai_key: str,
    gemini_key: str
) -> Tuple[str, str, str]:
    """Create a new debate and return debate_id"""
    if not proposition:
        return "", "Please enter a proposition", ""

    if not for_model or not against_model:
        return "", "Please select models for both sides", ""

    # Validate API keys
    api_keys = {
        "anthropic": anthropic_key,
        "openai": openai_key,
        "gemini": gemini_key
    }

    try:
        response = requests.post(
            f"{BACKEND_URL}/debate/create",
            json={
                "proposition": proposition,
                "for_model": for_model,
                "against_model": against_model
            }
        )
        response.raise_for_status()
        data = response.json()
        debate_id = data["debate_id"]

        return debate_id, f"Debate created! ID: {debate_id}", json.dumps(api_keys)

    except requests.exceptions.RequestException as e:
        return "", f"Error creating debate: {str(e)}", ""


def start_debate(debate_id: str, api_keys_json: str) -> Tuple[str, str]:
    """Start the debate and return the transcript"""
    if not debate_id:
        return "No debate created yet", ""

    try:
        api_keys = json.loads(api_keys_json)

        response = requests.post(
            f"{BACKEND_URL}/debate/{debate_id}/start",
            json=api_keys
        )
        response.raise_for_status()
        data = response.json()

        # Format the debate transcript
        transcript = format_debate_transcript(data)

        return transcript, "Debate completed! You can now adjudicate."

    except requests.exceptions.RequestException as e:
        return f"Error starting debate: {str(e)}", ""
    except json.JSONDecodeError:
        return "Error: Invalid API keys", ""


def format_debate_transcript(debate_data: dict) -> str:
    """Format debate messages into a readable transcript"""
    proposition = debate_data["proposition"]
    for_model = debate_data["for_model"]
    against_model = debate_data["against_model"]

    transcript = f"# Debate: {proposition}\n\n"
    transcript += f"**FOR**: {for_model}\n"
    transcript += f"**AGAINST**: {against_model}\n\n"
    transcript += "---\n\n"

    for i, msg in enumerate(debate_data["messages"], 1):
        role_label = "🟢 FOR" if msg["role"] == "for_agent" else "🔴 AGAINST"
        transcript += f"### Turn {(i + 1) // 2} - {role_label}\n\n"
        transcript += f"{msg['content']}\n\n"
        transcript += "---\n\n"

    return transcript


def adjudicate_debate(
    debate_id: str,
    adjudicator_model: str,
    api_keys_json: str
) -> str:
    """Adjudicate the debate and return results"""
    if not debate_id:
        return "No debate to adjudicate"

    if not adjudicator_model:
        return "Please select an adjudicator model"

    try:
        api_keys = json.loads(api_keys_json)

        response = requests.post(
            f"{BACKEND_URL}/debate/{debate_id}/adjudicate",
            params={"adjudicator_model": adjudicator_model},
            json={
                "adjudicator_model": adjudicator_model,
                **api_keys
            }
        )
        response.raise_for_status()
        result = response.json()

        # Format adjudication results
        output = "# 🏆 Adjudication Results\n\n"
        output += f"**Winner**: {result['winner'].upper()}\n\n"
        output += f"**FOR Score**: {result['for_score']}/100\n\n"
        output += f"**AGAINST Score**: {result['against_score']}/100\n\n"
        output += f"## Reasoning\n\n{result['reasoning']}\n"

        return output

    except requests.exceptions.RequestException as e:
        return f"Error adjudicating debate: {str(e)}"
    except json.JSONDecodeError:
        return "Error: Invalid API keys"


def check_models_selected(for_model: str, against_model: str) -> bool:
    """Check if both models are selected to enable the start button"""
    return bool(for_model and against_model)


# Create Gradio Interface
with gr.Blocks(title="AI Debate System", theme=gr.themes.Soft()) as app:
    gr.Markdown("# 🎭 AI Debate System")
    gr.Markdown("Watch AI models debate each other on any proposition!")

    # Hidden state to store debate_id and API keys
    debate_id_state = gr.State("")
    api_keys_state = gr.State("")

    with gr.Row():
        with gr.Column():
            gr.Markdown("### 🔑 API Keys")
            gr.Markdown("Enter your API keys for the models you want to use:")

            anthropic_key = gr.Textbox(
                label="Anthropic API Key",
                type="password",
                placeholder="sk-ant-..."
            )
            openai_key = gr.Textbox(
                label="OpenAI API Key",
                type="password",
                placeholder="sk-..."
            )
            gemini_key = gr.Textbox(
                label="Google Gemini API Key",
                type="password",
                placeholder="AI..."
            )

    gr.Markdown("---")

    # Proposition input
    proposition_input = gr.Textbox(
        label="Debate Proposition",
        placeholder="Enter the debate topic (e.g., 'Artificial Intelligence will be net positive for humanity')",
        lines=2
    )

    gr.Markdown("### Select Models for Each Side")

    # Model selection row
    with gr.Row():
        with gr.Column():
            gr.Markdown("#### 🟢 FOR the Motion")
            for_model_dropdown = gr.Dropdown(
                choices=ALL_MODELS,
                label="Select Model (FOR)",
                info="This model will argue FOR the proposition"
            )

        with gr.Column():
            gr.Markdown("#### 🔴 AGAINST the Motion")
            against_model_dropdown = gr.Dropdown(
                choices=ALL_MODELS,
                label="Select Model (AGAINST)",
                info="This model will argue AGAINST the proposition"
            )

    # Create and Start buttons
    with gr.Row():
        create_btn = gr.Button("Create Debate", variant="secondary", size="lg")
        start_btn = gr.Button("Start Debate", variant="primary", size="lg", interactive=False)

    status_output = gr.Textbox(label="Status", interactive=False)

    gr.Markdown("---")

    # Debate transcript
    gr.Markdown("### 📜 Debate Transcript")
    transcript_output = gr.Markdown("")

    gr.Markdown("---")

    # Adjudication section
    gr.Markdown("### ⚖️ Adjudication")
    with gr.Row():
        adjudicator_dropdown = gr.Dropdown(
            choices=ALL_MODELS,
            label="Select Adjudicator Model",
            info="This model will judge the debate"
        )
        adjudicate_btn = gr.Button("Adjudicate Debate", variant="primary")

    adjudication_output = gr.Markdown("")

    # Event handlers
    def on_create_debate(prop, for_m, against_m, ant_key, oai_key, gem_key):
        debate_id, status, keys_json = create_debate(
            prop, for_m, against_m, ant_key, oai_key, gem_key
        )
        # Enable start button if debate created successfully
        start_enabled = bool(debate_id)
        return debate_id, status, keys_json, gr.update(interactive=start_enabled)

    create_btn.click(
        fn=on_create_debate,
        inputs=[
            proposition_input,
            for_model_dropdown,
            against_model_dropdown,
            anthropic_key,
            openai_key,
            gemini_key
        ],
        outputs=[debate_id_state, status_output, api_keys_state, start_btn]
    )

    def on_start_debate(debate_id, keys_json):
        transcript, status = start_debate(debate_id, keys_json)
        return transcript, status

    start_btn.click(
        fn=on_start_debate,
        inputs=[debate_id_state, api_keys_state],
        outputs=[transcript_output, status_output]
    )

    adjudicate_btn.click(
        fn=adjudicate_debate,
        inputs=[debate_id_state, adjudicator_dropdown, api_keys_state],
        outputs=[adjudication_output]
    )

    gr.Markdown("---")
    gr.Markdown("""
    ### 📝 How to Use
    1. **Enter API Keys**: Provide API keys for the model providers you want to use
    2. **Enter Proposition**: Type the debate topic
    3. **Select Models**: Choose models for FOR and AGAINST positions
    4. **Create Debate**: Click to initialize the debate
    5. **Start Debate**: Begin the 5-turn debate (each side gets 5 turns)
    6. **Adjudicate**: After completion, select a judge model and get the verdict

    ### 🔧 Backend Configuration
    Make sure the FastAPI backend is running at: `{}`
    """.format(BACKEND_URL))


if __name__ == "__main__":
    app.launch(
        server_name="0.0.0.0",
        server_port=8000,
        share=False
    )
