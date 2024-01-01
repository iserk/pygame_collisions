import math


class Vector2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        return Vector2(self.x * other.x, self.y * other.y)

    def __truediv__(self, other):
        return Vector2(self.x / other.x, self.y / other.y)

    def __repr__(self):
        return f'Vector2({self.x}, {self.y})'

    def get_normalized(self):
        return Vector2(self.x / self.length(), self.y / self.length())

    def length(self):
        return math.sqrt(self.x * self.x + self.y * self.y)

    def get_perpendicular(self):
        return Vector2(-self.y, self.x)

