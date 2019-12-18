import os

from . import utils


class Cluster:
    def __init__(self, cluster, all_settings):
        """Class to manage cluster infobase and cluster settings.
        Args:
            cluster (str): cluster name
            all_settings (dict) = dict with data from settings file
        """
        settings = all_settings["variables"]['CLUSTERS'][cluster.upper()]
        path = settings['path']
        self.settings = all_settings
        self.path = os.path.join(path, settings['version'], 'bin')
        os.chdir(self.path)
        self.server_name = settings['server_name']
        self.ras_port = settings['ras_port']
        self._cluster_id = self._get_cluster_id()
        self.infobases = self._get_list_of_infobases()
        self.sql_server = settings['default_sql_server']

    def terminate_sessions(self, ib_name, session_number=''):
        """Terminate infobase sessions.
        Args:
            ib_name (str): infobase name
            session_number (str, int): session number, if not set, then all sessions terminate
        """
        sessions = self._get_sessions_list(ib_name)
        for session in sessions:
            if session['session-id'] == str(session_number) or not session_number:
                command = f'rac session terminate --cluster={self._cluster_id} --session={session["session"]}'
                command = self._add_ras_host(command)
                try:
                    utils.run_command('Terminate sessions:', command)
                except Exception as e:
                    print(f'failed to end session: {e}')

    def create_infobase(self, ib_name, sql_server=''):
        """Create new infobase in cluster.
        Args:
            ib_name (str): infobase name
            sql_server (str): name of SQL server from settings file
        """
        settings = self.settings['variables']['SQL_SERVERS']
        if sql_server:
            db = settings[sql_server]
        else:
            db = settings[self.sql_server]
        command = f'rac infobase' + \
                  f' --cluster={self._cluster_id}' \
                  f' create --create-database --name={ib_name}' \
                  f' --dbms={db["DBMS"]} --db-server={db["DB_HOST"]}' \
                  f' --db-user={db["DB_USER"]} --db-pwd={db["DB_PASSWORD"]}' \
                  f' --db-name={ib_name} --date-offset=2000 --security-level=1' \
                  f' --license-distribution=allow --locale=ru'
        command = self._add_ras_host(command)
        output = utils.run_command(f'Create infobase {ib_name} :', command)
        infobase_id = self._process_output(output, '')[0]['infobase']
        return infobase_id

    def drop_infobase(self, ib_name, username, pwd, mode=''):
        """Drop infobase.
        Args:
            ib_name (str): infobase name
            username (str): infobase administrator username
            pwd (str): infobase administrator password
            mode (str): mode of deleting database
                available value:
                    clear-database - clear database
                    drop-database - delete database
        """
        infobase_id = self._get_infobase_id(ib_name)
        command = f'rac infobase drop' \
                  f' --infobase={infobase_id}'
        if mode:
            self._check_value(mode, ['clear-database', 'drop-database'])
            command += f'--{mode}'
        command = self._add_user_credentials(command, username, pwd)
        command = self._add_ras_host(command)
        utils.run_command(f'drop infobase {ib_name} ', command)

    def set_session_lock(self, ib_name, mode, username, pwd):
        if self._check_value(mode, ['on', 'off']):
            return
        self._set_option(ib_name, option='sessions-deny', mode=mode, username=username, pwd=pwd)

    def set_schedule_jobs_lock(self, ib_name, mode, username, pwd):
        if self._check_value(mode, ['on', 'off']):
            return
        self._set_option(ib_name, option='scheduled-jobs-deny', mode=mode, username=username, pwd=pwd)

    def _get_list_of_infobases(self):
        command = f'rac infobase summary list --cluster={self._cluster_id}'
        command = self._add_ras_host(command)
        output = utils.run_command('get list of infobases ', command)
        list_of_ib = self._process_output(output, '')
        return [{i['name']: i['infobase']} for i in list_of_ib]

    def _get_cluster_id(self):
        command = 'rac.exe cluster list'
        command = self._add_ras_host(command)
        output = utils.run_command('get cluster id:', command)
        return self._process_output(output, '')[0]['cluster']

    def _set_option(self, ib_name, option, mode, username='', pwd=''):
        ib_id = self._get_infobase_id(ib_name)
        command = f'rac infobase update' \
                  f' --cluster={self._cluster_id}' \
                  f' --infobase={ib_id}' \
                  f' --{option}={mode}'
        command = self._add_user_credentials(command, username, pwd)
        command = self._add_ras_host(command)
        utils.run_command(f'Setting {option} to {mode}', command)

    def _get_infobase_id(self, ib_name):
        try:
            ib_id = utils.get_value_by_key_in_dicts_list(ib_name, self.infobases)
        except Exception:
            raise KeyError(f'Could not find the infobase: "{ib_name}"')
        return ib_id

    def _add_ras_host(self, command):
        return f'{command} {self.server_name}:{self.ras_port}'

    def _get_sessions_list(self, ib_name):
        ib_id = self._get_infobase_id(ib_name)
        if ib_id is None:
            return
        command = f'rac session list ' \
                  f'--cluster={self._cluster_id} ' \
                  f'--infobase={ib_id}'
        command = self._add_ras_host(command)
        output = utils.run_command(f'get sessions list of infobase {ib_name}:', command)
        session_list = self._process_output(output, 'data-separation')
        return session_list

    @staticmethod
    def _check_value(value, valid_values):
        """Checks the value for validity.
        Args:
            value (str): value for check
            valid_values (list): list of valid values
        """
        if value not in valid_values:
            raise ValueError(f'Invalid value {value}. Available values: {valid_values}')

    @staticmethod
    def _add_user_credentials(command, username='', pwd=''):
        if username:
            command += f' --infobase-user={username} --infobase-pwd={pwd}'
        return command

    @staticmethod
    def _process_output(output, separator):
        objects = []
        is_new_object = True
        for i in output:
            if not i and i != separator:
                continue
            if (i.startswith(separator) and bool(separator)) or separator == i:
                is_new_object = True
                continue
            if is_new_object:
                obj = {}
                objects.append(obj)
                is_new_object = False
            key, value = i.replace(' ', '').split(':', maxsplit=1)
            obj[key] = value
        return objects


class ClusterError(Exception):
    def __init__(self, text):
        self.txt = text
