import re
from typing import Optional
from app.memory.manager import memory_manager, memory_request_store, MemoryApprovalRequiredException

class MemoryCommandProcessor:
    @staticmethod
    async def process(message: str, session_id: str) -> Optional[str]:
        msg = message.strip().rstrip('.!? ')
        
        # 1. "Forget everything about SmartScan"
        m = re.match(r"^forget\s+everything\s+about\s+(.+)$", msg, re.IGNORECASE)
        if m:
            project_name = m.group(1).strip().strip('.')
            req = memory_request_store.create_request(
                category="PROJECT",
                key="forget_project",
                content=f"everything about {project_name}",
                project_id=project_name,
                session_id=session_id,
                question=f"Would you like me to forget everything about project '{project_name}'?",
                action="delete"
            )
            raise MemoryApprovalRequiredException(req)

        # 2. "Forget that I prefer TypeScript"
        m = re.match(r"^forget\s+that\s+(.+)$", msg, re.IGNORECASE)
        if m:
            target_content = m.group(1).strip().strip('.')
            mems = memory_manager.list_memories(status="ACTIVE")
            matched_mem = None
            for mem in mems:
                if target_content.lower() in mem["content"].lower():
                    matched_mem = mem
                    break
            
            if not matched_mem:
                return f"I couldn't find any memory matching '{target_content}'."
                
            req = memory_request_store.create_request(
                category=matched_mem["category"],
                key=matched_mem["key"],
                content=matched_mem["content"],
                project_id=matched_mem.get("project_id"),
                session_id=session_id,
                question=f"Would you like me to forget: '{matched_mem['content']}'?",
                action="delete"
            )
            raise MemoryApprovalRequiredException(req)

        # 3. "Remember that I prefer TypeScript"
        m = re.match(r"^remember\s+that\s+(.+)$", msg, re.IGNORECASE)
        if m:
            content = m.group(1).strip()
            content_lower = content.lower()
            category = "USER"
            project_id = None
            
            for proj in ["saarthi", "smartscan", "mks erp"]:
                if proj in content_lower:
                    category = "PROJECT"
                    project_id = proj.capitalize() if proj != "mks erp" else "MKS ERP"
                    break
                    
            key = MemoryCommandProcessor._generate_key(content)
            req = memory_request_store.create_request(
                category=category,
                key=key,
                content=content,
                project_id=project_id,
                session_id=session_id,
                question="Remember this information?",
                action="create"
            )
            raise MemoryApprovalRequiredException(req)

        # 4. "Remember this: Saarthi's source code is on E:\Saarthi"
        m = re.match(r"^remember\s+this:\s*(.+)$", msg, re.IGNORECASE)
        if m:
            content = m.group(1).strip()
            content_lower = content.lower()
            category = "USER"
            project_id = None
            
            for proj in ["saarthi", "smartscan", "mks erp"]:
                if proj in content_lower:
                    category = "PROJECT"
                    project_id = proj.capitalize() if proj != "mks erp" else "MKS ERP"
                    break
            
            key = MemoryCommandProcessor._generate_key(content)
            req = memory_request_store.create_request(
                category=category,
                key=key,
                content=content,
                project_id=project_id,
                session_id=session_id,
                question="Remember this information?",
                action="create"
            )
            raise MemoryApprovalRequiredException(req)

        # 5. "What do you remember about me?"
        m = re.match(r"^what\s+do\s+you\s+remember\s+about\s+me\??$", msg, re.IGNORECASE)
        if m:
            mems = memory_manager.list_memories(category="USER", status="ACTIVE")
            if not mems:
                return "I don't remember anything about you yet."
            lines = [f"- {mem['content']}" for mem in mems]
            return "Here is what I remember about you:\n" + "\n".join(lines)

        # 6. "What do you remember about Saarthi?" (or any project)
        m = re.match(r"^what\s+do\s+you\s+remember\s+about\s+(.+?)\??$", msg, re.IGNORECASE)
        if m:
            about_target = m.group(1).strip().strip('.')
            mems = memory_manager.list_memories(status="ACTIVE")
            matched_mems = []
            for mem in mems:
                if (mem.get("project_id") and mem["project_id"].lower() == about_target.lower()) or \
                   (about_target.lower() in mem["content"].lower()) or \
                   (about_target.lower() in mem["key"].lower()):
                    matched_mems.append(mem)
            if not matched_mems:
                return f"I don't remember anything about {about_target} yet."
            lines = [f"- {mem['content']}" for mem in matched_mems]
            return f"Here is what I remember about {about_target}:\n" + "\n".join(lines)

        # 7. "Show my project memories."
        m = re.match(r"^show\s+my\s+project\s+memories\??$", msg, re.IGNORECASE)
        if m:
            mems = memory_manager.list_memories(category="PROJECT", status="ACTIVE")
            if not mems:
                return "I don't have any project memories yet."
            lines = [f"- [{mem.get('project_id') or 'General'}] {mem['content']}" for mem in mems]
            return "Here are your project memories:\n" + "\n".join(lines)


        return None

    @staticmethod
    def _generate_key(content: str) -> str:
        words = re.findall(r"\w+", content.lower())
        if not words:
            return "memory"
        return "_".join(words[:4])
