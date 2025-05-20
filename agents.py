import json
from fpdf import FPDF
from swarm import Agent

def PDF_maker(text_data, title):
    print("This is the PDF file maker")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    # for line in text_data.split("\n"):
    #     pdf.cell(200, 10, line , ln=True , align='L')
    pdf.multi_cell(200,10,text_data)
    pdf.output(f"{title}.pdf")

def document_maker(text_data, title):
    print("This is the Document file maker")
    print(text_data)
    name = title
    file = open(f"{name}.txt", "w+", encoding="utf-8")
    file.write(text_data)
    file.close()

pdf_maker = Agent(
    name="pdf agent",
    model = "qwen3:latest",
    instructions="You are a helpful agent that genertates data of PDF file, and uses the PDF function, dont give the python code, give the data in text format and put that into the PDF file",
    functions=[PDF_maker],
)

document_agent = Agent(
    name="document agent",
    model="qwen3:latest",
    instructions="You are a helpful agent that generates clean, formatted document text (not code), and uses the document maker function to create a text file. Do not give Python code only provide document text content.",
    functions=[document_maker],
)

triage_agent = Agent(
    name="Triage Agent",
    model = "qwen3:latest",
    instructions="You have to only determine the correct agent to use for the users request and transfer that to the required agent",
)


def transfer_back_to_triage():
    """Call this function if a user is asking about a topic that is not handled by the current agent."""
    return triage_agent



def transfer_to_document():
    '''Call this function if this user is asking to create a document'''
    return document_agent

def transfer_to_pdf():
    '''Call this function if this user is asking to create a PDF'''
    return pdf_maker


triage_agent.functions=[ transfer_to_document, transfer_to_pdf]
pdf_maker.functions.append(transfer_back_to_triage)
document_agent.functions.append(transfer_back_to_triage)

