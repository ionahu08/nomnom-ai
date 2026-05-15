from pydantic import Field
from mcp.server.fastmcp import FastMCP
    # Import the `FastMCP` class from the official MCP Python 
    # SDK (`mcp` is the package name maintained by Anthropic; 
from mcp.server.fastmcp.prompts import base

mcp = FastMCP("DocumentMCP", log_level="ERROR")
    # Create a FastMCP instance — this is the "server object" that
    # will host all my tools, resources, and prompts.

    # Parameter Meanin
    # `"DocumentMCP"` | The server's **unique identifier name** — what the MCP client sees when it connects. Shown in Claude Desktop configs, server inspector, debug logs. Like the storefront sign. |
    # `log_level="ERROR"` | How verbose the logs are. Only errors get printed; normal operational logs stay silent. |
        ### Log Levels (loud → quiet)
        ### DEBUG  →  INFO  →  WARNING  →  ERROR  →  CRITICAL
          # loudest                                  quietest

    # >  **Why `ERROR` matters**: In stdio mode, the MCP server 
    # communicates with the client through **stdout**. Any stray 
    # log output (`print()` statements, INFO-level logs) would 
    # **pollute the protocol channel** and break the connection. 
    # Setting `log_level="ERROR"` keeps stdout clean for protocol 
    # messages.

docs = {
    "deposition.md": "This deposition covers the testimony of Angela Smith, P.E.",
    "report.pdf": "The report details the state of a 20m condenser tower.",
    "financials.docx": "These financials outline the project's budget and expenditures.",
    "outlook.pdf": "This document presents the projected future performance of the system.",
    "plan.md": "The plan outlines the steps for the project's implementation.",
    "spec.txt": "These specifications define the technical requirements for the equipment.",
}

# TODO: Write a tool to read a doc
# The decorator specifies the tool name and description, while the function 
# parameters define the required arguments. The Field class from Pydantic 
# provides argument descriptions that help Claude understand what each 
# parameter expects.
@mcp.tool(
    name="read_doc_contents",
    description="Read the contents of a document and return it as a string."
)
def read_document(
    doc_id: str = Field(description="Id of the document to read")
):
    if doc_id not in docs:
        raise ValueError(f"Doc with id {doc_id} not found")
    
    return docs[doc_id]


# TODO: Write a tool to edit a doc
@mcp.tool(
    name="edit_document",
    description="Edit a document by replacing a string in the documents content with a new string."
)
def edit_document(
    doc_id: str = Field(description="Id of the document that will be edited"),
    old_str: str = Field(description="The text to replace. Must match exactly, including whitespace."),
    new_str: str = Field(description="The new text to insert in place of the old text.")
):
    if doc_id not in docs:
        raise ValueError(f"Doc with id {doc_id} not found")
    
    docs[doc_id] = docs[doc_id].replace(old_str, new_str)

# TODO: Write a resource to return all doc id's
@mcp.resource(
    "docs://documents",
    mime_type="application/json"
)
def list_docs() -> list[str]:
    return list(docs.keys())

# TODO: Write a resource to return the contents of a particular doc
@mcp.resource(
    "docs://documents/{doc_id}",
    mime_type="text/plain"
)
def fetch_doc(doc_id: str) -> str:
    if doc_id not in docs:
        raise ValueError(f"Doc with id {doc_id} not found")
    return docs[doc_id]


# TODO: Write a prompt to rewrite a doc in markdown format

@mcp.prompt(
    name="format",
    description="Rewrites the contents of the document in Markdown format."
)
def format_document(
    doc_id: str = Field(description="Id of the document to format")
) -> list[base.Message]:
    prompt = f"""
Your goal is to reformat a document to be written with markdown syntax.

The id of the document you need to reformat is:
<document_id>
{doc_id}
</document_id>

Add in headers, bullet points, tables, etc as necessary. Feel free to add in structure.
Use the 'edit_document' tool to edit the document. After the document has been reformatted...
"""
    
    return [
        base.UserMessage(prompt)
    ]


# TODO: Write a prompt to summarize a doc


if __name__ == "__main__":
    mcp.run(transport="stdio")
