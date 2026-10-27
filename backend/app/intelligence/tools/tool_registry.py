from typing import Dict, Any, List, Optional
from app.intelligence.tools.tool_definition import ToolDefinition, RiskLevel

TOOLS_CATALOG: Dict[str, ToolDefinition] = {
    # File Operations
    "file.read": ToolDefinition(
        id="file.read",
        name="Read Local File",
        description="Reads contents of a local document or text file safely.",
        input_schema={"type": "object", "properties": {"file_path": {"type": "string"}}, "required": ["file_path"]},
        required_capability="tools.files",
        risk_level=RiskLevel.READ_ONLY,
        requires_confirmation=False,
        operation_type="OBSERVATION"
    ),
    "file.search": ToolDefinition(
        id="file.search",
        name="Search Local Files",
        description="Searches directory files for keyword matches.",
        input_schema={"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
        required_capability="tools.files",
        risk_level=RiskLevel.READ_ONLY,
        requires_confirmation=False,
        operation_type="OBSERVATION"
    ),
    "file.write": ToolDefinition(
        id="file.write",
        name="Write Local File",
        description="Writes content to a file in the workspace sandbox.",
        input_schema={"type": "object", "properties": {"file_path": {"type": "string"}, "content": {"type": "string"}}, "required": ["file_path", "content"]},
        required_capability="tools.files",
        risk_level=RiskLevel.MODERATE,
        requires_confirmation=False,
        operation_type="ACTION"
    ),
    "file.move": ToolDefinition(
        id="file.move",
        name="Move Local File",
        description="Moves or renames a file within the sandbox directory.",
        input_schema={"type": "object", "properties": {"source_path": {"type": "string"}, "destination_path": {"type": "string"}}, "required": ["source_path", "destination_path"]},
        required_capability="tools.files",
        risk_level=RiskLevel.MODERATE,
        requires_confirmation=False,
        operation_type="ACTION"
    ),
    "file.copy": ToolDefinition(
        id="file.copy",
        name="Copy Local File",
        description="Copies a file to a new destination within the sandbox.",
        input_schema={"type": "object", "properties": {"source_path": {"type": "string"}, "destination_path": {"type": "string"}}, "required": ["source_path", "destination_path"]},
        required_capability="tools.files",
        risk_level=RiskLevel.LOW_RISK,
        requires_confirmation=False,
        operation_type="ACTION"
    ),
    "file.delete": ToolDefinition(
        id="file.delete",
        name="Delete Local File",
        description="Permanently deletes a file within the sandbox. Requires explicit approval.",
        input_schema={"type": "object", "properties": {"file_path": {"type": "string"}}, "required": ["file_path"]},
        required_capability="tools.files",
        risk_level=RiskLevel.HIGH_RISK,
        requires_confirmation=True,
        operation_type="ACTION"
    ),
    "file.organize": ToolDefinition(
        id="file.organize",
        name="Organize Directory Files",
        description="Organizes files in a target directory by categorized subfolders.",
        input_schema={"type": "object", "properties": {"directory": {"type": "string"}}, "required": ["directory"]},
        required_capability="tools.files",
        risk_level=RiskLevel.MODERATE,
        requires_confirmation=False,
        operation_type="ACTION"
    ),

    # Web & Browser Operations
    "browser.search": ToolDefinition(
        id="browser.search",
        name="Web Search",
        description="Searches public web literature and grounding sources.",
        input_schema={"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
        required_capability="tools.search",
        risk_level=RiskLevel.READ_ONLY,
        requires_confirmation=False,
        operation_type="OBSERVATION"
    ),
    "browser.navigate": ToolDefinition(
        id="browser.navigate",
        name="Browser Navigate",
        description="Navigates to a validated external HTTP/HTTPS URL.",
        input_schema={"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]},
        required_capability="tools.search",
        risk_level=RiskLevel.LOW_RISK,
        requires_confirmation=False,
        operation_type="OBSERVATION"
    ),
    "browser.inspect": ToolDefinition(
        id="browser.inspect",
        name="Browser Inspect Page",
        description="Inspects DOM structure, headings, links, and forms of the current page.",
        input_schema={"type": "object", "properties": {"url": {"type": "string"}}},
        required_capability="tools.search",
        risk_level=RiskLevel.READ_ONLY,
        requires_confirmation=False,
        operation_type="OBSERVATION"
    ),
    "browser.extract": ToolDefinition(
        id="browser.extract",
        name="Browser Extract Content",
        description="Extracts structured text, tables, or citations from a web page.",
        input_schema={"type": "object", "properties": {"url": {"type": "string"}, "selector": {"type": "string"}}},
        required_capability="tools.search",
        risk_level=RiskLevel.READ_ONLY,
        requires_confirmation=False,
        operation_type="OBSERVATION"
    ),
    "browser.interact": ToolDefinition(
        id="browser.interact",
        name="Browser Interact",
        description="Performs permitted web actions such as clicking an element or submitting form inputs.",
        input_schema={"type": "object", "properties": {"url": {"type": "string"}, "action": {"type": "string"}, "selector": {"type": "string"}, "value": {"type": "string"}}, "required": ["action", "selector"]},
        required_capability="tools.browser",
        risk_level=RiskLevel.MODERATE,
        requires_confirmation=False,
        operation_type="ACTION"
    ),

    # Desktop Computer Control Foundation
    "desktop.observe": ToolDefinition(
        id="desktop.observe",
        name="Observe Active Desktop",
        description="Observes active application name, window title, focused control, and selected text.",
        input_schema={"type": "object", "properties": {}},
        required_capability="tools.computer_control",
        risk_level=RiskLevel.READ_ONLY,
        requires_confirmation=False,
        operation_type="OBSERVATION"
    ),
    "desktop.capture_screenshot": ToolDefinition(
        id="desktop.capture_screenshot",
        name="Capture Desktop Screenshot",
        description="Captures a screenshot of the display or active window for multimodal comprehension.",
        input_schema={"type": "object", "properties": {"scope": {"type": "string", "default": "active_window"}}},
        required_capability="tools.computer_control",
        risk_level=RiskLevel.READ_ONLY,
        requires_confirmation=False,
        operation_type="OBSERVATION"
    ),
    "desktop.insert_text": ToolDefinition(
        id="desktop.insert_text",
        name="Insert Text into Active App",
        description="Inserts synthesized text directly into the focused desktop field. Protects credential managers.",
        input_schema={"type": "object", "properties": {"text": {"type": "string"}, "target_app": {"type": "string"}}, "required": ["text"]},
        required_capability="tools.computer_control",
        risk_level=RiskLevel.MODERATE,
        requires_confirmation=False,
        operation_type="ACTION"
    ),
    "desktop.interact": ToolDefinition(
        id="desktop.interact",
        name="Desktop UI Interaction",
        description="Executes permitted desktop UI actions such as window focus or keystroke.",
        input_schema={"type": "object", "properties": {"action": {"type": "string"}, "target": {"type": "string"}}, "required": ["action"]},
        required_capability="tools.computer_control",
        risk_level=RiskLevel.MODERATE,
        requires_confirmation=True,
        operation_type="ACTION"
    ),

    # Document Generation
    "document.generate_report": ToolDefinition(
        id="document.generate_report",
        name="Generate Structured Report Document",
        description="Generates a structured research report, project plan, or summary document in the workspace.",
        input_schema={"type": "object", "properties": {"title": {"type": "string"}, "content": {"type": "string"}, "doc_type": {"type": "string"}, "output_filename": {"type": "string"}}, "required": ["title", "content"]},
        required_capability="documents.analysis",
        risk_level=RiskLevel.LOW_RISK,
        requires_confirmation=False,
        operation_type="ACTION"
    ),
    "document.verify": ToolDefinition(
        id="document.verify",
        name="Verify Document Integrity",
        description="Verifies that a generated document exists on disk, is non-empty, and has valid structure.",
        input_schema={"type": "object", "properties": {"file_path": {"type": "string"}}, "required": ["file_path"]},
        required_capability="documents.analysis",
        risk_level=RiskLevel.READ_ONLY,
        requires_confirmation=False,
        operation_type="OBSERVATION"
    ),

    # Research Synthesis & Evidence
    "research.synthesize": ToolDefinition(
        id="research.synthesize",
        name="Synthesize Research Evidence",
        description="Synthesizes research findings across sources with evidence classes: FACT, SOURCE-DERIVED, INFERENCE, UNCERTAIN.",
        input_schema={"type": "object", "properties": {"sources": {"type": "array"}, "topic": {"type": "string"}}, "required": ["topic"]},
        required_capability="research.multi_source",
        risk_level=RiskLevel.READ_ONLY,
        requires_confirmation=False,
        operation_type="OBSERVATION"
    ),
    "research.multi_source": ToolDefinition(
        id="research.multi_source",
        name="Multi-Source Research Search",
        description="Searches literature across arXiv and PubMed.",
        input_schema={"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
        required_capability="research.multi_source",
        risk_level=RiskLevel.READ_ONLY,
        requires_confirmation=False,
        operation_type="OBSERVATION"
    ),

    # Multimodal Agents
    "multimodal.analyze_screenshot": ToolDefinition(
        id="multimodal.analyze_screenshot",
        name="Analyze Desktop Screenshot",
        description="Performs OCR and visual understanding on captured screenshots. Treats content as untrusted.",
        input_schema={"type": "object", "properties": {"image_path": {"type": "string"}}, "required": ["image_path"]},
        required_capability="multimodal.documents",
        risk_level=RiskLevel.READ_ONLY,
        requires_confirmation=False,
        operation_type="OBSERVATION"
    ),
    "multimodal.process_document": ToolDefinition(
        id="multimodal.process_document",
        name="Process Multimodal Document",
        description="Extracts structured text and layout from PDF or document images safely.",
        input_schema={"type": "object", "properties": {"file_path": {"type": "string"}}, "required": ["file_path"]},
        required_capability="multimodal.documents",
        risk_level=RiskLevel.READ_ONLY,
        requires_confirmation=False,
        operation_type="OBSERVATION"
    ),

    # Code Execution & Terminal
    "code.execute": ToolDefinition(
        id="code.execute",
        name="Execute Python Code",
        description="Runs Python code in a local sandboxed environment.",
        input_schema={"type": "object", "properties": {"code": {"type": "string"}}, "required": ["code"]},
        required_capability="tools.code_execution",
        risk_level=RiskLevel.MODERATE,
        requires_confirmation=True,
        operation_type="ACTION"
    ),
    "terminal.execute": ToolDefinition(
        id="terminal.execute",
        name="Run Terminal Command",
        description="Executes a system shell command with explicit confirmation.",
        input_schema={"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]},
        required_capability="tools.terminal",
        risk_level=RiskLevel.HIGH_RISK,
        requires_confirmation=True,
        operation_type="ACTION"
    ),

    # Communication
    "email.draft": ToolDefinition(
        id="email.draft",
        name="Draft Email Letter",
        description="Synthesizes a professional email draft.",
        input_schema={"type": "object", "properties": {"recipient": {"type": "string"}, "subject": {"type": "string"}, "body": {"type": "string"}}},
        required_capability="tools.email",
        risk_level=RiskLevel.LOW_RISK,
        requires_confirmation=False,
        operation_type="ACTION"
    ),
    "email.send": ToolDefinition(
        id="email.send",
        name="Send Email Message",
        description="Sends an email message to external recipient. Strictly requires server-side approval.",
        input_schema={"type": "object", "properties": {"recipient": {"type": "string"}, "subject": {"type": "string"}, "body": {"type": "string"}}, "required": ["recipient", "subject", "body"]},
        required_capability="tools.email",
        risk_level=RiskLevel.HIGH_RISK,
        requires_confirmation=True,
        operation_type="ACTION"
    ),

    # Career Domain Tools
    "career.analyze_jd": ToolDefinition(
        id="career.analyze_jd",
        name="Analyze Job Description",
        description="Extracts requirements and matches evidence for a JD.",
        input_schema={"type": "object", "properties": {"jd_text": {"type": "string"}}, "required": ["jd_text"]},
        required_capability="career.jd_analysis",
        risk_level=RiskLevel.READ_ONLY,
        requires_confirmation=False,
        operation_type="OBSERVATION"
    ),
    "career.tailor_resume": ToolDefinition(
        id="career.tailor_resume",
        name="Tailor Resume truthful Diffs",
        description="Generates truthful resume diff patches matching JD requirements.",
        input_schema={"type": "object", "properties": {"jd_text": {"type": "string"}, "company": {"type": "string"}, "role": {"type": "string"}}},
        required_capability="career.resume_tailoring",
        risk_level=RiskLevel.READ_ONLY,
        requires_confirmation=False,
        operation_type="ACTION"
    ),
    "career.prepare_interview": ToolDefinition(
        id="career.prepare_interview",
        name="Generate Interview Questions",
        description="Generates targeted interview prep questions.",
        input_schema={"type": "object", "properties": {"jd_text": {"type": "string"}, "company": {"type": "string"}, "role": {"type": "string"}}},
        required_capability="career.interview_prep",
        risk_level=RiskLevel.READ_ONLY,
        requires_confirmation=False,
        operation_type="ACTION"
    ),
    "career.salary_analysis": ToolDefinition(
        id="career.salary_analysis",
        name="Analyze Salary & Offer Strategy",
        description="Calculates compensation breakdown and counter-offer draft.",
        input_schema={"type": "object", "properties": {"company": {"type": "string"}, "role": {"type": "string"}, "base_salary": {"type": "number"}}},
        required_capability="career.salary_coach",
        risk_level=RiskLevel.READ_ONLY,
        requires_confirmation=False,
        operation_type="OBSERVATION"
    ),

    # Routine & Workspace Tools
    "workspace.projects": ToolDefinition(
        id="workspace.projects",
        name="Review Project Workspace",
        description="Reviews active projects for blockers and status.",
        input_schema={"type": "object", "properties": {"scope": {"type": "string"}}},
        required_capability="workspace.projects",
        risk_level=RiskLevel.READ_ONLY,
        requires_confirmation=False,
        operation_type="OBSERVATION"
    ),
    "core.briefing": ToolDefinition(
        id="core.briefing",
        name="Generate Personalized Briefing",
        description="Synthesizes personalized morning or evening briefing.",
        input_schema={"type": "object", "properties": {"style": {"type": "string"}}},
        required_capability="core.chat.basic",
        risk_level=RiskLevel.READ_ONLY,
        requires_confirmation=False,
        operation_type="OBSERVATION"
    ),
    "task.review": ToolDefinition(
        id="task.review",
        name="Review Unfinished Tasks",
        description="Inspects pending tasks and deadlines.",
        input_schema={"type": "object", "properties": {"scope": {"type": "string"}}},
        required_capability="core.chat.basic",
        risk_level=RiskLevel.READ_ONLY,
        requires_confirmation=False,
        operation_type="OBSERVATION"
    ),
    "career.goals": ToolDefinition(
        id="career.goals",
        name="Review Career Goals",
        description="Evaluates progress toward career goals and milestones.",
        input_schema={"type": "object", "properties": {"scope": {"type": "string"}}},
        required_capability="career.goals",
        risk_level=RiskLevel.READ_ONLY,
        requires_confirmation=False,
        operation_type="OBSERVATION"
    ),
    "task.remind": ToolDefinition(
        id="task.remind",
        name="Dispatch Task Reminders",
        description="Dispatches reminders for important unfinished items.",
        input_schema={"type": "object", "properties": {"filter": {"type": "string"}}},
        required_capability="core.chat.basic",
        risk_level=RiskLevel.READ_ONLY,
        requires_confirmation=False,
        operation_type="ACTION"
    ),
    "routine.action": ToolDefinition(
        id="routine.action",
        name="Routine Action Execution",
        description="Executes a general routine action step.",
        input_schema={"type": "object", "properties": {"action_type": {"type": "string"}}},
        required_capability="agents.routines",
        risk_level=RiskLevel.READ_ONLY,
        requires_confirmation=False,
        operation_type="ACTION"
    )
}

class ToolRegistry:
    @staticmethod
    def list_tools() -> List[Dict[str, Any]]:
        return [t.model_dump() for t in TOOLS_CATALOG.values()]

    @staticmethod
    def get_tool(tool_id: str) -> Optional[ToolDefinition]:
        return TOOLS_CATALOG.get(tool_id)
