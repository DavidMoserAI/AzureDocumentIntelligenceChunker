from typing import List, Optional

from common.Node import Node


class Figure(Node):
    def __init__(self, path: int, doc: dict, figure: dict) -> None:
        super().__init__(path=path, data=figure)
        self.doc: dict = doc

    def get_text(self) -> str:
        """
        Turns the figure contents into the proper format.
        """
        paragraph_paths: List[str] = self.data.get("elements", [])
        index: int = -1
        caption: Optional[dict] = self.data.get("caption")

        # Remove caption from list if existent to later inject it at the right place
        if caption:
            caption_path: Optional[str] = caption.get("elements", [None])[0]
            caption_text: Optional[str] = self.data.get("caption", {}).get("content", None)
            if caption_path in paragraph_paths:
                index = paragraph_paths.index(caption_path)
                paragraph_paths.pop(index)

        # Merge all content excluding the caption
        content: str = " ".join(
            self.doc["analyzeResult"]["paragraphs"][int(path.split("/")[-1])].get(
                "content", ""
            )
            for path in paragraph_paths
        )

        # Format figure as text depending on where the caption was located
        if index == 0:
            return f"<figure>\n\n<figcaption>\n\n{caption_text}\n\n</figcaption>\n\n![]({self.path})\n\n{content}\n\n</figure>"
        elif index > 0:
            return f"<figure>\n\n![]({self.path})\n\n{content}\n\n<figcaption>\n\n{caption_text}\n\n</figcaption>\n\n</figure>"
        else:
            return f"<figure>\n\n![]({self.path})\n\n{content}\n\n</figure>"

    def get_bounding_boxes(self) -> List[List[float]]:
        """
        Extracts the bounding boxes of the figure.
        """
        all_polygons: List[List[float]] = []

        # Collect the bounding regions of the caption
        caption_bounding_regions: List[dict] = self.data.get("caption", {}).get("boundingRegions", [])
        caption_polygons: List[List[float]] = [region["polygon"] for region in caption_bounding_regions]

        # Collect the bounding regions of the table
        figure_bounding_regions: List[dict] = self.data.get("boundingRegions", [])
        figure_polygons: List[List[float]] = [region["polygon"] for region in figure_bounding_regions]

        # Combine the bounding regions of the caption and the table
        all_polygons.extend(caption_polygons)
        all_polygons.extend(figure_polygons)
        return all_polygons
