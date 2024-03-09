from __future__ import annotations
from aiogram.types import BufferedInputFile
from typing import List

from loguru import logger

from src.database.models import UserModel, NotifModel, ScheduleModel

import csv
import io
from datetime import datetime, timezone


async def convert_to_csv(objects, type_: str) -> BufferedInputFile:

    types = {
        "users": UserModel,
        "notifs": NotifModel,
        "schedule": ScheduleModel
    }

    if type_ not in types:
        raise ValueError(f"Type {type_} is not supported")

    model = types[type_]

    if not hasattr(model, '__table__'):
        raise ValueError(f"Model {model} Error")

    if objects:
        columns = objects[0].__table__.columns.keys()
    else:
        columns = []

    csv_data = io.StringIO()
    writer = csv.DictWriter(csv_data, fieldnames=columns)
    writer.writeheader()

    for obj in objects:
        row = {col: getattr(obj, col, '') for col in columns}
        writer.writerow(row)

    csv_data.seek(0)

    return BufferedInputFile(
        file=csv_data.getvalue().encode("utf-8"),
        filename=f"{type_}_{datetime.now(timezone.utc).strftime('%Y.%m.%d_%H.%M')}.csv",
    )
