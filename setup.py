from setuptools import setup
import os
from glob import glob

package_name = 'riptide_ignition2'

# bit of a hack to grab all of the model file dirs correctly
def glob_model_paths():
    result = {}
    for root, dirs, files in os.walk("models", topdown=True):
        for name in files:
            shareDir = os.path.join('share', package_name, root)
            if(not shareDir in result):
                result[shareDir] = []
            result[shareDir].append(os.path.join(root, name))

    return result.items()

data_files = []
data_files.extend(glob_model_paths())
data_files.extend([
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch*')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
        (os.path.join('share', package_name, 'worlds'), glob('worlds/*.world'))
    ])

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=data_files,
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Cole Tucker',
    maintainer_email='tucker.737@osu.edu',
    description='Riptide AUV simulator with ignition',
    license='BSD',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'depth_remap = riptide_ignition2.depth_remap:main',
            'imu_remap = riptide_ignition2.imu_remap:main',
            'kill_switch_publisher = riptide_ignition2.kill_switch_publisher:main',
            'thrust_remap = riptide_ignition2.thrust_remap:main',
        ],
    },
)
