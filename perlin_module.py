
import math
import random

from _collections_abc import Iterable

from typing import Optional, Union


from typing import List, Tuple



import math
import random
from typing import Generator, List, Tuple, Union


def dot(
    vec1: Union[List, Tuple],
    vec2: Union[List, Tuple],
) -> Union[float, int]:
   
    if len(vec1) != len(vec2):
        raise ValueError('lengths of two vectors are not equal')
    return sum([val1 * val2 for val1, val2 in zip(vec1, vec2)])


def sample_vector(dimensions: int, seed: int) -> List[float]:
   

    st = random.getstate()
    random.seed(seed)

    vec = []
    for _ in range(dimensions):
        vec.append(random.uniform(-1, 1))  

    random.setstate(st)
    return vec


def fade(given_value: float) -> float:
    
    if given_value < 0 or given_value > 1:
        raise ValueError('expected to have value in [0, 1]')
    return 6 * math.pow(given_value, 5) - 15 * math.pow(given_value, 4) + 10 * math.pow(given_value, 3)  # noqa: WPS221, WPS432, E501


def hasher(coors: Tuple[int]) -> int:
    
    return max(
        1,
        int(abs(
            dot(
                [10 ** coordinate for coordinate in range(len(coors))],
                coors,
                ) + 1,
        )),
    )


def product(iterable: Union[List, Tuple]) -> float:
    
    if len(iterable) == 1:
        return iterable[0]
    return iterable[0] * product(iterable[1:])


def each_with_each(
    arrays: List[Tuple[int, int]],
    prev=(),
) -> Generator[Tuple[int], None, None]:
   
    for el in arrays[0]:
        new = prev + (el,)
        if len(arrays) == 1:
            yield new
        else:
            yield from each_with_each(arrays[1:], prev=new)


class RandVec(object):
    

    def __init__(self, coordinates: Tuple[int], seed: int):
        
        self.coordinates = coordinates
        self.vec = sample_vector(dimensions=len(self.coordinates), seed=seed)

    def dists_to(self, coordinates: List[float]) -> Tuple[float, ...]:
        
        return tuple(
            coor1 - coor2
            for coor1, coor2 in zip(coordinates, self.coordinates)
            )

    def weight_to(self, coordinates: List[float]) -> float:
        
        weighted_dists = list(
            map(
                lambda dist: fade(1-abs(dist)),
                self.dists_to(coordinates),
            ))

        return product(weighted_dists)

    def get_weighted_val(self, coordinates: List[float]) -> float:
        
        return self.weight_to(coordinates) * dot(
            self.vec, self.dists_to(coordinates),
            )

class PerlinNoise(object):
    

    def __init__(self, octaves: float = 1, seed: Optional[int] = None):
        

        if octaves <= 0:
            raise ValueError('octaves expected to be positive number')

        if seed is not None and not isinstance(seed, int) and seed <= 0:
            raise ValueError('seed expected to be positive integer number')

        self.octaves: float = octaves
        self.seed: int = seed if seed else random.randint(1, 10 ^ 5)  # noqa: S311, E501

    def __call__(self, coordinates: Union[int, float, Iterable]) -> float:
        
        return self.noise(coordinates)

    def noise(self, coordinates: Union[int, float, Iterable]) -> float:
       
        if not isinstance(coordinates, (int, float, Iterable)):
            raise TypeError('coordinates must be int, float or iterable')

        if isinstance(coordinates, (int, float)):
            coordinates = [coordinates]

        coordinates = list(
            map(lambda coordinate: coordinate * self.octaves, coordinates),
        )

        coor_bounding_box = [
            (math.floor(coordinate), math.floor(coordinate+1))
            for coordinate in coordinates
        ]
        return sum([
            RandVec(
                coors, self.seed * hasher(coors),
            ).get_weighted_val(coordinates)
            for coors in each_with_each(coor_bounding_box)
        ])
