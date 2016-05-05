import ctypes
import time
libroaring = ctypes.CDLL('libroaring.so')


class BitMap:
    __BASE_TYPE__ = ctypes.c_uint32
    def __init__(self, values=None):
        if values is None:
            self.__obj__ = libroaring.roaring_bitmap_create()
        elif isinstance(values, BitMap):
            self.__obj__ = libroaring.roaring_bitmap_copy(values.__obj__)
        else:
            self.check_values(values)
            size = len(values)
            Array = self.__BASE_TYPE__*size
            values = Array(*values)
            self.__obj__ = libroaring.roaring_bitmap_of_ptr(size, values)

    def __del__(self):
        libroaring.roaring_bitmap_free(self.__obj__)

    @staticmethod
    def check_value(value):
        if not isinstance(value, int) or value < 0 or value > 4294967295:
            raise ValueError('Value %s is not an uint32.' % value)

    @staticmethod
    def check_values(values):
        for value in values:
            BitMap.check_value(value)

    def add(self, value):
        self.check_value(value)
        libroaring.roaring_bitmap_add(self.__obj__, value)

    def __contains__(self, value):
        self.check_value(value)
        return libroaring.roaring_bitmap_contains(self.__obj__, value)

    def __len__(self):
        return libroaring.roaring_bitmap_get_cardinality(self.__obj__)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return bool(libroaring.roaring_bitmap_equals(self.__obj__, other.__obj__))

    def __iter__(self):
        size = ctypes.pointer(self.__BASE_TYPE__(-1))
        to_array = libroaring.roaring_bitmap_to_uint32_array
        to_array.restype = ctypes.POINTER(self.__BASE_TYPE__)
        array = to_array(self.__obj__, size)
        for i in range(size.contents.value):
            yield int(array[i])