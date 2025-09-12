
class Customer:
    def __init__(self, brand="", color="red", year=2023):
        self.brand = brand
        self.color = color
        self.year = year
    
    def start_engine(self):
        return f"Color of the car {self.color}"