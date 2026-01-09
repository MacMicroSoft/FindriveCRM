from .models import *
from django.db.models import Sum, Count
from typing import Literal
import pandas as pd
from pprint import pprint



class AnalysManager:
    car_qr_list: list[dict] = [
        {
            **item,
            "created_at": item["created_at"].strftime("%d.%m.%Y"),
            "created_at_my": item["created_at"].strftime("%m.%Y"),
        }
        for item in Car.objects.values()
    ]
    pd_car_data  = pd.DataFrame(car_qr_list)

    def __init__(self, car: Car):
        self.car = car


    @classmethod
    def all_cars_count(cls) -> int:
        return len(cls.car_qr_list)
    

    @staticmethod
    def get_cars_per_status(cars: list[dict], status: Literal[CarStatusChoice.ACTIVE, CarStatusChoice.AWAIT]) -> list[Car]:
        return [car for car in cars if car.get('status') == status]


    @classmethod
    def status_cars_count(cls, status: Literal[CarStatusChoice.ACTIVE, CarStatusChoice.AWAIT] = CarStatusChoice.ACTIVE) -> int:
        return len(AnalysManager.get_cars_per_status(cls.car_qr_list, status))
    

    @classmethod
    def status_cars_percent(cls, status: Literal[CarStatusChoice.ACTIVE, CarStatusChoice.AWAIT], precise: bool = False) -> int|float:
        return (cls.status_cars_count(status) / cls.all_cars_count()) * 100 if precise else int((cls.status_cars_count(status) / cls.all_cars_count()) * 100)
    

    @classmethod
    def dynamic_cars_per_month(cls) -> list[dict]:
        data = cls.pd_car_data[['status', 'created_at', 'created_at_my']].copy()
        d1 = (
            data.groupby('created_at_my')
                .size()
                .reset_index(name='total')
                .rename(columns={'created_at_my': 'month'})
        )
        return d1.to_dict(orient="records")
    

    @classmethod
    def active_cars_per_month(cls) -> list[dict]:
        data = cls.pd_car_data[['status', 'created_at', 'created_at_my']].copy()
        data = data[data['status'] == CarStatusChoice.ACTIVE]
        
        return (
            data.groupby('created_at_my')
                .size()
                .reset_index(name='total')
                .rename(columns={'created_at_my': 'month'})
                .to_dict(orient='records')
        )
    
    # --------------------Owner - Car-------------------- #
    @classmethod
    def get_cars_per_owner(cls) -> list[dict]:
        owners = (
            Owner.objects
            .annotate(cars_total=Count('cars'))
            .order_by('-cars_total')
            .values('first_name', 'last_name', 'cars_total')
        )

        return owners
    

    @classmethod
    def head_cars_per_owner(cls, counts: int = 3) -> list[dict]:
        return cls.get_cars_per_owner()[:counts]


    def test(self):
        print(
            f"[all_cars_count] -> {self.all_cars_count()}\n \
            [get_cars_per_status]: ACTIVE -> {self.status_cars_count(status=CarStatusChoice.ACTIVE)}\n \
            [get_cars_per_status]: AWAIT -> {self.status_cars_count(status=CarStatusChoice.AWAIT)}\n \
            [status_cars_percent]: ACTIVE -> {self.status_cars_percent(status=CarStatusChoice.ACTIVE)}\n \
            [status_cars_percent]: AWAIT -> {self.status_cars_percent(status=CarStatusChoice.AWAIT)}\n \
            [dynamic_cars_per_month] -> {self.dynamic_cars_per_month()}\n \
            [active_cars_per_month] -> {self.active_cars_per_month()}\n \
            [get_cars_per_owner] -> {self.get_cars_per_owner()}\n \
            [head_cars_per_owner] -> {self.head_cars_per_owner(7)}\n"
        )