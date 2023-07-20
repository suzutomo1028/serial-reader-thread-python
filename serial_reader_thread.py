#!/usr/bin/env python3

from typing import Self
import threading as thr
import serial as ser
import logging as log

log.basicConfig(level=log.DEBUG, format='%(levelname)s : %(module)s : %(threadName)s : %(funcName)s : %(message)s')

class SerialReaderThread(thr.Thread):

    def __init__(self, serial: ser.Serial, name: str | None = None) -> None:
        super().__init__(name=name)
        self._serial = serial
        self._continue = True
        self._lock = thr.RLock()
        self._buffer = bytearray()

    def __enter__(self) -> Self:
        self.start()
        return self

    def __exit__(self, *args, **kwargs) -> None:
        self.stop()

    def run(self) -> None:
        while self._continue:
            n = self._serial.in_waiting
            if n:
                data = self._serial.read(size=n)
                with self._lock:
                    self._buffer.extend(data)

    def stop(self) -> None:
        self._continue = False

    def pop(self) -> None:
        with self._lock:
            try:
                return self._buffer.pop(0).to_bytes()
            except IndexError:
                raise RuntimeError('pop from empty buffer.')

    @property
    def buffer_size(self) -> int:
        with self._lock:
            return len(self._buffer)

    @property
    def buffer_empty(self) -> bool:
        return bool(self.buffer_size <= 0)

    def __str__(self) -> str:
        with self._lock:
            return str(self._buffer)

if __name__ == '__main__':
    with ser.Serial(port='COM4') as serial:
        with SerialReaderThread(serial=serial, name='SerialReaderThread') as reader:
            while True:
                if not reader.buffer_empty:
                    data = reader.pop()
                    serial.write(data)
