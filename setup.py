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

from setuptools import setup, find_packages

setup(name='mmp_tracer_api',
      version='0.1',
      license='Apache-2.0',
      description='API for MMPRaytracer to the MMP modelling platform',
      author='Olli Tapaninen, Mikko Majanen',
      author_email='olli.tapaninen@gmail.com, mikko.majanen@vtt.fi',
      packages=find_packages(),
      entry_points={
          'console_scripts':
          ['runTracerServer = mmp_tracer_api.tracerServer:main',
           'runTracerServerSingle=mmp_tracer_api.' +
           'tracerServer:runSingleServerInstance',
           'runTracerServerSingleNoNat=mmp_tracer_api.' +
           'tracerServer:runSingleServerInstanceNoNat',
           'killTracerServer = mmp_tracer_api.killTracerServer:main']
      },
      package_data={'mmp_tracer_api':
                    ['data/*.dat',
                     'data/DefaultLED.json',
                     'data/logging.conf']},
      eager_resources={'mmp_tracer_api':
                       ['data/*.dat', 'data/DefaultLED.json']},
      # This line is only for python setup.py bdist, for PyPI see MANIFEST.in
      requires=['numpy', 'scipy', 'setuptools', 'mupif', 'pandas'],
      include_package_data=True,
      url='http://www.vtt.fi/'

      )
