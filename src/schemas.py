from typing import List, Optional, Union, Any, Dict
from pydantic import BaseModel, Field, validator

# --- Legacy KPI Card Contract (v2025) ---
class KPICard(BaseModel):
    label: str
    value: str
    delta: Optional[str] = None
    color: str = Field(default="standard", description="Semantics: red, green, blue, standard")
    tooltip_data: Optional[str] = None

# --- Semantic Cube v2026 Contract ---

class IndicatorInternal(BaseModel):
    label: str
    value: Union[str, float, int]
    delta: Optional[str] = None
    status: Optional[str] = "standard" # CRITICAL, WARNING, SUCCESS, NEUTRAL
    tooltip: Optional[str] = None
    is_percentage: Optional[bool] = False

class MetricFormat(BaseModel):
    """Format metadata for metrics (from backend registry)"""
    unit_type: str  # "count" | "percentage" | "currency"
    symbol: Optional[str] = None  # None, "%", "S/", "$"
    decimals: int = 2  # Precision

class Dataset(BaseModel):
    label: str
    data: List[Union[float, int, None]]
    type: Optional[str] = None # 'line', 'bar' override
    color: Optional[str] = None
    format: Optional[MetricFormat] = None  # ✨ NEW: Dynamic formatting

class ChartPayload(BaseModel):
    labels: List[str]
    datasets: List[Dataset]
    tooltip_datasets: Optional[List[Dataset]] = None

class TablePayload(BaseModel):
    headers: List[str]
    rows: List[Union[List[Any], Dict[str, Any]]]

# --- Block Types ---
class TextBlockPayload(BaseModel):
    text: str 

class BlockMetadata(BaseModel):
    title: Optional[str] = None
    y_axis_label: Optional[str] = None
    show_legend: Optional[bool] = True
    x_axis: Optional[str] = None        # Legacy/Bridge
    series_names: Optional[Dict[str, str]] = None # Legacy/Bridge

# --- Visual Component Blocks ---
class VisualBlock(BaseModel):
    id: Optional[str] = None # Unique ID from backend (e.g., 'header_title_193502')
    type: str # discriminator: KPI_ROW, CHART, TABLE, etc.
    subtype: Optional[str] = None # LINE, BAR, PIE
    
    # Flexible payload to support both V1 (Legacy) and V2 (Semantic Cube)
    # V2: List[IndicatorInternal], ChartPayload, TablePayload
    # V1: List[KPICard], Dict (DataSeries), List[Dict] (Table)
    payload: Union[
        ChartPayload, 
        TablePayload, 
        List[IndicatorInternal], 
        List[KPICard], 
        Dict[str, Any], 
        str, 
        List[Any]
    ]
    
    metadata: Optional[Dict[str, Any]] = {}
    variant: Optional[str] = "standard"
    severity: Optional[str] = "info" # For TEXT blocks

    @validator('type')
    def known_type(cls, v):
        # V2 Types: KPI_ROW, CHART, TABLE
        # V1 Types: kpi_row, plot, table, data_series, debug_sql, talent_matrix, text
        allowed = [
            "KPI_ROW", "CHART", "TABLE", 
            "text", "kpi_row", "plot", "table", "data_series", "debug_sql", "talent_matrix"
        ]
        if v not in allowed:
            return v 
        return v

# --- Main Package ---
class VisualDataPackage(BaseModel):
    response_type: str = "visual_package"
    summary: Optional[str] = None
    content: List[VisualBlock]
