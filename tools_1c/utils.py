import subprocess as sub

import yaml


def read_settings():
    with open('settings.yaml', 'r', encoding='utf-8') as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)


def get_value_by_key_in_dicts_list(key, list_of_dictionaries):
    return [element[key] for element in list_of_dictionaries if element.get(key)][0]


def get_cluster_by_version(version):
    clusters = read_settings()['variables']['CLUSTERS']
    for cluster in clusters:
        if clusters[cluster]['version'] == version:
            return cluster


def run_command(description, command):
    try:
        proc = sub.Popen(command, stdout=sub.PIPE, stderr=sub.PIPE)
        outs, errs = proc.communicate()
        if errs:
            raise ChildProcessError(f'Error {errs.decode("cp866")} when {description}')
        else:
            output = outs.decode('cp866')
    except Exception as exc:
        raise exc
    return output.split('\r\n')


def get_cluster_and_ib_name(connection_string):
    connection_string = connection_string.replace('";', '')
    connection_string = connection_string.replace('Srvr="', '')
    cluster, ib_name = connection_string.split('Ref="')
    return cluster, ib_name

