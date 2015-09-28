#
# Copyright 2015 VTT Technical Research Center of Finland
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import argparse
import psutil

parser = argparse.ArgumentParser(description='Kill MMP-Tracer server.')


def main():
    print('####################################')
    print('Finding process...')
    for proc in psutil.process_iter():
        try:
            pinfo = proc.as_dict(attrs=['pid', 'name'])
        except psutil.NoSuchProcess:
            pass
        else:
            if pinfo['name'].find('runTracerServer') != -1:
                print(pinfo)
                psutil.Process(pinfo['pid']).kill()
                print('killed!')
            elif pinfo['name'].find('jobMan2cmd') != -1:
                print(pinfo)
                psutil.Process(pinfo['pid']).kill()
                print('killed!')
    print('done!')
    print('####################################')
