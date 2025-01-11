from typing import List, Union, Dict, Optional, TYPE_CHECKING

from common.Node import Node
from common.Table import Table
from common.Paragraph import Paragraph
from common.Figure import Figure
if TYPE_CHECKING:
    from common.Document import Document


class Section(Node):
    def __init__(
        self,
        path: str,
        section: dict,
        doc: dict,
        document: "Document",
        index: int,
        parent_headers: Optional[List[str]] = None,
    ) -> None:
        super().__init__(path=path, data=section)
        self.section: dict = section
        self.doc: dict = doc
        self.page: Optional[int] = self._get_page_number()
        self.children: List[Union[Section, Table, Figure, Paragraph]] = []
        self.parent_headers: List[str] = parent_headers.copy() if parent_headers else []
        self.current_header: Optional[str] = self._get_current_header()
        self._build_subtree(document=document)
        document.visited_sections.add(index)

    def _get_page_number(self) -> Optional[int]:
        """
        Returns the page number of the sections header.
        """
        return next(
            (
                item["boundingRegions"][0].get("pageNumber", "")
                for item in self.doc["analyzeResult"]["paragraphs"]
                if item["spans"][0]["offset"] == self.section["spans"][0]["offset"]
            ),
            None,
        )

    def _get_current_header(self) -> Optional[str]:
        """
        Returns the header of the current section.
        """
        return next(
            (
                paragraph.get("content", "")
                for paragraph in self.doc["analyzeResult"]["paragraphs"]
                if paragraph["spans"][0]["offset"] == self.section["spans"][0]["offset"]
            ),
            None,
        )

    def _build_subtree(self, document: "Document") -> None:
        """
        Constructs the subtree for a document section by iterating over its elements.
        Adds the corresponding child objects based on the element type.
        """
        for element_path in self.section.get("elements", []):
            element_type, element_id = element_path.split("/")[-2:]
            element_id: int = int(element_id)
            if element_type == "paragraphs":
                paragraph: dict = self.doc["analyzeResult"]["paragraphs"][element_id]
                self.add_child(Paragraph(path=element_path, paragraph=paragraph))
            elif element_type == "sections":
                section: dict = self.doc["analyzeResult"]["sections"][element_id]
                child_headers: List[str] = self.parent_headers.copy() + [self.current_header]
                self.add_child(
                    Section(
                        path=element_path,
                        section=section,
                        doc=self.doc,
                        document=document,
                        index=element_id,
                        parent_headers=child_headers,
                    )
                )
            elif element_type == "tables":
                table: dict = self.doc["analyzeResult"]["tables"][element_id]
                self.add_child(Table(path=element_path, table=table))
            elif element_type == "figures":
                figure: dict = self.doc["analyzeResult"]["figures"][element_id]
                self.add_child(Figure(path=element_path, doc=self.doc, figure=figure))

    def add_child(
        self, child: Union["Section", Table, Figure, Paragraph]
    ) -> None:
        """
        Adds children to a section. Children can be sections, tables, figures, or paragraphs.
        """
        self.children.append(child)

    def _has_content(self) -> bool:
        """
        Determines if the section contains more content than its own header and other sections.
        """
        elements: List[str] = self.section.get("elements", [])
        if not elements:
            return False

        # Get the header paragraph
        first_paragraph: Optional[str] = next(
            (element for element in elements if element.startswith("/paragraphs/")),
            None,
        )
        first_paragraph_id: int = int(first_paragraph.split("/")[-1])
        paragraphs: List[Dict[str, Union[str, int]]] = self.doc["analyzeResult"].get("paragraphs", [])
        header: Dict[str, Union[str, int]] = paragraphs[first_paragraph_id]

        # Check for elements that are not header paragraphs
        if (
            header
            and header.get("role") == "sectionHeading"
            or header.get("role") == "title"
        ):
            non_section_elements: List[str] = [
                element for element in elements if not element.startswith("/sections/")
            ]
            if len(non_section_elements) == 1:
                return False
        return True

    def get_chunk(self) -> Optional[Dict[str, Union[int, str]]]:
        if self._has_content():
            chunk: str = "\n\n".join(
                [
                    child.get_text()
                    for child in self.children
                    if isinstance(child, (Table, Figure, Paragraph))
                ]
            )
            bounding_boxes: List[List[float]] = [
                box
                for child in self.children
                if isinstance(child, (Table, Figure, Paragraph))
                for box in child.get_bounding_boxes()
            ]
            full_text: str = "\n".join(self.parent_headers + [chunk])
            return {"page": self.page, "chunk": full_text, "bboxes": bounding_boxes}
        else:
            return None
