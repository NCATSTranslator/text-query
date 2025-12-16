from __future__ import annotations
from enum import Enum

class Personas(str, Enum):
  RESEARCHER = "researcher"
  CLINICIAN = "clinician"
  GENERAL_PUBLIC = "general public"

class ConfidenceLevels(str, Enum):
  VERY_CONFIDENT = "very confident"
  CONFIDENT = "confident"
  SOMEWHAT_CONFIDENT = "somewhat confident"
  UNCONFIDENT = "unconfident"
  VERY_UNCONFIDENT = "very unconfident"
