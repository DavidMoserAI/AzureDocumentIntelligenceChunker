from typing import List

from common.Node import Node


class Paragraph(Node):
    def __init__(self, path: int, paragraph: dict):
        super().__init__(path=path, data=paragraph)

    def get_text(self) -> str:
        """
        Returns the content of the paragraph.
        """
        return self.data.get("content", "")
    
    def get_bounding_boxes(self) -> List[List[float]]:
        """
        Returns the bounding boxes of the paragraph.
        """
        bounding_regions: List[dict] = self.data.get("boundingRegions", [])
        all_polygons: List[List[float]] = [
            region["polygon"] for region in bounding_regions
        ]
        return all_polygons
