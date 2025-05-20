#!/bin/bash

export LD_LIBRARY_PATH=/opt/rocm/lib:$LD_LIBRARY_PATH # Путь к библиотекам ROCm (может отличаться)
export ZLUDA_VISIBLE_DEVICES=all                      #Или перечислите конкретные, если нужно. all - надежнее
export HIP_VISIBLE_DEVICES=all                        #Или перечислите конкретные, если нужно. all - надежнее
export CUDA_VISIBLE_DEVICES=all

"$@" # Запускает команду, переданную скрипту как аргумент
