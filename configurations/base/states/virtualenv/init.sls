include:
    - pip

virtualenv:
    pip.installed:
        - name: virtualenv
        - require:
            - package: pip
