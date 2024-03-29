import gradio as gr
import requests
# Defining System Prompts for Each Document Type
SYSTEM_PROMPTS = {
    "Zeugnisse": "Please enter the employee's name, the date of the certificate, their performance rating, key skills, and position. Add any additional remarks as needed.",
    "Abmahnung": "Please enter the employee's name, the date of the warning, a brief description of the incident, possible consequences, and any previous warnings. Add any additional remarks as needed.",
    "Jubiläum": "Please enter the employee's name, the date of the anniversary, the length of their service, significant contributions or achievements, and a personal message or note. Add any additional remarks as needed."
}
def send_request_to_llm(document_type, name, date, detail1, detail2, detail3, detail4):
    # URL for the local LLM server
    url = "https://api.together.xyz/v1/chat/completions"
    
    # Constructing the prompt based on document type and provided details
    prompt = f"{document_type} für {name}, Datum: {date}. "
    if document_type == "Zeugnisse":
        prompt += f"Leistungsbewertung: {detail1}, Fähigkeiten: {detail2}, Position: {detail3}. Zusätzliche Bemerkungen: {detail4}"
    elif document_type == "Abmahnung":
        prompt += f"Vorfall: {detail1}, Konsequenzen: {detail2}, Vorherige Verwarnungen: {detail3}. Zusätzliche Bemerkungen: {detail4}"
    elif document_type == "Jubiläum":
        prompt += f"Klinge enthusiastisch! Dienstjahre: {detail1}, Achievements: {detail2}, Persönliche Nachricht: {detail3}. Zusätzliche Bemerkungen: {detail4}"
    
    # Preparing data for the POST request
    data = {
    "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
    "temperature": 0.7,
    "messages": [
        {"role": "system", "content": "Schreibe ein " + document_type + " f+r " + name + " am " + date + ". Sei so detailliert wie möglich. Antworte immer in vollständigen DEUTSCHEN Sätzen. Sei ausdrucksstark und vermeide Wiederholungen. "},
            {
                "role":"user",
    "content": prompt,
            }]
        }
    headers = {
        "Authorization": "Bearer 649cc8a63fe72e596207ad8e8ce409d63494dae61c1818f06fa99c226d53e970",  # Replace with your actual token
        # Add other headers if needed
    }
    # Sending POST request to the local LLM server and returning the completion
    response = requests.post(url, json=data, headers=headers)
    result = response.json()

    return SYSTEM_PROMPTS[document_type], result.get("choices")[0].get("message").get("content") if result.get("choices") else "Error in generation"



# Create the Gradio Blocks interface
with gr.Blocks(    theme=gr.themes.Soft(),
    head='<link rel="icon" type="image/x-icon" href="https://d11wkw82a69pyn.cloudfront.net/style%20library/images/favicon.ico?rev=20231201095823"/> <style> font-family: Futura,Trebuchet MS,Arial,sans-serif !important; </style>',
    css="#dlt_btn {background-color: #b30000} #send_btn {background-color: #006400} #refresh-button { max-width: 32px } footer div {visibility: hidden}  footer a {visibility: hidden} ", 
    title="Huacaya AI Suite") as demo:
    gr.HTML(" <div style=\"display: flex; align-items: center; justify-content: center;margin-top:3%; margin-bottom:2%\"><img src='https://upload.wikimedia.org/wikipedia/commons/d/d4/Logo_w%C3%B6hner.svg' width='500' />")
    with gr.Row():
        with gr.Column():
            with gr.Row():
                document_type = gr.Dropdown(label="Dokumententyp wählen", choices=["Zeugnisse", "Abmahnung", "Jubiläum"])
            with gr.Row():
                name = gr.Textbox(label="Name")
                date = gr.Textbox(label="Date (e.g., '05.02.2023')")
            with gr.Row():
                detail1 = gr.Textbox(label="Detail 1")
                detail2 = gr.Textbox(label="Detail 2")
            with gr.Row():
                detail3 = gr.Textbox(label="Detail 3")
                detail4 = gr.Textbox(label="Detail 4")
            with gr.Row():
                system_prompt = gr.Textbox(label="System Prompt", interactive=False)
                generate_button = gr.Button("Generate")
                clear_button = gr.Button("Clear")
        with gr.Column():
            output = gr.Textbox(label="Generated Text")

    # Function to update details based on document type
    def clear_fields():
        document_type = gr.Dropdown(label="Dokumententyp wählen", choices=["Zeugnisse", "Abmahnung", "Jubiläum"],value="")
        name = gr.Textbox(label="Name",value="")
        date = gr.Textbox(label="Date (e.g., '05.02.2023')",value="")
        detail1 = gr.Textbox(label="Detail 1",value="")
        detail2 = gr.Textbox(label="Detail 2",value="")
        detail3 = gr.Textbox(label="Detail 3",value="")
        detail4 = gr.Textbox(label="Detail 4",value="")
        output = gr.Textbox(label="Generated Text",value="")
        system_prompt = gr.Textbox(label="System Prompt", interactive=False, value="")
        return document_type,name,date,detail1, detail2, detail3, detail4, output,system_prompt
    # Function to update details based on document type
    def update_details(document_type):
        if document_type not in SYSTEM_PROMPTS:  # Handle None or unexpected value
            document_type = "Zeugnisse"  # Defaul
        labels = {
            "Zeugnisse": ["Leistungsbewertung", "Fähigkeiten", "Position", "Zusätzliche Bemerkungen"],
            "Abmahnung": ["Vorfall", "Konsequenzen", "Vorherige Verwarnungen", "Zusätzliche Bemerkungen"],
            "Jubiläum": ["Dienstjahre", "Beiträge", "Persönliche Nachricht", "Zusätzliche Bemerkungen"]
        }.get(document_type, ["Detail 1", "Detail 2", "Detail 3", "Detail 4"])  # Default case
        detail1 = gr.Textbox(label=labels[0])
        detail2 = gr.Textbox(label=labels[1])
        detail3 = gr.Textbox(label=labels[2])
        detail4 = gr.Textbox(label=labels[3])
        system_prompt = gr.Textbox(label="System Prompt", interactive=False, value="System Prompt: " + SYSTEM_PROMPTS[document_type])
        return detail1, detail2, detail3, detail4, system_prompt
    document_type.change(fn=update_details, inputs=[document_type], outputs=[detail1, detail2, detail3, detail4, system_prompt])
    generate_button.click(send_request_to_llm, inputs=[document_type, name, date, detail1, detail2, detail3, detail4], outputs=[system_prompt, output])
    clear_button.click(fn=clear_fields,outputs=[document_type,name,date,detail1, detail2, detail3, detail4, output,system_prompt])

demo.launch(auth=("woehner","woehner"),server_port=5000,share=True,server_name="0.0.0.0")