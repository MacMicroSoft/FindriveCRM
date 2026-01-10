from .models import *
from django.db.models import Sum, Count
from typing import Literal, Union, Callable, List
import pandas as pd
from pprint import pprint



class AnalysManager:
    def __init__(self):
        self.car_qr_list: list[dict] = [
            {
                **item,
                "created_at": item["created_at"].strftime("%d.%m.%Y"),
                "created_at_my": item["created_at"].strftime("%m.%Y"),
            }
            for item in Car.objects.values()
        ]
        self.pd_car_data  = pd.DataFrame(self.car_qr_list)


    def all_cars_count(self) -> int:
        return len(self.car_qr_list)
    

    def get_cars_per_status(self, cars: list[dict], status: Literal[CarStatusChoice.ACTIVE, CarStatusChoice.AWAIT]) -> list[Car]:
        return [car for car in cars if car.get('status') == status]


    def status_cars_count(self, status: Literal[CarStatusChoice.ACTIVE, CarStatusChoice.AWAIT] = CarStatusChoice.ACTIVE) -> int:
        return len(self.get_cars_per_status(self.car_qr_list, status))
    

    def status_cars_percent(self, status: Literal[CarStatusChoice.ACTIVE, CarStatusChoice.AWAIT], precise: bool = False) -> int|float:
        return (self.status_cars_count(status) / self.all_cars_count()) * 100 if precise else int((self.status_cars_count(status) / self.all_cars_count()) * 100)
    

    def dynamic_cars_per_month(self) -> list[dict]:
        data = self.pd_car_data[['status', 'created_at', 'created_at_my']].copy()
        d1 = (
            data.groupby('created_at_my')
                .size()
                .reset_index(name='total')
                .rename(columns={'created_at_my': 'month'})
        )
        return d1.to_dict(orient="records")
    

    def active_cars_per_month(self) -> list[dict]:
        data = self.pd_car_data[['status', 'created_at', 'created_at_my']].copy()
        data = data[data['status'] == CarStatusChoice.ACTIVE]
        
        return (
            data.groupby('created_at_my')
                .size()
                .reset_index(name='total')
                .rename(columns={'created_at_my': 'month'})
                .to_dict(orient='records')
        )
    

    def get_cars_per_owner(self) -> list[dict]:
        owners = (
            Owner.objects
            .annotate(cars_total=Count('cars'))
            .order_by('-cars_total')
            .values('first_name', 'last_name', 'cars_total')
        )

        return owners
    

    def get_car_service_price(self, car_id) -> float:
        return sum([item.total for item in CarService.objects.filter(car_id=car_id)])
    

    def get_other_price(self, car_id) -> float:
        return sum([item.total_amount for item in Other.objects.filter(car_id=car_id)])
    

    def get_outlay_price(self, car_id) -> float:
        total = (
            Outlay.objects
                .filter(cars__uuid=car_id)
                .aggregate(total=Sum("amount__full_price"))
        )['total'] or 0
    
        return total
    

    def __total_expense_abs(self, price_counter: Union[Callable, List[Callable]]) -> list[dict]:
        result = []
        for car in self.car_qr_list:
            if isinstance(price_counter, Callable):
                total = price_counter(car_id=car['uuid'])
            if isinstance(price_counter, list):
                total = sum(x(car_id=car['uuid']) for x in price_counter)

            result.append({
                'uuid': car['uuid'],
                'mark': car['mark'],
                'model': car['model'],
                'license_plate': car['license_plate'],
                'total_expense': total,
            })

        return result


    def get_car_service_price_all(self) -> list[dict]:
        return self.__total_expense_abs(self.get_car_service_price)


    def get_other_price_all(self) -> list[dict]:
        return self.__total_expense_abs(self.get_other_price)
    

    def get_outlay_price_all(self) -> list[dict]:
        return self.__total_expense_abs(self.get_outlay_price)


    def head_cars_per_owner(self, counts: int = 3) -> list[dict]:
        return self.get_cars_per_owner()[:counts]
    

    def get_all_cars_expense(self) -> list[dict]:
        func_counter_list = [self.get_car_service_price, self.get_other_price, self.get_outlay_price]
        return self.__total_expense_abs(func_counter_list)


    def get_total_expense(self) -> float:
        return sum([x['total_expense'] for x in self.get_all_cars_expense()])
    

    def avg_cars_expense(self) -> float:
        return self.get_total_expense() / self.all_cars_count()
    

    def avg_cars_mileage(self) -> float:
        return round(sum(c['mileage'] for c in self.car_qr_list) / self.all_cars_count(), 2) if self.car_qr_list else 0