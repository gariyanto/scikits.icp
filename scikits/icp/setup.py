#!/usr/bin/env python


def configuration(parent_package='', top_path=None):
    from numpy.distutils.misc_util import Configuration

    config = Configuration('icp', parent_package, top_path)
    config.add_data_dir('tests')
    config.add_data_dir('data')
    return config


if __name__ == '__main__':
    from numpy.distutils.core import setup

    config = Configuration(top_path='').todict()
    setup(**config)
