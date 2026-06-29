"""
CortexOne Context Assembler

Version 2.0

Purpose
-------
Select only the most relevant documents for the current
founder request before sending them to the LLM.

This prevents huge prompts and keeps inference fast.
"""

from typing import List, Dict


class ContextAssembler:

    def __init__(self):

        #
        # Never send the whole repository
        #
        self.max_documents = 8

        #
        # Approx 10-15k characters
        #
        self.max_characters = 15000

        #
        # These documents are always important
        #
        self.core_keywords = [

            "constitution",
            "identity",
            "governance",
            "principles",
            "mission",
            "vision",
            "values"

        ]

    # =====================================================
    # Public API
    # =====================================================

    def assemble(

        self,

        executive_name: str,

        executive_os: List[Dict],

        executive_package: List[Dict],

        founder_request: str

    ) -> Dict:

        #
        # Always include core documents
        #

        selected = self._core_documents(executive_os)

        #
        # Add relevant Executive OS documents
        #

        selected.extend(

            self._rank_documents(

                executive_os,

                founder_request

            )

        )

        #
        # Add relevant Executive Package documents
        #

        selected.extend(

            self._rank_documents(

                executive_package,

                founder_request

            )

        )

        #
        # Remove duplicates
        #

        unique = {}

        for doc in selected:

            unique[doc["path"]] = doc

        selected = list(unique.values())

        #
        # Highest ranked only
        #

        selected = selected[: self.max_documents]

        prompt = self._build_prompt(

            executive_name,

            founder_request,

            selected

        )

        return {

            "executive": executive_name,

            "documents": selected,

            "prompt": prompt

        }

    # =====================================================
    # Core Documents
    # =====================================================

    def _core_documents(

        self,

        documents

    ):

        results = []

        for doc in documents:

            filename = doc["name"].lower()

            for keyword in self.core_keywords:

                if keyword in filename:

                    results.append(doc)

                    break

        return results

    # =====================================================
    # Rank Documents
    # =====================================================

    def _rank_documents(

        self,

        documents,

        founder_request

    ):

        words = [

            w.lower()

            for w in founder_request.split()

            if len(w) > 2

        ]

        ranked = []

        for doc in documents:

            score = 0

            searchable = (

                doc["name"]

                + " "

                + doc["content"][:5000]

            ).lower()

            for word in words:

                score += searchable.count(word)

            ranked.append(

                (

                    score,

                    doc

                )

            )

        ranked.sort(

            reverse=True,

            key=lambda x: x[0]

        )

        return [

            d

            for score, d in ranked

            if score > 0

        ]

    # =====================================================
    # Prompt Builder
    # =====================================================

    def _build_prompt(

        self,

        executive,

        founder_request,

        documents

    ):

        sections = []

        sections.append(

f"""You are the {executive.upper()} of CortexOne.

You MUST answer ONLY using the company knowledge supplied below.

If information is missing, clearly state that instead of inventing it.

Be concise.

Be executive.

Think before responding.

"""
        )

        sections.append(

f"""

========================
FOUNDER REQUEST
========================

{founder_request}

"""
        )

        sections.append(

"""

========================
COMPANY KNOWLEDGE
========================

"""
        )

        current_size = 0

        for doc in documents:

            text = doc["content"]

            #
            # Trim huge documents
            #

            if len(text) > 2500:

                text = text[:2500]

            if current_size + len(text) > self.max_characters:

                break

            current_size += len(text)

            sections.append(

f"""

--------------------------------------------------

FILE

{doc['relative_path']}

--------------------------------------------------

{text}

"""

            )

        sections.append(

"""

========================
END KNOWLEDGE
========================

Provide:

1. Executive Summary

2. Recommendations

3. Risks

4. Next Actions

"""

        )

        return "\n".join(sections)