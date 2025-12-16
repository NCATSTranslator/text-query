from __future__ import annotations
from unnamed.enums import ConfidenceLevels
from unnamed.enums import Personas
from pydantic import ConfigDict
from pydantic import BaseModel
from pydantic import Field

class ConfiguredBase(BaseModel):
  model_config: ConfigDict = ConfigDict(
    str_strip_whitespace=True,
    validate_assignment=True,
    use_enum_values=True,
    extra="forbid",
    populate_by_name=True,
  )

class Request(ConfiguredBase):
  persona: Personas = Field(Personas.GENERAL_PUBLIC)
  content: str = Field(..., max_length=1_500)

class Response(ConfiguredBase):
  """Knowledge Graph Derived Biomedical Hypothesis."""
  confidence: ConfidenceLevels = Field(ConfidenceLevels.VERY_UNCONFIDENT, description="Analysis Of Confidence In Hypothesis In Response.")
  content: str = Field(..., description="Textual Response To User.")

class Context(ConfiguredBase):
  persona: Personas = Field(Personas.GENERAL_PUBLIC)
