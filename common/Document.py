from typing import List, Dict, Set, Union, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from common.Section import Section


class Document:
    def __init__(self, doc: dict) -> None:        
        self.doc: dict = doc
        self.visited_sections: Set[int] = set()
        self.root_sections: List["Section"] = []

    def build_trees(self) -> None:
        """
        Traverses through sections while keeping track of visited sections.
        Might produce multiple trees if not all of the sections interlock.
        """
        from common.Section import Section

        sections: List[dict] = self.doc["analyzeResult"]["sections"]
        for index, section in enumerate(sections):
            if index not in self.visited_sections:
                self.visited_sections.add(index)
                path: str = f"/sections/{index}"
                root_section: Section = Section(
                    path=path,
                    section=section,
                    doc=self.doc,
                    document=self,
                    index=index,
                    parent_headers=[],
                )
                self.root_sections.append(root_section)

    def get_chunks(
        self,
        sections: List["Section"] = None,
        all_chunks: Optional[List[Dict[str, Union[int, str]]]] = None,
    ) -> List[Dict[str, Union[int, str]]]:
        """
        Traverses the trees and extracts text and page number per section.
        """
        from common.Section import Section

        if sections is None:
            sections = self.root_sections
        if all_chunks is None:
            all_chunks = []
        for section in sections:
            chunk: Optional[Dict[str, Union[int, str]]] = section.get_chunk()
            if chunk:
                all_chunks.append(chunk)
            subsections: List["Section"] = [
                child for child in section.children if isinstance(child, Section)
            ]
            self.get_chunks(sections=subsections, all_chunks=all_chunks)
        return all_chunks
