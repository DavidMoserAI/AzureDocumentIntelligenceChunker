from typing import Dict, List, Optional

from common.Node import Node


class Table(Node):
    def __init__(self, path: str, table: Dict[str, any]):
        super().__init__(path=path, data=table)

    def get_text(self) -> str:
        """
        Extracts the table and turns it into markdown.
        """
        # Check if table contains a caption
        caption: str = self.data.get("caption", {}).get("content", "")
        caption_index: int = -1
        if caption:
            caption_index = int(
                self.data["caption"].get("elements", "")[0].split("/")[-1]
            )
        first_paragraph: Optional[str] = next(
            (
                cell.get("elements", [])[0]
                for cell in self.data["cells"]
                if cell.get("elements")
            ),
            None,
        )
        if first_paragraph:
            first_paragraph_index: int = int(first_paragraph.split("/")[-1])

        # Extract cells into markdown
        headers: List[str] = [
            f" {cell['content']} " if cell["content"] else " "
            for cell in self.data["cells"]
            if cell["rowIndex"] == 0
        ]
        header_row: str = f"|{'|'.join(headers)}|"
        separator_row: str = f"{'| - ' * len(headers)}|"
        data_rows: List[str] = [
            "|"
            + "|".join(
                f"{' ' if cell['content'] == '' else ' ' + cell['content'] + ' '}"
                for cell in self.data["cells"]
                if cell["rowIndex"] == row_index
            )
            + "|"
            for row_index in range(1, self.data["rowCount"])
        ]

        # Format table as text depending on where the caption is located
        table: str = "\n".join([header_row, separator_row] + data_rows)
        if caption_index < first_paragraph_index and caption_index != -1:
            return f"{caption}\n\n{table}"
        elif caption_index > first_paragraph_index:
            return f"{table}\n\n{caption}"
        else:
            return table
        
    def get_bounding_boxes(self) -> List[List[float]]:
        """
        Returns the bounding boxes of the table.
        """
        all_polygons: List[List[float]] = []

        # Collect the bounding regions of the caption
        caption_bounding_regions: List[dict] = self.data.get("caption", {}).get("boundingRegions", [])
        caption_polygons: List[float] = [region["polygon"] for region in caption_bounding_regions]

        # Collect the bounding regions of the table
        table_bounding_regions: List[dict] = self.data.get("boundingRegions", [])
        table_polygons: List[List[float]] = [region["polygon"] for region in table_bounding_regions]

        # Combine the bounding regions of the caption and the table
        all_polygons.extend(caption_polygons)
        all_polygons.extend(table_polygons)
        return all_polygons
