import inspect
from typing import Dict, Type, TypeVar, Protocol, Generic, NewType, Optional

from fastapi import Depends, FastAPI, File, Form
from pydantic import BaseModel, validator, BaseSettings, Json

app = FastAPI()

StringId = NewType("StringId", str)


def as_form(cls: Type[BaseModel]):
    """
    Adds an as_form class method to decorated models. The as_form class method
    can be used with FastAPI endpoints
    """
    new_params = [
        inspect.Parameter(
            field.alias,
            inspect.Parameter.POSITIONAL_ONLY,
            default=(Form(field.default) if not field.required else Form(...)),
        )
        for field in cls.__fields__.values()
    ]

    async def _as_form(**data):
        return cls(**data)

    sig = inspect.signature(_as_form)
    sig = sig.replace(parameters=new_params)
    _as_form.__signature__ = sig
    setattr(cls, "as_form", _as_form)
    return cls


@as_form
class DatasetForm(BaseModel):
    name: str
    comment: Optional[str] = ""
    fetal_fraction_preface: float
    fetal_fraction_y_for_trisomy: float
    fetal_fraction_y_max: float
    fetal_fraction_y_min: float
    fetal_fraction_XXX: float
    fetal_fraction_X0: float
    y_axis_min: float
    y_axis_max: float
    k_upper: float
    k_lower: float
    m_lower: float
    m_upper: float
    trisomy_soft_max: float
    trisomy_hard_max: float
    trisomy_hard_min: float
