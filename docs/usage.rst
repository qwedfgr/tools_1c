-----
Usage
-----
To use tools-1c in a project::

    import tools_1c

Set settings to file settings.yaml

Example settings::

    variables:
      CLUSTERS:
        DEV:1641:
          server_name: 'dev'
          port: 1641
          version: '8.3.14.1854'
          ras_port: 1645
        DEV:1741:
          server_name: 'dev'
          port: 1741
          version: '8.3.15.1747'
          ras_port: 1745
      SQL_SERVERS:
        DEV:
          DBMS: 'MSSQLServer'
          DB_HOST: 'dev'
          DB_USER: 'DB_USER'
          DB_PASSWORD: 'DB_PASSWORD'


Cluster management is carried out using ras / rac services

Infobase creation
******************
::

    cluster = tools_1c.Cluster('cluster_name')
    cluster.create_infobase('ib_name', sql_server='DEV')

Drop infobase
******************
::

    cluster = tools_1c.Cluster('cluster_name')
    cluster.drop_infobase('ib_name', 'username', 'pwd', mode='drop-database')

Set shedule jobs lock for infobase
**********************************
::

    cluster = tools_1c.Cluster('cluster_name')
    cluster.set_schedule_jobs_lock('ib_name', 'on', 'username', 'pwd')

Set new session lock
********************
::

    cluster = tools_1c.Cluster('cluster_name')
    cluster.set_session_lock('ib_name', 'on', 'username', 'pwd')


Terminate sessions
******************
::

    cluster = tools_1c.Cluster('cluster_name')
    cluster.terminate_sessions('ib_name', 5)


