{% set pkgs=pillar['caches']['packages'] %}
{% set scripts=pillar['caches']['scripts'] %}

caffeine:
    file.managed:
        - name: {{ pkgs }}/caffeine.zip
        - source: http://download.lightheadsw.com/download.php?software=caffeine
        - source_hash: sha256=9203c30951f9aab41ac294bbeb1dcef7bed401ff0b353dcb34d68af32ea51853
        - backup: False
    cmd.wait:
        - name: "{{ scripts }}/unzip_and_mv.sh '{{ pkgs }}/caffeine.zip' 'Caffeine.app' '/Applications/Caffeine.app'"
        - stateful: True
        - watch:
            - file: '{{ pkgs }}/caffeine.zip'
