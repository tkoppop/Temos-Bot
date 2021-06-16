import random
import json
from pathlib import Path
from contextlib import contextmanager
from typing import Generator
import discord
import config


def data_path(path: object) -> str:
    return f"data/{path}"


class User:

    def __init__(self, user: discord.User) -> None:
        self.user: discord.User = user
        self.id: int = self.user.id  
        self.path: str = data_path(str(self.id)) 
        self.infoPath: str = self.location("Info.json")
        self.economyPath: str = self.location("Economy.json")

    def location(self, path: object) -> str:
        return f"{self.path}/{path}"

    def verify(self) -> None:
        if not Path(self.path).is_dir():
            Path(self.path).mkdir()
        with open(self.infoPath, "w") as file:
            json.dump({"id": self.id, "name": self.user.name}, file)

    def verify_economy(self) -> None:
        self.verify()
        economyData = {}
        try:
            with open(self.economyPath, "r") as file:
                economyData = json.load(file)
        except FileNotFoundError:
            pass

        for key in config.economy.attributes:
            if key not in economyData:
                economyData[key] = 0

        stockData = {}
        try:
            stockData = economyData["stocks"]
        except KeyError:
            pass

        for key in config.stocks.items:
            if key not in stockData:
                stockData[key] = 0

        economyData["stocks"] = stockData
        with open(self.economyPath, "w") as file:
            json.dump(economyData, file)

    @contextmanager
    def open_economy(self) -> Generator[dict, None, None]:
        self.verify_economy()
        data = {}
        with open(self.economyPath, "r") as file:
            data = json.load(file)
        try:
            yield data
        finally:
            with open(self.economyPath, "w") as file:
                json.dump(data, file)


class Stocks:
    def __init__(self) -> None:
        self.path: str = data_path("stocks.json")

    def verify(self) -> None:
        stockData = {}
        try:
            with open(self.path, "r") as file:
                stockData = json.load(file)
        except FileNotFoundError:
            pass
        for stock in config.stocks.items:
            if stock not in stockData:
                stockData[stock] = config.stocks.standard

        with open(self.path, "w") as file:
            json.dump(stockData, file)

    @contextmanager
    def open(self) -> Generator[dict, None, None]:
        self.verify()
        data = {}
        with open(self.path, "r") as file:
            data = json.load(file)
        try:
            yield data
        finally:
            with open(self.path, "w") as file:
                json.dump(data, file)

    def update(self) -> None:
        self.verify()
        with self.open() as data:
            for stock in data:
                data[stock] += random.randint(
                    -config.stocks.change,
                    config.stocks.change
                )